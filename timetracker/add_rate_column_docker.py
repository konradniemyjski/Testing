import sys
import os
from sqlalchemy import text
from app.db import engine

def add_column():
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN hourly_rate FLOAT DEFAULT 0.0"))
            conn.commit()
            print("Successfully added hourly_rate column.")
    except Exception as e:
        print(f"Error (might already exist): {e}")

if __name__ == "__main__":
    add_column()
