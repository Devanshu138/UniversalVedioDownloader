import os
import sys
import subprocess
from flask import Flask, render_template, request, Response

app = Flask(__name__)

DOWNLOADERS = [
    {
        "name": "yt-dlp",
        "command": [sys.executable, "-m", "yt_dlp", "--no-warnings", "{url}"],
        "check": [sys.executable, "-m", "yt_dlp", "--version"]
    },
    {
        "name": "you-get",
        "command": [sys.executable, "-m", "you_get", "{url}"],
        "check": [sys.executable, "-m", "you_get", "--version"]
    },
    {
        "name": "streamlink",
        "command": [sys.executable, "-m", "streamlink", "{url}", "best", "-o", "downloaded_video.mp4"],
        "check": [sys.executable, "-m", "streamlink", "--version"]
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download')
def download():
    url = request.args.get('url')
    if not url:
        return Response("data: Error: No URL provided\n\n", mimetype='text/event-stream')

    def generate():
        yield f"data: [*] Starting universal video downloader for: {url}\n\n"
        
        for downloader in DOWNLOADERS:
            yield f"data: ==============================================\n\n"
            yield f"data: [*] Attempting download with {downloader['name']}...\n\n"
            yield f"data: ==============================================\n\n"
            
            try:
                subprocess.run(downloader["check"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                yield f"data: [-] {downloader['name']} is not installed. Skipping.\n\n"
                continue

            cmd = [arg.replace("{url}", url) for arg in downloader["command"]]
            
            try:
                # Use Popen to read output line by line and stream it to the client
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                
                for line in process.stdout:
                    yield f"data: {line}\n\n"
                
                process.wait()
                if process.returncode == 0:
                    yield f"data: \n\n"
                    yield f"data: [+] Success! {downloader['name']} successfully downloaded the video.\n\n"
                    yield f"data: [*] Download complete! Exiting script.\n\n"
                    yield f"data: [DONE]\n\n"
                    return
                else:
                    yield f"data: \n\n"
                    yield f"data: [-] {downloader['name']} could not download the video.\n\n"
            except Exception as e:
                yield f"data: \n\n"
                yield f"data: [-] Error running {downloader['name']}: {e}\n\n"
                
        yield f"data: \n\n"
        yield f"data: [-] All download attempts failed.\n\n"
        yield f"data: [DONE]\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("Server running on http://127.0.0.0:5000")
    app.run(debug=True, port=5000, threaded=True)
