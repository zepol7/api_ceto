import json
import pytest
from app import app, tareas


@pytest.fixture
def client():
    app.config["TESTING"] = True
    tareas.clear()
    tareas.extend([
        {"id": 1, "titulo": "Tarea A", "completada": False},
        {"id": 2, "titulo": "Tarea B", "completada": True},
    ])
    with app.test_client() as c:
        yield c


class TestInicio:
    def test_retorna_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_contiene_mensaje(self, client):
        data = json.loads(client.get("/").data)
        assert "mensaje" in data


class TestSalud:
    def test_health_check(self, client):
        r = client.get("/salud")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["estado"] == "OK"


class TestTareas:
    def test_obtener_todas(self, client):
        r = client.get("/tareas")
        data = json.loads(r.data)
        assert len(data) == 2

    def test_filtrar_completadas(self, client):
        r = client.get("/tareas?completadas=true")
        data = json.loads(r.data)
        assert all(t["completada"] for t in data)

    def test_filtrar_pendientes(self, client):
        r = client.get("/tareas?completadas=false")
        data = json.loads(r.data)
        assert all(not t["completada"] for t in data)

    def test_obtener_por_id(self, client):
        r = client.get("/tareas/1")
        assert r.status_code == 200

    def test_id_inexistente_retorna_404(self, client):
        r = client.get("/tareas/999")
        assert r.status_code == 404

    def test_crear_tarea(self, client):
        r = client.post("/tareas", json={"titulo": "Nueva tarea"})
        assert r.status_code == 201
        data = json.loads(r.data)
        assert data["titulo"] == "Nueva tarea"

    def test_crear_sin_titulo_retorna_400(self, client):
        r = client.post("/tareas", json={})
        assert r.status_code == 400