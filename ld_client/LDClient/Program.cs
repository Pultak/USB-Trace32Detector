using LDClient.utils;
using LDClient.utils.loggers;

namespace LDClient; 

internal class Program {

    public static ConfigLoader Config { get; set; } = null!;

    // Main Method
    public static void Main() {
        Config = new ConfigLoader();

        while (true) {
            ALogger.Current.Info("Ok");
            ALogger.Current.Debug("Debug");
            ALogger.Current.Error("Error");
        }
    }
}