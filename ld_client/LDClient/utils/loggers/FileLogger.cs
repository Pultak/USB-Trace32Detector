using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;

namespace LDClient.utils.loggers
{
    public class FileLogger : ALogger
    {

        /// <summary>
        /// Folder name for the created log files
        /// </summary>
        private const string LogFolderName = "logs";
        /// <summary>
        /// Base name of the log file
        /// </summary>
        private const string LogFileName = "app_info.log";

        private readonly int _logChunkSize = Program.Config.LogChunkSize;
        private readonly int _logChunkMaxCount = Program.Config.LogChunkMaxCount;
        private readonly int _logArchiveMaxCount = Program.Config.LogArchiveMaxCount;
        private readonly int _logCleanupPeriod = Program.Config.LogCleanupPeriod;

        /// <summary>
        /// Destination folder used to store the created logs and zipped chunks
        /// </summary>
        private const string LogFolderPath = "ldClient\\" + LogFolderName;

        /// <summary>
        /// Flag that indicates that the log folder is already created
        /// </summary>
        private bool _logDirExists;

        /// <summary>
        /// Creates one entry in the rotating file.
        /// If the current log file is too big, it creates new log file.
        /// If there is too many log files it archives them.
        /// Deletes all archived files that are too old
        /// </summary>
        /// <param name="message">Desired message to be logged<</param>
        protected override void CreateLog(string message)
        {
            if (!_logDirExists)
            {
                _logDirExists = Directory.Exists(LogFolderPath);
                if (!_logDirExists)
                {
                    Directory.CreateDirectory(LogFolderPath);
                    _logDirExists = true;
                }
            }

            var logFilePath = Path.Combine(LogFolderPath, LogFileName);

            Rotate(logFilePath);

            using var sw = File.AppendText(logFilePath);
            sw.WriteLine(message);
        }

        /// <summary>
        /// Rotates last log file by creating new logging file in the process
        /// </summary>
        /// <param name="filePath">path to the last log file</param>
        private void Rotate(string filePath)
        {
            if (!File.Exists(filePath))
            {
                return;
            }

            var fileInfo = new FileInfo(filePath);
            if (fileInfo.Length < _logChunkSize)
            {
                return;
            }
            var fileTime = DateTime.Now.ToString("dd-MM-yyyy,hh-mm-ss,fff");
            var rotatedPath = filePath.Replace(".log", $".{fileTime}");
            File.Move(filePath, rotatedPath);

            var folderPath = Path.GetDirectoryName(rotatedPath);
            var logFolderContent = new DirectoryInfo(folderPath ?? string.Empty).GetFileSystemInfos();

            var chunks = logFolderContent.Where(x =>
                !x.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase));

            if (chunks.Count() <= _logChunkMaxCount)
            {
                return;
            }

            Archive(chunks, rotatedPath, fileTime, folderPath);
            DeleteOldArchives(logFolderContent);
        }

        /// <summary>
        /// Archives the all the last log files (chunks) 
        /// </summary>
        /// <param name="chunks">All log files that will be archived</param>
        /// <param name="rotatedPath">path to the log files, which will be archived</param>
        /// <param name="fileTime">current time stamp in string</param>
        /// <param name="folderPath">path to to the exported archives</param>
        private void Archive(IEnumerable<FileSystemInfo> chunks, string rotatedPath, string fileTime, string? folderPath)
        {

            var archiveFolderInfo = Directory.CreateDirectory(Path.Combine(Path.GetDirectoryName(rotatedPath) ?? LogFolderPath, $"{LogFolderName}_{fileTime}"));

            foreach (var chunk in chunks)
            {
                var destination = Path.Combine(archiveFolderInfo.FullName, chunk.Name);
                Directory.Move(chunk.FullName, destination);
            }

            ZipFile.CreateFromDirectory(archiveFolderInfo.FullName, Path.Combine(folderPath ?? LogFolderPath, $"{LogFolderName}_{fileTime}.zip"));
            Directory.Delete(archiveFolderInfo.FullName, true);
        }

        /// <summary>
        /// This function deletes all archives that are too old and exceeds the maximum zip files.
        /// Cleanup period and zip max count can be specified in the configuration file.
        /// </summary>
        /// <param name="logFolderContent">filesystem info of the log folder</param>
        private void DeleteOldArchives(FileSystemInfo[] logFolderContent)
        {

            var archives = logFolderContent.Where(x => x.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase)).ToArray();

            if (archives.Length <= _logArchiveMaxCount)
                return;

            //find oldest archive in the folder
            var oldestArchive = archives.OrderBy(x => x.CreationTime).First();
            var cleanupDate = oldestArchive.CreationTime.AddDays(_logCleanupPeriod);
            //is there any file older than specified cleanup cleanup period
            if (DateTime.Compare(cleanupDate, DateTime.Now) <= 0)
            {
                foreach (var file in logFolderContent)
                {
                    file.Delete();
                }
            }
            else
            {
                File.Delete(oldestArchive.FullName);
            }
        }
        public override string ToString() => $"{base.ToString()}, Chunk Size: {_logChunkSize}, Max chunk count: {_logChunkMaxCount}, Max log archive count: {_logArchiveMaxCount}, Cleanup period: {_logCleanupPeriod} days]";
    }
}