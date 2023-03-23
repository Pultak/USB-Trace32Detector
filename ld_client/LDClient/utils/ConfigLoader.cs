using LDClient.utils.loggers;
using Microsoft.Extensions.Configuration;
using System;
using System.Linq;

namespace LDClient.utils
{
    /// <summary>
    /// This class loads up the configuration file (appsettingss.json).
    /// </summary>
    internal class ConfigLoader
    {
        /// <summary>
        /// Status code indicating a successful termination of an application.
        /// </summary>
        private const int ErrorExitCode = 1;

        /// <summary>
        /// Path to the configuration file.
        /// </summary>
        private const string ConfigFile = "appsettings.json";

        /// <summary>
        /// Name of the logging section defined in the config file.
        /// </summary>
        private const string LoggingSection = "Logging";

        /// <summary>
        /// Name of the network section defined in the config file.
        /// </summary>
        private const string NetworkSection = "Network";

        /// <summary>
        /// Name of the cache section defined in the config file.
        /// </summary>
        private const string CacheSection = "Cache";

        /// <summary>
        /// Name of the detection section defined in the config file.
        /// </summary>
        private const string DdSection = "DebuggerDetection";

        #region Logger

        /// <summary>
        /// Maximum size of the log file (it will start to rotate when this limit is reached).
        /// </summary>
        public int LogChunkSize { get; private set; }

        /// <summary>
        /// Number of files to be created until there will be zipped up.
        /// </summary>
        public int LogChunkMaxCount { get; private set; }

        /// <summary>
        /// Maximum number of zip files
        /// </summary>
        public int LogArchiveMaxCount { get; private set; }

        /// <summary>
        /// Time after which the last logs will be cleaned up.
        /// </summary>
        public int LogCleanupPeriod { get; private set; }

        /// <summary>
        /// Level of verbosity.
        /// </summary>
        public LogVerbosity LogVerbosityType { get; private set; } = LogVerbosity.Full;

        /// <summary>
        /// Logger flow type.
        /// </summary>
        public LogFlow LogFlowType { get; private set; } = LogFlow.Console;

        #endregion

        #region Api

        /// <summary>
        /// URL to the API (it can be an IP address or a domain name if a DNS server is being used).
        /// </summary>
        public string ApiBaseAddress { get; private set; } = null!;

        /// <summary>
        /// Path to the API (e.g. /api/v1/ld-logs).
        /// </summary>
        public string ApiUsbEndPoint { get; private set; } = null!;

        /// <summary>
        /// Number of the port that the API runs on.
        /// </summary>
        public uint ApiPort { get; private set; }

        #endregion

        #region Cache

        /// <summary>
        /// Name of the cache (a directory of this name will be created).
        /// </summary>
        public string CacheFileName { get; private set; } = null!;

        /// <summary>
        /// Maximum number of payloads (entries) to be sent to the server at a time.
        /// </summary>
        public uint MaxRetries { get; private set; }

        /// <summary>
        /// Maximum number of entries that can be stored in the database.
        /// </summary>
        public uint MaxEntries { get; private set; }

        /// <summary>
        /// Period (how often) a certain number of entries will be resent to the server.
        /// </summary>
        public uint RetryPeriod { get; private set; }

        #endregion

        #region Detection

        /// <summary>
        /// Name of the process to be detected (the application programmers use to connect to the debugger).
        /// </summary>
        public string T32ProcessName { get; private set; } = null!;

        /// <summary>
        /// How often the application checks if there is the process (T32ProcessName) running on the PC.
        /// </summary>
        public uint DetectionPeriod { get; private set; }

        /// <summary>
        /// Location of the generated .txt file containing all information about a debugger.
        /// </summary>
        public string T32InfoLocation { get; private set; } = null!;

        /// <summary>
        /// Path to the t32rem.exe which is used to send commands to a debugger.
        /// </summary>
        public string T32RemExecutable { get; private set; } = null!;

        /// <summary>
        /// How many times the application attempts to check if there
        /// has been a .txt file generated containing all the desired information.
        /// </summary>
        public uint FetchInfoMaxAttempts { get; private set; }

        /// <summary>
        /// Period in milliseconds after which the application tries to locate and parse the .txt file. 
        /// </summary>
        public uint FetchInfoAttemptPeriod { get; private set; }

        /// <summary>
        /// Status code indication successful execution of the t32rem.exe file.
        /// </summary>
        public int T32RemSuccessExitCode { get; private set; }

        /// <summary>
        /// Timeout of the execution of t32rem.exe (when sending one command).
        /// </summary>
        public int T32RemWaitTimeoutMs { get; private set; }


        /// <summary>
        /// List of commands to be executed by though the t32 api
        /// </summary>
        public string[] T32ApiCommands { get; private set; } = null!;

        /// <summary>
        /// Address of the listening t32 application
        /// </summary>
        public string T32ApiAddress { get; private set; } = null!;

        /// <summary>
        /// Port of the listening t32 application
        /// </summary>
        public string T32ApiPort { get; private set; } = null!;

        /// <summary>
        /// Size of the packets send/received from t32 application
        /// </summary>
        public string T32ApiPacketLen { get; private set; } = null!;

        /// <summary>
        /// Superior number of attempts to fetch the information (outer loop).
        /// </summary>
        public uint FetchInfoSuperiorMaxAttempts { get; private set; }

        /// <summary>
        /// Period of the superior (outer) loop to fetch the data.
        /// </summary>
        public uint FetchInfoSuperiorAttemptPeriod { get; private set; }

        /// <summary>
        /// Polling period [ms] used when checking if a practice script has terminated
        /// </summary>
        public uint PracticeScriptPollingPeriodMs { get; private set; }

        /// <summary>
        /// Name of the practice script containing all commands sent to Trace32
        /// </summary>
        public string PracticeScriptName { get; private set; }

        #endregion

        /// <summary>
        /// Creates an instance of the class.
        /// </summary>
        public ConfigLoader()
        {
            // Create a new config builder to read the configuration file.
            var configuration = new ConfigurationBuilder()
                .AddJsonFile(ConfigFile)
                .Build();

            // Parse the logger section.
            ReadLoggerSection(configuration);

            // Parse the api section. 
            ReadApiSection(configuration);

            // Parse the cache section.
            ReadCacheSection(configuration);

            // Parse the detection section.
            ReadDebuggerSection(configuration);

            Console.WriteLine("Configuration successfully loaded!");
        }

        /// <summary>
        /// Parses the logging section of the configuration file.
        /// </summary>
        /// <param name="configuration">configuration</param>
        private void ReadLoggerSection(IConfiguration configuration)
        {
            try
            {
                var logging = configuration.GetSection(LoggingSection);
                LogChunkSize = int.Parse(logging["LogChunkSize"]);
                LogChunkMaxCount = int.Parse(logging["LogChunkMaxCount"]);
                LogArchiveMaxCount = int.Parse(logging["LogArchiveMaxCount"]);
                LogCleanupPeriod = int.Parse(logging["LogCleanupPeriod"]);
                LogFlowType = (LogFlow)int.Parse(logging["LogFlowType"]);
                LogVerbosityType = (LogVerbosity)int.Parse(logging["LogVerbosityType"]);
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                Environment.Exit(ErrorExitCode);
            }
        }

        /// <summary>
        /// Parses the api section of the configuration file.
        /// </summary>
        /// <param name="configuration">configuration</param>
        private void ReadApiSection(IConfiguration configuration)
        {
            try
            {
                var network = configuration.GetSection(NetworkSection);
                ApiBaseAddress = network["ApiBaseAddress"];
                ApiUsbEndPoint = network["ApiLDEndPoint"];
                ApiPort = uint.Parse(network["ApiPort"]);
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                Environment.Exit(ErrorExitCode);
            }
        }

        /// <summary>
        /// Parses the cache section of the configuration file.
        /// </summary>
        /// <param name="configuration">configuration</param>
        private void ReadCacheSection(IConfiguration configuration)
        {
            try
            {
                var cache = configuration.GetSection(CacheSection);
                RetryPeriod = uint.Parse(cache["RetryPeriod"]);
                MaxEntries = uint.Parse(cache["MaxEntries"]);
                MaxRetries = uint.Parse(cache["MaxRetries"]);
                CacheFileName = cache["CacheFileName"];
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                Environment.Exit(ErrorExitCode);
            }
        }

        /// <summary>
        /// Parses the detection section of the configuration file.
        /// </summary>
        /// <param name="configuration">configuration</param>
        private void ReadDebuggerSection(IConfiguration configuration)
        {
            try
            {
                var debugger = configuration.GetSection(DdSection);
                T32ProcessName = debugger["T32ProcessName"];
                T32InfoLocation = debugger["T32InfoLocation"];
                DetectionPeriod = uint.Parse(debugger["DetectionPeriod"]);
                T32RemExecutable = debugger["T32RemExecutable"];
                FetchInfoMaxAttempts = uint.Parse(debugger["FetchInfoMaxAttempts"]);
                FetchInfoAttemptPeriod = uint.Parse(debugger["FetchInfoAttemptPeriod"]);
                T32RemSuccessExitCode = int.Parse(debugger["T32RemSuccessExitCode"]);
                T32RemWaitTimeoutMs = int.Parse(debugger["T32RemWaitTimeoutMs"]);
                T32ApiCommands = configuration.GetSection($"{DdSection}:T32ApiCommands").GetChildren().Select(key => key.Value).ToArray();
                T32ApiAddress = debugger["T32ApiAddress"];
                T32ApiPort = debugger["T32ApiPort"];
                T32ApiPacketLen = debugger["T32ApiPacketLen"];
                FetchInfoSuperiorMaxAttempts = uint.Parse(debugger["FetchInfoSuperiorMaxAttempts"]);
                FetchInfoSuperiorAttemptPeriod = uint.Parse(debugger["FetchInfoSuperiorAttemptPeriod"]);
                PracticeScriptPollingPeriodMs = uint.Parse(debugger["PracticeScriptPollingPeriodMs"]);
                PracticeScriptName = debugger["PracticeScriptName"];
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
                Environment.Exit(ErrorExitCode);
            }
        }
    }
}
