using System.Runtime.InteropServices;
using LDClient.utils.loggers;
using Microsoft.Extensions.Configuration;

namespace LDClient.utils {
    
    internal class ConfigLoader {
        
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
        
        public string ApiBaseAddress { get; private set; }
        public string ApiUsbEndPoint { get; private set; }
        public uint ApiPort { get; private set; }

        #endregion

        #region Cache
        
        public string CacheFileName { get; private set; }
        public uint MaxRetries { get; private set; }
        public uint MaxEntries { get; private set; }
        public uint RetryPeriod { get; private set; }
        
        #endregion

        #region Detection
        public string T32ProcessName { get; private set; }
        public uint DetectionPeriod { get; private set; }
        public string T32InfoLocation { get; private set; }
        public string F32RemExecutable { get; private set; }
        public string F32RemArguments { get; private set; }
        public uint FetchInfoMaxAttempts { get; private set;  }
        public uint FetchInfoAttemptPeriod { get; private set; }
        
        #endregion

        public ConfigLoader() {
            var configuration = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json")
                .Build();
            ReadAllSettings(configuration);
        }

        private void ReadAllSettings(IConfiguration configuration) {

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
                
                var debugger = configuration.GetSection(DdSection);
                T32ProcessName = debugger["T32ProcessName"];
                T32InfoLocation = debugger["T32InfoLocation"];
                DetectionPeriod = uint.Parse(debugger["DetectionPeriod"]);
                F32RemExecutable = debugger["F32RemExecutable"];
                F32RemArguments = debugger["F32RemArguments"];
                FetchInfoMaxAttempts = uint.Parse(debugger["FetchInfoMaxAttempts"]);
                FetchInfoAttemptPeriod = uint.Parse(debugger["FetchInfoAttemptPeriod"]);

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
