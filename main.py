import os
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request, message_flashed
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from forms import CreatePostForm



app = Flask(__name__)
SECRET_KEY = os.urandom(32)
UPLOAD_FOLDER = 'static/images/project'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ckeditor = CKEditor(app)
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class ProjectPosts(db.Model):
    __tablename__ = "Posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_name: Mapped[str] = mapped_column(String(250), nullable=False)
    project_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    result = db.session.execute(db.select(ProjectPosts))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(ProjectPosts).where(ProjectPosts.title == form.title.data))
        result = result.scalars()
        if result:
            flash("This project was already created", 'error')
            return redirect(url_for("add_post"))
        f = form.img.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
            ))
            
        new_post = ProjectPosts(
            title=form.title.data,
            body=form.body.data,
            img_name=filename,
            project_url=form.project_url.data,
            
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_post.html", form=form)

@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = db.get_or_404(ProjectPosts, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

# TODO fix editing post

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(ProjectPosts, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        body=post.body,
        img_name=post.img_name,
        project_url=post.project_url,
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.body = edit_form.body.data
        post.img_name = edit_form.img.data
        post.project_url = edit_form.project_url.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_post.html", form=edit_form, is_edit=True)


if __name__ == "__main__":
    app.run(debug=False, port=5001)
