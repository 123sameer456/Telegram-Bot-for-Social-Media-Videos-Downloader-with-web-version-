from flask import Flask, request, jsonify, render_template
import yt_dlp
import os

app = Flask(__name__)

# Create the downloads folder
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Function to detect platform
def detect_platform(url):
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "facebook.com" in url or "fb.watch" in url:
        return "facebook"
    elif "instagram.com" in url or "instagr.am" in url:
        return "instagram"
    elif "x.com" in url or "twitter.com" in url:
        return "twitter"
    else:
        return "unknown"

# Download function
def download_video(url, platform):
    # ydl_opts = {
    #     'format': 'bestvideo+bestaudio/best',
    #     'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    #     'quiet': False,
    #     'merge_output_format': 'mp4',
    # }
    ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'merge_output_format': 'mp4',
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',  # Ensure proper mp4 encoding
    }],
    'postprocessor_args': [
        '-vcodec', 'libx264',  # Force H.264 video
        '-acodec', 'aac',      # Force AAC audio
        '-strict', 'experimental'
    ],
    'prefer_ffmpeg': True,
    'quiet': False,
}

    # Special handling for platforms
    if platform == "facebook":
        ydl_opts['force_generic_extractor'] = True  # Ensures Facebook videos work

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f"{platform.capitalize()} video downloaded successfully!"
    except Exception as e:
        return f"Download failed: {str(e)}"

# Route for frontend form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle video download (POST request only)
@app.route('/download', methods=['POST'])
def download():
    data = request.json  # Accept JSON input
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    platform = detect_platform(url)
    if platform == "unknown":
        return jsonify({"error": "Unsupported platform"}), 400

    message = download_video(url, platform)
    return jsonify({"message": message})

if __name__ == '__main__':
    app.run(debug=True)
