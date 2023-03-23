namespace LDClient.detection
{
    public class T32RemFetcher : AInfoFetcher
    {
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
        /// Instance of ProcessUtils which encapsulates common functionality
        /// when it comes to dealing with processes (limited by the needs of this application).
        /// </summary>
        public IProcessUtils ProcessUtils;

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
        public T32RemFetcher(uint maxAttempts, uint waitPeriodMs, uint practiceScriptPollingPeriodMs, string infoFilePath, string f32RemExecutable,
            string[] f32RemArguments, int f32SuccessExitCode, int f32WaitTimeoutMs) : base(maxAttempts, waitPeriodMs, practiceScriptPollingPeriodMs, infoFilePath)
        {
            _f32RemExecutable = f32RemExecutable;
            _f32RemArguments = f32RemArguments;
            _f32SuccessExitCode = f32SuccessExitCode;
            _f32WaitTimeoutMs = f32WaitTimeoutMs;
            ProcessUtils = new ProcessUtils();
        }

        /// <summary>
        /// Method tries to fetch the data from the trace32 application
        /// via defined executable 
        /// </summary>
        /// <returns>true upon success</returns>
        protected override bool FetchData()
        {
            if (_f32RemArguments == null)
            {
                Program.DefaultLogger.Error($"Failed to run {_f32RemExecutable} - no parameters were given");
                return false;
            }

            // Execute one all arguments (commands) one by one.
            foreach (var argument in _f32RemArguments)
            {
                if (!ProcessUtils.ExecuteNewProcess(_f32RemExecutable, argument, _f32WaitTimeoutMs, _f32SuccessExitCode))
                {
                    return false;
                }
            }
            return true;
        }
    }
}