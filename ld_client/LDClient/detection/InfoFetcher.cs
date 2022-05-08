using System.Diagnostics;
using LDClient.utils;
using LDClient.utils.loggers;

namespace LDClient.detection {

    /// <summary>
    /// This class implements the IInfoFetcher interface
    /// which defines the functionality of an info fetcher.
    /// </summary>
    public class InfoFetcher : IInfoFetcher {
        
        /// <summary>
        /// Default value of a serial number (undefined).
        /// </summary>
        private const string UndefinedSerialNumber = "number";

        /// <summary>
        /// Path to the t32rem.exe file which is used to send commands to the debugger.
        /// </summary>
        private readonly string _f32RemExecutable;
        
        /// <summary>
        /// Arguments (commands) sent to the debugger in order to generate a .txt file
        /// containing all the desired information.
        /// </summary>
        private readonly string[] _f32RemArguments;
        
        /// <summary>
        /// Status code indicating a successful termination of t32rem.exe
        /// </summary>
        private readonly int _f32SuccessExitCode;
        
        /// <summary>
        /// Timeout used when waiting for the t32rem.exe to finish.
        /// </summary>
        private readonly int _f32WaitTimeoutMs;
        
        /// <summary>
        /// Maximum number of attempts to locate and parse the .txt file.
        /// </summary>
        private readonly uint _maxAttempts;
        
        /// <summary>
        /// Period (how often) the application tries to locate and parse the .txt file.
        /// </summary>
        private readonly uint _waitPeriodMs;
        
        /// <summary>
        /// Path to the .txt file which is generated from the debugger.
        /// </summary>
        private readonly string _infoFilePath;

        /// <summary>
        /// Instance of ProcessUtils which encapsulates common functionality
        /// when it comes to dealing with processes (limited by the needs of this application).
        /// </summary>
        public IProcessUtils ProcessUtils;
        
        /// <summary>
        /// Instance of FileUtils which encapsulates common functionality
        /// when it comes to dealing with files (limited by the needs of this application).
        /// </summary>
        public IFileUtils FileUtils;

        /// <summary>
        /// Returns the head serial number of the debugger.
        /// </summary>
        public string HeadSerialNumber { get; set; } = UndefinedSerialNumber;
        
        /// <summary>
        /// Returns the body serial number of the debugger.
        /// </summary>
        public string BodySerialNumber { get; set; } = UndefinedSerialNumber;
        
        /// <summary>
        /// Creates an instance of this class.
        /// </summary>
        /// <param name="maxAttempts">Maximum number of attempts to locate and parse the .txt file</param>
        /// <param name="waitPeriodMs">Period (how often) the application tries to locate and parse the .txt file</param>
        /// <param name="infoFilePath">Path to the .txt file which is generated from the debugger</param>
        /// <param name="f32RemExecutable">Path to the t32rem.exe file which is used to send commands to the debugger</param>
        /// <param name="f32RemArguments">Arguments (commands) sent to the debugger in order to generate a .txt file containing all the desired information.</param>
        /// <param name="f32SuccessExitCode">Status code indicating a successful termination of t32rem.exe</param>
        /// <param name="f32WaitTimeoutMs">Timeout used when waiting for the t32rem.exe to finish</param>
        public InfoFetcher(uint maxAttempts, uint waitPeriodMs, string infoFilePath, string f32RemExecutable,
            string[] f32RemArguments, int f32SuccessExitCode, int f32WaitTimeoutMs) {
            // Store the parameters into the class variables.
            _maxAttempts = maxAttempts;
            _waitPeriodMs = waitPeriodMs;
            _infoFilePath = infoFilePath;
            _f32RemExecutable = f32RemExecutable;
            _f32RemArguments = f32RemArguments;
            _f32SuccessExitCode = f32SuccessExitCode;
            _f32WaitTimeoutMs = f32WaitTimeoutMs;
            
            // Create an instance of ProcessUtils.
            ProcessUtils = new ProcessUtils();
            
            // Create an instance of FileUtils.
            FileUtils = new FileUtils();
        }

        /// <summary>
        /// Fetches data from the debugger. It sends the commands defined
        /// in the appsettings.json file to the debugger and tries to
        /// parse the .txt (contains the serial numbers).
        /// </summary>
        /// <returns>True, if data was fetched successfully. False otherwise.</returns>
        public async Task<bool> FetchDataAsync() {
            Program.DefaultLogger.Info("Fetching data from the debugger.");
            
            // Send the commands to the debugger.
            var success = SendRetrieveInfoCommands(_f32RemExecutable, _f32RemArguments, _f32SuccessExitCode, _f32WaitTimeoutMs);
            
            // Make sure that all commands were sent and executed successfully.
            if (!success) {
                Program.DefaultLogger.Error("Failed to fetch data from the debugger.");
                return false;
            }
            
            // Periodically try to parse the .txt file. 
            for (var i = 0; i < _maxAttempts; i++) {
                Program.DefaultLogger.Info($"{i}. attempt to parse the info file.");
                
                // Try to parse .txt file.
                if (RetrieveDebuggerInfo(_infoFilePath)) {
                    Program.DefaultLogger.Info($"Info file has been parsed successfully.");
                    return true;
                }
                // Wait for a specified number of milliseconds.
                await Task.Delay((int)_waitPeriodMs);
            }
            Program.DefaultLogger.Error("Failed to parse the into file. It may have not been created.");
            return false;
        }

        /// <summary>
        /// Tries to retrieve information from the debugger.
        /// </summary>
        /// <param name="filePath">path to the .txt file that contains all information</param>
        /// <returns>True if the information was retrieved successfully. False, otherwise.</returns>
        private bool RetrieveDebuggerInfo(string filePath) {
            try {
                // Read the content of the .txt file.
                var fileContent = FileUtils.ReadFileAllLines(filePath).Aggregate("", (current, line) => $"{current}{line}\n");
                
                // Parse it (try to find the serial numbers)
                var (headSerialNumber, bodySerialNumber) = DebuggerInfoParser.Parse(fileContent);
                
                // Store the serial numbers into class variables (properties)
                HeadSerialNumber = headSerialNumber;
                BodySerialNumber = bodySerialNumber;
                
                // Finally, delete the file.
                File.Delete(filePath);
            } catch (Exception exception) {
                Program.DefaultLogger.Error($"Failed to retrieve debugger info. File {filePath} may not exist or it does not have the right format. {exception.Message}");
                return false;
            }
            return true;
        }

        /// <summary>
        /// Sends commands to the debugger.
        /// </summary>
        /// <param name="executableFile">Path to the t32rem.exe file</param>
        /// <param name="arguments">Arguments sent to the debugger through t32rem.exe (one argument is one command)</param>
        /// <param name="desiredExitCode">Status code indicating successful termination of t32rem.exe</param>
        /// <param name="waitTimeoutMs">Timeout used when waiting for t32rem.exe to finish</param>
        /// <returns>True if all the commands were executed successfully. False, otherwise.</returns>
        private bool SendRetrieveInfoCommands(string executableFile, IReadOnlyList<string>? arguments, int desiredExitCode, int waitTimeoutMs) {
            if (arguments == null) {
                Program.DefaultLogger.Error($"Failed to run {executableFile} - no parameters were given");
                return false;
            }
            // Execute one all arguments (commands) one by one.
            foreach (var argument in arguments) {
                if (!ProcessUtils.ExecuteNewProcess(executableFile, argument, waitTimeoutMs, desiredExitCode)) {
                    return false;
                }
            }
            return true;
        }
    }
}