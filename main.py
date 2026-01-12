"""
نظام قياس مخرجات التعلم للمقررات الدراسية
Course Learning Outcomes Measurement System

نقطة البداية الرئيسية للتطبيق
Main Entry Point

المؤلف: د. حسين يوسف العضيم
Author: Dr. Hussein Youssef Eledum

جامعة تبوك - قسم الإحصاء
University of Tabuk - Department of Statistics

الإصدار: 1.0
Version: 1.0
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# تعيين الترميز UTF-8 للكونسول
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# إضافة المسار الحالي إلى مسار البحث
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_LANGUAGE, APP_NAME_AR, APP_NAME_EN, VERSION
from translations import set_language
from views.login_dialog import LoginDialog
from views.main_window import MainWindow


def main():
    """الدالة الرئيسية"""
    
    print("=" * 60)
    print(f"{APP_NAME_EN}")
    print(f"{APP_NAME_AR}")
    print(f"Version {VERSION}")
    print("=" * 60)
    print()
    
    # تعيين اللغة الافتراضية
    set_language(DEFAULT_LANGUAGE)
    
    try:
        # عرض نافذة تسجيل الدخول
        print("Starting login dialog...")
        login = LoginDialog()
        user, access_control = login.run()
        
        # إذا تم تسجيل الدخول بنجاح
        if user:
            print(f"\n✓ Login successful!")
            print(f"  User: {user.full_name}")
            print(f"  Username: {user.username}")
            print(f"  Roles: {', '.join(user.roles)}")
            print(f"  User ID: {user.user_id}")
            print()
            
            # فتح النافذة الرئيسية
            print("Opening main window...")
            app = MainWindow(user, access_control)
            app.run()
            
            print("\nApplication closed.")
        else:
            print("\n✗ Login cancelled or failed.")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
        # عرض رسالة خطأ للمستخدم
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error",
            f"An error occurred:\n{str(e)}\n\nPlease check the console for details."
        )
        root.destroy()


if __name__ == '__main__':
    main()
