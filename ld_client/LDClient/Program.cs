using LDClient.detection;
using LDClient.network;
using LDClient.utils;
using LDClient.utils.loggers;

using static System.Diagnostics.Process;
using static System.Reflection.Assembly;

namespace LDClient;

internal static class Program {

    private const int MainLoopDelayMs = 30000; 

    public static ConfigLoader Config { get; } = new();
    public static ALogger DefaultLogger { get; } = ALogger.Current;
    private static IApiClient? DefaultApiClient { get; set; }
    
    private static readonly InfoFetcher InfoFetcher = new(
        Config.FetchInfoMaxAttempts,
        Config.FetchInfoAttemptPeriod,
        Config.T32InfoLocation,
        Config.F32RemExecutable,
        Config.F32RemArguments,
        Config.T32RemSuccessExitCode,
        Config.T32RemWaitTimeoutMs
    );
    
    public static int Main() {
        if (GetProcessesByName(Path.GetFileNameWithoutExtension(GetEntryAssembly()?.Location)).Length > 1) {
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
        
        IProcessDetection processProcessDetection = new ProcessDetection(
            Config.T32ProcessName,
            Config.DetectionPeriod,
            InfoFetcher,
            DefaultApiClient,
            new ProcessUtils()
        );
        
        var apiClientThread = new Thread(DefaultApiClient.Run) {
            IsBackground = true
        };
        apiClientThread.Start();

        var processThread = new Thread(processProcessDetection.RunPeriodicDetection) {
            IsBackground = true
        };
        processThread.Start();

        while (true) {
            Thread.Sleep(MainLoopDelayMs);
        }
    }
}