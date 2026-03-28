from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔓 CORS (IMPORTANTE para Netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 TU DATABASE URL (la de Render)
DATABASE_URL = "DATABASE_URL = "postgresql://pd8_db_user:xxxxx@dpg-xxxx.oregon-postgres.render.com/pd8_db"

# 🔐 Seguridad
SECRET = "CLAVE_SUPER_SECRETA"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📦 MODELOS
class Usuario(BaseModel):
    email: str
    password: str

# 🚀 CREAR TABLAS AUTOMÁTICAMENTE
def crear_tablas():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE,
        password TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS denuncias (
        id SERIAL PRIMARY KEY,
        nombre TEXT,
        ci TEXT,
        descripcion TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

crear_tablas()

# 🌐 RUTA BASE
@app.get("/")
def root():
    return {"mensaje": "API funcionando correctamente"}

# 📝 REGISTRO
@app.post("/registro")
def registrar(usuario: Usuario):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Verificar si ya existe
    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (usuario.email,))
    existente = cursor.fetchone()

    if existente:
        conn.close()
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    # Encriptar contraseña
    hashed_password = pwd_context.hash(usuario.password)

    cursor.execute(
        "INSERT INTO usuarios (email, password) VALUES (%s, %s)",
        (usuario.email, hashed_password)
    )

    conn.commit()
    conn.close()

    return {"mensaje": "Usuario registrado correctamente"}

# 🔑 LOGIN
@app.post("/login")
def login(usuario: Usuario):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (usuario.email,))
    user = cursor.fetchone()

    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="Usuario no existe")

    # user[2] = password
    if not pwd_context.verify(usuario.password, user[2]):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    # Crear token
    token = jwt.encode(
        {
            "sub": usuario.email,
            "exp": datetime.utcnow() + timedelta(hours=2)
        },
        SECRET,
        algorithm="HS256"
    )

    return {
        "mensaje": "Login exitoso",
        "token": token
    }

# 📌 CREAR DENUNCIA
@app.post("/denuncia")
def crear_denuncia(denuncia: dict):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO denuncias (nombre, ci, descripcion)
        VALUES (%s, %s, %s)
    """, (
        denuncia.get("nombre"),
        denuncia.get("ci"),
        denuncia.get("descripcion")
    ))

    conn.commit()
    conn.close()

    return {"mensaje": "Denuncia registrada"}

# 📋 VER DENUNCIAS
@app.get("/denuncias")
def ver_denuncias():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM denuncias")
    datos = cursor.fetchall()

    conn.close()

    return {"denuncias": datos}