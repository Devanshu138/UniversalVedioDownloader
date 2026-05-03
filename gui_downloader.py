import customtkinter as ctk
import subprocess
import threading
import sys
import os
import time
import webbrowser

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

        # Terminal Output
        self.terminal_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=13), text_color="#a7f3d0", fg_color="#020617")
        self.terminal_textbox.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="nsew")
        self.terminal_textbox.configure(state="disabled")

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

    def log(self, text):
        self.terminal_textbox.configure(state="normal")
        self.terminal_textbox.insert("end", text + "\n")
        self.terminal_textbox.see("end")
        self.terminal_textbox.configure(state="disabled")

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
            self.log("[-] Error: No URL provided.")
            return

        self.download_btn.configure(state="disabled", text="Downloading...")
        self.url_entry.configure(state="disabled")
        
        self.terminal_textbox.configure(state="normal")
        self.terminal_textbox.delete("0.0", "end")
        self.terminal_textbox.configure(state="disabled")

        # Run in a background thread to prevent freezing the GUI
        thread = threading.Thread(target=self.download_process, args=(url,), daemon=True)
        thread.start()

    def download_process(self, url):
        self.log(f"[*] Starting universal video downloader for: {url}\n")
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        success_overall = False
        
        for downloader in DOWNLOADERS:
            self.log("==============================================")
            self.log(f"[*] Attempting download with {downloader['name']}...")
            self.log("==============================================\n")
            
            try:
                subprocess.run(downloader["check"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.log(f"[-] {downloader['name']} is not installed. Skipping.\n")
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
                    self.after(0, self.log, line.strip())
                
                process.wait()
                if process.returncode == 0:
                    self.log(f"\n[+] Success! {downloader['name']} successfully downloaded the video.")
                    self.log("[*] Download complete! Exiting script.\n")
                    success_overall = True
                    break
                else:
                    self.log(f"\n[-] {downloader['name']} could not download the video.\n")
            except Exception as e:
                self.log(f"\n[-] Error running {downloader['name']}: {e}\n")
                
        if not success_overall:
            self.log("[-] All download attempts failed.")
            self.log("[*] Make sure the URL is accessible.")

        # Re-enable UI
        self.after(0, self.reset_ui)

    def reset_ui(self):
        self.download_btn.configure(state="normal", text="Download")
        self.url_entry.configure(state="normal")

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
