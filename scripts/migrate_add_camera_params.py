"""
Database migration script to add camera calibration parameter columns.
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path.parent))

from backend.database import engine
from backend.config import settings
import sqlite3

def migrate():
    """Add camera calibration parameter columns to calibration_runs table."""
    # Extract path from DATABASE_URL (format: sqlite:///path/to/db.db)
    db_url = settings.DATABASE_URL
    db_path = db_url.replace("sqlite:///", "")
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\nAdding camera calibration parameter columns...")
        
        # Add camera intrinsic matrix parameters
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_fx REAL")
        print("  ✓ Added camera_fx")
        
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_fy REAL")
        print("  ✓ Added camera_fy")
        
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_cx REAL")
        print("  ✓ Added camera_cx")
        
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_cy REAL")
        print("  ✓ Added camera_cy")
        
        # Add distortion coefficients
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_k1 REAL")
        print("  ✓ Added camera_k1")
        
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_k2 REAL")
        print("  ✓ Added camera_k2")
        
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_p1 REAL")
        print("  ✓ Added camera_p1")
        
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_p2 REAL")
        print("  ✓  Added camera_p2")
        
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_k3 REAL")
        print("  ✓ Added camera_k3")
        
        # Add source tracking
        cursor.execute("ALTER TABLE calibration_runs ADD COLUMN camera_calibration_source VARCHAR(20)")
        print("  ✓ Added camera_calibration_source")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"\n⚠ Columns already exist, skipping migration")
        else:
            print(f"\n✗ Error during migration: {e}")
            raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
