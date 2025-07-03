from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import stripe

stripe.api_key = "sk_test_51Re5cLPKrgJMbKdVW4Gi1XDpQhkVQdW7FO8DJbneU91KymSujuBa0lIETtj4yn5CNyhHObcB8wH8xyOG1Ty2eNyv00e78KBY6q"


app = Flask(__name__)
app.secret_key = 'acetato'  # Clave secreta para sesiones

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="acetato131962",
        database="logindb"
    )

# Decoradores para manejo de sesión y roles
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('rol') not in roles:
                return "Acceso denegado", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ------ Landing Page (raíz "/") ------
@app.route('/')
def landing():
    return render_template('landing.html')

# ------ Login ------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('usuario', '').strip()
        password = request.form.get('contrasena', '').strip()

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password_hash, rol FROM usuarios WHERE username = %s", (user_id,))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado and check_password_hash(resultado['password_hash'], password):
            session['rol'] = resultado['rol']
            session['username'] = resultado['username']
            session['user_id'] = resultado['id']

            if resultado['rol'] == 'admin':
                return redirect(url_for('admin'))
            elif resultado['rol'] == 'inventario':
                return redirect(url_for('inventario'))
            elif resultado['rol'] == 'cliente':
                session['carrito'] = []
                return redirect(url_for('cliente'))
        else:
            return render_template('LOGIN.html', error="Usuario o contraseña incorrectos")
    
    return render_template('LOGIN.html')

# ------ Registro ------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('usuario', '').strip()
        password = request.form.get('contrasena', '').strip()
        rol = request.form.get('rol', 'cliente')  # Por defecto 'cliente' si no se envía rol
        password_hash = generate_password_hash(password)

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()
            conexion.close()
            return render_template('registro.html', error="El nombre de usuario ya existe, elige otro.")

        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (username, password_hash, rol) VALUES (%s, %s, %s)",
                       (username, password_hash, rol))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('login'))
    else:
        return render_template('registro.html')


# ------ Logout ------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------ Vistas protegidas ------
@app.route('/admin')
@login_required
@role_required(['admin'])
def admin():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('admin.html', productos=productos)

@app.route('/inventario')
@login_required
@role_required(['inventario'])
def inventario():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('inventario.html', productos=productos)

@app.route('/cliente')
@login_required
@role_required(['cliente'])
def cliente():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('comprador.html', productos=productos)

# ------ CRUD Productos ------
@app.route('/agregar_producto', methods=['POST'])
@login_required
@role_required(['admin', 'inventario'])
def agregar_producto():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    imagen = request.form['imagen']

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO productos (nombre, descripcion, precio, imagen) VALUES (%s, %s, %s, %s)",
                   (nombre, descripcion, precio, imagen))
    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(request.referrer)

@app.route('/eliminar_producto/<int:id>')
@login_required
@role_required(['admin', 'inventario'])
def eliminar_producto(id):
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(request.referrer)

# --- Carrito Cliente ---

@app.route('/agregar_carrito/<int:id>', methods=['POST'])
@login_required
@role_required(['cliente'])
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
@login_required
@role_required(['cliente'])
def ver_carrito():
    carrito = session.get('carrito', [])
    total = sum(float(item['precio']) for item in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/eliminar_carrito/<int:id>', methods=['POST'])
@login_required
@role_required(['cliente'])
def eliminar_carrito(id):
    carrito = session.get('carrito', [])
    carrito = [item for item in carrito if item['id'] != id]
    session['carrito'] = carrito
    return redirect(url_for('ver_carrito'))

# --- Pagar carrito, con direcciones y tarjetas ---

@app.route('/pagar_carrito', methods=['POST'])
@login_required
@role_required(['cliente'])
def pagar_carrito():
    usuario_id = session['user_id']
    carrito = session.get('carrito', [])

    if not carrito:
        return redirect(url_for('cliente'))

    direccion_id = request.form.get('direccion_id')
    tarjeta_id = request.form.get('tarjeta_id')

    if not direccion_id or not tarjeta_id:
        return "Debes seleccionar dirección y tarjeta para pagar", 400

    total = sum(float(item['precio']) for item in carrito)

    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO compras (usuario_id, total, estatus, direccion_id, tarjeta_id) 
        VALUES (%s, %s, 'Pagada', %s, %s)
    """, (usuario_id, total, direccion_id, tarjeta_id))
    compra_id = cursor.lastrowid

    for item in carrito:
        cursor.execute("""
            INSERT INTO detalle_compras (compra_id, producto_id, cantidad, precio) 
            VALUES (%s, %s, %s, %s)
        """, (compra_id, item['id'], 1, item['precio']))

    conexion.commit()
    cursor.close()
    conexion.close()

    session['carrito'] = []

    return render_template('pago_exitoso.html', compra_id=compra_id)

@app.route('/crear_checkout', methods=['POST'])
@login_required
@role_required(['cliente'])
def crear_checkout():
    carrito = session.get('carrito', [])
    if not carrito:
        return redirect(url_for('cliente'))

    line_items = []
    for item in carrito:
        line_items.append({
            'price_data': {
                'currency': 'mxn',
                'product_data': {
                    'name': item['nombre'],
                },
                'unit_amount': int(float(item['precio']) * 100),  # en centavos
            },
            'quantity': 1,
        })

    session_stripe = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://localhost:5000/pago_exitoso_stripe',
        cancel_url='http://localhost:5000/ver_carrito',
    )
    return redirect(session_stripe.url, code=303)

@app.route('/pago_exitoso_stripe')
@login_required
@role_required(['cliente'])
def pago_exitoso_stripe():
    usuario_id = session['user_id']
    carrito = session.get('carrito', [])

    total = sum(float(item['precio']) for item in carrito)

    conexion = conectar_db()
    cursor = conexion.cursor()

    # Puedes poner valores dummy en direccion_id y tarjeta_id si no se usan con Stripe
    cursor.execute("""
        INSERT INTO compras (usuario_id, total, estatus, direccion_id, tarjeta_id) 
        VALUES (%s, %s, 'Pagada', NULL, NULL)
    """, (usuario_id, total))
    compra_id = cursor.lastrowid

    for item in carrito:
        cursor.execute("""
            INSERT INTO detalle_compras (compra_id, producto_id, cantidad, precio) 
            VALUES (%s, %s, %s, %s)
        """, (compra_id, item['id'], 1, item['precio']))

    conexion.commit()
    cursor.close()
    conexion.close()

    session['carrito'] = []

    return render_template('pago_exitoso.html', compra_id=compra_id)


# --- Direcciones ---

@app.route('/direcciones', methods=['GET', 'POST'])
@login_required
@role_required(['cliente'])
def direcciones():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    usuario_id = session['user_id']

    if request.method == 'POST':
        direccion = request.form['direccion']
        ciudad = request.form['ciudad']
        estado = request.form['estado']
        codigo_postal = request.form['codigo_postal']

        cursor.execute("""
            INSERT INTO direcciones (usuario_id, direccion, ciudad, estado, codigo_postal) 
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, direccion, ciudad, estado, codigo_postal))
        conexion.commit()

    cursor.execute("SELECT * FROM direcciones WHERE usuario_id = %s", (usuario_id,))
    direcciones = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template('direcciones.html', direcciones=direcciones)

# --- Tarjetas ---

@app.route('/tarjetas', methods=['GET', 'POST'])
@login_required
@role_required(['cliente'])
def tarjetas():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    usuario_id = session['user_id']

    if request.method == 'POST':
        numero = request.form['numero']
        nombre_titular = request.form['nombre_titular']
        fecha_expiracion = request.form['fecha_expiracion']
        cvv = request.form['cvv']

        cursor.execute("""
            INSERT INTO tarjetas (usuario_id, numero, nombre_titular, fecha_expiracion, cvv) 
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, numero, nombre_titular, fecha_expiracion, cvv))
        conexion.commit()

    cursor.execute("SELECT * FROM tarjetas WHERE usuario_id = %s", (usuario_id,))
    tarjetas = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template('tarjetas.html', tarjetas=tarjetas)

# --- Calificar producto ---

@app.route('/calificar/<int:producto_id>', methods=['GET', 'POST'])
@login_required
@role_required(['cliente'])
def calificar(producto_id):
    usuario_id = session['user_id']
    if request.method == 'POST':
        calificacion = int(request.form['calificacion'])
        comentario = request.form['comentario']

        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO calificaciones (usuario_id, producto_id, calificacion, comentario) 
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, producto_id, calificacion, comentario))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('cliente'))
    return render_template('calificar.html', producto_id=producto_id)

# --- Recomendaciones ---

@app.route('/recomendaciones', methods=['GET', 'POST'])
@login_required
@role_required(['cliente'])
def recomendaciones():
    usuario_id = session['user_id']

    if request.method == 'POST':
        texto = request.form['texto']
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO recomendaciones (usuario_id, texto) VALUES (%s, %s)", (usuario_id, texto))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('cliente'))

    return render_template('recomendaciones.html')

@app.route('/admin/pedidos')
@login_required
@role_required(['admin'])
def admin_pedidos():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.id, c.total, c.estatus, c.fecha_compra, u.username
        FROM compras c
        JOIN usuarios u ON c.usuario_id = u.id
        ORDER BY c.fecha_compra DESC
    """)
    pedidos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('admin_pedidos.html', pedidos=pedidos)


if __name__ == '__main__':
    app.run(debug=True)
    
    