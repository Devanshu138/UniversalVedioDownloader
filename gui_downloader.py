import customtkinter as ctk
import subprocess
import threading
import sys
import os
import time
import webbrowser
import re

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

DOWNLOADERS = [
    {
        "name": "yt-dlp",
        "command": [sys.executable, "-m", "yt_dlp", "--no-warnings", "-o", "%(title)s_{timestamp}.%(ext)s", "{url}"],
        "check": [sys.executable, "-m", "yt_dlp", "--version"]
    },
    {
        "name": "you-get",
        "command": [sys.executable, "-m", "you_get", "-O", "video_{timestamp}", "{url}"],
        "check": [sys.executable, "-m", "you_get", "--version"]
    },
    {
        "name": "streamlink",
        "command": [sys.executable, "-m", "streamlink", "{url}", "best", "-o", "video_{timestamp}.mp4"],
        "check": [sys.executable, "-m", "streamlink", "--version"]
    }
]

class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Universal Video Downloader")
        self.geometry("750x550")

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(self.header_frame, text="Universal Video Downloader", font=ctk.CTkFont(size=26, weight="bold"))
        self.header_label.grid(row=0, column=0, sticky="w")

        self.help_btn = ctk.CTkButton(self.header_frame, text="?", width=40, height=40, corner_radius=20, font=ctk.CTkFont(size=20, weight="bold"), command=self.show_help)
        self.help_btn.grid(row=0, column=1, sticky="e")

        # Input Frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Paste your video link here (e.g. YouTube, Twitter, Vimeo...)", height=45)
        self.url_entry.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="ew")

        self.download_btn = ctk.CTkButton(self.input_frame, text="Download", height=45, command=self.start_download)
        self.download_btn.grid(row=0, column=1, padx=(0, 15), pady=15)

        # Progress Section
        self.progress_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=15)
        self.progress_frame.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="nsew")
        
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_columnconfigure(1, weight=1)
        self.progress_frame.grid_columnconfigure(2, weight=1)
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="Ready to download", font=ctk.CTkFont(size=16, weight="bold"))
        self.status_label.grid(row=0, column=0, columnspan=3, pady=(20, 10))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=20, corner_radius=10)
        self.progress_bar.grid(row=1, column=0, columnspan=3, padx=40, pady=(10, 20), sticky="ew")
        self.progress_bar.set(0)
        
        self.pct_label = ctk.CTkLabel(self.progress_frame, text="0%", font=ctk.CTkFont(size=24, weight="bold"), text_color="#3b82f6")
        self.pct_label.grid(row=2, column=0, pady=(0, 20))
        
        self.speed_label = ctk.CTkLabel(self.progress_frame, text="Speed: --", font=ctk.CTkFont(size=15), text_color="#94a3b8")
        self.speed_label.grid(row=2, column=1, pady=(0, 20))
        
        self.eta_label = ctk.CTkLabel(self.progress_frame, text="ETA: --", font=ctk.CTkFont(size=15), text_color="#94a3b8")
        self.eta_label.grid(row=2, column=2, pady=(0, 20))

        # Developer Details (Professional & Clickable)
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=3, column=0, pady=(0, 15))
        
        dev_label = ctk.CTkLabel(self.footer_frame, text="Developed by Devanshu | ", font=ctk.CTkFont(size=13), text_color="#94a3b8")
        dev_label.pack(side="left")
        
        ig_link = ctk.CTkLabel(self.footer_frame, text="Instagram", font=ctk.CTkFont(size=13, underline=True), text_color="#38bdf8", cursor="hand2")
        ig_link.pack(side="left", padx=(0, 5))
        ig_link.bind("<Button-1>", lambda e: webbrowser.open("https://instagram.com/_devanshugautam"))
        
        github_link = ctk.CTkLabel(self.footer_frame, text="GitHub", font=ctk.CTkFont(size=13, underline=True), text_color="#38bdf8", cursor="hand2")
        github_link.pack(side="left")
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Devanshu138"))

    def update_status(self, text, color="#f8fafc"):
        self.status_label.configure(text=text, text_color=color)

    def reset_progress(self):
        self.progress_bar.set(0)
        self.pct_label.configure(text="0%")
        self.speed_label.configure(text="Speed: --")
        self.eta_label.configure(text="ETA: --")

    def parse_and_update(self, line):
        line = line.strip()
        if not line: return

        print(line)  # Keep in console for debugging

        if "[download]" in line and "%" in line and "ETA" in line:
            self.update_status("Downloading...", "#38bdf8")
            try:
                pct_match = re.search(r"([\d\.]+)%", line)
                if pct_match:
                    pct = float(pct_match.group(1))
                    self.progress_bar.set(pct / 100.0)
                    self.pct_label.configure(text=f"{pct}%")
                
                speed_match = re.search(r"at\s+([^\s]+)", line)
                if speed_match:
                    self.speed_label.configure(text=f"Speed: {speed_match.group(1)}")
                    
                eta_match = re.search(r"ETA\s+([\d:]+)", line)
                if eta_match:
                    self.eta_label.configure(text=f"ETA: {eta_match.group(1)}")
            except Exception:
                pass
        elif "Written" in line and "MB/s" in line: # streamlink
            self.update_status("Downloading Stream...", "#38bdf8")
            try:
                speed_match = re.search(r"@\s+([^\s]+\s+MB/s)", line)
                if speed_match:
                    self.speed_label.configure(text=f"Speed: {speed_match.group(1)}")
                current_val = self.progress_bar.get()
                self.progress_bar.set((current_val + 0.05) % 1.0)
                self.pct_label.configure(text="--%")
            except Exception:
                pass
        elif "Destination:" in line:
            self.update_status("Starting download...", "#f8fafc")
        elif "Merging formats into" in line or "Extracting" in line:
            self.update_status("Processing video (Merging/Extracting)...", "#eab308")
        elif "has already been downloaded" in line:
            self.progress_bar.set(1.0)
            self.pct_label.configure(text="100%")
            self.update_status("Already downloaded!", "#10b981")
        elif "[error]" in line.lower() or "error:" in line.lower():
            self.update_status("Error encountered. Retrying...", "#ef4444")

    def show_help(self):
        help_window = ctk.CTkToplevel(self)
        help_window.title("Help & Advanced Instructions")
        help_window.geometry("650x550")
        help_window.grab_set()  # Focus on this window
        
        # Bring window to front
        help_window.attributes("-topmost", True)
        help_window.after(100, lambda: help_window.attributes("-topmost", False))
        
        # Use a scrollable frame for better layout flexibility
        scroll_frame = ctk.CTkScrollableFrame(help_window, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- The Highlighted Note Box ---
        note_frame = ctk.CTkFrame(scroll_frame, fg_color="#1e293b", border_width=2, border_color="#3b82f6", corner_radius=10)
        note_frame.pack(fill="x", pady=(0, 25))
        
        note_text = "⭐ NOTE: For YouTube and most standard sites, you just need to copy the video link directly. You DON'T need to use Developer Mode!"
        note_label = ctk.CTkLabel(note_frame, text=note_text, font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#60a5fa", wraplength=550, justify="left")
        note_label.pack(padx=20, pady=20, anchor="w")

        # --- The Main Instructions ---
        title_label = ctk.CTkLabel(scroll_frame, text="🛠️ How to Get Protected Video Links", font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), text_color="#f8fafc")
        title_label.pack(anchor="w", pady=(0, 15))
        
        instructions = (
            "Step 1: Press F12 to open Developer Mode.\n\n"
            "Step 2: Go to the 'Console' tab.\n\n"
            "Step 3: Type 'allow pasting' and hit Enter (if prompted).\n\n"
            "Step 4: Paste this command and hit Enter:\n"
            "    copy(window._streams[0].file); console.log('Link copied to clipboard!');\n\n"
            "Step 5: Come back here, paste the link, and click Download!"
        )
        
        inst_label = ctk.CTkLabel(scroll_frame, text=instructions, font=ctk.CTkFont(family="Segoe UI", size=16), text_color="#cbd5e1", wraplength=550, justify="left")
        inst_label.pack(anchor="w")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.update_status("Error: No URL provided.", "#ef4444")
            return

        self.download_btn.configure(state="disabled", text="Downloading...")
        self.url_entry.configure(state="disabled")
        
        self.reset_progress()
        self.update_status("Initializing...", "#f8fafc")

        # Run in a background thread to prevent freezing the GUI
        thread = threading.Thread(target=self.download_process, args=(url,), daemon=True)
        thread.start()

    def download_process(self, url):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        success_overall = False
        
        for downloader in DOWNLOADERS:
            self.after(0, self.update_status, f"Attempting download with {downloader['name']}...", "#f8fafc")
            
            try:
                subprocess.run(downloader["check"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

            cmd = [arg.replace("{url}", url).replace("{timestamp}", timestamp) for arg in downloader["command"]]
            
            try:
                # hide console window on windows
                creationflags = 0
                if sys.platform == "win32":
                    creationflags = subprocess.CREATE_NO_WINDOW
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, creationflags=creationflags)
                
                for line in process.stdout:
                    # Update GUI safely from thread
                    self.after(0, self.parse_and_update, line)
                
                process.wait()
                if process.returncode == 0:
                    self.after(0, self.update_status, f"Success! Video downloaded with {downloader['name']}.", "#10b981")
                    self.after(0, lambda: self.progress_bar.set(1.0))
                    self.after(0, lambda: self.pct_label.configure(text="100%"))
                    success_overall = True
                    break
            except Exception as e:
                print(f"Error: {e}")
                
        if not success_overall:
            self.after(0, self.update_status, "All download attempts failed. Check URL.", "#ef4444")

        # Re-enable UI
        self.after(0, self.reset_ui)

    def reset_ui(self):
        self.download_btn.configure(state="normal", text="Download")
        self.url_entry.configure(state="normal")

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
