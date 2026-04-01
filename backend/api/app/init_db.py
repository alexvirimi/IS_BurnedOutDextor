"""
Script para inicializar la base de datos con tablas y datos de prueba.
Ejecuta: python app/init_db.py
"""
import sys
from pathlib import Path

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.database import engine, SessionLocal
from app.models.base import Base
from app.models.area import Area
from logic.controllers.area import create_area
from data.data import areas_test_data


def init_db(session: Session):
    """
    Crea todas las tablas y datos de prueba en la base de datos.
    """
    print("\n" + "="*60)
    print("🔨 CREANDO TABLAS EN LA BASE DE DATOS")
    print("="*60)
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        print("\n📊 Tablas creadas:")
        
        for table_name in Base.metadata.tables.keys():
            print(f"   ✓ {table_name}")
        
        # Buscar si existe un area de prueba
        print("\n" + "="*60)
        print("🌱 VERIFICANDO Y CREANDO DATOS DE PRUEBA")
        print("="*60)
        
        existing_area = session.query(Area).filter(Area.name == 'Engineering').first()
        
        if not existing_area:
            print("\nCreando datos de prueba para areas...")
            for area_data in areas_test_data:
                create_area(session=session, area_create=area_data)
                print(f"   ✓ Creada: {area_data.name}")
            
            print(f"\n✅ {len(areas_test_data)} areas de prueba creadas")
        else:
            print("✓ Datos de prueba ya existen, omitiendo...")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nSolución:")
        print("  - Verifica que Docker Compose esté corriendo: docker-compose up -d")
        print("  - Verifica la DATABASE_URL en core/config.py")
        raise


def init_db_testing(session: Session):
    """
    Crea tablas para pruebas (similar a la función de prueba del ejemplo)
    """
    Base.metadata.create_all(bind=engine)
    
    # Aquí puedes agregar datos mínimos para testing
    existing_area = session.query(Area).filter(Area.name == 'Engineering').first()
    
    if not existing_area:
        area_data = areas_test_data[0]
        create_area(session=session, area_create=area_data)


if __name__ == "__main__":
    session = SessionLocal()
    try:
        init_db(session)
    finally:
        session.close()
