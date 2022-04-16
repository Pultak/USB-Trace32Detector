using System.Runtime.InteropServices;
using System.Security.Principal;
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
    private static readonly NetworkDetection NetDetect = new(Config.ApiPort, Config.DetectionPeriod);
    private static readonly ProcessDetection ProcDetect = new(Config.T32ProcessName, Config.DetectionPeriod);
    
    // Main Method
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
        
        DefaultLogger.Debug("Main -> starting the ApiClient");
        var apiClientThread = new Thread(DefaultApiClient.Run) {
            IsBackground = true
        };
        apiClientThread.Start();

        var admin = IsAdministrator();
        DefaultLogger.Debug($"Is program executed with admin rights? {admin}");

        var networkTread = new Thread(NetDetect.RunPeriodicDetection);
        networkTread.Start();
        
        if (admin) {
            ProcDetect.RegisterProcessListeners();
        } else {
            var processThread = new Thread(ProcDetect.RunPeriodicDetection);
            processThread.Start();
            processThread.Join();
        }

        networkTread.Join();

        DefaultLogger.Debug("Main -> stopping the ApiClient");
        DefaultApiClient.Stop();
        apiClientThread.Join();
        DefaultLogger.Debug("Main -> finished");
        
        return 0;
    }

    private static bool IsAdministrator() {
        if (!RuntimeInformation.IsOSPlatform(OSPlatform.Windows)) {
            return false;
        }
        var identity = WindowsIdentity.GetCurrent();
        var principal = new WindowsPrincipal(identity);
        return principal.IsInRole(WindowsBuiltInRole.Administrator);
    }
}