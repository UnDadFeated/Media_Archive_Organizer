import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from PIL import Image
from core.organizer import OrganizerEngine
from core.scanner import ScannerEngine

import webbrowser

class OrganizerTab(ctk.CTkFrame):
    def __init__(self, master, log_callback, file_logger):
        super().__init__(master)
        # Make logger thread-safe
        self.log_callback = log_callback
        self.file_logger = file_logger
        
        def safe_log(msg):
            self.after(0, lambda: self.log_callback(msg))
            
        self.engine = OrganizerEngine(safe_log)
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # === Left Column: Config ===
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Source
        ctk.CTkLabel(self.frame_config, text="SOURCE FOLDER", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=10, pady=(10,0))
        
        self.path_frame = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.path_frame.pack(fill="x", padx=10, pady=5)
        
        self.entry_path = ctk.CTkEntry(self.path_frame, placeholder_text="Select folder...")
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(self.path_frame, text="...", width=40, command=self.browse_source)
        self.btn_browse.pack(side="right")

        # Options
        ctk.CTkLabel(self.frame_config, text="ORGANIZE", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=10, pady=(20,0))
        self.chk_photos = ctk.CTkCheckBox(self.frame_config, text="Photos", onvalue=True, offvalue=False)
        self.chk_photos.select()
        self.chk_photos.pack(anchor="w", padx=20, pady=5)
        
        self.chk_videos = ctk.CTkCheckBox(self.frame_config, text="Videos", onvalue=True, offvalue=False)
        self.chk_videos.select()
        self.chk_videos.pack(anchor="w", padx=20, pady=5)

        # === Right Column: Action ===
        self.frame_action = ctk.CTkFrame(self)
        self.frame_action.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frame_action, text="EXECUTION MODE", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w", padx=10, pady=(10,0))
        
        self.chk_dry_run = ctk.CTkSwitch(self.frame_action, text="Dry Run (Simulation)")
        self.chk_dry_run.select()
        self.chk_dry_run.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(self.frame_action, text="Recommmended for first run.", text_color="gray", font=("Arial", 11)).pack(anchor="w", padx=55, pady=0)

        self.btn_start = ctk.CTkButton(self.frame_action, text="Start Organization", height=40, fg_color="#007ACC", hover_color="#005A9E", command=self.start_organize)
        self.btn_start.pack(fill="x", padx=20, pady=(30, 0))

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self.frame_action)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        self.lbl_progress = ctk.CTkLabel(self.frame_action, text="Ready", text_color="gray")
        self.lbl_progress.pack(pady=5)

    def browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, path)

    def start_organize(self):
        path = self.entry_path.get()
        if not path or not os.path.isdir(path):
            messagebox.showerror("Error", "Invalid Source Directory")
            return
            
        dry_run = bool(self.chk_dry_run.get())
        self.btn_start.configure(state="disabled", text="Working...")
        self.progress_bar.set(0)
        self.lbl_progress.configure(text="Scanning files...")
        
        def on_progress(current, total):
            # Thread-safe update
            self.after(0, lambda: self.update_progress(current, total))

        def run():
            self.engine.organize(path, dry_run=dry_run, progress_callback=on_progress)
            self.after(0, lambda: self.btn_start.configure(state="normal", text="Start Organization"))
            self.after(0, lambda: self.lbl_progress.configure(text="Finished."))
            
        threading.Thread(target=run, daemon=True).start()

    def update_progress(self, current, total):
        if total > 0:
            self.progress_bar.set(current / total)
            self.lbl_progress.configure(text=f"Organizing... {current}/{total}")

class AIScannerTab(ctk.CTkFrame):
    def __init__(self, master, log_callback, file_logger):
        super().__init__(master)
        self.log_callback = log_callback
        self.file_logger = file_logger
        
        def safe_log(msg):
            self.after(0, lambda: self.log_callback(msg))
            
        self.scanner = ScannerEngine(safe_log)
        
        # Internal State
        self.keep_files = []
        self.exclude_files = []
        self.selected_item = None # (list_name, index, file_path)
        
        # Grid Plan:
        # Row 0: Header/Config
        # Row 1: Lists (Left: Keep, Right: Exclude) + Preview
        # Row 2: Actions
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # === Top Config ===
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.entry_path = ctk.CTkEntry(self.top_frame, placeholder_text="Folder to Scan...")
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        self.btn_browse = ctk.CTkButton(self.top_frame, text="...", width=40, command=self.browse_source)
        self.btn_browse.pack(side="left", padx=(0, 10))
        
        # Hardware Selection
        self.var_hw = ctk.StringVar(value="CPU")
        self.rb_cpu = ctk.CTkRadioButton(self.top_frame, text="CPU (MediaPipe)", variable=self.var_hw, value="CPU")
        self.rb_cpu.pack(side="left", padx=5)
        self.rb_gpu = ctk.CTkRadioButton(self.top_frame, text="GPU (OpenCV/OpenCL)", variable=self.var_hw, value="GPU")
        self.rb_gpu.pack(side="left", padx=5)
        
        # Keep Animals Checkbox
        self.chk_keep_animals = ctk.CTkCheckBox(self.top_frame, text="Keep Animals", width=20, onvalue=True, offvalue=False)
        self.chk_keep_animals.pack(side="left", padx=15)
        
        self.btn_scan = ctk.CTkButton(self.top_frame, text="Start 'No People' Scan", fg_color="#C2185B", hover_color="#880E4F", command=self.start_scan)
        self.btn_scan.pack(side="right", padx=10)
        
        # === Main Lists ===
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=1) # Keep
        self.content_frame.grid_columnconfigure(2, weight=1) # Exclude
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Left List (Keep)
        ctk.CTkLabel(self.content_frame, text="FLAGGED (No People)", text_color="#4CAF50", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        
        self.list_keep = ctk.CTkScrollableFrame(self.content_frame, label_text="Files (0)")
        self.list_keep.grid(row=1, column=0, sticky="nsew", padx=(0,5))
        
        # Center Controls
        self.center_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.center_frame.grid(row=1, column=1, padx=5)
        self.btn_mv_right = ctk.CTkButton(self.center_frame, text=">", width=40, command=lambda: self.move_item("right"))
        self.btn_mv_right.pack(pady=5)
        self.btn_mv_left = ctk.CTkButton(self.center_frame, text="<", width=40, command=lambda: self.move_item("left"))
        self.btn_mv_left.pack(pady=5)

        # Right List (Excluded)
        ctk.CTkLabel(self.content_frame, text="EXCLUDED (People)", text_color="#F44336", font=("Arial", 12, "bold")).grid(row=0, column=2, sticky="w")
        self.list_exclude = ctk.CTkScrollableFrame(self.content_frame, label_text="Files (0)")
        self.list_exclude.grid(row=1, column=2, sticky="nsew", padx=(5,0))

        # Preview (Far Right)
        self.preview_frame = ctk.CTkFrame(self.content_frame, width=200)
        self.preview_frame.grid(row=1, column=3, sticky="ns", padx=(10,0))
        ctk.CTkLabel(self.preview_frame, text="PREVIEW").pack(pady=5)
        self.lbl_preview = ctk.CTkLabel(self.preview_frame, text="[No Image]", width=180, height=180, fg_color="#222")
        self.lbl_preview.pack(pady=10, padx=10)

        # === Footer Actions ===
        self.footer = ctk.CTkFrame(self)
        self.footer.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        self.progress = ctk.CTkProgressBar(self.footer)
        self.progress.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        self.progress.set(0)
        
        # Move Files Button (Far Right)
        self.btn_move_files = ctk.CTkButton(self.footer, text="Move 'No People' Files", state="disabled", command=self.move_files_action)
        self.btn_move_files.pack(side="right", padx=10, pady=5)

        # Cancel Button (Next to Move Files)
        self.btn_cancel = ctk.CTkButton(self.footer, text="Stop", width=60, fg_color="#D32F2F", hover_color="#B71C1C", state="disabled", command=self.cancel_scan)
        self.btn_cancel.pack(side="right", padx=5)
        
        self.lbl_status = ctk.CTkLabel(self.footer, text="Ready", text_color="gray")
        # Pack this BEFORE the progress bar so it's on left? 
        # Actually standard pack is tricky with fill. 
        # Layout: [Status] [Progress ----------] [Stop] [Move]
        # Current Pack Order:
        # progress.pack(side="left", fill="x", expand=True) (Takes remaining space)
        # To make status be strictly left, pack it FIRST side=left.
        # To make buttons right, pack them FIRST side=right.
        
        # Let's repack footer.
        for widget in self.footer.winfo_children(): widget.pack_forget()

        # 1. Right side buttons
        self.btn_move_files.pack(side="right", padx=10, pady=5)
        self.btn_cancel.pack(side="right", padx=5)

        # 2. Left Label
        self.lbl_status.pack(side="left", padx=10)
        
        # 3. Fill Progress
        self.progress.pack(side="left", fill="x", expand=True, padx=10)

    def browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, path)

    def cancel_scan(self):
        self.scanner.cancel()
        self.btn_cancel.configure(state="disabled")
        self.lbl_status.configure(text="Stopping...")

    def start_scan(self):
        try:
            # Debug connection
            self.file_logger.info("SCAN: Start Button Clicked")
            
            path = self.entry_path.get()
            self.file_logger.info(f"SCAN: Selected Path: '{path}'")
            
            if not path:
                self.file_logger.error("SCAN: Path is empty")
                messagebox.showerror("Error", "Folder path is empty.\nPlease select a folder.")
                return
                
            if not os.path.exists(path):
                self.file_logger.error(f"SCAN: Path does not exist: {path}")
                messagebox.showerror("Error", f"Path does not exist:\n{path}")
                return
                
            if not os.path.isdir(path):
                self.file_logger.error(f"SCAN: Path is not a directory: {path}")
                messagebox.showerror("Error", f"Path is not a directory:\n{path}")
                return

            use_gpu = (self.var_hw.get() == "GPU")
            keep_animals = bool(self.chk_keep_animals.get())
            self.file_logger.info(f"SCAN: Config - GPU: {use_gpu}, Keep Animals: {keep_animals}")

            self.file_logger.debug("SCAN: Updating UI State - Buttons")
            self.btn_scan.configure(state="disabled")
            self.btn_cancel.configure(state="normal")
            self.btn_move_files.configure(state="disabled")
            
            self.file_logger.debug("SCAN: Clearing internal lists")
            self.keep_files.clear()
            self.exclude_files.clear()
            
            self.file_logger.debug("SCAN: Refreshing Lists UI")
            self.refresh_lists()
            
            self.file_logger.debug("SCAN: Updating Status Label")
            self.lbl_status.configure(text=f"Initializing Scan ({'GPU' if use_gpu else 'CPU'})...")
            
            self.file_logger.debug("SCAN: Setting Callbacks")
            self.scanner.progress_callback = self.on_progress
            
            def run():
                try:
                    self.file_logger.info("SCAN: Thread Started EXECUTION")
                    self.scanner.run_scan(path, use_gpu=use_gpu, keep_animals=keep_animals)
                    self.file_logger.info("SCAN: Thread Finished Normally")
                    # Finish call must happen on main thread to be safe with Tk
                    self.after(0, self.on_finished)
                except Exception as e:
                    self.file_logger.exception("SCAN: Thread Crashed")
                    self.after(0, lambda: messagebox.showerror("Error during scan", str(e)))
                    self.after(0, self.on_finished)

            self.file_logger.info("SCAN: Dispatching Thread...")
            threading.Thread(target=run, daemon=True).start()
            self.file_logger.info("SCAN: Thread Dispatched Successfully")

        except Exception as e:
            self.file_logger.exception("SCAN: Main Thread Error in start_scan")
            messagebox.showerror("System Error", f"Failed to start scan:\n{e}")
    
    def on_finished(self):
        self.keep_files = list(self.scanner.no_people_files)
        self.exclude_files = list(self.scanner.excluded_files)
        self.refresh_lists()
        self.btn_scan.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        if self.keep_files:
            self.btn_move_files.configure(state="normal")
        self.lbl_status.configure(text="Scan Complete.")
        self.progress.set(1.0)

    def on_progress(self, current, total, eta):
        # We invoke 'after' to update UI safely
        self.after(0, lambda: self.update_progress_ui(current, total, eta))

    def update_progress_ui(self, current, total, eta):
        val = current / max(total, 1)
        self.progress.set(val)
        self.lbl_status.configure(text=f"Scanning... {current}/{total} (ETA: {int(eta)}s)")

    def refresh_lists(self):
        for widget in self.list_keep.winfo_children(): widget.destroy()
        for widget in self.list_exclude.winfo_children(): widget.destroy()

        def add_item(parent, files, list_name):
            for i, f in enumerate(files):
                if i > 500: # Limit UI listing for performance
                    ctk.CTkLabel(parent, text=f"...and {len(files)-500} more").pack()
                    break
                    
                name = os.path.basename(f)
                btn = ctk.CTkButton(parent, text=name, fg_color="transparent", border_width=0, anchor="w",
                                  command=lambda f=f, idx=i, ln=list_name: self.select_file(f, idx, ln))
                btn.pack(fill="x", pady=1)

        add_item(self.list_keep, self.keep_files, "keep")
        add_item(self.list_exclude, self.exclude_files, "exclude")
        
        self.list_keep.configure(label_text=f"Files ({len(self.keep_files)})")
        self.list_exclude.configure(label_text=f"Files ({len(self.exclude_files)})")

    def select_file(self, f, idx, list_name):
        self.selected_item = (list_name, idx, f)
        # Show preview
        try:
            img = Image.open(f)
            img.thumbnail((180, 180))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.lbl_preview.configure(image=ctk_img, text="")
        except:
            self.lbl_preview.configure(image=None, text="[Error]")

    def move_item(self, direction):
        if not self.selected_item: return
        lname, idx, f = self.selected_item
        
        if direction == "right" and lname == "keep":
            if f in self.keep_files:
                self.keep_files.remove(f)
                self.exclude_files.append(f)
                self.refresh_lists()
        elif direction == "left" and lname == "exclude":
            if f in self.exclude_files:
                self.exclude_files.remove(f)
                self.keep_files.append(f)
                self.refresh_lists()
        
        self.selected_item = None

    def move_files_action(self):
        dest_dir = os.path.join(self.entry_path.get(), "No_People")
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        count = 0
        for f in self.keep_files:
            try:
                fname = os.path.basename(f)
                shutil.move(f, os.path.join(dest_dir, fname))
                count += 1
            except: pass
            
        messagebox.showinfo("Success", f"Moved {count} files to {dest_dir}")
        self.keep_files.clear()
        self.refresh_lists()
        self.btn_move_files.configure(state="disabled")

class DonateTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Center Content
        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(self.frame, text="☕", font=("Arial", 60)).pack(pady=10)
        ctk.CTkLabel(self.frame, text="Enjoying the App?", font=("Arial", 24, "bold")).pack(pady=5)
        
        ctk.CTkLabel(self.frame, text="Media Archive Organizer is completely free.\nIf this tool saved you time, consider buying me a coffee!", 
                     font=("Arial", 14), text_color="gray").pack(pady=20)
        
        # Buttons
        self.btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.btn_frame.pack(pady=20)
        
        # Custom Links for jscheema@gmail.com
        
        # PayPal: Generic Send
        # Using a standard generic link format since user didn't provide a specific paypal.me
        link_paypal = "https://www.paypal.com/cgi-bin/webscr?business=jscheema@gmail.com&cmd=_xclick&currency_code=USD&item_name=Donation"
        
        # Venmo: Deep link or web
        link_venmo = "https://venmo.com/?txn=pay&recipients=jscheema@gmail.com&note=MediaArchiveOrganizer"
        

        
        ctk.CTkButton(self.btn_frame, text="PayPal", width=120, height=40, fg_color="#0070BA", 
                      command=lambda: webbrowser.open(link_paypal)).grid(row=0, column=0, padx=10)
                      
        ctk.CTkButton(self.btn_frame, text="Venmo", width=120, height=40, fg_color="#008CFF", 
                      command=lambda: webbrowser.open(link_venmo)).grid(row=0, column=1, padx=10)
                      
        ctk.CTkLabel(self.frame, text="Thank you for your support!", font=("Arial", 12, "italic"), text_color="#E04F5F").pack(pady=20)

