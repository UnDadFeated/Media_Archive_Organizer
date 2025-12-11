using System;
using System.Threading.Tasks;
using System.Windows;
using Microsoft.Win32;
using Media_Archive_Organizer; // Core Library

namespace Media_Archive_Organizer.UI;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    private void BtnBrowse_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFolderDialog();
        dialog.Title = "Select Source Folder";
        dialog.Multiselect = false;
        
        if (dialog.ShowDialog() == true)
        {
            TxtSourcePath.Text = dialog.FolderName;
        }
    }

    private async void BtnStart_Click(object sender, RoutedEventArgs e)
    {
        string path = TxtSourcePath.Text;
        if (string.IsNullOrWhiteSpace(path) || !System.IO.Directory.Exists(path))
        {
            MessageBox.Show("Please select a valid source directory.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            return;
        }

        bool isDry = ChkDryRun.IsChecked == true;
        bool photos = ChkPhotos.IsChecked == true;
        bool videos = ChkVideos.IsChecked == true;

        BtnStart.IsEnabled = false;
        TxtLog.Clear();
        AppendLog("Initializing Logic 2.0 Engine...");

        var options = new OrganizerOptions
        {
            SourcePath = path,
            IsDryRun = isDry,
            OrganizePhotos = photos,
            OrganizeVideos = videos
        };

        var engine = new OrganizerEngine(options, AppendLog);

        await Task.Run(() => 
        {
            try 
            {
                engine.Run();
            } 
            catch (Exception ex)
            {
                // Marshal to UI thread
                Dispatcher.Invoke(() => AppendLog($"FATAL ERROR: {ex.Message}"));
            }
        });

        BtnStart.IsEnabled = true;
        AppendLog("Done.");
    }

    private void AppendLog(string message)
    {
        // Thread-safe UI update
        Dispatcher.Invoke(() => 
        {
            TxtLog.AppendText(message + Environment.NewLine);
            TxtLog.ScrollToEnd();
        });
    }
}