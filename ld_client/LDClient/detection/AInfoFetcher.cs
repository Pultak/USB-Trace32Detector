using LDClient.utils;

namespace LDClient.detection; 

/// <summary>
/// This abstract class implements the common functions of the IInfoFetcher interface
/// which defines the functionality of an info fetcher.
/// </summary>
public abstract class AInfoFetcher : IInfoFetcher {

    /// <summary>
    /// Default value of a serial number (undefined).
    /// </summary>
    private const string UndefinedSerialNumber = "number";

    /// <summary>
    /// Returns the head serial number of the debugger.
    /// </summary>
    public string HeadSerialNumber { get; set; } = UndefinedSerialNumber;

    /// <summary>
    /// Returns the body serial number of the debugger.
    /// </summary>
    public string BodySerialNumber { get; set; } = UndefinedSerialNumber;

    /// <summary>
    /// Instance of FileUtils which encapsulates common functionality
    /// when it comes to dealing with files (limited by the needs of this application).
    /// </summary>
    public IFileUtils FileUtils;

    /// <summary>
    /// Maximum number of attempts to locate and parse the .txt file.
    /// </summary>
    protected readonly uint _maxAttempts;

    /// <summary>
    /// Period (how often) the application tries to locate and parse the .txt file.
    /// </summary>
    protected readonly uint _waitPeriodMs;

    /// <summary>
    /// Path to the .txt file which is generated from the debugger.
    /// </summary>
    protected readonly string _infoFilePath;

    /// <summary>
    /// Abstract constructor of this class 
    /// </summary>
    /// <param name="maxAttempts">Maximum number of attempts to locate and parse the .txt file</param>
    /// <param name="waitPeriodMs">Period (how often) the application tries to locate and parse the .txt file</param>
    /// <param name="infoFilePath">Path to the .txt file which is generated from the debugger</param>

    protected AInfoFetcher(uint maxAttempts, uint waitPeriodMs, string infoFilePath) {
        this.FileUtils = new FileUtils();
        this._maxAttempts = maxAttempts;
        this._waitPeriodMs = waitPeriodMs;
        this._infoFilePath = infoFilePath;
    }

    /// <summary>
    /// Abstract definition of the data fetching function
    /// Function should send the commands to the debugger.
    /// </summary>
    /// <returns>true on success</returns>
    protected abstract bool FetchData();

    /// <summary>
    /// Fetches data from the debugger. It sends the commands defined
    /// in the appsettings.json file to the debugger and tries to
    /// parse the .txt (contains the serial numbers).
    /// </summary>
    /// <returns>True, if data was fetched successfully. False otherwise.</returns>
    public async Task<bool> FetchDataAsync() {
        Program.DefaultLogger.Info("Fetching data from the debugger.");
        // Send the commands to the debugger.
        var success = FetchData();

        // Make sure that all commands were sent and executed successfully.
        if (!success) {
            Program.DefaultLogger.Error("Failed to fetch data from the debugger.");
            return false;
        }
        // Periodically try to parse the .txt file. 
        for (var i = 0; i < _maxAttempts; i++) {
            Program.DefaultLogger.Info($"{i}. attempt to parse the info file.");
            // Try to parse .txt file.
            if (RetrieveDebuggerInfo(_infoFilePath)) {
                Program.DefaultLogger.Info($"Info file has been parsed successfully.");
                return true;
            }
            // Wait for a specified number of milliseconds.
            await Task.Delay((int)_waitPeriodMs);
        }
        Program.DefaultLogger.Error("Failed to parse the into file. It may have not been created.");
        return false;
    }

    /// <summary>
    /// Tries to retrieve information from the debugger.
    /// </summary>
    /// <param name="filePath">path to the .txt file that contains all information</param>
    /// <returns>True if the information was retrieved successfully. False, otherwise.</returns>

    protected bool RetrieveDebuggerInfo(string filePath) {
        try {
            // Read the content of the .txt file.
            var fileContent = FileUtils.ReadFileAllLines(filePath).Aggregate("", (current, line) => $"{current}{line}\n");

            // Parse it (try to find the serial numbers)
            var (headSerialNumber, bodySerialNumber) = DebuggerInfoParser.Parse(fileContent);

            // Store the serial numbers into class variables (properties)
            HeadSerialNumber = headSerialNumber;
            BodySerialNumber = bodySerialNumber;

            // Finally, delete the file.
            //File.Delete(filePath);
        } catch (Exception exception) {
            Program.DefaultLogger.Error($"Failed to retrieve debugger info. File {filePath} may not exist or it does not have the right format. {exception.Message}");
            return false;
        }
        return true;
    }
}