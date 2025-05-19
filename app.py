from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
from config import config
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms import registerForm, loginForm
from models.entities.user import User
from models.modelUser import ModelUser

# Inicializacion
app = Flask(__name__)


db = MySQL(app)
login_manager_app = LoginManager(app)
login_manager_app.login_view = 'login'  # Redirige al login si no esta autenticado

# Cargar usuario por ID
@login_manager_app.user_loader
def user_loader(user_id):
    return ModelUser.get_by_id(db, user_id)

# ============================
# RUTAS PUBLICAS
# ============================

@app.route('/')
def inicio():
    return render_template('auth/inicio.html')

@app.route('/nuestrosServicios')
def nuestros_servicios():
    return render_template('auth/login.html')

@app.route('/estadoTrafico')
def estado_trafico():
    return render_template('estado_trafico.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')


# ============================
# LOGIN / REGISTER
# ============================

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm()
    if request.method == 'POST':
        dni = request.form.get('dni')
        password = request.form.get('password')

        user = User(None, dni, None, None, password, None)
        logged_user = ModelUser.login(db, user)
        if logged_user and check_password_hash(logged_user.password, password):
            login_user(logged_user)

            if logged_user.rol == 'admin':
                return redirect(url_for('panel_admin'))
            else:
                return redirect(url_for('perfil_usuario'))

        flash('DNI o contraseña incorrectos')
        return redirect(url_for('login'))

    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = registerForm()
    if request.method == 'POST':
        dni = request.form.get('dni')
        nombre = request.form.get('nombre_completo')
        correo = request.form.get('correo')
        password = request.form.get('password')

        cur = db.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE dni = %s", (dni,))
        user = cur.fetchone()
        if user:
            flash('Ese DNI ya esta registrado.')
            return redirect(url_for('register'))

        hash_pass = generate_password_hash(password)
        cur.execute("INSERT INTO usuarios (dni, nombre_completo, correo, contraseña, rol) VALUES (%s, %s, %s, %s, %s)", (dni, nombre, correo, hash_pass, 'usuario'))
        db.connection.commit()

        flash('Registro exitoso. Ya puedes iniciar sesion.')
        return redirect(url_for('login'))

    return render_template('auth/register.html', form=form)

# ============================
# USUARIO
# ============================

@app.route('/miperfil')
@login_required
def perfil_usuario():
    if current_user.rol != 'usuario':
        return redirect(url_for('inicio'))
    return render_template('miperfil.html')


# VEHICULOS
# ============================================================================================================================================
@app.route('/vehiculos')
@login_required
def ver_vehiculos():
    if current_user.rol != 'usuario':
        return redirect(url_for('inicio'))

    cur = db.connection.cursor()
    sql = 'SELECT matricula, marca, modelo, color, imagen FROM vehiculos WHERE usuario_id = %s'
    cur.execute(sql, (current_user.id,))
    vehiculos = cur.fetchall()
    
    return render_template('auth/vehiculos.html', vehiculos=vehiculos)


@app.route('/añadirVehiculo', methods=['GET', 'POST'])
@login_required
def form_vehiculo():
    if current_user.rol != 'usuario':
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        matricula = request.form.get('matricula')
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        color = request.form.get('color')
        imagen = request.form.get('imagen')

        cur = db.connection.cursor()
        cur.execute('INSERT INTO vehiculos (usuario_id, matricula, marca, modelo, color, imagen) VALUES (%s, %s, %s, %s, %s, %s)',
                    (current_user.id, matricula, marca, modelo, color, imagen))
        db.connection.commit()
        flash('Vehiculo añadido correctamente')
        return redirect(url_for('ver_vehiculos'))

    return render_template('auth/add_coche.html')


@app.route('/eliminarVehiculo/<string:matricula>', methods=['POST'])
@login_required
def eliminar_vehiculo(matricula):
    if current_user.rol != 'usuario':
        return redirect(url_for('inicio'))

    cur = db.connection.cursor()
    sql = "DELETE FROM vehiculos WHERE matricula = %s AND usuario_id = %s"
    cur.execute(sql, (matricula, current_user.id))
    db.connection.commit()
    flash("Vehiculo eliminado correctamente")
    return redirect(url_for('ver_vehiculos'))
# ============================================================================================================================================



# ============================
# LOGOUT
# ============================

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('inicio'))


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run(debug=True, host='0.0.0.0')