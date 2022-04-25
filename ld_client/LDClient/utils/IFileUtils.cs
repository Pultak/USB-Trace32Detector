using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.utils {
    public interface IFileUtils {

        public string[] ReadFileAllLines(string file);
    }
}
