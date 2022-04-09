using LDClient.network.data;

namespace LDClient.network {
    public interface IApiClient {
        public Task SendPayloadAsync(Payload payload);
    }
}
