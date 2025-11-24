"""
Verification script to check that the database setup is correct.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import User, CalibrationRun, RobotPose, CameraPose, AlgorithmParameters
from backend.database import SessionLocal

def verify_setup():
    print("=" * 60)
    print("Verificando configuración de la base de datos")
    print("=" * 60)
    
    print("\n✓ Modelos importados correctamente")
    
    # Verificar conexión a la base de datos
    db = SessionLocal()
    
    try:
        # Verificar usuarios
        users = db.query(User).all()
        print(f"\n✓ Usuarios en la base de datos: {len(users)}")
        for user in users:
            print(f"  - {user.username} ({user.role.value})")
        
        # Verificar parámetros del algoritmo
        algo_params = db.query(AlgorithmParameters).all()
        print(f"\n✓ Parámetros de algoritmo: {len(algo_params)}")
        for param in algo_params:
            print(f"  - {param.name} (default: {param.is_default})")
        
        # Verificar que no hay calibraciones todavía
        calibrations = db.query(CalibrationRun).all()
        print(f"\n✓ Calibraciones en BD: {len(calibrations)}")
        
        print("\n" + "=" * 60)
        print("✓ Verificación completada exitosamente!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error durante la verificación: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    verify_setup()
