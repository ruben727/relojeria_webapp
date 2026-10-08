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
    
    def test_relojes_premium(self, client):
        reloj = {
            "modelo": "Rolex Submariner",
            "marca": "Rolex",
            "precio": 9500.0,
            "stock": 1
        }
        client.post("/api/relojes", json=reloj)
        response = client.get("/api/relojes/premium")
        assert response.status_code == 200
        data = response.json()["data"]
        assert any(r["modelo"] == "Rolex Submariner" for r in data)
        assert all(r["precio"] >= 1000 for r in data)

    def test_reparacion_costosa(self, client):
        reparacion = {
            "cliente": "Ana López",
            "reloj_modelo": "Omega Speedmaster",
            "problema": "Servicio completo",
            "costo": 99999.0
        }
        client.post("/api/reparaciones", json=reparacion)
        response = client.get("/api/reparaciones/costosa")
        assert response.status_code == 200
        assert response.json()["data"]["costo"] >= 99999.0

    def test_reparacion_costosa_sin_datos(self, client, tmp_path, monkeypatch):
        import app.main as main
        monkeypatch.setattr(main, "DB_PATH", tmp_path / "vacia.db")
        main.init_db()
        response = client.get("/api/reparaciones/costosa")
        assert response.status_code == 404

    def test_stats(self, client):
        response = client.get("/api/stats")
        assert response.status_code == 200
        assert "total_relojes" in response.json()
        assert "total_reparaciones" in response.json()
