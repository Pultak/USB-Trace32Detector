using System.Globalization;

namespace LDClient.utils.loggers {

    public abstract class ALogger : IDisposable {

        private readonly LogVerbosity _verbosity;
        private readonly LogFlow _logFlow;

        private readonly Queue<Action> _queue = new();
        private readonly ManualResetEvent _hasNewItems = new(false);
        private readonly ManualResetEvent _terminate = new(false);
        private readonly ManualResetEvent _waiting = new(false);
        private readonly Thread _loggingThread;

        private static readonly Lazy<ALogger> LazyLog = new(()
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

        public static ALogger Current => LazyLog.Value;

        protected ALogger() {
            _verbosity = Program.Config.LogVerbosityType;
            _logFlow = Program.Config.LogFlowType;
            _loggingThread = new Thread(ProcessQueue) { IsBackground = true };
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

        protected virtual string UnwrapExceptionMessages(Exception? ex) =>
            ex == null ? string.Empty : $"{ex}, Inner exception: {UnwrapExceptionMessages(ex.InnerException)} ";
        

        private void ProcessQueue() {
            while (true) {
                _waiting.Set();
                var i = WaitHandle.WaitAny(new WaitHandle[] { _hasNewItems, _terminate });
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
}
