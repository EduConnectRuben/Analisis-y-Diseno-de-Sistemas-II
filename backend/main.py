from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔥 IMPORTANTE: CORS para Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 TU URL DE RENDER (REEMPLAZA SI ES NECESARIO)
DATABASE_URL = "postgresql://pd8_db_user:9LmN3qxtlJC969WX8yeUq7BRmkgr68sV@dpg-d73srcua2pns73acu8qg-a.oregon-postgres.render.com/pd8_db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📦 MODELOS
class Usuario(BaseModel):
    email: str
    password: str

class Denuncia(BaseModel):
    nombre: str
    ci: str
    descripcion: str

# 🔌 CONEXIÓN BD
def get_conn():
    return psycopg2.connect(DATABASE_URL)

# 🧱 CREAR TABLAS AUTOMÁTICAMENTE
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS denuncias (
        id SERIAL PRIMARY KEY,
        nombre TEXT,
        ci TEXT,
        descripcion TEXT
    );
    """)

    conn.commit()
    conn.close()

# 📝 REGISTRO
@app.post("/registro")
def registro(user: Usuario):
    conn = get_conn()
    cursor = conn.cursor()

    hashed_password = pwd_context.hash(user.password)

    try:
        cursor.execute(
            "INSERT INTO usuarios (email, password) VALUES (%s, %s)",
            (user.email, hashed_password)
        )
        conn.commit()
        return {"mensaje": "Usuario registrado"}
    except:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    finally:
        conn.close()

# 🔐 LOGIN
@app.post("/login")
def login(user: Usuario):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM usuarios WHERE email=%s",
        (user.email,)
    )
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    if not pwd_context.verify(user.password, result[0]):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    return {"mensaje": "Login exitoso"}

# 📌 CREAR DENUNCIA
@app.post("/denuncias")
def crear_denuncia(d: Denuncia):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO denuncias (nombre, ci, descripcion) VALUES (%s, %s, %s)",
        (d.nombre, d.ci, d.descripcion)
    )

    conn.commit()
    conn.close()

    return {"mensaje": "Denuncia creada"}

# 📄 LISTAR DENUNCIAS
@app.get("/denuncias")
def listar_denuncias():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM denuncias")
    datos = cursor.fetchall()

    conn.close()

    return datos


