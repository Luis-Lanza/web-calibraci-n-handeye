"""
Database migration: Add charuco_corners and charuco_ids columns to calibration_images table.
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
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(calibration_images)")
    columns = [row[1] for row in cursor.fetchall()]
    
    changes_made = []
    
    if 'charuco_corners' not in columns:
        print("Adding column 'charuco_corners'...")
        cursor.execute("ALTER TABLE calibration_images ADD COLUMN charuco_corners TEXT")
        changes_made.append("charuco_corners")
    else:
        print("✓ Column 'charuco_corners' already exists")
    
    if 'charuco_ids' not in columns:
        print("Adding column 'charuco_ids'...")
        cursor.execute("ALTER TABLE calibration_images ADD COLUMN charuco_ids TEXT")
        changes_made.append("charuco_ids")
    else:
        print("✓ Column 'charuco_ids' already exists")
    
    if changes_made:
        conn.commit()
        print(f"✓ Successfully added columns: {', '.join(changes_made)}")
    else:
        print("✓ No changes needed, all columns exist")
    
except sqlite3.OperationalError as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()
    print("Database connection closed")
