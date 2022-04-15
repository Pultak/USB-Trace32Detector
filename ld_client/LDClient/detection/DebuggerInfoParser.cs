using System.Text.RegularExpressions;

namespace LDClient.detection {

    public static class DebuggerInfoParser {

        private const int ExpectedNumberOfMatches = 2;
        
        private static readonly Regex SerialNumberRegex = new("(?<=Serial Number: )(.*)");
        
        public static (string headSerialNumber, string bodySerialNumber) Parse(string dataTxt) {
            var matches = SerialNumberRegex.Matches(dataTxt);

            if (matches.Count != ExpectedNumberOfMatches) {
                throw new ArgumentException($"Expected {ExpectedNumberOfMatches} matches to be found in the text (actually found: {matches.Count})");
            }
            
            return (matches[0].ToString(), matches[1].ToString());
        }
    }
}