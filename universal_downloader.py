import subprocess
import sys
import os
import time

# We define a list of downloaders. They will be tried in order.
# Using 'python -m' ensures they run even if they aren't in the system PATH.
DOWNLOADERS = [
    {
        "name": "yt-dlp (The Best Overall)",
        "command": ["python", "-m", "yt_dlp", "--no-warnings", "-o", "%(title)s_{timestamp}.%(ext)s", "{url}"],
        "check": ["python", "-m", "yt_dlp", "--version"]
    },
    {
        "name": "you-get (Great for Asian & general sites)",
        "command": ["python", "-m", "you_get", "-O", "video_{timestamp}", "{url}"],
        "check": ["python", "-m", "you_get", "--version"]
    },
    {
        "name": "streamlink (Great for live streams & VODs)",
        "command": ["python", "-m", "streamlink", "{url}", "best", "-o", "video_{timestamp}.mp4"],
        "check": ["python", "-m", "streamlink", "--version"]
    }
]

def run_downloader(downloader, url):
    print(f"\n==============================================")
    print(f"[*] Attempting download with {downloader['name']}...")
    print(f"==============================================")
    
    try:
        # Check if the tool is installed by running its --version command
        subprocess.run(downloader["check"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"[-] {downloader['name']} is not installed. Skipping.")
        return False

    # Replace the '{url}' placeholder with the actual URL and timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    cmd = [arg.replace("{url}", url).replace("{timestamp}", timestamp) for arg in downloader["command"]]
    
    try:
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"\n[+] Success! {downloader['name']} successfully downloaded the video.")
            return True
        else:
            print(f"\n[-] {downloader['name']} could not download the video.")
            return False
    except Exception as e:
        print(f"\n[-] Error running {downloader['name']}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python universal_downloader.py \"<URL>\"")
        sys.exit(1)

    url = sys.argv[1]
    print(f"[*] Starting universal video downloader for: {url}\n")

    for downloader in DOWNLOADERS:
        success = run_downloader(downloader, url)
        if success:
            print("\n[*] Download complete! Exiting script.")
            break
    else:
        print("\n[-] All download attempts failed.")
        print("[*] Make sure the URL is accessible. If the site requires login or is highly protected, you might need to extract the direct video link (like we did earlier).")

if __name__ == "__main__":
    main()
