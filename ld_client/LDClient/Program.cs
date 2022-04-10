using System.Runtime.InteropServices;
using System.Security.Principal;
using LDClient.detection;
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


    private static NetworkDetection _netDetect = new(Config.ApiPort, Config.DetectionPeriod);
    private static ProcessDetection _procDetect = new(Config.T32ProcessName, Config.DetectionPeriod);


    // Main Method
    public static async Task Main() {
        var apiClientThread = new Thread(DefaultApiClient.Run) {
            IsBackground = true
        };
        DefaultLogger.Debug("Main -> starting the ApiClient");
        apiClientThread.Start();

        var admin = IsAdministrator();
        DefaultLogger.Debug($"Is program executed with admin rights? {admin}");

        var networkTread = new Thread(_netDetect.RunPeriodicDetection);
        networkTread.Start();
        if (admin) {
            _procDetect.RegisterProcessListeners();

        } else {
            var processThread = new Thread(_procDetect.RunPeriodicDetection);
            processThread.Start();
            processThread.Join();
        }

        networkTread.Join();

        DefaultLogger.Debug("Main -> stopping the ApiClient");
        DefaultApiClient.Stop();
        apiClientThread.Join();
        DefaultLogger.Debug("Main -> finished");
    }

    public static bool IsAdministrator() {
        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows)) {
            var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            return principal.IsInRole(WindowsBuiltInRole.Administrator);

        } else {
            return false;
        }
    }
}