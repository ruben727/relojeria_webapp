from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import sqlite3
from pathlib import Path
from app.seed import seed_db

app = FastAPI(
    title="API Relojería",
    description="API para práctica de DevOps y Docker",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "relojeria.db"
DATA_DIR.mkdir(exist_ok=True)

# ============================================================================
# MODELOS
# ============================================================================

class Reloj(BaseModel):
    modelo: str = Field(..., min_length=1)
    marca: str = Field(..., min_length=1)
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)

class Reparacion(BaseModel):
    cliente: str = Field(..., min_length=1)
    reloj_modelo: str = Field(..., min_length=1)
    problema: str = Field(..., min_length=1)
    estado: str = "Recibido"
    costo: float = Field(..., ge=0)

# ============================================================================
# BASE DE DATOS
# ============================================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS relojes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo TEXT NOT NULL,
        marca TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS reparaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT NOT NULL,
        reloj_modelo TEXT NOT NULL,
        problema TEXT NOT NULL,
        estado TEXT DEFAULT 'Recibido',
        costo REAL NOT NULL,
        fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    seed_db(conn)
    conn.close()

@app.on_event("startup")
def startup():
    init_db()
    print("✅ Base de datos inicializada")


# 1. GET /api/health
@app.get("/api/health", tags=["Sistema"])
def health_check():
    '''Verifica que la API esté operacional'''
    return {
        "statusCode": 200,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# 2. GET /api/relojes
@app.get("/api/relojes", tags=["Relojes"])
def listar_relojes():
    '''Obtiene la lista de todos los relojes'''
    conn = get_db()
    relojes = conn.execute("SELECT * FROM relojes").fetchall()
    conn.close()
    return {
        "statusCode": 200,
        "total": len(relojes),
        "data": [dict(r) for r in relojes]
    }

# 3. POST /api/relojes
@app.post("/api/relojes", status_code=201, tags=["Relojes"])
def crear_reloj(reloj: Reloj):
    '''Crea un nuevo reloj en el inventario'''
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO relojes (modelo, marca, precio, stock)
               VALUES (?, ?, ?, ?)""",
            (reloj.modelo, reloj.marca, reloj.precio, reloj.stock)
        )
        conn.commit()
        reloj_id = cursor.lastrowid
        conn.close()
        
        return {
            "statusCode": 201,
            "message": "Reloj creado exitosamente",
            "id": reloj_id
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

# 7. GET /api/relojes/premium
@app.get("/api/relojes/premium", tags=["Relojes"])
def listar_relojes_premium():
    '''Obtiene los relojes premium (precio >= 1000)'''
    conn = get_db()
    relojes = conn.execute(
        "SELECT * FROM relojes WHERE precio >= 1000 ORDER BY precio DESC"
    ).fetchall()
    conn.close()
    return {
        "statusCode": 200,
        "total": len(relojes),
        "data": [dict(r) for r in relojes]
    }

# 4. GET /api/reparaciones
@app.get("/api/reparaciones", tags=["Reparaciones"])
def listar_reparaciones():
    '''Obtiene la lista de todas las reparaciones'''
    conn = get_db()
    reparaciones = conn.execute("SELECT * FROM reparaciones").fetchall()
    conn.close()
    return {
        "statusCode": 200,
        "total": len(reparaciones),
        "data": [dict(r) for r in reparaciones]
    }

# 5. POST /api/reparaciones
@app.post("/api/reparaciones", status_code=201, tags=["Reparaciones"])
def crear_reparacion(reparacion: Reparacion):
    '''Crea una nueva reparación'''
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO reparaciones (cliente, reloj_modelo, problema, estado, costo)
               VALUES (?, ?, ?, ?, ?)""",
            (reparacion.cliente, reparacion.reloj_modelo, reparacion.problema,
             reparacion.estado, reparacion.costo)
        )
        conn.commit()
        reparacion_id = cursor.lastrowid
        conn.close()
        
        return {
            "statusCode": 201,
            "message": "Reparación creada exitosamente",
            "id": reparacion_id
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

# 8. GET /api/reparaciones/costosa
@app.get("/api/reparaciones/costosa", tags=["Reparaciones"])
def reparacion_mas_costosa():
    '''Obtiene la reparación más costosa'''
    conn = get_db()
    reparacion = conn.execute(
        "SELECT * FROM reparaciones ORDER BY costo DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if reparacion is None:
        raise HTTPException(status_code=404, detail="No hay reparaciones registradas")
    return {
        "statusCode": 200,
        "data": dict(reparacion)
    }

# 6. GET /api/stats
@app.get("/api/stats", tags=["Sistema"])
def estadisticas():
    '''Obtiene estadísticas generales del sistema'''
    conn = get_db()
    total_relojes = conn.execute("SELECT COUNT(*) as count FROM relojes").fetchone()
    total_reparaciones = conn.execute("SELECT COUNT(*) as count FROM reparaciones").fetchone()
    conn.close()
    
    return {
        "statusCode": 200,
        "timestamp": datetime.now().isoformat(),
        "total_relojes": total_relojes["count"],
        "total_reparaciones": total_reparaciones["count"],
        "version": "1.0.0"
    }

# ROOT
@app.get("/")
def root():
    return {
        "message": "Bienvenido a API Relojería v1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "relojes": "/api/relojes",
            "⭐ relojes_premium": "/api/relojes/premium",
            "reparaciones": "/api/reparaciones",
            "⭐ reparacion_costosa": "/api/reparaciones/costosa",
            "stats": "/api/stats"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
