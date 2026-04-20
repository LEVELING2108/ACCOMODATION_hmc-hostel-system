import sys
import os
from datetime import datetime

# Add the app directory to sys.path
sys.path.append(os.getcwd())

from app import app, get_db_connection, get_cursor

def test_routes():
    print("🧪 Starting Application Verification...")
    client = app.test_client()
    
    # 1. Test Index
    print("   🏠 Testing Home Page...")
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'HMC Hostel' in rv.data
    print("   ✅ Home Page OK")
    
    # 2. Test Student Form
    print("   📝 Testing Student Form...")
    rv = client.get('/student-form')
    assert rv.status_code == 200
    assert b'Application Form' in rv.data
    print("   ✅ Student Form OK")
    
    # 3. Test Admin Login Page
    print("   🔑 Testing Admin Login Page...")
    rv = client.get('/admin-login')
    assert rv.status_code == 200
    assert b'Admin Login' in rv.data
    print("   ✅ Admin Login Page OK")
    
    # 4. Test Form Submission (Dry Run)
    print("   📤 Testing Application Submission...")
    test_data = {
        'applicant_name': 'Test User',
        'designation': 'Tester',
        'applicant_type': 'Others',
        'other_applicant_type': 'Automated Test',
        'mobile': '1234567890',
        'email': 'test@example.com',
        'purpose': 'Testing',
        'from_date': '2026-05-01 10:00',
        'to_date': '2026-05-05 10:00',
        'rooms_required': '1',
        'total_guests': '1',
        'guest_name_1': 'Guest 1',
        'guest_type_1': 'Adult'
    }
    rv = client.post('/submit-application', data=test_data, follow_redirects=True)
    assert rv.status_code == 200
    assert b'submitted successfully' in rv.data
    print("   ✅ Application Submission OK")
    
    # 5. Verify Database Content
    print("   📊 Verifying Database Content...")
    conn = get_db_connection()
    cursor = get_cursor(conn)
    cursor.execute("SELECT * FROM applications WHERE applicant_name = 'Test User'")
    row = cursor.fetchone()
    assert row is not None
    print(f"   ✅ Database Record Found (ID: {row['app_id'] if isinstance(row, dict) else row[0]})")
    conn.close()

    print("\n🎉 ALL TESTS PASSED! The application is working correctly.")

if __name__ == "__main__":
    try:
        test_routes()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
