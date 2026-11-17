import os
import time
import psycopg2
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

DB = dict(
    host=os.getenv("DB_HOST", "db"),
    port=5432,
    dbname=os.getenv("DB_NAME", "formulario"),
    user=os.getenv("DB_USER", "ezequiel"),
    password=os.getenv("DB_PASSWORD", "cambiame"),
)

def init_db():
    # La base puede tardar unos segundos en estar lista: reintentamos
    for _ in range(10):
        try:
            conn = psycopg2.connect(**DB)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    correo TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    creado TIMESTAMP DEFAULT NOW()
                )
            """)
            conn.commit()
            conn.close()
            return
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("No se pudo conectar a la base de datos")

PAGINA = """
<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>Formulario</title>
<style>
  body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; }
  input, textarea { width: 100%; padding: .5rem; margin: .3rem 0 1rem; }
  button { padding: .6rem 1.2rem; }
  li { margin-bottom: .8rem; }
</style></head>
<body>
  <h1>Ezequiel Fernandez Brandon Maldonado</h1>
  <h3>Yo estudio en Yavirac</h3>
  <form method="post" action="/enviar">
    <label>Nombre</label><input name="nombre" required>
    <label>Correo</label><input name="correo" type="email" required>
    <label>Mensaje</label><textarea name="mensaje" rows="3" required></textarea>
    <button type="submit">Enviar</button>
  </form>
  <h2>Mensajes guardados ({{ filas|length }})</h2>
  <ul>
  {% for f in filas %}
    <li><b>{{ f[1] }}</b> ({{ f[2] }}) - {{ f[4].strftime('%d/%m/%Y %H:%M') }}<br>{{ f[3] }}</li>
  {% endfor %}
  </ul>
</body></html>
"""

@app.route("/")
def inicio():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, correo, mensaje, creado FROM mensajes ORDER BY id DESC")
    filas = cur.fetchall()
    conn.close()
    return render_template_string(PAGINA, filas=filas)

@app.route("/enviar", methods=["POST"])
def enviar():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mensajes (nombre, correo, mensaje) VALUES (%s, %s, %s)",
        (request.form["nombre"], request.form["correo"], request.form["mensaje"]),
    )
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
