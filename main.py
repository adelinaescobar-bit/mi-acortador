from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import sqlite3
import string
import random

app = FastAPI()

# Configuración de la base de datos


def init_db():
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, short_id TEXT, long_url TEXT)
    """)
    conn.commit()
    conn.close()


init_db()


def generate_short_id(length=5):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@app.get("/")
def home():
    return {"mensaje": "Acortador de URLs activo. Usa /crear?url=TU_URL"}


@app.get("/crear")
def create_url(url: str):
    short_id = generate_short_id()
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO urls (short_id, long_url) VALUES (?, ?)", (short_id, url))
    conn.commit()
    conn.close()
    return {"url_corta": f"/{short_id}", "url_original": url}


@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute("SELECT long_url FROM urls WHERE short_id = ?", (short_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return RedirectResponse(url=result[0])
    raise HTTPException(status_code=404, detail="Link no encontrado")
