namespace LDClient.detection
{
    /// <summary>
    /// This interface defines the main functionality of an trace32 API
    /// which is mainly used to send commands to the debugger. 
    /// </summary>
    public interface IT32Utils
    {

        /// <summary>
        /// This method initialized the connection with the trace32 application API.
        /// It setups the standard connection configuration a tries to connect to the API
        /// </summary>
        /// <returns>true on success</returns>
        public bool InitConnection();

        /// <summary>
        /// Method executes all passed commands though the trace32 API
        /// </summary>
        /// <returns>true on success</returns>
        public bool ExecuteCommands();

        /// <summary>
        /// This method closes the connection with the trace32 application api
        /// </summary>
        /// <returns>true on success</returns>
        public bool CloseConnection();
    }
}