using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.detection {
    public class ProcessUtils : IProcessUtils{

        public bool IsProcessRunning(string name) {
            return Process.GetProcessesByName(name).Length > 0;
        }


        public bool ExecuteNewProcess(string fileName, string argument, int timeout, int desiredExitCode) {

            var t32RemProcess = new Process();
            t32RemProcess.StartInfo.FileName = fileName;
            t32RemProcess.StartInfo.Arguments = argument;
            try {
                t32RemProcess.Start();
                if (!t32RemProcess.WaitForExit(timeout)) {
                    Program.DefaultLogger.Error($"Execution has not terminated within a predefined timeout of {timeout} ms");
                    return false;
                }
                if (t32RemProcess.ExitCode != desiredExitCode) {
                    Program.DefaultLogger.Error($"Execution terminated with an error code of {t32RemProcess.ExitCode}");
                    return false;
                }
            } catch (Exception exception) {
                Program.DefaultLogger.Error($"Failed to run {fileName} {argument}. {exception.Message}");
                return false;
            }

            return true;
        }

    }
}
