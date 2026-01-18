import sys
import os

def check_app_integrity():
    print("🖥️ CHECKING DASHBOARD INTEGRITY...")
    
    app_path = 'src/dashboard/app.py'
    if os.path.exists(app_path):
        print(f"✅ File found: {app_path}")
    else:
        print(f"❌ File missing: {app_path}")
        return

    # Cek Syntax Error dengan compile
    try:
        with open(app_path, 'r') as f:
            source = f.read()
        compile(source, app_path, 'exec')
        print("✅ Syntax Check: PASSED (Valid Python Code)")
    except Exception as e:
        print(f"❌ Syntax Check: FAILED ({str(e)})")
        return

    # Cek Ketersediaan Memory
    if os.path.exists('data/memory.json'):
        print("✅ Data Feed: CONNECTED (memory.json found)")
    else:
        print("⚠️ Data Feed: WARNING (memory.json missing, app will show error)")

    print("\nℹ️ NOTE: To view dashboard, run this command in terminal:")
    print("   streamlit run src/dashboard/app.py")

if __name__ == "__main__":
    check_app_integrity()
