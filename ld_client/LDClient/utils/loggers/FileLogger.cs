using System.IO.Compression;

namespace LDClient.utils.loggers; 

public class FileLogger : ALogger {

    private const string LogFolderName = "logs";
    private const string LogFileName = "app_info.log";
    private readonly int _logChunkSize = Program.Config.LogChunkSize;
    private readonly int _logChunkMaxCount = Program.Config.LogChunkMaxCount;
    private readonly int _logArchiveMaxCount = Program.Config.LogArchiveMaxCount;
    private readonly int _logCleanupPeriod = Program.Config.LogCleanupPeriod;

    private const string LogFolderPath = $"ldClient\\{LogFolderName}";

    private bool _logDirExists;

    protected override void CreateLog(string message) {

        if (!_logDirExists) {
            _logDirExists = Directory.Exists(LogFolderPath);
            if (!_logDirExists) {
                Directory.CreateDirectory(LogFolderPath);
                _logDirExists = true;
            }
        }

        var logFilePath = Path.Combine(LogFolderPath, LogFileName);

        Rotate(logFilePath);

        using var sw = File.AppendText(logFilePath);
        sw.WriteLine(message);
    }

    private void Rotate(string filePath) {
        if (!File.Exists(filePath)) {
            return;
        }

        var fileInfo = new FileInfo(filePath);
        if (fileInfo.Length < _logChunkSize) {
            return;
        }
        var fileTime = DateTime.Now.ToString("dd-MM-yyyy,hh-mm-ss,fff");
        var rotatedPath = filePath.Replace(".log", $".{fileTime}");
        File.Move(filePath, rotatedPath);

        var folderPath = Path.GetDirectoryName(rotatedPath);
        var logFolderContent = new DirectoryInfo(folderPath ?? string.Empty).GetFileSystemInfos();

        var chunks = logFolderContent.Where(x => 
            !x.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase));

        if (chunks.Count() <= _logChunkMaxCount) {
            return;
        }

        Archive(chunks, rotatedPath, fileTime, folderPath);
        DeleteOldArchives(logFolderContent);
    }

    private void Archive(IEnumerable<FileSystemInfo> chunks, string rotatedPath, string fileTime, string? folderPath) {

        var archiveFolderInfo = Directory.CreateDirectory(Path.Combine(Path.GetDirectoryName(rotatedPath) ?? LogFolderPath, $"{LogFolderName}_{fileTime}"));

        foreach (var chunk in chunks) {
            var destination = Path.Combine(archiveFolderInfo.FullName, chunk.Name);
            Directory.Move(chunk.FullName, destination);
        }

        ZipFile.CreateFromDirectory(archiveFolderInfo.FullName, Path.Combine(folderPath ?? LogFolderPath, $"{LogFolderName}_{fileTime}.zip"));
        Directory.Delete(archiveFolderInfo.FullName, true);
    }

    private void DeleteOldArchives(FileSystemInfo[] logFolderContent) {

        var archives = logFolderContent.Where(x => x.Extension.Equals(".zip", StringComparison.OrdinalIgnoreCase)).ToArray();

        if (archives.Length <= _logArchiveMaxCount)
            return;

        var oldestArchive = archives.OrderBy(x => x.CreationTime).First();
        var cleanupDate = oldestArchive.CreationTime.AddDays(_logCleanupPeriod);
        if (DateTime.Compare(cleanupDate, DateTime.Now) <= 0) {
            foreach (var file in logFolderContent) {
                file.Delete();
            }
        } else {
            File.Delete(oldestArchive.FullName);
        }
    }

    public override string ToString() => $"{base.ToString()}, Chunk Size: {_logChunkSize}, Max chunk count: {_logChunkMaxCount}, Max log archive count: {_logArchiveMaxCount}, Cleanup period: {_logCleanupPeriod} days]";
}