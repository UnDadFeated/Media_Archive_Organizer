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

import tkinter as tk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.logger.info("Initializing Main App Window")

        self.title(f"{APP_NAME} {__version__}")
        self.geometry("1000x700")
        
        # Use standard tkinter PanedWindow (CustomTkinter doesn't have one)
        # We set sash relief to flat/ridge for better look
        self.paned_window = tk.PanedWindow(self, orient="vertical", sashwidth=6, bg="#2b2b2b")
        self.paned_window.pack(fill="both", expand=True, padx=0, pady=0)

        # === Top Pane: Tab View ===
        # Wrap in a frame to ensure consistent background
        self.top_frame = ctk.CTkFrame(self.paned_window, fg_color="transparent")
        
        self.tab_view = ctk.CTkTabview(self.top_frame)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_org = self.tab_view.add("Media Organizer")
        self.tab_ai = self.tab_view.add("AI Scan")
        self.tab_donate = self.tab_view.add("Donate")

        # Init Tabs
        self.org_frame = OrganizerTab(self.tab_org, self.log, self.logger)
        self.org_frame.pack(fill="both", expand=True)

        self.ai_frame = AIScannerTab(self.tab_ai, self.log, self.logger)
        self.ai_frame.pack(fill="both", expand=True)

        self.donate_frame = DonateTab(self.tab_donate)
        self.donate_frame.pack(fill="both", expand=True)
        
        # Add Top Frame to Paned Window
        self.paned_window.add(self.top_frame, minsize=400) # Ensure tabs don't disappear
        
        # === Bottom Pane: Log Area ===
        self.bottom_frame = ctk.CTkFrame(self.paned_window, fg_color="transparent")
        
        # Visual Grip Area
        self.grip_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent", height=25)
        self.grip_frame.pack(fill="x", padx=0, pady=(0, 0))
        
        # Arrows Label
        self.lbl_grip = ctk.CTkLabel(self.grip_frame, text="▲", font=("Arial", 14, "bold"), text_color="gray")
        self.lbl_grip.pack(pady=(2,0))
        
        # Separator Line
        self.sep = ctk.CTkFrame(self.grip_frame, height=2, fg_color="#404040")
        self.sep.pack(fill="x", padx=20, pady=(2, 5))

        # Console Label
        ctk.CTkLabel(self.bottom_frame, text="LOG CONSOLE", font=("Arial", 10, "bold"), text_color="gray", anchor="w").pack(fill="x", padx=10, pady=(0, 2))
        
        self.log_text = ctk.CTkTextbox(self.bottom_frame, height=150, font=("Consolas", 12))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.paned_window.add(self.bottom_frame, minsize=100)
        
        # Bind resize event to update arrows
        self.bottom_frame.bind("<Configure>", self.update_grip_arrows)
        
        self.log(f"Welcome to {APP_NAME} {__version__} (Python Edition)")
        self.log("Ready.")

    def update_grip_arrows(self, event):
        # Heuristic: If height is small (near minsize), show UP arrow to indicate "Pull Me Up"
        # If height is large, show DOWN arrow to indicate "Push Me Down"
        try:
            h = event.height
            if h < 160: # Threshold for "collapsed" state
                self.lbl_grip.configure(text="▲")
            else:
                self.lbl_grip.configure(text="▼")
        except: pass

    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

if __name__ == "__main__":
    app = App()
    app.mainloop()
