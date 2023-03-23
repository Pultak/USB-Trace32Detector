using System;
using LDClient.detection;
using NUnit.Framework;

namespace LDClientTests.detection
{
    public class DebuggerInfoParserTests
    {
        public static readonly string CorrectFileContent =
            "B::version.hardware \r\n\r\n" +
            "PowerDebug USB 3.0 via USB 3.0 \r\n\r\n" +
            "   Serial Number: C12345678912 \r\n\r\n" +
            "   Firmware R.2021.02 (136263) \r\n\r\n" +
            "   Instance: 1. \r\n\r\n" +
            "   Automotive Debug Cable \r\n\r\n" +
            "      Serial Number: C98765432198 ";

        public static readonly string HeadSerialNumber = "C98765432198";
        public static readonly string BodySerialNumber = "C12345678912";


        [Test]
        [TestCase("B::version.hardware \r\n\r\n" +
                  "PowerDebug USB 3.0 via USB 3.0 \r\n\r\n" +
                  "   Serial Number: C12345678912 \r\n\r\n" +
                  "   Firmware R.2021.02 (136263) \r\n\r\n" +
                  "   Instance: 1. \r\n\r\n" +
                  "   Automotive Debug Cable \r\n\r\n" +
                  "      Serial Number: C12345678912 ", "C12345678912", "C12345678912")]
        [TestCase("B::version.hardware \r\n\r\n" +
                  "PowerDebug USB 3.0 via USB 3.0 \r\n\r\n" +
                  "   Serial Number: C1awfaw484 \r\n\r\n" +
                  "   Firmware R.2021.02 (136263) \r\n\r\n" +
                  "   Instance: 1. \r\n\r\n" +
                  "   Automotive Debug Cable \r\n\r\n" +
                  "      Serial Number: C16468551", "C16468551", "C1awfaw484")]
        public void Parse_CorrectValues_ReturnSerials(string file, string expectedHead, string expectedBody)
        {
            var (headResult, bodyResult) = DebuggerInfoParser.Parse(file);

            Assert.AreEqual(expectedHead, headResult);
            Assert.AreEqual(expectedBody, bodyResult);
        }


        [Test]
        [TestCase("B::version.hardware \r\n\r\n" +
                  "PowerDebug USB 3.0 via USB 3.0 \r\n\r\n" +
                  "   Serial Number: C12345678912 \r\n\r\n" +
                  "   Firmware R.2021.02 (136263) \r\n\r\n" +
                  "   Instance: 1. \r\n\r\n" +
                  "   Automotive Debug Cable \r\n\r\n" +
                  "      Serial Number: C12345678912 \n" +
                  "      Serial Number: C12345678912 ")]
        [TestCase("B::version.hardware \r\n\r\n" +
                  "PowerDebug USB 3.0 via USB 3.0 \r\n\r\n" +
                  "   Serial Number: C1awfaw484 \r\n\r\n" +
                  "   Firmware R.2021.02 (136263) \r\n\r\n" +
                  "   Instance: 1. \r\n\r\n" +
                  "   Automotive Debug Cable \r\n\r\n" +
                  "      Serial Numbeeeer: C16468551")]
        public void Parse_IncorrectValues_ThrowException(string file)
        {
            Assert.Throws<ArgumentException>(() => DebuggerInfoParser.Parse(file));
        }
    }
}