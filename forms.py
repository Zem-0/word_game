from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Regexp

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5)])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Regexp(r'^(?=.*[@#$%^&+=!])', message="Password must contain at least one special character")
        ]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo('password', message="Passwords must match")
        ]
    )
    role = SelectField(
        "Role",
        choices=[("player", "Player"), ("admin", "Admin")],
        validators=[DataRequired()]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
