using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using LDClient.network.data;

namespace LDClient.network
{
    /// <summary>
    /// Implementation of IHttpClient which defines the functionality
    /// of a HTTP client that is used by the API client to send data to the server. 
    /// </summary>
    public class HttpClient : IHttpClient
    {
        /// <summary>
        /// Instance of System.Net.Http.HttpClient
        /// </summary>
        private readonly System.Net.Http.HttpClient _httpClient;

        /// <summary>
        /// URL to which the HTTP client will connect
        /// </summary>
        private readonly string _uri;

        /// <summary>
        /// Creates an instance of the class
        /// </summary>
        /// <param name="uri">URL to which the HTTP client will connect</param>
        public HttpClient(string uri)
        {
            _httpClient = new System.Net.Http.HttpClient();
            _uri = uri;
        }

        /// <summary>
        /// Asynchronically sends data in JSON format to the server.
        /// </summary>
        /// <param name="payload">Payload to be sent to the server</param>
        /// <returns></returns>
        public Task<HttpResponseMessage> PostAsJsonAsync(Payload payload)
        {
            // Serialize the payload and send it to the server as JSON.
            return _httpClient.PostAsJsonAsync(_uri, payload, new JsonSerializerOptions
            {
                Converters = {
                    new JsonStringEnumConverter( JsonNamingPolicy.CamelCase)
                }
            });

        }
    }
}
