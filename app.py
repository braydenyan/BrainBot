from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
import os
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy


class CommentForm(FlaskForm):
    text = StringField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
db = SQLAlchemy(app)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))

def create_db():
    with app.app_context():
        db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload1():
    return render_template('upload.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        

        file_url = url_for('uploaded_file', filename=filename)
        return render_template('result.html', file_url=file_url)
    else:
        return 'no such file type'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/result')
def result():
    comments = Comment.query.all()
    return render_template('result.html', comments=comments)

@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    form = CommentForm()
    if form.validate_on_submit():
        comment_text = form.text.data
        comment = Comment(text=comment_text)
        db.session.add(comment)
        db.session.commit()
        flash('Comment submitted successfully!', 'success')
        return redirect(url_for('result'))
    return render_template('result.html', form=form, comments=Comment.query.all())


if __name__ == '__main__':
    create_db()
    app.run(debug=True)