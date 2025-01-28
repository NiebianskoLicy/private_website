from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class CreatePostForm(FlaskForm):
    title = StringField("Post Title", validators=[DataRequired()])
    body = CKEditorField("Content", validators=[DataRequired()])
    img = FileField('Image', validators=[FileRequired(), FileAllowed(('txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'), "Only photos")])
    project_url = StringField("Link to project", validators=[DataRequired(), URL()])
    submit = SubmitField("Submit Post")