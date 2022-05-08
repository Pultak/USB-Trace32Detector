using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.detection {

    public class T32ApiFetcher : AInfoFetcher, IT32Utils {
#if _WINDOWS
        private const string T32DllLibrary = "./lib/t32api64.dll";
#else
        private const string T32DllLibrary = "./lib/t32api64.so";
#endif

        private readonly string _t32Address;
        private readonly string _t32Port;
        private readonly string _t32PacketLength;
        private readonly string[] _commands;

        public T32ApiFetcher(uint maxAttempts, uint waitPeriodMs, string infoFilePath, string t32Address, 
            string t32Port, string t32PacketLength, string[] commands) : base(maxAttempts, waitPeriodMs, infoFilePath) {
            this._t32Address = t32Address;
            this._t32Port = t32Port;
            this._t32PacketLength = t32PacketLength;
            this._commands = commands;
        }


        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Config(string s1, string s2);

        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Init();

        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Attach(int dev);

        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Cmd(string command);

        [DllImport(T32DllLibrary, CharSet = CharSet.Ansi)]
        private static extern int T32_Exit();
        
        public bool InitConnection() {
            Program.DefaultLogger.Debug("Trace32 connection initialization");
            var config1 = T32_Config("NODE=", _t32Address);
            var config2 = T32_Config("PORT=", _t32Port);
            var config3 = T32_Config("PACKLEN=", _t32PacketLength);

            if (config1 != 0 || config2 != 0 || config3 != 0) {
                Program.DefaultLogger.Error("Trace32 API connection configuration failed.");
                return false;
            }
            var init = T32_Init();
            if (init != 0) {
                Program.DefaultLogger.Error("Trace32 API connection init failed.");
                return false;
            }

            var attach = T32_Attach(1);
            if (attach != 0) {
                Program.DefaultLogger.Error("Trace32 API connection attach failed.");
            }

            Program.DefaultLogger.Info("Trace32 connection established");
            return true;
        }

        public bool ExecuteCommands() {
            Program.DefaultLogger.Info("Trace32 API commands execution.");
            foreach (var command in _commands) {
                Program.DefaultLogger.Debug($"Executing Trace32 command '{command}'.");
                var ret = T32_Cmd(command);
                if (ret != 0) {
                    Program.DefaultLogger.Error($"Execution of command '{command}' failed. Return code {ret}.");
                    return false;
                }
            }
            Program.DefaultLogger.Info("All Trace32 commands executed successfully.");
            return true;
        }

        public bool CloseConnection() {
            Program.DefaultLogger.Debug("Trace32 connection exit");
            return T32_Exit() == 0;
        }

        protected override bool FetchData() {
            var connected = false;
            for (var i = 0; i < _maxAttempts; i++) {
                connected = InitConnection();
                if (connected) {
                    break;
                }
                Thread.Sleep((int)_waitPeriodMs);

            }
            return connected && ExecuteCommands() && CloseConnection();
        }
    }
}
