using System.Runtime.Serialization;

namespace LDClient.network.data {
    public enum ConnectionStatus {
        [EnumMember(Value = "connected")]
        Connected,
        [EnumMember(Value = "disconnected")]
        Disconnected

    }
}
