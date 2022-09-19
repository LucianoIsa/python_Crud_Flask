from flask import Flask
from flask import render_template, request
from flaskext.mysql import MySQL
from datetime import datetime


app = Flask(__name__)

# Config MySQL
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema'

# Init MySQL
mysql.init_app(app)


@app.route('/')
def index():

    sql = "SELECT * FROM `empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    
    empleados = cursor.fetchall()   #me regresa toda la info obtenida
    print(empleados)

    conn.commit()   #cierra la conexión
    return render_template('empleados/index.html', empleados = empleados)




@app.route('/create')
def create():
    return render_template('empleados/create.html')


@app.route('/store', methods=['POST'])
def storage():

    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']

    _foto = request.files['txtFoto']

    # obtengo el formato de ltiempo cuando subimos la foto
    now = datetime.now()    #almaceno la fercha actual
    tiempo = now.strftime("%Y%H%M%S") #tiempo dependera de esa fecha y la convierto a formato de tiempo
    
    #Evitamos sobreescribir una fotografia y la subimos y la guardo con el nuevo nombre en carpeta uploads
    if _foto.filename !='':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    datos = (_nombre, _correo, nuevoNombreFoto)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return render_template('empleados/index.html')


if __name__ == '__main__':
    app.run(debug=True)
