
from flask import Flask, render_template, redirect, url_for, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

load_dotenv()

# ================= APP SETUP =================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
ckeditor = CKEditor(app)

# ================= MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    posts = db.relationship('Post', backref='author', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


# ================= LOGIN MANAGER =================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ================= ROUTES =================

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route('/blog')
def blog():
    posts = Post.query.all()
    return render_template("blog.html", posts=posts)


# ================= REGISTER =================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'])

        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("register.html")


# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))

    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ================= CREATE POST =================

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':

        image = request.files['image']
        filename = None

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        post = Post(
            title=request.form['title'],
            content=request.form['content'],
            image=filename,
            user_id=current_user.id
        )

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template("create_post.html")


# ================= EDIT POST =================

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template("edit_post.html", post=post)


# ================= DELETE POST =================

@app.route('/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))


# ================= POST DETAIL =================

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post_detail.html", post=post)


# ================= LIKE =================

@app.route('/like/<int:post_id>')
@login_required
def like(post_id):
    like = Like(user_id=current_user.id, post_id=post_id)
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))


# ================= COMMENT =================

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment(post_id):
    new_comment = Comment(
        text=request.form['comment'],
        user_id=current_user.id,
        post_id=post_id
    )

    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))


# ================= RUN =================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()