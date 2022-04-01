using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Configuration.Json;

namespace LDClient {
    internal class ConfigurationLoader {

        private readonly string LOGGING_SECTION = "Logging";


        public int LogChunkSize { get; set; }
        public int LogChunkMaxCount { get; set; }
        public int LogArchiveMaxCount { get; set; }

        public int LogCleanupPeriod { get; set; }

        private LogVerbosity _logVerbosity = LogVerbosity.Full;
        public LogVerbosity LogVerbosityType {
            get {
                return _logVerbosity;
            } 
            set 
                { _logVerbosity = value; 
            } 
        }

        private LogFlow _logFlowType = LogFlow.Console;
        public LogFlow LogFlowType { 
            get {
                return _logFlowType;
            } 
            set {
                _logFlowType = value;
            } 
        }

        public ConfigurationLoader() {
            var configuration = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json")
                .Build();
            ReadAllSettings(configuration);
        }

        void ReadAllSettings(IConfigurationRoot configuration) {

            try {
                var logging = configuration.GetSection(LOGGING_SECTION);
                //TODO: Exception handling
                LogChunkSize = Int32.Parse(logging["LogChunkSize"]);
                LogChunkMaxCount = Int32.Parse(logging["LogChunkMaxCount"]);
                LogArchiveMaxCount = Int32.Parse(logging["LogArchiveMaxCount"]);
                LogCleanupPeriod = Int32.Parse(logging["LogCleanupPeriod"]);
                LogFlowType = (LogFlow)Int32.Parse(logging["LogFlowType"]);
                LogVerbosityType = (LogVerbosity)Int32.Parse(logging["LogVerbosityType"]);


                Console.WriteLine("Configuration successfully loaded!");
            } catch (FormatException e) {
                //Console.WriteLine("Error reading app settings");
                //TODO: remove stacktrace print in production
                Console.WriteLine("Error during reading of configuration occured!" + e);
                throw new IOException("Reading of configuration file failed! " + e);
            }
        }

    }
}
