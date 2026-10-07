"""
Endpoints para gestión de Relojes
15+ endpoints para CRUD y operaciones especializadas
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import sqlite3
from pathlib import Path
from datetime import datetime
from app.models import (
    Relojes, RelojesCreate, RelojesUpdate, RelojesStockUpdate,
    Reseña, ReseñaCreate, Marca, Categoria
)

router = APIRouter(prefix="/api/relojes", tags=["Relojes"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "relojeria.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# ENDPOINTS CRUD PRINCIPALES
# ============================================================================

@router.get("", response_model=List[Relojes], summary="Listar todos los relojes")
def listar_relojes(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """
    Obtiene lista paginada de todos los relojes.
    
    **Parámetros:**
    - skip: Número de registros a saltar
    - limit: Número máximo de registros a retornar
    """
    conn = get_db()
    relojes = conn.execute(
        "SELECT * FROM relojes LIMIT ? OFFSET ?", 
        (limit, skip)
    ).fetchall()
    conn.close()
    return [dict(r) for r in relojes]


@router.get("/{reloj_id}", response_model=Relojes, summary="Obtener reloj por ID")
def obtener_reloj(reloj_id: int):
    """Obtiene los detalles de un reloj específico por su ID."""
    conn = get_db()
    reloj = conn.execute("SELECT * FROM relojes WHERE id = ?", (reloj_id,)).fetchone()
    conn.close()
    
    if not reloj:
        raise HTTPException(status_code=404, detail=f"Reloj con ID {reloj_id} no encontrado")
    
    return dict(reloj)


@router.post("", response_model=dict, status_code=201, summary="Crear nuevo reloj")
def crear_reloj(reloj: RelojesCreate):
    """
    Crea un nuevo reloj en el inventario.
    
    **Campos requeridos:**
    - modelo: Modelo del reloj
    - marca_id: ID de la marca
    - categoria_id: ID de la categoría
    - precio: Precio del reloj
    - stock: Cantidad en inventario
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO relojes (modelo, marca_id, categoria_id, precio, stock, descripcion, mecanismo, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reloj.modelo, reloj.marca_id, reloj.categoria_id, reloj.precio,
            reloj.stock, reloj.descripcion, reloj.mecanismo, datetime.now()
        ))
        conn.commit()
        reloj_id = cursor.lastrowid
        conn.close()
        
        return {"statusCode": 201, "message": "Reloj creado exitosamente", "id": reloj_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{reloj_id}", response_model=dict, summary="Actualizar reloj")
def actualizar_reloj(reloj_id: int, reloj_update: RelojesUpdate):
    """Actualiza los datos de un reloj existente."""
    conn = get_db()
    
    # Verificar que existe
    existente = conn.execute("SELECT * FROM relojes WHERE id = ?", (reloj_id,)).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reloj {reloj_id} no encontrado")
    
    # Construir actualización dinámica
    update_data = reloj_update.model_dump(exclude_unset=True)
    if update_data:
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [reloj_id]
        conn.execute(f"UPDATE relojes SET {set_clause} WHERE id = ?", values)
        conn.commit()
    
    conn.close()
    return {"statusCode": 200, "message": "Reloj actualizado exitosamente"}


@router.delete("/{reloj_id}", response_model=dict, summary="Eliminar reloj")
def eliminar_reloj(reloj_id: int):
    """Elimina un reloj del inventario (eliminación lógica)."""
    conn = get_db()
    
    existente = conn.execute("SELECT * FROM relojes WHERE id = ?", (reloj_id,)).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reloj {reloj_id} no encontrado")
    
    # Eliminación lógica: marcar como inactivo
    conn.execute("UPDATE relojes SET activo = 0 WHERE id = ?", (reloj_id,))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": "Reloj eliminado exitosamente"}


# ============================================================================
# ENDPOINTS DE BÚSQUEDA Y FILTRADO
# ============================================================================

@router.get("/buscar/modelo", response_model=List[Relojes], summary="Buscar relojes por modelo")
def buscar_por_modelo(modelo: str = Query(..., min_length=1)):
    """Busca relojes que coincidan parcialmente con el modelo ingresado."""
    conn = get_db()
    relojes = conn.execute(
        "SELECT * FROM relojes WHERE modelo LIKE ? AND activo = 1",
        (f"%{modelo}%",)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in relojes]


@router.get("/marca/{marca_id}", response_model=List[Relojes], summary="Relojes por marca")
def relojes_por_marca(marca_id: int):
    """Obtiene todos los relojes de una marca específica."""
    conn = get_db()
    
    # Verificar marca existe
    marca = conn.execute("SELECT * FROM marcas WHERE id = ?", (marca_id,)).fetchone()
    if not marca:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Marca {marca_id} no encontrada")
    
    relojes = conn.execute(
        "SELECT * FROM relojes WHERE marca_id = ? AND activo = 1",
        (marca_id,)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in relojes]


@router.get("/categoria/{categoria_id}", response_model=List[Relojes], summary="Relojes por categoría")
def relojes_por_categoria(categoria_id: int):
    """Obtiene todos los relojes de una categoría específica."""
    conn = get_db()
    
    categoria = conn.execute("SELECT * FROM categorias WHERE id = ?", (categoria_id,)).fetchone()
    if not categoria:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Categoría {categoria_id} no encontrada")
    
    relojes = conn.execute(
        "SELECT * FROM relojes WHERE categoria_id = ? AND activo = 1",
        (categoria_id,)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in relojes]


@router.get("/rango-precio/filtro", response_model=List[Relojes], summary="Relojes por rango de precio")
def relojes_rango_precio(
    min_precio: float = Query(0, ge=0),
    max_precio: float = Query(1000000, gt=0)
):
    """
    Obtiene relojes dentro de un rango de precio.
    
    **Parámetros:**
    - min_precio: Precio mínimo
    - max_precio: Precio máximo
    """
    if min_precio > max_precio:
        raise HTTPException(status_code=400, detail="min_precio no puede ser mayor a max_precio")
    
    conn = get_db()
    relojes = conn.execute(
        "SELECT * FROM relojes WHERE precio BETWEEN ? AND ? AND activo = 1",
        (min_precio, max_precio)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in relojes]


# ============================================================================
# ENDPOINTS DE STOCK
# ============================================================================

@router.get("/stock/disponibles", response_model=List[Relojes], summary="Relojes con stock disponible")
def relojes_con_stock():
    """Obtiene solo los relojes que tienen stock disponible (stock > 0)."""
    conn = get_db()
    relojes = conn.execute(
        "SELECT * FROM relojes WHERE stock > 0 AND activo = 1"
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in relojes]


@router.patch("/{reloj_id}/stock", response_model=dict, summary="Actualizar stock de reloj")
def actualizar_stock(reloj_id: int, stock_update: RelojesStockUpdate):
    """
    Actualiza el stock de un reloj (suma o resta cantidad).
    
    **Parámetros:**
    - cantidad: Número a sumar (positivo) o restar (negativo)
    """
    conn = get_db()
    
    reloj = conn.execute("SELECT stock FROM relojes WHERE id = ?", (reloj_id,)).fetchone()
    if not reloj:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reloj {reloj_id} no encontrado")
    
    nuevo_stock = reloj["stock"] + stock_update.cantidad
    
    if nuevo_stock < 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Stock no puede ser negativo")
    
    conn.execute("UPDATE relojes SET stock = ? WHERE id = ?", (nuevo_stock, reloj_id))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": f"Stock actualizado a {nuevo_stock}"}


# ============================================================================
# ENDPOINTS DE RESEÑAS
# ============================================================================

@router.get("/{reloj_id}/reseñas", response_model=List[Reseña], summary="Obtener reseñas de un reloj")
def obtener_reseñas_reloj(reloj_id: int):
    """Obtiene todas las reseñas de un reloj específico."""
    conn = get_db()
    
    # Verificar reloj existe
    reloj = conn.execute("SELECT * FROM relojes WHERE id = ?", (reloj_id,)).fetchone()
    if not reloj:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reloj {reloj_id} no encontrado")
    
    reseñas = conn.execute(
        "SELECT * FROM reseñas WHERE reloj_id = ?",
        (reloj_id,)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in reseñas]


@router.post("/{reloj_id}/reseña", response_model=dict, status_code=201, summary="Crear reseña")
def crear_reseña(reloj_id: int, reseña: ReseñaCreate):
    """Crea una nueva reseña para un reloj."""
    conn = get_db()
    
    reloj = conn.execute("SELECT * FROM relojes WHERE id = ?", (reloj_id,)).fetchone()
    if not reloj:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reloj {reloj_id} no encontrado")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reseñas (reloj_id, calificacion, comentario, cliente_nombre, fecha_creacion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            reloj_id, reseña.calificacion, reseña.comentario, 
            reseña.cliente_nombre, datetime.now()
        ))
        conn.commit()
        reseña_id = cursor.lastrowid
        conn.close()
        
        return {"statusCode": 201, "message": "Reseña creada exitosamente", "id": reseña_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{reloj_id}/reseña/{reseña_id}", response_model=dict, summary="Eliminar reseña")
def eliminar_reseña(reloj_id: int, reseña_id: int):
    """Elimina una reseña específica de un reloj."""
    conn = get_db()
    
    reseña = conn.execute(
        "SELECT * FROM reseñas WHERE id = ? AND reloj_id = ?",
        (reseña_id, reloj_id)
    ).fetchone()
    
    if not reseña:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reseña {reseña_id} no encontrada")
    
    conn.execute("DELETE FROM reseñas WHERE id = ?", (reseña_id,))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": "Reseña eliminada exitosamente"}


@router.get("/{reloj_id}/calificacion-promedio", response_model=dict, summary="Calificación promedio")
def calificacion_promedio(reloj_id: int):
    """Obtiene la calificación promedio de un reloj basada en sus reseñas."""
    conn = get_db()
    
    reloj = conn.execute("SELECT * FROM relojes WHERE id = ?", (reloj_id,)).fetchone()
    if not reloj:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Reloj {reloj_id} no encontrado")
    
    resultado = conn.execute(
        "SELECT AVG(calificacion) as promedio, COUNT(*) as total FROM reseñas WHERE reloj_id = ?",
        (reloj_id,)
    ).fetchone()
    conn.close()
    
    promedio = resultado["promedio"] or 0
    total = resultado["total"] or 0
    
    return {
        "statusCode": 200,
        "reloj_id": reloj_id,
        "calificacion_promedio": round(promedio, 2),
        "total_reseñas": total
    }
