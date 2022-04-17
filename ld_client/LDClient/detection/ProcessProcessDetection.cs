using System.Diagnostics;
using System.Text.Json;
using LDClient.network;
using LDClient.network.data;

namespace LDClient.detection {
   
	 public class ProcessProcessDetection : IProcessDetection {
        
        private const string DatetimeFormat = "yyyy-MM-dd hh:mm:ss";

        private readonly string _processName;
        private readonly uint _detectionPeriodMs;
        private bool _processIsActive;
        private bool _failedToRetrieveData;
        private Payload? _lastConnectedPayload;

        private readonly InfoFetcher _infoFetcher;
        private readonly IApiClient _apiClient;

        public ProcessProcessDetection(string processName, uint detectionPeriodMs, InfoFetcher infoFetcher, IApiClient apiClient) {
            _processName = processName;
            _detectionPeriodMs = detectionPeriodMs;
            _infoFetcher = infoFetcher;
            _apiClient = apiClient;
            _failedToRetrieveData = false;
        }

        private async Task<bool> RetrieveDataFromDebugger() {
            var success = await _infoFetcher.FetchDataAsync();
            if (success) {
                _lastConnectedPayload = await SendDataToServerAsync(_infoFetcher.HeadSerialNumber, _infoFetcher.BodySerialNumber, DatetimeFormat);
            }
            return success;
        }
        
        private async Task DebuggerDisconnected() {
            if (_lastConnectedPayload is not null) {
                _lastConnectedPayload.Status = ConnectionStatus.Disconnected;
                _lastConnectedPayload.TimeStamp = DateTime.Now.ToString(DatetimeFormat);
                await _apiClient.SendPayloadAsync(_lastConnectedPayload);
                _lastConnectedPayload = null;
            }
        }

        private async Task DetectProcessAsync() {
            var processExists = Process.GetProcessesByName(_processName).Length > 0;

            if (processExists && !_processIsActive) {
                Program.DefaultLogger.Info($"Process started: {_processName}");
                if (!_failedToRetrieveData) {
                    _failedToRetrieveData = !await RetrieveDataFromDebugger();
                }
            } else if (!processExists && _processIsActive) {
                Program.DefaultLogger.Info($"Process stopped: {_processName}");
                _failedToRetrieveData = false;
                await DebuggerDisconnected();
            }
            _processIsActive = processExists;
        }
        
        private async Task<Payload> SendDataToServerAsync(string headSerialNumber, string bodySerialNumber, string datetimeFormat) {
            Payload payload = new() {
                UserName = Environment.UserName,
                HostName = Environment.MachineName,
                TimeStamp = DateTime.Now.ToString(datetimeFormat),
                HeadDevice = new DebuggerInfo {
                    SerialNumber = headSerialNumber
                },
                BodyDevice = new DebuggerInfo {
                    SerialNumber = bodySerialNumber
                },
                Status = ConnectionStatus.Connected
            };
            await _apiClient.SendPayloadAsync(payload);
            return payload;
        }
        
        public async void RunPeriodicDetection() {
            Program.DefaultLogger.Info("Process periodic detector has started");
            while (true) {
                await DetectProcessAsync();
                Thread.Sleep((int)_detectionPeriodMs);
            }
            // ReSharper disable once FunctionNeverReturns
        }
    }
}
