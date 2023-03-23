namespace LDClient.detection
{
    /// <summary>
    /// This interface defines the functionality of a process detector.
    /// A process detector is used to determine whether a user is currently
    /// using a debugger or not.
    /// </summary>
    internal interface IProcessDetection
    {
        /// <summary>
        /// Periodically runs process detection. This method is instantiated
        /// as a thread from the main class (Program.cs).
        /// </summary>
        public void RunPeriodicDetection();
    }
}