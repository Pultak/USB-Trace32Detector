using LDClient.utils.loggers;
using Microsoft.Extensions.Configuration;

namespace LDClient.utils {
    internal class ConfigLoader {
        private const string LoggingSection = "Logging";


        public int LogChunkSize { get; set; }
        public int LogChunkMaxCount { get; set; }
        public int LogArchiveMaxCount { get; set; }

        public int LogCleanupPeriod { get; set; }

        public LogVerbosity LogVerbosityType { get; set; } = LogVerbosity.Full;

        public LogFlow LogFlowType { get; set; } = LogFlow.Console;

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
