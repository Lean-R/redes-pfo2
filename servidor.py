import sqlite3

from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

# Crear el servidor
app = Flask(__name__)

# definir nombre de base de datos como constante
BASE = "tareas.db"


def iniciar_db():
    conexion = sqlite3.connect(BASE)
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contraseña_hash TEXT NOT NULL
        )
        """)
    conexion.commit()
    conexion.close()


@app.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json()
    usuario = datos["usuario"]
    contraseña = datos["contraseña"]

    hash = generate_password_hash(contraseña)

    conexion = sqlite3.connect(BASE)
    try:
        conexion.execute(
            "INSERT INTO usuarios (usuario, contraseña_hash) VALUES (?, ?)",
            (usuario, hash),
        )
        conexion.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "el usuario ya existe"}), 400
    finally:
        conexion.close()

    return jsonify(
        {
            "mensaje": "usuario registrado",
        }
    ), 201


@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json()
    usuario = datos["usuario"]
    contraseña = datos["contraseña"]

    conexion = sqlite3.connect(BASE)
    fila = conexion.execute(
        "SELECT contraseña_hash FROM usuarios WHERE usuario = ?", (usuario,)
    ).fetchone()

    conexion.close()

    if fila is None or not check_password_hash(fila[0], contraseña):
        return jsonify({"error": "credenciales inválidas"}), 401

    return jsonify({"mensaje": "sesion iniciada"})


if __name__ == "__main__":
    iniciar_db()
    app.run(debug=True)
