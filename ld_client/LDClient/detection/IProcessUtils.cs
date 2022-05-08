using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.detection {
    
    /// <summary>
    /// This interface defines the functionality of all methods that
    /// are used to work with processes (within this project).
    /// </summary>
    public interface IProcessUtils {
        
        /// <summary>
        /// Checks if a process is running or not.
        /// </summary>
        /// <param name="name">Name of the process</param>
        /// <returns>True, if the process is running. False otherwise.</returns>
        public bool IsProcessRunning(string name);

        /// <summary>
        /// Executes a new process (t32rem.exe) with arguments which are passed in
        /// as a parameter of the method.
        /// </summary>
        /// <param name="fileName">Path to the .exe file</param>
        /// <param name="argument">Arguments passed into the .exe file</param>
        /// <param name="timeout">Timeout used when waiting for the process to terminate</param>
        /// <param name="desiredExitCode">Status code indicating a successful termination of the process.</param>
        /// <returns>True, if the command was executed successfully. False otherwise.</returns>
        public bool ExecuteNewProcess(string fileName, string argument, int timeout, int desiredExitCode);
    }
}
