using DiskQueue;
using LDClient.detection;
using LDClient.network;
using LDClient.utils;
using LDClient.utils.loggers;

using static System.Diagnostics.Process;
using static System.Reflection.Assembly;

namespace LDClient;

/// <summary>
/// This class represents the main class of the application.
/// </summary>
internal static class Program {

    /// <summary>
    /// Sleep period of the main thread of the application.
    /// </summary>
    private const int MainLoopDelayMs = 30000; 

    /// <summary>
    /// Instance of a config loader.
    /// </summary>
    public static ConfigLoader Config { get; } = new();
    
    /// <summary>
    /// Default logger used throughout the application.
    /// </summary>
    public static ALogger DefaultLogger { get; } = ALogger.Current;
    
    /// <summary>
    /// Instance of an API client.
    /// </summary>
    private static IApiClient? DefaultApiClient { get; set; }

    /*

    It is possible to use previous info fetching method

    /// <summary>
    /// Instance of an info fetcher.
    /// </summary>
    private static readonly IInfoFetcher InfoFetcher = new(
        Config.FetchInfoMaxAttempts,
        Config.FetchInfoAttemptPeriod,
        Config.T32InfoLocation,
        Config.T32RemExecutable,
        Config.T32RemArguments,
        Config.T32RemSuccessExitCode,
        Config.T32RemWaitTimeoutMs
    );
    */
    /// <summary>
    /// Instance of an info fetcher
    /// </summary>
    private static readonly IInfoFetcher InfoFetcher = new T32ApiFetcher(
        Config.FetchInfoMaxAttempts,
        Config.FetchInfoAttemptPeriod,
        Config.T32InfoLocation,
        Config.T32ApiAddress,
        Config.T32ApiPort,
        Config.T32ApiPacketLen,
        Config.T32ApiCommands
    );

    /// <summary>
    /// The main entry pint of the application.
    /// </summary>
    /// <returns>1 if something goes wrong, 0 otherwise.</returns>
    public static int Main() {
        // Make sure that there is only one running instance of this application.
        if (GetProcessesByName(Path.GetFileNameWithoutExtension(GetEntryAssembly()?.Location)).Length > 1) {
            DefaultLogger.Error("Another instance of the application is already running");
            return 1;
        }
        
        // Create an instance of an API client with all
        // the appropriate parameters defined in the config file.
        DefaultApiClient = new ApiClient(
            Config.ApiBaseAddress,
            Config.ApiPort, 
            Config.ApiUsbEndPoint, 
            Config.RetryPeriod, Config.MaxEntries,
            Config.MaxRetries, 
            new PersistentQueue(Config.CacheFileName)
        );
        
        // Create a new process detector.
        IProcessDetection processProcessDetection = new ProcessDetection(
            Config.T32ProcessName,
            Config.DetectionPeriod,
            InfoFetcher,
            DefaultApiClient,
            new ProcessUtils(),
            Config.FetchInfoSuperiorMaxAttempts,
            Config.FetchInfoSuperiorAttemptPeriod
        );
        
        // Create and start a new thread that periodically
        // resends filed payloads to the server.
        var apiClientThread = new Thread(DefaultApiClient.Run) {
            IsBackground = true
        };
        apiClientThread.Start();

        // Create and start a new thread that periodically checks
        // if the desired process is currently running or not.
        var processThread = new Thread(processProcessDetection.RunPeriodicDetection) {
            IsBackground = true
        };
        processThread.Start();

        // The main thread does "nothing"
        while (true) {
            Thread.Sleep(MainLoopDelayMs);
        }

        // The execution of the program should never reach this point.
        return 0;
    }
}