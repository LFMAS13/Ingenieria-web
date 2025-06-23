import pyodbc

conexion = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=logindb;'
    'UID=sa;'  # Cambia si es otro usuario
    'PWD=tu_contraseña_sql_server'  # Cambia por tu contraseña real
)

cursor = conexion.cursor()
cursor.execute("SELECT * FROM usuarios")
usuarios = cursor.fetchall()

for u in usuarios:
    print(u)

cursor.close()
conexion.close()
