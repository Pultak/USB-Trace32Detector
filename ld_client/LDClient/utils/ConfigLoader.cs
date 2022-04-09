using LDClient.utils.loggers;
using Microsoft.Extensions.Configuration;

namespace LDClient.utils {
    internal class ConfigLoader {
        private const string LoggingSection = "Logging";
        private const string NetworkSection = "Network";


        public int LogChunkSize { get; set; }
        public int LogChunkMaxCount { get; set; }
        public int LogArchiveMaxCount { get; set; }

        public int LogCleanupPeriod { get; set; }

        public LogVerbosity LogVerbosityType { get; set; } = LogVerbosity.Full;

        public LogFlow LogFlowType { get; set; } = LogFlow.Console;

        public string ApiBaseAddress { get; set; }
        public string ApiUsbEndPoint { get; set; }
        public uint ApiPort { get; set; }
        public uint ApiRetryPeriod { get; set; }

        public string DebuggerAddress { get; set; }
        public int DebuggerPort { get; set; }

        public ConfigLoader() {
            var configuration = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json")
                .Build();
            ReadAllSettings(configuration);
        }

        private void ReadAllSettings(IConfigurationRoot configuration) {

            try {
                var logging = configuration.GetSection(LoggingSection);
                //TODO: Exception handling
                LogChunkSize = int.Parse(logging["LogChunkSize"]);
                LogChunkMaxCount = int.Parse(logging["LogChunkMaxCount"]);
                LogArchiveMaxCount = int.Parse(logging["LogArchiveMaxCount"]);
                LogCleanupPeriod = int.Parse(logging["LogCleanupPeriod"]);
                LogFlowType = (LogFlow)int.Parse(logging["LogFlowType"]);
                LogVerbosityType = (LogVerbosity)int.Parse(logging["LogVerbosityType"]);
                
                var network = configuration.GetSection(NetworkSection);
                ApiBaseAddress = network["ApiBaseAddress"];
                ApiUsbEndPoint = network["ApiLDEndPoint"];
                ApiPort = uint.Parse(network["ApiPort"]);
                ApiRetryPeriod = uint.Parse(network["ApiRetryPeriod"]);


                DebuggerAddress = network["DebuggerAddress"];
                DebuggerPort = int.Parse(network["DebuggerPort"]);

                Console.WriteLine("Configuration successfully loaded!");
            } catch (FormatException e) {
                //Console.WriteLine("Error reading app settings");
                //TODO: remove stacktrace print in production
                Console.WriteLine("Error during reading of configuration occurred!" + e);
                throw new IOException("Reading of configuration file failed! " + e);
            }
        }

    }
}
