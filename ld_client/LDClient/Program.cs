using LDClient.network;
using LDClient.utils;
using LDClient.utils.loggers;

namespace LDClient; 

internal class Program {

    public static ConfigLoader Config { get; set; } = new();
    public static ALogger DefaultLogger { get; } = ALogger.Current;

    public static IApiClient DefaultApiClient { get; set; } = new ApiClient(Config.ApiBaseAddress,
        Config.ApiPort, Config.ApiUsbEndPoint, Config.RetryPeriod, Config.MaxEntries,
        Config.MaxRetries, Config.CacheFileName);

    // Main Method
    public static async Task Main() {

        var apiClientThread = new Thread(DefaultApiClient.Run) {
            IsBackground = true
        };
        apiClientThread.Start();

        DefaultLogger.Debug("Main -> starting SendPayloadAsync");
        await DefaultApiClient.SendPayloadAsync(ApiClient.ExampleInfo);


        DefaultLogger.Debug("Main -> lets slack for a bit");
        Thread.Sleep(30000);

        DefaultLogger.Debug("Main -> stopping the ApiClient");
        DefaultApiClient.Stop();
        apiClientThread.Join();
        DefaultLogger.Debug("Main -> finished");
    }
    }
}