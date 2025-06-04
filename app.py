# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="admin",    
        password="admin123", 
        database="logindb"
    )

@app.route('/')
def login():
    return render_template('LOGIN.html')

@app.route('/login', methods=['POST'])
def validar_login():
    user_id = request.form['usuario']
    password = request.form['contrasena']

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE id = %s AND password = %s", (user_id, password))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()

    if resultado:
        rol = resultado[0]
        if rol == 'admin':
            return redirect(url_for('admin'))
        elif rol == 'inventario':
            return redirect(url_for('inventario'))
        elif rol == 'comprador':
            return redirect(url_for('comprador'))
    else:
        return "Credenciales incorrectas"

# Nuevas rutas según el rol
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/inventario')
def inventario():
    return render_template('inventario.html')

@app.route('/comprador')
def comprador():
    return render_template('comprador.html')

if __name__ == '__main__':
    app.run(debug=True)
