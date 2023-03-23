using System;
using System.Collections.Generic;
using System.Globalization;
using System.Threading;

namespace LDClient.utils.loggers
{
    /// <summary>
    /// This class implements all abstract functions of the logger.
    /// It contains all functions (error, info, debug) that are present in any other standard logger.
    /// Class is used as singleton design pattern
    /// </summary>
    public abstract class ALogger : IDisposable
    {
        /// <summary>
        /// Logger verbosity type identifies how much information should be actually logged
        /// </summary>
        private readonly LogVerbosity _verbosity;

        /// <summary>
        /// Current type of logger
        /// </summary>
        private readonly LogFlow _logFlow;

        /// <summary>
        /// Queue of all not yet logged messages
        /// </summary>
        private readonly Queue<Action> _queue = new();

        /// <summary>
        /// Synchronization prime used to identify if the is anything new in the queue 
        /// </summary>
        private readonly ManualResetEvent _hasNewItems = new(false);
        /// <summary>
        /// Synchronization prime used to identify if the logger should be terminated
        /// </summary>
        private readonly ManualResetEvent _terminate = new(false);
        /// <summary>
        /// Synchronization prime used to identify if the current thread is waiting
        /// </summary>
        private readonly ManualResetEvent _waiting = new(false);

        /// <summary>
        /// Thread instance of logging thread
        /// </summary>
        private readonly Thread _loggingThread;

        /// <summary>
        /// Instance of the default logger initialized with the lazy binding mechanism
        /// </summary>
        private static readonly Lazy<ALogger> LazyLog = new(()
            =>
        {
            switch (Program.Config.LogFlowType)
            {
                case LogFlow.File:
                    return new FileLogger();
                case LogFlow.Console:
                default:
                    return new ConsoleLogger();

            }
        }
        );

        /// <summary>
        /// Instance of the current logger type
        /// </summary>
        public static ALogger Current => LazyLog.Value;

        /// <summary>
        /// Singleton constructor that initialized and starts the logger with arguments parsed by the config loader
        /// </summary>
        protected ALogger()
        {
            _verbosity = Program.Config.LogVerbosityType;
            _logFlow = Program.Config.LogFlowType;
            _loggingThread = new Thread(ProcessQueue) { IsBackground = true };
            _loggingThread.Start();
        }

        /// <summary>
        /// Creates new log with Info identifier
        /// </summary>
        /// <param name="message">Desired message to be logged</param>
        public void Info(string message)
        {
            Log(message, LogType.Info);
        }

        /// <summary>
        /// Creates new log with Debug identifier
        /// </summary>
        /// <param name="message">Desired message to be logged</param>
        public void Debug(string message)
        {
            Log(message, LogType.Debug);
        }

        /// <summary>
        /// Creates new log with Error identifier
        /// </summary>
        /// <param name="message">Desired message to be logged</param>
        public void Error(string message)
        {
            Log(message, LogType.Error);
        }

        /// <summary>
        /// Creates new log from the catched exception
        /// </summary>
        /// <param name="e">catched exception tha should be logged</param>
        public void Error(Exception e)
        {
            if (_verbosity != LogVerbosity.None)
            {
                Log(UnwrapExceptionMessages(e), LogType.Error);
            }
        }

        /// <summary>
        /// Creates new string info about current logger configuration
        /// </summary>
        /// <returns></returns>
        public override string ToString() => $"Logger settings: [Type: {this.GetType().Name}, Verbosity: {_verbosity}, ";

        protected abstract void CreateLog(string message);

        /// <summary>
        /// Waits for the logger to finish the logging
        /// </summary>
        public void Flush() => _waiting.WaitOne();

        /// <summary>
        /// Function stops the logger thread
        /// </summary>
        public void Dispose()
        {
            _terminate.Set();
            _loggingThread.Join();
        }

        /// <summary>
        /// Composes the log with actual timestamp, log type and its main message
        /// </summary>
        /// <param name="message">main message of the log</param>
        /// <param name="logType">Type of the logged message</param>
        /// <returns></returns>
        protected virtual string ComposeLogRow(string message, LogType logType) =>
            $"[{DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss,fff", CultureInfo.InvariantCulture)} - {logType}] - {message}";

        /// <summary>
        /// Function creates log from the catched exception
        /// </summary>
        /// <param name="ex">catched exception tha should be logged</param>
        /// <returns></returns>
        protected virtual string UnwrapExceptionMessages(Exception? ex) =>
            ex == null ? string.Empty : $"{ex}, Inner exception: {UnwrapExceptionMessages(ex.InnerException)} ";

        /// <summary>
        /// Function that periodically processes message queue
        /// </summary>
        private void ProcessQueue()
        {
            while (true)
            {
                _waiting.Set();
                //wait until there is new item in the queue or until termination invoked
                var i = WaitHandle.WaitAny(new WaitHandle[] { _hasNewItems, _terminate });
                //was the termination invoked?
                if (i == 1) return;
                _hasNewItems.Reset();
                _waiting.Reset();

                Queue<Action> queueCopy;
                lock (_queue)
                {
                    queueCopy = new Queue<Action>(_queue);
                    _queue.Clear();
                }

                foreach (var log in queueCopy)
                {
                    log();
                }
            }
        }

        /// <summary>
        /// Creates new log string from the current timestamp 
        /// </summary>
        /// <param name="message"></param>
        /// <param name="logType"></param>
        private void Log(string message, LogType logType)
        {
            if (string.IsNullOrEmpty(message))
                return;

            var logRow = ComposeLogRow(message, logType);
            System.Diagnostics.Debug.WriteLine(logRow);

            if (_verbosity == LogVerbosity.Full)
            {
                lock (_queue)
                    _queue.Enqueue(() => CreateLog(logRow));

                _hasNewItems.Set();
            }
        }
    }
}