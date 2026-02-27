# test_db_connection.py

from backend.store.db import engine

try:
    with engine.connect() as conn:
        print("Database connection successful.")
except Exception as e:
    print("Connection failed:", e)