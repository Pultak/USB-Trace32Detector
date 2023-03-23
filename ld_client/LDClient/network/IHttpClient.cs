using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using LDClient.network.data;

namespace LDClient.network
{
    /// <summary>
    /// This interface defines the functionality of a HTTP client
    /// through which the API client sends data (payloads) to the server.
    /// </summary>
    public interface IHttpClient
    {

        /// <summary>
        /// Asynchronically sends data in JSON format to the server.
        /// </summary>
        /// <param name="payload">Payload to be sent to the server</param>
        /// <returns></returns>
        public Task<HttpResponseMessage> PostAsJsonAsync(Payload payload);
    }
}
