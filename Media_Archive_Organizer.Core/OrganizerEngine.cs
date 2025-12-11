using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace Media_Archive_Organizer;

public class OrganizerOptions
{
    public required string SourcePath { get; set; }
    public bool IsDryRun { get; set; }
    public bool OrganizePhotos { get; set; } = true;
    public bool OrganizeVideos { get; set; } = true;
}

public class OrganizerEngine
{
    private readonly OrganizerOptions _options;
    private readonly MetadataService _metadataService;
    private readonly Action<string> _logger; // Callback for UI/Console logging
    
    // Thread-safe stats
    private int _processedCount = 0;
    private int _errorCount = 0;
    private int _skippedCount = 0; // Duplicates

    private static readonly HashSet<string> ImageExtensions = new(StringComparer.OrdinalIgnoreCase) 
    { 
        ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".png",
        ".heic", ".cr2", ".nef", ".arw", ".dng" // RAW & HEIC support
    };
    
    private static readonly HashSet<string> VideoExtensions = new(StringComparer.OrdinalIgnoreCase) 
    { 
        ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".m4v"
    };

    public OrganizerEngine(OrganizerOptions options, Action<string> logger)
    {
        _options = options;
        _logger = logger;
        _metadataService = new MetadataService();
    }

    public void Run()
    {
        string sourcePath = _options.SourcePath;
        if (!Directory.Exists(sourcePath))
        {
            _logger($"[ERROR] Source directory not found: {sourcePath}");
            return;
        }

        _logger($"Starting Organization...");
        _logger($"Mode: {(_options.IsDryRun ? "DRY RUN (No changes)" : "LIVE EXECUTION")}");
        _logger("Scanning files...");

        _logger("Scanning files (streaming mode)...");

        // MEMORY LEAK FIX: Use EnumerateFiles instead of GetFiles to avoid loading millions of strings into RAM.
        // Also removed .ToList() to maintain lazy evaluation.
        var allFiles = Directory.EnumerateFiles(sourcePath, "*.*", SearchOption.AllDirectories);
        
        // Note: For Parallel.ForEach with EnumerateFiles, we just pass the IEnumerable.
        // However, EnumerateFiles can throw access exceptions on system folders. 
        // A robust solution might need a custom traverser, but for this scope, standard Enumerate is safer than GetFiles array.

        string photosRoot = Path.Combine(sourcePath, "Photos");
        string videosRoot = Path.Combine(sourcePath, "Videos");

        if (!_options.IsDryRun)
        {
            if (_options.OrganizePhotos) Directory.CreateDirectory(photosRoot);
            if (_options.OrganizeVideos) Directory.CreateDirectory(videosRoot);
        }

        // Setup Log File
        string logFileName = $"process_log_{DateTime.Now:yyyyMMdd_HHmmss}{(_options.IsDryRun ? "_DRYRUN" : "")}.txt";
        string logFilePath = Path.Combine(sourcePath, logFileName);
        
        using (StreamWriter logFile = new StreamWriter(logFilePath, false, Encoding.UTF8))
        {
            // Thread-safe wrapper for file writing
            object fileLock = new object();
            void LogToFile(string line) { lock(fileLock) { logFile.WriteLine(line); } }

            LogToFile($"Media Archive Organizer Log - {DateTime.Now}");
            LogToFile($"Source: {sourcePath}");
            LogToFile($"Dry Run: {_options.IsDryRun}");
            LogToFile("--------------------------------------------------");

            // PARALLEL PROCESSING
            // We use the enumerable directly.
            Parallel.ForEach(allFiles, new ParallelOptions { MaxDegreeOfParallelism = Environment.ProcessorCount }, (file) =>
            {
                try
                {
                    if (IsMediaFile(file))
                    {
                        ProcessFile(file, photosRoot, videosRoot, LogToFile);
                    }
                }
                catch (Exception ex)
                {
                   Interlocked.Increment(ref _errorCount);
                   string err = $"[ERROR] Error processing {Path.GetFileName(file)}: {ex.Message}";
                   _logger(err);
                   LogToFile(err);
                }
            });

            LogToFile("--------------------------------------------------");
            LogToFile($"Summary: Processed {_processedCount}, Skipped/Duplicates {_skippedCount}, Errors {_errorCount}");
        }

        _logger("");
        _logger("=========================================");
        _logger($"Run Complete! Log: {logFileName}");
        _logger($"Processed: {_processedCount}");
        _logger($"Duplicates/Skipped: {_skippedCount}");
        _logger($"Errors: {_errorCount}");
        _logger("=========================================");
    }

    private bool IsMediaFile(string path)
    {
        string ext = Path.GetExtension(path);
        if (ImageExtensions.Contains(ext)) return _options.OrganizePhotos;
        if (VideoExtensions.Contains(ext)) return _options.OrganizeVideos;
        return false;
    }

    private void ProcessFile(string file, string photosRoot, string videosRoot, Action<string> logToFile)
    {
        // Skip if already in destination folders (prevent recursive mess)
        if (file.StartsWith(photosRoot, StringComparison.OrdinalIgnoreCase) || 
            file.StartsWith(videosRoot, StringComparison.OrdinalIgnoreCase))
        {
            return;
        }

        string extension = Path.GetExtension(file);
        bool isImage = ImageExtensions.Contains(extension);
        
        // 1. Get Date
        DateTime date = _metadataService.GetOriginalCreationDate(file) ?? File.GetLastWriteTime(file);
        
        // 2. Determine Target
        string yearMonth = date.ToString("yyyy-MM");
        string targetBase = isImage ? photosRoot : videosRoot;
        string targetFolder = Path.Combine(targetBase, yearMonth);
        
        // 3. Build Name
        string originalName = Path.GetFileName(file);
        string datePrefix = date.ToString("yyyy-MM-dd_");
        
        // Avoid double prefixing if run multiple times
        string newFileName = originalName.StartsWith(datePrefix) ? originalName : datePrefix + originalName;
        string targetPath = Path.Combine(targetFolder, newFileName);

        // 4. Handle Collisions (Deduplication)
        if (File.Exists(targetPath))
        {
            if (AreFilesIdentical(file, targetPath))
            {
                Interlocked.Increment(ref _skippedCount);
                string msg = $"[DUPLICATE] Skipped {Path.GetFileName(file)} (Identical to existing {Path.GetFileName(targetPath)})";
                _logger(msg);
                logToFile(msg);
                return; // SKIP MOVE
            }
            else
            {
                // Name Collision only - Rename
                int counter = 1;
                while (File.Exists(targetPath))
                {
                    string nameNoExt = Path.GetFileNameWithoutExtension(newFileName);
                    // Handle existing _1 to prevent _1_1_1
                    // Simple approach: append counter to original-ish base
                    string duplicateName = $"{Path.GetFileNameWithoutExtension(newFileName)}_{counter}{extension}";
                    targetPath = Path.Combine(targetFolder, duplicateName);
                    counter++;
                }
            }
        }

        // 5. Execution
        string relDest = Path.Combine(yearMonth, Path.GetFileName(targetPath));
        string logMsg = $"{( _options.IsDryRun ? "[DRY RUN]" : "[SUCCESS]" )} {originalName} -> {relDest}";

        _logger(logMsg);
        logToFile(logMsg);

        if (!_options.IsDryRun)
        {
             // Create specific subfolder just-in-time safely
             Directory.CreateDirectory(targetFolder); 
             File.Move(file, targetPath);
        }
        
        Interlocked.Increment(ref _processedCount);
    }

    private bool AreFilesIdentical(string file1, string file2)
    {
        // 1. Fast Check: Size
        var fh1 = new FileInfo(file1);
        var fh2 = new FileInfo(file2);
        if (fh1.Length != fh2.Length) return false;

        // 2. Slow Check: MD5
        // For performance on large videos, we might want to read chunks, but MD5 is safest.
        using (var md5 = MD5.Create())
        using (var stream1 = File.OpenRead(file1))
        using (var stream2 = File.OpenRead(file2))
        {
            byte[] hash1 = md5.ComputeHash(stream1);
            byte[] hash2 = md5.ComputeHash(stream2);
            return hash1.SequenceEqual(hash2);
        }
    }
}
