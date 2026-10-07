"""
Endpoints de práctica con datos MOCK (en memoria, sin base de datos).
Los datos viven mientras el servidor está corriendo; si reinicias uvicorn,
se reinician al estado inicial de MOCK_REPARACIONES / MOCK_EMPLEADOS.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/mock", tags=["Mock (sin BD)"])


def response(data):
    return {"statusCode": 200, "data": data}


# ---------------------------------------------------------------------------
# Datos mock
# ---------------------------------------------------------------------------

MOCK_REPARACIONES = [
    {
        "id": 1,
        "cliente": "Juan Pérez",
        "reloj_modelo": "Casio G-Shock GA-2100",
        "problema": "Cambio de pila",
        "estado": "Recibido",
        "costo_estimado": 150.0,
        "fecha_ingreso": "2026-09-20",
    },
    {
        "id": 2,
        "cliente": "María López",
        "reloj_modelo": "Seiko Presage SRPB43",
        "problema": "Correa rota",
        "estado": "En proceso",
        "costo_estimado": 450.0,
        "fecha_ingreso": "2026-09-22",
    },
    {
        "id": 3,
        "cliente": "Carlos Ramírez",
        "reloj_modelo": "Citizen Eco-Drive BM8180",
        "problema": "Cristal rayado",
        "estado": "Terminado",
        "costo_estimado": 600.0,
        "fecha_ingreso": "2026-09-25",
    },
]

MOCK_EMPLEADOS = [
    {
        "id": 1,
        "nombre": "Ana Torres",
        "puesto": "Relojera",
        "telefono": "555-1010",
        "salario": 9500.0,
    },
    {
        "id": 2,
        "nombre": "Luis Fernández",
        "puesto": "Vendedor",
        "telefono": "555-2020",
        "salario": 7200.0,
    },
]

_next_reparacion_id = len(MOCK_REPARACIONES) + 1
_next_empleado_id = len(MOCK_EMPLEADOS) + 1


# ---------------------------------------------------------------------------
# Modelos (bodies para POST / PUT / PATCH)
# ---------------------------------------------------------------------------

class ReparacionCreate(BaseModel):
    cliente: str = Field(min_length=1, examples=["Juan Pérez"])
    reloj_modelo: str = Field(min_length=1, examples=["Casio G-Shock GA-2100"])
    problema: str = Field(min_length=1, examples=["Cambio de pila"])
    estado: str = Field(default="Recibido", examples=["Recibido"])
    costo_estimado: float = Field(ge=0, examples=[150.0])
    fecha_ingreso: str = Field(examples=["2026-09-29"])


class ReparacionUpdate(BaseModel):
    """Usado en PUT: reemplaza el registro completo."""
    cliente: str = Field(min_length=1)
    reloj_modelo: str = Field(min_length=1)
    problema: str = Field(min_length=1)
    estado: str
    costo_estimado: float = Field(ge=0)
    fecha_ingreso: str


class ReparacionEstadoPatch(BaseModel):
    """Usado en PATCH: solo cambia el estado (ej. avanzar la reparación)."""
    estado: str = Field(min_length=1, examples=["Terminado"])


class EmpleadoCreate(BaseModel):
    nombre: str = Field(min_length=1, examples=["Ana Torres"])
    puesto: str = Field(min_length=1, examples=["Relojera"])
    telefono: str = Field(min_length=1, examples=["555-1010"])
    salario: float = Field(ge=0, examples=[9500.0])


class EmpleadoUpdate(BaseModel):
    nombre: str = Field(min_length=1)
    puesto: str = Field(min_length=1)
    telefono: str
    salario: float = Field(ge=0)


# ---------------------------------------------------------------------------
# 1. GET /api/mock/reparaciones -> listar todas
# ---------------------------------------------------------------------------
@router.get("/reparaciones")
def listar_reparaciones():
    return response(MOCK_REPARACIONES)


# ---------------------------------------------------------------------------
# 2. GET /api/mock/reparaciones/{id} -> obtener una
# ---------------------------------------------------------------------------
@router.get("/reparaciones/{reparacion_id}")
def obtener_reparacion(reparacion_id: int):
    for r in MOCK_REPARACIONES:
        if r["id"] == reparacion_id:
            return response(r)
    raise HTTPException(status_code=404, detail="Reparación no encontrada")


# ---------------------------------------------------------------------------
# 3. POST /api/mock/reparaciones -> crear
# Body de ejemplo:
# {
#   "cliente": "Sofía Martín",
#   "reloj_modelo": "Rolex Submariner",
#   "problema": "Servicio de mantenimiento",
#   "estado": "Recibido",
#   "costo_estimado": 2500.0,
#   "fecha_ingreso": "2026-09-29"
# }
# ---------------------------------------------------------------------------
@router.post("/reparaciones", status_code=201)
def crear_reparacion(reparacion: ReparacionCreate):
    global _next_reparacion_id
    nueva = {"id": _next_reparacion_id, **reparacion.model_dump()}
    MOCK_REPARACIONES.append(nueva)
    _next_reparacion_id += 1
    return response(nueva)


# ---------------------------------------------------------------------------
# 4. PUT /api/mock/reparaciones/{id} -> reemplazar completo
# Body de ejemplo:
# {
#   "cliente": "Juan Pérez",
#   "reloj_modelo": "Casio G-Shock GA-2100",
#   "problema": "Cambio de pila y correa",
#   "estado": "En proceso",
#   "costo_estimado": 300.0,
#   "fecha_ingreso": "2026-09-20"
# }
# ---------------------------------------------------------------------------
@router.put("/reparaciones/{reparacion_id}")
def actualizar_reparacion(reparacion_id: int, datos: ReparacionUpdate):
    for r in MOCK_REPARACIONES:
        if r["id"] == reparacion_id:
            r.update(datos.model_dump())
            return response(r)
    raise HTTPException(status_code=404, detail="Reparación no encontrada")


# ---------------------------------------------------------------------------
# 5. PATCH /api/mock/reparaciones/{id} -> actualizar solo el estado
# Body de ejemplo:
# { "estado": "Entregado" }
# ---------------------------------------------------------------------------
@router.patch("/reparaciones/{reparacion_id}")
def cambiar_estado_reparacion(reparacion_id: int, datos: ReparacionEstadoPatch):
    for r in MOCK_REPARACIONES:
        if r["id"] == reparacion_id:
            r["estado"] = datos.estado
            return response(r)
    raise HTTPException(status_code=404, detail="Reparación no encontrada")


# ---------------------------------------------------------------------------
# 6. DELETE /api/mock/reparaciones/{id} -> eliminar
# ---------------------------------------------------------------------------
@router.delete("/reparaciones/{reparacion_id}")
def eliminar_reparacion(reparacion_id: int):
    for i, r in enumerate(MOCK_REPARACIONES):
        if r["id"] == reparacion_id:
            eliminada = MOCK_REPARACIONES.pop(i)
            return response({"mensaje": "Reparación eliminada", "reparacion": eliminada})
    raise HTTPException(status_code=404, detail="Reparación no encontrada")


# ---------------------------------------------------------------------------
# 7. GET /api/mock/empleados -> listar todos
# ---------------------------------------------------------------------------
@router.get("/empleados")
def listar_empleados():
    return response(MOCK_EMPLEADOS)


# ---------------------------------------------------------------------------
# 8. POST /api/mock/empleados -> crear
# Body de ejemplo:
# {
#   "nombre": "Pedro Sánchez",
#   "puesto": "Técnico",
#   "telefono": "555-3030",
#   "salario": 8000.0
# }
# ---------------------------------------------------------------------------
@router.post("/empleados", status_code=201)
def crear_empleado(empleado: EmpleadoCreate):
    global _next_empleado_id
    nuevo = {"id": _next_empleado_id, **empleado.model_dump()}
    MOCK_EMPLEADOS.append(nuevo)
    _next_empleado_id += 1
    return response(nuevo)


# ---------------------------------------------------------------------------
# 9. PUT /api/mock/empleados/{id} -> actualizar completo
# Body de ejemplo:
# {
#   "nombre": "Ana Torres",
#   "puesto": "Relojera senior",
#   "telefono": "555-1010",
#   "salario": 11000.0
# }
# ---------------------------------------------------------------------------
@router.put("/empleados/{empleado_id}")
def actualizar_empleado(empleado_id: int, datos: EmpleadoUpdate):
    for e in MOCK_EMPLEADOS:
        if e["id"] == empleado_id:
            e.update(datos.model_dump())
            return response(e)
    raise HTTPException(status_code=404, detail="Empleado no encontrado")


# ---------------------------------------------------------------------------
# 10. DELETE /api/mock/empleados/{id} -> eliminar
# ---------------------------------------------------------------------------
@router.delete("/empleados/{empleado_id}")
def eliminar_empleado(empleado_id: int):
    for i, e in enumerate(MOCK_EMPLEADOS):
        if e["id"] == empleado_id:
            eliminado = MOCK_EMPLEADOS.pop(i)
            return response({"mensaje": "Empleado eliminado", "empleado": eliminado})
    raise HTTPException(status_code=404, detail="Empleado no encontrado")
