"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent))
from config import DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Drop all database tables (use with caution)
    """
    from .models import Base
    Base.metadata.drop_all(bind=engine)

def init_database():
    """
    Initialize database with tables and default data
    """
    try:
        create_tables()

        # Create default admin user
        from .crud import create_default_admin
        db = SessionLocal()
        try:
            create_default_admin(db)
            print("✓ Database initialized successfully")
        finally:
            db.close()
    except Exception as e:
        print(f"✗ Database initialization error: {e}")
        # Create basic database structure manually
        import sqlite3
        import os

        db_path = "data/army_mental_health.db"
        os.makedirs("data", exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create basic users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                army_id TEXT,
                rank TEXT,
                unit TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert default admin
        import hashlib
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, hashed_password, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ("admin", "admin@army.mil", admin_password, "System Administrator", "admin"))

        conn.commit()
        conn.close()
        print("✓ Basic database created successfully")
