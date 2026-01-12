"""
حوار اختيار مقرر
Course Selection Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models import Course
from models.user import User
from managers.course_manager import CourseManager
from managers.access_control import AccessControl
from config import FONTS
from translations import t


class CourseSelectionDialog(tk.Toplevel):
    """حوار اختيار مقرر"""

    def __init__(self, parent, language: str = 'ar', user: User = None, access_control: AccessControl = None):
        super().__init__(parent)

        self.language = language
        self.user = user
        self.access_control = access_control
        self.selected_course = None

        # إعداد النافذة
        self.title("اختيار مقرر" if language == 'ar' else "Select Course")
        self.geometry("750x600")
        self.resizable(True, True)
        self.configure(bg='#f5f5f5')

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # إنشاء الواجهة
        self._create_widgets()

        # تحميل المقررات
        self._load_courses()

        # مركزة النافذة
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # الإطار الرئيسي مع padding
        main_frame = tk.Frame(self, bg='#f5f5f5', padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # إطار العنوان مع خلفية ملونة
        header_frame = tk.Frame(main_frame, bg='#1976D2', padx=20, pady=15)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # العنوان
        title_text = "اختر المقرر" if self.language == 'ar' else "Select Course"
        tk.Label(
            header_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='#1976D2',
            fg='white'
        ).pack()

        # إطار القائمة
        list_frame = tk.LabelFrame(
            main_frame,
            text="  المقررات المتاحة:  " if self.language == 'ar' else "  Available Courses:  ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#1976D2',
            padx=15,
            pady=15,
            relief=tk.GROOVE,
            borderwidth=2
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # الجدول
        columns = ('code', 'title')

        # إطار الجدول مع شريط التمرير
        tree_frame = tk.Frame(list_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # إنشاء نمط مخصص للـ Treeview
        style = ttk.Style()
        style.theme_use('clam')

        # تخصيص الألوان
        style.configure('Custom.Treeview',
                       background='#fafafa',
                       foreground='#333',
                       fieldbackground='#fafafa',
                       borderwidth=0,
                       font=('Arial', 10))

        style.configure('Custom.Treeview.Heading',
                       background='#1976D2',
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       borderwidth=1,
                       relief=tk.FLAT)

        style.map('Custom.Treeview',
                 background=[('selected', '#1976D2')],
                 foreground=[('selected', 'white')])

        style.map('Custom.Treeview.Heading',
                 background=[('active', '#1565C0')])

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15,
            style='Custom.Treeview'
        )
        scrollbar.config(command=self.tree.yview)

        # تعريف الأعمدة
        if self.language == 'ar':
            headers = {
                'code': 'رمز المقرر',
                'title': 'اسم المقرر'
            }
        else:
            headers = {
                'code': 'Course Code',
                'title': 'Course Title'
            }

        # تعيين عناوين الأعمدة وعرضها
        widths = {
            'code': 180,
            'title': 450
        }

        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor='w')

        self.tree.pack(fill=tk.BOTH, expand=True, padx=(0, 5))

        # ربط حدث النقر المزدوج
        self.tree.bind('<Double-1>', lambda e: self._select_course())

        # الأزرار
        buttons_frame = tk.Frame(main_frame, bg='#f5f5f5')
        buttons_frame.pack(pady=(5, 0), fill=tk.X)

        # إطار مركزي للأزرار
        center_buttons = tk.Frame(buttons_frame, bg='#f5f5f5')
        center_buttons.pack()

        # زر اختيار
        select_text = "Select" if self.language == 'en' else "اختيار"
        self.select_btn = tk.Button(
            center_buttons,
            text=select_text,
            command=self._select_course,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=20,
            height=2,
            cursor='hand2',
            relief=tk.FLAT,
            borderwidth=0,
            activebackground='#45a049',
            activeforeground='white'
        )
        self.select_btn.pack(side=tk.LEFT, padx=8)

        # تأثير hover للزر
        self.select_btn.bind('<Enter>', lambda e: self.select_btn.config(bg='#45a049'))
        self.select_btn.bind('<Leave>', lambda e: self.select_btn.config(bg='#4CAF50'))

        # زر إلغاء
        cancel_text = "Cancel" if self.language == 'en' else "إلغاء"
        self.cancel_btn = tk.Button(
            center_buttons,
            text=cancel_text,
            command=self.destroy,
            bg='#757575',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=20,
            height=2,
            cursor='hand2',
            relief=tk.FLAT,
            borderwidth=0,
            activebackground='#616161',
            activeforeground='white'
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=8)

        # تأثير hover للزر
        self.cancel_btn.bind('<Enter>', lambda e: self.cancel_btn.config(bg='#616161'))
        self.cancel_btn.bind('<Leave>', lambda e: self.cancel_btn.config(bg='#757575'))

    def _load_courses(self):
        """تحميل المقررات المتاحة"""
        cm = CourseManager()
        courses_info = cm.list_all_courses()

        # الحصول على أسماء البرامج المسموحة لمنسق البرنامج
        allowed_program_names = []
        allowed_course_ids = []
        if self.user and self.access_control:
            allowed_program_names = self.access_control.get_program_names_for_user(self.user)
            allowed_course_ids = self.access_control.get_allowed_course_ids_for_user(self.user)

        # تصفية المقررات حسب البرنامج الأكاديمي لمنسق البرنامج
        filtered_courses = []
        for course_info in courses_info:
            course_id = course_info['course_id']

            # تصفية حسب معرفات المقررات (منسق مقرر أو مدرس شعبة)
            if allowed_course_ids:
                if course_id not in allowed_course_ids:
                    continue  # تجاوز هذا المقرر

            # تصفية حسب البرنامج الأكاديمي (منسق برنامج)
            if allowed_program_names:
                course = cm.load_course(course_id)
                if course:
                    course_program = getattr(course.info, 'program', None)
                    if course_program not in allowed_program_names:
                        continue  # تجاوز هذا المقرر

            filtered_courses.append(course_info)

        # فرز المقررات حسب الرمز
        filtered_courses.sort(key=lambda c: c['course_code'])

        for course_info in filtered_courses:
            self.tree.insert('', 'end', values=(
                course_info['course_code'],
                course_info['course_title']
            ))

        self.all_courses_info = filtered_courses

    def _select_course(self):
        """اختيار المقرر"""
        selection = self.tree.selection()

        if not selection:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار مقرر" if self.language == 'ar' else "Please select a course",
                parent=self
            )
            return

        # الحصول على المقرر المختار
        item = selection[0]
        values = self.tree.item(item, 'values')
        course_code = values[0]

        # البحث عن المقرر في القائمة
        course_info = None
        for c_info in self.all_courses_info:
            if c_info['course_code'] == course_code:
                course_info = c_info
                break

        if not course_info:
            messagebox.showerror(
                t('error', self.language),
                "فشل تحميل المقرر" if self.language == 'ar' else "Failed to load course",
                parent=self
            )
            return

        # تحميل المقرر
        cm = CourseManager()
        self.selected_course = cm.load_course(course_info['course_id'])

        if not self.selected_course:
            messagebox.showerror(
                t('error', self.language),
                "فشل تحميل المقرر" if self.language == 'ar' else "Failed to load course",
                parent=self
            )
            return

        # إغلاق النافذة
        self.destroy()
