from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'  # Necesaria para manejar sesiones

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="acetato131962",
        database="logindb"
    )

@app.route('/')
def login():
    return render_template('LOGIN.html')

@app.route('/login', methods=['POST'])
def validar_login():
    user_id = request.form.get('usuario', '').strip()
    password = request.form.get('contrasena', '').strip()

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE username = %s AND password = %s", (user_id, password))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()

    if resultado:
        rol = resultado[0]
        session['rol'] = rol
        if rol == 'admin':
            return redirect(url_for('admin'))
        elif rol == 'inventario':
            return redirect(url_for('inventario'))
        elif rol == 'cliente':
            session['carrito'] = []  # inicializa carrito vacío
            return redirect(url_for('cliente'))
    else:
        return render_template('LOGIN.html', error="Usuario o contraseña incorrectos")

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    username = request.form.get('usuario', '').strip()
    password = request.form.get('contrasena', '').strip()

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, 'cliente')", (username, password))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('admin.html', productos=productos)

@app.route('/inventario')
def inventario():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('inventario.html', productos=productos)

@app.route('/cliente')
def cliente():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('comprador.html', productos=productos)

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    imagen = request.form['imagen']  # Debe ser solo el nombre del archivo de imagen

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO productos (nombre, descripcion, precio, imagen) VALUES (%s, %s, %s, %s)",
                   (nombre, descripcion, precio, imagen))
    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(request.referrer)

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(request.referrer)

# --------- CARRITO FUNCIONES ---------

@app.route('/agregar_carrito/<int:id>', methods=['POST'])
def agregar_carrito(id):
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()

    if 'carrito' not in session:
        session['carrito'] = []

    carrito = session['carrito']
    carrito.append(producto)
    session['carrito'] = carrito

    return redirect(url_for('cliente'))

@app.route('/ver_carrito')
def ver_carrito():
    carrito = session.get('carrito', [])
    total = sum([float(item['precio']) for item in carrito])
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/eliminar_carrito/<int:id>', methods=['POST'])
def eliminar_carrito(id):
    carrito = session.get('carrito', [])
    carrito = [item for item in carrito if item['id'] != id]
    session['carrito'] = carrito
    return redirect(url_for('ver_carrito'))

@app.route('/pagar_carrito', methods=['POST'])
def pagar_carrito():
    # Lógica de "pago" (ejemplo: limpiar el carrito)
    session['carrito'] = []
    return render_template('pago_exitoso.html')

if __name__ == '__main__':
    app.run(debug=True)
