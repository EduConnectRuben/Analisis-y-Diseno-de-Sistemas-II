CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email TEXT,
    password TEXT,
    rol TEXT
);

CREATE TABLE denuncias (
    id SERIAL PRIMARY KEY,
    nombre TEXT,
    ci TEXT,
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);