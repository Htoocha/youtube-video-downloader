from flask import Flask, render_template, request
from pytubefix import YouTube
import os

app = Flask(__name__)
DOWNLOAD_PATH = "/storage/emulated/0/memo/"

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            yt = YouTube(url)
            title = yt.title.replace(" ", "_")

            video = yt.streams.filter(res="1080p", mime_type="video/mp4", only_video=True).first()
            audio = yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by('abr').desc().first()

            if not video or not audio:
                message = "1080p or audio not found."
            else:
                video_path = video.download(output_path=DOWNLOAD_PATH, filename="temp_video.mp4")
                audio_path = audio.download(output_path=DOWNLOAD_PATH, filename="temp_audio.mp4")
                output_path = os.path.join(DOWNLOAD_PATH, f"{title}_1080p.mp4")

                ffmpeg_cmd = f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{output_path}"'
                os.system(ffmpeg_cmd)

                os.remove(video_path)
                os.remove(audio_path)

                message = f"Download complete: {output_path}"

        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("index.html", message=message)

if __name__ == '__main__':
    app.run(debug=True)
    
