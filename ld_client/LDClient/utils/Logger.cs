using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LDClient {
    enum LogVerbosity {
        None = 0,
        Exceptions,
        Full
    }

    public enum LogType {
        Info = 0,
        Debug,
        Error
    }

    enum LogFlow {
        Console = 0,
        File
    }


    public abstract class Logger : IDisposable {

        private LogVerbosity _verbosity;
        private LogFlow _logFlow;

        private Queue<Action> _queue = new Queue<Action>();
        private ManualResetEvent _hasNewItems = new ManualResetEvent(false);
        private ManualResetEvent _terminate = new ManualResetEvent(false);
        private ManualResetEvent _waiting = new ManualResetEvent(false);
        private Thread _loggingThread;

        private static readonly Lazy<Logger> _lazyLog = new Lazy<Logger>(()
            => {
                switch (Program.Config.LogFlowType) {
                    case LogFlow.File:
                        return new FileLogger();
                    case LogFlow.Console:
                    default:
                        return new ConsoleLogger();

                }
            }
        );

        public static Logger Current => _lazyLog.Value;

        protected Logger() {
            _verbosity = (LogVerbosity)Program.Config.LogVerbosityType;
            _logFlow = (LogFlow)Program.Config.LogFlowType;
            _loggingThread = new Thread(new ThreadStart(ProcessQueue)) { IsBackground = true };
            _loggingThread.Start();
        }

        public void Info(string message) {
            Log(message, LogType.Info);
        }

        public void Debug(string message) {
            Log(message, LogType.Debug);
        }

        public void Error(string message) {
            Log(message, LogType.Error);
        }

        public void Error(Exception e) {
            if (_verbosity != LogVerbosity.None) {
                Log(UnwrapExceptionMessages(e), LogType.Error);
            }
        }

        public override string ToString() => $"Logger settings: [Type: {this.GetType().Name}, Verbosity: {_verbosity}, ";

        protected abstract void CreateLog(string message);

        public void Flush() => _waiting.WaitOne();

        public void Dispose() {
            _terminate.Set();
            _loggingThread.Join();
        }

        protected virtual string ComposeLogRow(string message, LogType logType) =>
            $"[{DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss,fff", CultureInfo.InvariantCulture)} - {logType}] - {message}";

        protected virtual string UnwrapExceptionMessages(Exception ex) {
            if (ex == null)
                return string.Empty;

            return $"{ex}, Inner exception: {UnwrapExceptionMessages(ex.InnerException)} ";
        }

        private void ProcessQueue() {
            while (true) {
                _waiting.Set();
                int i = WaitHandle.WaitAny(new WaitHandle[] { _hasNewItems, _terminate });
                if (i == 1) return;
                _hasNewItems.Reset();
                _waiting.Reset();

                Queue<Action> queueCopy;
                lock (_queue) {
                    queueCopy = new Queue<Action>(_queue);
                    _queue.Clear();
                }

                foreach (var log in queueCopy) {
                    log();
                }
            }
        }

        private void Log(string message, LogType logType) {
            if (string.IsNullOrEmpty(message))
                return;

            var logRow = ComposeLogRow(message, logType);
            System.Diagnostics.Debug.WriteLine(logRow);

            if (_verbosity == LogVerbosity.Full) {
                lock (_queue)
                    _queue.Enqueue(() => CreateLog(logRow));

                _hasNewItems.Set();
            }
        }
    }

    class ConsoleLogger : Logger {
        protected override void CreateLog(string message) {
            Console.WriteLine(message);
        }
    }


    class FileLogger : Logger {

        private const string LogFolderName = "logs";
        private const string LogFileName = "app_info.log";
        private readonly int _logChunkSize = Program.Config.LogChunkSize;
        private readonly int _logChunkMaxCount = Program.Config.LogChunkMaxCount;
        private readonly int _logArchiveMaxCount = Program.Config.LogArchiveMaxCount;
        private readonly int _logCleanupPeriod = Program.Config.LogCleanupPeriod;

        private readonly string logFolderPath = Path.Combine(Path.GetTempPath(), $"ldClient\\{LogFolderName}");

        private bool _logDirExists = false;

        protected override void CreateLog(string message) {

            if (!_logDirExists) {
                _logDirExists = Directory.Exists(logFolderPath);
                if (!_logDirExists) {
                    Directory.CreateDirectory(logFolderPath);
                    _logDirExists = true;
                }
            }

            var logFilePath = Path.Combine(logFolderPath, LogFileName);

            Rotate(logFilePath);

            using (var sw = File.AppendText(logFilePath)) {
                sw.WriteLine(message);
            }
        }

        private void Rotate(string filePath) {
            if (!File.Exists(filePath))
                return;

            var fileInfo = new FileInfo(filePath);
            if (fileInfo.Length < _logChunkSize)
                return;

            var fileTime = DateTime.Now.ToString("dd-MM-yyyy,hh-mm-ss,fff");
            var rotatedPath = filePath.Replace(".log", $".{fileTime}");
            File.Move(filePath, rotatedPath);

            var folderPath = Path.GetDirectoryName(rotatedPath);
            var logFolderContent = new DirectoryInfo(folderPath).GetFileSystemInfos();

            var chunks = logFolderContent.Where(x => !x.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase));

            if (chunks.Count() <= _logChunkMaxCount)
                return;

            var archiveFolderInfo = Directory.CreateDirectory(Path.Combine(Path.GetDirectoryName(rotatedPath), $"{LogFolderName}_{fileTime}"));

            foreach (var chunk in chunks) {
                var destination = Path.Combine(archiveFolderInfo.FullName, chunk.Name);
                Directory.Move(chunk.FullName, destination);
            }

            ZipFile.CreateFromDirectory(archiveFolderInfo.FullName, Path.Combine(folderPath, $"{LogFolderName}_{fileTime}.zip"));
            Directory.Delete(archiveFolderInfo.FullName, true);

            var archives = logFolderContent.Where(x => x.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase)).ToArray();

            if (archives.Count() <= _logArchiveMaxCount)
                return;

            var oldestArchive = archives.OrderBy(x => x.CreationTime).First();
            var cleanupDate = oldestArchive.CreationTime.AddDays(_logCleanupPeriod);
            if (DateTime.Compare(cleanupDate, DateTime.Now) <= 0) {
                foreach (var file in logFolderContent) {
                    file.Delete();
                }
            } else
                File.Delete(oldestArchive.FullName);

        }

        public override string ToString() => $"{base.ToString()}, Chunk Size: {_logChunkSize}, Max chunk count: {_logChunkMaxCount}, Max log archive count: {_logArchiveMaxCount}, Cleanup period: {_logCleanupPeriod} days]";
    }


}
