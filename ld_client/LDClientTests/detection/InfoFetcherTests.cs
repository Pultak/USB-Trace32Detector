using System.IO;
using System.Threading.Tasks;
using LDClient.detection;
using LDClient.utils;
using Moq;
using NUnit.Framework;

namespace LDClientTests.detection; 

internal class InfoFetcherTests {
    private AInfoFetcher _defaultFetcher;
    private AInfoFetcher _fetcherWithoutPars;
        

    private readonly string[] _defaultArguments = new[] { "argument 1", "argument 2" , "argument 3"};
    private const uint DefaultMaxAttempts = 5;

    private Mock<IProcessUtils> _mockProcessUtils;
    private Mock<IFileUtils> _mockFileUtils;

    [SetUp]
    public void Setup() {
        _mockProcessUtils = new Mock<IProcessUtils>(MockBehavior.Strict);

        _mockFileUtils = new Mock<IFileUtils>(MockBehavior.Strict);
    

        _defaultFetcher = new T32RemFetcher(DefaultMaxAttempts, 50, "info.txt", "executable.exe",
            _defaultArguments, 0, 50) {
            FileUtils = _mockFileUtils.Object,
            ProcessUtils = _mockProcessUtils.Object
        };


        _fetcherWithoutPars = new T32RemFetcher(DefaultMaxAttempts, 50, "info.txt", "executable.exe",
            null, 0, 50) {
            FileUtils = _mockFileUtils.Object,
            ProcessUtils = _mockProcessUtils.Object
        };
    }

    [Test]
    public async Task FetchDataAsync_ExecuteAll_ExecutedAndFetched() {

        _mockProcessUtils.Setup(x => x.ExecuteNewProcess(It.IsAny<string>(), It.IsAny<string>(),
            It.IsAny<int>(), It.IsAny<int>())).Returns(true);
        _mockFileUtils.Setup(x => x.ReadFileAllLines(It.IsAny<string>())).
            Returns(DebuggerInfoParserTests.CorrectFileContent.Split("\n"));


        bool result = await _defaultFetcher.FetchDataAsync();

        Assert.IsTrue(result);
        _mockProcessUtils.Verify(x => x.ExecuteNewProcess(It.IsAny<string>(), It.IsAny<string>(),
            It.IsAny<int>(), It.IsAny<int>()), Times.Exactly(_defaultArguments.Length));

        Assert.AreEqual(DebuggerInfoParserTests.BodySerialNumber, _defaultFetcher.BodySerialNumber);
        Assert.AreEqual(DebuggerInfoParserTests.HeadSerialNumber, _defaultFetcher.HeadSerialNumber);

    }



    [Test]
    public async Task FetchDataAsync_ExecuteNonExistentProgram_ExecutionFailed() {

        _mockProcessUtils.Setup(x => x.ExecuteNewProcess(It.IsAny<string>(), It.IsAny<string>(),
            It.IsAny<int>(), It.IsAny<int>())).Returns(false);
        _mockFileUtils.Setup(x => x.ReadFileAllLines(It.IsAny<string>())).
            Returns(new []{""});


        bool result = await _defaultFetcher.FetchDataAsync();


        Assert.IsFalse(result);
        _mockProcessUtils.Verify(x => x.ExecuteNewProcess(It.IsAny<string>(), It.IsAny<string>(),
            It.IsAny<int>(), It.IsAny<int>()), Times.Exactly(1));
        _mockFileUtils.Verify(x => x.ReadFileAllLines(It.IsAny<string>()), Times.Never);
    }

    [Test]
    public async Task FetchDataAsync_ExecuteWithoutParameters_NotExecuted() {
        _mockProcessUtils.Setup(x => x.ExecuteNewProcess(It.IsAny<string>(), It.IsAny<string>(),
            It.IsAny<int>(), It.IsAny<int>())).Returns(false);
        _mockFileUtils.Setup(x => x.ReadFileAllLines(It.IsAny<string>())).
            Returns(new[] { "" });

        bool result = await _fetcherWithoutPars.FetchDataAsync();
            
        Assert.IsFalse(result);
        _mockProcessUtils.Verify(x => x.ExecuteNewProcess(It.IsAny<string>(), It.IsAny<string>(),
            It.IsAny<int>(), It.IsAny<int>()), Times.Never);
        _mockFileUtils.Verify(x => x.ReadFileAllLines(It.IsAny<string>()), Times.Never);

    }


    [Test]
    public async Task FetchDataAsync_ExecuteInfoNotCreated_FetchFailed() {
        _mockProcessUtils.Setup(x => x.ExecuteNewProcess(It.IsAny<string>(), It.IsAny<string>(),
            It.IsAny<int>(), It.IsAny<int>())).Returns(true);
        _mockFileUtils.Setup(x => x.ReadFileAllLines(It.IsAny<string>())).Throws(new FileNotFoundException());

        bool result = await _defaultFetcher.FetchDataAsync();
        Assert.IsFalse(result);

        _mockProcessUtils.Verify(x => x.ExecuteNewProcess(It.IsAny<string>(), It.IsAny<string>(),
            It.IsAny<int>(), It.IsAny<int>()), Times.Exactly(_defaultArguments.Length));
        _mockFileUtils.Verify(x => x.ReadFileAllLines(It.IsAny<string>()), Times.Exactly((int)DefaultMaxAttempts));

    }




}