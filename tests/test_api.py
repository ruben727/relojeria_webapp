import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

class TestEndpoints:
    
    def test_health_check(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
    
    def test_listar_relojes(self, client):
        response = client.get("/api/relojes")
        assert response.status_code == 200
        assert "total" in response.json()
    
    def test_crear_reloj(self, client):
        reloj = {
            "modelo": "Seiko SKX007",
            "marca": "Seiko",
            "precio": 150.0,
            "stock": 5
        }
        response = client.post("/api/relojes", json=reloj)
        assert response.status_code == 201
        assert "id" in response.json()
    
    def test_listar_reparaciones(self, client):
        response = client.get("/api/reparaciones")
        assert response.status_code == 200
        assert "total" in response.json()
    
    def test_crear_reparacion(self, client):
        reparacion = {
            "cliente": "Juan Pérez",
            "reloj_modelo": "Seiko SKX007",
            "problema": "Batería muerta",
            "costo": 50.0
        }
        response = client.post("/api/reparaciones", json=reparacion)
        assert response.status_code == 201
        assert "id" in response.json()
    
    def test_stats(self, client):
        response = client.get("/api/stats")
        assert response.status_code == 200
        assert "total_relojes" in response.json()
        assert "total_reparaciones" in response.json()
