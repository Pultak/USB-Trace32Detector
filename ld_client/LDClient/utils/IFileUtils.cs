namespace LDClient.utils
{
    /// <summary>
    /// This interface defines IO operations.
    /// </summary>
    public interface IFileUtils
    {
        /// <summary>
        /// Reads all lines of a files and returns them as a array.
        /// </summary>
        /// <param name="file">path to the file</param>
        /// <returns>all the lines of the file (as an array)</returns>
        public string[] ReadFileAllLines(string file);
    }
}
