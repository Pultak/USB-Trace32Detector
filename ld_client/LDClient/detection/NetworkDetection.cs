using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.detection {
    public class NetworkDetection : IDetection {

        private readonly uint _port;

        private bool _isRunning;
        
        private readonly uint _detectionPeriod;

        public NetworkDetection(uint port, uint detectionPeriod) {
            this._port = port;
            this._detectionPeriod = detectionPeriod;
        }

        public void DetectAsync() {

            var listeners = System.Net.NetworkInformation.IPGlobalProperties.GetIPGlobalProperties().GetActiveTcpListeners();

            Program.DefaultLogger.Debug($"NetworkDetection -> Checking all currently listening.");
            foreach (var listener in listeners) {
                //Program.DefaultLogger.Debug($"{listener.Address}:{listener.Port}");
                if (listener.Port == _port) {
                    Program.DefaultLogger.Info($"Found some process listening on {listener.Address}:{_port}");
                }
            }

        }


        public void RunPeriodicDetection() {
            Program.DefaultLogger.Info("Network periodic detector has started");
            _isRunning = true;
            while (_isRunning) {
                DetectAsync();
                Thread.Sleep((int)_detectionPeriod);
            }
        }

        public void StopPeriodicDetection() {
            _isRunning = false;
        }
    }
}
