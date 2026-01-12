"""
نافذة إدارة بيانات المقرر - المرحلة الأولى
Course Data Management Dialog - Stage 1
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from datetime import datetime
from tkcalendar import DateEntry

from models.course import Course, CourseInfo, CLO, Topic, AssessmentActivity, Semester, CLOCategory
from managers.course_manager import CourseManager
from managers.academic_program_manager import AcademicProgramManager
from translations import t
from config import COLORS, FONTS
from utils.excel_template_utils import ExcelTemplateGenerator, ExcelTemplateReader


class Stage1CourseDialog(tk.Toplevel):
    """نافذة إدارة بيانات المقرر - المرحلة الأولى"""

    def __init__(self, parent, course_manager: CourseManager, current_user,
                 course_id: Optional[str] = None, language='ar', access_control=None):
        super().__init__(parent)

        self.course_manager = course_manager
        self.current_user = current_user
        self.access_control = access_control
        self.course_id = course_id
        self.language = language
        self.course: Optional[Course] = None
        self.is_new_course = False  # علامة لتتبع المقررات الجديدة غير المحفوظة
        self.course_saved = False   # علامة لتتبع ما إذا تم حفظ المقرر مرة واحدة على الأقل

        # تهيئة مدير البرامج الأكاديمية
        self.program_manager = AcademicProgramManager()

        # تحميل المقرر إذا كان موجوداً
        if self.course_id:
            self.course = self.course_manager.load_course(self.course_id)
            self.course_saved = True  # المقررات الموجودة محفوظة بالفعل
        else:
            # إنشاء كائن مقرر جديد بدون حفظه في قاعدة البيانات
            new_id = f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.course = Course(new_id)
            self.course.created_by = current_user.username
            self.course_id = new_id
            self.is_new_course = True  # مقرر جديد لم يُحفظ بعد
            self.course_saved = False  # لم يتم حفظه بعد

        if not self.course:
            messagebox.showerror(
                t("error", language),
                t("error_loading_course", language),
                parent=self
            )
            self.destroy()
            return

        # حالة تعديل غير محفوظة
        self.is_dirty = False

        # اعتراض زر الإغلاق لتأكيد الحفظ
        self.protocol('WM_DELETE_WINDOW', self.on_close)

        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.title(t("stage1_course_data", self.language))

        # تحديد حجم النافذة
        window_width = 900
        window_height = 650
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # إعدادات النافذة
        self.configure(bg=COLORS['bg'])

        # إطار الترويسة مع زر تبديل اللغة
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # العنوان
        title_label = ttk.Label(
            header_frame,
            text=t("stage1_course_data", self.language),
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header']
        )
        title_label.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

        # زر تبديل اللغة
        lang_btn = ttk.Button(
            header_frame,
            text="🌐 EN" if self.language == 'ar' else "🌐 عربي",
            command=self.toggle_language,
            width=10
        )
        lang_btn.pack(side=tk.LEFT if self.language == 'ar' else tk.RIGHT, padx=10)

        # إنشاء Notebook للتبويبات
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # التبويبات
        self.create_info_tab()
        self.create_clos_tab()
        self.create_topics_tab()
        self.create_activities_tab()
        # ملاحظة: جدول المواصفات جزء من المرحلة الثانية، لذا لا نعرضه هنا
        
        # أزرار التحكم
        self.create_control_buttons()
        
        # تحميل البيانات
        self.load_data()
    
    def create_info_tab(self):
        """إنشاء تبويب معلومات المقرر"""
        is_rtl = (self.language == 'ar')

        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=t("course_information", self.language))

        # إنشاء Canvas و Scrollbar
        canvas = tk.Canvas(tab, bg='#F8F9FA')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F8F9FA')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # الحقول
        self.info_entries = {}

        # الحقول العادية
        fields = [
            ('course_title', t("course_title", self.language), '#E3F2FD', '#1976D2'),      # أزرق
            ('course_code', t("course_code", self.language), '#F3E5F5', '#7B1FA2'),        # بنفسجي
            ('version', t("version", self.language), '#E8F5E9', '#388E3C'),                # أخضر
            ('faculty', t("faculty", self.language), '#E0F2F1', '#00796B'),                # تركواز
            ('department', t("department", self.language), '#FFF3E0', '#F57C00'),          # برتقالي
            ('program', t("program", self.language), '#FCE4EC', '#C2185B'),                # وردي
        ]

        for i, (field, label, bg_color, border_color) in enumerate(fields):
            # إطار خارجي ملون
            outer_frame = tk.Frame(scrollable_frame, bg=bg_color,
                                  highlightbackground=border_color,
                                  highlightthickness=2)
            outer_frame.pack(fill=tk.X, padx=20, pady=8)

            # إطار داخلي
            inner_frame = tk.Frame(outer_frame, bg=bg_color)
            inner_frame.pack(fill=tk.X, padx=15, pady=12)

            # العنوان والحقل حسب الاتجاه
            if is_rtl:
                # العربية: العنوان على اليمين، الحقل على اليسار
                label_widget = tk.Label(inner_frame, text=label,
                                       font=FONTS['normal'],
                                       bg=bg_color, fg=border_color,
                                       anchor='e', width=20)
                label_widget.pack(side=tk.RIGHT, padx=(10, 5))

                # استخدام Combobox للكلية والقسم والبرنامج
                if field == 'faculty':
                    colleges = self.program_manager.get_unique_colleges_ar() if self.language == 'ar' else self.program_manager.get_unique_colleges_en()
                    entry = ttk.Combobox(inner_frame, font=FONTS['normal'], values=colleges, state='readonly')
                elif field == 'department':
                    departments = self.program_manager.get_unique_departments_ar() if self.language == 'ar' else self.program_manager.get_unique_departments_en()
                    entry = ttk.Combobox(inner_frame, font=FONTS['normal'], values=departments, state='readonly')
                elif field == 'program':
                    # تصفية البرامج حسب صلاحيات المستخدم
                    all_programs = self.program_manager.get_all_programs()
                    if self.current_user.has_role('admin'):
                        # المدير يرى جميع البرامج
                        accessible_programs = all_programs
                    elif self.current_user.has_role('program_coordinator'):
                        # منسق البرنامج يرى برامجه فقط
                        accessible_programs = [p for p in all_programs if p.program_id in self.current_user.assigned_programs]
                    else:
                        # المستخدمون الآخرون لا يمكنهم إنشاء أو تعديل مقررات
                        accessible_programs = []

                    program_names = [p.program_name_ar if self.language == 'ar' else p.program_name_en
                                    for p in accessible_programs]
                    entry = ttk.Combobox(inner_frame, font=FONTS['normal'], values=program_names, state='readonly')
                else:
                    entry = ttk.Entry(inner_frame, font=FONTS['normal'])
                entry.pack(side=tk.RIGHT, padx=(5, 10), fill=tk.X, expand=True)
            else:
                # الإنجليزية: العنوان على اليسار، الحقل على اليمين
                label_widget = tk.Label(inner_frame, text=label,
                                       font=FONTS['normal'],
                                       bg=bg_color, fg=border_color,
                                       anchor='w', width=20)
                label_widget.pack(side=tk.LEFT, padx=(5, 10))

                # استخدام Combobox للكلية والقسم والبرنامج
                if field == 'faculty':
                    colleges = self.program_manager.get_unique_colleges_ar() if self.language == 'ar' else self.program_manager.get_unique_colleges_en()
                    entry = ttk.Combobox(inner_frame, font=FONTS['normal'], values=colleges, state='readonly')
                elif field == 'department':
                    departments = self.program_manager.get_unique_departments_ar() if self.language == 'ar' else self.program_manager.get_unique_departments_en()
                    entry = ttk.Combobox(inner_frame, font=FONTS['normal'], values=departments, state='readonly')
                elif field == 'program':
                    # تصفية البرامج حسب صلاحيات المستخدم
                    all_programs = self.program_manager.get_all_programs()
                    if self.current_user.has_role('admin'):
                        # المدير يرى جميع البرامج
                        accessible_programs = all_programs
                    elif self.current_user.has_role('program_coordinator'):
                        # منسق البرنامج يرى برامجه فقط
                        accessible_programs = [p for p in all_programs if p.program_id in self.current_user.assigned_programs]
                    else:
                        # المستخدمون الآخرون لا يمكنهم إنشاء أو تعديل مقررات
                        accessible_programs = []

                    program_names = [p.program_name_ar if self.language == 'ar' else p.program_name_en
                                    for p in accessible_programs]
                    entry = ttk.Combobox(inner_frame, font=FONTS['normal'], values=program_names, state='readonly')
                else:
                    entry = ttk.Entry(inner_frame, font=FONTS['normal'])
                entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

            self.info_entries[field] = entry
            # تعقب التعديلات لتمكين حفظ آمن
            if field in ['faculty', 'department', 'program']:
                entry.bind('<<ComboboxSelected>>', lambda e: self.mark_dirty())
            else:
                entry.bind('<KeyRelease>', lambda e: self.mark_dirty())

        # حقل التاريخ للسنة الدراسية
        self._create_date_field(scrollable_frame, 'academic_year',
                                t("academic_year", self.language),
                                '#FFF8E1', '#FBC02D', is_rtl)

        # إدارة الكليات والأقسام المستفيدة
        self._create_beneficiary_section(scrollable_frame, is_rtl)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_date_field(self, parent, field_name, label_text, bg_color, border_color, is_rtl):
        """إنشاء حقل تاريخ"""
        # إطار خارجي ملون
        outer_frame = tk.Frame(parent, bg=bg_color,
                              highlightbackground=border_color,
                              highlightthickness=2)
        outer_frame.pack(fill=tk.X, padx=20, pady=8)

        # إطار داخلي
        inner_frame = tk.Frame(outer_frame, bg=bg_color)
        inner_frame.pack(fill=tk.X, padx=15, pady=12)

        # العنوان والحقل حسب الاتجاه
        if is_rtl:
            # العربية: العنوان على اليمين، الحقل على اليسار
            label_widget = tk.Label(inner_frame, text=label_text,
                                   font=FONTS['normal'],
                                   bg=bg_color, fg=border_color,
                                   anchor='e', width=20)
            label_widget.pack(side=tk.RIGHT, padx=(10, 5))

            date_entry = DateEntry(inner_frame, font=FONTS['normal'],
                                  date_pattern='yyyy-mm-dd',
                                  width=30)
            date_entry.pack(side=tk.RIGHT, padx=(5, 10), fill=tk.X, expand=True)
        else:
            # الإنجليزية: العنوان على اليسار، الحقل على اليمين
            label_widget = tk.Label(inner_frame, text=label_text,
                                   font=FONTS['normal'],
                                   bg=bg_color, fg=border_color,
                                   anchor='w', width=20)
            label_widget.pack(side=tk.LEFT, padx=(5, 10))

            date_entry = DateEntry(inner_frame, font=FONTS['normal'],
                                  date_pattern='yyyy-mm-dd',
                                  width=30)
            date_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

        self.info_entries[field_name] = date_entry
        date_entry.bind('<<DateEntrySelected>>', lambda e: self.mark_dirty())

    def _create_beneficiary_section(self, parent, is_rtl):
        """إنشاء قسم إدارة الكليات والأقسام المستفيدة"""
        # إطار رئيسي
        main_frame = tk.LabelFrame(
            parent,
            text="الكليات والأقسام المستفيدة" if is_rtl else "Beneficiary Faculties & Departments",
            font=FONTS['arabic_main'] if is_rtl else FONTS['english_main'],
            bg='#F5F5F5',
            fg='#1976D2',
            bd=2,
            relief=tk.GROOVE
        )
        main_frame.pack(fill=tk.X, padx=20, pady=10)

        # إطار مربع الخيار
        checkbox_frame = tk.Frame(main_frame, bg='#F5F5F5')
        checkbox_frame.pack(fill=tk.X, padx=15, pady=(10, 5))

        # متغير لتخزين حالة مربع الخيار
        self.taught_outside_dept_var = tk.BooleanVar(value=False)

        # مربع الخيار
        checkbox_text = "يُدرس المقرر خارج القسم" if is_rtl else "Course is taught outside the department"
        self.taught_outside_checkbox = tk.Checkbutton(
            checkbox_frame,
            text=checkbox_text,
            variable=self.taught_outside_dept_var,
            command=self._toggle_beneficiary_section,
            font=FONTS['normal'],
            bg='#F5F5F5',
            fg='#1976D2',
            activebackground='#F5F5F5',
            selectcolor='#E3F2FD',
            cursor='hand2'
        )

        if is_rtl:
            self.taught_outside_checkbox.pack(side=tk.RIGHT, padx=10)
        else:
            self.taught_outside_checkbox.pack(side=tk.LEFT, padx=10)

        content_frame = tk.Frame(main_frame, bg='#F5F5F5')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # حفظ المرجع للإطار الرئيسي للمحتوى لتفعيله/تعطيله لاحقاً
        self.beneficiary_content_frame = content_frame

        # قائمة لتخزين البيانات
        self.beneficiary_data = []  # [(faculty, department), ...]

        # إطار الإدخال
        input_frame = tk.Frame(content_frame, bg='#E3F2FD', bd=1, relief=tk.SOLID)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        input_inner = tk.Frame(input_frame, bg='#E3F2FD')
        input_inner.pack(fill=tk.X, padx=10, pady=10)

        # حقل الكلية (يأتي أولاً)
        faculty_frame = tk.Frame(input_inner, bg='#E3F2FD')
        faculty_frame.pack(fill=tk.X, pady=5)

        faculty_label = tk.Label(
            faculty_frame,
            text="الكلية المستفيدة:" if is_rtl else "Beneficiary Faculty:",
            font=FONTS['normal'],
            bg='#E3F2FD',
            fg='#1976D2',
            width=20,
            anchor='e' if is_rtl else 'w'
        )

        self.beneficiary_faculty_entry = ttk.Entry(faculty_frame, font=FONTS['normal'])

        if is_rtl:
            faculty_label.pack(side=tk.RIGHT, padx=(10, 5))
            self.beneficiary_faculty_entry.pack(side=tk.RIGHT, padx=(5, 10), fill=tk.X, expand=True)
        else:
            faculty_label.pack(side=tk.LEFT, padx=(5, 10))
            self.beneficiary_faculty_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

        # حقل القسم (يأتي ثانياً)
        dept_frame = tk.Frame(input_inner, bg='#E3F2FD')
        dept_frame.pack(fill=tk.X, pady=5)

        dept_label = tk.Label(
            dept_frame,
            text="القسم المستفيد:" if is_rtl else "Beneficiary Department:",
            font=FONTS['normal'],
            bg='#E3F2FD',
            fg='#1976D2',
            width=20,
            anchor='e' if is_rtl else 'w'
        )

        self.beneficiary_department_entry = ttk.Entry(dept_frame, font=FONTS['normal'])

        if is_rtl:
            dept_label.pack(side=tk.RIGHT, padx=(10, 5))
            self.beneficiary_department_entry.pack(side=tk.RIGHT, padx=(5, 10), fill=tk.X, expand=True)
        else:
            dept_label.pack(side=tk.LEFT, padx=(5, 10))
            self.beneficiary_department_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

        # زر الإضافة
        add_btn_frame = tk.Frame(input_inner, bg='#E3F2FD')
        add_btn_frame.pack(fill=tk.X, pady=5)

        self.beneficiary_add_btn = tk.Button(
            add_btn_frame,
            text="➕ " + ("إضافة" if is_rtl else "Add"),
            command=self._add_beneficiary,
            bg='#4CAF50',
            fg='white',
            font=FONTS['normal'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2
        )
        self.beneficiary_add_btn.pack(side=tk.RIGHT if is_rtl else tk.LEFT, padx=10)

        # جدول البيانات المضافة
        list_frame = tk.Frame(content_frame, bg='white', bd=1, relief=tk.SUNKEN)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # رأس الجدول
        header_frame = tk.Frame(list_frame, bg='#1976D2')
        header_frame.pack(fill=tk.X)

        headers = ["الكلية", "القسم", "حذف"] if is_rtl else ["Faculty", "Department", "Delete"]
        for header in headers:
            lbl = tk.Label(
                header_frame,
                text=header,
                font=FONTS['normal'],
                bg='#1976D2',
                fg='white',
                padx=10,
                pady=5
            )
            lbl.pack(side=tk.RIGHT if is_rtl else tk.LEFT, fill=tk.X, expand=True)

        # إطار قابل للتمرير للقائمة
        canvas = tk.Canvas(list_frame, bg='white', height=150)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.beneficiary_list_frame = tk.Frame(canvas, bg='white')

        self.beneficiary_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.beneficiary_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # تعطيل القسم افتراضياً حتى يتم تفعيل مربع الخيار
        self._toggle_beneficiary_section()

    def _toggle_beneficiary_section(self):
        """تفعيل أو تعطيل قسم الكليات والأقسام المستفيدة"""
        is_enabled = self.taught_outside_dept_var.get()

        # تغيير حالة الويدجيتس
        state = 'normal' if is_enabled else 'disabled'

        # تعطيل/تفعيل حقول الإدخال
        self.beneficiary_faculty_entry.config(state=state)
        self.beneficiary_department_entry.config(state=state)

        # تعطيل/تفعيل زر الإضافة
        if is_enabled:
            self.beneficiary_add_btn.config(state='normal', cursor='hand2')
        else:
            self.beneficiary_add_btn.config(state='disabled', cursor='arrow')

        # تغيير لون الإطار للإشارة إلى التعطيل
        if is_enabled:
            self.beneficiary_content_frame.config(bg='#F5F5F5')
        else:
            self.beneficiary_content_frame.config(bg='#E0E0E0')

        # تحديث جميع الإطارات الفرعية
        for widget in self.beneficiary_content_frame.winfo_children():
            self._update_widget_state(widget, is_enabled)

    def _update_widget_state(self, widget, is_enabled):
        """تحديث حالة الويدجيت وجميع أبنائه بشكل تكراري"""
        # تحديث لون الخلفية للإطارات
        if isinstance(widget, tk.Frame):
            if is_enabled:
                # استعادة اللون الأصلي
                try:
                    original_bg = widget.cget('bg')
                    if original_bg == '#E0E0E0':
                        widget.config(bg='#E3F2FD')
                except:
                    pass
            else:
                # تعطيل بتغيير اللون
                try:
                    current_bg = widget.cget('bg')
                    if current_bg in ['#E3F2FD', '#F5F5F5']:
                        widget.config(bg='#E0E0E0')
                except:
                    pass

        # تحديث حالة الأبناء بشكل تكراري
        try:
            for child in widget.winfo_children():
                self._update_widget_state(child, is_enabled)
        except:
            pass

    def _add_beneficiary(self):
        """إضافة كلية وقسم مستفيد"""
        faculty = self.beneficiary_faculty_entry.get().strip()
        department = self.beneficiary_department_entry.get().strip()

        if not faculty or not department:
            messagebox.showwarning(
                t("warning", self.language),
                "يرجى إدخال الكلية والقسم" if self.language == 'ar' else "Please enter both faculty and department",
                parent=self
            )
            return

        # إضافة للقائمة
        self.beneficiary_data.append((faculty, department))
        self.mark_dirty()

        # مسح الحقول
        self.beneficiary_faculty_entry.delete(0, tk.END)
        self.beneficiary_department_entry.delete(0, tk.END)

        # تحديث العرض
        self._refresh_beneficiary_list()

    def _refresh_beneficiary_list(self):
        """تحديث عرض قائمة الكليات والأقسام"""
        is_rtl = (self.language == 'ar')

        # مسح القائمة الحالية
        for widget in self.beneficiary_list_frame.winfo_children():
            widget.destroy()

        # عرض البيانات
        for idx, (faculty, department) in enumerate(self.beneficiary_data):
            row_bg = '#F5F5F5' if idx % 2 == 0 else 'white'
            row_frame = tk.Frame(self.beneficiary_list_frame, bg=row_bg)
            row_frame.pack(fill=tk.X, pady=1)

            # الكلية
            faculty_lbl = tk.Label(
                row_frame,
                text=faculty,
                font=FONTS['normal'],
                bg=row_bg,
                anchor='e' if is_rtl else 'w',
                padx=10,
                pady=5
            )
            faculty_lbl.pack(side=tk.RIGHT if is_rtl else tk.LEFT, fill=tk.X, expand=True)

            # القسم
            dept_lbl = tk.Label(
                row_frame,
                text=department,
                font=FONTS['normal'],
                bg=row_bg,
                anchor='e' if is_rtl else 'w',
                padx=10,
                pady=5
            )
            dept_lbl.pack(side=tk.RIGHT if is_rtl else tk.LEFT, fill=tk.X, expand=True)

            # زر الحذف
            delete_btn = tk.Button(
                row_frame,
                text="🗑",
                command=lambda i=idx: self._delete_beneficiary(i),
                bg='#F44336',
                fg='white',
                font=FONTS['normal'],
                cursor='hand2',
                width=3
            )
            delete_btn.pack(side=tk.RIGHT if is_rtl else tk.LEFT, padx=5, pady=2)

    def _delete_beneficiary(self, index):
        """حذف كلية وقسم من القائمة"""
        if 0 <= index < len(self.beneficiary_data):
            del self.beneficiary_data[index]
            self.mark_dirty()
            self._refresh_beneficiary_list()

    def create_clos_tab(self):
        """إنشاء تبويب نواتج التعلم"""
        is_rtl = (self.language == 'ar')

        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=t("learning_outcomes", self.language))

        header_font = FONTS['arabic_header'] if is_rtl else FONTS['english_header']

        # ═══════════════════════════════════════════════════════════
        # إطار الإضافة - بنظام ألوان بنفسجي أزرق محسّن
        # ═══════════════════════════════════════════════════════════
        top_frame = tk.LabelFrame(tab, text=t("add_clo", self.language),
                                 font=header_font,
                                 bg='#E8EAF6', fg='#3F51B5',
                                 bd=2, relief=tk.GROOVE)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        content_frame = tk.Frame(top_frame, bg='#E8EAF6')
        content_frame.pack(fill=tk.X, padx=15, pady=15)

        # صف 1: الكود والفئة بألوان مختلفة
        fields = [
            ('clo_code_entry', t("clo_code", self.language), '#E1F5FE', '#0277BD', 20),
            ('category_combo', t("category", self.language), '#F3E5F5', '#6A1B9A', 20),
        ]

        for field_name, label_text, bg_color, fg_color, width in fields:
            field_frame = tk.Frame(content_frame, bg=bg_color, bd=1, relief=tk.SOLID)
            field_frame.pack(fill=tk.X, pady=5)

            inner_frame = tk.Frame(field_frame, bg=bg_color)
            inner_frame.pack(fill=tk.X, padx=5, pady=5)

            label_widget = tk.Label(inner_frame, text=label_text,
                                   font=FONTS['normal'],
                                   bg=bg_color, fg=fg_color,
                                   width=15, anchor='e' if is_rtl else 'w')

            if field_name == 'category_combo':
                self.clo_category_var = tk.StringVar(value="Knowledge")
                entry = ttk.Combobox(inner_frame, textvariable=self.clo_category_var,
                                    values=["Knowledge", "Skills", "Values"],
                                    state="readonly", font=FONTS['normal'], width=width)
            else:
                entry = ttk.Entry(inner_frame, font=FONTS['normal'], width=width)
                setattr(self, field_name, entry)
                entry.bind('<KeyRelease>', lambda e: self.mark_dirty())

            if is_rtl:
                label_widget.pack(side=tk.RIGHT, padx=(10, 5))
                entry.pack(side=tk.RIGHT, padx=(5, 10), fill=tk.X, expand=True)
            else:
                label_widget.pack(side=tk.LEFT, padx=(5, 10))
                entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

        # صف 2: الوصف - مربع نص كبير
        desc_frame = tk.Frame(content_frame, bg='#FFF9C4', bd=1, relief=tk.SOLID)
        desc_frame.pack(fill=tk.X, pady=5)

        desc_inner = tk.Frame(desc_frame, bg='#FFF9C4')
        desc_inner.pack(fill=tk.X, padx=5, pady=5)

        desc_label = tk.Label(desc_inner, text=t("description", self.language),
                            font=FONTS['normal'], bg='#FFF9C4', fg='#F57F17',
                            width=15, anchor='e' if is_rtl else 'w')
        desc_label.pack(side=tk.RIGHT if is_rtl else tk.LEFT, padx=(10, 5), anchor='n')

        self.clo_desc_text = tk.Text(desc_inner, font=FONTS['normal'],
                                    width=60, height=3, wrap=tk.WORD,
                                    bg='#FFFFFF', relief=tk.SOLID, bd=1)
        self.clo_desc_text.pack(side=tk.RIGHT if is_rtl else tk.LEFT,
                               padx=(5, 10), fill=tk.X, expand=True)
        self.clo_desc_text.bind('<KeyRelease>', lambda e: self.mark_dirty())

        # صف 3: PLOs المرتبطة
        plos_frame = tk.Frame(content_frame, bg='#E8F5E9', bd=1, relief=tk.SOLID)
        plos_frame.pack(fill=tk.X, pady=5)

        plos_inner = tk.Frame(plos_frame, bg='#E8F5E9')
        plos_inner.pack(fill=tk.X, padx=5, pady=5)

        plos_label = tk.Label(plos_inner, text=t("aligned_plos", self.language),
                            font=FONTS['normal'], bg='#E8F5E9', fg='#2E7D32',
                            width=15, anchor='e' if is_rtl else 'w')

        self.clo_plos_entry = ttk.Entry(plos_inner, font=FONTS['normal'], width=40)
        self.clo_plos_entry.bind('<KeyRelease>', lambda e: self.mark_dirty())

        if is_rtl:
            plos_label.pack(side=tk.RIGHT, padx=(10, 5))
            self.clo_plos_entry.pack(side=tk.RIGHT, padx=(5, 10), fill=tk.X, expand=True)
        else:
            plos_label.pack(side=tk.LEFT, padx=(5, 10))
            self.clo_plos_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

        # أزرار بألوان جذابة
        btn_frame = tk.Frame(top_frame, bg='#E8EAF6')
        btn_frame.pack(pady=10)

        # Create buttons
        edit_btn = tk.Button(btn_frame, text="✏️ " + t("edit", self.language),
                            font=FONTS['normal'],
                            bg='#2196F3', fg='#FFFFFF',
                            relief=tk.FLAT, cursor='hand2',
                            padx=20, pady=8,
                            command=self.edit_clo)

        update_btn = tk.Button(btn_frame, text="🔄 " + t("update", self.language),
                              font=FONTS['normal'],
                              bg='#9C27B0', fg='#FFFFFF',
                              relief=tk.FLAT, cursor='hand2',
                              padx=20, pady=8,
                              command=self.update_clo,
                              state=tk.DISABLED)

        add_btn = tk.Button(btn_frame, text=t("add", self.language),
                           font=FONTS['normal'],
                           bg='#4CAF50', fg='#FFFFFF',
                           relief=tk.FLAT, cursor='hand2',
                           padx=20, pady=8,
                           command=self.add_clo)

        clear_btn = tk.Button(btn_frame, text=t("clear", self.language),
                             font=FONTS['normal'],
                             bg='#FF9800', fg='#FFFFFF',
                             relief=tk.FLAT, cursor='hand2',
                             padx=20, pady=8,
                             command=self.clear_clo_fields)

        # Store button references for later control
        self.edit_clo_btn = edit_btn
        self.update_clo_btn = update_btn
        self.add_clo_btn = add_btn

        # Arrange buttons based on language direction
        if is_rtl:
            clear_btn.pack(side=tk.LEFT, padx=5)
            add_btn.pack(side=tk.LEFT, padx=5)
            update_btn.pack(side=tk.LEFT, padx=5)
            edit_btn.pack(side=tk.LEFT, padx=5)
        else:
            edit_btn.pack(side=tk.RIGHT, padx=5)
            update_btn.pack(side=tk.RIGHT, padx=5)
            add_btn.pack(side=tk.RIGHT, padx=5)
            clear_btn.pack(side=tk.RIGHT, padx=5)

        # Excel buttons frame - only for new courses
        if self.is_new_course:
            excel_btn_frame = tk.Frame(top_frame, bg='#E8EAF6')
            excel_btn_frame.pack(pady=5)

            if is_rtl:
                # زر استيراد من Excel
                import_btn = tk.Button(excel_btn_frame,
                                      text="📥 استيراد من Excel",
                                      font=FONTS['normal'],
                                      bg='#2196F3', fg='#FFFFFF',
                                      relief=tk.FLAT, cursor='hand2',
                                      padx=20, pady=8,
                                      command=self.import_clos_from_excel)
                import_btn.pack(side=tk.LEFT, padx=5)

                # زر تحميل القالب
                template_btn = tk.Button(excel_btn_frame,
                                       text="📄 تحميل قالب Excel",
                                       font=FONTS['normal'],
                                       bg='#FF9800', fg='#FFFFFF',
                                       relief=tk.FLAT, cursor='hand2',
                                       padx=20, pady=8,
                                       command=self.download_clos_template)
                template_btn.pack(side=tk.LEFT, padx=5)
            else:
                # Download template button
                template_btn = tk.Button(excel_btn_frame,
                                       text="📄 Download Excel Template",
                                       font=FONTS['normal'],
                                       bg='#FF9800', fg='#FFFFFF',
                                       relief=tk.FLAT, cursor='hand2',
                                       padx=20, pady=8,
                                       command=self.download_clos_template)
                template_btn.pack(side=tk.RIGHT, padx=5)

                # Import from Excel button
                import_btn = tk.Button(excel_btn_frame,
                                      text="📥 Import from Excel",
                                      font=FONTS['normal'],
                                      bg='#2196F3', fg='#FFFFFF',
                                      relief=tk.FLAT, cursor='hand2',
                                      padx=20, pady=8,
                                      command=self.import_clos_from_excel)
                import_btn.pack(side=tk.RIGHT, padx=5)

        # ═══════════════════════════════════════════════════════════
        # إطار القائمة - بنظام ألوان بنفسجي محسّن
        # ═══════════════════════════════════════════════════════════
        bottom_frame = tk.LabelFrame(tab, text=t("clos_list", self.language),
                                     font=header_font,
                                     bg='#F3E5F5', fg='#6A1B9A',
                                     bd=2, relief=tk.GROOVE)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # تنسيق الجدول بألوان بنفسجية
        style = ttk.Style()
        style.configure("CLOs.Treeview",
                       background="#FFFFFF",
                       foreground="#4A148C",
                       rowheight=25,
                       fieldbackground="#FFFFFF",
                       font=FONTS['normal'])
        style.map('CLOs.Treeview',
                 background=[('selected', '#CE93D8')])
        style.configure("CLOs.Treeview.Heading",
                       font=header_font,
                       background="#9C27B0",
                       foreground="#FFFFFF")

        columns = ('code', 'category', 'description', 'plos')
        self.clos_tree = ttk.Treeview(bottom_frame, columns=columns,
                                     show='headings', height=8,
                                     style="CLOs.Treeview")

        col_headers = {
            'code': t("code", self.language),
            'category': t("category", self.language),
            'description': t("description", self.language),
            'plos': t("aligned_plos", self.language)
        }

        for col, header in col_headers.items():
            self.clos_tree.heading(col, text=header)
            if col == 'description':
                self.clos_tree.column(col, width=300)
            elif col == 'code':
                self.clos_tree.column(col, width=80)
            else:
                self.clos_tree.column(col, width=120)

        vsb = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.clos_tree.yview)
        hsb = ttk.Scrollbar(bottom_frame, orient="horizontal", command=self.clos_tree.xview)
        self.clos_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.clos_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)
        hsb.grid(row=1, column=0, sticky='ew', padx=10)

        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        # زر الحذف
        delete_frame = tk.Frame(bottom_frame, bg='#F3E5F5')
        delete_frame.grid(row=2, column=0, columnspan=2, pady=10)

        delete_btn = tk.Button(delete_frame, text="🗑️ " + t("delete_selected", self.language),
                              font=FONTS['normal'],
                              bg='#F44336', fg='#FFFFFF',
                              relief=tk.FLAT, cursor='hand2',
                              padx=20, pady=8,
                              command=self.delete_clo)
        delete_btn.pack()
    
    def create_topics_tab(self):
        """إنشاء تبويب الموضوعات"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=t("topics", self.language))

        is_rtl = (self.language == 'ar')

        # إطار العلوي - إضافة/تعديل - مع لون أخضر
        header_font = FONTS['arabic_header'] if is_rtl else FONTS['english_header']
        top_frame = tk.LabelFrame(tab, text=t("add_topic", self.language),
                                 font=header_font,
                                 bg='#E8F5E9', fg='#2E7D32',  # أخضر فاتح / Light Green
                                 bd=2, relief=tk.GROOVE)
        top_frame.pack(fill=tk.X, padx=20, pady=10)

        # Canvas for scrolling
        canvas = tk.Canvas(top_frame, bg='#F8F9FA', highlightthickness=0)
        scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F8F9FA')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الحقول مع الألوان والاتجاه الصحيح
        fields = [
            ('topic_num_entry', t("topic_number", self.language), '#E1F5FE', '#0277BD', 15),      # أزرق فاتح / Light Blue
            ('topic_hours_entry', t("contact_hours", self.language), '#FFF3E0', '#EF6C00', 15),   # برتقالي فاتح / Light Orange
            ('topic_title_entry', t("topic_title", self.language), '#F3E5F5', '#6A1B9A', 60),    # بنفسجي فاتح / Light Purple
        ]

        normal_font = FONTS['normal']

        for i, (field, label_text, bg_color, border_color, width) in enumerate(fields):
            # إطار خارجي ملون
            outer_frame = tk.Frame(scrollable_frame, bg=bg_color,
                                  highlightbackground=border_color,
                                  highlightthickness=2)
            outer_frame.pack(fill=tk.X, padx=20, pady=8)

            # إطار داخلي للعنوان والحقل
            inner_frame = tk.Frame(outer_frame, bg=bg_color)
            inner_frame.pack(fill=tk.X, padx=10, pady=10)

            # العنوان
            label_widget = tk.Label(inner_frame, text=label_text,
                                   font=normal_font,
                                   bg=bg_color, fg=border_color)

            # حقل الإدخال
            entry = ttk.Entry(inner_frame, font=normal_font, width=width)
            setattr(self, field, entry)
            entry.bind('<KeyRelease>', lambda e: self.mark_dirty())

            # ترتيب العناصر حسب الاتجاه
            if is_rtl:
                # العربية: العنوان يمين، الحقل يسار
                label_widget.pack(side=tk.RIGHT, padx=(10, 5))
                entry.pack(side=tk.RIGHT, padx=(5, 10), fill=tk.X, expand=True)
            else:
                # الإنجليزية: العنوان يسار، الحقل يمين
                label_widget.pack(side=tk.LEFT, padx=(5, 10))
                entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

        # إطار الأزرار تحت حقل Topic Title
        buttons_outer_frame = tk.Frame(scrollable_frame, bg='#E8F5E9',
                                      highlightbackground='#4CAF50',
                                      highlightthickness=2)
        buttons_outer_frame.pack(fill=tk.X, padx=20, pady=8)

        buttons_inner_frame = tk.Frame(buttons_outer_frame, bg='#E8F5E9')
        buttons_inner_frame.pack(pady=15)

        # إنشاء الأزرار بتنسيق أفضل
        edit_btn = tk.Button(
            buttons_inner_frame,
            text="✏️ " + t("edit", self.language),
            command=self.edit_topic,
            bg='#2196F3',
            fg='white',
            font=FONTS['normal'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=30,
            pady=10
        )

        update_btn = tk.Button(
            buttons_inner_frame,
            text="🔄 " + t("update", self.language),
            command=self.update_topic,
            bg='#9C27B0',
            fg='white',
            font=FONTS['normal'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=30,
            pady=10,
            state=tk.DISABLED
        )

        add_btn = tk.Button(
            buttons_inner_frame,
            text="➕ " + t("add", self.language),
            command=self.add_topic,
            bg='#4CAF50',
            fg='white',
            font=FONTS['normal'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=30,
            pady=10
        )

        clear_btn = tk.Button(
            buttons_inner_frame,
            text="🗑 " + t("clear", self.language),
            command=self.clear_topic_fields,
            bg='#FF9800',
            fg='white',
            font=FONTS['normal'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=30,
            pady=10
        )

        # Store button references
        self.edit_topic_btn = edit_btn
        self.update_topic_btn = update_btn
        self.add_topic_btn = add_btn

        # ترتيب الأزرار حسب الاتجاه
        if is_rtl:
            clear_btn.pack(side=tk.RIGHT, padx=10)
            add_btn.pack(side=tk.RIGHT, padx=10)
            update_btn.pack(side=tk.RIGHT, padx=10)
            edit_btn.pack(side=tk.RIGHT, padx=10)
        else:
            edit_btn.pack(side=tk.LEFT, padx=10)
            update_btn.pack(side=tk.LEFT, padx=10)
            add_btn.pack(side=tk.LEFT, padx=10)
            clear_btn.pack(side=tk.LEFT, padx=10)

        # Excel buttons for Topics - only for new courses
        if self.is_new_course:
            excel_buttons_frame = tk.Frame(scrollable_frame, bg='#E8F5E9',
                                           highlightbackground='#2196F3',
                                           highlightthickness=2)
            excel_buttons_frame.pack(fill=tk.X, padx=20, pady=8)

            excel_inner_frame = tk.Frame(excel_buttons_frame, bg='#E8F5E9')
            excel_inner_frame.pack(pady=15)

            template_btn = tk.Button(
                excel_inner_frame,
                text="📄 " + ("تحميل قالب Excel" if is_rtl else "Download Excel Template"),
                command=self.download_topics_template,
                bg='#FF9800',
                fg='white',
                font=FONTS['normal'],
                cursor='hand2',
                relief=tk.RAISED,
                bd=2,
                padx=30,
                pady=10
            )

            import_btn = tk.Button(
                excel_inner_frame,
                text="📥 " + ("استيراد من Excel" if is_rtl else "Import from Excel"),
                command=self.import_topics_from_excel,
                bg='#2196F3',
                fg='white',
                font=FONTS['normal'],
                cursor='hand2',
                relief=tk.RAISED,
                bd=2,
                padx=30,
                pady=10
            )

            if is_rtl:
                import_btn.pack(side=tk.RIGHT, padx=10)
                template_btn.pack(side=tk.RIGHT, padx=10)
            else:
                template_btn.pack(side=tk.LEFT, padx=10)
                import_btn.pack(side=tk.LEFT, padx=10)

        # إطار السفلي - قائمة الموضوعات - مع لون أخضر داكن
        bottom_frame = tk.LabelFrame(tab, text=t("topics_list", self.language),
                                    font=header_font,
                                    bg='#C8E6C9', fg='#1B5E20',  # أخضر متوسط / Medium Green
                                    bd=2, relief=tk.GROOVE)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview مع تحسينات الألوان
        columns = ('number', 'title', 'hours')

        style = ttk.Style()
        style.configure("Topics.Treeview",
                       background="#FFFFFF",
                       foreground="#1B5E20",
                       rowheight=25,
                       fieldbackground="#FFFFFF")
        style.map('Topics.Treeview',
                 background=[('selected', '#81C784')])  # أخضر عند التحديد

        self.topics_tree = ttk.Treeview(bottom_frame, columns=columns, show='headings',
                                       height=15, style="Topics.Treeview")

        # تعريف الأعمدة
        col_headers = {
            'number': t("number", self.language),
            'title': t("title", self.language),
            'hours': t("contact_hours", self.language)
        }

        for col, header in col_headers.items():
            self.topics_tree.heading(col, text=header)
            if col == 'title':
                self.topics_tree.column(col, width=600)
            else:
                self.topics_tree.column(col, width=100)

        # Scrollbars
        vsb = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.topics_tree.yview)
        hsb = ttk.Scrollbar(bottom_frame, orient="horizontal", command=self.topics_tree.xview)
        self.topics_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.topics_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)
        hsb.grid(row=1, column=0, sticky='ew', padx=10)

        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        # أزرار الحذف
        delete_frame = tk.Frame(bottom_frame, bg='#C8E6C9')
        delete_frame.grid(row=2, column=0, pady=10)

        ttk.Button(delete_frame, text=t("delete_selected", self.language),
                  command=self.delete_topic).pack(padx=5)
    
    def create_activities_tab(self):
        """إنشاء تبويب أنشطة التقييم"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=t("assessment_activities", self.language))

        is_rtl = (self.language == 'ar')

        # إطار العلوي - إضافة/تعديل - مع لون برتقالي
        header_font = FONTS['arabic_header'] if is_rtl else FONTS['english_header']
        top_frame = tk.LabelFrame(tab, text=t("add_activity", self.language),
                                 font=header_font,
                                 bg='#FFF3E0', fg='#E65100',  # برتقالي فاتح / Light Orange
                                 bd=2, relief=tk.GROOVE)
        top_frame.pack(fill=tk.X, padx=20, pady=10)

        # Canvas for scrolling
        canvas = tk.Canvas(top_frame, bg='#F8F9FA', highlightthickness=0)
        scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F8F9FA')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الحقول مع الألوان والاتجاه الصحيح
        fields = [
            ('activity_name_entry', t("activity_name", self.language), '#E3F2FD', '#1565C0', 40),    # أزرق فاتح / Light Blue
            ('activity_mark_entry', t("mark", self.language), '#FCE4EC', '#C2185B', 15),             # وردي فاتح / Light Pink
            ('activity_percent_entry', t("percentage", self.language) + " (%)", '#FFF9C4', '#F57F17', 15),  # أصفر فاتح / Light Yellow
            ('activity_timing_entry', t("timing", self.language), '#F3E5F5', '#7B1FA2', 35),        # بنفسجي فاتح / Light Purple
        ]

        normal_font = FONTS['normal']

        for i, (field, label_text, bg_color, border_color, width) in enumerate(fields):
            # إطار خارجي ملون
            outer_frame = tk.Frame(scrollable_frame, bg=bg_color,
                                  highlightbackground=border_color,
                                  highlightthickness=2)
            outer_frame.pack(fill=tk.X, padx=20, pady=8)

            # إطار داخلي للعنوان والحقل
            inner_frame = tk.Frame(outer_frame, bg=bg_color)
            inner_frame.pack(fill=tk.X, padx=10, pady=10)

            # العنوان
            label_widget = tk.Label(inner_frame, text=label_text,
                                   font=normal_font,
                                   bg=bg_color, fg=border_color)

            # حقل الإدخال
            entry = ttk.Entry(inner_frame, font=normal_font, width=width)
            setattr(self, field, entry)
            entry.bind('<KeyRelease>', lambda e: self.mark_dirty())

            # ترتيب العناصر حسب الاتجاه
            if is_rtl:
                # العربية: العنوان يمين، الحقل يسار
                label_widget.pack(side=tk.RIGHT, padx=(10, 5))
                entry.pack(side=tk.RIGHT, padx=(5, 10), fill=tk.X, expand=True)
            else:
                # الإنجليزية: العنوان يسار، الحقل يمين
                label_widget.pack(side=tk.LEFT, padx=(5, 10))
                entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

        # ربط بالمخرجات - إطار ملون منفصل
        clo_outer_frame = tk.Frame(scrollable_frame, bg='#E8EAF6',
                                   highlightbackground='#3F51B5',
                                   highlightthickness=2)
        clo_outer_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        clo_inner_frame = tk.Frame(clo_outer_frame, bg='#E8EAF6')
        clo_inner_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # العنوان في أعلى الإطار
        clo_label = tk.Label(clo_inner_frame, text=t("link_clos", self.language),
                            font=normal_font,
                            bg='#E8EAF6', fg='#3F51B5')
        clo_label.pack(side=tk.TOP, anchor='e' if is_rtl else 'w', pady=(0, 10))

        # إطار المخرجات يأخذ بقية المساحة
        self.clo_checks_frame = tk.Frame(clo_inner_frame, bg='#E8EAF6')
        self.clo_check_vars: dict = {}
        self.clo_checks_frame.pack(fill=tk.BOTH, expand=True)

        # سيتم تعبئة المربعات بواسطة refresh_clo_checkboxes()
        self.refresh_clo_checkboxes()

        # إطار الأزرار تحت صندوق Link to CLOs
        buttons_outer_frame = tk.Frame(scrollable_frame, bg='#FFF3E0',
                                      highlightbackground='#FF9800',
                                      highlightthickness=2)
        buttons_outer_frame.pack(fill=tk.X, padx=20, pady=8)

        buttons_inner_frame = tk.Frame(buttons_outer_frame, bg='#FFF3E0')
        buttons_inner_frame.pack(pady=15)

        # إنشاء الأزرار بتنسيق أفضل
        edit_btn = tk.Button(
            buttons_inner_frame,
            text="✏️ " + t("edit", self.language),
            command=self.edit_activity,
            bg='#2196F3',
            fg='white',
            font=FONTS['normal'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=10
        )

        update_btn = tk.Button(
            buttons_inner_frame,
            text="🔄 " + t("update", self.language),
            command=self.update_activity,
            bg='#9C27B0',
            fg='white',
            font=FONTS['normal'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )

        add_btn = tk.Button(
            buttons_inner_frame,
            text="➕ " + t("add", self.language),
            command=self.add_activity,
            bg='#4CAF50',
            fg='white',
            font=FONTS['normal'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=10
        )

        clear_btn = tk.Button(
            buttons_inner_frame,
            text="🗑 " + t("clear", self.language),
            command=self.clear_activity_fields,
            bg='#FF9800',
            fg='white',
            font=FONTS['normal'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=10
        )

        # حفظ مراجع الأزرار للتحكم بها لاحقاً
        self.edit_activity_btn = edit_btn
        self.update_activity_btn = update_btn
        self.add_activity_btn = add_btn

        # ترتيب الأزرار حسب الاتجاه
        if is_rtl:
            clear_btn.pack(side=tk.RIGHT, padx=5)
            add_btn.pack(side=tk.RIGHT, padx=5)
            update_btn.pack(side=tk.RIGHT, padx=5)
            edit_btn.pack(side=tk.RIGHT, padx=5)
        else:
            edit_btn.pack(side=tk.LEFT, padx=5)
            update_btn.pack(side=tk.LEFT, padx=5)
            add_btn.pack(side=tk.LEFT, padx=5)
            clear_btn.pack(side=tk.LEFT, padx=5)

        # Excel buttons for Activities - only for new courses
        if self.is_new_course:
            excel_buttons_frame = tk.Frame(scrollable_frame, bg='#FFF3E0',
                                           highlightbackground='#2196F3',
                                           highlightthickness=2)
            excel_buttons_frame.pack(fill=tk.X, padx=20, pady=8)

            excel_inner_frame = tk.Frame(excel_buttons_frame, bg='#FFF3E0')
            excel_inner_frame.pack(pady=15)

            template_btn = tk.Button(
                excel_inner_frame,
                text="📄 " + ("تحميل قالب Excel" if is_rtl else "Download Excel Template"),
                command=self.download_activities_template,
                bg='#FF9800',
                fg='white',
                font=FONTS['normal'],
                cursor='hand2',
                relief=tk.RAISED,
                bd=2,
                padx=30,
                pady=10
            )

            import_btn = tk.Button(
                excel_inner_frame,
                text="📥 " + ("استيراد من Excel" if is_rtl else "Import from Excel"),
                command=self.import_activities_from_excel,
                bg='#2196F3',
                fg='white',
                font=FONTS['normal'],
                cursor='hand2',
                relief=tk.RAISED,
                bd=2,
                padx=30,
                pady=10
            )

            if is_rtl:
                import_btn.pack(side=tk.RIGHT, padx=10)
                template_btn.pack(side=tk.RIGHT, padx=10)
            else:
                template_btn.pack(side=tk.LEFT, padx=10)
                import_btn.pack(side=tk.LEFT, padx=10)

        # إطار السفلي - قائمة الأنشطة - مع لون برتقالي داكن
        bottom_frame = tk.LabelFrame(tab, text=t("activities_list", self.language),
                                    font=header_font,
                                    bg='#FFE0B2', fg='#BF360C',  # برتقالي متوسط / Medium Orange
                                    bd=2, relief=tk.GROOVE)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview مع تحسينات الألوان + عمود Link to CLOs
        columns = ('name', 'mark', 'percentage', 'timing', 'linked_clos')  # إضافة عمود CLOs

        style = ttk.Style()
        style.configure("Activities.Treeview",
                       background="#FFFFFF",
                       foreground="#BF360C",
                       rowheight=25,
                       fieldbackground="#FFFFFF")
        style.map('Activities.Treeview',
                 background=[('selected', '#FFAB91')])  # برتقالي عند التحديد

        self.activities_tree = ttk.Treeview(bottom_frame, columns=columns, show='headings',
                                           height=15, style="Activities.Treeview")

        # تعريف الأعمدة مع إضافة Link to CLOs
        col_headers = {
            'name': t("name", self.language),
            'mark': t("mark", self.language),
            'percentage': t("percentage", self.language),
            'timing': t("timing", self.language),
            'linked_clos': t("link_clos", self.language)  # عمود جديد
        }

        for col, header in col_headers.items():
            self.activities_tree.heading(col, text=header)
            if col == 'name':
                self.activities_tree.column(col, width=250)
            elif col == 'timing':
                self.activities_tree.column(col, width=200)
            elif col == 'linked_clos':
                self.activities_tree.column(col, width=200)
            else:
                self.activities_tree.column(col, width=100)

        # Scrollbars
        vsb = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.activities_tree.yview)
        hsb = ttk.Scrollbar(bottom_frame, orient="horizontal", command=self.activities_tree.xview)
        self.activities_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.activities_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)
        hsb.grid(row=1, column=0, sticky='ew', padx=10)

        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        # أزرار الحذف
        delete_frame = tk.Frame(bottom_frame, bg='#FFE0B2')
        delete_frame.grid(row=2, column=0, pady=10)

        ttk.Button(delete_frame, text=t("delete_selected", self.language),
                  command=self.delete_activity).pack(padx=5)
    
    def create_specifications_tab(self):
        """إنشاء تبويب جدول المواصفات"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=t("table_of_specifications", self.language))
        
        # رسالة توضيحية
        info_label = ttk.Label(tab, 
                              text=t("specifications_info", self.language),
                              font=FONTS['normal'],
                              wraplength=1000)
        info_label.pack(pady=10)
        
        # إطار أعلى لإضافة مدخل في جدول المواصفات
        top_frame = ttk.LabelFrame(tab, text=t('add_specification', self.language))
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        fields_frame = ttk.Frame(top_frame)
        fields_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # اختيار رقم الموضوع
        ttk.Label(fields_frame, text=t('spec_topic', self.language), font=FONTS['normal']).grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        self.spec_topic_var = tk.StringVar()
        self.spec_topic_combo = ttk.Combobox(fields_frame, textvariable=self.spec_topic_var, values=[], state='readonly', width=10, font=FONTS['normal'])
        self.spec_topic_combo.grid(row=0, column=0, padx=5, pady=5)
        
        # اختيار مخرج التعلم
        ttk.Label(fields_frame, text=t('spec_clo', self.language), font=FONTS['normal']).grid(row=0, column=3, padx=5, pady=5, sticky=tk.E)
        self.spec_clo_var = tk.StringVar()
        self.spec_clo_combo = ttk.Combobox(fields_frame, textvariable=self.spec_clo_var, values=[], state='readonly', width=15, font=FONTS['normal'])
        self.spec_clo_combo.grid(row=0, column=2, padx=5, pady=5)
        
        # اختيار النشاط
        ttk.Label(fields_frame, text=t('spec_activity', self.language), font=FONTS['normal']).grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)
        self.spec_activity_var = tk.StringVar()
        self.spec_activity_combo = ttk.Combobox(fields_frame, textvariable=self.spec_activity_var, values=[], state='readonly', width=20, font=FONTS['normal'])
        self.spec_activity_combo.grid(row=1, column=0, padx=5, pady=5)
        
        # الدرجة داخل الجدول
        ttk.Label(fields_frame, text=t('spec_mark', self.language), font=FONTS['normal']).grid(row=1, column=3, padx=5, pady=5, sticky=tk.E)
        self.spec_mark_entry = ttk.Entry(fields_frame, font=FONTS['normal'], width=10)
        self.spec_mark_entry.grid(row=1, column=2, padx=5, pady=5)
        
        # أزرار
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text=t('add', self.language), command=self.add_specification).pack(side=tk.RIGHT, padx=5)
        
        # إطار السفلي - عرض مدخلات جدول المواصفات
        bottom_frame = ttk.LabelFrame(tab, text=t('table_of_specifications', self.language))
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('topic', 'clo', 'activity', 'mark')
        self.specs_tree = ttk.Treeview(bottom_frame, columns=columns, show='headings', height=10)
        headers = {
            'topic': t('spec_topic', self.language),
            'clo': t('spec_clo', self.language),
            'activity': t('spec_activity', self.language),
            'mark': t('spec_mark', self.language)
        }
        for col, header in headers.items():
            self.specs_tree.heading(col, text=header)
            self.specs_tree.column(col, width=150)
        
        vsb = ttk.Scrollbar(bottom_frame, orient='vertical', command=self.specs_tree.yview)
        self.specs_tree.configure(yscrollcommand=vsb.set)
        self.specs_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        # زر الحذف
        delete_frame = ttk.Frame(bottom_frame)
        delete_frame.grid(row=2, column=0, pady=5)
        ttk.Button(delete_frame, text=t('delete_selected', self.language), command=self.delete_specification).pack(side=tk.RIGHT, padx=5)
        
        # تهيئة القيم
        self.refresh_spec_widgets()
    
    def create_control_buttons(self):
        """إنشاء أزرار التحكم"""
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        is_rtl = (self.language == 'ar')

        # إنشاء الأزرار بناءً على اتجاه اللغة
        if is_rtl:
            # RTL: الأزرار من اليمين لليسار
            # زر الحفظ
            save_btn = tk.Button(control_frame, text="💾 " + t("save", self.language),
                                command=self.save_course, width=18,
                                bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                                relief=tk.RAISED, bd=2, cursor='hand2')
            save_btn.pack(side=tk.RIGHT, padx=5)

            # زر توليد التقرير
            report_btn = tk.Button(control_frame, text="📄 " + t("generate_report", self.language),
                                  command=self.generate_report, width=22,
                                  bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                                  relief=tk.RAISED, bd=2, cursor='hand2')
            report_btn.pack(side=tk.RIGHT, padx=5)

            # زر الإلغاء
            cancel_btn = tk.Button(control_frame, text="❌ " + t("cancel", self.language),
                                  command=self.on_close, width=18,
                                  bg='#9E9E9E', fg='white', font=('Arial', 10, 'bold'),
                                  relief=tk.RAISED, bd=2, cursor='hand2')
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            # زر المساعدة (على اليسار)
            help_btn = tk.Button(control_frame, text="❓ " + t("help", self.language),
                                command=self.show_help, width=18,
                                bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                                relief=tk.RAISED, bd=2, cursor='hand2')
            help_btn.pack(side=tk.LEFT, padx=5)
        else:
            # LTR: الأزرار من اليسار لليمين
            # زر المساعدة (على اليسار)
            help_btn = tk.Button(control_frame, text="❓ " + t("help", self.language),
                                command=self.show_help, width=18,
                                bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                                relief=tk.RAISED, bd=2, cursor='hand2')
            help_btn.pack(side=tk.LEFT, padx=5)

            # زر الإلغاء (على اليمين)
            cancel_btn = tk.Button(control_frame, text="❌ " + t("cancel", self.language),
                                  command=self.on_close, width=18,
                                  bg='#9E9E9E', fg='white', font=('Arial', 10, 'bold'),
                                  relief=tk.RAISED, bd=2, cursor='hand2')
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            # زر توليد التقرير
            report_btn = tk.Button(control_frame, text="📄 " + t("generate_report", self.language),
                                  command=self.generate_report, width=22,
                                  bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                                  relief=tk.RAISED, bd=2, cursor='hand2')
            report_btn.pack(side=tk.RIGHT, padx=5)

            # زر الحفظ
            save_btn = tk.Button(control_frame, text="💾 " + t("save", self.language),
                                command=self.save_course, width=18,
                                bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                                relief=tk.RAISED, bd=2, cursor='hand2')
            save_btn.pack(side=tk.RIGHT, padx=5)

    def mark_dirty(self, *_):
        """وضع علم أن هناك تغييرات غير محفوظة"""
        self.is_dirty = True

    def on_close(self):
        """معالجة إغلاق النافذة - نسأل المستخدم إذا كانت هناك تغييرات غير محفوظة"""
        try:
            # التحقق من وجود كود المقرر
            course_code = self.info_entries['course_code'].get().strip()

            if getattr(self, 'is_dirty', False):
                # إذا لم يكن هناك كود مقرر، لا نحتاج للحفظ
                if not course_code:
                    msg_ar = "لم يتم إدخال كود المقرر.\n\nهل تريد الخروج بدون حفظ؟"
                    msg_en = "Course Code not entered.\n\nDo you want to exit without saving?"

                    confirm = messagebox.askyesno(
                        t('warning', self.language),
                        msg_ar if self.language == 'ar' else msg_en,
                        parent=self
                    )
                    if confirm:
                        self.destroy()
                    return

                # إذا كان هناك كود مقرر، نسأل عن الحفظ
                res = messagebox.askyesnocancel(
                    t('save_changes_prompt', self.language),
                    t('save_changes_prompt_detail', self.language),
                    parent=self
                )
                # True = نعم (حفظ)، False = لا (رفض التغييرات)، None = إلغاء
                if res is None:
                    return
                if res is True:
                    saved = self.save_course()
                    if not saved:
                        return
                # إما تم الحفظ أو رفض الحفظ -> إغلاق
                self.destroy()
            else:
                # لا توجد تغييرات - إغلاق مباشر
                self.destroy()
        except Exception as e:
            messagebox.showerror(t('error', self.language), str(e), parent=self)
    
    # دوال إدارة نواتج التعلم
    def add_clo(self):
        """إضافة ناتج تعلم"""
        try:
            code = self.clo_code_entry.get().strip()
            if not code:
                messagebox.showwarning(
                    t("warning", self.language),
                    t("enter_clo_code", self.language),
                    parent=self
                )
                return
            
            category = CLOCategory(self.clo_category_var.get())
            clo = CLO(code, category)
            
            clo.description = self.clo_desc_text.get("1.0", tk.END).strip()
            clo.aligned_plos = self.clo_plos_entry.get().strip()
            # حقول الدرجة/معيار النجاح/المستوى المستهدف تخص المرحلة الثانية؛ نتركها بالقيم الافتراضية هنا
            
            # التحقق من الصحة (التحقق الخاص بالمرحلة الأولى: كود ووصف فقط)
            is_valid, error = clo.validate_stage1()
            if not is_valid:
                messagebox.showerror(
                    t("error", self.language),
                    error,
                    parent=self
                )
                return
            
            # الإضافة
            if not self.course.add_clo(clo):
                messagebox.showerror(
                    t("error", self.language),
                    t("clo_already_exists", self.language),
                    parent=self
                )
                return
            
            # تحديث القائمة
            self.refresh_clos_list()
            try:
                self.refresh_clo_checkboxes()
            except Exception:
                pass
            self.clear_clo_fields()
            # تعيين علم التعديل
            self.mark_dirty()
            
            messagebox.showinfo(
                t("success", self.language),
                t("clo_added_successfully", self.language),
                parent=self
            )
            
        except ValueError as e:
            messagebox.showerror(
                t("error", self.language),
                t("invalid_number_format", self.language),
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                str(e),
                parent=self
            )
    
    def delete_clo(self):
        """حذف ناتج تعلم"""
        selection = self.clos_tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                t("select_clo_to_delete", self.language),
                parent=self
            )
            return
        
        item = self.clos_tree.item(selection[0])
        clo_code = item['values'][0]
        
        result = messagebox.askyesno(
            t("confirm", self.language),
            t("confirm_delete_clo", self.language).format(clo_code),
            parent=self
        )
        
        if result:
            self.course.remove_clo(clo_code)
            self.refresh_clos_list()
            try:
                self.refresh_clo_checkboxes()
            except Exception:
                pass
            self.mark_dirty()
    
    def edit_clo(self):
        """تعديل ناتج تعلم محدد"""
        selection = self.clos_tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                "يرجى اختيار مخرج تعلم للتعديل" if self.language == 'ar' else "Please select a CLO to edit",
                parent=self
            )
            return

        # Get selected CLO data
        item = self.clos_tree.item(selection[0])
        clo_code = item['values'][0]

        # Find the CLO object
        for clo in self.course.clos:
            if clo.code == clo_code:
                # Fill fields with CLO data
                self.clo_code_entry.delete(0, tk.END)
                self.clo_code_entry.insert(0, clo.code)

                self.clo_category_var.set(clo.category.value if isinstance(clo.category, CLOCategory) else clo.category)

                self.clo_desc_text.delete("1.0", tk.END)
                self.clo_desc_text.insert("1.0", clo.description)

                self.clo_plos_entry.delete(0, tk.END)
                self.clo_plos_entry.insert(0, clo.aligned_plos)

                # Disable Add and Edit buttons, Enable Update button
                self.add_clo_btn.config(state=tk.DISABLED)
                self.edit_clo_btn.config(state=tk.DISABLED)
                self.update_clo_btn.config(state=tk.NORMAL)

                # Store the original code for updating
                self.editing_clo_code = clo_code
                break

    def update_clo(self):
        """تحديث ناتج تعلم"""
        try:
            code = self.clo_code_entry.get().strip()
            if not code:
                messagebox.showwarning(
                    t("warning", self.language),
                    t("enter_clo_code", self.language),
                    parent=self
                )
                return

            # Find the CLO to update
            clo_to_update = None
            for clo in self.course.clos:
                if clo.code == self.editing_clo_code:
                    clo_to_update = clo
                    break

            if clo_to_update:
                # Update CLO data
                clo_to_update.code = code
                clo_to_update.category = CLOCategory(self.clo_category_var.get())
                clo_to_update.description = self.clo_desc_text.get("1.0", tk.END).strip()
                clo_to_update.aligned_plos = self.clo_plos_entry.get().strip()

                # Validate
                is_valid, error = clo_to_update.validate_stage1()
                if not is_valid:
                    messagebox.showerror(
                        t("error", self.language),
                        error,
                        parent=self
                    )
                    return

                # Refresh and clear
                self.refresh_clos_list()
                try:
                    self.refresh_clo_checkboxes()
                except Exception:
                    pass
                self.clear_clo_fields()
                self.mark_dirty()

                # Re-enable buttons
                self.add_clo_btn.config(state=tk.NORMAL)
                self.edit_clo_btn.config(state=tk.NORMAL)
                self.update_clo_btn.config(state=tk.DISABLED)

                messagebox.showinfo(
                    t("success", self.language),
                    "تم تحديث المخرج بنجاح!" if self.language == 'ar' else "CLO updated successfully!",
                    parent=self
                )

        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                str(e),
                parent=self
            )

    def clear_clo_fields(self):
        """مسح حقول نواتج التعلم"""
        self.clo_code_entry.delete(0, tk.END)
        self.clo_desc_text.delete("1.0", tk.END)
        self.clo_plos_entry.delete(0, tk.END)
        self.clo_category_var.set("Knowledge")

        # Re-enable buttons when clearing
        if hasattr(self, 'add_clo_btn'):
            self.add_clo_btn.config(state=tk.NORMAL)
            self.edit_clo_btn.config(state=tk.NORMAL)
            self.update_clo_btn.config(state=tk.DISABLED)
    
    def refresh_clos_list(self):
        """تحديث قائمة نواتج التعلم"""
        # مسح القائمة
        for item in self.clos_tree.get_children():
            self.clos_tree.delete(item)
        
        # إضافة العناصر
        for clo in self.course.clos:
            self.clos_tree.insert('', 'end', values=(
                clo.code,
                clo.category.value if hasattr(clo.category, 'value') else clo.category,
                    clo.description[:50] + '...' if len(clo.description) > 50 else clo.description,
                clo.aligned_plos
            ))
    
    # دوال إدارة الموضوعات
    def add_topic(self):
        """إضافة موضوع"""
        try:
            number = int(self.topic_num_entry.get())
            title = self.topic_title_entry.get().strip()
            hours = float(self.topic_hours_entry.get())
            
            topic = Topic(number)
            topic.title = title
            topic.contact_hours = hours
            
            # التحقق من الصحة
            is_valid, error = topic.validate()
            if not is_valid:
                messagebox.showerror(
                    t("error", self.language),
                    error,
                    parent=self
                )
                return
            
            # الإضافة
            if not self.course.add_topic(topic):
                messagebox.showerror(
                    t("error", self.language),
                    t("topic_already_exists", self.language),
                    parent=self
                )
                return
            
            # تحديث القائمة
            self.refresh_topics_list()
            self.clear_topic_fields()
            
            messagebox.showinfo(
                t("success", self.language),
                t("topic_added_successfully", self.language),
                parent=self
            )
            self.mark_dirty()
        except ValueError:
            messagebox.showerror(
                t("error", self.language),
                t("invalid_number_format", self.language),
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                str(e),
                parent=self
            )
    
    def delete_topic(self):
        """حذف موضوع"""
        selection = self.topics_tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                t("select_topic_to_delete", self.language),
                parent=self
            )
            return
        
        item = self.topics_tree.item(selection[0])
        topic_number = int(item['values'][0])
        
        result = messagebox.askyesno(
            t("confirm", self.language),
            t("confirm_delete_topic", self.language).format(topic_number),
            parent=self
        )
        
        if result:
            self.course.remove_topic(topic_number)
            self.refresh_topics_list()
            self.mark_dirty()
    
    def edit_topic(self):
        """تعديل موضوع محدد"""
        selection = self.topics_tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                "يرجى اختيار موضوع للتعديل" if self.language == 'ar' else "Please select a topic to edit",
                parent=self
            )
            return

        # Get selected topic data
        item = self.topics_tree.item(selection[0])
        topic_number = item['values'][0]

        # Find the topic object
        for topic in self.course.topics:
            if topic.number == topic_number:
                # Fill fields with topic data
                self.topic_num_entry.delete(0, tk.END)
                self.topic_num_entry.insert(0, str(topic.number))

                self.topic_title_entry.delete(0, tk.END)
                self.topic_title_entry.insert(0, topic.title)

                self.topic_hours_entry.delete(0, tk.END)
                self.topic_hours_entry.insert(0, str(topic.contact_hours))

                # Disable Add and Edit buttons, Enable Update button
                self.add_topic_btn.config(state=tk.DISABLED)
                self.edit_topic_btn.config(state=tk.DISABLED)
                self.update_topic_btn.config(state=tk.NORMAL)

                # Store the original number for updating
                self.editing_topic_number = topic_number
                break

    def update_topic(self):
        """تحديث موضوع"""
        try:
            number = int(self.topic_num_entry.get().strip())
            title = self.topic_title_entry.get().strip()
            hours = float(self.topic_hours_entry.get().strip())

            if not title:
                messagebox.showwarning(
                    t("warning", self.language),
                    "يرجى إدخال عنوان الموضوع" if self.language == 'ar' else "Please enter topic title",
                    parent=self
                )
                return

            # Find the topic to update
            topic_to_update = None
            for topic in self.course.topics:
                if topic.number == self.editing_topic_number:
                    topic_to_update = topic
                    break

            if topic_to_update:
                # Update topic data
                topic_to_update.number = number
                topic_to_update.title = title
                topic_to_update.contact_hours = hours

                # Refresh and clear
                self.refresh_topics_list()
                self.clear_topic_fields()
                self.mark_dirty()

                # Re-enable buttons
                self.add_topic_btn.config(state=tk.NORMAL)
                self.edit_topic_btn.config(state=tk.NORMAL)
                self.update_topic_btn.config(state=tk.DISABLED)

                messagebox.showinfo(
                    t("success", self.language),
                    "تم تحديث الموضوع بنجاح!" if self.language == 'ar' else "Topic updated successfully!",
                    parent=self
                )

        except ValueError:
            messagebox.showerror(
                t("error", self.language),
                t("invalid_number_format", self.language),
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                str(e),
                parent=self
            )

    def clear_topic_fields(self):
        """مسح حقول الموضوعات"""
        self.topic_num_entry.delete(0, tk.END)
        self.topic_title_entry.delete(0, tk.END)
        self.topic_hours_entry.delete(0, tk.END)

        # Re-enable buttons when clearing
        if hasattr(self, 'add_topic_btn'):
            self.add_topic_btn.config(state=tk.NORMAL)
            self.edit_topic_btn.config(state=tk.NORMAL)
            self.update_topic_btn.config(state=tk.DISABLED)

    def refresh_topics_list(self):
        """تحديث قائمة الموضوعات"""
        # مسح القائمة
        for item in self.topics_tree.get_children():
            self.topics_tree.delete(item)
        
        # إضافة العناصر
        for topic in self.course.topics:
            self.topics_tree.insert('', 'end', values=(
                topic.number,
                topic.title,
                topic.contact_hours
            ))
    
    # دوال إدارة الأنشطة
    def add_activity(self):
        """إضافة نشاط تقييم"""
        try:
            name = self.activity_name_entry.get().strip()
            if not name:
                messagebox.showwarning(
                    t("warning", self.language),
                    t("enter_activity_name", self.language),
                    parent=self
                )
                return
            
            activity = AssessmentActivity(name)
            activity.mark = float(self.activity_mark_entry.get())
            activity.percentage = float(self.activity_percent_entry.get())
            activity.timing = self.activity_timing_entry.get().strip()
            
            # قراءة المخرجات المحددة من الـ Listbox
            # اقرأ المخرجات المحددة من مربعات الاختيار
            selected = [code for code, var in self.clo_check_vars.items() if var.get()]
            activity.measures_clos = selected
            
            # التحقق من الصحة
            is_valid, error = activity.validate()
            if not is_valid:
                messagebox.showerror(
                    t("error", self.language),
                    error,
                    parent=self
                )
                return
            
            # الإضافة
            if not self.course.add_activity(activity):
                messagebox.showerror(
                    t("error", self.language),
                    t("activity_already_exists", self.language),
                    parent=self
                )
                return
            
            # تحديث القائمة
            self.refresh_activities_list()
            self.clear_activity_fields()
            
            messagebox.showinfo(
                t("success", self.language),
                t("activity_added_successfully", self.language),
                parent=self
            )
            self.mark_dirty()
        except ValueError:
            messagebox.showerror(
                t("error", self.language),
                t("invalid_number_format", self.language),
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                str(e),
                parent=self
            )
    
    def delete_activity(self):
        """حذف نشاط تقييم"""
        selection = self.activities_tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                t("select_activity_to_delete", self.language),
                parent=self
            )
            return
        
        item = self.activities_tree.item(selection[0])
        activity_name = item['values'][0]
        
        result = messagebox.askyesno(
            t("confirm", self.language),
            t("confirm_delete_activity", self.language).format(activity_name),
            parent=self
        )
        
        if result:
            self.course.remove_activity(activity_name)
            self.refresh_activities_list()
            self.mark_dirty()

    def edit_activity(self):
        """تحميل نشاط محدد لحقول التحرير"""
        sel = self.activities_tree.selection()
        if not sel:
            messagebox.showwarning(t("warning", self.language), t("select_activity_to_edit", self.language), parent=self)
            return
        item = self.activities_tree.item(sel[0])
        activity_name = item['values'][0]
        activity = self.course.get_activity(activity_name)
        if not activity:
            messagebox.showerror(t("error", self.language), t("activity_not_found", self.language), parent=self)
            return
        # تعبئة الحقول
        self.activity_name_entry.delete(0, tk.END)
        self.activity_name_entry.insert(0, activity.name)
        self.activity_mark_entry.delete(0, tk.END)
        self.activity_mark_entry.insert(0, str(activity.mark))
        self.activity_percent_entry.delete(0, tk.END)
        self.activity_percent_entry.insert(0, str(activity.percentage))
        self.activity_timing_entry.delete(0, tk.END)
        self.activity_timing_entry.insert(0, activity.timing)
        # تحديد المخرجات في القائمة
        try:
            # تفريغ الحالة ثم تفعيل المربعات المطابقة
            for code, var in self.clo_check_vars.items():
                var.set(False)
            for code in activity.measures_clos:
                if code in self.clo_check_vars:
                    self.clo_check_vars[code].set(True)
        except Exception:
            pass
        self._editing_activity_name = activity_name
        # تفعيل زر التحديث وتعطيل إضافة جديدة
        try:
            self.update_activity_btn.config(state=tk.NORMAL)
            self.add_activity_btn.config(state=tk.DISABLED)
        except Exception:
            pass

    def update_activity(self):
        """تحديث النشاط بعد التحرير"""
        if not getattr(self, '_editing_activity_name', None):
            return
        try:
            name = self.activity_name_entry.get().strip()
            if not name:
                messagebox.showwarning(t("warning", self.language), t("enter_activity_name", self.language), parent=self)
                return
            activity = AssessmentActivity(name)
            activity.mark = float(self.activity_mark_entry.get())
            activity.percentage = float(self.activity_percent_entry.get())
            activity.timing = self.activity_timing_entry.get().strip()

            # جمع المخرجات المحددة من checkboxes
            activity.measures_clos = [code for code, var in self.clo_check_vars.items() if var.get()]

            is_valid, error = activity.validate()
            if not is_valid:
                messagebox.showerror(t("error", self.language), error, parent=self)
                return
            if not self.course.update_activity(self._editing_activity_name, activity):
                messagebox.showerror(t("error", self.language), t("activity_already_exists", self.language), parent=self)
                return
            self.refresh_activities_list()
            self.clear_activity_fields()
            messagebox.showinfo(t("success", self.language), t("activity_updated_successfully", self.language), parent=self)
            self._editing_activity_name = None
            try:
                self.update_activity_btn.config(state=tk.DISABLED)
                self.add_activity_btn.config(state=tk.NORMAL)
            except Exception:
                pass
            self.mark_dirty()
        except ValueError:
            messagebox.showerror(t("error", self.language), t("invalid_number_format", self.language), parent=self)
        except Exception as e:
            messagebox.showerror(t("error", self.language), str(e), parent=self)
    
    def clear_activity_fields(self):
        """مسح حقول الأنشطة"""
        self.activity_name_entry.delete(0, tk.END)
        self.activity_mark_entry.delete(0, tk.END)
        self.activity_percent_entry.delete(0, tk.END)
        self.activity_timing_entry.delete(0, tk.END)

        # إلغاء تحديد جميع checkboxes
        try:
            for var in self.clo_check_vars.values():
                var.set(False)
        except Exception:
            pass

        # إعادة تعيين وضع التحرير إن وُجد
        self._editing_activity_name = None
        try:
            self.update_activity_btn.config(state=tk.DISABLED)
            self.add_activity_btn.config(state=tk.NORMAL)
        except Exception:
            pass
    
    def refresh_activities_list(self):
        """تحديث قائمة الأنشطة"""
        # مسح القائمة
        for item in self.activities_tree.get_children():
            self.activities_tree.delete(item)

        # إضافة العناصر مع عمود CLOs
        for activity in self.course.activities:
            # تجميع أكواد CLOs المرتبطة بالنشاط
            linked_clos = ', '.join(activity.measures_clos) if activity.measures_clos else '-'

            self.activities_tree.insert('', 'end', values=(
                activity.name,
                activity.mark,
                f"{activity.percentage}%",
                activity.timing,
                linked_clos  # عمود جديد: Link to CLOs
            ))
        # تحديث عناصر جدول المواصفات
        self.refresh_spec_widgets()

    def refresh_spec_widgets(self):
        """تحديث القوائم المستخدمة في جدول المواصفات
        هذه الدالة قد تُستدعى حتى لو لم نعرض تبويب جدول المواصفات في المرحلة 1.
        نتأكد هنا من وجود عناصر واجهة الجدول قبل التحديث لمنع استثناءات AttributeError."""
        # إذا لم تُنشأ حقول جدول المواصفات (نحن لا نظهر الجدول في Stage 1) نتجاوز التحديث
        if not hasattr(self, 'spec_topic_var') or not hasattr(self, 'spec_clo_var') or not hasattr(self, 'spec_activity_var'):
            # لكن لا ننسى تحديث مربعات اختيار الـ CLOs في تبويب الأنشطة إذا وُجدت
            try:
                self.refresh_clo_checkboxes()
            except Exception:
                pass
            return

        # مواضيع
        topic_values = [str(t.number) for t in self.course.topics]
        self.spec_topic_combo['values'] = topic_values
        if topic_values and not self.spec_topic_var.get():
            self.spec_topic_var.set(topic_values[0])
        
        # CLOs
        clo_values = [c.code for c in self.course.clos]
        self.spec_clo_combo['values'] = clo_values
        if clo_values and not self.spec_clo_var.get():
            self.spec_clo_var.set(clo_values[0])
        # تحديث قائمة اختيار CLOs في تبويب الأنشطة (إن وُجدت)
        try:
            self.refresh_clo_checkboxes()
        except Exception:
            pass
        
        # Activities
        act_values = [a.name for a in self.course.activities]
        self.spec_activity_combo['values'] = act_values
        if act_values and not self.spec_activity_var.get():
            self.spec_activity_var.set(act_values[0])
        
        # تحديث عرض الجدول
        self.refresh_specifications_list()

    def add_specification(self):
        """إضافة مدخل إلى جدول المواصفات"""
        try:
            topic = int(self.spec_topic_var.get())
            clo = self.spec_clo_var.get().strip()
            activity = self.spec_activity_var.get().strip()
            mark = float(self.spec_mark_entry.get())

            # التعيين
            self.course.table_of_specifications.set_specification(topic, clo, activity, mark)
            self.course.update_modified_date()

            # ربط النشاط بالمخرج (إذا لم يكن مرتبطاً)
            activity_obj = self.course.get_activity(activity)
            if activity_obj and clo not in activity_obj.measures_clos:
                activity_obj.measures_clos.append(clo)

            self.refresh_spec_widgets()
            self.spec_mark_entry.delete(0, tk.END)
            messagebox.showinfo(t('success', self.language), t('add', self.language) + ' ✓', parent=self)
            self.mark_dirty()
        except Exception as e:
            messagebox.showerror(t('error', self.language), str(e), parent=self)

    def refresh_clo_checkboxes(self):
        """بناء مربعات الاختيار للمخرجات وتقسيمها حسب الفئة"""
        # تهيئة
        try:
            for child in self.clo_checks_frame.winfo_children():
                child.destroy()
        except Exception:
            pass
        self.clo_check_vars = {}

        # تنظيم المخرجات حسب الفئة
        categories = [("Knowledge", t("knowledge", self.language)),
                      ("Skills", t("skills", self.language)),
                      ("Values", t("values", self.language))]

        is_rtl = (self.language == 'ar')
        row = 0

        for cat_key, cat_label in categories:
            # قائمة المخرجات من هذه الفئة
            items = [c for c in self.course.clos if (c.category.value if hasattr(c.category, 'value') else c.category) == cat_key]
            if not items:
                continue

            # عنوان الفئة
            label = tk.Label(
                self.clo_checks_frame,
                text=cat_label,
                font=(FONTS['normal'][0], 10, 'bold'),
                bg='#E8EAF6',
                fg='#3F51B5',
                anchor='e' if is_rtl else 'w'
            )
            label.grid(row=row, column=0, sticky='ew', padx=5, pady=(5, 2))
            row += 1

            # حاوية للـ checkboxes في صف واحد
            checkboxes_container = tk.Frame(self.clo_checks_frame, bg='#E8EAF6')
            checkboxes_container.grid(row=row, column=0, sticky='ew', padx=20, pady=(0, 5))

            # إضافة الـ checkboxes من اليمين لليسار في العربية
            if is_rtl:
                items_reversed = list(reversed(items))
                for i, clo in enumerate(items_reversed):
                    var = tk.BooleanVar(value=False)
                    cb = tk.Checkbutton(
                        checkboxes_container,
                        text=clo.code,
                        variable=var,
                        command=self.mark_dirty,
                        bg='#E8EAF6',
                        activebackground='#E8EAF6',
                        font=FONTS['normal']
                    )
                    cb.grid(row=0, column=i, padx=8, sticky='e')
                    self.clo_check_vars[clo.code] = var
            else:
                for i, clo in enumerate(items):
                    var = tk.BooleanVar(value=False)
                    cb = tk.Checkbutton(
                        checkboxes_container,
                        text=clo.code,
                        variable=var,
                        command=self.mark_dirty,
                        bg='#E8EAF6',
                        activebackground='#E8EAF6',
                        font=FONTS['normal']
                    )
                    cb.grid(row=0, column=i, padx=8, sticky='w')
                    self.clo_check_vars[clo.code] = var

            row += 1

        # جعل العمود قابل للتمدد
        self.clo_checks_frame.grid_columnconfigure(0, weight=1)
    def refresh_specifications_list(self):
        """تحديث عرض جدول المواصفات"""
        # مسح القائمة
        for item in self.specs_tree.get_children():
            self.specs_tree.delete(item)

        # إضافة العناصر
        for topic, clo_dict in sorted(self.course.table_of_specifications.specifications.items()):
            for clo, activities in clo_dict.items():
                for activity, mark in activities.items():
                    self.specs_tree.insert('', 'end', values=(topic, clo, activity, mark))

    def delete_specification(self):
        """حذف مدخل من جدول المواصفات"""
        sel = self.specs_tree.selection()
        if not sel:
            messagebox.showwarning(t('warning', self.language), t('select_topic_to_delete', self.language), parent=self)
            return
        item = self.specs_tree.item(sel[0])
        topic, clo, activity, mark = item['values']
        topic = int(topic)
        # إزالة المدخل
        if topic in self.course.table_of_specifications.specifications and clo in self.course.table_of_specifications.specifications[topic]:
            if activity in self.course.table_of_specifications.specifications[topic][clo]:
                del self.course.table_of_specifications.specifications[topic][clo][activity]
                # تنظيف الفروع الفارغة
                if not self.course.table_of_specifications.specifications[topic][clo]:
                    del self.course.table_of_specifications.specifications[topic][clo]
                if not self.course.table_of_specifications.specifications[topic]:
                    del self.course.table_of_specifications.specifications[topic]
                self.refresh_spec_widgets()
                messagebox.showinfo(t('success', self.language), t('delete_selected', self.language) + ' ✓', parent=self)
                self.mark_dirty()
        else:
            messagebox.showerror(t('error', self.language), t('error_loading_course', self.language), parent=self)
    
    # دوال رئيسية
    def load_data(self):
        """تحميل بيانات المقرر"""
        # تحميل معلومات المقرر (تأكد من أن الحقول قابلة للتحرير)
        info_values = [
            ('course_title', self.course.info.course_title),
            ('course_code', self.course.info.course_code),
            ('version', self.course.info.version),
            # المراحل التالية (شعب، محاضر، منسق، فصل) تم نقلها خارج المرحلة الأولى
            ('department', self.course.info.department),
            ('program', self.course.info.program),
            ('faculty', self.course.info.faculty),
        ]
        for key, val in info_values:
            entry = self.info_entries.get(key)
            if not entry:
                continue
            try:
                entry.config(state='normal')
            except Exception:
                pass
            entry.delete(0, tk.END)
            entry.insert(0, val)

        # تحميل التاريخ
        if hasattr(self.course.info, 'academic_year') and self.course.info.academic_year:
            try:
                # محاولة تحليل التاريخ
                date_entry = self.info_entries.get('academic_year')
                if date_entry:
                    from datetime import datetime
                    date_obj = datetime.strptime(self.course.info.academic_year, '%Y-%m-%d')
                    date_entry.set_date(date_obj)
            except:
                pass

        # تحميل حالة "يُدرس خارج القسم"
        if hasattr(self.course.info, 'taught_outside_department'):
            self.taught_outside_dept_var.set(self.course.info.taught_outside_department)
        else:
            self.taught_outside_dept_var.set(False)

        # تحديث حالة القسم بناءً على مربع الخيار
        self._toggle_beneficiary_section()

        # تحميل بيانات الكليات والأقسام المستفيدة
        self.beneficiary_data = []
        if hasattr(self.course.info, 'other_departments') and hasattr(self.course.info, 'other_departments_faculty'):
            if self.course.info.other_departments and self.course.info.other_departments_faculty:
                depts = [d.strip() for d in self.course.info.other_departments.split('|') if d.strip()]
                faculties = [f.strip() for f in self.course.info.other_departments_faculty.split('|') if f.strip()]

                # دمج البيانات
                for i in range(min(len(depts), len(faculties))):
                    self.beneficiary_data.append((faculties[i], depts[i]))

                self._refresh_beneficiary_list()
        
        # لا نعرض أو نتعامل مع معلومات الشعب/المحاضر/المنسق/الفصل هنا (Stage 1 فقط)
        
        # تحميل القوائم
        self.refresh_clos_list()
        self.refresh_topics_list()
        self.refresh_activities_list()
    
    def save_course(self):
        """حفظ المقرر - يتطلب كود المقرر على الأقل"""
        try:
            # الحصول على كود المقرر
            course_code = self.info_entries['course_code'].get().strip()

            # التحقق من وجود كود المقرر (شرط أساسي للحفظ)
            if not course_code:
                msg_ar = "⚠️ تحذير!\n\nلا يمكن حفظ المقرر بدون كود المقرر.\n\n" \
                        "الرجاء إدخال كود المقرر أولاً."
                msg_en = "⚠️ Warning!\n\nCannot save course without Course Code.\n\n" \
                        "Please enter the Course Code first."

                messagebox.showwarning(
                    t("warning", self.language),
                    msg_ar if self.language == 'ar' else msg_en,
                    parent=self
                )
                return False

            # حفظ معلومات المقرر
            self.course.info.course_code = course_code
            self.course.info.course_title = self.info_entries['course_title'].get().strip()
            self.course.info.version = self.info_entries['version'].get().strip()
            # لا نقوم بحفظ الشعب/المحاضر/المنسق/الفصل في المرحلة الأولى
            self.course.info.department = self.info_entries['department'].get().strip()
            self.course.info.program = self.info_entries['program'].get().strip()
            self.course.info.faculty = self.info_entries['faculty'].get().strip()

            # التحقق من صلاحية المستخدم لإنشاء/تعديل المقرر في هذا البرنامج
            program_name = self.course.info.program
            if program_name and self.access_control:
                # البحث عن البرنامج بالاسم للحصول على program_id
                all_programs = self.program_manager.get_all_programs()
                program_id = None
                for p in all_programs:
                    if p.program_name_ar == program_name or p.program_name_en == program_name:
                        program_id = p.program_id
                        break

                # التحقق من الصلاحية
                if program_id:
                    if not self.access_control.user_can_manage_course_for_program(
                        self.current_user.user_id, program_id
                    ):
                        msg_ar = "⚠️ خطأ في الصلاحيات!\n\n" \
                                "ليس لديك صلاحية لإنشاء أو تعديل مقررات في هذا البرنامج الأكاديمي.\n\n" \
                                "يمكنك فقط إدارة المقررات في البرامج المعينة لك."
                        msg_en = "⚠️ Permission Error!\n\n" \
                                "You don't have permission to create or edit courses in this program.\n\n" \
                                "You can only manage courses in your assigned programs."

                        messagebox.showerror(
                            t("error", self.language),
                            msg_ar if self.language == 'ar' else msg_en,
                            parent=self
                        )
                        return False

            # حفظ التاريخ
            date_entry = self.info_entries.get('academic_year')
            if date_entry:
                try:
                    self.course.info.academic_year = date_entry.get_date().strftime('%Y-%m-%d')
                except:
                    self.course.info.academic_year = ''

            # حفظ حالة "يُدرس خارج القسم"
            self.course.info.taught_outside_department = self.taught_outside_dept_var.get()

            # حفظ بيانات الكليات والأقسام المستفيدة
            if self.beneficiary_data:
                faculties = []
                departments = []
                for faculty, department in self.beneficiary_data:
                    faculties.append(faculty)
                    departments.append(department)

                self.course.info.other_departments_faculty = '|'.join(faculties)
                self.course.info.other_departments = '|'.join(departments)
            else:
                self.course.info.other_departments_faculty = ''
                self.course.info.other_departments = ''

            # حفظ في قاعدة البيانات
            if self.course_manager.save_course(self.course):
                # وضع علم الحفظ وإرجاع النجاح
                self.is_dirty = False
                self.course_saved = True  # تم حفظ المقرر بنجاح
                messagebox.showinfo(
                    t("success", self.language),
                    t("course_saved_successfully", self.language),
                    parent=self
                )
                return True
            else:
                messagebox.showerror(
                    t("error", self.language),
                    t("error_saving_course", self.language),
                    parent=self
                )
                return False

        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"{t('error_saving_course', self.language)}\n{str(e)}",
                parent=self
            )
            return False
    
    def complete_stage1(self):
        """إكمال المرحلة الأولى"""
        try:
            # حفظ أولاً
            saved = self.save_course()
            if not saved:
                return

            # محاولة إكمال المرحلة
            success, message = self.course_manager.complete_stage1(
                self.course_id,
                self.current_user.username
            )
            
            if success:
                # علم أن التغييرات محفوظة
                self.is_dirty = False
                messagebox.showinfo(
                    t("success", self.language),
                    message,
                    parent=self
                )
                self.destroy()
            else:
                messagebox.showerror(
                    t("error", self.language),
                    message,
                    parent=self
                )
        except Exception as e:
            messagebox.showerror(
                t('error', self.language),
                str(e),
                parent=self
            )
    
    def generate_report(self):
        """توليد تقرير PDF للمقرر"""
        try:
            # التحقق من حفظ المقرر
            if not self.course_saved:
                messagebox.showwarning(
                    t("warning", self.language),
                    t("save_course_before_report", self.language),
                    parent=self
                )
                return

            # إنشاء اسم الملف
            course_code = self.course.info.course_code or "course"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{course_code}_Stage1_Report_{timestamp}.pdf"

            # مسار مجلد التقارير
            reports_dir = os.path.join("reports", "generated")
            os.makedirs(reports_dir, exist_ok=True)
            output_path = os.path.join(reports_dir, filename)

            # توليد التقرير
            from reports.stage1_report_generator import Stage1ReportGenerator
            generator = Stage1ReportGenerator(self.course, self.language)

            if generator.generate_report(output_path):
                msg_ar = f"تم توليد التقرير بنجاح!\n\n{t('report_saved_to', self.language)}\n{output_path}"
                msg_en = f"Report generated successfully!\n\n{t('report_saved_to', self.language)}\n{output_path}"

                messagebox.showinfo(
                    t("success", self.language),
                    msg_ar if self.language == 'ar' else msg_en,
                    parent=self
                )

                # فتح المجلد
                import subprocess
                subprocess.Popen(f'explorer /select,"{os.path.abspath(output_path)}"')
            else:
                messagebox.showerror(
                    t("error", self.language),
                    t("error_generating_report", self.language),
                    parent=self
                )

        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"{t('error_generating_report', self.language)}\n\n{str(e)}",
                parent=self
            )

    def show_help(self):
        """عرض المساعدة"""
        help_text = t("help_stage1", self.language)
        messagebox.showinfo(
            t("help", self.language),
            help_text,
            parent=self
        )

    def download_clos_template(self):
        """تحميل قالب Excel لمخرجات التعلم"""
        try:
            # اختيار مكان الحفظ
            filename = f"CLOs_Template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                parent=self,
                title="حفظ القالب" if self.language == 'ar' else "Save Template",
                initialfile=filename,
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if file_path:
                generator = ExcelTemplateGenerator(self.language)
                if generator.generate_clos_template(file_path):
                    messagebox.showinfo(
                        t("success", self.language),
                        "تم إنشاء القالب بنجاح!" if self.language == 'ar' else "Template created successfully!",
                        parent=self
                    )
                    # فتح المجلد
                    os.startfile(os.path.dirname(file_path))
        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"خطأ في إنشاء القالب:\n{str(e)}" if self.language == 'ar' else f"Error creating template:\n{str(e)}",
                parent=self
            )

    def import_clos_from_excel(self):
        """استيراد مخرجات التعلم من ملف Excel"""
        try:
            # اختيار الملف
            file_path = filedialog.askopenfilename(
                parent=self,
                title="اختيار ملف Excel" if self.language == 'ar' else "Select Excel File",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if not file_path:
                return

            # قراءة البيانات من Excel
            reader = ExcelTemplateReader()
            clos_data = reader.read_clos_from_excel(file_path)

            if not clos_data:
                messagebox.showwarning(
                    t("warning", self.language),
                    "لم يتم العثور على بيانات في الملف!" if self.language == 'ar' else "No data found in file!",
                    parent=self
                )
                return

            # تأكيد الاستيراد
            msg_ar = f"تم العثور على {len(clos_data)} مخرج تعلم.\n\nهل تريد استيراد البيانات؟\n\nملاحظة: سيتم دمج البيانات مع المخرجات الموجودة."
            msg_en = f"Found {len(clos_data)} CLOs.\n\nDo you want to import the data?\n\nNote: Data will be merged with existing CLOs."

            if not messagebox.askyesno(
                t("confirm", self.language),
                msg_ar if self.language == 'ar' else msg_en,
                parent=self
            ):
                return

            # استيراد البيانات
            imported_count = 0
            updated_count = 0

            for clo_data in clos_data:
                clo_code = clo_data['code']

                # البحث عن المخرج الموجود
                existing_clo = None
                for clo in self.course.clos:
                    if clo.code == clo_code:
                        existing_clo = clo
                        break

                if existing_clo:
                    # تحديث المخرج الموجود
                    existing_clo.description = clo_data['description']
                    # تحويل التصنيف إلى CLOCategory
                    category_str = clo_data['category']
                    if category_str == 'Knowledge':
                        existing_clo.category = CLOCategory.KNOWLEDGE
                    elif category_str == 'Skills':
                        existing_clo.category = CLOCategory.SKILLS
                    elif category_str == 'Values':
                        existing_clo.category = CLOCategory.VALUES
                    existing_clo.aligned_plos = clo_data['aligned_plos']
                    updated_count += 1
                else:
                    # إضافة مخرج جديد
                    # تحويل التصنيف إلى CLOCategory
                    category_str = clo_data['category']
                    if category_str == 'Skills':
                        category = CLOCategory.SKILLS
                    elif category_str == 'Values':
                        category = CLOCategory.VALUES
                    else:
                        category = CLOCategory.KNOWLEDGE  # افتراضي

                    new_clo = CLO(
                        code=clo_code,
                        category=category
                    )
                    new_clo.description = clo_data['description']
                    new_clo.aligned_plos = clo_data['aligned_plos']
                    self.course.clos.append(new_clo)
                    imported_count += 1

            # وضع علامة على التعديل
            self.mark_dirty()
            self.refresh_clos_list()

            msg_ar = f"✅ تم الاستيراد بنجاح!\n\nجديد: {imported_count}\nمحدث: {updated_count}\nالمجموع: {len(self.course.clos)}\n\nلا تنسى حفظ المقرر!"
            msg_en = f"✅ Import successful!\n\nNew: {imported_count}\nUpdated: {updated_count}\nTotal: {len(self.course.clos)}\n\nDon't forget to save the course!"

            messagebox.showinfo(
                t("success", self.language),
                msg_ar if self.language == 'ar' else msg_en,
                parent=self
            )

        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"خطأ في الاستيراد:\n{str(e)}" if self.language == 'ar' else f"Import error:\n{str(e)}",
                parent=self
            )

    def download_topics_template(self):
        """تحميل قالب Excel للمواضيع"""
        try:
            filename = f"Topics_Template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                parent=self,
                title="حفظ القالب" if self.language == 'ar' else "Save Template",
                initialfile=filename,
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if file_path:
                generator = ExcelTemplateGenerator(self.language)
                if generator.generate_topics_template(file_path):
                    messagebox.showinfo(
                        t("success", self.language),
                        "تم إنشاء القالب بنجاح!" if self.language == 'ar' else "Template created successfully!",
                        parent=self
                    )
                    os.startfile(os.path.dirname(file_path))
        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"خطأ في إنشاء القالب:\n{str(e)}" if self.language == 'ar' else f"Error creating template:\n{str(e)}",
                parent=self
            )

    def import_topics_from_excel(self):
        """استيراد المواضيع من ملف Excel"""
        try:
            file_path = filedialog.askopenfilename(
                parent=self,
                title="اختيار ملف Excel" if self.language == 'ar' else "Select Excel File",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if not file_path:
                return

            reader = ExcelTemplateReader()
            topics_data = reader.read_topics_from_excel(file_path)

            if not topics_data:
                messagebox.showwarning(
                    t("warning", self.language),
                    "لم يتم العثور على بيانات في الملف!" if self.language == 'ar' else "No data found in file!",
                    parent=self
                )
                return

            msg_ar = f"تم العثور على {len(topics_data)} موضوع.\n\nهل تريد استيراد البيانات؟\n\nملاحظة: سيتم دمج البيانات مع المواضيع الموجودة."
            msg_en = f"Found {len(topics_data)} topics.\n\nDo you want to import the data?\n\nNote: Data will be merged with existing topics."

            if not messagebox.askyesno(
                t("confirm", self.language),
                msg_ar if self.language == 'ar' else msg_en,
                parent=self
            ):
                return

            imported_count = 0
            updated_count = 0

            for topic_data in topics_data:
                topic_number = topic_data['number']

                existing_topic = None
                for topic in self.course.topics:
                    if topic.number == topic_number:
                        existing_topic = topic
                        break

                if existing_topic:
                    existing_topic.title = topic_data['title']
                    existing_topic.contact_hours = topic_data['hours']
                    updated_count += 1
                else:
                    new_topic = Topic(number=topic_number)
                    new_topic.title = topic_data['title']
                    new_topic.contact_hours = topic_data['hours']
                    self.course.topics.append(new_topic)
                    imported_count += 1

            self.mark_dirty()
            self.refresh_topics_list()

            msg_ar = f"✅ تم الاستيراد بنجاح!\n\nجديد: {imported_count}\nمحدث: {updated_count}\nالمجموع: {len(self.course.topics)}\n\nلا تنسى حفظ المقرر!"
            msg_en = f"✅ Import successful!\n\nNew: {imported_count}\nUpdated: {updated_count}\nTotal: {len(self.course.topics)}\n\nDon't forget to save the course!"

            messagebox.showinfo(
                t("success", self.language),
                msg_ar if self.language == 'ar' else msg_en,
                parent=self
            )

        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"خطأ في الاستيراد:\n{str(e)}" if self.language == 'ar' else f"Import error:\n{str(e)}",
                parent=self
            )

    def download_activities_template(self):
        """تحميل قالب Excel للأنشطة"""
        try:
            filename = f"Activities_Template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                parent=self,
                title="حفظ القالب" if self.language == 'ar' else "Save Template",
                initialfile=filename,
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if file_path:
                generator = ExcelTemplateGenerator(self.language)
                if generator.generate_activities_template(file_path):
                    messagebox.showinfo(
                        t("success", self.language),
                        "تم إنشاء القالب بنجاح!" if self.language == 'ar' else "Template created successfully!",
                        parent=self
                    )
                    os.startfile(os.path.dirname(file_path))
        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"خطأ في إنشاء القالب:\n{str(e)}" if self.language == 'ar' else f"Error creating template:\n{str(e)}",
                parent=self
            )

    def import_activities_from_excel(self):
        """استيراد الأنشطة من ملف Excel"""
        try:
            file_path = filedialog.askopenfilename(
                parent=self,
                title="اختيار ملف Excel" if self.language == 'ar' else "Select Excel File",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if not file_path:
                return

            reader = ExcelTemplateReader()
            activities_data = reader.read_activities_from_excel(file_path)

            if not activities_data:
                messagebox.showwarning(
                    t("warning", self.language),
                    "لم يتم العثور على بيانات في الملف!" if self.language == 'ar' else "No data found in file!",
                    parent=self
                )
                return

            msg_ar = f"تم العثور على {len(activities_data)} نشاط.\n\nهل تريد استيراد البيانات؟\n\nملاحظة: سيتم دمج البيانات مع الأنشطة الموجودة."
            msg_en = f"Found {len(activities_data)} activities.\n\nDo you want to import the data?\n\nNote: Data will be merged with existing activities."

            if not messagebox.askyesno(
                t("confirm", self.language),
                msg_ar if self.language == 'ar' else msg_en,
                parent=self
            ):
                return

            imported_count = 0
            updated_count = 0

            for activity_data in activities_data:
                activity_name = activity_data['name']

                # البحث عن النشاط الموجود بالاسم
                existing_activity = None
                for activity in self.course.activities:
                    if activity.name == activity_name:
                        existing_activity = activity
                        break

                if existing_activity:
                    # تحديث النشاط الموجود
                    existing_activity.mark = activity_data['mark']
                    existing_activity.percentage = activity_data['percentage']
                    existing_activity.timing = activity_data['timing']

                    # تحديث مخرجات التعلم المرتبطة
                    if activity_data['linked_clos']:
                        # تحويل النص إلى قائمة أرقام (مثل: "1, 2, 3" -> ["1", "2", "3"])
                        clo_codes = [code.strip() for code in activity_data['linked_clos'].split(',')]
                        existing_activity.measures_clos = clo_codes

                    updated_count += 1
                else:
                    # إضافة نشاط جديد
                    new_activity = AssessmentActivity(name=activity_name)
                    new_activity.mark = activity_data['mark']
                    new_activity.percentage = activity_data['percentage']
                    new_activity.timing = activity_data['timing']

                    # إضافة مخرجات التعلم المرتبطة
                    if activity_data['linked_clos']:
                        clo_codes = [code.strip() for code in activity_data['linked_clos'].split(',')]
                        new_activity.measures_clos = clo_codes

                    self.course.activities.append(new_activity)
                    imported_count += 1

            self.mark_dirty()
            self.refresh_activities_list()

            msg_ar = f"✅ تم الاستيراد بنجاح!\n\nجديد: {imported_count}\nمحدث: {updated_count}\nالمجموع: {len(self.course.activities)}\n\nلا تنسى حفظ المقرر!"
            msg_en = f"✅ Import successful!\n\nNew: {imported_count}\nUpdated: {updated_count}\nTotal: {len(self.course.activities)}\n\nDon't forget to save the course!"

            messagebox.showinfo(
                t("success", self.language),
                msg_ar if self.language == 'ar' else msg_en,
                parent=self
            )

        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"خطأ في الاستيراد:\n{str(e)}" if self.language == 'ar' else f"Import error:\n{str(e)}",
                parent=self
            )

    def toggle_language(self):
        """تبديل اللغة"""
        # تحفظ البيانات الحالية قبل التبديل
        if self.is_dirty:
            msg = "هناك تغييرات غير محفوظة. هل تريد حفظها قبل تبديل اللغة؟" if self.language == 'ar' else "There are unsaved changes. Do you want to save before switching language?"
            result = messagebox.askyesnocancel(
                "حفظ التغييرات / Save Changes" if self.language == 'ar' else "Save Changes",
                msg,
                parent=self
            )
            if result is None:  # إلغاء
                return
            if result:  # نعم، احفظ
                if not self.save_course():
                    return

        # تبديل اللغة
        new_lang = 'en' if self.language == 'ar' else 'ar'
        self.language = new_lang

        # إعادة بناء الواجهة
        # مسح جميع العناصر
        for widget in self.winfo_children():
            widget.destroy()

        # إعادة بناء الواجهة
        self.setup_ui()

        # إعادة تحميل البيانات
        self.load_data()
