"""
Endpoints para gestión de Reparaciones
15+ endpoints para CRUD y operaciones especializadas
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import sqlite3
from pathlib import Path
from datetime import datetime
from app.models import (
    Reparacion, ReparacionCreate, ReparacionUpdate, ReparacionEstadoUpdate,
    NotaReparacion, NotaReparacionCreate
)

router = APIRouter(prefix="/api/reparaciones", tags=["Reparaciones"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "relojeria.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# ENDPOINTS CRUD PRINCIPALES
# ============================================================================

@router.get("", response_model=List[Reparacion], summary="Listar todas las reparaciones")
def listar_reparaciones(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """Obtiene lista paginada de todas las reparaciones."""
    conn = get_db()
    reparaciones = conn.execute(
        "SELECT * FROM reparaciones LIMIT ? OFFSET ?",
        (limit, skip)
    ).fetchall()
    conn.close()
    return [dict(r) for r in reparaciones]


@router.get("/{reparacion_id}", response_model=Reparacion, summary="Obtener reparación por ID")
def obtener_reparacion(reparacion_id: int):
    """Obtiene los detalles de una reparación específica."""
    conn = get_db()
    reparacion = conn.execute(
        "SELECT * FROM reparaciones WHERE id = ?",
        (reparacion_id,)
    ).fetchone()
    conn.close()
    
    if not reparacion:
        raise HTTPException(status_code=404, detail=f"Reparación {reparacion_id} no encontrada")
    
    return dict(reparacion)


@router.post("", response_model=dict, status_code=201, summary="Crear nueva reparación")
def crear_reparacion(reparacion: ReparacionCreate):
    """Crea una nueva reparación en el sistema."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reparaciones 
            (cliente_nombre, reloj_modelo, problema, estado, costo_estimado, fecha_ingreso)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            reparacion.cliente_nombre, reparacion.reloj_modelo,
            reparacion.problema, "Recibido", reparacion.costo_estimado,
            datetime.now()
        ))
        conn.commit()
        reparacion_id = cursor.lastrowid
        conn.close()
        
        return {"statusCode": 201, "message": "Reparación creada", "id": reparacion_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{reparacion_id}", response_model=dict, summary="Actualizar reparación")
def actualizar_reparacion(reparacion_id: int, reparacion_update: ReparacionUpdate):
    """Actualiza los datos de una reparación existente."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM reparaciones WHERE id = ?",
        (reparacion_id,)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reparación {reparacion_id} no encontrada")
    
    update_data = reparacion_update.model_dump(exclude_unset=True)
    if update_data:
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [reparacion_id]
        conn.execute(f"UPDATE reparaciones SET {set_clause} WHERE id = ?", values)
        conn.commit()
    
    conn.close()
    return {"statusCode": 200, "message": "Reparación actualizada"}


@router.delete("/{reparacion_id}", response_model=dict, summary="Eliminar reparación")
def eliminar_reparacion(reparacion_id: int):
    """Elimina una reparación (eliminación lógica)."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM reparaciones WHERE id = ?",
        (reparacion_id,)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reparación {reparacion_id} no encontrada")
    
    # Eliminación lógica
    conn.execute("UPDATE reparaciones SET activo = 0 WHERE id = ?", (reparacion_id,))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": "Reparación eliminada"}


# ============================================================================
# ENDPOINTS DE FILTRADO Y BÚSQUEDA
# ============================================================================

@router.get("/filtro/estado", response_model=List[Reparacion], summary="Reparaciones por estado")
def reparaciones_por_estado(estado: str = Query(..., min_length=1)):
    """Obtiene reparaciones filtradas por estado específico."""
    conn = get_db()
    reparaciones = conn.execute(
        "SELECT * FROM reparaciones WHERE estado = ? AND activo = 1",
        (estado,)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in reparaciones]


@router.get("/cliente/{cliente_nombre}", response_model=List[Reparacion], summary="Reparaciones de un cliente")
def reparaciones_por_cliente(cliente_nombre: str = Query(..., min_length=1)):
    """Obtiene todas las reparaciones de un cliente específico."""
    conn = get_db()
    reparaciones = conn.execute(
        "SELECT * FROM reparaciones WHERE cliente_nombre LIKE ? AND activo = 1",
        (f"%{cliente_nombre}%",)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in reparaciones]


@router.get("/filtro/avanzado", response_model=List[Reparacion], summary="Filtro avanzado")
def filtro_avanzado(
    estado: str = Query(None),
    cliente: str = Query(None),
    min_costo: float = Query(None, ge=0),
    max_costo: float = Query(None, gt=0)
):
    """
    Filtro avanzado de reparaciones con múltiples criterios.
    Todos los parámetros son opcionales.
    """
    conn = get_db()
    query = "SELECT * FROM reparaciones WHERE activo = 1"
    params = []
    
    if estado:
        query += " AND estado = ?"
        params.append(estado)
    
    if cliente:
        query += " AND cliente_nombre LIKE ?"
        params.append(f"%{cliente}%")
    
    if min_costo is not None:
        query += " AND costo_estimado >= ?"
        params.append(min_costo)
    
    if max_costo is not None:
        query += " AND costo_estimado <= ?"
        params.append(max_costo)
    
    reparaciones = conn.execute(query, params).fetchall()
    conn.close()
    
    return [dict(r) for r in reparaciones]


# ============================================================================
# ENDPOINTS DE ESTADO
# ============================================================================

@router.patch("/{reparacion_id}/estado", response_model=dict, summary="Actualizar estado")
def actualizar_estado(reparacion_id: int, estado_update: ReparacionEstadoUpdate):
    """Actualiza el estado de una reparación."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM reparaciones WHERE id = ?",
        (reparacion_id,)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reparación {reparacion_id} no encontrada")
    
    conn.execute(
        "UPDATE reparaciones SET estado = ? WHERE id = ?",
        (estado_update.estado, reparacion_id)
    )
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": f"Estado actualizado a {estado_update.estado}"}


# ============================================================================
# ENDPOINTS DE NOTAS
# ============================================================================

@router.get("/{reparacion_id}/notas", response_model=List[NotaReparacion], summary="Obtener notas")
def obtener_notas(reparacion_id: int):
    """Obtiene todas las notas de una reparación."""
    conn = get_db()
    
    reparacion = conn.execute(
        "SELECT * FROM reparaciones WHERE id = ?",
        (reparacion_id,)
    ).fetchone()
    if not reparacion:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reparación {reparacion_id} no encontrada")
    
    notas = conn.execute(
        "SELECT * FROM notas_reparacion WHERE reparacion_id = ?",
        (reparacion_id,)
    ).fetchall()
    conn.close()
    
    return [dict(n) for n in notas]


@router.post("/{reparacion_id}/notas", response_model=dict, status_code=201, summary="Crear nota")
def crear_nota(reparacion_id: int, nota: NotaReparacionCreate):
    """Agrega una nota a una reparación."""
    conn = get_db()
    
    reparacion = conn.execute(
        "SELECT * FROM reparaciones WHERE id = ?",
        (reparacion_id,)
    ).fetchone()
    if not reparacion:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reparación {reparacion_id} no encontrada")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notas_reparacion (reparacion_id, contenido, fecha_creacion)
            VALUES (?, ?, ?)
        """, (reparacion_id, nota.contenido, datetime.now()))
        conn.commit()
        nota_id = cursor.lastrowid
        conn.close()
        
        return {"statusCode": 201, "message": "Nota creada", "id": nota_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{reparacion_id}/notas/{nota_id}", response_model=dict, summary="Eliminar nota")
def eliminar_nota(reparacion_id: int, nota_id: int):
    """Elimina una nota específica de una reparación."""
    conn = get_db()
    
    nota = conn.execute(
        "SELECT * FROM notas_reparacion WHERE id = ? AND reparacion_id = ?",
        (nota_id, reparacion_id)
    ).fetchone()
    
    if not nota:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Nota {nota_id} no encontrada")
    
    conn.execute("DELETE FROM notas_reparacion WHERE id = ?", (nota_id,))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": "Nota eliminada"}


# ============================================================================
# ENDPOINTS DE ESTADÍSTICAS
# ============================================================================

@router.get("/stats/resumen", response_model=dict, summary="Estadísticas de reparaciones")
def estadisticas_reparaciones():
    """Obtiene estadísticas generales de reparaciones."""
    conn = get_db()
    
    total = conn.execute("SELECT COUNT(*) as count FROM reparaciones WHERE activo = 1").fetchone()
    por_estado = conn.execute("""
        SELECT estado, COUNT(*) as cantidad FROM reparaciones 
        WHERE activo = 1 GROUP BY estado
    """).fetchall()
    
    conn.close()
    
    return {
        "statusCode": 200,
        "total_reparaciones": total["count"],
        "por_estado": {row["estado"]: row["cantidad"] for row in por_estado}
    }


@router.get("/proximas-entregas", response_model=List[Reparacion], summary="Próximas entregas")
def proximas_entregas(dias: int = Query(7, ge=1, le=30)):
    """Obtiene reparaciones próximas a entregar (en ciertos días)."""
    conn = get_db()
    reparaciones = conn.execute(
        "SELECT * FROM reparaciones WHERE estado IN ('Terminado', 'En proceso') AND activo = 1 LIMIT ?",
        (dias,)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in reparaciones]


@router.patch("/{reparacion_id}/asignar-tecnico", response_model=dict, summary="Asignar técnico")
def asignar_tecnico(reparacion_id: int, tecnico_nombre: str = Query(..., min_length=1)):
    """Asigna un técnico a una reparación."""
    conn = get_db()
    
    reparacion = conn.execute(
        "SELECT * FROM reparaciones WHERE id = ?",
        (reparacion_id,)
    ).fetchone()
    if not reparacion:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reparación {reparacion_id} no encontrada")
    
    conn.execute(
        "UPDATE reparaciones SET tecnico_asignado = ? WHERE id = ?",
        (tecnico_nombre, reparacion_id)
    )
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": f"Técnico {tecnico_nombre} asignado"}
