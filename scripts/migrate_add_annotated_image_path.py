"""
Database migration: Add annotated_image_path column to calibration_images table.
"""
import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).parent.parent / "handeye_calibration.db"

print(f"Connecting to database: {db_path}")

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(calibration_images)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'annotated_image_path' in columns:
        print("✓ Column 'annotated_image_path' already exists")
    else:
        print("Adding column 'annotated_image_path'...")
        cursor.execute("ALTER TABLE calibration_images ADD COLUMN annotated_image_path VARCHAR(500)")
        conn.commit()
        print("✓ Column 'annotated_image_path' added successfully")
    
except sqlite3.OperationalError as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()
    print("Database connection closed")
