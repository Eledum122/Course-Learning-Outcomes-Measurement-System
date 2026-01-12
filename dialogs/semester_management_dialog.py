# -*- coding: utf-8 -*-
"""
نافذة إدارة بيانات الفصل الدراسي
Semester Management Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models.course import Course, SemesterData, Semester
from models.user import User
from managers.course_manager import CourseManager
from managers.access_control import AccessControl
from managers.faculty_manager import FacultyManager
from config import FONTS
from translations import t


class SemesterManagementDialog(tk.Toplevel):
    """نافذة إدارة بيانات الفصل الدراسي (منسق المقرر، المدرسين، المستويات المستهدفة)"""

    def __init__(self, parent, course: Course, language: str = 'ar'):
        super().__init__(parent)

        self.course = course
        self.language = language
        self.result = None
        self.has_unsaved_changes = False  # تتبع التغييرات غير المحفوظة

        # تهيئة المديرين
        self.access_control = AccessControl()
        self.faculty_manager = FacultyManager()

        # إعداد النافذة
        self.title("إدارة بيانات الفصل الدراسي" if language == 'ar' else "Semester Management")
        self.geometry("1000x750")
        self.resizable(True, True)

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # معالج إغلاق النافذة
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # إنشاء الواجهة
        self._create_widgets()

        # تحميل البيانات المحفوظة تلقائياً إذا وجدت
        self._auto_load_existing_data()

        # مركزة النافذة
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # إطار الأزرار الثابت في الأسفل
        buttons_frame = tk.Frame(self, bg='#f5f5f5', pady=15)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # زر الحفظ (أخضر، بارز)
        tk.Button(
            buttons_frame,
            text="💾 حفظ" if self.language == 'ar' else "💾 Save",
            command=self._save_semester_data,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

        # زر الإلغاء (أحمر)
        tk.Button(
            buttons_frame,
            text="✖ إلغاء" if self.language == 'ar' else "✖ Cancel",
            command=self._on_closing,
            bg='#F44336',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

        # زر تحميل البيانات (أزرق)
        tk.Button(
            buttons_frame,
            text="📥 تحميل بيانات الفصل" if self.language == 'ar' else "📥 Load Semester Data",
            command=self._load_semester_data,
            bg='#2196F3',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=18,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

        # إطار قابل للتمرير للمحتوى
        canvas = tk.Canvas(self, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # دعم التمرير بعجلة الماوس
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الإطار الرئيسي داخل الإطار القابل للتمرير
        main_frame = tk.Frame(scrollable_frame, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # العنوان
        title_text = "إدارة بيانات الفصل الدراسي" if self.language == 'ar' else "Semester Management"
        tk.Label(
            main_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='white',
            fg='#1976D2'
        ).pack(pady=(0, 20))

        # معلومات المقرر
        info_frame = tk.LabelFrame(
            main_frame,
            text="معلومات المقرر" if self.language == 'ar' else "Course Information",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            padx=10,
            pady=10
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))

        course_info_text = f"{self.course.info.course_code} - {self.course.info.course_title}"
        tk.Label(
            info_frame,
            text=course_info_text,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            fg='#555'
        ).pack()

        # نموذج إدخال البيانات
        form_frame = tk.Frame(main_frame, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True)

        # السنة الدراسية
        self._create_form_field(
            form_frame, 0,
            "السنة الدراسية:" if self.language == 'ar' else "Academic Year:",
            "academic_year",
            placeholder="1445-1446"
        )

        # الفصل الدراسي
        semester_label = "الفصل الدراسي:" if self.language == 'ar' else "Semester:"
        tk.Label(
            form_frame,
            text=semester_label,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).grid(row=1, column=1 if self.language == 'ar' else 0, sticky='e' if self.language == 'ar' else 'w', pady=8)

        self.semester_var = tk.StringVar(value="First")
        semester_combo = ttk.Combobox(
            form_frame,
            textvariable=self.semester_var,
            values=["First", "Second", "Summer"],
            state='readonly',
            font=FONTS['english_main'],
            width=25
        )
        semester_combo.grid(row=1, column=0 if self.language == 'ar' else 1, sticky='ew', pady=8, padx=(0, 10) if self.language == 'ar' else (10, 0))
        semester_combo.bind('<<ComboboxSelected>>', self._on_semester_changed)

        # تكوين الأعمدة
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # إطار منسق المقرر
        coordinator_frame = tk.LabelFrame(
            main_frame,
            text="منسق المقرر" if self.language == 'ar' else "Course Coordinator",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            padx=10,
            pady=10
        )
        coordinator_frame.pack(fill=tk.X, pady=(15, 0))

        self._create_coordinator_section(coordinator_frame)

        # إطار المدرسين
        instructors_frame = tk.LabelFrame(
            main_frame,
            text="مدرسو الشعب" if self.language == 'ar' else "Section Instructors",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            padx=10,
            pady=10
        )
        instructors_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        self._create_instructors_section(instructors_frame)

        # إطار المستويات المستهدفة
        target_frame = tk.LabelFrame(
            main_frame,
            text="المستويات المستهدفة لمخرجات التعلم" if self.language == 'ar' else "CLO Target Levels",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            padx=10,
            pady=10
        )
        target_frame.pack(fill=tk.X, pady=(15, 10))

        self._create_clo_target_levels(target_frame)

    def _create_form_field(self, parent, row: int, label_text: str, field_name: str, placeholder: str = ""):
        """إنشاء حقل في النموذج"""
        tk.Label(
            parent,
            text=label_text,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).grid(row=row, column=1 if self.language == 'ar' else 0, sticky='e' if self.language == 'ar' else 'w', pady=8)

        entry = tk.Entry(
            parent,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=30
        )
        entry.grid(row=row, column=0 if self.language == 'ar' else 1, sticky='ew', pady=8, padx=(0, 10) if self.language == 'ar' else (10, 0))

        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg='gray')

            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg='black')

            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg='gray')

            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)

        # تتبع التغييرات
        entry.bind('<KeyRelease>', lambda e: self._mark_as_changed())

        setattr(self, f"{field_name}_entry", entry)

    def _create_coordinator_section(self, parent):
        """إنشاء قسم منسق المقرر"""
        # إطار الإدخال
        input_frame = tk.Frame(parent, bg='white')
        input_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            input_frame,
            text="اختر المنسق:" if self.language == 'ar' else "Select Coordinator:",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # تحميل قائمة الأعضاء من FacultyManager
        from managers.faculty_manager import FacultyManager
        self.faculty_manager = FacultyManager()
        faculty_list = self.faculty_manager.get_members_for_combobox()

        self.coordinator_var = tk.StringVar()
        self.coordinator_combo = ttk.Combobox(
            input_frame,
            textvariable=self.coordinator_var,
            values=faculty_list,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=45,
            state='readonly'
        )
        self.coordinator_combo.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(
            input_frame,
            text="تعيين" if self.language == 'ar' else "Set",
            command=self._set_coordinator,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # عرض المنسق الحالي
        display_frame = tk.Frame(parent, bg='white')
        display_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            display_frame,
            text="المنسق الحالي:" if self.language == 'ar' else "Current Coordinator:",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            fg='#666'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        self.coordinator_display = tk.Label(
            display_frame,
            text="لم يتم التعيين" if self.language == 'ar' else "Not Set",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='#E3F2FD',
            fg='#1976D2',
            relief=tk.RIDGE,
            padx=10,
            pady=5
        )
        self.coordinator_display.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5, fill=tk.X, expand=True)

        # زر الحذف
        tk.Button(
            parent,
            text="حذف المنسق" if self.language == 'ar' else "Remove Coordinator",
            command=self._remove_coordinator,
            bg='#F44336',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            cursor='hand2'
        ).pack(pady=(5, 0))

    def _create_instructors_section(self, parent):
        """إنشاء قسم المدرسين"""
        # إطار الإدخال
        input_frame = tk.Frame(parent, bg='white')
        input_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            input_frame,
            text="اختر المدرس:" if self.language == 'ar' else "Select Instructor:",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # استخدام نفس faculty_manager المحملة في _create_coordinator_section
        faculty_list = self.faculty_manager.get_members_for_combobox()

        self.instructor_var = tk.StringVar()
        self.instructor_combo = ttk.Combobox(
            input_frame,
            textvariable=self.instructor_var,
            values=faculty_list,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=40,
            state='readonly'
        )
        self.instructor_combo.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(
            input_frame,
            text="إضافة" if self.language == 'ar' else "Add",
            command=self._add_instructor,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # قائمة المدرسين
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.instructors_listbox = tk.Listbox(
            list_frame,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            yscrollcommand=scrollbar.set,
            height=5
        )
        self.instructors_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.instructors_listbox.yview)

        # زر الحذف
        tk.Button(
            parent,
            text="حذف المدرس المحدد" if self.language == 'ar' else "Remove Selected",
            command=self._remove_instructor,
            bg='#F44336',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            cursor='hand2'
        ).pack(pady=(10, 0))

        # ملاحظة توضيحية
        note_text = "ملاحظة: يتم إضافة المدرسين تلقائياً من الشعب المحفوظة لنفس الفصل الدراسي" if self.language == 'ar' \
                    else "Note: Instructors are automatically added from saved sections for the same semester"
        tk.Label(
            parent,
            text=note_text,
            font=FONTS['arabic_small'] if self.language == 'ar' else FONTS['english_small'],
            bg='white',
            fg='#666',
            wraplength=400,
            justify='right' if self.language == 'ar' else 'left'
        ).pack(pady=(5, 0))

    def _create_clo_target_levels(self, parent):
        """إنشاء حقول المستويات المستهدفة للمخرجات"""
        # إطار للجدول مع scrollbar
        table_container = tk.Frame(parent, bg='white')
        table_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        canvas = tk.Canvas(table_container, bg='white', height=200)
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            # تحديث عرض النافذة الداخلية ليتطابق مع عرض Canvas
            canvas.itemconfig(canvas_window, width=event.width)

        scrollable_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # رأس الجدول
        headers = ["CLO Code", "Description", "Current Target (%)", "New Target (%)"]
        headers_ar = ["رمز المخرج", "الوصف", "المستوى الحالي (%)", "المستوى الجديد (%)"]

        header_labels = headers_ar if self.language == 'ar' else headers
        col_weights = [1, 5, 2, 2]  # زيادة وزن عمود الوصف

        for idx, (header, weight) in enumerate(zip(header_labels, col_weights)):
            col_idx = len(header_labels) - 1 - idx if self.language == 'ar' else idx
            tk.Label(
                scrollable_frame,
                text=header,
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                bg='#E3F2FD',
                relief=tk.RIDGE,
                padx=10,
                pady=8,
                borderwidth=1
            ).grid(row=0, column=col_idx, sticky='nsew', padx=1, pady=1)
            scrollable_frame.columnconfigure(col_idx, weight=weight, minsize=80)

        # حقول المخرجات
        self.clo_target_entries = {}
        for idx, clo in enumerate(self.course.clos):
            row = idx + 1

            # رمز المخرج
            col_idx = 3 if self.language == 'ar' else 0
            tk.Label(
                scrollable_frame,
                text=clo.code,
                font=FONTS['english_main'],
                bg='white',
                relief=tk.RIDGE,
                padx=8,
                pady=6,
                borderwidth=1
            ).grid(row=row, column=col_idx, sticky='nsew', padx=1, pady=1)

            # الوصف
            col_idx = 2 if self.language == 'ar' else 1
            desc_text = clo.description[:70] + "..." if len(clo.description) > 70 else clo.description
            tk.Label(
                scrollable_frame,
                text=desc_text,
                font=FONTS['arabic_small'] if self.language == 'ar' else FONTS['english_small'],
                bg='white',
                relief=tk.RIDGE,
                padx=8,
                pady=6,
                anchor='e' if self.language == 'ar' else 'w',
                wraplength=400,
                borderwidth=1
            ).grid(row=row, column=col_idx, sticky='nsew', padx=1, pady=1)

            # المستوى الحالي
            col_idx = 1 if self.language == 'ar' else 2
            tk.Label(
                scrollable_frame,
                text=f"{clo.target_level:.1f}",
                font=FONTS['english_main'],
                bg='#F5F5F5',
                relief=tk.RIDGE,
                padx=8,
                pady=6,
                borderwidth=1
            ).grid(row=row, column=col_idx, sticky='nsew', padx=1, pady=1)

            # المستوى الجديد
            col_idx = 0 if self.language == 'ar' else 3
            target_entry = tk.Entry(
                scrollable_frame,
                font=FONTS['english_main'],
                justify='center',
                width=15,
                relief=tk.SOLID,
                borderwidth=1
            )
            target_entry.insert(0, f"{clo.target_level:.1f}")
            target_entry.grid(row=row, column=col_idx, sticky='nsew', padx=3, pady=3)

            # تتبع التغييرات
            target_entry.bind('<KeyRelease>', lambda e: self._mark_as_changed())

            self.clo_target_entries[clo.code] = target_entry

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _set_coordinator(self):
        """تعيين منسق المقرر"""
        coordinator_display_name = self.coordinator_var.get().strip()
        if coordinator_display_name:
            self.coordinator_display.config(
                text=coordinator_display_name,
                bg='#C8E6C9',
                fg='#2E7D32'
            )
            self.coordinator_var.set('')
            self._mark_as_changed()
        else:
            messagebox.showwarning(
                "تحذير" if self.language == 'ar' else "Warning",
                "يرجى اختيار منسق من القائمة" if self.language == 'ar' else "Please select a coordinator from the list",
                parent=self
            )

    def _remove_coordinator(self):
        """حذف منسق المقرر"""
        current_text = self.coordinator_display.cget('text')
        if current_text != ("لم يتم التعيين" if self.language == 'ar' else "Not Set"):
            result = messagebox.askyesno(
                "تأكيد الحذف" if self.language == 'ar' else "Confirm Delete",
                "هل تريد حذف المنسق الحالي؟" if self.language == 'ar' else "Do you want to remove the current coordinator?",
                parent=self
            )
            if result:
                self.coordinator_display.config(
                    text="لم يتم التعيين" if self.language == 'ar' else "Not Set",
                    bg='#E3F2FD',
                    fg='#1976D2'
                )
                self._mark_as_changed()

    def _add_instructor(self):
        """إضافة مدرس إلى القائمة"""
        instructor_display_name = self.instructor_var.get().strip()
        if instructor_display_name and instructor_display_name not in self.instructors_listbox.get(0, tk.END):
            self.instructors_listbox.insert(tk.END, instructor_display_name)
            self.instructor_var.set('')
            self._mark_as_changed()

    def _remove_instructor(self):
        """حذف مدرس من القائمة"""
        selection = self.instructors_listbox.curselection()
        if selection:
            self.instructors_listbox.delete(selection[0])
            self._mark_as_changed()

    def _mark_as_changed(self):
        """تعليم النموذج بأن هناك تغييرات غير محفوظة"""
        self.has_unsaved_changes = True
        # تحديث عنوان النافذة للإشارة إلى وجود تغييرات
        current_title = self.title()
        if not current_title.endswith('*'):
            self.title(current_title + ' *')

    def _on_closing(self):
        """معالج إغلاق النافذة - تحذير إذا كانت هناك تغييرات غير محفوظة"""
        if self.has_unsaved_changes:
            message = "لديك تغييرات غير محفوظة. هل تريد حقاً الإغلاق بدون حفظ؟" if self.language == 'ar' \
                      else "You have unsaved changes. Do you really want to close without saving?"
            title = "تحذير" if self.language == 'ar' else "Warning"

            result = messagebox.askyesno(
                title,
                message,
                parent=self,
                icon='warning'
            )

            if not result:  # المستخدم قال "لا"
                return  # لا تغلق النافذة

        # إغلاق النافذة
        self.destroy()

    def _on_semester_changed(self, event=None):
        """عند تغيير الفصل الدراسي، تحميل البيانات المخزنة إن وجدت"""
        # تحميل البيانات تلقائياً عند تغيير الفصل
        academic_year = self.academic_year_entry.get().strip()
        if academic_year and academic_year != "1445-1446":
            self._load_semester_data_silent()

    def _auto_load_existing_data(self):
        """تحميل البيانات المحفوظة تلقائياً عند فتح النموذج"""
        # البحث عن أحدث بيانات محفوظة
        if self.course.semester_data:
            # الحصول على أحدث سنة دراسية
            latest_key = sorted(self.course.semester_data.keys(), reverse=True)[0]
            academic_year, semester = latest_key.split('_')

            # ملء السنة الدراسية والفصل
            self.academic_year_entry.delete(0, tk.END)
            self.academic_year_entry.insert(0, academic_year)
            self.academic_year_entry.config(fg='black')
            self.semester_var.set(semester)

            # تحميل البيانات
            self._load_semester_data_silent()

    def _get_instructors_from_sections(self, academic_year: str, semester: str) -> list:
        """جمع أسماء المدرسين من الشعب المحفوظة لنفس الفصل الدراسي"""
        instructors = set()

        try:
            from managers.section_manager import SectionManager
            sm = SectionManager()

            # تحميل جميع الشعب للمقرر
            sections = sm.get_sections_by_course(self.course.course_id)

            # جمع المدرسين من الشعب التي تطابق السنة والفصل
            for section in sections:
                section_year = getattr(section, 'academic_year', '')
                section_semester = getattr(section, 'semester', None)

                # تحويل semester إلى string إذا كان Enum
                if hasattr(section_semester, 'value'):
                    section_semester = section_semester.value

                if section_year == academic_year and section_semester == semester:
                    instructor = getattr(section, 'section_instructor', '')
                    if instructor and instructor.strip():
                        instructors.add(instructor.strip())
        except Exception as e:
            # في حالة حدوث خطأ، نتجاهله ونعيد قائمة فارغة
            print(f"Warning: Could not load instructors from sections: {e}")

        return sorted(list(instructors))

    def _load_semester_data_silent(self):
        """تحميل بيانات الفصل الدراسي بدون رسائل تأكيد"""
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_var.get()

        if not academic_year or academic_year == "1445-1446":
            return

        semester_data = self.course.get_semester_data(academic_year, semester)

        # جمع المدرسين من الشعب المحفوظة
        section_instructors = self._get_instructors_from_sections(academic_year, semester)

        if semester_data:
            # تحميل المنسق
            if semester_data.course_coordinator:
                self.coordinator_display.config(
                    text=semester_data.course_coordinator,
                    bg='#C8E6C9',
                    fg='#2E7D32'
                )
            else:
                self.coordinator_display.config(
                    text="لم يتم التعيين" if self.language == 'ar' else "Not Set",
                    bg='#E3F2FD',
                    fg='#1976D2'
                )

            # تحميل المدرسين من البيانات المحفوظة
            self.instructors_listbox.delete(0, tk.END)
            saved_instructors = set(semester_data.instructors)

            # إضافة المدرسين من الشعب المحفوظة تلقائياً
            for instructor in section_instructors:
                saved_instructors.add(instructor)

            # عرض جميع المدرسين
            for instructor in sorted(saved_instructors):
                self.instructors_listbox.insert(tk.END, instructor)

            # تحميل المستويات المستهدفة
            for clo_code, target_entry in self.clo_target_entries.items():
                if clo_code in semester_data.clo_target_levels:
                    target_entry.delete(0, tk.END)
                    target_entry.insert(0, f"{semester_data.clo_target_levels[clo_code]:.1f}")
        else:
            # لا توجد بيانات محفوظة، لكن يمكن تحميل المدرسين من الشعب
            if section_instructors:
                self.instructors_listbox.delete(0, tk.END)
                for instructor in section_instructors:
                    self.instructors_listbox.insert(tk.END, instructor)

    def _load_semester_data(self):
        """تحميل بيانات الفصل الدراسي المحفوظة (مع رسالة تأكيد)"""
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_var.get()

        if not academic_year or academic_year == "1445-1446":
            messagebox.showwarning(
                t('warning', self.language),
                "يجب إدخال السنة الدراسية أولاً" if self.language == 'ar' else "Please enter academic year first",
                parent=self
            )
            return

        semester_data = self.course.get_semester_data(academic_year, semester)

        if semester_data:
            # استخدام الدالة الصامتة للتحميل
            self._load_semester_data_silent()

            messagebox.showinfo(
                t('success', self.language),
                "تم تحميل بيانات الفصل الدراسي بنجاح" if self.language == 'ar' else "Semester data loaded successfully",
                parent=self
            )
        else:
            # تفريغ الحقول عند عدم وجود بيانات محفوظة
            # تفريغ منسق المقرر
            self.coordinator_display.config(
                text="لم يتم التعيين" if self.language == 'ar' else "Not Set",
                bg='#E3F2FD',
                fg='#1976D2'
            )

            # تفريغ قائمة المدرسين
            self.instructors_listbox.delete(0, tk.END)

            # تفريغ المستويات المستهدفة وإعادتها للقيم الافتراضية
            for clo_code, target_entry in self.clo_target_entries.items():
                # البحث عن المخرج للحصول على القيمة الافتراضية
                for clo in self.course.clos:
                    if clo.code == clo_code:
                        target_entry.delete(0, tk.END)
                        target_entry.insert(0, f"{clo.target_level:.1f}")
                        break

            messagebox.showinfo(
                t('info', self.language),
                "لا توجد بيانات محفوظة لهذا الفصل الدراسي\nتم تفريغ الحقول لإدخال بيانات جديدة"
                if self.language == 'ar'
                else "No saved data for this semester\nFields have been cleared for new data entry",
                parent=self
            )

    def _save_semester_data(self):
        """حفظ بيانات الفصل الدراسي"""
        # جمع البيانات
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_var.get()
        course_coordinator = self.coordinator_display.cget('text')

        # التحقق من البيانات
        if not academic_year or academic_year == "1445-1446":
            messagebox.showerror(
                t('error', self.language),
                "يجب إدخال السنة الدراسية" if self.language == 'ar' else "Academic year is required",
                parent=self
            )
            return

        if not course_coordinator or course_coordinator == ("لم يتم التعيين" if self.language == 'ar' else "Not Set"):
            messagebox.showerror(
                t('error', self.language),
                "يجب تعيين منسق المقرر" if self.language == 'ar' else "Course coordinator must be set",
                parent=self
            )
            return

        # جمع قائمة المدرسين
        instructors = list(self.instructors_listbox.get(0, tk.END))

        # جمع المستويات المستهدفة
        clo_target_levels = {}
        for clo_code, target_entry in self.clo_target_entries.items():
            try:
                target_value = float(target_entry.get().strip())
                if not (0 <= target_value <= 100):
                    messagebox.showerror(
                        t('error', self.language),
                        f"المستوى المستهدف للمخرج {clo_code} يجب أن يكون بين 0 و 100" if self.language == 'ar'
                        else f"Target level for CLO {clo_code} must be between 0 and 100",
                        parent=self
                    )
                    return

                # التحقق من أن المستوى الجديد يساوي أو يزيد عن المستوى الحالي
                current_target = None
                for clo in self.course.clos:
                    if clo.code == clo_code:
                        current_target = clo.target_level
                        break

                if current_target is not None and target_value < current_target:
                    messagebox.showerror(
                        t('error', self.language),
                        f"المستوى المستهدف الجديد للمخرج {clo_code} ({target_value:.1f}%) يجب أن يساوي أو يزيد عن المستوى الحالي ({current_target:.1f}%)"
                        if self.language == 'ar'
                        else f"New target level for CLO {clo_code} ({target_value:.1f}%) must be equal to or greater than current level ({current_target:.1f}%)",
                        parent=self
                    )
                    return

                clo_target_levels[clo_code] = target_value
            except ValueError:
                messagebox.showerror(
                    t('error', self.language),
                    f"المستوى المستهدف للمخرج {clo_code} يجب أن يكون رقماً" if self.language == 'ar'
                    else f"Target level for CLO {clo_code} must be a number",
                    parent=self
                )
                return

        # إنشاء كائن SemesterData
        semester_data = SemesterData(academic_year, Semester(semester))
        semester_data.course_coordinator = course_coordinator
        semester_data.instructors = instructors
        semester_data.clo_target_levels = clo_target_levels

        # حفظ في المقرر
        self.course.set_semester_data(semester_data)

        # حفظ المقرر
        cm = CourseManager()
        if cm.save_course(self.course):
            # ربط منسق المقرر تلقائياً بالمقرر
            self._auto_assign_course_coordinator(course_coordinator)

            # ربط المدرسين تلقائياً بالشعب (سيتم تنفيذه لاحقاً)
            self._auto_assign_instructors(instructors)

            # تحديث جميع الشعب الموجودة لهذا الفصل الدراسي
            self._update_sections_target_levels(academic_year, semester, clo_target_levels)

            self.result = semester_data

            # إعادة تعيين حالة التغييرات
            self.has_unsaved_changes = False
            # إزالة * من العنوان
            title = self.title()
            if title.endswith(' *'):
                self.title(title[:-2])

            messagebox.showinfo(
                t('success', self.language),
                "تم حفظ بيانات الفصل الدراسي بنجاح" if self.language == 'ar' else "Semester data saved successfully",
                parent=self
            )
            self.destroy()
        else:
            messagebox.showerror(
                t('error', self.language),
                "فشل حفظ بيانات الفصل الدراسي" if self.language == 'ar' else "Failed to save semester data",
                parent=self
            )

    def _update_sections_target_levels(self, academic_year: str, semester: str, clo_target_levels: dict):
        """
        تحديث المستويات المستهدفة في جميع الشعب لهذا الفصل الدراسي
        Update target levels in all sections for this semester
        """
        try:
            from managers.section_manager import SectionManager
            sm = SectionManager()

            # الحصول على جميع شعب هذا المقرر
            sections = sm.get_sections_by_course(self.course.course_id)

            updated_count = 0
            for section in sections:
                # التحقق من أن الشعبة تنتمي لنفس الفصل الدراسي
                section_semester = section.semester.value if hasattr(section.semester, 'value') else section.semester
                if section.academic_year == academic_year and section_semester == semester:
                    # تحديث المستويات المستهدفة
                    section.clo_target_levels = clo_target_levels.copy()
                    # حفظ الشعبة
                    if sm.save_section(section):
                        updated_count += 1

            if updated_count > 0:
                print(f"Updated target levels in {updated_count} section(s)")

        except Exception as e:
            print(f"Error updating sections: {e}")

    def _auto_assign_course_coordinator(self, coordinator_name: str):
        """
        ربط منسق المقرر تلقائياً بالمقرر

        Args:
            coordinator_name: اسم منسق المقرر
        """
        try:
            if not coordinator_name or coordinator_name in ["لم يتم التعيين", "Not Set"]:
                return

            # البحث عن عضو هيئة التدريس باسم العرض (display name)
            # اسم العرض يكون بصيغة: "الرقم - الاسم (الدرجة)"
            faculty_member = self.faculty_manager.get_member_by_display_name(coordinator_name)

            if not faculty_member:
                print(f"⚠️ عضو هيئة التدريس غير موجود: {coordinator_name}")
                messagebox.showwarning(
                    "تحذير" if self.language == 'ar' else "Warning",
                    f"عضو هيئة التدريس '{coordinator_name}' غير موجود في قاعدة البيانات.\n"
                    f"لن يتم إنشاء حساب مستخدم تلقائياً.\n\n"
                    f"الرجاء إضافة عضو هيئة التدريس أولاً من قائمة إدارة أعضاء هيئة التدريس."
                    if self.language == 'ar' else
                    f"Faculty member '{coordinator_name}' not found in database.\n"
                    f"User account will not be created automatically.\n\n"
                    f"Please add the faculty member first from Faculty Management menu.",
                    parent=self
                )
                return

            # البحث عن المستخدم المرتبط بعضو هيئة التدريس
            user = self.access_control.get_user_by_faculty_id(faculty_member.faculty_id)

            if not user:
                # إنشاء مستخدم جديد لعضو هيئة التدريس
                username = User.generate_username(faculty_member.name, faculty_member.employee_id)
                password = User.generate_password(faculty_member.employee_id)

                user = self.access_control.create_user_from_faculty(
                    faculty_member,
                    roles=['course_coordinator']
                )

                if user:
                    print(f"✅ تم إنشاء حساب مستخدم لمنسق المقرر:")
                    print(f"   الاسم: {faculty_member.name}")
                    print(f"   اسم المستخدم: {username}")
                    print(f"   كلمة المرور: {password}")
                    print(f"   الدور: منسق مقرر")

                    # إظهار رسالة للمستخدم
                    messagebox.showinfo(
                        "تم إنشاء حساب مستخدم" if self.language == 'ar' else "User Account Created",
                        f"تم إنشاء حساب مستخدم لمنسق المقرر:\n\n"
                        f"الاسم: {faculty_member.name}\n"
                        f"اسم المستخدم: {username}\n"
                        f"كلمة المرور: {password}\n\n"
                        f"تم ربطه بالمقرر: {self.course.info.course_code}"
                        if self.language == 'ar' else
                        f"User account created for course coordinator:\n\n"
                        f"Name: {faculty_member.name}\n"
                        f"Username: {username}\n"
                        f"Password: {password}\n\n"
                        f"Assigned to course: {self.course.info.course_code}",
                        parent=self
                    )
                else:
                    print(f"⚠️ فشل إنشاء حساب المستخدم (ربما موجود مسبقاً)")
            else:
                # إضافة دور منسق المقرر إذا لم يكن موجوداً
                if 'course_coordinator' not in user.roles:
                    user.add_role('course_coordinator')
                    self.access_control.save_users()
                    print(f"✅ تم إضافة دور 'منسق مقرر' للمستخدم: {user.username}")

            # ربط المستخدم بالمقرر
            if user:
                self.access_control.assign_user_to_course(user.user_id, self.course.course_id)
                print(f"✅ تم ربط منسق المقرر {coordinator_name} بالمقرر {self.course.info.course_code}")

        except Exception as e:
            print(f"❌ خطأ في ربط منسق المقرر تلقائياً: {e}")
            import traceback
            traceback.print_exc()

    def _auto_assign_instructors(self, instructors: list):
        """
        ربط المدرسين تلقائياً بالشعب (placeholder - سيتم تنفيذه عند تعيين الشعب)

        Args:
            instructors: قائمة أسماء المدرسين
        """
        # هذه الدالة placeholder لأن ربط المدرسين بالشعب يحتاج معلومات الشعبة
        # سيتم تنفيذ الربط الفعلي عند تعيين مدرس لشعبة معينة
        pass
