CREATE DATABASE IF NOT EXISTS logindb;
USE logindb;

CREATE TABLE usuarios (
    id VARCHAR(50) PRIMARY KEY,  -- id será el nombre de usuario
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'inventario', 'comprador') NOT NULL
);

INSERT INTO usuarios (id, password, rol) VALUES ('admin', 'admin123', 'admin');
INSERT INTO usuarios (id, password, rol) VALUES ('inventario', 'inventario123', 'inventario');
INSERT INTO usuarios (id, password, rol) VALUES ('comprador', 'comprador123', 'comprador');
