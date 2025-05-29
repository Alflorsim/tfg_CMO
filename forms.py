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

class pagoMultaForm(FlaskForm):
    nombre = StringField("Nombre en la tarjeta", validators=(DataRequired(), Length(min=4, max=50)))
    tarjeta = StringField("Número de tarjeta", validators=(DataRequired(), Length(min=16, max=19)))
    cvv = StringField("CVV", validators=(DataRequired(), Length(min=3, max=4)))
    expiracion = StringField("Fecha de expiración (MM/AA)", validators=(DataRequired(), Length(min=5, max=5)))
    submit = SubmitField("Confirmar pago")


class contactForm(FlaskForm):
    nombre = StringField("Nombre completo", validators=(DataRequired(), Length(min=4, max=50)))
    correo = EmailField("Pon tu correo", validators=(DataRequired(), Length(max=25, min=4), Email()))
    mensaje = StringField("Pon tu mensaje", validators=(DataRequired(), Length(min=5, max=400)))
    submit = SubmitField("Enviar")