"""
تشخيص مشاكل التشغيل
Diagnose Startup Issues
"""

import sys
import os
import io

# تعيين الترميز UTF-8 للكونسول
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("DIAGNOSIS - تشخيص النظام")
print("=" * 70)
print()

# 1. معلومات Python
print("1. Python Information:")
print(f"   Version: {sys.version}")
print(f"   Executable: {sys.executable}")
print(f"   Platform: {sys.platform}")
print()

# 2. التحقق من المسار
print("2. Current Directory:")
current_dir = os.getcwd()
print(f"   {current_dir}")
expected_dir = r"d:\Dropbox\CLOs_Measurement_System_03"
if current_dir.lower() != expected_dir.lower():
    print(f"   WARNING: Expected directory is {expected_dir}")
print()

# 3. التحقق من وجود الملفات المهمة
print("3. Checking Important Files:")
important_files = [
    'main.py',
    'config.py',
    'translations.py',
    'views/login_dialog.py',
    'views/main_window.py',
    'managers/access_control.py',
    'utils/audit_logger.py',
    'managers/backup_manager.py',
    'dialogs/admin_user_management_dialog.py'
]

for file in important_files:
    exists = os.path.exists(file)
    status = "✓ OK" if exists else "✗ MISSING"
    print(f"   {status}: {file}")
print()

# 4. التحقق من tkinter
print("4. Checking Tkinter (GUI Library):")
try:
    import tkinter as tk
    print("   ✓ tkinter imported successfully")

    # اختبار إنشاء نافذة
    try:
        root = tk.Tk()
        root.withdraw()
        print("   ✓ Can create Tkinter window")
        root.destroy()
    except Exception as e:
        print(f"   ✗ Cannot create Tkinter window: {e}")
except ImportError as e:
    print(f"   ✗ tkinter not available: {e}")
    print("   SOLUTION: Install Python with tkinter support")
print()

# 5. التحقق من المكتبات المطلوبة
print("5. Checking Required Libraries:")
required_libs = [
    ('reportlab', 'ReportLab PDF library'),
    ('PIL', 'Pillow (PIL)'),
    ('arabic_reshaper', 'Arabic Reshaper'),
    ('bidi', 'Python BiDi')
]

missing_libs = []
for lib, desc in required_libs:
    try:
        __import__(lib)
        print(f"   ✓ {desc}")
    except ImportError:
        print(f"   ✗ {desc} - MISSING")
        missing_libs.append(lib)

if missing_libs:
    print()
    print("   TO INSTALL MISSING LIBRARIES:")
    print(f"   pip install {' '.join(missing_libs)}")
print()

# 6. اختبار استيراد الملفات الرئيسية
print("6. Testing Main Imports:")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

imports_to_test = [
    ('config', 'Configuration'),
    ('translations', 'Translations'),
    ('views.login_dialog', 'Login Dialog'),
    ('views.main_window', 'Main Window'),
    ('managers.access_control', 'Access Control'),
]

all_imports_ok = True
for module, desc in imports_to_test:
    try:
        __import__(module)
        print(f"   ✓ {desc}")
    except Exception as e:
        print(f"   ✗ {desc}: {e}")
        all_imports_ok = False
print()

# 7. اختبار GUI بسيط
print("7. Testing Simple GUI Window:")
try:
    import tkinter as tk
    from tkinter import messagebox

    def test_gui():
        root = tk.Tk()
        root.title("GUI Test")
        root.geometry("400x200")

        label = tk.Label(root, text="If you see this window, GUI is working!",
                        font=('Arial', 12))
        label.pack(pady=20)

        btn = tk.Button(root, text="Close", command=root.destroy,
                       bg='green', fg='white', padx=20, pady=10)
        btn.pack(pady=20)

        # إغلاق تلقائي بعد 3 ثواني
        root.after(3000, root.destroy)
        root.mainloop()

    print("   Opening test window for 3 seconds...")
    test_gui()
    print("   ✓ GUI test completed")

except Exception as e:
    print(f"   ✗ GUI test failed: {e}")
    import traceback
    traceback.print_exc()
print()

# 8. اختبار تسجيل الدخول
print("8. Testing Login System:")
try:
    from managers.access_control import AccessControl

    ac = AccessControl()
    print(f"   ✓ AccessControl created")
    print(f"   - Users in system: {len(ac.users)}")

    # اختبار تسجيل الدخول
    user = ac.authenticate('admin', 'admin123')
    if user:
        print(f"   ✓ Default admin login works")
        print(f"   - Username: {user.username}")
        print(f"   - Full name: {user.full_name}")
    else:
        print(f"   ✗ Default admin login failed")

except Exception as e:
    print(f"   ✗ Login system test failed: {e}")
    import traceback
    traceback.print_exc()
print()

# 9. النتائج والتوصيات
print("=" * 70)
print("RESULTS - النتائج")
print("=" * 70)

if all_imports_ok and not missing_libs:
    print()
    print("✓ ALL CHECKS PASSED - جميع الفحوصات نجحت")
    print()
    print("The system should work correctly.")
    print("النظام يجب أن يعمل بشكل صحيح.")
    print()
    print("TO RUN THE APPLICATION:")
    print("  Method 1: Double-click run.bat")
    print("  Method 2: python main.py")
    print("  Method 3: python run_app.py")
    print()
else:
    print()
    print("⚠ SOME ISSUES FOUND - تم اكتشاف بعض المشاكل")
    print()

    if missing_libs:
        print("Missing libraries - مكتبات مفقودة:")
        for lib in missing_libs:
            print(f"  - {lib}")
        print()
        print("Install with:")
        print(f"  pip install {' '.join(missing_libs)}")
        print()

    if not all_imports_ok:
        print("Some imports failed - بعض الاستيرادات فشلت")
        print("Check error messages above.")
        print()

print("=" * 70)
