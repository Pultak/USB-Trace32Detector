using System.Text.Json.Serialization;

namespace LDClient.network.data {
    public class DebuggerInfo {
        
        [JsonPropertyName("serial_number")]
        public string SerialNumber { get; set; }
    }
}
