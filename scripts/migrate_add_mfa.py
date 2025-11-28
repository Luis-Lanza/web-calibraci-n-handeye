import sys
from pathlib import Path
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings

def migrate():
    """
    Add MFA columns to users table.
    """
    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add mfa_enabled column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN mfa_enabled BOOLEAN DEFAULT 0 NOT NULL")
            print("Added mfa_enabled column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("mfa_enabled column already exists")
            else:
                raise e
                
        # Add mfa_code column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN mfa_code VARCHAR(6)")
            print("Added mfa_code column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("mfa_code column already exists")
            else:
                raise e

        # Add mfa_code_expires_at column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN mfa_code_expires_at DATETIME")
            print("Added mfa_code_expires_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("mfa_code_expires_at column already exists")
            else:
                raise e
                
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error migrating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
