using System;

namespace LDClient.utils.loggers
{
    public class ConsoleLogger : ALogger
    {
        /// <summary>
        /// CreateLog function for the ConsoleLogger prints the desired message to the console
        /// </summary>
        /// <param name="message">Desired message to be printed</param>
        protected override void CreateLog(string message)
        {
            Console.WriteLine(message);
        }
    }
}
