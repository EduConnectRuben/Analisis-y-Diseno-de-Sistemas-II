from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Permisos totales para evitar errores de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TU URL DE BASE DE DATOS (Asegúrate que sea la EXTERNAL si pruebas desde fuera, o esta si es en Render)
DATABASE_URL = "postgresql://pd8_db_user:9LmN3qxtlJC969WX8yeUq7BRmkgr68sV@dpg-d73srcua2pns73acu8qg-a.oregon-postgres.render.com/pd8_db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Usuario(BaseModel):
    email: str
    password: str

def get_conn():
    # Retorna la conexión a la base de datos
    return psycopg2.connect(DATABASE_URL)

@app.get("/")
def home():
    return {"status": "Servidor funcionando correctamente"}

@app.on_event("startup")
def startup():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE,
                password TEXT
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Base de datos conectada y tabla lista")
    except Exception as e:
        print(f"ERROR conectando a la base de datos: {e}")

@app.post("/registro")
async def registro(user: Usuario):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        hashed_password = pwd_context.hash(user.password)
        cursor.execute("INSERT INTO usuarios (email, password) VALUES (%s, %s)", (user.email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Usuario registrado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.post("/login")
async def login(user: Usuario):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM usuarios WHERE email=%s", (user.email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and pwd_context.verify(user.password, result[0]):
            return {"mensaje": "Login exitoso"}
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))