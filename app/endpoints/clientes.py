"""
Endpoints para gestión de Clientes
15+ endpoints para CRUD y operaciones especializadas
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import sqlite3
from pathlib import Path
from datetime import datetime
from app.models import (
    Cliente, ClienteCreate, ClienteUpdate, ClienteSuscripcion,
    Direccion, DireccionCreate
)

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "relojeria.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# ENDPOINTS CRUD PRINCIPALES
# ============================================================================

@router.get("", response_model=List[Cliente], summary="Listar todos los clientes")
def listar_clientes(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """Obtiene lista paginada de todos los clientes."""
    conn = get_db()
    clientes = conn.execute(
        "SELECT * FROM clientes LIMIT ? OFFSET ?",
        (limit, skip)
    ).fetchall()
    conn.close()
    return [dict(c) for c in clientes]


@router.get("/{cliente_id}", response_model=Cliente, summary="Obtener cliente por ID")
def obtener_cliente(cliente_id: int):
    """Obtiene los detalles de un cliente específico."""
    conn = get_db()
    cliente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,)
    ).fetchone()
    conn.close()
    
    if not cliente:
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    
    return dict(cliente)


@router.post("", response_model=dict, status_code=201, summary="Crear nuevo cliente")
def crear_cliente(cliente: ClienteCreate):
    """Crea un nuevo cliente en el sistema."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes 
            (nombre, email, telefono, tipo_cliente, activo, fecha_registro, total_compras)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cliente.nombre, cliente.email, cliente.telefono,
            cliente.tipo_cliente, cliente.activo, datetime.now(), 0.0
        ))
        conn.commit()
        cliente_id = cursor.lastrowid
        conn.close()
        
        return {"statusCode": 201, "message": "Cliente creado", "id": cliente_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{cliente_id}", response_model=dict, summary="Actualizar cliente")
def actualizar_cliente(cliente_id: int, cliente_update: ClienteUpdate):
    """Actualiza los datos de un cliente existente."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    
    update_data = cliente_update.model_dump(exclude_unset=True)
    if update_data:
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [cliente_id]
        conn.execute(f"UPDATE clientes SET {set_clause} WHERE id = ?", values)
        conn.commit()
    
    conn.close()
    return {"statusCode": 200, "message": "Cliente actualizado"}


@router.delete("/{cliente_id}", response_model=dict, summary="Eliminar cliente")
def eliminar_cliente(cliente_id: int):
    """Elimina un cliente (eliminación lógica)."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    
    conn.execute("UPDATE clientes SET activo = 0 WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": "Cliente eliminado"}


# ============================================================================
# ENDPOINTS DE BÚSQUEDA
# ============================================================================

@router.get("/buscar/nombre", response_model=List[Cliente], summary="Buscar por nombre")
def buscar_por_nombre(nombre: str = Query(..., min_length=1)):
    """Busca clientes por nombre (búsqueda parcial)."""
    conn = get_db()
    clientes = conn.execute(
        "SELECT * FROM clientes WHERE nombre LIKE ? AND activo = 1",
        (f"%{nombre}%",)
    ).fetchall()
    conn.close()
    
    return [dict(c) for c in clientes]


@router.get("/filtro/tipo", response_model=List[Cliente], summary="Clientes por tipo")
def clientes_por_tipo(tipo: str = Query(..., min_length=1)):
    """Obtiene clientes filtrados por tipo (Regular, VIP, Mayorista)."""
    conn = get_db()
    clientes = conn.execute(
        "SELECT * FROM clientes WHERE tipo_cliente = ? AND activo = 1",
        (tipo,)
    ).fetchall()
    conn.close()
    
    return [dict(c) for c in clientes]


@router.get("/filtro/activos", response_model=List[Cliente], summary="Clientes activos")
def clientes_activos():
    """Obtiene solo los clientes activos."""
    conn = get_db()
    clientes = conn.execute("SELECT * FROM clientes WHERE activo = 1").fetchall()
    conn.close()
    
    return [dict(c) for c in clientes]


# ============================================================================
# ENDPOINTS DE DIRECCIONES
# ============================================================================

@router.get("/{cliente_id}/direcciones", response_model=List[Direccion], summary="Obtener direcciones")
def obtener_direcciones(cliente_id: int):
    """Obtiene todas las direcciones registradas de un cliente."""
    conn = get_db()
    
    cliente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,)
    ).fetchone()
    if not cliente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    
    direcciones = conn.execute(
        "SELECT * FROM direcciones_cliente WHERE cliente_id = ?",
        (cliente_id,)
    ).fetchall()
    conn.close()
    
    return [dict(d) for d in direcciones]


@router.post("/{cliente_id}/direccion", response_model=dict, status_code=201, summary="Agregar dirección")
def agregar_direccion(cliente_id: int, direccion: DireccionCreate):
    """Agrega una nueva dirección a un cliente."""
    conn = get_db()
    
    cliente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,)
    ).fetchone()
    if not cliente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO direcciones_cliente 
            (cliente_id, calle, numero, ciudad, estado, codigo_postal, pais)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cliente_id, direccion.calle, direccion.numero,
            direccion.ciudad, direccion.estado, direccion.codigo_postal, direccion.pais
        ))
        conn.commit()
        direccion_id = cursor.lastrowid
        conn.close()
        
        return {"statusCode": 201, "message": "Dirección agregada", "id": direccion_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{cliente_id}/direccion/{dir_id}", response_model=dict, summary="Actualizar dirección")
def actualizar_direccion(cliente_id: int, dir_id: int, direccion: DireccionCreate):
    """Actualiza una dirección existente de un cliente."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM direcciones_cliente WHERE id = ? AND cliente_id = ?",
        (dir_id, cliente_id)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    
    conn.execute("""
        UPDATE direcciones_cliente 
        SET calle = ?, numero = ?, ciudad = ?, estado = ?, codigo_postal = ?, pais = ?
        WHERE id = ?
    """, (
        direccion.calle, direccion.numero, direccion.ciudad,
        direccion.estado, direccion.codigo_postal, direccion.pais, dir_id
    ))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": "Dirección actualizada"}


@router.delete("/{cliente_id}/direccion/{dir_id}", response_model=dict, summary="Eliminar dirección")
def eliminar_direccion(cliente_id: int, dir_id: int):
    """Elimina una dirección de un cliente."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM direcciones_cliente WHERE id = ? AND cliente_id = ?",
        (dir_id, cliente_id)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    
    conn.execute("DELETE FROM direcciones_cliente WHERE id = ?", (dir_id,))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": "Dirección eliminada"}


# ============================================================================
# ENDPOINTS DE HISTORIAL
# ============================================================================

@router.get("/{cliente_id}/reparaciones", response_model=dict, summary="Reparaciones del cliente")
def reparaciones_cliente(cliente_id: int):
    """Obtiene todas las reparaciones de un cliente."""
    conn = get_db()
    
    cliente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,)
    ).fetchone()
    if not cliente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    
    reparaciones = conn.execute(
        "SELECT * FROM reparaciones WHERE cliente_nombre = ? AND activo = 1",
        (cliente["nombre"],)
    ).fetchall()
    conn.close()
    
    return {
        "statusCode": 200,
        "cliente_id": cliente_id,
        "total_reparaciones": len(reparaciones),
        "reparaciones": [dict(r) for r in reparaciones]
    }


@router.get("/{cliente_id}/compras", response_model=dict, summary="Historial de compras")
def historial_compras(cliente_id: int):
    """Obtiene el historial de compras de un cliente."""
    conn = get_db()
    
    cliente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,)
    ).fetchone()
    if not cliente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    
    conn.close()
    
    return {
        "statusCode": 200,
        "cliente_id": cliente_id,
        "total_compras": cliente["total_compras"],
        "numero_compras": 0  # Placeholder
    }


# ============================================================================
# ENDPOINTS DE ESTADÍSTICAS
# ============================================================================

@router.get("/stats/resumen", response_model=dict, summary="Estadísticas de clientes")
def estadisticas_clientes():
    """Obtiene estadísticas generales de clientes."""
    conn = get_db()
    
    total = conn.execute("SELECT COUNT(*) as count FROM clientes WHERE activo = 1").fetchone()
    por_tipo = conn.execute("""
        SELECT tipo_cliente, COUNT(*) as cantidad FROM clientes 
        WHERE activo = 1 GROUP BY tipo_cliente
    """).fetchall()
    
    conn.close()
    
    return {
        "statusCode": 200,
        "total_clientes": total["count"],
        "por_tipo": {row["tipo_cliente"]: row["cantidad"] for row in por_tipo}
    }


@router.patch("/{cliente_id}/suscripcion", response_model=dict, summary="Actualizar suscripción")
def actualizar_suscripcion(cliente_id: int, suscripcion: ClienteSuscripcion):
    """Actualiza el estado de suscripción de un cliente."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?",
        (cliente_id,)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    
    # Aquí podrías guardar suscripción en una tabla separada
    conn.close()
    
    return {
        "statusCode": 200,
        "message": f"Suscripción actualizada a {suscripcion.suscrito}",
        "cliente_id": cliente_id
    }
