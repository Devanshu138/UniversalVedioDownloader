# Universal Video Downloader

A python-based desktop GUI application that can download videos from almost any platform using multiple fallback methods (`yt-dlp`, `you-get`, `streamlink`).

## Developer

Developed by **Devanshu** 💻
- **GitHub**: [@Devanshu138](https://github.com/Devanshu138)
- **Instagram**: [Follow on Instagram 📸](https://instagram.com/devanshu138) 

## Features
- **Sleek Modern GUI**: Built with `customtkinter` for a dark-mode, premium look.
- **Multiple Engines**: Automatically falls back to alternative downloaders if one fails.
- **Real-Time Terminal Output**: See exactly what the download engine is doing directly in the app.
- **Help Guide**: Includes advanced instructions for grabbing hidden video links from protected streaming sites via Developer Tools.

## Installation

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the GUI app:
```bash
python gui_downloader.py
```
Paste a URL into the input field and hit "Download"!


