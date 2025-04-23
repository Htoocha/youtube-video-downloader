from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from pytubefix import YouTube
import os
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)
DOWNLOAD_PATH = "/storage/emulated/0/memo/"

# Progress variable
download_progress = 0

def download_video(url):
    global download_progress
    try:
        yt = YouTube(url)
        title = yt.title.replace(" ", "_")

        # Send message to update front-end
        socketio.emit('update_message', {'message': "Download started..."})

        # Try 1080p first
        video = yt.streams.filter(res="1080p", mime_type="video/mp4", only_video=True).first()

        # If 1080p is not available, try 720p
        if not video:
            video = yt.streams.filter(res="720p", mime_type="video/mp4", only_video=True).first()

        # Try to get the best audio
        audio = yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by('abr').desc().first()

        if not video or not audio:
            socketio.emit('update_message', {'message': "1080p or 720p video or audio not found."})
            return

        # Simulate downloading video
        socketio.emit('update_message', {'message': "Downloading video temp..."})
        video_path = video.download(output_path=DOWNLOAD_PATH, filename="temp_video.mp4")

        # Simulate downloading audio
        socketio.emit('update_message', {'message': "Downloading audio temp..."})
        audio_path = audio.download(output_path=DOWNLOAD_PATH, filename="temp_audio.mp4")

        # Simulate progress
        for i in range(1, 101):
            download_progress = i
            socketio.emit('update_progress', {'progress': i})
            time.sleep(0.1)  # Simulate download delay

        # Merging video and audio
        socketio.emit('update_message', {'message': "Merging..."})
        output_path = os.path.join(DOWNLOAD_PATH, f"{title}_1080p.mp4")
        ffmpeg_cmd = f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{output_path}"'
        os.system(ffmpeg_cmd)

        os.remove(video_path)
        os.remove(audio_path)

        # Final message
        socketio.emit('update_message', {'message': f"Download complete: {output_path}"})
    except Exception as e:
        socketio.emit('update_message', {'message': f"Error: {str(e)}"})

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/start_download', methods=['POST'])
def start_download():
    url = request.form.get('url')
    global download_progress
    download_progress = 0  # Reset progress
    # Start download in a separate thread
    threading.Thread(target=download_video, args=(url,)).start()
    return '', 200

@app.route('/progress', methods=['GET'])
def progress():
    global download_progress
    return {'progress': download_progress}

if __name__ == '__main__':
    socketio.run(app, debug=True)
