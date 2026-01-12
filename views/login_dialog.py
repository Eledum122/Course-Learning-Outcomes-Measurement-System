"""
نافذة تسجيل الدخول
Login Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import COLORS, FONTS, WINDOW
from translations import t, set_language, get_language
from managers.access_control import AccessControl


class LoginDialog:
    """نافذة تسجيل الدخول"""
    
    def __init__(self, parent=None):
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title(t('login'))
        self.access_control = AccessControl()
        self.authenticated_user = None
        
        # تعيين الأيقونة والحجم
        self.setup_window()
        
        # إنشاء الواجهة
        self.create_widgets()
        
        # وضع النافذة في المنتصف
        self.center_window()
        
        # التركيز على حقل اسم المستخدم
        self.username_entry.focus()
        
        # ربط مفتاح Enter
        self.root.bind('<Return>', lambda e: self.login())
    
    def setup_window(self):
        """إعداد النافذة"""
        # حجم النافذة
        width = 500
        height = 600
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        
        # لون الخلفية
        self.root.configure(bg=COLORS['bg_main'])
    
    def center_window(self):
        """وضع النافذة في المنتصف"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        
        # ═══════════════════════════════════════════════════════════
        # الترويسة
        # ═══════════════════════════════════════════════════════════
        header_frame = tk.Frame(self.root, bg=COLORS['bg_header'], height=150)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # شعار الجامعة (نصي)
        logo_label = tk.Label(
            header_frame,
            text="🎓",
            font=('Arial', 48),
            bg=COLORS['bg_header'],
            fg=COLORS['text_white']
        )
        logo_label.pack(pady=10)
        
        # اسم الجامعة
        university_label = tk.Label(
            header_frame,
            text="University of Tabuk\nجامعة تبوك",
            font=FONTS['english_header'],
            bg=COLORS['bg_header'],
            fg=COLORS['text_white'],
            justify='center'
        )
        university_label.pack()
        
        # ═══════════════════════════════════════════════════════════
        # المحتوى الرئيسي
        # ═══════════════════════════════════════════════════════════
        main_frame = tk.Frame(self.root, bg=COLORS['bg_main'])
        main_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        # عنوان تسجيل الدخول
        title_label = tk.Label(
            main_frame,
            text=t('login'),
            font=FONTS['arabic_header'],
            bg=COLORS['bg_main'],
            fg=COLORS['primary_green']
        )
        title_label.pack(pady=(0, 20))
        
        # ═══════════════════════════════════════════════════════════
        # حقل اسم المستخدم
        # ═══════════════════════════════════════════════════════════
        username_label = tk.Label(
            main_frame,
            text=t('username'),
            font=FONTS['arabic_main'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        username_label.pack(anchor='w', pady=(10, 5))
        
        self.username_entry = ttk.Entry(
            main_frame,
            font=FONTS['english_main'],
            width=30
        )
        self.username_entry.pack(fill='x', ipady=8)
        
        # ═══════════════════════════════════════════════════════════
        # حقل كلمة المرور
        # ═══════════════════════════════════════════════════════════
        password_label = tk.Label(
            main_frame,
            text=t('password'),
            font=FONTS['arabic_main'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_primary']
        )
        password_label.pack(anchor='w', pady=(20, 5))
        
        self.password_entry = ttk.Entry(
            main_frame,
            font=FONTS['english_main'],
            show='●',
            width=30
        )
        self.password_entry.pack(fill='x', ipady=8)
        
        # ═══════════════════════════════════════════════════════════
        # خيارات إضافية
        # ═══════════════════════════════════════════════════════════
        options_frame = tk.Frame(main_frame, bg=COLORS['bg_main'])
        options_frame.pack(fill='x', pady=15)
        
        # تذكرني
        self.remember_var = tk.BooleanVar()
        remember_check = ttk.Checkbutton(
            options_frame,
            text=t('remember_me'),
            variable=self.remember_var
        )
        remember_check.pack(side='left')
        
        # اختيار اللغة
        lang_frame = tk.Frame(options_frame, bg=COLORS['bg_main'])
        lang_frame.pack(side='right')
        
        tk.Label(
            lang_frame,
            text=t('language') + ':',
            font=FONTS['arabic_small'],
            bg=COLORS['bg_main']
        ).pack(side='left', padx=(0, 5))
        
        self.language_var = tk.StringVar(value='en')  # Default to English
        language_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=['ar', 'en'],
            state='readonly',
            width=8
        )
        language_combo.pack(side='left')
        language_combo.bind('<<ComboboxSelected>>', self.change_language)
        
        # ═══════════════════════════════════════════════════════════
        # زر تسجيل الدخول
        # ═══════════════════════════════════════════════════════════
        self.login_button = tk.Button(
            main_frame,
            text=t('login'),
            font=FONTS['arabic_header'],
            bg=COLORS['btn_primary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['btn_primary_hover'],
            activeforeground=COLORS['text_white'],
            relief='flat',
            cursor='hand2',
            command=self.login
        )
        self.login_button.pack(fill='x', ipady=12, pady=(10, 0))
        
        # تأثير hover
        self.login_button.bind('<Enter>', lambda e: self.login_button.config(
            bg=COLORS['btn_primary_hover']))
        self.login_button.bind('<Leave>', lambda e: self.login_button.config(
            bg=COLORS['btn_primary']))
        
        # ═══════════════════════════════════════════════════════════
        # رسالة المعلومات الافتراضية
        # ═══════════════════════════════════════════════════════════
        info_label = tk.Label(
            main_frame,
            text="Default login: admin / admin123",
            font=FONTS['english_small'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary']
        )
        info_label.pack(pady=(20, 0))
    
    def change_language(self, event=None):
        """تغيير اللغة"""
        new_language = self.language_var.get()
        set_language(new_language)
        
        # إعادة إنشاء النافذة
        self.root.destroy()
        self.__init__()
    
    def login(self):
        """تسجيل الدخول"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # التحقق من البيانات
        if not username or not password:
            messagebox.showerror(
                t('error'),
                t('invalid_data'),
                parent=self.root
            )
            return
        
        # محاولة المصادقة
        user = self.access_control.authenticate(username, password)

        if user:
            self.authenticated_user = user

            # بدء الجلسة
            self.access_control.start_session(user)

            messagebox.showinfo(
                t('success'),
                f"{t('login_success')}\n{t('welcome')}: {user.full_name}",
                parent=self.root
            )
            self.root.destroy()
        else:
            messagebox.showerror(
                t('login_failed'),
                t('invalid_credentials'),
                parent=self.root
            )
            self.password_entry.delete(0, 'end')
            self.password_entry.focus()
    
    def run(self):
        """تشغيل النافذة"""
        self.root.mainloop()
        return self.authenticated_user, self.access_control


if __name__ == '__main__':
    login = LoginDialog()
    user, access_control = login.run()
    if user:
        print(f"Logged in as: {user.full_name}")
        print(f"Roles: {user.roles}")
        print(f"Permissions: {access_control.get_user_permissions(user.user_id)}")
