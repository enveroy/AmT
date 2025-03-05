from flask import Flask, render_template, request, redirect, url_for, Response
import psycopg2
import csv
from psycopg2.extras import DictCursor
from datetime import datetime
import os
from urllib.parse import urlparse
import threading
import time

app = Flask(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_default_secret_key") # Change to a strong secret key
    DEBUG = False # Turn off Debug mode in production
    
    # Database Configuration (PostgreSQL on Render)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass

app.config.from_object(ProductionConfig)  # Use Production Config in Render
 # Initialize app-specific configurations
app.secret_key = app.config['SECRET_KEY'] # Set the secret key

# Function to get a PostgreSQL database connection (Updated)
def get_db_connection():
    try:
        database_url = app.config['DATABASE_URL']
        if not database_url:
            raise ValueError("DATABASE_URL is not set in environment variables.")

        parsed_url = urlparse(database_url)
        conn = psycopg2.connect(
            dbname=parsed_url.path[1:],  # Remove leading slash
            user=parsed_url.username,
            password=parsed_url.password,
            host=parsed_url.hostname,
            port=parsed_url.port,
            sslmode='require'  # Required for Neon
        )
        return conn
    except Exception as e:
        print(f"⚠️ Database connection error: {e}")
        return None  # Handle the error gracefully


# Home route: Fetch and display chemicals borrowed
@app.route("/", defaults={'page': 1})
@app.route("/<int:page>")
def home(page):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    # Pagination settings
    limit = 15
    offset = (page - 1) * limit
    
    # Fetch borrowers with pagination
    cursor.execute("""
        SELECT id, borrower_name, division, phone_number, chemical_name, date_borrowed, status 
        FROM borrowed_chemicals 
        ORDER BY status, date_borrowed DESC 
        LIMIT %(limit)s OFFSET %(offset)s
    """, {"limit": limit, "offset": offset})
    
    borrowers = cursor.fetchall()
    
    # Count total records for pagination
    cursor.execute("SELECT COUNT(*) FROM borrowed_chemicals")
    total_records = cursor.fetchone()[0]
    total_pages = -(-total_records // limit)
    
    conn.close()
    
    # Format the date
    for borrower in borrowers:
        if borrower["date_borrowed"]:
            borrower["date_borrowed"] = borrower["date_borrowed"].strftime("%d-%m-%Y")
    
    return render_template("home.html", borrowers=borrowers, page=page, pages=total_pages)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # Get form data
        borrower_name = request.form.get("borrower_name")
        phone_number = request.form.get("phone_number")
        lab = request.form.get("lab")
        division = request.form.get("division")
        chemical_name = request.form.get("chemical_name")
        bottle_quantity = request.form.get("bottle_quantity")
        date_borrowed = datetime.now().strftime("%Y-%m-%d")
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO borrowed_chemicals (borrower_name, phone_number, lab, division, chemical_name, bottle_quantity, date_borrowed, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Borrowed')
        """, (borrower_name, phone_number, lab, division, chemical_name, bottle_quantity, date_borrowed))
        
        conn.commit()
        conn.close()
        
        return redirect("/")
    
    return render_template("add.html")

@app.route("/return/<int:id>")
def mark_as_returned(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update status to 'Returned'
    cursor.execute("UPDATE borrowed_chemicals SET status='Returned', date_returned=%s WHERE id=%s", 
                   (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    
    conn.commit()
    conn.close()
    
    return redirect("/")

@app.route("/indent", defaults={'page': 1})
@app.route("/indent/<int:page>")
def indent(page):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    # Pagination settings
    limit = 15
    offset = (page - 1) * limit
    
    # Fetch indents with pagination
    cursor.execute("""
        SELECT * FROM indent
        ORDER BY date DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """, {"limit": limit, "offset": offset})
    
    indents = cursor.fetchall()
    
    # Count total records for pagination
    cursor.execute("SELECT COUNT(*) FROM indent")
    total_records = cursor.fetchone()[0]
    total_pages = -(-total_records // limit)
    
    conn.close()
    
    # Format the date
    for indent in indents:
        if indent["date"]:
            indent["date"] = indent["date"].strftime("%d-%m-%Y")
    
    return render_template("indent.html", indents=indents, page=page, pages=total_pages)

@app.route("/add_indent", methods=["GET", "POST"])
def add_indent():
    if request.method == "POST":
        date = datetime.now().strftime("%Y-%m-%d")
        chemical_name = request.form.get("chemical_name")
        cas_no = request.form.get("cas_no")
        company = request.form.get("company")
        quantity = request.form.get("quantity")
        bottle_quantity = request.form.get("bottle_quantity")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO indent (date, chemical_name, cas_no, company, quantity, bottle_quantity, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
        """, (date, chemical_name, cas_no, company, quantity, bottle_quantity))

        conn.commit()
        conn.close()

        return redirect("/indent")

    return render_template("indent_add.html")

@app.route("/validate_indent", defaults={'page': 1})
@app.route("/validate_indent/<int:page>")
def validate_indent(page):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)

        # Pagination settings
        limit = 15
        offset = (page - 1) * limit

        cursor.execute("""
            SELECT * FROM indent WHERE status='Pending'
            ORDER BY date DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """, {"limit": limit, "offset": offset})
        
        indents = cursor.fetchall()

        # Count total records for pagination
        cursor.execute("SELECT COUNT(*) FROM indent WHERE status='Pending'")
        total_records = cursor.fetchone()[0]
        total_pages = -(-total_records // limit)

        conn.close()

        # Format the date
        for indent in indents:
            if indent["date"]:
                indent["date"] = indent["date"].strftime("%d-%m-%Y")

        return render_template("validate.html", indents=indents, page=page, pages=total_pages)
    except Exception as e:
        return f"An error occurred: {e}", 500

@app.route("/validate_indent/<int:id>", methods=["POST"])
def update_indent_status(id):
    try:
        status = request.form.get("status")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE indent SET status=%s WHERE id=%s", (status, id))
        
        conn.commit()
        conn.close()

        return redirect("/validate_indent")
    except Exception as e:
        return f"Failed to update status: {e}", 500

@app.route("/resolve", defaults={'page': 1})
@app.route("/resolve/<int:page>")
def resolve(page):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)

    # Pagination settings
    limit = 15
    offset = (page - 1) * limit

    cursor.execute("""
        SELECT * FROM borrowed_chemicals 
        ORDER BY status, date_borrowed DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """, {"limit": limit, "offset": offset})
    
    borrowers = cursor.fetchall()

    # Count total records for pagination
    cursor.execute("SELECT COUNT(*) FROM borrowed_chemicals")
    total_records = cursor.fetchone()[0]
    total_pages = -(-total_records // limit)

    conn.close()

    # Format the date
    for borrower in borrowers:
        if borrower["date_borrowed"]:
            borrower["date_borrowed"] = borrower["date_borrowed"].strftime("%d-%m-%Y")

    return render_template("resolve.html", borrowers=borrowers, page=page, pages=total_pages)

@app.route('/export_indents', methods=['GET'])
def export_indents():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return 'Please provide both start and end dates.', 400
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    # Query to fetch accepted indents within the date range
    cursor.execute("""
        SELECT * FROM indent 
        WHERE status='Approved' AND date BETWEEN %s AND %s 
        ORDER BY date DESC
    """, (start_date, end_date))
    
    indents = cursor.fetchall()
    
    # Close the database connection
    conn.close()
    
    # Create a CSV response
    def generate_csv():
        # Write header row
        yield ','.join([ 'Date', 'Chemical Name', 'CAS Number', 'Company', 'Quantity', 'Bottles']) + '\n'
        
        # Write data rows
        for indent in indents:
            yield ','.join([
                indent['date'].strftime('%Y-%m-%d'),
                indent['chemical_name'],
                indent['cas_no'],
                indent['company'],
                indent['quantity'],
                str(indent['bottle_quantity']),
            ]) + '\n'
    
    # Return the response as a downloadable CSV file
    return Response(
        generate_csv(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=indents.csv"}
    )

# Function to Clean and Vacuum Database
def cleanup_and_vacuum():
    while True:
        print(f"🕒 Running Cleanup - {datetime.now()}")

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    -- Delete old records
                    DELETE FROM borrowed_chemicals WHERE status = 'Returned' AND date_returned < NOW() - INTERVAL '6 months';
                    DELETE FROM indent WHERE status <> 'Pending' AND date < NOW() - INTERVAL '6 months';

                    -- Optimize storage
                    VACUUM ANALYZE borrowed_chemicals;
                    VACUUM ANALYZE indent;
                """)
                conn.commit()
                print("✅ Cleanup and Vacuuming Done")
            except Exception as e:
                print(f"⚠️ Error during cleanup: {e}")
            finally:
                conn.close()

        # Run cleanup every 24 hours
        time.sleep(86400)  # 86400 seconds = 24 hours

# Step 2: Start the Cleanup Thread when Flask Starts
cleanup_thread = threading.Thread(target=cleanup_and_vacuum, daemon=True)
cleanup_thread.start()

if __name__ == "__main__":
    app.run(debug=True)