using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using LDClient.network.data;

namespace LDClient.network {
    public interface IHttpClient {

        public Task<HttpResponseMessage> PostAsJsonAsync(Payload payload);
    }
}
