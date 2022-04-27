using System.Diagnostics;
using LDClient.utils;
using LDClient.utils.loggers;

namespace LDClient.detection {

    public class InfoFetcher : IInfoFetcher {
        
        private const string UndefinedSerialNumber = "number";

        private readonly string _f32RemExecutable;
        private readonly string[] _f32RemArguments;
        private readonly int _f32SuccessExitCode;
        private readonly int _f32WaitTimeoutMs;
        private readonly uint _maxAttempts;
        private readonly uint _waitPeriodMs;
        private readonly string _infoFilePath;

        public IProcessUtils ProcessUtils;
        public IFileUtils FileUtils;

        public string HeadSerialNumber { get; set; } = UndefinedSerialNumber;
        public string BodySerialNumber { get; set; } = UndefinedSerialNumber;


        public InfoFetcher(uint maxAttempts, uint waitPeriodMs, string infoFilePath, string f32RemExecutable,
            string[] f32RemArguments, int f32SuccessExitCode, int f32WaitTimeoutMs) {
            _maxAttempts = maxAttempts;
            _waitPeriodMs = waitPeriodMs;
            _infoFilePath = infoFilePath;
            _f32RemExecutable = f32RemExecutable;
            _f32RemArguments = f32RemArguments;
            _f32SuccessExitCode = f32SuccessExitCode;
            _f32WaitTimeoutMs = f32WaitTimeoutMs;
            ProcessUtils = new ProcessUtils();
            FileUtils = new FileUtils();

        }

        public async Task<bool> FetchDataAsync() {
            Program.DefaultLogger.Info("Fetching data from the debugger.");
            var success = SendRetrieveInfoCommands(_f32RemExecutable, _f32RemArguments, _f32SuccessExitCode, _f32WaitTimeoutMs);
            if (!success) {
                Program.DefaultLogger.Error("Failed to fetch data from the debugger.");
                return false;
            }
            for (var i = 0; i < _maxAttempts; i++) {
                Program.DefaultLogger.Info($"{i}. attempt to parse the info file.");
                if (RetrieveDebuggerInfo(_infoFilePath)) {
                    Program.DefaultLogger.Info($"Info file has been parsed successfully.");
                    return true;
                }
                await Task.Delay((int)_waitPeriodMs);
            }
            Program.DefaultLogger.Error("Failed to parse the into file. It may have not been created.");
            return false;
        }

        private bool RetrieveDebuggerInfo(string filePath) {
            try {
                var fileContent = FileUtils.ReadFileAllLines(filePath).Aggregate("", (current, line) => $"{current}{line}\n");
                var (headSerialNumber, bodySerialNumber) = DebuggerInfoParser.Parse(fileContent);
                HeadSerialNumber = headSerialNumber;
                BodySerialNumber = bodySerialNumber;
                File.Delete(filePath);
            } catch (Exception exception) {
                Program.DefaultLogger.Error($"Failed to retrieve debugger info. File {filePath} may not exist or it does not have the right format. {exception.Message}");
                return false;
            }
            return true;
        }

        private bool SendRetrieveInfoCommands(string executableFile, IReadOnlyList<string>? arguments, int desiredExitCode, int waitTimeoutMs) {
            if (arguments == null) {
                Program.DefaultLogger.Error($"Failed to run {executableFile} - no parameters were given");
                return false;
            }
            foreach (var argument in arguments) {
                if (!ProcessUtils.ExecuteNewProcess(executableFile, argument, waitTimeoutMs, desiredExitCode)) {
                    return false;
                }
            }
            return true;
        }
    }
}