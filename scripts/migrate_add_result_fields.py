"""
Migration script to add calibration result fields to calibration_runs table.
Run this script to add: rotation_error_deg, translation_error_mm, poses_valid, poses_processed, and method columns.
"""
import sqlite3
import os

# Get the database path - look in backend directory
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
db_path = os.path.join(backend_dir, "handeye_calibration.db")

if not os.path.exists(db_path):
    # Try alternative location (root)
    db_path = os.path.join(os.path.dirname(__file__), "..", "handeye_calibration.db")

print(f"📊 Connecting to database: {db_path}")

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add the new columns
    print("➕ Adding rotation_error_deg column...")
    cursor.execute("ALTER TABLE calibration_runs ADD COLUMN rotation_error_deg REAL")
    
    print("➕ Adding translation_error_mm column...")
    cursor.execute("ALTER TABLE calibration_runs ADD COLUMN translation_error_mm REAL")
    
    print("➕ Adding poses_valid column...")
    cursor.execute("ALTER TABLE calibration_runs ADD COLUMN poses_valid INTEGER")
    
    print("➕ Adding poses_processed column...")
    cursor.execute("ALTER TABLE calibration_runs ADD COLUMN poses_processed INTEGER")
    
    print("➕ Adding method column...")
    cursor.execute("ALTER TABLE calibration_runs ADD COLUMN method VARCHAR(50)")
    
    # Commit the changes
    conn.commit()
    print("✅ Migration completed successfully!")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️  Columns already exist, skipping migration.")
    else:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise
finally:
    conn.close()
    print("📊 Database connection closed.")
