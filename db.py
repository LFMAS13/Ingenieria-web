import mysql.connector

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="tu_usuario_mysql",
    password="tu_contraseña_mysql",
    database="logindb"
)

cursor = conexion.cursor()

# Solo para prueba: leer todos los usuarios
cursor.execute("SELECT * FROM usuarios")
usuarios = cursor.fetchall()

for u in usuarios:
    print(u)

# Cierra la conexión
cursor.close()
conexion.close()
