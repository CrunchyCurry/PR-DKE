from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from application import User


class RegisterForm(FlaskForm):
    username = StringField("Benutzername", validators=[DataRequired(), Length(min=2, max=16)])
    password = PasswordField("Passwort", validators=[DataRequired(), Length(min=8, max=16)])
    confirm_password = PasswordField("Passwort wiederholen",
                                     validators=[DataRequired(), Length(min=8, max=16), EqualTo("password")])
    submit = SubmitField("Benutzer anlegen")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Benutzername bereits vergeben. Bitte einen anderen Benutzernamen wählen.")


class LoginForm(FlaskForm):
    username = StringField("Benutzername", validators=[DataRequired(), Length(min=2, max=16)])
    password = PasswordField("Passwort", validators=[DataRequired()])
    remember = BooleanField("Angemeldet bleiben")
    submit = SubmitField("Einloggen")


class StationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    state = StringField("Bundesland", validators=[DataRequired()])
    submit = SubmitField("Bestätigen")
