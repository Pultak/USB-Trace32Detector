using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.utils {
    public class FileUtils : IFileUtils {
        public string[] ReadFileAllLines(string file) {
            return File.ReadAllLines(file);
        }
    }
}
