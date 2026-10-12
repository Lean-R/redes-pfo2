import sqlite3

from flask import Flask, jsonify, render_template_string, request
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

    # crear tabla para tareas
    conexion.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                completada INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
    conexion.commit()
    conexion.close()


# funcion auxiliar para buscar un usuario en la DB a partir de su nombre de usuario
def buscar_usuario(nombre):
    conexion = sqlite3.connect(BASE)
    fila = conexion.execute(
        "SELECT id FROM usuarios WHERE usuario = ?", (nombre,)
    ).fetchone()

    conexion.close()
    return fila[0] if fila else None


# endpoint para crear un usuario
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


# ruta base para mostrar el HTML
@app.route("/tareas")
def tareas():
    return render_template_string("""
            <h1>Bienvenido al gestor de tareas</h1>
            <p>La API  está funcionando</p>
            <p>Se pueden obtener las tareas con <code>GET /api/tareas?usuario=nombre_usuario</code></p>
        """)


# endpoint para crear una tarea
@app.route("/api/tareas", methods=["POST"])
def crear_tarea():
    datos = request.get_json()
    usuario_id = buscar_usuario(datos.get("usuario"))
    if usuario_id is None:
        return jsonify({"error": "usuario inexistente"}), 400

    conexion = sqlite3.connect(BASE)
    cursor = conexion.execute(
        "INSERT INTO tareas (usuario_id, titulo) VALUES (?, ?)",
        (usuario_id, datos["titulo"]),
    )
    conexion.commit()
    conexion.close()

    return jsonify({"mensaje": "tarea creada", "id": cursor.lastrowid}), 201


# endpoint para obtener tareas
@app.route("/api/tareas", methods=["GET"])
def obtener_tareas():
    usuario_id = buscar_usuario(request.args.get("usuario"))
    if usuario_id is None:
        return jsonify({"error": "usuario inexistente"}), 404

    conexion = sqlite3.connect(BASE)
    filas = conexion.execute(
        "SELECT id, titulo, completada FROM tareas WHERE usuario_id = ? ORDER BY id",
        (usuario_id,),
    ).fetchall()
    conexion.close()

    tareas = [{"id": f[0], "titulo": f[1], "completada": bool(f[2])} for f in filas]

    return jsonify(tareas)


# endpoint para marcar una tarea como completada
@app.route("/api/tareas/<int:id>", methods=["PUT"])
def completar_tarea(id):
    datos = request.get_json()
    usuario_id = buscar_usuario(datos.get("usuario"))
    if usuario_id is None:
        return jsonify({"error": "usuario inexistente"}), 404

    conexion = sqlite3.connect(BASE)
    cursor = conexion.execute(
        "UPDATE tareas SET completada = 1 WHERE id = ? AND usuario_id = ?",
        (id, usuario_id),
    )
    conexion.commit()
    conexion.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "tarea no encontrada"}), 404

    return jsonify({"mensaje": "tarea completada"})


# endpoint para borrar una tarea
@app.route("/api/tareas/<int:id>", methods=["DELETE"])
def borrar_tarea(id):
    datos = request.get_json()
    usuario_id = buscar_usuario(datos.get("usuario"))

    if usuario_id is None:
        return jsonify({"error": "usuario inexistente"}), 404

    conexion = sqlite3.connect(BASE)
    cursor = conexion.execute(
        "DELETE FROM tareas WHERE id = ? AND usuario_id = ?", (id, usuario_id)
    )
    conexion.commit()
    conexion.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "tarea no encontrada"}), 404

    return jsonify({"mensaje": "tarea borrada"})


if __name__ == "__main__":
    iniciar_db()
    app.run(debug=True)
