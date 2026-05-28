from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# "Base de datos" en memoria
tareas = [
    {"id": 1, "titulo": "Aprender Docker", "completada": False},
    {"id": 2, "titulo": "Configurar Jenkins", "completada": True},
    {"id": 3, "titulo": "Escribir pruebas", "completada": False},
]
siguiente_id = 4


@app.route("/")
def inicio():
    return jsonify({
        "mensaje": "API de Tareas funcionando en Docker",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/salud")
def salud():
    """Endpoint de health check para Docker."""
    return jsonify({"estado": "OK", "servicio": "api-tareas"}), 200


@app.route("/tareas", methods=["GET"])
def obtener_tareas():
    completadas = request.args.get("completadas")
    if completadas == "true":
        resultado = [t for t in tareas if t["completada"]]
    elif completadas == "false":
        resultado = [t for t in tareas if not t["completada"]]
    else:
        resultado = tareas
    return jsonify(resultado)


@app.route("/tareas/<int:tarea_id>", methods=["GET"])
def obtener_tarea(tarea_id: int):
    tarea = next((t for t in tareas if t["id"] == tarea_id), None)
    if tarea is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify(tarea)


@app.route("/tareas", methods=["POST"])
def crear_tarea():
    global siguiente_id
    data = request.get_json()
    if not data or "titulo" not in data:
        return jsonify({"error": "El campo 'titulo' es requerido"}), 400

    nueva_tarea = {
        "id": siguiente_id,
        "titulo": data["titulo"],
        "completada": data.get("completada", False)
    }
    tareas.append(nueva_tarea)
    siguiente_id += 1
    return jsonify(nueva_tarea), 201


@app.route("/tareas/<int:tarea_id>", methods=["PATCH"])
def actualizar_tarea(tarea_id: int):
    tarea = next((t for t in tareas if t["id"] == tarea_id), None)
    if tarea is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    data = request.get_json()
    if "completada" in data:
        tarea["completada"] = data["completada"]
    if "titulo" in data:
        tarea["titulo"] = data["titulo"]
    return jsonify(tarea)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)