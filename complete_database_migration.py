#!/usr/bin/env python3
"""
Complete database migration to add all missing fields and create new tables
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    print("🔧 Complete Database Migration...")
    
    db_path = "instance/idverse.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Fix BenefitApplication table
        print("1️⃣ Fixing BenefitApplication table...")
        cursor.execute("PRAGMA table_info(benefit_applications)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'approved_at' not in columns:
            print("   ➕ Adding approved_at column...")
            cursor.execute("ALTER TABLE benefit_applications ADD COLUMN approved_at DATETIME")
        
        # 2. Create Document table
        print("2️⃣ Creating Document table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) NOT NULL,
                cid VARCHAR(255) NOT NULL,
                uploaded_by INTEGER NOT NULL,
                file_size INTEGER,
                document_type VARCHAR(100),
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES users (id)
            )
        """)
        
        # 3. Create LinkedID table
        print("3️⃣ Creating LinkedID table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linked_ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                id_type VARCHAR(50) NOT NULL,
                id_number VARCHAR(255) NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                verified_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # 4. Create DocumentType enum table
        print("4️⃣ Creating DocumentType enum...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                is_required BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Insert default document types
        cursor.execute("""
            INSERT OR IGNORE INTO document_types (type_name, description, is_required) VALUES
            ('aadhaar', 'Aadhaar Card', TRUE),
            ('pan', 'PAN Card', TRUE),
            ('voter_id', 'Voter ID', FALSE),
            ('passport', 'Passport', FALSE),
            ('driving_license', 'Driving License', FALSE)
        """)
        
        # 5. Create indexes
        print("5️⃣ Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON documents (uploaded_by)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linked_ids_user_id ON linked_ids (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linked_ids_type ON linked_ids (id_type)")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📊 Tables created: {', '.join(tables)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    if migrate_database():
        print("🎉 Complete database migration successful!")
        print("🔄 Please restart your backend server: python run.py")
    else:
        print("❌ Migration failed!")
