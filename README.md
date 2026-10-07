# 🕐 API Relojería - Proyecto CI/CD

API REST profesional para gestión de relojería con automatización CI/CD, tests y despliegue en AWS EC2.

## 📊 Estado del Proyecto

- **Endpoints**: 61+ ✅
- **Cobertura de Tests**: En progreso 🔄
- **Base de Datos**: SQLite3 ✅
- **Framework**: FastAPI 0.115.12 ✅
- **Servidor**: Uvicorn ✅

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Cliente       │
└────────┬────────┘
         │
    HTTP/REST
         │
┌────────▼─────────────────────────┐
│  FastAPI + Uvicorn (Puerto 8000)  │
├──────────────────────────────────┤
│  ✅ CORS habilitado               │
│  ✅ Docs interactivos (/docs)     │
└────────┬─────────────────────────┘
         │
┌────────▼──────────────────────────┐
│   Routers (61+ Endpoints)          │
├───────────────────────────────────┤
│  • Relojes (15 endpoints)         │
│  • Reparaciones (15 endpoints)    │
│  • Clientes (15 endpoints)        │
│  • Marcas/Categorías (10 endpoints)│
│  • Sistema (6 endpoints)          │
└────────┬──────────────────────────┘
         │
┌────────▼─────────────────────────┐
│   SQLite3 Database                │
├───────────────────────────────────┤
│  📊 8 tablas principales          │
│  📈 Índices de optimización       │
│  🔒 Claves foráneas               │
└───────────────────────────────────┘
```

## 📁 Estructura de Archivos

```
relojeria_webapp/
├── .github/
│   └── workflows/
│       └── main.yml              # Workflow CI/CD (próximo paso)
├── app/
│   ├── __init__.py
│   ├── main.py                   # Aplicación principal ✅
│   ├── models.py                 # Modelos Pydantic ✅
│   └── endpoints/
│       ├── __init__.py
│       ├── relojes.py            # 15 endpoints ✅
│       ├── reparaciones.py       # 15 endpoints ✅
│       ├── clientes.py           # 15 endpoints ✅
│       ├── marcas_categorias.py  # 10 endpoints ✅
│       └── sistema.py            # 6 endpoints ✅
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Configuración pytest ✅
│   └── test_api.py               # Tests básicos ✅
├── data/
│   └── relojeria.db              # Base de datos SQLite
├── backups/                       # Backups de BD
├── .dockerignore                  # Archivos a excluir del Docker ✅
├── .gitignore                     # Archivos a excluir de Git ✅
├── Dockerfile                     # Imagen Docker ✅
├── requirements.txt               # Dependencias producción ✅
├── requirements-dev.txt           # Dependencias desarrollo ✅
└── README.md                      # Este archivo ✅
```

## 🚀 Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu_usuario/relojeria_webapp.git
cd relojeria_webapp
```

### 2. Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
# Dependencias de producción
pip install -r requirements.txt

# Dependencias de desarrollo (para tests)
pip install -r requirements-dev.txt
```

### 4. Ejecutar la API
```bash
# Opción 1: Uvicorn directo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Script Python
python app/main.py
```

La API estará disponible en: **http://localhost:8000**

### 5. Acceder a la documentación
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 📊 Endpoints Disponibles

### 🕐 **Relojes** (15 endpoints)
```
GET    /api/relojes                      # Listar relojes (paginado)
GET    /api/relojes/{id}                 # Obtener por ID
POST   /api/relojes                      # Crear nuevo reloj
PUT    /api/relojes/{id}                 # Actualizar reloj
DELETE /api/relojes/{id}                 # Eliminar reloj
GET    /api/relojes/buscar/modelo        # Buscar por modelo
GET    /api/relojes/marca/{marca_id}     # Por marca
GET    /api/relojes/categoria/{cat_id}   # Por categoría
GET    /api/relojes/rango-precio/filtro  # Rango de precio
GET    /api/relojes/stock/disponibles    # Con stock disponible
PATCH  /api/relojes/{id}/stock           # Actualizar stock
GET    /api/relojes/{id}/reseñas         # Obtener reseñas
POST   /api/relojes/{id}/reseña          # Crear reseña
DELETE /api/relojes/{id}/reseña/{res_id} # Eliminar reseña
GET    /api/relojes/{id}/calificacion    # Calificación promedio
```

### 🔧 **Reparaciones** (15 endpoints)
```
GET    /api/reparaciones                 # Listar reparaciones
GET    /api/reparaciones/{id}            # Obtener por ID
POST   /api/reparaciones                 # Crear reparación
PUT    /api/reparaciones/{id}            # Actualizar reparación
DELETE /api/reparaciones/{id}            # Eliminar reparación
GET    /api/reparaciones/filtro/estado   # Filtrar por estado
GET    /api/reparaciones/cliente/{nombre}# Reparaciones de cliente
GET    /api/reparaciones/filtro/avanzado # Filtro avanzado
PATCH  /api/reparaciones/{id}/estado     # Cambiar estado
GET    /api/reparaciones/{id}/notas      # Obtener notas
POST   /api/reparaciones/{id}/notas      # Agregar nota
DELETE /api/reparaciones/{id}/notas/{nid}# Eliminar nota
GET    /api/reparaciones/stats/resumen   # Estadísticas
GET    /api/reparaciones/proximas-entregas
PATCH  /api/reparaciones/{id}/asignar-tecnico
```

### 👤 **Clientes** (15 endpoints)
```
GET    /api/clientes                     # Listar clientes
GET    /api/clientes/{id}                # Obtener por ID
POST   /api/clientes                     # Crear cliente
PUT    /api/clientes/{id}                # Actualizar cliente
DELETE /api/clientes/{id}                # Eliminar cliente
GET    /api/clientes/buscar/nombre       # Buscar por nombre
GET    /api/clientes/filtro/tipo         # Por tipo
GET    /api/clientes/filtro/activos      # Solo activos
GET    /api/clientes/{id}/direcciones    # Direcciones
POST   /api/clientes/{id}/direccion      # Agregar dirección
PUT    /api/clientes/{id}/direccion/{did}# Actualizar dirección
DELETE /api/clientes/{id}/direccion/{did}# Eliminar dirección
GET    /api/clientes/{id}/reparaciones   # Reparaciones del cliente
GET    /api/clientes/{id}/compras        # Historial de compras
PATCH  /api/clientes/{id}/suscripcion    # Actualizar suscripción
```

### 🏷️ **Marcas y Categorías** (10 endpoints)
```
GET    /api/marcas                       # Listar marcas
POST   /api/marcas                       # Crear marca
GET    /api/marcas/{id}                  # Obtener marca
PUT    /api/marcas/{id}                  # Actualizar marca
DELETE /api/marcas/{id}                  # Eliminar marca
GET    /api/categorias                   # Listar categorías
POST   /api/categorias                   # Crear categoría
GET    /api/categorias/{id}              # Obtener categoría
PUT    /api/categorias/{id}              # Actualizar categoría
DELETE /api/categorias/{id}              # Eliminar categoría
```

### ⚙️ **Sistema** (6 endpoints)
```
GET    /api/health                       # Health check
GET    /api/health/db                    # Verificar BD
GET    /api/version                      # Versión API
GET    /api/stats                        # Estadísticas generales
GET    /api/stats/detallado              # Estadísticas detalladas
GET    /api/docs                         # Info de documentación
GET    /api/info                         # Info general
GET    /                                 # Root endpoint
```

---

## 🧪 Pruebas

### Ejecutar todos los tests
```bash
pytest tests/ -v
```

### Con reporte de cobertura
```bash
pytest tests/ --cov=app --cov-report=html
```

### Test específico
```bash
pytest tests/test_api.py::TestSistema::test_health_check -v
```

### Coverage mínimo del 70%
```bash
pytest tests/ --cov=app --cov-fail-under=70
```

---

## 🐳 Docker

### Construir imagen
```bash
docker build -t relojeria:latest .
```

### Ejecutar contenedor
```bash
docker run -d --name relojeria -p 8000:8000 relojeria:latest
```

### Push a Docker Hub
```bash
docker tag relojeria:latest tu_usuario/relojeria:latest
docker push tu_usuario/relojeria:latest
```

---

## 📋 Variables de Entorno

Crear archivo `.env` (opcional):
```env
DATABASE_URL=sqlite:///./data/relojeria.db
API_PORT=8000
ENVIRONMENT=production
```

---

## 🔄 Próximos Pasos

- [ ] **Paso 1**: Tests automatizados con 70%+ cobertura
- [ ] **Paso 2**: GitHub Actions - Workflow CI/CD
- [ ] **Paso 3**: Publicar en Docker Hub automáticamente
- [ ] **Paso 4**: Despliegue automático en EC2
- [ ] **Paso 5**: Documentación en PDF

---

## 📚 Tecnologías Utilizadas

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Framework Web | FastAPI | 0.115.12 |
| Servidor | Uvicorn | 0.34.0 |
| Base de Datos | SQLite3 | 3.x |
| Validación | Pydantic | 2.10.0 |
| Testing | pytest | 8.0.0 |
| Cobertura | pytest-cov | 4.1.0 |
| Contenedorización | Docker | Latest |
| CI/CD | GitHub Actions | Native |
| Cloud | AWS EC2 | Ubuntu Server |

---

## 🔐 Seguridad

- ✅ Validación de entrada con Pydantic
- ✅ CORS configurado
- ✅ SQLite con PRAGMA foreign_keys
- ✅ Manejo de excepciones HTTP
- ✅ Eliminación lógica (no física)

---

## 📝 Licencia

Este proyecto es para fines educativos en el contexto de DevOps y CI/CD.

---

## 👤 Autor

Desarrollado como proyecto integrador de CI/CD.

---

## 📞 Contacto y Soporte

Para preguntas o issues, crea un issue en GitHub.

---

**Última actualización**: 2026-10-07
**Estado**: En desarrollo 🚀
