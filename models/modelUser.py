
from models.entities.user import User
from werkzeug.security import check_password_hash

class ModelUser():

    @classmethod
    def login(cls, db, user):
        try:
            cur = db.connection.cursor()
            sql = 'SELECT * FROM usuarios WHERE dni = %s'
            cur.execute(sql, (user.dni,))
            row = cur.fetchone()
            if row:
                if check_password_hash(row[4], user.password):
                    return User(row[0],row[1],row[2],row[3],row[4],row[5])
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
        
    
        