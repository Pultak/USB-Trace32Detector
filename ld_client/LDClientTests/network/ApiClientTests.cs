using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using DiskQueue;
using LDClient.network;
using LDClient.network.data;
using Moq;
using Newtonsoft.Json.Serialization;
using NUnit.Framework;
using NUnit.Framework.Internal;


namespace LDClientTests.network {
    internal class ApiClientTests {

        private ApiClient _client;

        
        private Mock<IHttpClient> _httpClientMock;

        private Mock<IPersistentQueue> _cacheMock;
        private Mock<IPersistentQueueSession> _cacheSessionMock;

        public static readonly Payload ExamplePayload = new() {
            UserName = "honikCz",
            HostName = "Bramborak",
            TimeStamp = "2022-03-21 18:05:00",
            HeadDevice = new DebuggerInfo {
                SerialNumber = "C12345678912"
            },
            BodyDevice = new DebuggerInfo {
                SerialNumber = "C98765432198"
            },
            Status = ConnectionStatus.Connected
        };
        
        public static readonly string ApiUrl = "http://127.0.0.1";
        public static readonly string ApiEndPoint = "/lauterbach-debugger-logs/";
        public static readonly uint ApiPort = 8000;
        public static readonly uint ApiRetryPeriod = 50;
        public static readonly uint ApiMaxEntries = 10;
        public static readonly uint ApiMaxRetries = 5;
        
        
        [SetUp]
        public void Setup() {
            
            _httpClientMock = new Mock<IHttpClient>(MockBehavior.Strict);
            _cacheMock = new Mock<IPersistentQueue>(MockBehavior.Strict);

            _cacheSessionMock = new Mock<IPersistentQueueSession>(MockBehavior.Strict);
            _cacheSessionMock.Setup(x => x.Dequeue()).Returns(JsonSerializer.SerializeToUtf8Bytes(ExamplePayload));
            _cacheSessionMock.Setup(x => x.Dispose()).Callback(() => { });
            _cacheSessionMock.Setup(p => p.Enqueue(It.IsAny<byte[]>())).Callback(() => { });
            _cacheSessionMock.Setup(p => p.Flush()).Callback(() => { });

            _cacheMock.Setup(p => p.OpenSession()).Returns(_cacheSessionMock.Object);

            _client = new ApiClient(ApiUrl, ApiPort, ApiEndPoint, ApiRetryPeriod, ApiMaxEntries, ApiMaxRetries, _cacheMock.Object) {
                _client = _httpClientMock.Object
            };
        }


        [Test]
        public async Task SendPayloadAsync_SendingSuccess_PayloadSent() {
            _httpClientMock.Setup(p => p.PostAsJsonAsync(It.IsAny<Payload>()))
                .Returns(Task.FromResult(new HttpResponseMessage(System.Net.HttpStatusCode.OK)));

            await _client.SendPayloadAsync(ExamplePayload);

            _httpClientMock.Verify(x => x.PostAsJsonAsync(It.IsAny<Payload>()), Times.Once);
        }


        [Test]
        [TestCase(15, true)]
        [TestCase(0, false)]
        public async Task SendPayloadAsync_SendingFailure_PayloadSaved2Cache(int itemsInQueueCount, bool isDequeueHappening) {

            _httpClientMock.Setup(p => p.PostAsJsonAsync(It.IsAny<Payload>()))
                .Returns(Task.FromResult(new HttpResponseMessage(System.Net.HttpStatusCode.UnprocessableEntity)));
            _cacheMock.Setup(p => p.EstimatedCountOfItemsInQueue).Returns(itemsInQueueCount);

            await _client.SendPayloadAsync(ExamplePayload);
            
            _cacheSessionMock.Verify(p => p.Enqueue(It.IsAny<byte[]>()), Times.Once);
            _httpClientMock.Verify(x => x.PostAsJsonAsync(It.IsAny<Payload>()), Times.Once);
            _cacheSessionMock.Verify(x => x.Flush(), Times.Once);
            
            _cacheSessionMock.Verify(x => x.Dequeue(), isDequeueHappening ? Times.Once : Times.Never);
        }


        [Test]
        [Timeout(1000)]
        public void Run_EmptyCache_NothingSent() {
            //nothing in cache 
            _cacheMock.Setup(p => p.EstimatedCountOfItemsInQueue).Returns(0);
            _httpClientMock.Setup(p => p.PostAsJsonAsync(It.IsAny<Payload>()))
                .Returns(Task.FromResult(new HttpResponseMessage(System.Net.HttpStatusCode.UnprocessableEntity)));

            var clientThread = new Thread(_client.Run);

            clientThread.Start();
            Thread.Sleep(400);
            _client.ClientRunning = false;
            //_processDetection.DetectionRunning = false;
            clientThread.Join();

            _httpClientMock.Verify(p => p.PostAsJsonAsync(It.IsAny<Payload>()), Times.Never);
            _cacheSessionMock.Verify(p => p.Enqueue(It.IsAny<byte[]>()), Times.Never);
            _cacheSessionMock.Verify(p => p.Flush(), Times.Never);
            _cacheMock.Verify(p => p.EstimatedCountOfItemsInQueue, Times.AtLeastOnce);

        }

        /// <summary>
        /// Some tests here can fail due to not long enough sleep period.
        /// 
        /// </summary>
        /// <param name="itemsInQueueCount"></param>
        /// <param name="flushedHappened"></param>
        /// <param name="testSleep"></param>
        [Test]
        [Timeout(5000)]
        [TestCase(100, 20, 2000)]
        [TestCase(15, 3, 600)]
        [TestCase(1, 1, 200)]
        [TestCase(6, 2, 400)]
        public void Run_CacheContainX_SentX(int itemsInQueueCount, int flushedHappened, int testSleep) {

            var cacheItemCount = itemsInQueueCount;
            //nothing in cache 
            _cacheMock.Setup(p => p.EstimatedCountOfItemsInQueue).Returns(() => { return cacheItemCount; });
            _httpClientMock.Setup(p => p.PostAsJsonAsync(It.IsAny<Payload>()))
                .Returns(Task.FromResult(new HttpResponseMessage(System.Net.HttpStatusCode.OK)));
            _cacheSessionMock.Setup(x => x.Dequeue())
                .Returns(() => {
                    --cacheItemCount;
                    return JsonSerializer.SerializeToUtf8Bytes(ExamplePayload);
                });

            var clientThread = new Thread(_client.Run);

            clientThread.Start();
            Thread.Sleep(testSleep);
            _client.ClientRunning = false;
            //_processDetection.DetectionRunning = false;
            clientThread.Join();

            _httpClientMock.Verify(p => p.PostAsJsonAsync(It.IsAny<Payload>()), Times.Exactly(itemsInQueueCount));
            _cacheSessionMock.Verify(p => p.Enqueue(It.IsAny<byte[]>()), Times.Never);
            _cacheSessionMock.Verify(p => p.Flush(), Times.Exactly(flushedHappened));
            _cacheMock.Verify(p => p.EstimatedCountOfItemsInQueue, Times.AtLeastOnce);
        }
        

    }
}
