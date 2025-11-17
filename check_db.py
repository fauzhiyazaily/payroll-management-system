import os
from app import app, db
from models import User

print("🔍 Checking database status...")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

# Check if database file exists
db_files = [f for f in os.listdir('.') if f.endswith('.db')]
print(f"Database files found: {db_files}")

with app.app_context():
    try:
        # Try to query users
        users = User.query.all()
        print(f"✅ Database is working! Found {len(users)} users")
        for user in users:
            print(f"   - {user.username} ({user.role})")
    except Exception as e:
        print(f"❌ Database error: {e}")