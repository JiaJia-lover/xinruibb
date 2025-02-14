from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///love.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB限制

db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200))
    uploader = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


with app.app_context():
    db.create_all()

# 简单密码验证
PASSWORD = "baobei040529"  # 请修改为你的密码


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # 处理消息
        if 'message' in request.form:
            new_message = Message(
                content=request.form['content'],
                author=request.form['author']
            )
            db.session.add(new_message)
            db.session.commit()

        # 处理图片上传
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = str(uuid.uuid4()) + secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_image = Image(
                    filename=filename,
                    caption=request.form.get('caption'),
                    uploader=request.form.get('author')
                )
                db.session.add(new_image)
                db.session.commit()

    messages = Message.query.order_by(Message.timestamp.desc()).all()
    images = Image.query.order_by(Image.timestamp.desc()).all()
    return render_template('index.html', messages=messages, images=images)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run()