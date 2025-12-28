import customtkinter as ctk
from ui.tabs import OrganizerTab, AIScannerTab, DonateTab
import sys
import os
from core.logger import setup_logger
from version import __version__, APP_NAME

# Ensure src is in path logic if running raw
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.logger.info("Initializing Main App Window")

        self.title(f"{APP_NAME} {__version__}")
        self.geometry("1000x550")
        
        # Grid Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # Log Area option
        self.grid_columnconfigure(0, weight=1)

        # Tab View
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_org = self.tab_view.add("Media Organizer")
        self.tab_ai = self.tab_view.add("AI Objects Scanner")
        self.tab_donate = self.tab_view.add("Donate")

        # Init Tabs
        # Tab 1
        self.org_frame = OrganizerTab(self.tab_org, self.log, self.logger)
        self.org_frame.pack(fill="both", expand=True)

        # Tab 2
        self.ai_frame = AIScannerTab(self.tab_ai, self.log, self.logger)
        self.ai_frame.pack(fill="both", expand=True)

        # Tab 3
        self.donate_frame = DonateTab(self.tab_donate)
        self.donate_frame.pack(fill="both", expand=True)
        
        # Log Area (Bottom) - Shared
        self.log_text = ctk.CTkTextbox(self, height=100, font=("Consolas", 12))
        self.log_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.log(f"Welcome to {APP_NAME} {__version__} (Python Edition)")
        self.log("Ready.")

    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

if __name__ == "__main__":
    app = App()
    app.mainloop()
