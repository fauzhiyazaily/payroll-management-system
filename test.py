import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from payroll_calculations import PayrollCalculator

    print("✅ payroll_calculations import successful!")

    from models import db

    print("✅ models import successful!")

    from auth import auth

    print("✅ auth import successful!")

    print("🎉 All imports working! You can run app.py now.")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Current directory:", os.path.dirname(os.path.abspath(__file__)))
    print("📁 Files in directory:", os.listdir('.'))