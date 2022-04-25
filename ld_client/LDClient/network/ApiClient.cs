using System.Diagnostics;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using DiskQueue;
using LDClient.network.data;

namespace LDClient.network {
    
    public sealed class ApiClient : IApiClient {
        
        public IHttpClient _client;

        public bool ClientRunning;

        private readonly uint _retryPeriod;
        private readonly uint _maxEntries;
        private readonly uint _maxRetries;
        private readonly IPersistentQueue _cache;

        public ApiClient(string url, uint port, string path, uint retryPeriod, uint maxEntries, uint maxRetries, IPersistentQueue cache) {
            var uri = $"{url}:{port}{path}";
            _retryPeriod = retryPeriod;
            _maxEntries = maxEntries;
            _maxRetries = maxRetries;

            _client = new HttpClient(uri);
            _cache = cache;
        }

        public async Task SendPayloadAsync(Payload payload) {
            try {
                Stopwatch stopWatch = new();
                stopWatch.Start();
                
                var response = await _client.PostAsJsonAsync(payload);
                stopWatch.Stop();
                CreateRequestLog(payload, response, stopWatch.ElapsedMilliseconds);

                response.EnsureSuccessStatusCode();
            } catch (Exception e) {
                Program.DefaultLogger.Error($"Failed to send {payload} to the server. Due to: {e.Message}");
                CachePayload(payload);
            }
        }

        private static void CreateRequestLog(Payload payload, HttpResponseMessage response, long durationMs) {
            var responseToLog = new {
                statusCode = response.StatusCode,
                content = response.Content,
                headers = response.Headers,
                errorMessage = response.RequestMessage,
            };

            Program.DefaultLogger.Info($"Request completed in {durationMs} ms,\n" +
                                 $"Request body: {payload},\n" +
                                 $"Response: {responseToLog}");
        }
        
        private async Task ResendPayloadsAsync() {
            var numberOfPayloadsToResend = Math.Min(_maxRetries, _cache.EstimatedCountOfItemsInQueue);
            var payloads = new List<Payload>();
            if (numberOfPayloadsToResend > 0) {
                using var session = _cache.OpenSession();
                for (var i = 0; i < numberOfPayloadsToResend; i++) {
                    var rawBytes = session.Dequeue();
                    var payload = JsonSerializer.Deserialize<Payload>(rawBytes);
                    if (payload is not null) {
                        payloads.Add(payload);
                    }
                }
                session.Flush();
            }

            if (payloads.Count > 0) {
                Program.DefaultLogger.Debug($"ResendPayloadAsync -> {payloads.Count} unsent payloads");
                var tasks = new List<Task>();
                foreach (var payload in payloads) {
                    Program.DefaultLogger.Info($"Resending {payload}.");
                    tasks.Add(SendPayloadAsync(payload));
                }
                await Task.WhenAll(tasks);
            }
        }
        
        private void CachePayload(Payload payload) {
            Program.DefaultLogger.Info($"Storing {payload} into the cache.");
            var numberOfCachedPayloads = _cache.EstimatedCountOfItemsInQueue;
            using var session = _cache.OpenSession();
            if (numberOfCachedPayloads >= _maxEntries) {
                session.Dequeue();
            }
            var payloadJson = JsonSerializer.Serialize(payload);
            session.Enqueue(Encoding.UTF8.GetBytes(payloadJson));
            session.Flush();
        }

        public async void Run() {
            Program.DefaultLogger.Info("Api Client thread has started");
            ClientRunning = true;
            while (ClientRunning) {
                await ResendPayloadsAsync();
                Thread.Sleep((int) _retryPeriod);
            }
        }
    }
}
