using System;
using System.IO;

namespace Media_Archive_Organizer;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("=========================================");
        Console.WriteLine("     Media Archive Organizer v1.01       ");
        Console.WriteLine("=========================================");
        Console.WriteLine();
        
        // 1. Get Path
        string? sourcePath = "";
        if (args.Length > 0 && Directory.Exists(args[0]))
        {
            sourcePath = args[0];
            Console.WriteLine($"Source: {sourcePath}");
        }
        else
        {
            Console.Write("Enter the source folder path to process: ");
            sourcePath = Console.ReadLine()?.Trim();
        }

        if (string.IsNullOrEmpty(sourcePath) || !Directory.Exists(sourcePath))
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine("Error: Invalid directory path.");
            Console.ResetColor();
            return;
        }

        // 2. Dry Run Prompt
        Console.WriteLine();
        Console.Write("Run in Dry Run mode (simulate only)? [Y/n]: ");
        string? dryRunInput = Console.ReadLine()?.Trim().ToLower();
        bool isDryRun = string.IsNullOrEmpty(dryRunInput) || dryRunInput == "y" || dryRunInput == "yes";

        var options = new OrganizerOptions
        {
            SourcePath = sourcePath,
            IsDryRun = isDryRun,
            OrganizePhotos = true,
            OrganizeVideos = true
        };

        // 3. Run Engine
        var engine = new OrganizerEngine(options, (msg) => Console.WriteLine(msg));
        engine.Run();

        Console.WriteLine();
        Console.WriteLine("Press any key to exit...");
        Console.ReadKey();
    }
}
