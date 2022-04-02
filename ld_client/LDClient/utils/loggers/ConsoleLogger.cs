namespace LDClient.utils.loggers {
    public class ConsoleLogger : ALogger {
        protected override void CreateLog(string message) {
            Console.WriteLine(message);
        }
    }
}
