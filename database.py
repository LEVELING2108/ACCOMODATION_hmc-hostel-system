# database.py
import sqlite3
import json
import hashlib
from datetime import datetime
import os

# 🔴 POSTGRESQL SUPPORT
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

_raw_url = os.environ.get('DATABASE_URL')
if _raw_url and _raw_url.startswith('postgres://'):
    DATABASE_URL = _raw_url.replace('postgres://', 'postgresql://', 1)
else:
    DATABASE_URL = _raw_url

# Only use Postgres if both URL and Library are present
IS_POSTGRES = DATABASE_URL is not None and POSTGRES_AVAILABLE

def get_db_connection():
    """Create database connection (Postgres or SQLite)"""
    try:
        if IS_POSTGRES:
            return psycopg2.connect(DATABASE_URL, sslmode='prefer')
        else:
            return sqlite3.connect(DB_NAME)
    except Exception as e:
        print(f"❌ DATABASE CONNECTION ERROR: {e}")
        raise e

def get_cursor(conn):
    """Get appropriate cursor"""
    if IS_POSTGRES:
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        conn.row_factory = sqlite3.Row
        return conn.cursor()

def format_query(query):
    """Replace ? with %s if using Postgres"""
    if IS_POSTGRES:
        return query.replace('?', '%s')
    return query

def init_database():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        cursor = get_cursor(conn)
    except Exception as e:
        print(f"⚠️ Could not connect to DB for init: {e}")
        return
    
    try:
        # Use SERIAL for Postgres, AUTOINCREMENT for SQLite
        id_type = "SERIAL PRIMARY KEY" if IS_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    text_type = "TEXT"
    timestamp_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    
    # Applications table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS applications (
            app_id {id_type},
            applicant_name {text_type} NOT NULL,
            designation {text_type},
            applicant_type {text_type},
            mobile {text_type},
            email {text_type},
            purpose {text_type},
            referred_by {text_type},
            remarks {text_type},
            guest_details {text_type} DEFAULT '[]',
            from_date {text_type},
            to_date {text_type},
            rooms_required INTEGER DEFAULT 1,
            messing_required {text_type} DEFAULT 'No',
            billing_person {text_type},
            signature {text_type},
            status {text_type} DEFAULT 'Pending',
            submitted_date {timestamp_type},
            approved_by {text_type},
            approved_date TIMESTAMP,
            check_in_date TIMESTAMP,
            check_out_date TIMESTAMP,
            room_status {text_type} DEFAULT 'Booked'
        )
    ''')
    
    # 🔴 ADMIN TABLE
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS admin (
            admin_id {id_type},
            username {text_type} UNIQUE NOT NULL,
            password {text_type} NOT NULL,
            full_name {text_type},
            email {text_type}
        )
    ''')
    
    # 🔴 Insert default admin if not exists
    check_query = format_query("SELECT * FROM admin WHERE username=?")
    cursor.execute(check_query, ('admin',))
    if not cursor.fetchone():
        hashed = hashlib.sha256("admin123".encode()).hexdigest()
        insert_query = format_query('''
            INSERT INTO admin (username, password, full_name, email)
            VALUES (?, ?, ?, ?)
        ''')
        cursor.execute(insert_query, ('admin', hashed, 'Administrator', 'admin@diat.ac.in'))
        print("✅ Default admin user created")
    
    conn.commit()
    
    # Check if we have any applications
    cursor.execute("SELECT COUNT(*) as count FROM applications")
    res = cursor.fetchone()
    count = res['count'] if isinstance(res, dict) else res[0]
    
    if count == 0:
        print("📝 Adding sample applications...")
        add_sample_applications(conn)
    
    conn.close()
    print(f"✅ Database initialized successfully")

def add_sample_applications(conn):
    """Add sample applications for testing"""
    cursor = get_cursor(conn)
    
    guests1 = json.dumps([{'name': 'Dr. Rajesh Kumar', 'guest_type': 'Adult'}])
    
    # Insert sample data
    sample_apps = [
        ('Dr. Rajesh Kumar', 'Serving DRDO', '9876543210', 'rajesh@drdo.in',
         'Research Meeting', 'Dr. Sharma', 'Urgent', guests1,
         '15-03-2026 10:00', '18-03-2026 18:00', 1, 'No', 'Self', 'Dr. Rajesh Kumar', 'Pending', 'Booked')
    ]
    
    for app in sample_apps:
        query = format_query('''
            INSERT INTO applications (
                applicant_name, applicant_type, mobile, email, purpose,
                referred_by, remarks, guest_details, from_date, to_date,
                rooms_required, messing_required, billing_person, signature, status, room_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''')
        cursor.execute(query, app)
    
    conn.commit()

def insert_application(form_data, guest_list):
    """Insert new application"""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    
    query = format_query('''
        INSERT INTO applications (
            applicant_name, designation, applicant_type, mobile, email,
            purpose, referred_by, remarks, guest_details, from_date,
            to_date, rooms_required, messing_required, billing_person, signature
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''')
    
    cursor.execute(query, (
        form_data.get('applicant_name', ''),
        form_data.get('designation', ''),
        form_data.get('applicant_type', ''),
        form_data.get('mobile', ''),
        form_data.get('email', ''),
        form_data.get('purpose', ''),
        form_data.get('referred_by', ''),
        form_data.get('remarks', ''),
        json.dumps(guest_list),
        form_data.get('from_date', ''),
        form_data.get('to_date', ''),
        int(form_data.get('rooms_required', 1)),
        form_data.get('messing_required', 'No'),
        form_data.get('billing_person', ''),
        form_data.get('signature', '')
    ))
    
    # Get last ID
    if IS_POSTGRES:
        cursor.execute("SELECT LASTVAL()")
        app_id = cursor.fetchone()['lastval']
    else:
        app_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return app_id

def get_all_applications():
    """Get all applications"""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    
    try:
        cursor.execute('''
            SELECT * FROM applications ORDER BY submitted_date DESC
        ''')
        applications = cursor.fetchall()
        
        result = []
        for app in applications:
            # Handle guest count
            guest_count = 0
            adult_count = 0
            child_count = 0
            if app['guest_details']:
                try:
                    guests = json.loads(app['guest_details'])
                    guest_count = len(guests)
                    for g in guests:
                        if g.get('guest_type') == 'Child':
                            child_count += 1
                        else:
                            adult_count += 1
                except: guest_count = 0
            
            # Convert to regular dict for consistency
            item = dict(app)
            item['guest_count'] = guest_count
            item['adult_count'] = adult_count
            item['child_count'] = child_count
            
            # 🔴 CRITICAL: Convert datetime objects to strings for PostgreSQL
            for key, value in item.items():
                if isinstance(value, datetime):
                    item[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            
            result.append(item)
        
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        conn.close()

def get_application_by_id(app_id):
    """Get single application"""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    query = format_query("SELECT * FROM applications WHERE app_id = ?")
    cursor.execute(query, (app_id,))
    application = cursor.fetchone()
    conn.close()
    return dict(application) if application else None

def update_application_status(app_id, status, approved_by='Admin'):
    """Update status"""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    query = format_query('''
        UPDATE applications 
        SET status=?, approved_by=?, approved_date=CURRENT_TIMESTAMP
        WHERE app_id=?
    ''')
    cursor.execute(query, (status, approved_by, app_id))
    conn.commit()
    conn.close()

def verify_admin(username, password):
    """Verify admin"""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    hashed = hashlib.sha256(password.encode()).hexdigest()
    query = format_query("SELECT * FROM admin WHERE username=? AND password=?")
    cursor.execute(query, (username, hashed))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None

def get_room_status_count():
    """Get count of rooms"""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    
    TOTAL_ROOMS = 250
    
    # Occupied
    query_occ = format_query("SELECT SUM(rooms_required) FROM applications WHERE room_status = 'Occupied'")
    cursor.execute(query_occ)
    res = cursor.fetchone()
    occupied = (res['sum'] if IS_POSTGRES else res[0]) or 0
    
    # Booked
    query_book = format_query("SELECT SUM(rooms_required) FROM applications WHERE status = 'Approved' AND room_status = 'Booked'")
    cursor.execute(query_book)
    res = cursor.fetchone()
    booked = (res['sum'] if IS_POSTGRES else res[0]) or 0
    
    conn.close()
    return {
        'occupied': int(occupied),
        'booked': int(booked),
        'vacant': TOTAL_ROOMS - (int(occupied) + int(booked))
    }

def delete_application(app_id):
    """Delete application"""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    query = format_query("DELETE FROM applications WHERE app_id = ?")
    cursor.execute(query, (app_id,))
    conn.commit()
    conn.close()

def get_current_occupancy():
    """Get all currently occupied rooms"""
    conn = get_db_connection()
    cursor = get_cursor(conn)
    
    try:
        cursor.execute('''
            SELECT * FROM applications 
            WHERE room_status = 'Occupied' 
            ORDER BY check_in_date DESC
        ''')
        occupied = cursor.fetchall()
        
        result = []
        for app in occupied:
            guest_count = 0
            adult_count = 0
            child_count = 0
            if app['guest_details']:
                try:
                    guests = json.loads(app['guest_details'])
                    guest_count = len(guests)
                    for g in guests:
                        if g.get('guest_type') == 'Child':
                            child_count += 1
                        else:
                            adult_count += 1
                except: guest_count = 0
            
            item = dict(app)
            item['guest_count'] = guest_count
            item['adult_count'] = adult_count
            item['child_count'] = child_count
            result.append(item)
            
        return result
    except Exception as e:
        print(f"❌ Error fetching occupancy: {e}")
        return []
    finally:
        conn.close()

# Add other missing functions as needed...
def check_in_application(app_id, admin_name):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    query = format_query("UPDATE applications SET check_in_date = CURRENT_TIMESTAMP, room_status = 'Occupied' WHERE app_id = ?")
    cursor.execute(query, (app_id,))
    conn.commit()
    conn.close()
    return True, "Success"

def check_out_application(app_id):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    query = format_query("UPDATE applications SET check_out_date = CURRENT_TIMESTAMP, room_status = 'Vacant' WHERE app_id = ?")
    cursor.execute(query, (app_id,))
    conn.commit()
    conn.close()
    return True, "Success"
