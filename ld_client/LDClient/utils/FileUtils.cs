using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.utils {
    
    /// <summary>
    /// This class implements the IFileUtils interface
    /// which defines IO operations.
    /// </summary>
    public class FileUtils : IFileUtils {
        
        /// <summary>
        /// Reads all lines of a files and returns them as a array.
        /// </summary>
        /// <param name="file">path to the file</param>
        /// <returns>all the lines of the file (as an array)</returns>
        public string[] ReadFileAllLines(string file) {
            return File.ReadAllLines(file);
        }
    }
}
