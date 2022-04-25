using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using LDClient.network.data;

namespace LDClient.network {
    public class HttpClient : IHttpClient{

        private readonly System.Net.Http.HttpClient _httpClient;

        private readonly string _uri;
        public HttpClient(string uri) {

            _httpClient = new System.Net.Http.HttpClient();
            _uri = uri;
        }

        public Task<HttpResponseMessage> PostAsJsonAsync(Payload payload) {
            return _httpClient.PostAsJsonAsync(_uri, payload, new JsonSerializerOptions {
                Converters = {
                    new JsonStringEnumConverter( JsonNamingPolicy.CamelCase)
                }
            });

        }
    }
}
