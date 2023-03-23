using System.Threading;
using System.Threading.Tasks;
using LDClient.detection;
using LDClient.network;
using LDClient.network.data;
using Moq;
using NUnit.Framework;

namespace LDClientTests.detection
{
    public class ProcessDetectionTests
    {
        private ProcessDetection _processDetection;

        private Mock<IApiClient> _mockApiClient;
        private Mock<IInfoFetcher> _mockInfoFetcher;
        private Mock<IProcessUtils> _mockProcessUtils;

        private readonly string _defaultSerialNumber = "C12345678912";

        [SetUp]
        public void Setup()
        {
            _mockApiClient = new Mock<IApiClient>(MockBehavior.Strict);
            _mockApiClient.Setup(x => x.SendPayloadAsync(It.IsAny<Payload>())).Returns(Task.CompletedTask);


            _mockInfoFetcher = new Mock<IInfoFetcher>(MockBehavior.Strict);
            _mockInfoFetcher.Setup(x => x.BodySerialNumber).Returns(_defaultSerialNumber);
            _mockInfoFetcher.Setup(x => x.HeadSerialNumber).Returns(_defaultSerialNumber);

            _mockProcessUtils = new Mock<IProcessUtils>(MockBehavior.Strict);


            _processDetection = new ProcessDetection("process", 50, _mockInfoFetcher.Object, _mockApiClient.Object, _mockProcessUtils.Object, 1, 0);
        }

        private void StartAndStopDetection(int timeout)
        {
            var detectionThread = new Thread(_processDetection.RunPeriodicDetection);

            detectionThread.Start();

            Thread.Sleep(timeout);

            _processDetection.DetectionRunning = false;
            detectionThread.Join();
        }

        [Test]
        [Timeout(1000)]
        public void RunPeriodicDetection_ProcessStartFetchFailed_1Fetch0PayloadSent()
        {
            _mockInfoFetcher.Setup(x => x.FetchDataAsync()).Returns(Task.FromResult(false));
            _mockProcessUtils.Setup(x => x.IsProcessRunning(It.IsAny<string>())).Returns(true);


            StartAndStopDetection(500);

            _mockApiClient.Verify(x => x.SendPayloadAsync(It.IsAny<Payload>()), Times.Never);
            _mockInfoFetcher.Verify(x => x.FetchDataAsync(), Times.Once);
        }

        [Test]
        [Timeout(1000)]
        public void RunPeriodicDetection_ProcessStartFetchSuccess_1Fetch1PayloadSent()
        {
            _mockInfoFetcher.Setup(x => x.FetchDataAsync()).Returns(Task.FromResult(true));
            _mockProcessUtils.Setup(x => x.IsProcessRunning(It.IsAny<string>())).Returns(true);


            StartAndStopDetection(500);

            _mockApiClient.Verify(x => x.SendPayloadAsync(It.IsAny<Payload>()), Times.Once);
            _mockInfoFetcher.Verify(x => x.FetchDataAsync(), Times.Once);
        }

        [Test]
        [Timeout(1000)]
        public void RunPeriodicDetection_ProcessStartAndStopped_1Fetch2PayloadSent()
        {
            _mockInfoFetcher.Setup(x => x.FetchDataAsync()).Returns(Task.FromResult(true));
            _mockProcessUtils.Setup(x => x.IsProcessRunning(It.IsAny<string>())).Returns(true);

            var detectionThread = new Thread(_processDetection.RunPeriodicDetection);

            detectionThread.Start();

            Thread.Sleep(250);
            _mockProcessUtils.Setup(x => x.IsProcessRunning(It.IsAny<string>())).Returns(false);

            Thread.Sleep(250);

            _processDetection.DetectionRunning = false;
            detectionThread.Join();

            _mockApiClient.Verify(x => x.SendPayloadAsync(It.IsAny<Payload>()), Times.Exactly(2));
            _mockInfoFetcher.Verify(x => x.FetchDataAsync(), Times.Once);
        }

        [Test]
        [Timeout(2000)]
        public void RunPeriodicDetection_2xProcessStartAndStopped_2Fetch4PayloadSent()
        {
            _mockInfoFetcher.Setup(x => x.FetchDataAsync()).Returns(Task.FromResult(true));
            _mockProcessUtils.Setup(x => x.IsProcessRunning(It.IsAny<string>())).Returns(true);

            var detectionThread = new Thread(_processDetection.RunPeriodicDetection);

            detectionThread.Start();

            Thread.Sleep(200);
            _mockProcessUtils.Setup(x => x.IsProcessRunning(It.IsAny<string>())).Returns(false);

            Thread.Sleep(200);
            _mockProcessUtils.Setup(x => x.IsProcessRunning(It.IsAny<string>())).Returns(true);


            Thread.Sleep(200);
            _mockProcessUtils.Setup(x => x.IsProcessRunning(It.IsAny<string>())).Returns(false);
            Thread.Sleep(200);

            _processDetection.DetectionRunning = false;
            detectionThread.Join();

            _mockApiClient.Verify(x => x.SendPayloadAsync(It.IsAny<Payload>()), Times.Exactly(4));
            _mockInfoFetcher.Verify(x => x.FetchDataAsync(), Times.Exactly(2));
        }
    }
}