from curses import flash
from wtforms.fields.simple import EmailField
from flask_wtf import FlaskForm
from wtforms import StringField,FileField,SubmitField,EmailField,PasswordField,SelectField,IntegerField,IntegerRangeField
from wtforms.validators import DataRequired,EqualTo,NumberRange
from flask_ckeditor import CKEditorField




class user_form(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    username=StringField("UserName",validators=[DataRequired()])
    college=SelectField("College")
    email=EmailField("Email",validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit=SubmitField("Submit")


class login_form(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit=SubmitField("Submit")

class file_upload_form(FlaskForm):
    author=StringField("Author",validators=[DataRequired()])
    subject=StringField("Subject",validators=[DataRequired()])
    branch=StringField("Branch",validators=[DataRequired()])
    modules=SelectField("Module")
    sem=IntegerField("Semester",validators=[NumberRange(min=1,max=8)])
    college=SelectField("College")
    content=StringField("Topics")
    file = FileField("File")
    submit=SubmitField("Submit")


class file_search_form(FlaskForm):
    author=StringField("Author",validators=[DataRequired()])
    subject=StringField("Subject",validators=[DataRequired()])
    branch=StringField("Branch",validators=[DataRequired()])
    modules=SelectField("Module")
    sem=IntegerField("Semester",validators=[NumberRange(min=1,max=8)])
    college=SelectField("College")
    file = FileField("File")
    submit=SubmitField("Submit")


class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Submit")


class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = CKEditorField('Content', validators=[DataRequired()])
	slug = StringField("Topic", validators=[DataRequired()])
	submit = SubmitField("Submit")

class ReplyForm(FlaskForm):
	content = CKEditorField('Reply', validators=[DataRequired()])
	submit = SubmitField("Submit")

