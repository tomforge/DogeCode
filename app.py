import os
from flask import Flask, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from crypto import encryption_api, decryption_api, load_image
UPLOAD_FOLDER = '/home/ubuntu/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/yo')
def yo():
    return 'yo'

@app.route('/encode')
def encode_file():
    print('hello')
    message = request.args['message']
    uri = encryption_api(message)
    print(uri)
    return send_file(uri, mimetype="image/png")

@app.route('/decode', methods=['POST'])
def decode_file():
    #passphrase = request.form['pass']
    file = request.files['media']
    image = load_image(file)
    return decryption_api(image, "Shoob")

@app.route('/site-map')
def test():
    links = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return links

    # if request.method == 'POST':
    #     # check if the post request has the file part
    #     if 'file' not in request.files:
    #         flash('No file part')
    #         return redirect(request.url)
    #     file = request.files['file']
    #     # if user does not select file, browser also
    #     # submit a empty part without filename
    #     if file.filename == '':
    #         flash('No selected file')
    #         return redirect(request.url)
    #     if file and allowed_file(file.filename):
    #         filename = secure_filename(file.filename)
    #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #         return redirect(url_for('uploaded_file',
    #                                 filename=filename))

if __name__ == "__main__":
    app.run(debug=True)

