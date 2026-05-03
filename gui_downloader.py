import customtkinter as ctk
import tkinter as tk
import subprocess
import threading
import sys
import os
import time
import webbrowser
import re
import psutil
import math

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

# yt-dlp uses --continue by default, so partial .part files are auto-resumed.
# We add --retries and --fragment-retries for network resilience.
DOWNLOADERS = [
    {
        "name": "yt-dlp",
        "command": [sys.executable, "-m", "yt_dlp", "--no-warnings",
                    "--retries", "10", "--fragment-retries", "10",
                    "-o", "%(title)s_{timestamp}.%(ext)s", "{url}"],
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
        self.geometry("850x700")
        self.minsize(800, 600)

        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.current_process = None   # The running subprocess
        self.is_paused = False        # Pause state flag
        self.is_stopped = False       # Stop state flag
        self._gradient_offset = 0     # For animation

        # ── Animated gradient background ────────────────────────
        self.bg_canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._draw_gradient()
        self.bg_canvas.bind("<Configure>", lambda e: self._draw_gradient())
        self._animate_gradient()

        # ── Main content frame (sits on top of gradient) ────────
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(4, weight=1)

        # Header Frame
        self.header_frame = ctk.CTkFrame(self.content, fg_color=("#EDF2F4", "#2B2D42"), corner_radius=15)
        self.header_frame.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(self.header_frame, text="⚡ Universal Video Downloader", font=ctk.CTkFont(size=28, weight="bold"), text_color=("#2B2D42", "#EDF2F4"))
        self.header_label.grid(row=0, column=0, sticky="w", padx=20, pady=15)

        self.help_btn = ctk.CTkButton(self.header_frame, text="?", width=40, height=40, corner_radius=20, font=ctk.CTkFont(size=20, weight="bold"), fg_color="#EF233C", hover_color="#D90429", command=self.show_help)
        self.help_btn.grid(row=0, column=1, sticky="e", padx=20, pady=15)

        # Input Frame (glass panel)
        self.input_frame = ctk.CTkFrame(self.content, fg_color=("#EDF2F4", "#2B2D42"), corner_radius=15, border_width=1, border_color=("#8D99AE", "#3d3f5c"))
        self.input_frame.grid(row=1, column=0, padx=25, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Paste your video link here (e.g. YouTube, Twitter, Vimeo...)", height=48, corner_radius=12, border_color=("#8D99AE", "#3d3f5c"), font=ctk.CTkFont(size=14))
        self.url_entry.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="ew")

        self.download_btn = ctk.CTkButton(self.input_frame, text="⬇ Download", height=48, corner_radius=12, command=self.start_download, fg_color="#EF233C", hover_color="#D90429", font=ctk.CTkFont(size=14, weight="bold"))
        self.download_btn.grid(row=0, column=1, padx=(0, 5), pady=15)

        self.pause_btn = ctk.CTkButton(self.input_frame, text="⏸ Pause", height=48, width=105, corner_radius=12, command=self.toggle_pause, fg_color="#f59e0b", hover_color="#d97706", text_color="#1a1a2e", font=ctk.CTkFont(size=14, weight="bold"), state="disabled")
        self.pause_btn.grid(row=0, column=2, padx=(0, 5), pady=15)

        self.stop_btn = ctk.CTkButton(self.input_frame, text="⏹ Stop", height=48, width=105, corner_radius=12, command=self.stop_download, fg_color="#D90429", hover_color="#a80320", font=ctk.CTkFont(size=13, weight="bold"), state="disabled")
        self.stop_btn.grid(row=0, column=3, padx=(0, 15), pady=15)

        # Options Row (Quality + Subtitles + Batch toggle)
        self.options_frame = ctk.CTkFrame(self.content, fg_color=("#EDF2F4", "#2B2D42"), corner_radius=15, border_width=1, border_color=("#8D99AE", "#3d3f5c"))
        self.options_frame.grid(row=2, column=0, padx=25, pady=(0, 10), sticky="ew")
        self.options_frame.grid_columnconfigure(4, weight=1)

        q_label = ctk.CTkLabel(self.options_frame, text="Quality:", font=ctk.CTkFont(size=13, weight="bold"), text_color=("#2B2D42", "#EDF2F4"))
        q_label.grid(row=0, column=0, padx=(15, 5), pady=12)

        self.quality_var = ctk.StringVar(value="Best")
        self.quality_menu = ctk.CTkComboBox(self.options_frame, variable=self.quality_var, values=["Best", "1080p", "720p", "480p", "Audio Only"], width=130, height=36, corner_radius=10, fg_color="#1a1b2e", button_color="#EF233C", button_hover_color="#D90429", border_color="#3d3f5c", dropdown_fg_color="#1a1b2e", dropdown_hover_color="#EF233C", font=ctk.CTkFont(size=13), state="readonly")
        self.quality_menu.grid(row=0, column=1, padx=(0, 20), pady=12)

        s_label = ctk.CTkLabel(self.options_frame, text="Subtitles:", font=ctk.CTkFont(size=13, weight="bold"), text_color=("#2B2D42", "#EDF2F4"))
        s_label.grid(row=0, column=2, padx=(0, 5), pady=12)

        self.subs_var = ctk.StringVar(value="No Subtitles")
        self.subs_menu = ctk.CTkComboBox(self.options_frame, variable=self.subs_var, values=["No Subtitles", "English", "Hindi", "English + Hindi"], width=145, height=36, corner_radius=10, fg_color="#1a1b2e", button_color="#EF233C", button_hover_color="#D90429", border_color="#3d3f5c", dropdown_fg_color="#1a1b2e", dropdown_hover_color="#EF233C", font=ctk.CTkFont(size=13), state="readonly")
        self.subs_menu.grid(row=0, column=3, padx=(0, 10), pady=12)

        self.batch_var = ctk.BooleanVar(value=False)
        self.batch_check = ctk.CTkCheckBox(self.options_frame, text="Batch Mode", variable=self.batch_var, font=ctk.CTkFont(size=13, weight="bold"), text_color=("#2B2D42", "#EDF2F4"), fg_color="#EF233C", hover_color="#D90429", corner_radius=6, command=self._toggle_batch)
        self.batch_check.grid(row=0, column=4, padx=(0, 15), pady=12, sticky="w")

        # Batch URL text area (hidden by default)
        self.batch_frame = ctk.CTkFrame(self.content, fg_color=("#EDF2F4", "#2B2D42"), corner_radius=15, border_width=1, border_color=("#8D99AE", "#3d3f5c"))
        self.batch_textbox = ctk.CTkTextbox(self.batch_frame, height=100, corner_radius=10, font=ctk.CTkFont(family="Consolas", size=13), fg_color="#0f1120", text_color="#22c55e")
        self.batch_textbox.pack(fill="both", expand=True, padx=15, pady=15)
        self.batch_textbox.insert("1.0", "# Paste one URL per line\n")
        # batch_frame is hidden by default, shown when Batch Mode is toggled

        # Progress Section (glass panel)
        self.progress_frame = ctk.CTkFrame(self.content, fg_color=("#EDF2F4", "#2B2D42"), corner_radius=15, border_width=1, border_color=("#8D99AE", "#3d3f5c"))
        self.progress_frame.grid(row=4, column=0, padx=25, pady=(0, 10), sticky="nsew")
        
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_columnconfigure(1, weight=1)
        self.progress_frame.grid_columnconfigure(2, weight=1)
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="Ready to download", font=ctk.CTkFont(size=18, weight="bold"), text_color=("#2B2D42", "#EDF2F4"))
        self.status_label.grid(row=0, column=0, columnspan=3, pady=(30, 10))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=22, corner_radius=11, progress_color="#22c55e", fg_color=("#c8cdd4", "#1a1b2e"))
        self.progress_bar.grid(row=1, column=0, columnspan=3, padx=50, pady=(10, 25), sticky="ew")
        self.progress_bar.set(0)
        
        self.pct_label = ctk.CTkLabel(self.progress_frame, text="0%", font=ctk.CTkFont(size=28, weight="bold"), text_color="#22c55e")
        self.pct_label.grid(row=2, column=0, pady=(0, 25))
        
        self.speed_label = ctk.CTkLabel(self.progress_frame, text="Speed: --", font=ctk.CTkFont(size=15), text_color=("#5a6070", "#8D99AE"))
        self.speed_label.grid(row=2, column=1, pady=(0, 25))
        
        self.eta_label = ctk.CTkLabel(self.progress_frame, text="ETA: --", font=ctk.CTkFont(size=15), text_color=("#5a6070", "#8D99AE"))
        self.eta_label.grid(row=2, column=2, pady=(0, 25))

        # Developer Details (Professional & Clickable)
        self.footer_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.footer_frame.grid(row=5, column=0, pady=(0, 15))
        
        dev_label = ctk.CTkLabel(self.footer_frame, text="Developed by Devanshu  ·  ", font=ctk.CTkFont(size=13), text_color=("#5a6070", "#8D99AE"))
        dev_label.pack(side="left")
        
        ig_link = ctk.CTkLabel(self.footer_frame, text="Instagram", font=ctk.CTkFont(size=13, underline=True), text_color=("#D90429", "#EF233C"), cursor="hand2")
        ig_link.pack(side="left", padx=(0, 8))
        ig_link.bind("<Button-1>", lambda e: webbrowser.open("https://instagram.com/_devanshugautam"))
        
        sep = ctk.CTkLabel(self.footer_frame, text="·", font=ctk.CTkFont(size=13), text_color=("#5a6070", "#8D99AE"))
        sep.pack(side="left", padx=(0, 8))

        github_link = ctk.CTkLabel(self.footer_frame, text="GitHub", font=ctk.CTkFont(size=13, underline=True), text_color=("#D90429", "#EF233C"), cursor="hand2")
        github_link.pack(side="left")
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Devanshu138"))

    # ── Gradient background ─────────────────────────────────────

    def _lerp_color(self, c1, c2, t):
        """Linearly interpolate between two (r,g,b) tuples."""
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    def _draw_gradient(self):
        """Draw a smooth vertical gradient on the background canvas."""
        self.bg_canvas.delete("gradient")
        w = self.winfo_width() or 800
        h = self.winfo_height() or 600

        o = self._gradient_offset
        # Coolors: dark navy → steel blue → deep charcoal (shifts with offset)
        top    = self._lerp_color((30, 32, 50),  (50, 55, 75),  (0.5 + 0.5 * math.sin(o)))
        mid    = self._lerp_color((43, 45, 66),  (65, 70, 95),  (0.5 + 0.5 * math.sin(o + 1.5)))
        bottom = self._lerp_color((20, 22, 38),  (35, 38, 55),  (0.5 + 0.5 * math.sin(o + 3.0)))

        steps = 80  # number of bands
        half = steps // 2
        for i in range(steps):
            if i < half:
                t = i / half
                r, g, b = self._lerp_color(top, mid, t)
            else:
                t = (i - half) / half
                r, g, b = self._lerp_color(mid, bottom, t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(h * i / steps)
            y1 = int(h * (i + 1) / steps) + 1
            self.bg_canvas.create_rectangle(0, y0, w, y1, fill=color, outline=color, tags="gradient")

    def _animate_gradient(self):
        """Slowly shift the gradient colors over time."""
        self._gradient_offset += 0.02
        self._draw_gradient()
        self.after(100, self._animate_gradient)  # ~10 FPS, very light

    def _toggle_batch(self):
        """Show/hide batch URL text area."""
        if self.batch_var.get():
            self.batch_frame.grid(row=3, column=0, padx=25, pady=(0, 10), sticky="ew")
            self.url_entry.configure(placeholder_text="Batch Mode: use the box below ↓")
            self.url_entry.configure(state="disabled")
        else:
            self.batch_frame.grid_forget()
            self.url_entry.configure(state="normal")
            self.url_entry.configure(placeholder_text="Paste your video link here (e.g. YouTube, Twitter, Vimeo...)")

    def update_status(self, text, color="#f8fafc"):
        self.status_label.configure(text=text, text_color=color)

    def reset_progress(self):
        self.progress_bar.set(0)
        self.pct_label.configure(text="0%")
        self.speed_label.configure(text="Speed: --")
        self.eta_label.configure(text="ETA: --")

    def set_controls_downloading(self):
        """Switch buttons to the 'downloading' state."""
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.url_entry.configure(state="disabled")
        self.pause_btn.configure(state="normal", text="⏸ Pause")
        self.stop_btn.configure(state="normal")
        self.quality_menu.configure(state="disabled")
        self.subs_menu.configure(state="disabled")
        self.batch_check.configure(state="disabled")

    def set_controls_idle(self):
        """Switch buttons back to the 'idle' state."""
        self.download_btn.configure(state="normal", text="⬇ Download")
        if not self.batch_var.get():
            self.url_entry.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸ Pause")
        self.stop_btn.configure(state="disabled")
        self.quality_menu.configure(state="readonly")
        self.subs_menu.configure(state="readonly")
        self.batch_check.configure(state="normal")
        self.is_paused = False
        self.is_stopped = False
        self.current_process = None

    def _get_quality_args(self):
        """Build yt-dlp format arguments based on quality selection."""
        q = self.quality_var.get()
        if q == "1080p":
            return ["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]"]
        elif q == "720p":
            return ["-f", "bestvideo[height<=720]+bestaudio/best[height<=720]"]
        elif q == "480p":
            return ["-f", "bestvideo[height<=480]+bestaudio/best[height<=480]"]
        elif q == "Audio Only":
            return ["-x", "--audio-format", "mp3"]
        return []  # "Best" = default

    def _get_subtitle_args(self):
        """Build yt-dlp subtitle arguments based on dropdown selection."""
        s = self.subs_var.get()
        if s == "English":
            return ["--write-auto-subs", "--sub-langs", "en", "--embed-subs", "--ignore-errors"]
        elif s == "Hindi":
            return ["--write-auto-subs", "--sub-langs", "hi", "--embed-subs", "--ignore-errors"]
        elif s == "English + Hindi":
            return ["--write-auto-subs", "--sub-langs", "en,hi", "--embed-subs", "--ignore-errors"]
        return []  # "No Subtitles"

    # ── Progress parser ─────────────────────────────────────────

    def parse_and_update(self, line):
        line = line.strip()
        if not line:
            return

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
        elif "Written" in line and "MB/s" in line:  # streamlink
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

    # ── Help window ─────────────────────────────────────────────

    def _copy_to_clipboard(self, text, btn):
        """Copy text to clipboard and show feedback on the button."""
        self.clipboard_clear()
        self.clipboard_append(text)
        original_text = btn.cget("text")
        btn.configure(text="✅ Copied!", fg_color="#22c55e")
        btn.after(1500, lambda: btn.configure(text=original_text, fg_color="#EF233C"))

    def show_help(self):
        help_window = ctk.CTkToplevel(self)
        help_window.title("Help & Advanced Instructions")
        
        # Center on screen
        win_w, win_h = 700, 620
        screen_w = help_window.winfo_screenwidth()
        screen_h = help_window.winfo_screenheight()
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        help_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
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
        note_label = ctk.CTkLabel(note_frame, text=note_text, font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#60a5fa", wraplength=600, justify="left")
        note_label.pack(padx=20, pady=20, anchor="w")

        # --- The Main Instructions Title ---
        title_label = ctk.CTkLabel(scroll_frame, text="🛠️ How to Get Protected Video Links", font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), text_color="#f8fafc")
        title_label.pack(anchor="w", pady=(0, 20))

        # --- Helper to create a step card ---
        def make_step(parent, step_num, title, description, command=None):
            """Create a step card with optional copy button."""
            card = ctk.CTkFrame(parent, fg_color="#1a1b2e", corner_radius=10, border_width=1, border_color="#2B2D42")
            card.pack(fill="x", pady=(0, 12))
            card.grid_columnconfigure(0, weight=1)

            # Step header
            header = ctk.CTkLabel(card, text=f"Step {step_num}: {title}", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#EDF2F4")
            header.grid(row=0, column=0, sticky="w", padx=15, pady=(12, 4))

            # Description
            desc = ctk.CTkLabel(card, text=description, font=ctk.CTkFont(family="Segoe UI", size=14), text_color="#8D99AE", wraplength=500, justify="left")
            desc.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

            if command:
                # Command box + Copy button row
                cmd_frame = ctk.CTkFrame(card, fg_color="#0f1120", corner_radius=8)
                cmd_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 12))
                cmd_frame.grid_columnconfigure(0, weight=1)

                cmd_label = ctk.CTkLabel(cmd_frame, text=command, font=ctk.CTkFont(family="Consolas", size=13), text_color="#22c55e", wraplength=480, justify="left")
                cmd_label.grid(row=0, column=0, sticky="w", padx=12, pady=10)

                copy_btn = ctk.CTkButton(cmd_frame, text="📋 Copy", width=80, height=32, corner_radius=8, fg_color="#EF233C", hover_color="#D90429", font=ctk.CTkFont(size=12, weight="bold"), command=lambda c=command, b=None: None)
                copy_btn.grid(row=0, column=1, padx=(5, 10), pady=10)
                # Re-bind with actual button reference
                copy_btn.configure(command=lambda c=command, b=copy_btn: self._copy_to_clipboard(c, b))

        # --- Step Cards ---
        make_step(scroll_frame, 1,
                  "Open Developer Tools",
                  "Press F12 on your keyboard to open the browser's Developer Tools panel.")

        make_step(scroll_frame, 2,
                  "Go to the Console Tab",
                  "Click on the 'Console' tab at the top of the Developer Tools panel.")

        make_step(scroll_frame, 3,
                  "Allow Pasting",
                  "The console may block pasting. Type this command and press Enter:",
                  command="allow pasting")

        make_step(scroll_frame, 4,
                  "Extract the Video Link",
                  "Paste this command into the console and press Enter to copy the video link:",
                  command="copy(window._streams[0].file); console.log('Link copied to clipboard!');")

        make_step(scroll_frame, 5,
                  "Download!",
                  "Come back to this app, paste the link (Ctrl+V) into the input box, and click Download!")

    # ── Download controls ───────────────────────────────────────

    def start_download(self):
        # Collect URLs
        if self.batch_var.get():
            raw = self.batch_textbox.get("1.0", "end").strip()
            urls = [u.strip() for u in raw.splitlines() if u.strip() and not u.strip().startswith("#")]
            if not urls:
                self.update_status("Error: No URLs in batch list.", "#ef4444")
                return
        else:
            url = self.url_entry.get().strip()
            if not url:
                self.update_status("Error: No URL provided.", "#ef4444")
                return
            urls = [url]

        self.is_stopped = False
        self.is_paused = False
        self.set_controls_downloading()
        self.reset_progress()

        quality_args = self._get_quality_args()
        subtitle_args = self._get_subtitle_args()

        if len(urls) == 1:
            self.update_status("Initializing...", "#f8fafc")
            thread = threading.Thread(target=self.download_process, args=(urls[0], quality_args, subtitle_args), daemon=True)
            thread.start()
        else:
            self.update_status(f"Batch: 0/{len(urls)} completed", "#f8fafc")
            thread = threading.Thread(target=self._batch_download, args=(urls, quality_args, subtitle_args), daemon=True)
            thread.start()

    def _batch_download(self, urls, quality_args, subtitle_args):
        """Download multiple URLs sequentially."""
        total = len(urls)
        for i, url in enumerate(urls, 1):
            if self.is_stopped:
                break
            self.after(0, self.update_status, f"Batch [{i}/{total}]: Starting...", "#38bdf8")
            self.after(0, self.reset_progress)
            self.download_process(url, quality_args, subtitle_args, batch_label=f"[{i}/{total}]")

        if not self.is_stopped:
            self.after(0, self.update_status, f"Batch complete! {total} videos processed ✓", "#10b981")
        self.after(0, self.set_controls_idle)

    def toggle_pause(self):
        """Pause or resume the running subprocess using psutil."""
        if self.current_process is None:
            return

        try:
            parent = psutil.Process(self.current_process.pid)
            children = parent.children(recursive=True)
        except psutil.NoSuchProcess:
            return

        if not self.is_paused:
            # PAUSE – suspend parent + all children (e.g. ffmpeg)
            self.is_paused = True
            self.pause_btn.configure(text="▶ Resume")
            self.update_status("Paused", "#eab308")
            for proc in children + [parent]:
                try:
                    proc.suspend()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        else:
            # RESUME
            self.is_paused = False
            self.pause_btn.configure(text="⏸ Pause")
            self.update_status("Resuming...", "#38bdf8")
            for proc in children + [parent]:
                try:
                    proc.resume()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

    def stop_download(self):
        """Stop the running download immediately (kills entire process tree)."""
        self.is_stopped = True
        self.is_paused = False
        if self.current_process:
            try:
                parent = psutil.Process(self.current_process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        self.after(0, self.update_status, "Download stopped.", "#ef4444")
        self.after(0, self.set_controls_idle)

    # ── Download logic ──────────────────────────────────────────

    @staticmethod
    def _is_youtube(url):
        """Check if the URL belongs to YouTube."""
        yt_patterns = ["youtube.com", "youtu.be", "youtube-nocookie.com"]
        return any(p in url.lower() for p in yt_patterns)

    def download_process(self, url, quality_args=None, subtitle_args=None, batch_label=""):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        success_overall = False
        quality_args = quality_args or []
        subtitle_args = subtitle_args or []

        # Pick output folder based on URL
        if self._is_youtube(url):
            folder = os.path.join(os.getcwd(), "YouTube Videos")
        else:
            folder = os.path.join(os.getcwd(), "Others")
        os.makedirs(folder, exist_ok=True)
        
        for downloader in DOWNLOADERS:
            if self.is_stopped:
                break

            label = f"{batch_label} " if batch_label else ""
            self.after(0, self.update_status, f"{label}Trying {downloader['name']}...", "#f8fafc")
            
            try:
                subprocess.run(downloader["check"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

            cmd = [arg.replace("{url}", url).replace("{timestamp}", timestamp) for arg in downloader["command"]]

            # Inject quality and subtitle args for yt-dlp
            if downloader["name"] == "yt-dlp":
                insert_pos = cmd.index("--no-warnings") + 1
                for arg in reversed(quality_args + subtitle_args):
                    cmd.insert(insert_pos, arg)

            # Replace the output filename with the correct folder path
            for i, arg in enumerate(cmd):
                if "%(title)s_" in arg:
                    cmd[i] = os.path.join(folder, arg)
                elif arg.startswith("video_"):
                    cmd[i] = os.path.join(folder, arg)
            
            try:
                creationflags = 0
                if sys.platform == "win32":
                    creationflags = subprocess.CREATE_NO_WINDOW
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, creationflags=creationflags)
                self.current_process = process
                
                for line in process.stdout:
                    if self.is_stopped:
                        process.terminate()
                        break
                    self.after(0, self.parse_and_update, line)
                
                process.wait()

                if self.is_stopped:
                    break

                if process.returncode == 0:
                    folder_name = "YouTube Videos" if self._is_youtube(url) else "Others"
                    self.after(0, self.update_status, f"{label}Saved to '{folder_name}' ✓", "#10b981")
                    self.after(0, lambda: self.progress_bar.set(1.0))
                    self.after(0, lambda: self.pct_label.configure(text="100%"))
                    self.after(0, lambda: self.speed_label.configure(text="Speed: Done"))
                    self.after(0, lambda: self.eta_label.configure(text="ETA: 00:00"))
                    success_overall = True
                    break
            except Exception as e:
                print(f"Error: {e}")

        if not success_overall and not self.is_stopped:
            self.after(0, self.update_status, f"{batch_label} Failed. Check URL.", "#ef4444")

        # Only reset controls if NOT in batch mode (batch handles it)
        if not batch_label:
            self.after(0, self.set_controls_idle)

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
