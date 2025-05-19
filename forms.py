from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class registerForm(FlaskForm):
    dni = StringField("Pon tu dni", validators=(DataRequired(), Length(max=25, min=4)))
    nombre_completo= StringField("Pon tu nombre completo", validators=(DataRequired(), Length(max=25, min=4)))
    correo = EmailField("Pon tu correo", validators=(DataRequired(), Length(max=25, min=4), Email()))
    contraseña = PasswordField("Pon tu contraseña", validators=(DataRequired(), Length(max=25, min=4)))
    submit = SubmitField('Crear usuario')


class loginForm(FlaskForm):
    dni = StringField("Pon tu dni", validators=(DataRequired(), Length(max=25, min=4)))
    contraseña = PasswordField("Pon tu contraseña", validators=(DataRequired(), Length(max=25, min=4)))
    submit = SubmitField('Iniciar sesion')

