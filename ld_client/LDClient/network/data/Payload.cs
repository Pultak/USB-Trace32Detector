using System.Text.Json.Serialization;
using Newtonsoft.Json;

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
    }
}
