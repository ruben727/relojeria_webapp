"""
Modelos Pydantic para la API de Relojería
Definen la estructura de datos validados para requests y responses
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ============================================================================
# ENUMS (Estados y categorías)
# ============================================================================

class EstadoReparacion(str, Enum):
    RECIBIDO = "Recibido"
    EN_PROCESO = "En proceso"
    TERMINADO = "Terminado"
    ENTREGADO = "Entregado"
    CANCELADO = "Cancelado"


class EstadoReparacionUpdate(str, Enum):
    EN_PROCESO = "En proceso"
    TERMINADO = "Terminado"
    ENTREGADO = "Entregado"
    CANCELADO = "Cancelado"


class TipoClienteEnum(str, Enum):
    REGULAR = "Regular"
    VIP = "VIP"
    MAYORISTA = "Mayorista"


# ============================================================================
# RELOJES
# ============================================================================

class MarcaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)


class MarcaCreate(MarcaBase):
    pass


class Marca(MarcaBase):
    id: int

    class Config:
        from_attributes = True


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)


class CategoriaCreate(CategoriaBase):
    pass


class Categoria(CategoriaBase):
    id: int

    class Config:
        from_attributes = True


class ReseñaBase(BaseModel):
    calificacion: int = Field(..., ge=1, le=5)
    comentario: str = Field(..., min_length=1, max_length=500)
    cliente_nombre: str = Field(..., min_length=1)


class ReseñaCreate(ReseñaBase):
    pass


class Reseña(ReseñaBase):
    id: int
    reloj_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class RelojesBase(BaseModel):
    modelo: str = Field(..., min_length=1, max_length=100)
    marca_id: int
    categoria_id: int
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    descripcion: Optional[str] = None
    mecanismo: Optional[str] = None  # Automático, Manual, Cuarzo, etc.


class RelojesCreate(RelojesBase):
    pass


class RelojesUpdate(BaseModel):
    modelo: Optional[str] = None
    marca_id: Optional[int] = None
    categoria_id: Optional[int] = None
    precio: Optional[float] = None
    descripcion: Optional[str] = None
    mecanismo: Optional[str] = None


class RelojesStockUpdate(BaseModel):
    cantidad: int = Field(..., ne=0)  # Positivo suma, negativo resta


class Relojes(RelojesBase):
    id: int
    fecha_creacion: datetime
    reseñas: List[Reseña] = []

    class Config:
        from_attributes = True


# ============================================================================
# REPARACIONES
# ============================================================================

class NotaReparacionBase(BaseModel):
    contenido: str = Field(..., min_length=1, max_length=1000)


class NotaReparacionCreate(NotaReparacionBase):
    pass


class NotaReparacion(NotaReparacionBase):
    id: int
    reparacion_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class ReparacionBase(BaseModel):
    cliente_nombre: str = Field(..., min_length=1)
    reloj_modelo: str = Field(..., min_length=1)
    problema: str = Field(..., min_length=1)
    costo_estimado: float = Field(..., ge=0)


class ReparacionCreate(ReparacionBase):
    pass


class ReparacionUpdate(BaseModel):
    cliente_nombre: Optional[str] = None
    reloj_modelo: Optional[str] = None
    problema: Optional[str] = None
    costo_estimado: Optional[float] = None
    tecnico_asignado: Optional[str] = None


class ReparacionEstadoUpdate(BaseModel):
    estado: EstadoReparacionUpdate


class Reparacion(ReparacionBase):
    id: int
    estado: str
    fecha_ingreso: datetime
    tecnico_asignado: Optional[str] = None
    notas: List[NotaReparacion] = []

    class Config:
        from_attributes = True


# ============================================================================
# CLIENTES
# ============================================================================

class DireccionBase(BaseModel):
    calle: str = Field(..., min_length=1, max_length=100)
    numero: str = Field(..., min_length=1, max_length=10)
    ciudad: str = Field(..., min_length=1, max_length=50)
    estado: str = Field(..., min_length=1, max_length=50)
    codigo_postal: str = Field(..., min_length=1, max_length=10)
    pais: str = Field(default="México", min_length=1, max_length=50)


class DireccionCreate(DireccionBase):
    pass


class Direccion(DireccionBase):
    id: int
    cliente_id: int

    class Config:
        from_attributes = True


class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefono: str = Field(..., min_length=10, max_length=15)
    tipo_cliente: TipoClienteEnum = TipoClienteEnum.REGULAR
    activo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    tipo_cliente: Optional[TipoClienteEnum] = None
    activo: Optional[bool] = None


class ClienteSuscripcion(BaseModel):
    suscrito: bool


class Cliente(ClienteBase):
    id: int
    fecha_registro: datetime
    total_compras: float = 0.0
    total_reparaciones: int = 0
    direcciones: List[Direccion] = []

    class Config:
        from_attributes = True


# ============================================================================
# RESPUESTAS ESTÁNDAR
# ============================================================================

class ResponseBase(BaseModel):
    statusCode: int
    message: Optional[str] = None
    data: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: Optional[str] = None


class StatsResponse(BaseModel):
    total_relojes: int
    total_reparaciones: int
    total_clientes: int
    reparaciones_pendientes: int
    reparaciones_completadas: int
