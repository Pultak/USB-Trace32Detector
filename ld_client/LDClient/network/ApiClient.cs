﻿using System.Diagnostics;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using DiskQueue;
using LDClient.network.data;

namespace LDClient.network {
    public class ApiClient : IApiClient {
        
        public static readonly Payload ExampleInfo = new() {
            UserName = "honikCz",
            HostName = "Bramborak",
            TimeStamp = DateTime.Parse("2022-03-21 18:05:00.168895"),
            HeadDevice = new DebuggerInfo {
                SerialNumber = "C12345678912"
            },
            BodyDevice = new DebuggerInfo {
                SerialNumber = "C98765432198"
            },
            Status = ConnectionStatus.Connected
        };

        private bool _running;


        private readonly string _uri;
        private readonly HttpClient _client;
        private readonly IPersistentQueue _cache;
        private readonly uint _retryPeriod;
        private readonly uint _maxEntries;
        private readonly uint _maxRetries;
        


        public ApiClient(string url, uint port, string path, uint retryPeriod, uint maxEntries, uint maxRetries,
            string cacheFilename) {
            _uri = $"{url}:{port}{path}";
            _retryPeriod = retryPeriod;
            _maxEntries = maxEntries;
            _maxRetries = maxRetries;

            _client = new HttpClient();
            _cache = new PersistentQueue(cacheFilename);

        }

        public async Task SendPayloadAsync(Payload payload) {
            try {
                Stopwatch stopWatch = new();
                stopWatch.Start();

                var json = JsonConvert.SerializeObject(ExampleInfo);
                if (json is null) {
                    Program.DefaultLogger.Error($"Failed to serialize object: {ExampleInfo}");
                    return;
                }
                var response = await _client.PostAsJsonAsync(_uri, payload, new JsonSerializerOptions {
                    Converters = {
                        new JsonStringEnumConverter( JsonNamingPolicy.CamelCase)
                    }

                });
                stopWatch.Stop();
                Response2Log(json, response, stopWatch.ElapsedMilliseconds);

                response.EnsureSuccessStatusCode();
                var serverResponse = await response.Content.ReadAsStringAsync();
                CheckResponse(serverResponse);
            } catch (Exception e) {
                Program.DefaultLogger.Error($"Failed to send {payload} to the server. Due to: {e.Message}");
            }
        }
        
        private static bool CheckResponse(string response) {
            dynamic json = JObject.Parse(response);

            if (json.statusCode < 400) {
                return true;
            }
            throw new Exception($"Server responded with error code: {json.statusCode}");
        }
        
        private static void Response2Log(string json, HttpResponseMessage response, long durationMs) {
            var responseToLog = new {
                statusCode = response.StatusCode,
                content = response.Content,
                headers = response.Headers,
                errorMessage = response.RequestMessage,
            };

            Program.DefaultLogger.Info($"Request completed in {durationMs} ms,\n" +
                                 $"Request body: {json},\n" +
                                 $"Response: {JsonConvert.SerializeObject(responseToLog)}");

        private async Task ResendPayloadsAsync() {
            var numberOfPayloadsToResend = Math.Min(_maxRetries, _cache.EstimatedCountOfItemsInQueue);
            var payloads = new List<Payload>();

            using (var session = _cache.OpenSession()) {
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
            _running = true;
            while (_running) {
                await ResendPayloadsAsync();
                Thread.Sleep((int)_retryPeriod);
            }
        }

        public void Stop() {
            _running = false;
        }
    }
}
