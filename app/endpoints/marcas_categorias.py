"""
Endpoints para Marcas y Categorías
10 endpoints para CRUD
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import sqlite3
from pathlib import Path
from app.models import Marca, MarcaCreate, Categoria, CategoriaCreate

router = APIRouter(tags=["Marcas y Categorías"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "relojeria.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# MARCAS
# ============================================================================

@router.get("/api/marcas", response_model=List[Marca], summary="Listar marcas")
def listar_marcas(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    """Obtiene lista de todas las marcas disponibles."""
    conn = get_db()
    marcas = conn.execute(
        "SELECT * FROM marcas LIMIT ? OFFSET ?",
        (limit, skip)
    ).fetchall()
    conn.close()
    return [dict(m) for m in marcas]


@router.get("/api/marcas/{marca_id}", response_model=Marca, summary="Obtener marca")
def obtener_marca(marca_id: int):
    """Obtiene los detalles de una marca específica."""
    conn = get_db()
    marca = conn.execute("SELECT * FROM marcas WHERE id = ?", (marca_id,)).fetchone()
    conn.close()
    
    if not marca:
        raise HTTPException(status_code=404, detail=f"Marca {marca_id} no encontrada")
    
    return dict(marca)


@router.post("/api/marcas", response_model=dict, status_code=201, summary="Crear marca")
def crear_marca(marca: MarcaCreate):
    """Crea una nueva marca."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO marcas (nombre) VALUES (?)", (marca.nombre,))
        conn.commit()
        marca_id = cursor.lastrowid
        conn.close()
        
        return {"statusCode": 201, "message": "Marca creada", "id": marca_id}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="La marca ya existe")
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/api/marcas/{marca_id}", response_model=dict, summary="Actualizar marca")
def actualizar_marca(marca_id: int, marca_update: MarcaCreate):
    """Actualiza una marca existente."""
    conn = get_db()
    
    existente = conn.execute("SELECT * FROM marcas WHERE id = ?", (marca_id,)).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Marca {marca_id} no encontrada")
    
    try:
        conn.execute("UPDATE marcas SET nombre = ? WHERE id = ?", (marca_update.nombre, marca_id))
        conn.commit()
        conn.close()
        return {"statusCode": 200, "message": "Marca actualizada"}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="El nombre de marca ya existe")


@router.delete("/api/marcas/{marca_id}", response_model=dict, summary="Eliminar marca")
def eliminar_marca(marca_id: int):
    """Elimina una marca."""
    conn = get_db()
    
    existente = conn.execute("SELECT * FROM marcas WHERE id = ?", (marca_id,)).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Marca {marca_id} no encontrada")
    
    # Verificar si hay relojes asociados
    relojes = conn.execute(
        "SELECT COUNT(*) as count FROM relojes WHERE marca_id = ?",
        (marca_id,)
    ).fetchone()
    
    if relojes["count"] > 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar: hay {relojes['count']} relojes asociados"
        )
    
    conn.execute("DELETE FROM marcas WHERE id = ?", (marca_id,))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": "Marca eliminada"}


# ============================================================================
# CATEGORÍAS
# ============================================================================

@router.get("/api/categorias", response_model=List[Categoria], summary="Listar categorías")
def listar_categorias(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    """Obtiene lista de todas las categorías disponibles."""
    conn = get_db()
    categorias = conn.execute(
        "SELECT * FROM categorias LIMIT ? OFFSET ?",
        (limit, skip)
    ).fetchall()
    conn.close()
    return [dict(c) for c in categorias]


@router.get("/api/categorias/{categoria_id}", response_model=Categoria, summary="Obtener categoría")
def obtener_categoria(categoria_id: int):
    """Obtiene los detalles de una categoría específica."""
    conn = get_db()
    categoria = conn.execute(
        "SELECT * FROM categorias WHERE id = ?",
        (categoria_id,)
    ).fetchone()
    conn.close()
    
    if not categoria:
        raise HTTPException(status_code=404, detail=f"Categoría {categoria_id} no encontrada")
    
    return dict(categoria)


@router.post("/api/categorias", response_model=dict, status_code=201, summary="Crear categoría")
def crear_categoria(categoria: CategoriaCreate):
    """Crea una nueva categoría."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (categoria.nombre,))
        conn.commit()
        categoria_id = cursor.lastrowid
        conn.close()
        
        return {"statusCode": 201, "message": "Categoría creada", "id": categoria_id}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="La categoría ya existe")
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/api/categorias/{categoria_id}", response_model=dict, summary="Actualizar categoría")
def actualizar_categoria(categoria_id: int, categoria_update: CategoriaCreate):
    """Actualiza una categoría existente."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM categorias WHERE id = ?",
        (categoria_id,)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Categoría {categoria_id} no encontrada")
    
    try:
        conn.execute(
            "UPDATE categorias SET nombre = ? WHERE id = ?",
            (categoria_update.nombre, categoria_id)
        )
        conn.commit()
        conn.close()
        return {"statusCode": 200, "message": "Categoría actualizada"}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="El nombre de categoría ya existe")


@router.delete("/api/categorias/{categoria_id}", response_model=dict, summary="Eliminar categoría")
def eliminar_categoria(categoria_id: int):
    """Elimina una categoría."""
    conn = get_db()
    
    existente = conn.execute(
        "SELECT * FROM categorias WHERE id = ?",
        (categoria_id,)
    ).fetchone()
    if not existente:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Categoría {categoria_id} no encontrada")
    
    # Verificar si hay relojes asociados
    relojes = conn.execute(
        "SELECT COUNT(*) as count FROM relojes WHERE categoria_id = ?",
        (categoria_id,)
    ).fetchone()
    
    if relojes["count"] > 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar: hay {relojes['count']} relojes asociados"
        )
    
    conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
    conn.commit()
    conn.close()
    
    return {"statusCode": 200, "message": "Categoría eliminada"}
