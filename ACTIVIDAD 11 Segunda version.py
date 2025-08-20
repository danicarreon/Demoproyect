from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
import re
import uuid
import time

app = Flask(__name__)

# Simulación de base de datos en memoria
usuarios = {}
tokens = {"admin_token": "admin"}  # Token de ejemplo para autenticación


# ------------------------------
# Funciones auxiliares
# ------------------------------
def validar_email(email):
    """Valida que el email tenga un formato correcto."""
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email)


def generar_id():
    """Genera un ID único para cada usuario."""
    return str(uuid.uuid4())


def requiere_token(f):
    """Decorador para requerir token de autenticación."""
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify(error="No se envio token de autenticacion"), 401
        if token not in tokens:
            return jsonify(error="Token inválido"), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


# ------------------------------
# Endpoints
# ------------------------------

@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    """Crea un nuevo usuario."""
    datos = request.get_json()

    # Validar datos
    if not datos or "nombre" not in datos or "email" not in datos:
        return jsonify(error="Datos incompletos"), 400

    nombre = datos["nombre"].strip()
    email = datos["email"].strip()

    if not validar_email(email):
        return jsonify(error="Formato de email inválido"), 422

    # Verificar duplicado
    if email in [u["email"] for u in usuarios.values()]:
        return jsonify(error="Usuario con ese email ya existe"), 409

    # Crear usuario
    user_id = generar_id()
    usuarios[user_id] = {"id": user_id, "nombre": nombre, "email": email}

    return jsonify(mensaje="Usuario creado correctamente", usuario=usuarios[user_id]), 201


@app.route("/usuarios/<user_id>", methods=["GET"])
@requiere_token
def obtener_usuario(user_id):
    """Obtiene datos de un usuario."""
    if user_id not in usuarios:
        return jsonify(error="Usuario no encontrado"), 404
    return jsonify(usuarios[user_id]), 200


@app.route("/usuarios/<user_id>", methods=["PUT"])
@requiere_token
def actualizar_usuario(user_id):
    """Actualiza los datos de un usuario."""
    if user_id not in usuarios:
        return jsonify(error="Usuario no encontrado"), 404

    datos = request.get_json()
    if not datos:
        return jsonify(error="Datos incompletos"), 400

    if "email" in datos and not validar_email(datos["email"]):
        return jsonify(error="Formato de email inválido"), 422

    usuarios[user_id].update(datos)
    return jsonify(mensaje="Usuario actualizado correctamente", usuario=usuarios[user_id]), 200


@app.route("/usuarios/<user_id>", methods=["DELETE"])
@requiere_token
def eliminar_usuario(user_id):
    """Elimina un usuario."""
    if user_id not in usuarios:
        return jsonify(error="Usuario no encontrado"), 404

    del usuarios[user_id]
    return jsonify(mensaje="Usuario eliminado correctamente"), 200


@app.route("/prohibido", methods=["GET"])
def recurso_prohibido():
    """Simula acceso prohibido."""
    return jsonify(error="No tienes permisos para acceder a este recurso"), 403


@app.route("/solo_get", methods=["GET"])
def solo_get():
    """Este endpoint solo permite GET."""
    return jsonify(mensaje="Método permitido"), 200


# ------------------------------
# Manejo de errores personalizados
# ------------------------------

@app.errorhandler(405)
def metodo_no_permitido(e):
    return jsonify(error="Método HTTP no permitido en este endpoint"), 405


@app.errorhandler(500)
def error_interno(e):
    return jsonify(error="Error interno del servidor"), 500


@app.route("/error_interno", methods=["GET"])
def forzar_error():
    """Fuerza un error 500."""
    raise Exception("Error simulado en el servidor")


@app.route("/servicio_no_disponible", methods=["GET"])
def servicio_no_disponible():
    """Simula un servicio fuera de línea."""
    time.sleep(2)  # Retraso simulado
    return jsonify(error="Servicio no disponible temporalmente"), 503


# ------------------------------
# Ejecutar servidor
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
