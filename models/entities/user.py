from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, dni, nombre_completo, correo, password, rol):
        self.id = id
        self.dni = dni
        self.nombre_completo = nombre_completo
        self.correo = correo
        self.password = password
        self.rol = rol
