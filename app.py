from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
from config import config
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms import registerForm, loginForm, contactForm
from models.entities.user import User
from models.modelUser import ModelUser

import smtplib, ssl, os
from dotenv import load_dotenv
from email.message import EmailMessage

# Inicializacion
app = Flask(__name__)

load_dotenv()

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
    return render_template('auth/nuestros_servicios.html')

@app.route('/estadoTrafico')
def estado_trafico():
    return render_template('estado_trafico.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    form = contactForm()
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        mensaje = request.form.get('mensaje')

        sender_mail = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        smtp_server = "smtp.gmail.com"
        port = 587

        cuerpo = f"""Nuevo mensaje desde el formulario de contacto:

Nombre completo: {nombre}
Correo: {correo}
Mensaje: {mensaje}
"""

        try:
            msg = EmailMessage()
            msg["Subject"] = "Nuevo mensaje de usuario"
            msg["From"] = sender_mail
            msg["To"] = sender_mail 
            msg.set_content(cuerpo)

            context = ssl.create_default_context()
            server = smtplib.SMTP(smtp_server, port)
            server.starttls(context=context)
            server.login(sender_mail, password)
            server.send_message(msg)
            server.quit()

            flash('Mensaje enviado correctamente.', 'success')
        except Exception as e:
            flash('Hubo un error al enviar el mensaje.', 'error')

        return redirect(url_for('contacto'))

    return render_template('auth/contacto.html', form=form)


# ============================================================================================================================================
# LOGIN / REGISTER
# ============================================================================================================================================

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

        flash('DNI o contraseña incorrectos','error')
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
            flash('Ese DNI ya esta registrado.','error')
            return redirect(url_for('register'))

        hash_pass = generate_password_hash(password)
        cur.execute("INSERT INTO usuarios (dni, nombre_completo, correo, contraseña, rol) VALUES (%s, %s, %s, %s, %s)", (dni, nombre, correo, hash_pass, 'usuario'))
        db.connection.commit()

        flash('Registro exitoso, ya puedes iniciar sesion.','success')
        return redirect(url_for('login'))

    return render_template('auth/register.html', form=form)
# ========================================================================================================================================================================




# ============================
# USUARIO
# ============================

@app.route('/miperfil')
@login_required
def perfil_usuario():
    if current_user.rol != 'usuario':
        return redirect(url_for('inicio'))
    return render_template('miperfil.html')

@app.route('/administrador')
@login_required
def admin_panel():
    if current_user.rol != 'admin':
        return render_template('auth/login.html')
    return render_template('admin.html')


# ============================================================================================================================================
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
        cur.execute('INSERT INTO vehiculos (usuario_id, matricula, marca, modelo, color, imagen) VALUES (%s, %s, %s, %s, %s, %s)', (current_user.id, matricula, marca, modelo, color, imagen))
        db.connection.commit()
        flash('Vehiculo añadido correctamente','success')
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
    flash("Vehiculo eliminado correctamente","success")
    return redirect(url_for('ver_vehiculos'))


@app.route('/editar_coche/<matricula>', methods=['GET', 'POST'])
@login_required
def editar_coche(matricula):

    cur = db.connection.cursor()
    cur.execute("SELECT * FROM vehiculos WHERE matricula = %s AND usuario_id = %s", (matricula, current_user.id))
    vehiculo = cur.fetchone()

    if not vehiculo:
        flash('Vehículo no encontrado o no autorizado', 'error')
        cur.close()
        return redirect(url_for('ver_vehiculos'))

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        imagen = request.form['imagen']
        cur.execute("UPDATE vehiculos SET marca = %s, modelo = %s, color = %s, imagen = %s WHERE matricula = %s AND usuario_id = %s", (marca, modelo, color, imagen, matricula, current_user.id))
        db.connection.commit()
        cur.close()
        flash('Vehículo actualizado correctamente', 'success')
        return redirect(url_for('ver_vehiculos'))

    cur.close()
    return render_template('auth/editar_coche.html', vehiculo=vehiculo)



# ============================================================================================================================================




# ============================
# ADMIN 
# ============================

@app.route('/administrador')
@login_required
def panel_admin():
    if current_user.rol != 'admin':
        return redirect(url_for('inicio'))
    return render_template('admin.html')

@app.route('/poner_multa', methods=['GET', 'POST'])
@login_required
def poner_multa():
    if current_user.rol != 'admin':
        return redirect(url_for('perfil_usuario'))

    if request.method == 'POST':
        matricula = request.form['matricula']
        descripcion = request.form['descripcion']
        foto = request.form['foto']
        importe = request.form['importe']

        cur = db.connection.cursor()
        cur.execute("SELECT usuario_id FROM vehiculos WHERE matricula = %s", (matricula,))
        resultado = cur.fetchone()

        if not resultado:
            flash('No existe ningún vehículo con esa matrícula', 'error')
            cur.close()
            return redirect(url_for('poner_multa'))

        usuario_id = resultado[0]

        cur.execute("""
            INSERT INTO multas (matricula, usuario_id, descripcion, foto, importe)
            VALUES (%s, %s, %s, %s, %s)
        """, (matricula, usuario_id, descripcion, foto, importe))
        db.connection.commit()

        cur.execute("SELECT correo FROM usuarios WHERE id = %s", (usuario_id,))
        correo_destino = cur.fetchone()[0]
        cur.close()

        

        sender_mail = os.getenv("EMAIL_SENDER")  
        password = os.getenv("EMAIL_PASSWORD")   
        smtp_server = "smtp.gmail.com"
        port = 465  

        cuerpo = f"""Subject: Nueva multa registrada


Se ha registrado una nueva multa a tu vehiculo con matricula: {matricula}

Descripcion: {descripcion}
Importe: {importe} €
Foto: {foto}

Consulta tus multas desde tu perfil.

Saludos,
DGT Virtual
"""

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as s:
                s.login(sender_mail, password)
                s.sendmail(sender_mail, correo_destino, cuerpo.encode('utf-8'))

            flash('Multa asignada y correo enviado correctamente.', 'success')
        except Exception as e:
            flash('Multa registrada, pero error al enviar correo.', 'warning')

        return redirect(url_for('poner_multa'))

    return render_template('poner_multa.html')



@app.route('/multas')
@login_required
def ver_multas():
    if current_user.rol != 'usuario':
        return redirect(url_for('inicio'))

    cur = db.connection.cursor()
    cur.execute("SELECT * FROM multas WHERE usuario_id = %s", (current_user.id,))
    multas = cur.fetchall()
    cur.close()

    pagada = request.args.get('pagada') == '1'
    return render_template('auth/multas.html', multas=multas, pagada=pagada)



@app.route('/pagar/<int:multa_id>', methods=['POST'])
@login_required
def pagar_multa(multa_id):
    cur = db.connection.cursor()
    cur.execute("DELETE FROM multas WHERE id = %s AND usuario_id = %s", (multa_id, current_user.id))
    db.connection.commit()
    cur.close()
    return redirect(url_for('ver_multas', pagada=1))



# ============================
# LOGOUT
# ============================

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('inicio'))


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run(debug=True, host='0.0.0.0', port=5000)