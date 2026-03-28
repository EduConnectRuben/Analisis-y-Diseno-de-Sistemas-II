from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ AQUÍ VA LA URL QUE MOSTRASTE EN TU CAPTURA
DATABASE_URL = "postgresql://pd8_db_user:9LmN3qxtlJC969WX8yeUq7BRmkgr68sV@dpg-d73srcua2pns73acu8qg-a.oregon-postgres.render.com/pd8_db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Usuario(BaseModel):
    email: str
    password: str

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.on_event("startup")
def startup():
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
    conn.close()

@app.post("/registro")
def registro(user: Usuario):
    conn = get_conn()
    cursor = conn.cursor()
    hashed = pwd_context.hash(user.password)
    try:
        cursor.execute("INSERT INTO usuarios (email, password) VALUES (%s, %s)", (user.email, hashed))
        conn.commit()
        return {"mensaje": "registrado"}
    except:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    finally:
        conn.close()

@app.post("/login")
def login(user: Usuario):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM usuarios WHERE email=%s", (user.email,))
    result = cursor.fetchone()
    conn.close()
    if not result or not pwd_context.verify(user.password, result[0]):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    return {"mensaje": "ok"}