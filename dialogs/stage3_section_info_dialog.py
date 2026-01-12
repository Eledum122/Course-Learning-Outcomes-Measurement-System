"""
حوار إدخال بيانات الشعبة - المرحلة الثالثة - الخطوة 1
Stage 3 Step 1: Section Information Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models import CourseSection, Course, Semester
from models.user import User
from managers.section_manager import SectionManager
from managers.course_manager import CourseManager
from managers.access_control import AccessControl
from managers.faculty_manager import FacultyManager
from config import FONTS
from translations import t


class Stage3SectionInfoDialog(tk.Toplevel):
    """حوار إدخال بيانات الشعبة"""

    def __init__(self, parent, course: Course, language: str = 'ar',
                 section: Optional[CourseSection] = None):
        super().__init__(parent)

        self.course = course
        self.language = language
        self.section = section  # للتعديل على شعبة موجودة
        self.result = None

        # تهيئة المديرين
        self.access_control = AccessControl()
        self.faculty_manager = FacultyManager()

        # إعداد النافذة
        self.title(t('stage3_step1_title', language) if language == 'en'
                  else "المرحلة الثالثة - الخطوة 1: بيانات الشعبة")
        self.geometry("850x650")
        self.resizable(True, True)

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # التحقق من اكتمال جدول المواصفات
        self._verify_specifications_table()

        # إنشاء الواجهة
        self._create_widgets()

        # تحميل قائمة المدرسين من FacultyManager
        self._load_instructors_list()

        # تحميل البيانات إذا كانت شعبة موجودة
        if self.section:
            self._load_section_data()
        else:
            # ملء البيانات الافتراضية من معلومات المقرر
            self._auto_fill_course_info()

        # مركزة النافذة
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _verify_specifications_table(self):
        """التحقق من اكتمال جدول المواصفات"""
        has_specifications = False
        for topic in self.course.topics:
            if hasattr(topic, 'specifications_table') and topic.specifications_table:
                has_specifications = True
                break

        if not has_specifications:
            msg_ar = "⚠️ لم يتم بناء جدول المواصفات لهذا المقرر.\n\nيجب إكمال المرحلة الثانية - الخطوة 4: جدول المواصفات أولاً."
            msg_en = "⚠️ Table of Specifications has not been created for this course.\n\nPlease complete Stage 2 - Step 4: Table of Specifications first."
            messagebox.showerror(
                t('error', self.language),
                msg_ar if self.language == 'ar' else msg_en,
                parent=self
            )
            self.destroy()

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # إطار قابل للتمرير
        canvas = tk.Canvas(self, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # دعم التمرير بعجلة الماوس
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الإطار الرئيسي داخل الإطار القابل للتمرير
        main_frame = tk.Frame(scrollable_frame, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # العنوان
        title_text = "بيانات الشعبة" if self.language == 'ar' else "Section Information"
        tk.Label(
            main_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='white',
            fg='#1976D2'
        ).pack(pady=(0, 20))

        # معلومات المقرر (للقراءة فقط)
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

        # نموذج إدخال بيانات الشعبة
        form_frame = tk.Frame(main_frame, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True)

        # رقم الشعبة
        self._create_form_field(
            form_frame, 0,
            "رقم الشعبة:" if self.language == 'ar' else "Section Number:",
            "section_number"
        )

        # السنة الدراسية (قائمة منسدلة)
        year_label = "السنة الدراسية:" if self.language == 'ar' else "Academic Year:"
        tk.Label(
            form_frame,
            text=year_label,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).grid(row=1, column=1 if self.language == 'ar' else 0, sticky='e' if self.language == 'ar' else 'w', pady=8)

        # جمع السنوات الدراسية من البيانات السابقة
        academic_years = self._get_academic_years()

        self.academic_year_var = tk.StringVar()
        self.academic_year_combo = ttk.Combobox(
            form_frame,
            textvariable=self.academic_year_var,
            values=academic_years,
            font=FONTS['english_main'],
            width=25
        )
        self.academic_year_combo.grid(row=1, column=0 if self.language == 'ar' else 1, sticky='ew', pady=8, padx=(0, 10) if self.language == 'ar' else (10, 0))

        # الفصل الدراسي
        semester_label = "الفصل الدراسي:" if self.language == 'ar' else "Semester:"
        tk.Label(
            form_frame,
            text=semester_label,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).grid(row=2, column=1 if self.language == 'ar' else 0, sticky='e' if self.language == 'ar' else 'w', pady=8)

        self.semester_var = tk.StringVar(value="First")
        semester_combo = ttk.Combobox(
            form_frame,
            textvariable=self.semester_var,
            values=["First", "Second", "Summer"],
            state='readonly',
            font=FONTS['english_main'],
            width=25
        )
        semester_combo.grid(row=2, column=0 if self.language == 'ar' else 1, sticky='ew', pady=8, padx=(0, 10) if self.language == 'ar' else (10, 0))

        # إضافة مستمع لتحديث منسق المقرر عند تغيير السنة أو الفصل
        self.academic_year_combo.bind('<<ComboboxSelected>>', self._on_semester_info_changed)
        self.academic_year_combo.bind('<KeyRelease>', self._on_semester_info_changed)
        semester_combo.bind('<<ComboboxSelected>>', self._on_semester_info_changed)

        # منسق المقرر
        self._create_form_field(
            form_frame, 3,
            "منسق المقرر:" if self.language == 'ar' else "Course Coordinator:",
            "course_coordinator"
        )

        # مدرس الشعبة (قائمة منسدلة)
        instructor_label = "مدرس الشعبة:" if self.language == 'ar' else "Section Instructor:"
        tk.Label(
            form_frame,
            text=instructor_label,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).grid(row=4, column=1 if self.language == 'ar' else 0, sticky='e' if self.language == 'ar' else 'w', pady=8)

        self.section_instructor_var = tk.StringVar()
        self.section_instructor_combo = ttk.Combobox(
            form_frame,
            textvariable=self.section_instructor_var,
            values=[],  # سيتم تحديثها عند اختيار الفصل
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=25
        )
        self.section_instructor_combo.grid(row=4, column=0 if self.language == 'ar' else 1, sticky='ew', pady=8, padx=(0, 10) if self.language == 'ar' else (10, 0))

        # القسم المستفيد (قائمة منسدلة)
        dept_label = t("beneficiary_department", self.language) + ":"
        tk.Label(
            form_frame,
            text=dept_label,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).grid(row=5, column=1 if self.language == 'ar' else 0, sticky='e' if self.language == 'ar' else 'w', pady=8)

        # جمع الأقسام المستفيدة من معلومات المقرر
        departments = self._get_beneficiary_departments()

        self.beneficiary_department_var = tk.StringVar()
        self.beneficiary_department_combo = ttk.Combobox(
            form_frame,
            textvariable=self.beneficiary_department_var,
            values=departments,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=25
        )
        self.beneficiary_department_combo.grid(row=5, column=0 if self.language == 'ar' else 1, sticky='ew', pady=8, padx=(0, 10) if self.language == 'ar' else (10, 0))

        # كلية القسم المستفيد (قائمة منسدلة)
        faculty_label = t("beneficiary_faculty", self.language) + ":"
        tk.Label(
            form_frame,
            text=faculty_label,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).grid(row=6, column=1 if self.language == 'ar' else 0, sticky='e' if self.language == 'ar' else 'w', pady=8)

        # جمع الكليات من معلومات المقرر
        faculties = self._get_beneficiary_faculties()

        self.beneficiary_faculty_var = tk.StringVar()
        self.beneficiary_faculty_combo = ttk.Combobox(
            form_frame,
            textvariable=self.beneficiary_faculty_var,
            values=faculties,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=25
        )
        self.beneficiary_faculty_combo.grid(row=6, column=0 if self.language == 'ar' else 1, sticky='ew', pady=8, padx=(0, 10) if self.language == 'ar' else (10, 0))

        # الشطر (طلاب/طالبات)
        gender_label = t('gender_section', self.language) + ":"
        tk.Label(
            form_frame,
            text=gender_label,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).grid(row=7, column=1 if self.language == 'ar' else 0, sticky='e' if self.language == 'ar' else 'w', pady=8)

        self.gender_var = tk.StringVar(value="Male")
        gender_combo = ttk.Combobox(
            form_frame,
            textvariable=self.gender_var,
            values=["Male", "Female"],
            state='readonly',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=25
        )
        gender_combo.grid(row=7, column=0 if self.language == 'ar' else 1, sticky='ew', pady=8, padx=(0, 10) if self.language == 'ar' else (10, 0))

        # تكوين الأعمدة
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # ملاحظة: المستويات المستهدفة للمخرجات تُدار مركزياً في نموذج إدارة الفصل الدراسي
        note_text = "ملاحظة: المستويات المستهدفة للمخرجات تُدار في نموذج إدارة الفصل الدراسي" if self.language == 'ar' \
                    else "Note: CLO target levels are managed in Semester Management"
        tk.Label(
            main_frame,
            text=note_text,
            font=FONTS['arabic_small'] if self.language == 'ar' else FONTS['english_small'],
            bg='white',
            fg='#666',
            pady=10
        ).pack()

        # الأزرار
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=(20, 20))

        save_text = "💾 حفظ" if self.language == 'ar' else "💾 Save"
        tk.Button(
            buttons_frame,
            text=save_text,
            command=self._save_section,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

        cancel_text = "✖ إلغاء" if self.language == 'ar' else "✖ Cancel"
        tk.Button(
            buttons_frame,
            text=cancel_text,
            command=self.destroy,
            bg='#F44336',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

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

        setattr(self, f"{field_name}_entry", entry)

    def _get_academic_years(self):
        """جمع السنوات الدراسية من بيانات الفصول السابقة"""
        years = set()

        # من بيانات الفصول الدراسية المحفوظة
        for key in self.course.semester_data.keys():
            academic_year = key.split('_')[0]
            years.add(academic_year)

        # إضافة السنة الحالية كخيار افتراضي
        from datetime import datetime
        current_hijri_year = datetime.now().year - 622  # تقريبي
        default_year = f"{current_hijri_year}-{current_hijri_year + 1}"
        years.add(default_year)

        return sorted(list(years), reverse=True)

    def _get_beneficiary_departments(self):
        """جمع الأقسام المستفيدة من معلومات المقرر"""
        departments = []

        # القسم الرئيسي
        if hasattr(self.course.info, 'department') and self.course.info.department:
            departments.append(self.course.info.department)

        # الأقسام الأخرى المستفيدة (التنسيق الجديد: مفصولة بـ |)
        if hasattr(self.course.info, 'other_departments') and self.course.info.other_departments:
            # دعم التنسيق الجديد (|) والقديم (,)
            separator = '|' if '|' in self.course.info.other_departments else ','
            other_depts = self.course.info.other_departments.split(separator)
            for dept in other_depts:
                dept = dept.strip()
                if dept and dept not in departments:
                    departments.append(dept)

        return departments

    def _get_beneficiary_faculties(self):
        """جمع الكليات من معلومات المقرر"""
        faculties = []

        # الكلية الرئيسية
        if hasattr(self.course.info, 'faculty') and self.course.info.faculty:
            faculties.append(self.course.info.faculty)

        # كلية الأقسام الأخرى (التنسيق الجديد: مفصولة بـ |)
        if hasattr(self.course.info, 'other_departments_faculty') and self.course.info.other_departments_faculty:
            # دعم التنسيق الجديد (|) والقديم (,)
            separator = '|' if '|' in self.course.info.other_departments_faculty else ','
            other_faculties = self.course.info.other_departments_faculty.split(separator)
            for faculty in other_faculties:
                faculty = faculty.strip()
                if faculty and faculty not in faculties:
                    faculties.append(faculty)

        return faculties

    def _on_semester_info_changed(self, event=None):
        """تحديث منسق المقرر وقائمة المدرسين عند تغيير السنة الدراسية أو الفصل"""
        academic_year = self.academic_year_var.get().strip()
        semester = self.semester_var.get()

        if academic_year and semester:
            # تحميل بيانات الفصل الدراسي
            semester_data = self.course.get_semester_data(academic_year, semester)

            if semester_data:
                # تحديث منسق المقرر
                if semester_data.course_coordinator:
                    self.course_coordinator_entry.delete(0, tk.END)
                    self.course_coordinator_entry.insert(0, semester_data.course_coordinator)

                # تحديث قائمة المدرسين من semester_data فقط
                instructors_list = []

                # إضافة المدرسين من semester_data
                if semester_data.instructors:
                    instructors_list.extend(semester_data.instructors)

                # إزالة المكررات والفرز
                instructors_list = sorted(list(set(instructors_list)))

                self.section_instructor_combo['values'] = instructors_list

    def _load_instructors_list(self):
        """تحميل قائمة المدرسين من بيانات الفصل الدراسي فقط"""
        instructors_list = []

        # تحميل من بيانات الفصل الدراسي إذا كانت موجودة
        academic_year = self.academic_year_var.get().strip()
        semester = self.semester_var.get()

        if academic_year and semester:
            semester_data = self.course.get_semester_data(academic_year, semester)
            if semester_data and semester_data.instructors:
                instructors_list.extend(semester_data.instructors)

        # إزالة المكررات والفرز
        instructors_list = sorted(list(set(instructors_list)))

        self.section_instructor_combo['values'] = instructors_list

    def _auto_fill_course_info(self):
        """ملء البيانات الافتراضية من معلومات المقرر"""
        # ملء القسم المستفيد
        if hasattr(self.course.info, 'other_departments') and self.course.info.other_departments:
            # دعم التنسيق الجديد (|) والقديم (,)
            separator = '|' if '|' in self.course.info.other_departments else ','
            first_dept = self.course.info.other_departments.split(separator)[0].strip()
            if first_dept:
                self.beneficiary_department_var.set(first_dept)

        # ملء كلية القسم المستفيد
        if hasattr(self.course.info, 'other_departments_faculty') and self.course.info.other_departments_faculty:
            # دعم التنسيق الجديد (|) والقديم (,)
            separator = '|' if '|' in self.course.info.other_departments_faculty else ','
            first_faculty = self.course.info.other_departments_faculty.split(separator)[0].strip()
            if first_faculty:
                self.beneficiary_faculty_var.set(first_faculty)

    def _load_section_data(self):
        """تحميل بيانات الشعبة للتعديل"""
        if not self.section:
            return

        self.section_number_entry.delete(0, tk.END)
        self.section_number_entry.insert(0, self.section.section_number)

        self.academic_year_var.set(self.section.academic_year)

        semester_value = self.section.semester.value if hasattr(self.section.semester, 'value') else self.section.semester
        self.semester_var.set(semester_value)

        self.course_coordinator_entry.delete(0, tk.END)
        self.course_coordinator_entry.insert(0, self.section.course_coordinator)

        self.section_instructor_var.set(self.section.section_instructor)

        self.beneficiary_department_var.set(self.section.beneficiary_department)

        self.beneficiary_faculty_var.set(self.section.beneficiary_faculty)

        # تحميل الشطر
        if hasattr(self.section, 'gender_section'):
            self.gender_var.set(self.section.gender_section)

    def _save_section(self):
        """حفظ بيانات الشعبة"""
        # جمع البيانات
        section_number = self.section_number_entry.get().strip()
        academic_year = self.academic_year_var.get().strip()
        semester = self.semester_var.get()
        course_coordinator = self.course_coordinator_entry.get().strip()
        section_instructor = self.section_instructor_var.get().strip()
        beneficiary_department = self.beneficiary_department_var.get().strip()
        beneficiary_faculty = self.beneficiary_faculty_var.get().strip()
        gender_section = self.gender_var.get()

        # التحقق من البيانات
        if not section_number:
            messagebox.showerror(
                t('error', self.language),
                "يجب إدخال رقم الشعبة" if self.language == 'ar' else "Section number is required",
                parent=self
            )
            return

        if not academic_year:
            messagebox.showerror(
                t('error', self.language),
                "يجب إدخال السنة الدراسية" if self.language == 'ar' else "Academic year is required",
                parent=self
            )
            return

        if not course_coordinator:
            messagebox.showerror(
                t('error', self.language),
                "يجب إدخال اسم منسق المقرر" if self.language == 'ar' else "Course coordinator is required",
                parent=self
            )
            return

        if not section_instructor:
            messagebox.showerror(
                t('error', self.language),
                "يجب إدخال اسم مدرس الشعبة" if self.language == 'ar' else "Section instructor is required",
                parent=self
            )
            return

        # إنشاء أو تحديث الشعبة
        sm = SectionManager()

        if self.section:
            # تحديث شعبة موجودة
            self.section.section_number = section_number
            self.section.academic_year = academic_year
            self.section.semester = Semester(semester)
            self.section.course_coordinator = course_coordinator
            self.section.section_instructor = section_instructor
            self.section.beneficiary_department = beneficiary_department
            self.section.beneficiary_faculty = beneficiary_faculty
            self.section.gender_section = gender_section
            self.section.section_data_completed = True

            # تحديث المستويات المستهدفة من بيانات الفصل الدراسي
            semester_data = self.course.get_semester_data(academic_year, semester)
            if semester_data and semester_data.clo_target_levels:
                self.section.clo_target_levels = semester_data.clo_target_levels.copy()
            else:
                # استخدام المستويات الافتراضية من CLOs
                self.section.clo_target_levels = {clo.code: clo.target_level for clo in self.course.clos}
        else:
            # إنشاء شعبة جديدة
            section_id = sm.generate_section_id(
                self.course.course_id,
                section_number,
                academic_year,
                semester
            )

            # التحقق من عدم وجود شعبة بنفس المعرف
            if sm.section_exists(section_id):
                messagebox.showerror(
                    t('error', self.language),
                    "هذه الشعبة موجودة بالفعل!" if self.language == 'ar' else "This section already exists!",
                    parent=self
                )
                return

            self.section = CourseSection(section_id)
            self.section.course_id = self.course.course_id
            self.section.section_number = section_number
            self.section.academic_year = academic_year
            self.section.semester = Semester(semester)
            self.section.course_coordinator = course_coordinator
            self.section.section_instructor = section_instructor
            self.section.beneficiary_department = beneficiary_department
            self.section.beneficiary_faculty = beneficiary_faculty
            self.section.gender_section = gender_section
            self.section.section_data_completed = True
            self.section.specifications_table_verified = True

            # نسخ المستويات المستهدفة من بيانات الفصل الدراسي
            semester_data = self.course.get_semester_data(academic_year, semester)
            if semester_data and semester_data.clo_target_levels:
                self.section.clo_target_levels = semester_data.clo_target_levels.copy()
            else:
                # استخدام المستويات الافتراضية من CLOs
                self.section.clo_target_levels = {clo.code: clo.target_level for clo in self.course.clos}

        # حفظ الشعبة
        if sm.save_section(self.section):
            # ربط مدرس الشعبة تلقائياً بالشعبة
            self._auto_assign_section_instructor(section_instructor, self.section.section_number)

            self.result = self.section
            messagebox.showinfo(
                t('success', self.language),
                "تم حفظ بيانات الشعبة بنجاح" if self.language == 'ar' else "Section data saved successfully",
                parent=self
            )
            self.destroy()
        else:
            messagebox.showerror(
                t('error', self.language),
                "فشل حفظ بيانات الشعبة" if self.language == 'ar' else "Failed to save section data",
                parent=self
            )

    def _auto_assign_section_instructor(self, instructor_name: str, section_number: str):
        """
        ربط مدرس الشعبة تلقائياً بالشعبة

        Args:
            instructor_name: اسم مدرس الشعبة
            section_number: رقم الشعبة
        """
        try:
            if not instructor_name:
                return

            # البحث عن عضو هيئة التدريس باسم العرض (display name)
            # اسم العرض يكون بصيغة: "الرقم - الاسم (الدرجة)"
            faculty_member = self.faculty_manager.get_member_by_display_name(instructor_name)

            if not faculty_member:
                print(f"⚠️ عضو هيئة التدريس غير موجود: {instructor_name}")
                messagebox.showwarning(
                    "تحذير" if self.language == 'ar' else "Warning",
                    f"عضو هيئة التدريس '{instructor_name}' غير موجود في قاعدة البيانات.\n"
                    f"لن يتم إنشاء حساب مستخدم تلقائياً.\n\n"
                    f"الرجاء إضافة عضو هيئة التدريس أولاً من قائمة إدارة أعضاء هيئة التدريس."
                    if self.language == 'ar' else
                    f"Faculty member '{instructor_name}' not found in database.\n"
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
                    roles=['section_instructor']
                )

                if user:
                    print(f"✅ تم إنشاء حساب مستخدم لمدرس الشعبة:")
                    print(f"   الاسم: {faculty_member.name}")
                    print(f"   اسم المستخدم: {username}")
                    print(f"   كلمة المرور: {password}")
                    print(f"   الدور: مدرس شعبة")

                    # إظهار رسالة للمستخدم
                    messagebox.showinfo(
                        "تم إنشاء حساب مستخدم" if self.language == 'ar' else "User Account Created",
                        f"تم إنشاء حساب مستخدم لمدرس الشعبة:\n\n"
                        f"الاسم: {faculty_member.name}\n"
                        f"اسم المستخدم: {username}\n"
                        f"كلمة المرور: {password}\n\n"
                        f"تم ربطه بالشعبة: {section_number}\n"
                        f"في المقرر: {self.course.info.course_code}"
                        if self.language == 'ar' else
                        f"User account created for section instructor:\n\n"
                        f"Name: {faculty_member.name}\n"
                        f"Username: {username}\n"
                        f"Password: {password}\n\n"
                        f"Assigned to section: {section_number}\n"
                        f"Course: {self.course.info.course_code}",
                        parent=self
                    )
                else:
                    print(f"⚠️ فشل إنشاء حساب المستخدم (ربما موجود مسبقاً)")
            else:
                # إضافة دور مدرس شعبة إذا لم يكن موجوداً
                if 'section_instructor' not in user.roles:
                    user.add_role('section_instructor')
                    self.access_control.save_users()
                    print(f"✅ تم إضافة دور 'مدرس شعبة' للمستخدم: {user.username}")

            # ربط المستخدم بالشعبة
            if user:
                self.access_control.assign_user_to_section(
                    user.user_id,
                    self.course.course_id,
                    section_number
                )
                print(f"✅ تم ربط مدرس الشعبة {instructor_name} بالشعبة {section_number} في المقرر {self.course.info.course_code}")

        except Exception as e:
            print(f"❌ خطأ في ربط مدرس الشعبة تلقائياً: {e}")
            import traceback
            traceback.print_exc()
