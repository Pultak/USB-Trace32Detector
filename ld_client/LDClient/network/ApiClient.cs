using System.Diagnostics;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using LDClient.network.data;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

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


        private readonly string _uri;
        private readonly HttpClient _client;
        private readonly uint _retryPeriod;


        public ApiClient(string url, uint port, string path, uint retryPeriod) {
            _uri = $"{url}:{port}{path}";
            _retryPeriod = retryPeriod;
            
            _client = new HttpClient();

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
        }
    }
}
