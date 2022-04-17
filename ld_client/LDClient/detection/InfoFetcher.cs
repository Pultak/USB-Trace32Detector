using System.Diagnostics;
using LDClient.utils;

namespace LDClient.detection {

    public class InfoFetcher {

        private const string F32RemExecutable = "/home/silhavyj/School/KIV-ASWI/aswi2022bug-thugs/ld_client/Mock/t32rem/build/t32rem_mock";
        private const string F32RemArguments = "localhost port=20000 VERSION.HARDWARE";
        private const string UndefinedSerialNumber = "number";

        private readonly int _maxAttempts;
        private readonly int _waitPeriodMs;
        private readonly string _infoFilePath;

        public string HeadSerialNumber { get; private set; } = UndefinedSerialNumber;
        public string BodySerialNumber { get; private set; } = UndefinedSerialNumber;

        public InfoFetcher(int maxAttempts, int waitPeriodMs, string infoFilePath) {
            _maxAttempts = maxAttempts;
            _waitPeriodMs = waitPeriodMs;
            _infoFilePath = infoFilePath;
        }

        public async Task<bool> FetchDataAsync() {
            Program.DefaultLogger.Info("Fetching data from the debugger.");
            var success = await SendRetrieveInfoCommandAsync(F32RemExecutable, F32RemArguments);
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
                await Task.Delay(_waitPeriodMs);
            }
            Program.DefaultLogger.Error("Failed to parse the into file. It may have not been created.");
            return false;
        }

        private bool RetrieveDebuggerInfo(string filePath) {
            try {
                var fileContent = IoUtils.ReadFile(filePath);
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

        private static async Task<bool> SendRetrieveInfoCommandAsync(string executableFile, string arguments) {
            var t32RemProcess = new Process();
            t32RemProcess.StartInfo.FileName = executableFile;
            t32RemProcess.StartInfo.Arguments = arguments;
            try {
                t32RemProcess.Start();
                await t32RemProcess.WaitForExitAsync();
            } catch (Exception exception) {
                Program.DefaultLogger.Error($"Failed to run {executableFile}. {exception.Message}");
                return false;
            }
            return true;
        }
    }
}