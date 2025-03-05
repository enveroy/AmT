import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"Connected to PostgreSQL: {db_version}")
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
