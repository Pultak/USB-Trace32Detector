using LDClient.utils.loggers;
using Microsoft.Extensions.Configuration;

namespace LDClient.utils {
    
    internal class ConfigLoader {

        private const int ErrorExitCode = 1;
        private const string ConfigFile = "appsettings.json";
        private const string LoggingSection = "Logging";
        private const string NetworkSection = "Network";
        private const string CacheSection = "Cache";
        private const string DdSection = "DebuggerDetection";

        #region Logger
        
        public int LogChunkSize { get; private set; }
        public int LogChunkMaxCount { get; private set; }
        public int LogArchiveMaxCount { get; private set; }
        public int LogCleanupPeriod { get; private set; }
        public LogVerbosity LogVerbosityType { get; private set; } = LogVerbosity.Full;
        public LogFlow LogFlowType { get; private set; } = LogFlow.Console;
        
        #endregion

        #region Api
        
        public string ApiBaseAddress { get; private set; } = null!;
        public string ApiUsbEndPoint { get; private set; } = null!;
        public uint ApiPort { get; private set; }

        #endregion

        #region Cache
        
        public string CacheFileName { get; private set; } = null!;
        public uint MaxRetries { get; private set; }
        public uint MaxEntries { get; private set; }
        public uint RetryPeriod { get; private set; }
        
        #endregion

        #region Detection
        public string T32ProcessName { get; private set; } = null!;
        public uint DetectionPeriod { get; private set; }
        public string T32InfoLocation { get; private set; } = null!;
        public string F32RemExecutable { get; private set; } = null!;
        public uint FetchInfoMaxAttempts { get; private set;  }
        public uint FetchInfoAttemptPeriod { get; private set; }
        public string[] F32RemArguments { get; private set; } = null!;
        public int T32RemSuccessExitCode { get; private set; }
        public int T32RemWaitTimeoutMs { get; private set; }

        #endregion

        public ConfigLoader() {
            var configuration = new ConfigurationBuilder()
                .AddJsonFile(ConfigFile)
                .Build();

            ReadLoggerSection(configuration);
            ReadApiSection(configuration);
            ReadCacheSection(configuration);
            ReadDebuggerSection(configuration);
            
            Console.WriteLine("Configuration successfully loaded!");
        }

        private void ReadLoggerSection(IConfiguration configuration) {
            try {
                var logging = configuration.GetSection(LoggingSection);
                LogChunkSize = int.Parse(logging["LogChunkSize"]);
                LogChunkMaxCount = int.Parse(logging["LogChunkMaxCount"]);
                LogArchiveMaxCount = int.Parse(logging["LogArchiveMaxCount"]);
                LogCleanupPeriod = int.Parse(logging["LogCleanupPeriod"]);
                LogFlowType = (LogFlow)int.Parse(logging["LogFlowType"]);
                LogVerbosityType = (LogVerbosity)int.Parse(logging["LogVerbosityType"]);
            } catch (Exception e) {
                Console.WriteLine(e.Message);
                Environment.Exit(ErrorExitCode);
            }
        }

        private void ReadApiSection(IConfiguration configuration) {
            try {
                var network = configuration.GetSection(NetworkSection);
                ApiBaseAddress = network["ApiBaseAddress"];
                ApiUsbEndPoint = network["ApiLDEndPoint"];
                ApiPort = uint.Parse(network["ApiPort"]);
            } catch (Exception e) {
                Console.WriteLine(e.Message);
                Environment.Exit(ErrorExitCode);
            }
        }

        private void ReadCacheSection(IConfiguration configuration) {
            try {
                var cache = configuration.GetSection(CacheSection);
                RetryPeriod = uint.Parse(cache["RetryPeriod"]);
                MaxEntries = uint.Parse(cache["MaxEntries"]);
                MaxRetries = uint.Parse(cache["MaxRetries"]);
                CacheFileName = cache["CacheFileName"];
            } catch (Exception e) {
                Console.WriteLine(e.Message);
                Environment.Exit(ErrorExitCode);
            }
        }

        private void ReadDebuggerSection(IConfiguration configuration) {
            try {
                var debugger = configuration.GetSection(DdSection);
                T32ProcessName = debugger["T32ProcessName"];
                T32InfoLocation = debugger["T32InfoLocation"];
                DetectionPeriod = uint.Parse(debugger["DetectionPeriod"]);
                F32RemExecutable = debugger["F32RemExecutable"];
                FetchInfoMaxAttempts = uint.Parse(debugger["FetchInfoMaxAttempts"]);
                FetchInfoAttemptPeriod = uint.Parse(debugger["FetchInfoAttemptPeriod"]);
                T32RemSuccessExitCode = int.Parse(debugger["T32RemSuccessExitCode"]);
                T32RemWaitTimeoutMs = int.Parse(debugger["T32RemWaitTimeoutMs"]);
                F32RemArguments = configuration.GetSection($"{DdSection}:F32RemArguments").GetChildren().Select(key => key.Value).ToArray();
            } catch (Exception e) {
                Console.WriteLine(e);
                Environment.Exit(ErrorExitCode);
            }
        }
    }
}
