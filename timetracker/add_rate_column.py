import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from sqlalchemy import text, create_engine

# Manually load .env since python-dotenv might not be active or loaded
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

    # Construct DATABASE_URL if missing (since it is in docker-compose, not .env)
    if "DATABASE_URL" not in os.environ and "POSTGRES_USER" in os.environ:
        user = os.environ.get("POSTGRES_USER")
        pwd = os.environ.get("POSTGRES_PASSWORD")
        db = os.environ.get("POSTGRES_DB")
        # Use 127.0.0.1 for script execution from host
        os.environ["DATABASE_URL"] = f"postgresql+psycopg://{user}:{pwd}@127.0.0.1:5432/{db}"
        print(f"Constructed DATABASE_URL: {os.environ['DATABASE_URL']}")

load_env()

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
