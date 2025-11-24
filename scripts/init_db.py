"""
Database initialization script for the Hand-Eye Calibration System.
Creates all tables and populates with default data.

Usage:
    python scripts/init_db.py
"""
import sys
from pathlib import Path

# Add parent directory to path to import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import engine, Base, SessionLocal
from backend.models import User, AlgorithmParameters, CalibrationImage
from backend.models.user import UserRole
from backend.config import settings
from backend.auth import get_password_hash


def init_database():
    """
    Initialize the database by creating all tables.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created successfully!")


def create_upload_directories():
    """
    Create upload directories if they don't exist.
    """
    print("\nCreating upload directories...")
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ Created upload directory: {upload_dir}")


def create_default_users(db):
    """
    Create default users for each role.
    """
    print("\nCreating default users...")
    
    default_users = [
        {
            "username": "admin",
            "email": "admin@handeye.com",
            "password": "admin123",  # Change in production!
            "role": UserRole.ENGINEER
        },
        {
            "username": "tech1",
            "email": "tech1@handeye.com",
            "password": "tech123",
            "role": UserRole.TECHNICIAN
        },
        {
            "username": "supervisor1",
            "email": "supervisor1@handeye.com",
            "password": "super123",
            "role": UserRole.SUPERVISOR
        }
    ]
    
    for user_data in default_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if existing_user:
            print(f"  ⊗ User '{user_data['username']}' already exists, skipping...")
            continue
        
        # Create new user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            role=user_data["role"],
            is_active=True
        )
        db.add(user)
        print(f"  ✓ Created user: {user_data['username']} (role: {user_data['role'].value})")
    
    db.commit()
    print("✓ Default users created!")


def create_default_algorithm_params(db):
    """
    Create default algorithm parameters.
    """
    print("\nCreating default algorithm parameters...")
    
    # Get the admin user as the creator
    admin_user = db.query(User).filter(User.username == "admin").first()
    
    if not admin_user:
        print("  ⊗ Admin user not found, cannot create default parameters")
        return
    
    # Check if default parameters already exist
    existing_params = db.query(AlgorithmParameters).filter(
        AlgorithmParameters.is_default == True
    ).first()
    
    if existing_params:
        print("  ⊗ Default parameters already exist, skipping...")
        return
    
    # Create default parameters for Tsai-Lenz algorithm
    default_params = AlgorithmParameters(
        name="Default Tsai-Lenz",
        algorithm_type="tsai_lenz",
        tolerance=1e-6,
        max_iterations=100,
        optimization_method="svd",
        created_by_user_id=admin_user.id,
        is_default=True,
        description="Default parameters for Tsai-Lenz hand-eye calibration algorithm"
    )
    
    db.add(default_params)
    db.commit()
    print("  ✓ Created default algorithm parameters")
    print("✓ Default algorithm parameters created!")


def main():
    """
    Main initialization function.
    """
    print("=" * 60)
    print("Hand-Eye Calibration System - Database Initialization")
    print("=" * 60)
    
    # Create tables
    init_database()
    
    # Create upload directories
    create_upload_directories()
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create default data
        create_default_users(db)
        create_default_algorithm_params(db)
        
        print("\n" + "=" * 60)
        print("✓ Database initialization completed successfully!")
        print("=" * 60)
        print("\nDefault Credentials:")
        print("  Engineer: admin / admin123")
        print("  Technician: tech1 / tech123")
        print("  Supervisor: supervisor1 / super123")
        print("\n⚠ WARNING: Change these passwords in production!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
