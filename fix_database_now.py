#!/usr/bin/env python3
"""
Quick database fix to add missing approved_at column
"""

import sqlite3
import os

def fix_database():
    print("Fixing database schema...")
    
    db_path = "instance/idverse.db"
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if approved_at column exists
        cursor.execute("PRAGMA table_info(benefit_applications)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'approved_at' not in columns:
            print("Adding approved_at column...")
            
            # Create new table with approved_at column
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
                    approved_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (applicant_id) REFERENCES users (id)
                )
            """)
            
            # Copy data from old table
            cursor.execute("""
                INSERT INTO benefit_applications_new 
                (id, application_id, scheme_name, applicant_id, application_data, 
                 supporting_documents, status, rejection_reason, reviewed_by, 
                 reviewed_at, approved_at, created_at, applied_at, updated_at)
                SELECT id, application_id, scheme_name, applicant_id, application_data,
                       supporting_documents, status, rejection_reason, reviewed_by,
                       reviewed_at, NULL, created_at, created_at, updated_at
                FROM benefit_applications
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE benefit_applications")
            cursor.execute("ALTER TABLE benefit_applications_new RENAME TO benefit_applications")
            
            # Recreate indexes
            cursor.execute("CREATE UNIQUE INDEX ix_benefit_applications_application_id ON benefit_applications (application_id)")
            cursor.execute("CREATE INDEX ix_benefit_applications_applicant_id ON benefit_applications (applicant_id)")
            
            conn.commit()
            print("approved_at column added successfully!")
        else:
            print("approved_at column already exists!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database fix failed: {e}")
        return False

if __name__ == "__main__":
    if fix_database():
        print("Database fixed successfully!")
        print("Please restart your backend server: python run.py")
    else:
        print("Database fix failed!")
