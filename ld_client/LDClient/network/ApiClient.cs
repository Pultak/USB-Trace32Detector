using System.Diagnostics;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using DiskQueue;
using LDClient.network.data;

namespace LDClient.network {
    
    /// <summary>
    /// This class implements IApiClient which is an interface
    /// defining all the functionality required from an API client.
    /// </summary>
    public sealed class ApiClient : IApiClient {
        
        /// <summary>
        /// Instance of an HTTP client the is used to send data off to the server 
        /// </summary>
        public IHttpClient _client;

        /// <summary>
        /// Flag used to stop the client (periodical retrieval from the cache)
        /// </summary>
        public bool ClientRunning;

        /// <summary>
        /// Number of milliseconds after which the class tries to resend failed payloads to the server.
        /// </summary>
        private readonly uint _retryPeriod;
        
        /// <summary>
        /// Maximum number of entries (payloads) that can be sent to the server within one period (_retryPeriod).
        /// </summary>
        private readonly uint _maxEntries;
        
        /// <summary>
        /// Maximum number of failed payloads to be kept in the file-based cache (FIFO - when the maximum number is reached)
        /// </summary>
        private readonly uint _maxRetries;
        private readonly IPersistentQueue _cache;

        /// <summary>
        /// Creates an instance of the class.
        /// </summary>
        /// <param name="url">IP address of the server (url in case a DNS server is being used)</param>
        /// <param name="port">port that the API is running on</param>
        /// <param name="path">path of the API e.g. /api/v1/lg-logs</param>
        /// <param name="retryPeriod">number of milliseconds after which the class tries to resend failed payloads to the server</param>
        /// <param name="maxEntries">maximum number of entries (payloads) that can be sent to the server within one period</param>
        /// <param name="maxRetries">maximum number of failed payloads to be kept in the file-based cache</param>
        /// <param name="cache">instance of a persistent cache for storing failed payloads</param>
        public ApiClient(string url, uint port, string path, uint retryPeriod, uint maxEntries, uint maxRetries, IPersistentQueue cache) {
            // Construct the entire path to the API.
            var uri = $"{url}:{port}{path}";
            
            // Store the values into class variables.
            _retryPeriod = retryPeriod;
            _maxEntries = maxEntries;
            _maxRetries = maxRetries;
            _cache = cache;

            // Create an instance of a HttpClient which takes care of
            // establishing a connection to the server;
            _client = new HttpClient(uri);
        }

        /// <summary>
        /// Sends a payload to the server (API).
        /// </summary>
        /// <param name="payload">instance of a payload to be sent off to the server</param>
        public async Task SendPayloadAsync(Payload payload) {
            Program.DefaultLogger.Debug("SendPayloadAsync called.");
            try {
                // Create an instance of Stopwatch (to measure how much
                // the action took).
                Stopwatch stopWatch = new();
                
                // Send the payload to the server.
                stopWatch.Start();
                var response = await _client.PostAsJsonAsync(payload);
                stopWatch.Stop();
                
                // Create a log message.
                CreateRequestLog(payload, response, stopWatch.ElapsedMilliseconds);
                
                // Make sure the request was successful.
                response.EnsureSuccessStatusCode();
            } catch (Exception e) {
                Program.DefaultLogger.Error($"Failed to send {payload} to the server. Due to: {e.Message}");
                CachePayload(payload);
            }
        }

        /// <summary>
        /// Creates a request log message.
        /// </summary>
        /// <param name="payload">payload involved in the process of sending data to the server</param>
        /// <param name="response">response from the server</param>
        /// <param name="durationMs">duration in milliseconds (how much time it took to send off the payload)</param>
        private static void CreateRequestLog(Payload payload, HttpResponseMessage response, long durationMs) {
            // Create the log message.
            var responseToLog = new {
                statusCode = response.StatusCode,
                content = response.Content,
                headers = response.Headers,
                errorMessage = response.RequestMessage,
            };
            
            // Log the message using the logger defined in Program (main class).
            Program.DefaultLogger.Info($"Request completed in {durationMs} ms,\n" +
                                       $"Request body: {payload},\n" +
                                       $"Response: {responseToLog}");
        }
        
        /// <summary>
        /// Resends unsuccessful payloads to the server.
        /// </summary>
        private async Task ResendPayloadsAsync() {
            // Calculate the maximum number of payloads to be sent to the server.
            var numberOfPayloadsToResend = Math.Min(_maxRetries, _cache.EstimatedCountOfItemsInQueue);
            
            // Create a list for those payloads
            var payloads = new List<Payload>();
            
            // Retrieve the payloads from the cache.
            if (numberOfPayloadsToResend > 0) {
                // Open up a session to the cache.
                using var session = _cache.OpenSession();
                
                // Pop out payloads, deserialize them, and store them into the list.
                for (var i = 0; i < numberOfPayloadsToResend; i++) {
                    var rawBytes = session.Dequeue();
                    var payload = JsonSerializer.Deserialize<Payload>(rawBytes);
                    if (payload is not null) {
                        payloads.Add(payload);
                    }
                }
                // Flush the changes.
                session.Flush();
            }
            
            // If there are some payloads to be resent to the server.
            if (payloads.Count > 0) {
                Program.DefaultLogger.Debug($"ResendPayloadAsync -> {payloads.Count} unsent payloads");
                var tasks = new List<Task>();
                
                // Create a separate task for each payload - resend them to the server.
                foreach (var payload in payloads) {
                    Program.DefaultLogger.Info($"Resending {payload}.");
                    tasks.Add(SendPayloadAsync(payload));
                }
                // Wait until all tasks are finished. 
                await Task.WhenAll(tasks);
            }
        }
        
        /// <summary>
        /// Stores a failed payload into a persistent cache.
        /// </summary>
        /// <param name="payload"></param>
        private void CachePayload(Payload payload) {
            Program.DefaultLogger.Info($"Storing {payload} into the cache.");
            
            // Number of payloads stored in the cache.
            var numberOfCachedPayloads = _cache.EstimatedCountOfItemsInQueue;
            
            // Open up a session to the cache.
            using var session = _cache.OpenSession();
            
            // If the cache is "full", make room for the latest failed
            // payload by discarding the oldest one.
            if (numberOfCachedPayloads >= _maxEntries) {
                session.Dequeue();
            }
            
            // Store the payload into the cache.
            var payloadJson = JsonSerializer.Serialize(payload);
            session.Enqueue(Encoding.UTF8.GetBytes(payloadJson));
            
            // Flush the changes.
            session.Flush();
        }

        /// <summary>
        /// Runs the periodical retrieval of failed payloads stored
        /// in a file-based cache. This method is instantiated as a thread.
        /// </summary>
        public async void Run() {
            Program.DefaultLogger.Info("Api Client thread has started");
            
            // Keep the thread running.
            ClientRunning = true;
            
            // Keep resending failed payloads to the server.
            while (ClientRunning) {
                await ResendPayloadsAsync();
                Thread.Sleep((int) _retryPeriod);
            }
        }
    }
}
