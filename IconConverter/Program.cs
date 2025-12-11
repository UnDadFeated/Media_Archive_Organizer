using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

namespace IconConverter;

class Program
{
    static void Main(string[] args)
    {
        string inputPath = @"..\app_icon.png";
        string outputPath = @"..\app_icon.ico";

        if (!File.Exists(inputPath))
        {
            Console.WriteLine("Input file not found: " + inputPath);
            return;
        }

        // 1. Load Original (Source)
        using (var fs = new FileStream(inputPath, FileMode.Open, FileAccess.Read))
        using (var source = new Bitmap(fs))
        {
            // 2. Create Explicit 32-bit ARGB Bitmap (Destination)
            // This guarantees we have an Alpha channel. 
            // Often "new Bitmap(stream)" keeps the original format (e.g. 24bpp RGB) which turns "Transparent" into Black/White.
            int size = 256;
            using (var finalBmp = new Bitmap(size, size, PixelFormat.Format32bppArgb))
            {
                using (var g = Graphics.FromImage(finalBmp))
                {
                    // Clean canvas
                    g.Clear(Color.Transparent);
                    
                    // High quality scaling
                    g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
                    g.DrawImage(source, new Rectangle(0, 0, size, size));
                }

                // 3. Apply Aggressive Chroma Key to the *Final* 32-bit Bitmap
                ApplyGreenScreenFilter(finalBmp);

                // 4. Save as ICO
               using (var fileStream = new FileStream(outputPath, FileMode.Create))
               {
                   // ICO Header
                   fileStream.WriteByte(0); fileStream.WriteByte(0); 
                   fileStream.WriteByte(1); fileStream.WriteByte(0); 
                   fileStream.WriteByte(1); fileStream.WriteByte(0); 

                   // Directory Entry
                   fileStream.WriteByte((byte)(size >= 256 ? 0 : size)); 
                   fileStream.WriteByte((byte)(size >= 256 ? 0 : size)); 
                   fileStream.WriteByte(0); 
                   fileStream.WriteByte(0); 
                   fileStream.WriteByte(0); fileStream.WriteByte(0); 
                   fileStream.WriteByte(32); fileStream.WriteByte(0); 
                   
                   // PNG Data
                   using (var memoryStream = new MemoryStream())
                   {
                       finalBmp.Save(memoryStream, ImageFormat.Png);
                       byte[] pngData = memoryStream.ToArray();
                       int dataSize = pngData.Length;
                       
                       fileStream.WriteByte((byte)(dataSize & 0xFF));
                       fileStream.WriteByte((byte)((dataSize >> 8) & 0xFF));
                       fileStream.WriteByte((byte)((dataSize >> 16) & 0xFF));
                       fileStream.WriteByte((byte)((dataSize >> 24) & 0xFF));

                       fileStream.WriteByte(22); fileStream.WriteByte(0); fileStream.WriteByte(0); fileStream.WriteByte(0);

                       fileStream.Write(pngData, 0, pngData.Length);
                   }
               }
            }
        }
        Console.WriteLine("Icon created successfully (Force 32bpp).");
    }

    static void ApplyGreenScreenFilter(Bitmap bmp)
    {
        int pixelsChanged = 0;
        for (int y = 0; y < bmp.Height; y++)
        {
            for (int x = 0; x < bmp.Width; x++)
            {
                Color pixel = bmp.GetPixel(x, y);
                
                // Heuristic: Is it predominantly GREEN?
                // Visual green is usually G > R and G > B.
                
                if (pixel.G > 80 && // Lowered threshold slightly to catch dark green shadows
                    pixel.G > pixel.R + 30 && // Difference check
                    pixel.G > pixel.B + 30)   // Difference check
                {
                    bmp.SetPixel(x, y, Color.Transparent);
                    pixelsChanged++;
                }
            }
        }
        Console.WriteLine($"Aggressive Filter: Made {pixelsChanged} pixels transparent.");
    }
}
