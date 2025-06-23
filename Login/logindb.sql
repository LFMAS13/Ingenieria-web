-- Crear la base de datos si no existe
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'logindb')
BEGIN
    CREATE DATABASE logindb;
END
GO

USE logindb;
GO

-- Eliminar la tabla si existe
IF OBJECT_ID('usuarios', 'U') IS NOT NULL
BEGIN
    DROP TABLE usuarios;
END
GO

-- Crear la tabla 'usuarios'
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('admin', 'inventario', 'cliente'))
);
GO

-- Insertar usuarios de prueba
INSERT INTO usuarios (username, password, rol) VALUES ('admin', 'admin123', 'admin');
INSERT INTO usuarios (username, password, rol) VALUES ('inventario', 'inventario123', 'inventario');
GO
