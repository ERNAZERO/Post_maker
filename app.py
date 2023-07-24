from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from peewee import *

from models import db, Post, MyUser

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return MyUser.select().where(MyUser.id==int(user_id)).first()


@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = MyUser.select().where(MyUser.email==email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect('/login/')
        else:
            login_user(user)
            return redirect('/')
    return render_template('login.html')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/login/')


def validate_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    return True


def save_default_avatar():
    with open('./static/images/img.png', 'rb') as default_avatar_file:
        default_avatar_data = default_avatar_file.read()
        return default_avatar_data

def save_default_post_image():
    with open('./static/images/Why You Should Do Nothing.jpeg', 'rb') as default_post_image_file:
        default_post_image_data = default_post_image_file.read()
        return  default_post_image_data


@app.route('/register/', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        age = request.form['age']
        full_name = request.form['full_name']
        password = request.form['password']
        file = request.files['avatar']
        user = MyUser.select().where(MyUser.email == email).first()
        if file.filename == '':
            avatar_data = save_default_avatar()
        else:
            avatar_data = file.read()
        if user:
            flash('email addres already exists')
            return redirect('/register/')
        if MyUser.select().where(MyUser.username==username).first():
            flash('username already exists')
            return redirect('/register/')
        else:
            if validate_password(password):
                MyUser.create(
                    email=email,
                    username=username,
                    age=age,
                    password=generate_password_hash(password),
                    full_name=full_name,
                    avatar=avatar_data
                )
                return redirect('/login/')
            else:
                flash('wrong password')
                return redirect('/register/')
    return render_template('register.html')


@app.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['post_image']
        if file.filename == '':
            post_image_data = save_default_post_image()
        else:
            post_image_data = file.read()

        Post.create(
            title=title,
            author = current_user,
            content = content,
            post_image=post_image_data
        )
        return redirect('/')
    return render_template('create.html')


@app.route('/<int:id>/')
def get_post(id):
    post = Post.select().where(Post.id == id).first()
    if post:
        return render_template('post_detail.html', post=post)
    return f'Post with id = {id} does not exists'


@app.route('/<int:id>/like/', methods=('GET', 'POST'))
@login_required
def like_post(id):
    post = Post.get_or_none(Post.id == id)
    if post:
        if 'liked_posts' not in session:
            session['liked_posts'] = []
        if id not in session['liked_posts']:
            post.likes += 1
            post.save()
            session['liked_posts'].append(id)
        return redirect(f'/{id}/')
    return render_template('post_detail.html', post=post)


#route decorator
@app.route('/')
def index():
    all_posts = Post.select()
    return render_template("index.html", posts=all_posts)


@app.route('/profile/<int:id>/')
@login_required
def profile():
    user = MyUser.select().where(MyUser.id==id).first()
    posts = Post.select().where(Post.author==user)
    return render_template('profile.html', user=user, posts = posts)


@app.route('/current_profile/')
@login_required
def my_profile():
    posts = Post.select().where(Post.author==current_user)
    return render_template('profile.html', user=current_user, posts=posts)


@app.route('/update_profile/', methods=('GET', 'POST'))
@login_required
def profile_update():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        age = request.form['age']
        full_name = request.form['full_name']
        file = request.files['avatar']
        avatar_data = file.read()

        obj = MyUser.update({
            MyUser.username: username,
            MyUser.email: email,
            MyUser.age: age,
            MyUser.full_name: full_name,

            MyUser.avatar: avatar_data
        }).where(MyUser.id == current_user.id)
        obj.execute()
        return redirect(f'/current_profile/')
    return render_template('update_profile.html', user=current_user)


@app.route('/<int:id>/update/', methods=('GET', 'POST'))
@login_required
def update(id):
    post = Post.select().where(Post.id==id).first()
    if request.method == 'POST':
        if post:
            if current_user == post.author:
                title = request.form['title']
                content = request.form['content']
                filename = request.files['post_image']
                post_image_data = filename.read()
                obj = Post.update({
                    Post.title: title,
                    Post.content: content,
                    Post.post_image: post_image_data
                }).where(Post.id == id)
                obj.execute()
                return redirect(f'/{id}/')
            return f'you are not author of this post'
        return f'Post with id = {id} does not exists'
    return render_template('update.html', post=post)






@app.route('/<int:id>/delete/', methods=('GET', 'POST'))
@login_required
def delete(id):
    post = Post.select().where(Post.id==id).first()
    if request.method == 'POST':
        if post:
            if current_user == post.author:
                post.delete_instance()
                return redirect('/')
            return f'you are not author of this post'
        return f'Post with id = {id} does not exists'
    return render_template('delete.html', post=post)


@app.route('/avatar/<int:user_id>')
def avatar(user_id):
    user = MyUser.get_or_none(id=user_id)
    if user and user.avatar:
        return app.response_class(user.avatar, content_type='image/jpeg')
    else:
        return 'Аватарка не найдена.'


@app.route('/post_image/<int:post_id>')
def post_image(post_id):
    post = Post.get_or_none(id=post_id)
    if post and post.post_image:
        return app.response_class(post.post_image, content_type='image/jpeg')
    else:
        return 'Error.'



@app.errorhandler(404)
def page_not_found_(e):
    return render_template('error404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('error505.html'), 500





if __name__ == '__main__':
    app.debug = True
    app.run()