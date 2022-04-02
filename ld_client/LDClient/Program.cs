using LDClient;
using System;


class Program {

    public static LDClient.ConfigLoader Config { get; set; }

    // Main Method
    static public void Main() {
        Config = new LDClient.ConfigLoader();

        while (true) {
            Logger.Current.Info("Ok");
            Logger.Current.Debug("Debug");
            Logger.Current.Error("Error");
        }
    }
}