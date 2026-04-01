"""
📝 ARCHIVO DE PRUEBA
Este archivo contiene datos de prueba para la tabla Area.
Son datos ficticios creados automáticamente en init_db.py.
⚠️ Si cambias la estructura de Area, actualiza estos datos de prueba.
"""

from logic.schemas.area import AreaCreate

# 📊 Datos de prueba para Areas (10 ejemplos)
areas_test_data = [
    AreaCreate(name="Engineering"),      # Ingeniería / Desarrollo
    AreaCreate(name="Product"),          # Producto / Product Management
    AreaCreate(name="Design"),           # Diseño / UX/UI
    AreaCreate(name="Marketing"),        # Marketing / Comunicación
    AreaCreate(name="Sales"),            # Ventas / Comercial
    AreaCreate(name="Human Resources"),  # RRHH / Talento
    AreaCreate(name="Finance"),          # Finanzas / Contabilidad
    AreaCreate(name="Support"),          # Soporte / Customer Success
    AreaCreate(name="Operations"),       # Operaciones / Administración
    AreaCreate(name="Management"),       # Dirección / Executive
]
