using LDClient.network;
using LDClient.network.data;

namespace LDClient.detection; 

/// <summary>
/// This class takes care of process detection. When t32mtc (process)
/// is detected, it means that the debugger is currently being used.
/// The class keeps track of the current state of a debugger.
/// </summary>
public sealed class ProcessDetection : IProcessDetection {

    /// <summary>
    /// Datetime format used when sending payloads to the server.
    /// </summary>
    private const string DatetimeFormat = "yyyy-MM-dd hh:mm:ss";

    /// <summary>
    /// Name of the process the application detects.
    /// </summary>
    private readonly string _processName;
        
    /// <summary>
    /// How often the application check the current status of the process (cunning / not running).
    /// </summary>
    private readonly uint _detectionPeriodMs;
        
    /// <summary>
    /// Instance of InfoFetcher used to fetch information from the debugger
    /// (when the process is detected).
    /// </summary>
    private readonly IInfoFetcher _infoFetcher;
        
    /// <summary>
    /// Instance of API clients used for sending data off to the server.
    /// </summary>
    private readonly IApiClient _apiClient;
        
    /// <summary>
    /// Instance of ProcessUtils which encapsulates common functionality
    /// when it comes to dealing with processes (limited by the needs of this application).
    /// </summary>
    private readonly IProcessUtils _processUtils;

    /// <summary>
    /// Flag indicating whether the process is currently running or not.
    /// </summary>
    private bool _processIsActive;
        
    /// <summary>
    /// Flag if the application failed to retrieve data when the process was detected.
    /// </summary>
    private bool _failedToRetrieveData;
        
    /// <summary>
    /// Last payload that was sent to the server.
    /// </summary>
    private Payload? _lastConnectedPayload;

    /// <summary>
    /// Flag used to stop the thread (process detection).
    /// </summary>
    public bool DetectionRunning = false;
        
    /// <summary>
    /// Creates an instance of this class.
    /// </summary>
    /// <param name="processName">Name of the process the application detects</param>
    /// <param name="detectionPeriodMs">How often the application check the current status of the process (cunning / not running)</param>
    /// <param name="infoFetcher">Instance of InfoFetcher used to fetch information from the debugger</param>
    /// <param name="apiClient">Instance of API clients used for sending data off to the server</param>
    /// <param name="processUtils">Instance of ProcessUtils which encapsulates common functionality when it comes to dealing with processes (limited by the needs of this application)</param>
    public ProcessDetection(string processName, uint detectionPeriodMs, IInfoFetcher infoFetcher,
        IApiClient apiClient, IProcessUtils processUtils) {
        _processName = processName;
        _detectionPeriodMs = detectionPeriodMs;
        _infoFetcher = infoFetcher;
        _apiClient = apiClient;
        _failedToRetrieveData = false;
        _processUtils = processUtils;
    }

    /// <summary>
    /// Retrieves data from the debugger.
    /// </summary>
    /// <returns>True, if the data was fetched successfully. False, otherwise.</returns>
    private async Task<bool> RetrieveDataFromDebugger() {
        // Try to fetch data from the debugger.
        var success = await _infoFetcher.FetchDataAsync();
            
        // If the data was fetched successfully, send a payload off to the server.
        if (success) {
            _lastConnectedPayload = await SendDataToServerAsync(_infoFetcher.HeadSerialNumber,
                _infoFetcher.BodySerialNumber, DatetimeFormat);
        }
        return success;
    }

    /// <summary>
    /// Sends a payload to the server when a debugger gets disconnected.
    /// </summary>
    private async Task DebuggerDisconnected() {
        // Make sure the debugger was connected in the first place.
        if (_lastConnectedPayload is not null) {
            // Update the status and timestamp of the last payload
            // (the serial numbers remain the same).
            _lastConnectedPayload.Status = ConnectionStatus.Disconnected;
            _lastConnectedPayload.TimeStamp = DateTime.Now.ToString(DatetimeFormat);
                
            // Send the data to the server.
            await _apiClient.SendPayloadAsync(_lastConnectedPayload);
                
            // Clear the last payload.
            _lastConnectedPayload = null;
        }
    }

    /// <summary>
    /// Checks if the t32mtc process is running or not. 
    /// </summary>
    private async Task DetectProcessAsync() {
        // Check if the process is running.
        var processExists = _processUtils.IsProcessRunning(_processName);

        // Check if the process was not running but now it is (flip flop ON). 
        if (processExists && !_processIsActive) {
            Program.DefaultLogger.Info($"Process started: {_processName}");
            if (!_failedToRetrieveData) {
                _failedToRetrieveData = !await RetrieveDataFromDebugger();
            }
        }
        // Check if the process was running but now it is not (fli flop OFF).
        else if (!processExists && _processIsActive) {
            Program.DefaultLogger.Info($"Process stopped: {_processName}");
            _failedToRetrieveData = false;
            await DebuggerDisconnected();
        }

        // Keep track of the current state of the debugger.
        _processIsActive = processExists;
    }

    /// <summary>
    /// Creates a payload and sends it to the server.
    /// </summary>
    /// <param name="headSerialNumber">serial number of the head of the debugger</param>
    /// <param name="bodySerialNumber">serial number of the body of the debugger</param>
    /// <param name="datetimeFormat">datetime format (timestamp)</param>
    /// <returns>the newly-created payload</returns>
    private async Task<Payload> SendDataToServerAsync(string headSerialNumber, string bodySerialNumber, string datetimeFormat) {
        // Create a new payload. 
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
            
        // Send it to the server and return it.
        await _apiClient.SendPayloadAsync(payload);
        return payload;
    }

    /// <summary>
    /// Periodically runs process detection. This method is instantiated
    /// as a thread from the main class (Program.cs).
    /// </summary>
    public async void RunPeriodicDetection() {
        Program.DefaultLogger.Info("Process periodic detector has started");
        DetectionRunning = true;
            
        while (DetectionRunning) {
            await DetectProcessAsync();
            Thread.Sleep((int) _detectionPeriodMs);
        }
    }
}