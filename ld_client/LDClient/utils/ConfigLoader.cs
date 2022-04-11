using LDClient.utils.loggers;
using Microsoft.Extensions.Configuration;

namespace LDClient.utils {
    internal class ConfigLoader {
        private const string LoggingSection = "Logging";
        private const string NetworkSection = "Network";
        private const string CacheSection = "Cache";
        private const string DDSection = "DebuggerDetection";

        #region Logger
        public int LogChunkSize { get; set; }
        public int LogChunkMaxCount { get; set; }
        public int LogArchiveMaxCount { get; set; }

        public int LogCleanupPeriod { get; set; }

        public LogVerbosity LogVerbosityType { get; set; } = LogVerbosity.Full;

        public LogFlow LogFlowType { get; set; } = LogFlow.Console;
        #endregion

        #region Api
        public string ApiBaseAddress { get; set; }
        public string ApiUsbEndPoint { get; set; }
        public uint ApiPort { get; set; }

        #endregion

        #region Cache
        public string CacheFileName { get; set; }
        public uint MaxRetries { get; set; }
        public uint MaxEntries { get; set; }
        public uint RetryPeriod { get; set; }
        #endregion

        #region Detection
        public string T32Address { get; set; }
        public int T32Port { get; set; }
        public string T32ProcessName { get; set; }
        public uint DetectionPeriod { get; set; }
        public string T32InfoLocation { get; set; }
        #endregion

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


                var cache = configuration.GetSection(CacheSection);
                RetryPeriod = uint.Parse(cache["RetryPeriod"]);
                MaxEntries = uint.Parse(cache["MaxEntries"]);
                MaxRetries = uint.Parse(cache["MaxRetries"]);
                CacheFileName = cache["CacheFileName"];


                var debugger = configuration.GetSection(DDSection);
                T32Address = debugger["T32Address"];
                T32Port = int.Parse(debugger["T32Port"]);
                T32ProcessName = debugger["T32ProcessName"];
                T32InfoLocation = debugger["T32InfoLocation"];
                DetectionPeriod = uint.Parse(debugger["DetectionPeriod"]);

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
