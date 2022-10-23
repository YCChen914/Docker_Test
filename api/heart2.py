import os
from flask import Flask, request, render_template,redirect,url_for
from flask_celery import make_celery
from flask_cors import CORS
import model
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = set(['xlsx'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(CELERY_CONFIG={
    'broker_url': 'redis://localhost:6379/0',
    'result_backend':'redis://localhost:6379/1',
})

celery = make_celery(app)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result/<filename>', methods=['GET'])
def result(filename):
    if(filename != 'wait'):
        global col_result
        col_result  = feature_selection.delay(filename)
        return render_template('Result.html',result = col_result)#render_template('index.html')
    else:
        return render_template('Result.html',result = col_result)

@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == 'GET':
        return render_template('Upload.html')
    else:
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('result',filename=filename))

@celery.task(name='feature selection')
def feature_selection(filename):
    return model.result(filename)      



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)