import psycopg2
import os
from urllib.parse import urlparse

# Get database URL from environment variables (same as in Flask)
DATABASE_URL = os.environ.get("DATABASE_URL")

def cleanup_database():
    if not DATABASE_URL:
        print("❌ DATABASE_URL is not set!")
        return
    
    try:
        # Parse the DATABASE_URL
        parsed_url = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            dbname=parsed_url.path[1:],
            user=parsed_url.username,
            password=parsed_url.password,
            host=parsed_url.hostname,
            port=parsed_url.port,
            sslmode="require"
        )
        cursor = conn.cursor()

        # Delete old records in borrowed_chemicals (older than 6 months and returned)
        cursor.execute("""
            DELETE FROM borrowed_chemicals
            WHERE status = 'Returned' 
            AND date_borrowed < NOW() - INTERVAL '6 months';
        """)

        # Delete old records in indent (older than 6 months and not pending)
        cursor.execute("""
            DELETE FROM indent
            WHERE status != 'Pending' 
            AND date < NOW() - INTERVAL '6 months';
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database cleanup completed successfully!")
    
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

# Run the cleanup function
cleanup_database()
