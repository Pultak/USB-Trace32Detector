using System.Runtime.Serialization;

namespace LDClient.network.data 
{
    /// <summary>
    /// This enumeration defines different states in
    /// which a debugger can be.
    /// </summary>
    public enum ConnectionStatus
    {
        /// <summary>
        /// Debugger is connected
        /// </summary>
        [EnumMember(Value = "connected")]
        Connected,

        /// <summary>
        /// Debugger is disconnected
        /// </summary>
        [EnumMember(Value = "disconnected")]
        Disconnected
    }
}
