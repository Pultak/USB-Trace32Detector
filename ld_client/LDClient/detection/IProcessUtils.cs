using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.detection {
    public interface IProcessUtils {
        public bool IsProcessRunning(string name);

        public bool ExecuteNewProcess(string fileName, string argument, int timeout, int desiredExitCode);
    }
}
