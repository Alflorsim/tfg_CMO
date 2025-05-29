
from models.entities.user import User
from werkzeug.security import check_password_hash

class ModelUser():

    @classmethod
    def login(cls, db, user):
        try:
            cur = db.connection.cursor()
            sql = 'SELECT id, dni, nombre_completo, correo, contraseña, rol FROM usuarios WHERE dni = %s'
            cur.execute(sql, (user.dni,))
            row = cur.fetchone()
            cur.close()
            if row:
                return User(row[0], row[1], row[2], row[3], row[4], row[5])
            return None
        except Exception as e:
            raise Exception(e)
        
    @classmethod
    def get_by_id(cls, db, id):
        try:
            cur = db.connection.cursor()
            sql = 'SELECT * FROM usuarios WHERE id = %s'
            cur.execute(sql, (id,))
            row = cur.fetchone()
            if row:
                return User(row[0],row[1],row[2],row[3],row[4],row[5])
            return None
        except Exception as e:
            raise Exception(e)
        
    
        