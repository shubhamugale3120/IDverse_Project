#!/usr/bin/env python3
"""
Quick database migration to add applied_at field to BenefitApplication
"""

import sqlite3
import os
from datetime import datetime

def fix_database():
    print("🔧 Fixing database schema...")
    
    db_path = "instance/idverse.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if applied_at column exists
        cursor.execute("PRAGMA table_info(benefit_applications)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'applied_at' not in columns:
            print("➕ Adding applied_at column to benefit_applications table...")
            
            # Add the applied_at column
            cursor.execute("""
                ALTER TABLE benefit_applications 
                ADD COLUMN applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """)
            
            # Update existing records to have applied_at = created_at
            cursor.execute("""
                UPDATE benefit_applications 
                SET applied_at = created_at 
                WHERE applied_at IS NULL
            """)
            
            conn.commit()
            print("✅ applied_at column added successfully!")
        else:
            print("✅ applied_at column already exists!")
        
        # Verify the fix
        cursor.execute("SELECT COUNT(*) FROM benefit_applications")
        count = cursor.fetchone()[0]
        print(f"📊 Found {count} benefit applications in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

if __name__ == "__main__":
    if fix_database():
        print("🎉 Database migration completed successfully!")
        print("🔄 Please restart your backend server: python run.py")
    else:
        print("❌ Database migration failed!")

