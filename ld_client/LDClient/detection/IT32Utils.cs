using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.detection {
    public interface IT32Utils {

        public bool InitConnection();
        public bool ExecuteCommands();
        public bool CloseConnection();

    }
}
