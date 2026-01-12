"""
تشغيل البرنامج مباشرة
Run Application Directly
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import io

# تعيين الترميز UTF-8 للكونسول
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# إضافة المسار الحالي إلى مسار البحث
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Starting CLOs Measurement System")
print("=" * 60)

try:
    # استيراد المكونات
    print("Loading modules...")
    from config import DEFAULT_LANGUAGE
    from translations import set_language
    from views.login_dialog import LoginDialog
    from views.main_window import MainWindow

    print("Modules loaded successfully!")

    # تعيين اللغة الافتراضية
    set_language(DEFAULT_LANGUAGE)

    # عرض نافذة تسجيل الدخول
    print("\nOpening login dialog...")
    print("Please login with:")
    print("  Username: admin")
    print("  Password: admin123")
    print()

    login = LoginDialog()
    user, access_control = login.run()

    # إذا تم تسجيل الدخول بنجاح
    if user:
        print(f"\nLogin successful!")
        print(f"User: {user.full_name}")
        print(f"Username: {user.username}")
        print(f"Roles: {', '.join(user.roles)}")
        print()

        # فتح النافذة الرئيسية
        print("Opening main window...")
        app = MainWindow(user, access_control)
        app.run()

        print("\nApplication closed normally.")
    else:
        print("\nLogin cancelled.")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

    # عرض رسالة خطأ للمستخدم
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error",
            f"An error occurred:\n{str(e)}\n\nPlease check the console for details."
        )
        root.destroy()
    except:
        pass

print("\n" + "=" * 60)
print("Program terminated.")
print("=" * 60)
