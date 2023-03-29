using System.Threading;
using System.Runtime.InteropServices;
using System;
using System.IO;

namespace LDClient.detection
{
    public class T32ApiFetcher : AInfoFetcher, IT32Utils
    {
#if _WINDOWS
        /// <summary>
        /// Path to the Trace32 API library
        /// </summary>
        private const string T32DllLibrary = "./lib/t32api.dll";
#else
        private const string T32DllLibrary = "./lib/t32api.so";
#endif
        /// <summary>
        /// Address of the listening t32 application
        /// </summary>
        private readonly string _t32Address;

        /// <summary>
        ///  Port of the listening t32 application
        /// </summary>
        private readonly string _t32Port;

        /// <summary>
        /// Size of the packets send/received from t32 application
        /// </summary>
        private readonly string _t32PacketLength;

        /// <summary>
        /// List of commands to be executed by though the t32 api
        /// </summary>
        private readonly string[] _commands;

        /// <summary>
        /// Absolute path to the practice script
        /// </summary>
        private readonly string _practiceScriptAbsolutePath;

        /// <summary>
        /// 
        /// </summary>
        /// <param name="maxAttempts">Maximum number of attempts to locate and parse the .txt file</param>
        /// <param name="waitPeriodMs">Period (how often) the application tries to locate and parse the .txt file</param>
        /// <param name="infoFilePath">Path to the .txt file which is generated from the debugger</param>
        /// <param name="t32Address">Address of the listening t32 application</param>
        /// <param name="t32Port">Port of the listening t32 application</param>
        /// <param name="t32PacketLength"> Size of the packets send/received from t32 application </param>
        /// <param name="commands"> List of commands to be executed by though the t32 api</param>
        public T32ApiFetcher(uint maxAttempts, uint waitPeriodMs, string infoFilePath, string t32Address,
            string t32Port, string t32PacketLength, uint practiceScriptPollingPeriodMs, string[] commands, string practiceScriptName) : base(maxAttempts, waitPeriodMs, practiceScriptPollingPeriodMs, infoFilePath)
        {
            this._t32Address = t32Address;
            this._t32Port = t32Port;
            this._t32PacketLength = t32PacketLength;
            this._commands = commands;
            
            string practiceScript = string.Join("\n", commands);

            File.WriteAllText(practiceScriptName, practiceScript);
            _practiceScriptAbsolutePath = Path.GetFullPath(practiceScriptName);
        }

        /// <summary>
        /// To see full documentation of following T32 API methods please check the https://www2.lauterbach.com/pdf/api_remote_c.pdf
        /// </summary>
        /// <param name="s1"></param>
        /// <param name="s2"></param>
        /// <returns>return code</returns>
        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Config(string s1, string s2);

        /// <summary>
        /// To see full documentation of following T32 API methods please check the https://www2.lauterbach.com/pdf/api_remote_c.pdf
        /// </summary>
        /// <returns>Return code</returns>
        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Init();

        /// <summary>
        /// To see full documentation of following T32 API methods please check the https://www2.lauterbach.com/pdf/api_remote_c.pdf
        /// </summary>
        /// <param name="dev"></param>
        /// <returns>Return code</returns>
        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Attach(int dev);

        /// <summary>
        /// To see full documentation of following T32 API methods please check the https://www2.lauterbach.com/pdf/api_remote_c.pdf
        /// </summary>
        /// <param name="command"></param>
        /// <returns>Return code</returns>
        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Cmd(string command);

        /// <summary>
        /// To see full documentation of following T32 API methods please check the https://www2.lauterbach.com/pdf/api_remote_c.pdf
        /// </summary>
        /// <returns>Return code</returns>
        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Exit();

        /// <summary>
        /// To see full documentation of following T32 API methods please check the https://www2.lauterbach.com/pdf/api_remote_c.pdf
        /// </summary>
        /// <param name="pstate"></param>
        /// <returns>Return code</returns>
        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_GetPracticeState(ref int pstate);

        /// <summary>
        /// To see full documentation of following T32 API methods please check the https://www2.lauterbach.com/pdf/api_remote_c.pdf
        /// </summary>
        /// <param name="command"></param>
        /// <param name="commands"></param>
        /// <returns></returns>
        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Cmd_f(string command, params string[] commands);

        private void WaitForPracticeScriptTermination(int pollingPeriodMs)
        {
            int pstate = 0;

            while (T32_GetPracticeState(ref pstate) == 0 && pstate != 0)
            {
                Thread.Sleep(pollingPeriodMs);
            }
        }

        private bool ExecutePracticeScript(string practiceScriptPath)
        {
            Program.DefaultLogger.Debug("Waiting for any potential running practice script to finish");
            WaitForPracticeScriptTermination((int)_practiceScriptPollingPeriodMs);
            Program.DefaultLogger.Debug("All previously running practice scripts have finished");

            if (T32_Cmd_f("DO " + practiceScriptPath) != 0)
            {
                return false;
            }

            WaitForPracticeScriptTermination((int)_practiceScriptPollingPeriodMs);

            return true;
        }

        /// <summary>
        /// This method initialized the connection with the trace32 application API.
        /// It setups the standard connection configuration a tries to connect to the API
        /// </summary>
        /// <returns>true on success</returns>
        public bool InitConnection()
        {
            Program.DefaultLogger.Debug("Trace32 connection initialization");
            var config1 = T32_Config("NODE=", _t32Address);
            var config2 = T32_Config("PORT=", _t32Port);
            var config3 = T32_Config("PACKLEN=", _t32PacketLength);

            if (config1 != 0 || config2 != 0 || config3 != 0)
            {
                Program.DefaultLogger.Error("Trace32 API connection configuration failed.");
                return false;
            }
            var init = T32_Init();
            if (init != 0)
            {
                Program.DefaultLogger.Error("Trace32 API connection init failed.");
                return false;
            }

            var attach = T32_Attach(1);
            if (attach != 0)
            {
                Program.DefaultLogger.Error("Trace32 API connection attach failed.");
            }

            Program.DefaultLogger.Info("Trace32 connection established");
            return true;
        }

        /// <summary>
        /// Method executes all passed commands though the trace32 API
        /// </summary>
        /// <returns>true on success</returns>
        public bool ExecuteCommands()
        {
            Program.DefaultLogger.Info("Trace32 API commands execution.");
            foreach (var command in _commands)
            {
                Program.DefaultLogger.Debug("Waiting for any potential running practice script to finish");
                WaitForPracticeScriptTermination((int)_practiceScriptPollingPeriodMs);
                Program.DefaultLogger.Debug("All previously running practice scripts have finished");

                Program.DefaultLogger.Debug($"Executing Trace32 command '{command}'.");
                var ret = T32_Cmd(command);
                if (ret != 0)
                {
                    Program.DefaultLogger.Error($"Execution of command '{command}' failed. Return code {ret}.");
                    return false;
                }
            }
            Program.DefaultLogger.Info("All Trace32 commands executed successfully.");
            return true;
        }

        /// <summary>
        /// This method closes the connection with the trace32 application api
        /// </summary>
        /// <returns>true on success</returns>
        public bool CloseConnection()
        {
            Program.DefaultLogger.Debug("Trace32 connection exit");
            return T32_Exit() == 0;
        }

        /// <summary>
        /// Method tries to fetch the data from the trace32 application.
        /// Upon connection fail it tries again for specified number of times
        /// </summary>
        /// <returns>true on success</returns>
        protected override bool FetchData()
        {
            var connected = false;
            for (var i = 0; i < _maxAttempts; i++)
            {
                connected = InitConnection();
                if (connected)
                {
                    break;
                }
                Thread.Sleep((int)_waitPeriodMs);
            }

            // return connected && ExecuteCommands() && CloseConnection();
            return connected && ExecutePracticeScript(_practiceScriptAbsolutePath) && CloseConnection();
        }
    }
}