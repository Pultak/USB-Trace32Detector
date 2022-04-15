namespace LDClient.utils {

    public static class IoUtils {

        public static string ReadFile(string filename) {
            return File.ReadAllLines(filename).Aggregate("", (current, line) => $"{current}{line}\n");
        }
    }
}