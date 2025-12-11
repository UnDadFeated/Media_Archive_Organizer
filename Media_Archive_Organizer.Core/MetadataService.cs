using MetadataExtractor;
using MetadataExtractor.Formats.Exif;
using MetadataExtractor.Formats.QuickTime;
using MetadataExtractor.Formats.Avi;
using MetadataExtractor.Formats.FileSystem;

namespace Media_Archive_Organizer;

public class MetadataService
{
    public DateTime? GetOriginalCreationDate(string filePath)
    {
        try
        {
            var directories = ImageMetadataReader.ReadMetadata(filePath);

            // 1. Try EXIF SubIFD (Images)
            var subIfdDirectory = directories.OfType<ExifSubIfdDirectory>().FirstOrDefault();
            if (subIfdDirectory != null && subIfdDirectory.TryGetDateTime(ExifDirectoryBase.TagDateTimeOriginal, out var dateOriginal))
            {
                return dateOriginal;
            }

            // 2. Try QuickTime (MP4, MOV)
            var qtDirectory = directories.OfType<QuickTimeMovieHeaderDirectory>().FirstOrDefault();
            if (qtDirectory != null && qtDirectory.TryGetDateTime(QuickTimeMovieHeaderDirectory.TagCreated, out var qtDate))
            {
                // QuickTime dates are typically UTC. Convert to Local Time.
                return qtDate.ToLocalTime();
            }
            
            // 3. Try AVI
            // AVI metadata is less standardized in MetadataExtractor, often falls back to file properties or specific streams.
            // We checks for standard distinct tags if possible, otherwise we might rely on file system stats if better tags aren't found.
            
            // 4. Fallback: Check for other common date tags (e.g. Digitized)
            if (subIfdDirectory != null && subIfdDirectory.TryGetDateTime(ExifDirectoryBase.TagDateTimeDigitized, out var dateDigitized))
            {
                return dateDigitized;
            }

            // If no internal metadata found, return null (caller will decide fallback)
            return null;
        }
        catch (Exception)
        {
            // If reading metadata fails (e.g. corrupt file or unsupported format), return null
            return null;
        }
    }
}
