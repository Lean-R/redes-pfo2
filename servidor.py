from flask import Flask, jsonify, request

# Crear el servidor
app = Flask(__name__)


@app.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json()
    return jsonify({"mensaje": "registro recibido", "datos": datos}), 201


@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json()
    return jsonify({"mensaje": "login recibido", "datos": datos})


if __name__ == "__main__":
    app.run(debug=True)
