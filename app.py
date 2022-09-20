from distutils.util import execute
from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os


app = Flask(__name__)
app.secret_key="admin"

# Config MySQL
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema'

# Init MySQL
mysql.init_app(app)

# Almaceno la ruta especifica de la carpeta uploads, creando una referencia a la variable config, para acceder a ella
CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/')
def index():

    sql = "SELECT * FROM `empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    
    empleados = cursor.fetchall()   # me regresa toda la info obtenida
    print(empleados)

    conn.commit()   # cierra la conexión
    return render_template('empleados/index.html', empleados=empleados)


# eliminar datos
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM empleados WHERE id = %s", (id))
    empleados=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))

    cursor.execute("DELETE FROM empleados WHERE id=%s", (id))
    conn.commit()
    return redirect('/')


# editar datos
@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id = %s", (id))
    empleados = cursor.fetchall()
    conn.commit()
    print(empleados)
    return render_template('empleados/edit.html', empleados=empleados)

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    id = request.form['txtID']   
    sql = "UPDATE  empleados SET  nombre=%s ,correo=%s WHERE id=%s ;"
    datos = (_nombre, _correo, id)

    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()   
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':

        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)
        
        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        fila = cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s", (nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql, datos)

    conn.commit()

    return redirect('/')


@app.route('/create')
def create():
    return render_template('empleados/create.html')


@app.route('/store', methods=['POST'])
def storage():

    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    if (_nombre=='' or _correo=='' or _foto==''):
        flash('Debes completar todos los datos de los campos')
        return redirect(url_for('create'))

    # obtengo el formato de ltiempo cuando subimos la foto
    now = datetime.now()    # almaceno la fercha actual
    tiempo = now.strftime("%Y%H%M%S")  # tiempo dependera de esa fecha y la convierto a formato de tiempo
    
    # Evitamos sobreescribir una fotografia y la subimos y la guardo con el nuevo nombre en carpeta uploads
    if _foto.filename != '':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    datos = (_nombre, _correo,nuevoNombreFoto)

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute(sql, datos)

    conn.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
