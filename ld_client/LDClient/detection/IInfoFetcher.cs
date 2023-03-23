using System.Threading.Tasks;

namespace LDClient.detection
{
    /// <summary>
    /// This interface defines the functionality of an info fetcher which
    /// takes care of sending commands to the debugger. 
    /// </summary>
    public interface IInfoFetcher
    {

        /// <summary>
        /// Returns the head serial number of the debugger.
        /// </summary>
        public string HeadSerialNumber { get; set; }

        /// <summary>
        /// Returns the body serial number of the debugger.
        /// </summary>
        public string BodySerialNumber { get; set; }

        /// <summary>
        /// Fetches data from the debugger. It sends the commands defined
        /// in the appsettings.json file to the debugger and tries to
        /// parse the .txt (contains the serial numbers).
        /// </summary>
        /// <returns>True, if data was fetched successfully. False otherwise.</returns>
        public Task<bool> FetchDataAsync();
    }
}