from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()

DATABASE_URL = "postgresql://pd8_db_user:9LmN3qxtlJC969WX8yeUq7BRmkgr68sV@dpg-d73srcua2pns73acu8qg-a/pd8_db"
SECRET = "CLAVE_SUPER_SECRETA"

@app.on_event("startup")
def crear_tablas():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        email TEXT,
        password TEXT,
        rol TEXT
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Usuario(BaseModel):
    email: str
    password: str

class Denuncia(BaseModel):
    nombre: str
    ci: str
    descripcion: str

@app.post("/registro")
def registro(user: Usuario):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    hash_pass = pwd_context.hash(user.password)

    cursor.execute(
        "INSERT INTO usuarios (email, password, rol) VALUES (%s,%s,'admin')",
        (user.email, hash_pass)
    )

    conn.commit()
    conn.close()

    return {"msg": "Usuario creado"}

@app.post("/login")
def login(user: Usuario):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT password, rol FROM usuarios WHERE email=%s", (user.email,))
    result = cursor.fetchone()

    if not result or not pwd_context.verify(user.password, result[0]):
        raise HTTPException(status_code=401, detail="Error")

    token = jwt.encode({
        "sub": user.email,
        "rol": result[1],
        "exp": datetime.utcnow() + timedelta(hours=2)
    }, SECRET)

    return {"token": token, "rol": result[1]}

@app.post("/denuncias")
def crear(d: Denuncia):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO denuncias (nombre, ci, descripcion) VALUES (%s,%s,%s)",
        (d.nombre, d.ci, d.descripcion)
    )

    conn.commit()
    conn.close()

    return {"msg": "Guardado"}

@app.get("/denuncias")
def listar():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM denuncias")
    data = cursor.fetchall()

    conn.close()

    return data
