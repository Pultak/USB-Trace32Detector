using System.Text.Json;
using System.Text.Json.Serialization;
using Newtonsoft.Json;
using JsonSerializer = System.Text.Json.JsonSerializer;

namespace LDClient.network.data {
    [JsonObject(MemberSerialization.OptIn)]
    public class Payload {

        [JsonPropertyName("username")]
        public string UserName { get; set; }

        [JsonPropertyName("hostname")]
        public string HostName { get; set; }

        [JsonPropertyName("timestamp")]
        //[Newtonsoft.Json.JsonConverter(typeof(DateFormatConverter), "yyyy-MM-dd HH:mm:ss.ffffff")]
        public DateTime TimeStamp { get; set; }

        [JsonPropertyName("head_device")]
        public DebuggerInfo HeadDevice { get; set; }


        [JsonPropertyName("body_device")]
        public DebuggerInfo  BodyDevice { get; set; }
        
        [JsonPropertyName("status")]
        //[Newtonsoft.Json.JsonConverter(typeof(StringEnumConverter))]
        public ConnectionStatus Status { get; set; }


        public override string ToString() {
            return ParseToJson(this);
        }

        public string ParseToJson() {
            return Payload.ParseToJson(this);
        }

        public static string ParseToJson(Payload payload) {
            var options = new JsonSerializerOptions {
                Converters = {
                    new JsonStringEnumConverter(JsonNamingPolicy.CamelCase)
                }
            };

            return JsonSerializer.Serialize(payload, options);
        }
    }
}
