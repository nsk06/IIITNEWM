from flask_wtf import FlaskForm
from wtforms import *
#from wtforms.validators import *
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,Length
from database import User
from flask import request
#from flask_babel import lazy_gettext as _l

class Login(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
class CommentForm(FlaskForm):
    post =TextAreaField('post', validators=[DataRequired(),Length(min=1, max=140)])
    submit = SubmitField('Submit')
class GroupForm(FlaskForm):
    name = TextAreaField('Name the group',validators=[
        DataRequired(),Length(min=1,max=45)])
    Type = SelectField('Group_Type',choices = [(1,'private'),(2,'public'),(3,'closed')],coerce = int)
    submit = SubmitField('enter')
class MessageForm(FlaskForm):
    msg = TextAreaField('Enter your message',validators=[
        DataRequired(), Length(min=1, max=700)])
    submit = SubmitField('send')
class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
            super(SearchForm, self).__init__(*args, **kwargs)