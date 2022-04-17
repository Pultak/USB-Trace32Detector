using LDClient.detection;
using LDClient.network;
using LDClient.utils;
using LDClient.utils.loggers;

using static System.Diagnostics.Process;
using static System.Reflection.Assembly;

namespace LDClient;

internal static class Program {

    public static ConfigLoader Config { get; } = new();
    public static ALogger DefaultLogger { get; } = ALogger.Current;
    private static IApiClient? DefaultApiClient { get; set; }
    
    private static readonly InfoFetcher InfoFetcher = new(
        5,
        1000,
        "output.txt"
    );
    
    public static int Main() {
        var exists = GetProcessesByName(Path.GetFileNameWithoutExtension(GetEntryAssembly()?.Location)).Length > 1;
        if (exists) {
            DefaultLogger.Error("Another instance of the application is already running");
            return 1;
        }
        
        DefaultApiClient = new ApiClient(
            Config.ApiBaseAddress,
            Config.ApiPort, 
            Config.ApiUsbEndPoint, 
            Config.RetryPeriod, Config.MaxEntries,
            Config.MaxRetries, 
            Config.CacheFileName
        );
        
        IProcessDetection processProcessDetection = new ProcessProcessDetection(
            Config.T32ProcessName,
            Config.DetectionPeriod,
            InfoFetcher,
            DefaultApiClient
        );
        
        DefaultLogger.Debug("Main -> starting the ApiClient");
        var apiClientThread = new Thread(DefaultApiClient.Run) {
            IsBackground = true
        };
        apiClientThread.Start();

        var processThread = new Thread(processProcessDetection.RunPeriodicDetection) {
            IsBackground = true
        };
        processThread.Start();

        while (true) {
            Thread.Sleep(10 * 1000);
        }
        return 0;
    }
}