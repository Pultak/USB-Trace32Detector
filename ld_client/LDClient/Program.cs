using LDClient.network;
using LDClient.utils;
using LDClient.utils.loggers;

namespace LDClient; 

internal class Program {

    public static ConfigLoader Config { get; set; } = new();
    public static ALogger DefaultLogger { get; } = ALogger.Current;

    public static IApiClient DefaultApiClient { get; set; } = new ApiClient(Config.ApiBaseAddress,
        Config.ApiPort, Config.ApiUsbEndPoint, Config.ApiRetryPeriod);

    // Main Method
    public static async Task Main() {
        await DefaultApiClient.SendPayloadAsync(ApiClient.ExampleInfo);
        Console.WriteLine("Finished!");
    }
}