using System.Diagnostics;

namespace LDClient.detection; 

/// <summary>
/// This class implements the IProcessUtils interface.
/// It implements methods that are used when dealing with processes.
/// </summary>
public class ProcessUtils : IProcessUtils {

    /// <summary>
    /// Checks if a process is running or not.
    /// </summary>
    /// <param name="name">Name of the process</param>
    /// <returns>True, if the process is running. False otherwise.</returns>
    public bool IsProcessRunning(string name) {
        return Process.GetProcessesByName(name).Length > 0;
    }
        
    /// <summary>
    /// Executes a new process (t32rem.exe) with arguments which are passed in
    /// as a parameter of the method.
    /// </summary>
    /// <param name="fileName">Path to the .exe file</param>
    /// <param name="argument">Arguments passed into the .exe file</param>
    /// <param name="timeout">Timeout used when waiting for the process to terminate</param>
    /// <param name="desiredExitCode">Status code indicating a successful termination of the process.</param>
    /// <returns>True, if the command was executed successfully. False otherwise.</returns>
    public bool ExecuteNewProcess(string fileName, string argument, int timeout, int desiredExitCode) {
        // Create a new process.
        var t32RemProcess = new Process();
        t32RemProcess.StartInfo.FileName = fileName;
        t32RemProcess.StartInfo.Arguments = argument;
            
        try {
            // Execute the process and wait until it terminates or until the timeout is up.
            t32RemProcess.Start();
            if (!t32RemProcess.WaitForExit(timeout)) {
                Program.DefaultLogger.Error($"Execution has not terminated within a predefined timeout of {timeout} ms");
                return false;
            }
                
            // Check if the process terminated successfully.
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