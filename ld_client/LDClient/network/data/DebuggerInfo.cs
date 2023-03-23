using System.Text.Json.Serialization;

namespace LDClient.network.data
{
    /// <summary>
    /// This class holds all the information about
    /// a specific part of a debugger (head/body).
    /// </summary>
    public class DebuggerInfo
    {
        /// <summary>
        /// Serial number of the part of a debugger.
        /// </summary>
        [JsonPropertyName("serial_number")]
        public string? SerialNumber { get; set; }
    }
}
