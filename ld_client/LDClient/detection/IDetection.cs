using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.detection {
    internal interface IDetection {

        public void DetectAsync();

        public void RunPeriodicDetection();
        public void StopPeriodicDetection();
    }
}
