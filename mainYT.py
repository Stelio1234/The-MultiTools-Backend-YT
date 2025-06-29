from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pytube import YouTube
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "YouTube Downloader backend is online 🚀"})

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    quality = request.args.get('quality', 'highest')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        yt = YouTube(url)

        # Filter for mp4 + progressive = has video + audio
        streams = yt.streams.filter(progressive=True, file_extension='mp4')

        if quality == "highest":
            stream = streams.order_by('resolution').desc().first()
        else:
            stream = streams.filter(res=quality).first()

        if not stream:
            return jsonify({'error': f'{quality} not available for this video'}), 404

        safe_title = yt.title.replace('/', '_').replace('\\', '_')
        filename = f"{safe_title}.mp4"
        stream.download(filename=filename)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up the file if it was created
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
