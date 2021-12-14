from typing import Text
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms import validators
from wtforms.fields.simple import TextField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Repeat Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already taken.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min = 0, max = 140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
        
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your old password"})
    new_password_1 = PasswordField('New Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your new password"})
    new_password_2 = PasswordField('New Password Again', validators=[DataRequired()], render_kw={"placeholder": "Repeat your new password"})
    submit = SubmitField('Update password')
                


class PostForm(FlaskForm):
    post = TextAreaField('Post Caption', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class CreateRoomForm(FlaskForm):
    name = TextField('Room Name', validators=[DataRequired(), Length(min=1, max=40)])
    desc = TextAreaField('Room Description', validators=[DataRequired(), Length(min=1, max=250)])
    submit = SubmitField('Create Room')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class ReportForm(FlaskForm):
    report_desc = TextAreaField('Report Reason', validators=[DataRequired(), Length(min=20, max=300)], render_kw={"placeholder": "Enter reason for report"})
    submit = SubmitField('Submit Report')

class ReplyForm(FlaskForm):
    body = TextAreaField('Reply Body', validators=[DataRequired(), Length(min=1, max=50)], render_kw={"placeholder": "Enter reply"})
    submit = SubmitField('Submit Reply')