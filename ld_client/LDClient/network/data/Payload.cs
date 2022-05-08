using System.Text.Json;
using System.Text.Json.Serialization;
using Newtonsoft.Json;
using JsonSerializer = System.Text.Json.JsonSerializer;

namespace LDClient.network.data {
    
    /// <summary>
    /// This class represents a single payload that is sent to the server.
    /// </summary>
    [JsonObject(MemberSerialization.OptIn)]
    public class Payload {

        /// <summary>
        /// Username of the currently logged user.
        /// </summary>
        [JsonPropertyName("username")]
        public string? UserName { get; set; }

        /// <summary>
        /// Hostname of the pc.
        /// </summary>
        [JsonPropertyName("hostname")]
        public string? HostName { get; set; }

        /// <summary>
        /// Timestamp (when a debugger was plugged/unplugged).
        /// </summary>
        [JsonPropertyName("timestamp")]
        public string? TimeStamp { get; set; }

        /// <summary>
        /// Information about the head of the debugger.
        /// </summary>
        [JsonPropertyName("head_device")]
        public DebuggerInfo? HeadDevice { get; set; }

        /// <summary>
        /// Information about the body of the debugger.
        /// </summary>
        [JsonPropertyName("body_device")]
        public DebuggerInfo?  BodyDevice { get; set; }
        
        /// <summary>
        /// Status of the debugger (connected/disconnected).
        /// </summary>
        [JsonPropertyName("status")]
        public ConnectionStatus Status { get; set; }
        
        /// <summary>
        /// Returns a string representation of the payload.
        /// </summary>
        /// <returns></returns>
        public override string ToString() {
            return ParseToJson(this);
        }

        /// <summary>
        /// Parses (converts) the payload into JSON format.
        /// </summary>
        /// <returns></returns>
        public string ParseToJson() {
            return Payload.ParseToJson(this);
        }

        /// <summary>
        /// Serializes a given payload into JSON format.
        /// </summary>
        /// <param name="payload">payload to be serialized into JSON</param>
        /// <returns></returns>
        public static string ParseToJson(Payload payload) {
            // Create options for serialization.
            var options = new JsonSerializerOptions {
                Converters = {
                    new JsonStringEnumConverter(JsonNamingPolicy.CamelCase)
                }
            };
            // Serialize the payload and return it.
            return JsonSerializer.Serialize(payload, options);
        }
    }
}
