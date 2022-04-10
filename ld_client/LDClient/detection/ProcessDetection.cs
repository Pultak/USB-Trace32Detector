using System;
using System.Collections.Generic;
using System.Diagnostics;
using System;
using System.Management;

namespace LDClient.detection {
    public class ProcessDetection : IDetection {

        private const string ProcessStartQuery = "SELECT * FROM Win32_ProcessStartTrace";
        private const string ProcessStopQuery = "SELECT * FROM Win32_ProcessStopTrace";

        private ManagementEventWatcher _stopWatch;

        private bool _isRunning;

        private readonly string _processName;
        private readonly uint _detectionPeriod;
        private bool _processActive;
        public ProcessDetection(string processName, uint detectionPeriod) {
            this._processName = processName;
            this._detectionPeriod = detectionPeriod;
        }


        public void DetectAsync() {
            var processes = Process.GetProcessesByName(_processName);
            Program.DefaultLogger.Info($"Found {processes.Length} processes with name: {_processName}");
            var processFound = false;
            foreach (var process in processes) {
                if (process.ProcessName.Equals(_processName)) {
                    if (!_processActive) {
                        Program.DefaultLogger.Info($"Process started: {_processName}");
                    }
                    _processActive = true;
                    processFound = true;
                    break;
                }
                Console.WriteLine(process);
            }

            if (!processFound) {
                if (_processActive) {
                    Program.DefaultLogger.Info($"Process stopped: {_processName}");
                }
                _processActive = false;
            }
        }


        public void RunPeriodicDetection() {

            Program.DefaultLogger.Info("Process periodic detector has started");
            _isRunning = true;
            while (_isRunning) {
                DetectAsync();
                Thread.Sleep((int)_detectionPeriod);
            }
        }

        public void StopPeriodicDetection() {
            _isRunning = false;
        }


        public void RegisterProcessListeners() {
            ManagementEventWatcher startWatch = new ManagementEventWatcher(
                new WqlEventQuery(ProcessStartQuery));
            startWatch.EventArrived += startWatch_EventArrived;
            startWatch.Start();

            _stopWatch = new ManagementEventWatcher(
                new WqlEventQuery(ProcessStopQuery));
            _stopWatch.EventArrived += stopWatch_EventArrived;
            _stopWatch.Start();
        }

        void stopWatch_EventArrived(object sender, EventArrivedEventArgs e) {
            var processName = e.NewEvent.Properties["ProcessName"].Value.ToString();
            if (processName.Equals(_processName + ".exe")) {
                Program.DefaultLogger.Info($"Process stopped: {processName}");
            }
        }

        void startWatch_EventArrived(object sender, EventArrivedEventArgs e) {
            var processName = e.NewEvent.Properties["ProcessName"].Value.ToString();
            if (processName.Equals(_processName + ".exe")) {
                Program.DefaultLogger.Info($"Process started: {processName}");
            }
        }
    }
}
