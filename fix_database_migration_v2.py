#!/usr/bin/env python3
"""
Database migration to add applied_at field to BenefitApplication
Uses table recreation approach for SQLite compatibility
"""

import sqlite3
import os
from datetime import datetime

def fix_database():
    print("🔧 Fixing database schema (SQLite compatible)...")
    
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
            
            # Create new table with applied_at column
            cursor.execute("""
                CREATE TABLE benefit_applications_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id VARCHAR(100) UNIQUE NOT NULL,
                    scheme_name VARCHAR(255) NOT NULL,
                    applicant_id INTEGER NOT NULL,
                    application_data JSON,
                    supporting_documents JSON,
                    status VARCHAR(50) DEFAULT 'submitted',
                    rejection_reason TEXT,
                    reviewed_by VARCHAR(255),
                    reviewed_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (applicant_id) REFERENCES users (id)
                )
            """)
            
            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO benefit_applications_new 
                (id, application_id, scheme_name, applicant_id, application_data, 
                 supporting_documents, status, rejection_reason, reviewed_by, 
                 reviewed_at, created_at, applied_at, updated_at)
                SELECT id, application_id, scheme_name, applicant_id, application_data,
                       supporting_documents, status, rejection_reason, reviewed_by,
                       reviewed_at, created_at, created_at, updated_at
                FROM benefit_applications
            """)
            
            # Drop old table
            cursor.execute("DROP TABLE benefit_applications")
            
            # Rename new table
            cursor.execute("ALTER TABLE benefit_applications_new RENAME TO benefit_applications")
            
            # Recreate indexes
            cursor.execute("CREATE UNIQUE INDEX ix_benefit_applications_application_id ON benefit_applications (application_id)")
            cursor.execute("CREATE INDEX ix_benefit_applications_applicant_id ON benefit_applications (applicant_id)")
            
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

