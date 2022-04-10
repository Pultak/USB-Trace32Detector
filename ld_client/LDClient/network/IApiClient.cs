using LDClient.network.data;

namespace LDClient.network {
    public interface IApiClient {
        public Task SendPayloadAsync(Payload payload);
        public void Run();
        public void Stop();
    }
}
