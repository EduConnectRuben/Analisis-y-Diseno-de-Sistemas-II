from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permisos para que Netlify pueda entrar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://pd8_db_user:9LmN3qxtlJC969WX8yeUq7BRmkgr68sV@dpg-d73srcua2pns73acu8qg-a.oregon-postgres.render.com/pd8_db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Usuario(BaseModel):
    email: str
    password: str

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# ESTO QUITARÁ EL "NOT FOUND"
@app.get("/")
def inicio():
    return {"mensaje": "¡Servidor PD8 funcionando correctamente!"}

@app.on_event("startup")
def startup():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY, email TEXT UNIQUE, password TEXT);")
    conn.commit()
    conn.close()

@app.post("/registro")
async def registro(user: Usuario):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        hashed = pwd_context.hash(user.password)
        cursor.execute("INSERT INTO usuarios (email, password) VALUES (%s, %s)", (user.email, hashed))
        conn.commit()
        conn.close()
        return {"mensaje": "Usuario registrado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

@app.post("/login")
async def login(user: Usuario):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM usuarios WHERE email=%s", (user.email,))
    result = cursor.fetchone()
    conn.close()
    if result and pwd_context.verify(user.password, result[0]):
        return {"mensaje": "Login exitoso"}
    raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")