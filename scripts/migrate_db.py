import sqlite3

def migrate():
    print("Migrating database...")
    conn = sqlite3.connect("handeye_calibration.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN mfa_secret VARCHAR(32)")
        print("✅ Added mfa_secret column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ Column mfa_secret already exists")
        else:
            print(f"❌ Error adding column: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
