from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, TextAreaField
from wtforms.validators import InputRequired, Regexp, Email, EqualTo, Length


class CreateAccountForm(FlaskForm):
    email = StringField(
        label='Email',
        validators=[
            InputRequired('E-mail field is required.'),
            Email('Invalid e-mail address.'),
            Regexp(
                regex=r'[^@]+@[^@]+\.[a-zA-Z]{2,6}',
                message='Use this format your e-mail address someone@example.com.'
            )
        ]
    )
    username = StringField(
        label='Username',
        validators=[
            InputRequired('Username field is required'),
            Length(max=16, message="The username must be less or equal to 16 characters.")
        ]
    )
    password = PasswordField(
        label='Password',
        validators=[
            InputRequired('Password field is required.'),
            EqualTo('confirm_password', message='Passwords must match.'),
            Regexp(
                regex=r'^(?=.*[0-9]+.*)(?=.*[a-zA-Z]+.*)[0-9a-zA-Z]{6,}$',
                message='Password must contain at least one letter, \
                    at least one number, and be longer than six charaters.'
            )
        ]
    )
    confirm_password = PasswordField(label='Confirm Password',
        validators=[InputRequired('Confirm your password.')]
    ) 
    

class LoginForm(FlaskForm):
    username = StringField(label='Username', 
        validators=[InputRequired('Username field is required')]
    )
    password = PasswordField(label='Password',
        validators=[InputRequired('Password field is requiered')]
    )


class UploadBrocatForm(FlaskForm):
    title = StringField(
        label='Title',
        validators=[
            InputRequired('The Brocat needs a title!'),
            Length(max=100, message='100 is the maximum characters for a title')
        ]
    )
    thumbnail = FileField(label='Thuumbnail')
    audio = FileField(label='Audio', validators=[InputRequired('We need your Brocat here!')])
    description = TextAreaField(label='Description')
