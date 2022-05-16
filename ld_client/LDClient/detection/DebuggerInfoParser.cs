using System.Text.RegularExpressions;

namespace LDClient.detection; 

/// <summary>
/// This class parses the .txt file generated from the debugger.
/// Its primary interest is to find two serial numbers (head + body). 
/// </summary>
public static class DebuggerInfoParser {

    /// <summary>
    /// Number of serial numbers expected to be in the .txt file (number of matches - regex).
    /// </summary>
    private const int ExpectedNumberOfMatches = 2;
        
    /// <summary>
    /// Regular expression used to find the serial numbers.
    /// </summary>
    private static readonly Regex SerialNumberRegex = new("(?<=Serial Number: )(.*)");
        
    /// <summary>
    /// Takes the content of a .txt file and tries to find the two serial numbers (head and body).
    /// If it succeed, it will return the two numbers.
    /// </summary>
    /// <param name="dataTxt">the content of a .txt file (generated from the debugger)</param>
    /// <returns>two serial numbers (head and body) of the debugger</returns>
    /// <exception cref="ArgumentException">throws an exception if it fails to find the serial numbers</exception>
    public static (string headSerialNumber, string bodySerialNumber) Parse(string dataTxt) {
        // Find all matches in the content of the file that satisfy the regular expression.
        var matches = SerialNumberRegex.Matches(dataTxt);

        // Make sure an exact number of matches has been found.
        if (matches.Count != ExpectedNumberOfMatches) {
            throw new ArgumentException($"Expected {ExpectedNumberOfMatches} matches to be found in the text (actually found: {matches.Count})");
        }
            
        // Return the two serial numbers (head and body).
        return (matches[1].ToString().Trim(), matches[0].ToString().Trim());
    }
}