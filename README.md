# ⚡ Universal Video Downloader v1.3.8

A professional desktop application that downloads videos from **any platform** using multiple fallback engines (`yt-dlp`, `you-get`, `streamlink`). Built with a sleek, modern dark-mode GUI.

![Version](https://img.shields.io/badge/version-1.3.8-EF233C?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Windows-2B2D42?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-8D99AE?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge)

---

## 📥 Download

> **[⬇ Download Universal Video Downloader v1.3.8 (.exe)](https://github.com/Devanshu138/UniversalVedioDownloader/releases/tag/v1.3.8)**
>
> No installation required — just download and run!

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎬 **Multi-Engine** | Automatically falls back between `yt-dlp`, `you-get`, and `streamlink` |
| 🎨 **Modern GUI** | Premium dark-mode interface built with `customtkinter` |
| 📊 **Live Progress** | Real-time progress bar, speed, and ETA display |
| 🎥 **Quality Selector** | Choose from Best, 1080p, 720p, 480p, or Audio Only |
| 📝 **Subtitle Support** | Download English, Hindi, or both subtitles (if available) |
| 📦 **Batch Mode** | Download multiple videos at once — paste one URL per line |
| 🎵 **Playlist Support** | Paste a YouTube playlist URL and download all videos |
| ⏸ **Pause / Resume** | Pause and resume downloads with one click |
| 📋 **Help Guide** | Step-by-step instructions with one-click copy buttons |
| 🔄 **Auto-Resume** | Automatically resumes interrupted downloads |

---

## 🖥️ Supported Platforms

YouTube · Instagram · Twitter/X · Facebook · Vimeo · Reddit · TikTok · Dailymotion · Twitch · and **1000+ more** sites supported by yt-dlp.

---

## 🚀 Quick Start

### Option 1: Download the EXE (Recommended)
1. Go to [**Releases**](https://github.com/Devanshu138/UniversalVedioDownloader/releases/tag/v1.3.8)
2. Download `UniversalVideoDownloader.exe`
3. Run it — no installation needed!

### Option 2: Run from Source
```bash
# Clone the repo
git clone https://github.com/Devanshu138/UniversalVedioDownloader.git
cd UniversalVedioDownloader

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python gui_downloader.py
```

---

## 🛠 Build from Source

To create a standalone `.exe` and Windows installer:

```bash
python build_exe.py
```

**Requirements:**
- [PyInstaller](https://pyinstaller.org/) — `pip install pyinstaller`
- [Inno Setup](https://jrsoftware.org/isdl.php) — for creating the Windows installer

---

## 👨‍💻 Developer

Developed with ❤️ by **Devanshu**

- **GitHub**: [@Devanshu138](https://github.com/Devanshu138)
- **Instagram**: [@_devanshugautam](https://www.instagram.com/_devanshugautam/)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
