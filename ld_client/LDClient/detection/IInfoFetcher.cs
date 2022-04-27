using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient.detection {
    public interface IInfoFetcher {

        public string HeadSerialNumber { get; set; }
        public string BodySerialNumber { get; set; }

        public Task<bool> FetchDataAsync();
    }
}
