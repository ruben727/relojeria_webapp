"""
Endpoints de Sistema y Salud
5+ endpoints para monitoreo y estadísticas
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import sqlite3
from pathlib import Path
from app.models import HealthResponse, StatsResponse

router = APIRouter(prefix="/api", tags=["Sistema"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "relojeria.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# ENDPOINTS DE SALUD
# ============================================================================

@router.get("/health", response_model=HealthResponse, summary="Health Check")
def health_check():
    """
    Verifica que la API esté operacional.
    Retorna estado general del servicio.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        database="sqlite3"
    )


@router.get("/health/db", response_model=dict, summary="Health Check BD")
def health_check_db():
    """
    Verifica que la base de datos esté accessible.
    Realiza una consulta de prueba a la BD.
    """
    try:
        conn = get_db()
        result = conn.execute("SELECT 1").fetchone()
        conn.close()
        
        return {
            "statusCode": 200,
            "status": "database_ok",
            "timestamp": datetime.now().isoformat(),
            "message": "Base de datos operacional"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "status": "database_error",
            "timestamp": datetime.now().isoformat(),
            "message": str(e)
        }


# ============================================================================
# ENDPOINTS DE INFORMACIÓN
# ============================================================================

@router.get("/version", response_model=dict, summary="Versión de la API")
def get_version():
    """Retorna la versión actual de la API."""
    return {
        "statusCode": 200,
        "version": "1.0.0",
        "api_name": "API Relojería",
        "description": "Web App de una relojería para práctica de DevOps y Docker",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# ENDPOINTS DE ESTADÍSTICAS
# ============================================================================

@router.get("/stats", response_model=StatsResponse, summary="Estadísticas generales")
def estadisticas_generales():
    """
    Obtiene estadísticas generales de la API.
    Incluye resumen de relojes, reparaciones y clientes.
    """
    conn = get_db()
    
    total_relojes = conn.execute("SELECT COUNT(*) as count FROM relojes WHERE activo = 1").fetchone()
    total_reparaciones = conn.execute("SELECT COUNT(*) as count FROM reparaciones WHERE activo = 1").fetchone()
    total_clientes = conn.execute("SELECT COUNT(*) as count FROM clientes WHERE activo = 1").fetchone()
    
    reparaciones_pendientes = conn.execute(
        "SELECT COUNT(*) as count FROM reparaciones WHERE estado IN ('Recibido', 'En proceso') AND activo = 1"
    ).fetchone()
    
    reparaciones_completadas = conn.execute(
        "SELECT COUNT(*) as count FROM reparaciones WHERE estado IN ('Terminado', 'Entregado') AND activo = 1"
    ).fetchone()
    
    conn.close()
    
    return StatsResponse(
        total_relojes=total_relojes["count"],
        total_reparaciones=total_reparaciones["count"],
        total_clientes=total_clientes["count"],
        reparaciones_pendientes=reparaciones_pendientes["count"],
        reparaciones_completadas=reparaciones_completadas["count"]
    )


@router.get("/stats/detallado", response_model=dict, summary="Estadísticas detalladas")
def estadisticas_detalladas():
    """
    Obtiene estadísticas detalladas y métricas de rendimiento.
    Incluye información por categoría, marca, etc.
    """
    conn = get_db()
    
    # Relojes por categoría
    relojes_por_cat = conn.execute("""
        SELECT c.nombre, COUNT(r.id) as cantidad 
        FROM categorias c LEFT JOIN relojes r ON c.id = r.categoria_id AND r.activo = 1
        GROUP BY c.id
    """).fetchall()
    
    # Relojes por marca
    relojes_por_marca = conn.execute("""
        SELECT m.nombre, COUNT(r.id) as cantidad 
        FROM marcas m LEFT JOIN relojes r ON m.id = r.marca_id AND r.activo = 1
        GROUP BY m.id
    """).fetchall()
    
    # Reparaciones por estado
    rep_por_estado = conn.execute("""
        SELECT estado, COUNT(*) as cantidad 
        FROM reparaciones WHERE activo = 1
        GROUP BY estado
    """).fetchall()
    
    # Clientes por tipo
    clientes_por_tipo = conn.execute("""
        SELECT tipo_cliente, COUNT(*) as cantidad 
        FROM clientes WHERE activo = 1
        GROUP BY tipo_cliente
    """).fetchall()
    
    conn.close()
    
    return {
        "statusCode": 200,
        "timestamp": datetime.now().isoformat(),
        "relojes_por_categoria": {row["nombre"]: row["cantidad"] for row in relojes_por_cat},
        "relojes_por_marca": {row["nombre"]: row["cantidad"] for row in relojes_por_marca},
        "reparaciones_por_estado": {row["estado"]: row["cantidad"] for row in rep_por_estado},
        "clientes_por_tipo": {row["tipo_cliente"]: row["cantidad"] for row in clientes_por_tipo}
    }


@router.get("/docs", response_model=dict, summary="Documentación de API")
def documentacion_api():
    """
    Retorna información sobre los endpoints disponibles.
    Para documentación interactiva, visita /docs
    """
    return {
        "statusCode": 200,
        "message": "Bienvenido a la API Relojería v1.0.0",
        "documentacion_interactiva": "/docs",
        "documentacion_alternativa": "/redoc",
        "openapi_schema": "/openapi.json",
        "endpoints_principales": {
            "relojes": "/api/relojes",
            "reparaciones": "/api/reparaciones",
            "clientes": "/api/clientes",
            "marcas": "/api/marcas",
            "categorias": "/api/categorias",
            "salud": "/api/health",
            "estadisticas": "/api/stats"
        }
    }


@router.get("/info", response_model=dict, summary="Información de la API")
def informacion_api():
    """Retorna información general sobre la API."""
    return {
        "statusCode": 200,
        "nombre": "API Relojería",
        "descripcion": "Web App de una relojería para práctica de DevOps y Docker",
        "version": "1.0.0",
        "ambiente": "production",
        "base_de_datos": "SQLite",
        "framework": "FastAPI",
        "timestamp": datetime.now().isoformat()
    }
