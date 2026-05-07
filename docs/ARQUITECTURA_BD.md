# 📋 ARQUITECTURA - BASE DE DATOS Y ENDPOINTS

> **📝 ARQUIVO DE PRUEBA** - Este documento fue generado como documentación técnica de referencia durante el desarrollo inicial. Puede cambiar sin previo aviso.

---

## 📋 RESUMEN DE CAMBIOS REALIZADOS

### **1. ESTRUCTURA DE CARPETAS**
```
backend/api/
├── app/
│   ├── models/              # 11 modelos con relaciones SQLAlchemy
│   ├── database.py          # Engine y sesiones centralizadas
│   ├── config.py            # Configuración (DATABASE_URL)
│   └── init_db.py           # Script: crear tablas + datos prueba
├── logic/
│   ├── controllers/
│   │   └── area.py          # CRUD operations para Area
│   └── schemas/
│       └── area.py          # Pydantic schemas (AreaCreate, AreaResponse)
└── data/
    └── data.py              # Datos de prueba (10 áreas)
```

---

## 🔄 CÓMO FUNCIONA

### **A. INICIALIZACIÓN DE BASE DE DATOS**

```python
# app/database.py - Se ejecuta UNA VEZ al arrancar la app
engine = create_engine(
    "postgresql://postgres:postgres@localhost:5432/inbudex",
    echo=False,               # Log queries SQL
    pool_size=5,              # Max 5 conexiones simultáneass
    pool_recycle=3600,        # Recicla cada hora
)

SessionLocal = sessionmaker(bind=engine)  # Factory para sesiones
```

**¿Qué significa?**
- Un ÚNICO engine que TODA la app comparte
- Pool de conexiones reutilizable (eficiente)
- Thread-safe: SQLAlchemy maneja concurrencia automáticamente

### **B. CREACIÓN DE TABLAS (init_db.py)**

```python
# Ejecutar: poetry run python app/init_db.py
Base.metadata.create_all(bind=engine)  # Crea 11 tablas
```

**Tablas creadas:**
```
✓ worker          ✓ survey          ✓ answer
✓ group           ✓ question        ✓ area
✓ rank            ✓ question_survey ✓ result
✓ identity_mapping
✓ company
```

### **C. CAMBIOS CRÍTICOS EN LOS MODELOS**

#### **1. UUID NATIVO (Antes: String(36))**

**ANTES - ERROR:**
```python
# PostgreSQL almacenaba como VARCHAR
id: Mapped[uuid.UUID] = mapped_column(String(36), ...)

# Cuando Query intentaba: WHERE area.id = 'uuid'::uuid
# ❌ Error: character varying = uuid (tipos incompatibles)
```

**DESPUÉS - CORRECTO:**
```python
# PostgreSQL almacena como UUID nativo
id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ...)

# Ahora Query: WHERE area.id = 'uuid'::uuid
# ✅ Ambos lados son UUID, sin casting
```

**Aplicado a:**
- Todos los `id` primarios (11 tablas)
- Todas las foreign keys con UUID

#### **2. RELACIONES BIDIRECCIONALES (Antes: Mismatched back_populates)**

**ANTES - ERROR:**
```python
# workers.py
mapping: Mapped[IdentityMapping] = relationship(back_populates='workers')

# identity_mapping.py  
worker: Mapped[Worker] = relationship(back_populates='mapping')

# ❌ No coinciden: 'workers' ≠ 'mapping'
# SQLAlchemy: "Mapper has no property 'workers'"
```

**DESPUÉS - CORRECTO:**
```python
# workers.py
group: Mapped[Group] = relationship(back_populates='workers', foreign_keys=[id_group])
mapping: Mapped[IdentityMapping] = relationship(back_populates='worker')

# groups.py
workers: Mapped[list[Worker]] = relationship(
    back_populates='group', 
    foreign_keys='Worker.id_group'
)
worker_leader: Mapped[Worker] = relationship(
    back_populates='group_leader', 
    foreign_keys='Group.id_leader'
)

# ✅ Todos los back_populates coinciden exactamente
```

**Matriz de relaciones corregidas:**

| Tabla | Relación | back_populates | Status |
|-------|----------|---|--------|
| Worker | group | workers | ✅ |
| Worker | group_leader | group_leader | ✅ |
| Worker | rank | workers | ✅ |
| Worker | mapping | worker | ✅ |
| Worker | company | worker | ✅ |
| Group | workers | group | ✅ |
| Group | worker_leader | group_leader | ✅ |
| Group | area | groups | ✅ |
| Group | answers | group | ✅ |
| Group | results | group | ✅ |
| Area | groups | area | ✅ |
| Area | answers | area | ✅ |
| Area | results | area | ✅ |
| Surveys | question_surveys | survey | ✅ |
| Surveys | results | survey | ✅ |
| Question | question_surveys | question | ✅ |
| QuestionSurveys | answers | question_survey | ✅ |
| Answer | group | answers | ✅ |
| Answer | identity_mapping | answers | ✅ |
| Answer | question_survey | answers | ✅ |
| Answer | area | answers | ✅ |
| Result | identity_mapping | results | ✅ |
| Result | survey | results | ✅ |
| Result | area | results | ✅ |
| Result | group | results | ✅ |

---

## ✅ COMPATIBILIDAD CON ENDPOINTS

**SÍ, 100% compatible.** Así integras todo en FastAPI:

### **Patrón ESTÁNDAR para cualquier endpoint:**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from logic.controllers.area import get_all_areas, create_area
from logic.schemas.area import AreaCreate, AreaResponse

router = APIRouter(prefix="/areas", tags=["areas"])

# 📌 POST - Crear Area
@router.post("/", response_model=AreaResponse, status_code=201)
def create_new_area(
    area: AreaCreate,
    db: Session = Depends(get_db)  # ← INYECTA sesión automáticamente
):
    return create_area(session=db, area_create=area)

# 📌 GET - Listar todas las Areas
@router.get("/", response_model=list[AreaResponse])
def list_areas(db: Session = Depends(get_db)):
    return get_all_areas(session=db)

# 📌 GET - Obtener una Area por ID
@router.get("/{area_id}", response_model=AreaResponse)
def get_area(area_id: str, db: Session = Depends(get_db)):
    return get_area_by_id(session=db, area_id=area_id)

# 📌 PUT - Actualizar Area
@router.put("/{area_id}", response_model=AreaResponse)
def update_area(
    area_id: str,
    area: AreaUpdate,
    db: Session = Depends(get_db)
):
    return update_area(session=db, area_id=area_id, area_update=area)

# 📌 DELETE - Eliminar Area
@router.delete("/{area_id}", status_code=204)
def delete_area(area_id: str, db: Session = Depends(get_db)):
    delete_area(session=db, area_id=area_id)
```

### **¿Cómo fluye una request?**

```
1. Cliente: POST /areas {"name": "Engineering"}
   ↓
2. FastAPI deserializa JSON → AreaCreate(name="Engineering")
   ↓
3. Llama Depends(get_db)
   ↓
4. get_db():
   db = SessionLocal()  # ← Usa el ENGINE
   try:
       yield db         # ← Pasa al endpoint
   finally:
       db.close()       # ← Cierra conexión
   ↓
5. Pasa sesión a create_area(session=db, ...)
   ↓
6. create_area() en controller:
   area = Area(
       id=uuid4(),
       name="Engineering"
   )
   session.add(area)
   session.commit()
   session.refresh(area)  # ← Obtiene datos insertados
   return area
   ↓
7. FastAPI serializa con AreaResponse
   ↓
8. Cliente recibe JSON: {"id": "xxx-xxx", "name": "Engineering"}
```

---

## 🔌 EL ENGINE - CENTRO DEL SISTEMA

### **Propiedades del Engine:**

```python
engine = create_engine(
    DATABASE_URL,           # Conexión a PostgreSQL
    echo=False,             # Log SQL queries (True en DEBUG)
    pool_size=5,            # Max 5 conexiones concurrentes
    pool_recycle=3600,      # Recicla conexiones cada 1 hora
)
```

### **¿Por qué UN engine para toda la app?**

✅ **Eficiencia:** Reutiliza conexiones (pool)  
✅ **Memory-efficient:** No crea múltiples instancias  
✅ **Thread-safe:** SQLAlchemy gestiona concurrencia  
✅ **Escalable:** Pool soporta miles de requests  
✅ **Automático:** No necesitas configurar nada más  

### **¿Cómo lo usan los endpoints?**

```python
# El engine existe en memory (singleton)
engine = create_engine(...)

# SessionLocal = factory que crea sesiones
SessionLocal = sessionmaker(bind=engine)

# En cada request:
def get_db():
    db = SessionLocal()  # ← Abre conexión del pool del engine
    try:
        yield db
    finally:
        db.close()       # ← Retorna conexión al pool
```

---

## 🎯 FLUJO COMPLETO: Crear una Area

**Código en el endpoint:**
```python
@router.post("/areas", response_model=AreaResponse)
def crear_area(area: AreaCreate, db: Session = Depends(get_db)):
    return create_area(session=db, area_create=area)
```

**Lo que ocurre internamente:**

1. **Cliente envía:** `POST /areas {"name": "Engineering"}`

2. **FastAPI deserializa:**
   ```python
   area = AreaCreate(name="Engineering")
   ```

3. **Depends(get_db) ejecuta:**
   ```python
   db = SessionLocal()  # Del engine existente
   ```

4. **Se llama create_area():**
   ```python
   # logic/controllers/area.py
   def create_area(session: Session, area_create: AreaCreate) -> Area:
       db_area = Area(
           id=uuid4(),           # UUID generado automáticamente
           name=area_create.name # "Engineering"
       )
       session.add(db_area)      # Agregado a la transacción
       session.commit()          # INSERT into area...
       session.refresh(db_area)  # Obtiene datos desde BD (ej: confirmación)
       return db_area
   ```

5. **SQLAlchemy genera SQL:**
   ```sql
   INSERT INTO area (id, name) 
   VALUES ('cad0a5e3-393f-42a1-87c3-c336d4e47a30'::uuid, 'Engineering')
   RETURNING *;
   ```

6. **FastAPI serializa con AreaResponse:**
   ```python
   # logic/schemas/area.py
   class AreaResponse(BaseModel):
       id: UUID
       name: str
   ```

7. **Cliente recibe:**
   ```json
   {
       "id": "cad0a5e3-393f-42a1-87c3-c336d4e47a30",
       "name": "Engineering"
   }
   ```

8. **Conexión retorna al pool:**
   ```python
   db.close()  # En dispositivo Depends context manager
   ```

---

## 📊 CAMBIOS RESUMIDOS

| Aspecto | Antes | Después | Beneficio |
|---------|-------|---------|-----------|
| **UUID Storage** | `String(36)` | `UUID(as_uuid=True)` | Sin errores de casting |
| **Relaciones** | Mismatched | Validated | SQLAlchemy sin errores |
| **Ambiguous FK** | No especificadas | `foreign_keys=[...]` | Disambiguated joins |
| **Engine** | Ad-hoc | Singleton compartido | Eficiencia + pooling |
| **Sesiones** | Manuales | Via Depends | FastAPI integración |
| **Foreign Keys** | Nombres inconsistentes | Standardized | Sin confusiones |

---

## 🚀 IMPLEMENTAR NUEVOS ENDPOINTS

**Patrón que SIEMPRE seguir:**

```python
# 1. Define schema (Pydantic)
from pydantic import BaseModel

class TuModelCreate(BaseModel):
    campo1: str
    campo2: int

class TuModelResponse(TuModelCreate):
    id: UUID

# 2. Define controller (Business logic)
def crear_tumodel(session: Session, item: TuModelCreate):
    db_item = TuModel(id=uuid4(), campo1=item.campo1, ...)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

# 3. Define endpoint (FastAPI)
@router.post("/tumodels")
def endpoint(item: TuModelCreate, db: Session = Depends(get_db)):
    return crear_tumodel(session=db, item=item)
```

**El engine ya está listo.** Solo necesitas:
- ✅ Crear schema (Pydantic)
- ✅ Crear controller (lógica)
- ✅ Crear endpoint (FastAPI request handler)

Todo el pooling, concurrencia y eficiencia ocurre **automáticamente**.

---

## 🔗 REFERENCIAS ÚTILES

- **Inicializar BD:** `poetry run python app/init_db.py`
- **Ver datos:** http://localhost:8080 (Adminer)
- **Credenciales Adminer:**
  - Sistema: PostgreSQL
  - Host: postgres
  - User: postgres
  - Password: postgres
  - Database: inbudex

---

**Última actualización:** 31 de Marzo de 2026  
**Status:** ✅ Producción-ready
