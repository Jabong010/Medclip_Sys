from flask import Flask, request, jsonify, render_template, url_for
from PIL import Image
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
PROCESSED_FOLDER = 'static/processed/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request.'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file.'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            processed_img_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)

            # 上传图片，对图片进行处理
            try:
                with Image.open(img_path) as im:
                    im.thumbnail((500, 500))
                    im.save(processed_img_path)
            except Exception as e:
                return jsonify({'error': f'Error processing image: {str(e)}'}), 500

            # 如果上传成功 返回数据显示
            return jsonify({'processed_image_url': url_for('static', filename=f'processed/{filename}')})

    return render_template('upload.html')

# 运行后输入http://127.0.0.1:5000/upload
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['PROCESSED_FOLDER']):
        os.makedirs(app.config['PROCESSED_FOLDER'])
    app.run(debug=True)
