using LDClient.network.data;
using System.Threading.Tasks;

namespace LDClient.network
{
    /// <summary>
    /// This interface defines the functionality of an API client
    /// which is used to send information (payloads) to the server.
    /// </summary>
    public interface IApiClient
    {
        /// <summary>
        /// Sends a payload to the server (API).
        /// </summary>
        /// <param name="payload">instance of a payload to be sent off to the server</param>
        public Task SendPayloadAsync(Payload payload);

        /// <summary>
        /// Runs the periodical retrieval of failed payloads stored
        /// in a file-based cache. This method is instantiated as a thread.
        /// </summary>
        public void Run();
    }
}
