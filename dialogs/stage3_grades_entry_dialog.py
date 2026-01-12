"""
حوار إدخال درجات الطلاب - المرحلة الثالثة - الخطوة 3
Stage 3 Step 3: Grades Entry Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, List
import os
from models import CourseSection, Student, StudentStatus, Course
from managers.section_manager import SectionManager
from managers.course_manager import CourseManager
from config import FONTS, COLORS
from translations import t


class Stage3GradesEntryDialog(tk.Toplevel):
    """حوار إدخال درجات الطلاب"""

    def __init__(self, parent, section: CourseSection, language: str = 'ar'):
        super().__init__(parent)

        self.section = section
        self.language = language

        # تحميل بيانات المقرر
        cm = CourseManager()
        self.course = cm.load_course(section.course_id)

        if not self.course:
            messagebox.showerror(
                t('error', language),
                "فشل تحميل بيانات المقرر" if language == 'ar' else "Failed to load course data"
            )
            self.destroy()
            return

        # خريطة الدرجات القصوى لكل نشاط ومخرج من جدول المواصفات
        self.max_marks = self._build_max_marks_map()

        # عناصر الإدخال
        self.entry_widgets = {}

        # إعداد النافذة
        self.title("المرحلة الثالثة - الخطوة 3: إدخال الدرجات" if language == 'ar'
                  else "Stage 3 - Step 3: Grades Entry")

        # جعل النافذة بملء الشاشة
        self.state('zoomed')

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # إنشاء الواجهة
        self._create_widgets()

        # تحميل الدرجات الموجودة
        self._load_grades()

    def _build_max_marks_map(self) -> Dict[str, Dict[str, float]]:
        """بناء خريطة الدرجات القصوى من جدول المواصفات"""
        max_marks = {}

        # لكل نشاط، نبني خريطة CLO -> Max Mark
        for activity in self.course.activities:
            activity_marks = {}

            # المرور على جميع المواضيع وجمع الدرجات لكل CLO
            for topic in self.course.topics:
                if hasattr(topic, 'specifications_table') and topic.specifications_table:
                    for clo in self.course.clos:
                        key = f"{clo.code}|{activity.name}"
                        mark = topic.specifications_table.get(key, 0)

                        if mark > 0:
                            if clo.code not in activity_marks:
                                activity_marks[clo.code] = 0
                            activity_marks[clo.code] += mark

            max_marks[activity.name] = activity_marks

        return max_marks

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # الإطار الرئيسي
        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # إطار المعلومات العلوي
        self._create_info_panel(main_frame)

        # إطار الأزرار
        self._create_buttons_panel(main_frame)

        # إطار الجدول
        self._create_grades_table(main_frame)

        # إطار الأزرار السفلية
        self._create_bottom_buttons(main_frame)

    def _create_info_panel(self, parent):
        """إنشاء لوحة المعلومات"""
        info_frame = tk.Frame(parent, bg=COLORS['primary_green'], padx=20, pady=15)
        info_frame.pack(fill=tk.X)

        # الصف الأول: معلومات المقرر والشعبة
        row1 = tk.Frame(info_frame, bg=COLORS['primary_green'])
        row1.pack(fill=tk.X, pady=(0, 10))

        course_text = f"{self.course.info.course_code} - {self.course.info.course_title}"
        tk.Label(
            row1,
            text=course_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg=COLORS['primary_green'],
            fg='white'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

        section_text = f"الشعبة: {self.section.section_number} - {self.section.academic_year} - " if self.language == 'ar' \
            else f"Section: {self.section.section_number} - {self.section.academic_year} - "

        semester_map = {'First': 'الأول', 'Second': 'الثاني', 'Summer': 'الصيفي'}
        semester_value = self.section.semester.value if hasattr(self.section.semester, 'value') else self.section.semester
        semester_text = semester_map.get(semester_value, semester_value) if self.language == 'ar' else semester_value

        tk.Label(
            row1,
            text=section_text + semester_text,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg=COLORS['primary_green'],
            fg='white'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

        # الصف الثاني: إحصائيات الطلاب
        row2 = tk.Frame(info_frame, bg=COLORS['primary_green'])
        row2.pack(fill=tk.X)

        # حساب الإحصائيات
        total = len(self.section.students)
        regular = len([s for s in self.section.students if s.status == StudentStatus.REGULAR])
        dropped = len([s for s in self.section.students if s.status == StudentStatus.DROPPED])
        prohibited = len([s for s in self.section.students if s.status == StudentStatus.PROHIBITED])
        incomplete = len([s for s in self.section.students if s.status == StudentStatus.INCOMPLETE])

        if self.language == 'ar':
            stats_text = f"إجمالي: {total} | منتظم: {regular} | معتذر: {dropped} | محروم: {prohibited} | غير مكتمل: {incomplete}"
        else:
            stats_text = f"Total: {total} | Regular: {regular} | Dropped: {dropped} | Prohibited: {prohibited} | Incomplete: {incomplete}"

        tk.Label(
            row2,
            text=stats_text,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg=COLORS['primary_green'],
            fg='white'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

    def _create_buttons_panel(self, parent):
        """إنشاء لوحة الأزرار"""
        buttons_frame = tk.Frame(parent, bg='white', padx=10, pady=10)
        buttons_frame.pack(fill=tk.X)

        # زر رفع ملف Excel
        upload_text = "📁 رفع ملف Excel للنشاط" if self.language == 'ar' else "📁 Upload Excel for Activity"
        tk.Button(
            buttons_frame,
            text=upload_text,
            command=self._import_activity_grades,
            bg='#2196F3',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=25,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر تحميل نموذج Excel
        template_text = "📥 تحميل نموذج Excel" if self.language == 'ar' else "📥 Download Excel Template"
        tk.Button(
            buttons_frame,
            text=template_text,
            command=self._download_grades_template,
            bg='#9C27B0',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=25,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

    def _create_grades_table(self, parent):
        """إنشاء جدول الدرجات"""
        # إطار قابل للتمرير
        container = tk.Frame(parent, bg='white')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas و Scrollbars
        canvas = tk.Canvas(container, bg='white')
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)

        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # تعبئة الجدول
        self._fill_grades_table(scrollable_frame)

        # ترتيب العناصر
        canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

    def _fill_grades_table(self, parent):
        """ملء جدول الدرجات"""
        # رأس الجدول
        headers_row = 0
        col = 0

        # رقم الطالب
        tk.Label(
            parent, text="Seq" if self.language == 'en' else "#",
            font=FONTS['english_main'], bg='#E3F2FD', relief=tk.RIDGE,
            width=5, pady=8
        ).grid(row=headers_row, column=col, sticky='nsew')
        col += 1

        # الرقم الجامعي
        tk.Label(
            parent, text="Student No" if self.language == 'en' else "الرقم الجامعي",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='#E3F2FD', relief=tk.RIDGE, width=15, pady=8
        ).grid(row=headers_row, column=col, sticky='nsew')
        col += 1

        # الاسم
        tk.Label(
            parent, text="Student Name" if self.language == 'en' else "اسم الطالب",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='#E3F2FD', relief=tk.RIDGE, width=35, pady=8
        ).grid(row=headers_row, column=col, sticky='nsew')
        col += 1

        # الحالة
        tk.Label(
            parent, text="Status" if self.language == 'en' else "الحالة",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='#E3F2FD', relief=tk.RIDGE, width=12, pady=8
        ).grid(row=headers_row, column=col, sticky='nsew')
        col += 1

        # أعمدة الأنشطة - كل نشاط له أعمدة فرعية حسب المخرجات
        activity_start_col = col
        for activity in self.course.activities:
            # عدد المخرجات التي يقيسها هذا النشاط (فقط التي قيمتها أكبر من صفر)
            clos_for_activity = []
            if hasattr(activity, 'measures_clos') and activity.measures_clos:
                for clo in self.course.clos:
                    if clo.code in activity.measures_clos:
                        # التحقق من أن الدرجة القصوى أكبر من صفر
                        max_mark = self.max_marks.get(activity.name, {}).get(clo.code, 0)
                        if max_mark > 0:
                            clos_for_activity.append(clo)

            if not clos_for_activity:
                continue

            # عنوان النشاط (يمتد على جميع أعمدة المخرجات)
            activity_label = tk.Label(
                parent,
                text=f"{activity.name}\n({activity.mark:.0f})",
                font=FONTS['arabic_bold'] if self.language == 'ar' else FONTS['bold'],
                bg='#FFE082',
                relief=tk.RIDGE,
                pady=5
            )
            activity_label.grid(row=headers_row, column=col, columnspan=len(clos_for_activity), sticky='ew')

            # عناوين المخرجات الفرعية (فقط التي قيمتها أكبر من صفر)
            for clo in clos_for_activity:
                max_mark = self.max_marks.get(activity.name, {}).get(clo.code, 0)
                clo_label = tk.Label(
                    parent,
                    text=f"{clo.code}\n({max_mark:.0f})",
                    font=FONTS['english_small'],
                    bg='#FFF9C4',
                    relief=tk.RIDGE,
                    width=8,
                    pady=5
                )
                clo_label.grid(row=headers_row + 1, column=col, sticky='nsew')
                col += 1

        # إجمالي الدرجة
        tk.Label(
            parent, text="Total\n(100)" if self.language == 'en' else "المجموع\n(100)",
            font=FONTS['arabic_bold'] if self.language == 'ar' else FONTS['bold'],
            bg='#C8E6C9', relief=tk.RIDGE, width=10, pady=8
        ).grid(row=headers_row, column=col, rowspan=2, sticky='nsew')

        # صفوف الطلاب
        students = sorted([s for s in self.section.students], key=lambda x: x.seq)

        for row_idx, student in enumerate(students, start=headers_row + 2):
            col = 0

            # رقم الترتيب
            tk.Label(
                parent, text=str(student.seq),
                font=FONTS['english_main'], bg='white', relief=tk.RIDGE,
                width=5, pady=5
            ).grid(row=row_idx, column=col, sticky='nsew')
            col += 1

            # الرقم الجامعي
            tk.Label(
                parent, text=student.student_id,
                font=FONTS['english_main'], bg='white', relief=tk.RIDGE,
                width=15, pady=5
            ).grid(row=row_idx, column=col, sticky='nsew')
            col += 1

            # الاسم
            tk.Label(
                parent, text=student.name,
                font=FONTS['arabic_small'] if self.language == 'ar' else FONTS['english_small'],
                bg='white', relief=tk.RIDGE, width=35, pady=5, anchor='w', padx=5
            ).grid(row=row_idx, column=col, sticky='nsew')
            col += 1

            # الحالة
            status_display = self._get_status_display(student.status)
            status_bg = {
                StudentStatus.REGULAR: 'white',
                StudentStatus.DROPPED: '#FFECB3',
                StudentStatus.PROHIBITED: '#FFCDD2',
                StudentStatus.INCOMPLETE: '#E1BEE7'
            }.get(student.status, 'white')

            tk.Label(
                parent, text=status_display,
                font=FONTS['arabic_small'] if self.language == 'ar' else FONTS['english_small'],
                bg=status_bg, relief=tk.RIDGE, width=12, pady=5
            ).grid(row=row_idx, column=col, sticky='nsew')
            col += 1

            # حقول إدخال الدرجات
            row_total = 0
            for activity in self.course.activities:
                # عدد المخرجات التي يقيسها هذا النشاط (فقط التي قيمتها أكبر من صفر)
                clos_for_activity = []
                if hasattr(activity, 'measures_clos') and activity.measures_clos:
                    for clo in self.course.clos:
                        if clo.code in activity.measures_clos:
                            # التحقق من أن الدرجة القصوى أكبر من صفر
                            max_mark = self.max_marks.get(activity.name, {}).get(clo.code, 0)
                            if max_mark > 0:
                                clos_for_activity.append(clo)

                if not clos_for_activity:
                    continue

                for clo in clos_for_activity:
                    max_mark = self.max_marks.get(activity.name, {}).get(clo.code, 0)

                    # حقل الإدخال
                    entry = tk.Entry(
                        parent,
                        font=FONTS['english_main'],
                        width=8,
                        justify='center',
                        relief=tk.RIDGE,
                        validate='key',
                        validatecommand=(parent.register(self._validate_number), '%P')
                    )
                    entry.grid(row=row_idx, column=col, sticky='nsew', padx=1, pady=1)

                    # تخزين المعلومات
                    entry_key = f"{student.student_id}|{activity.name}|{clo.code}"
                    self.entry_widgets[entry_key] = {
                        'widget': entry,
                        'student_id': student.student_id,
                        'activity': activity.name,
                        'clo': clo.code,
                        'max_mark': max_mark
                    }

                    # ربط حدث التغيير
                    entry.bind('<FocusOut>', lambda e, ek=entry_key: self._validate_entry(ek))
                    entry.bind('<Return>', lambda e, ek=entry_key: self._validate_entry(ek))

                    col += 1

            # المجموع الكلي
            total_label = tk.Label(
                parent,
                text="0.0",
                font=FONTS['english_main'],
                bg='#E8F5E9',
                relief=tk.RIDGE,
                width=10,
                pady=5
            )
            total_label.grid(row=row_idx, column=col, sticky='nsew')

            # تخزين label المجموع
            self.entry_widgets[f"{student.student_id}|TOTAL"] = {
                'widget': total_label,
                'type': 'total'
            }

    def _validate_number(self, value):
        """التحقق من أن القيمة رقم"""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _validate_entry(self, entry_key):
        """التحقق من الدرجة المدخلة وتلوين الخلية"""
        entry_info = self.entry_widgets.get(entry_key)
        if not entry_info:
            return

        entry = entry_info['widget']
        max_mark = entry_info['max_mark']

        value_str = entry.get().strip()
        if not value_str:
            entry.config(bg='white')
            self._update_student_total(entry_info['student_id'])
            return

        try:
            value = float(value_str)

            # التحقق من القيمة
            if value < 0:
                entry.config(bg='#FFCDD2')  # أحمر فاتح
                messagebox.showwarning(
                    t('warning', self.language),
                    "الدرجة لا يمكن أن تكون سالبة" if self.language == 'ar' else "Mark cannot be negative",
                    parent=self
                )
            elif value > max_mark:
                entry.config(bg='#FF5252')  # أحمر
                messagebox.showwarning(
                    t('warning', self.language),
                    f"الدرجة ({value}) أكبر من الدرجة القصوى ({max_mark})" if self.language == 'ar'
                    else f"Mark ({value}) exceeds maximum ({max_mark})",
                    parent=self
                )
            else:
                entry.config(bg='white')

            # تحديث المجموع
            self._update_student_total(entry_info['student_id'])

        except ValueError:
            entry.config(bg='#FFCDD2')

    def _update_student_total(self, student_id):
        """تحديث المجموع الكلي للطالب"""
        total = 0.0

        # جمع جميع الدرجات للطالب
        for key, info in self.entry_widgets.items():
            if key.startswith(student_id) and '|TOTAL' not in key:
                value_str = info['widget'].get().strip()
                if value_str:
                    try:
                        total += float(value_str)
                    except ValueError:
                        pass

        # تحديث label المجموع
        total_key = f"{student_id}|TOTAL"
        if total_key in self.entry_widgets:
            self.entry_widgets[total_key]['widget'].config(text=f"{total:.1f}")

    def _get_status_display(self, status):
        """الحصول على نص عرض الحالة"""
        if self.language == 'ar':
            status_map = {
                StudentStatus.REGULAR: 'منتظم',
                StudentStatus.DROPPED: 'معتذر',
                StudentStatus.PROHIBITED: 'محروم',
                StudentStatus.INCOMPLETE: 'غير مكتمل'
            }
        else:
            status_map = {
                StudentStatus.REGULAR: 'Regular',
                StudentStatus.DROPPED: 'Dropped',
                StudentStatus.PROHIBITED: 'Prohibited',
                StudentStatus.INCOMPLETE: 'Incomplete'
            }

        if isinstance(status, str):
            status = StudentStatus(status)

        return status_map.get(status, status.value)

    def _create_bottom_buttons(self, parent):
        """إنشاء الأزرار السفلية"""
        buttons_frame = tk.Frame(parent, bg='white', padx=10, pady=15)
        buttons_frame.pack(fill=tk.X)

        # زر حفظ الدرجات (يتطلب اكتمال درجات الطلاب المنتظمين)
        save_text = "💾 حفظ الدرجات" if self.language == 'ar' else "💾 Save Grades"
        tk.Button(
            buttons_frame,
            text=save_text,
            command=lambda: self._save_grades(as_draft=False),
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=20,
            cursor='hand2',
            pady=10
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر حفظ كمسودة (بدون التحقق من الاكتمال)
        draft_text = "📝 حفظ كمسودة" if self.language == 'ar' else "📝 Save as Draft"
        tk.Button(
            buttons_frame,
            text=draft_text,
            command=lambda: self._save_grades(as_draft=True),
            bg='#FF9800',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=20,
            cursor='hand2',
            pady=10
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر إغلاق
        close_text = "إغلاق" if self.language == 'ar' else "Close"
        tk.Button(
            buttons_frame,
            text=close_text,
            command=self.destroy,
            bg='#757575',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=20,
            cursor='hand2',
            pady=10
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

    def _load_grades(self):
        """تحميل الدرجات الموجودة"""
        for student in self.section.students:
            # تحميل درجات الأنشطة
            for activity_name, marks_dict in student.activity_marks.items():
                for clo_code, mark in marks_dict.items():
                    entry_key = f"{student.student_id}|{activity_name}|{clo_code}"
                    if entry_key in self.entry_widgets:
                        self.entry_widgets[entry_key]['widget'].delete(0, tk.END)
                        self.entry_widgets[entry_key]['widget'].insert(0, f"{mark:.1f}")

            # تحديث المجموع
            self._update_student_total(student.student_id)

    def _check_regular_students_completion(self) -> List[str]:
        """
        التحقق من اكتمال درجات الطلاب المنتظمين فقط

        Returns:
            قائمة بأسماء الطلاب المنتظمين الذين لديهم درجات ناقصة
        """
        missing_grades = []

        for student in self.section.students:
            # التحقق من الطلاب المنتظمين فقط
            if student.status != StudentStatus.REGULAR:
                continue

            # التحقق من جميع الأنشطة
            for activity in self.course.activities:
                # الحصول على CLOs المرتبطة بالنشاط
                clos_for_activity = []
                if hasattr(activity, 'measures_clos') and activity.measures_clos:
                    clos_for_activity = [clo for clo in self.course.clos if clo.code in activity.measures_clos]

                # التحقق من كل CLO
                for clo in clos_for_activity:
                    entry_key = f"{student.student_id}|{activity.name}|{clo.code}"
                    if entry_key in self.entry_widgets:
                        value_str = self.entry_widgets[entry_key]['widget'].get().strip()
                        if not value_str:
                            student_info = f"{student.name} ({student.student_id}) - {activity.name} - {clo.code}"
                            missing_grades.append(student_info)
                            break  # الانتقال للطالب التالي

                if missing_grades and student.student_id in missing_grades[-1]:
                    break  # وجدنا درجة ناقصة لهذا الطالب، ننتقل للتالي

        return missing_grades

    def _save_grades(self, as_draft=False):
        """
        حفظ الدرجات

        Args:
            as_draft: إذا كان True، يتم الحفظ كمسودة بدون التحقق من اكتمال الدرجات
        """
        # التحقق من وجود درجات غير صحيحة
        invalid_entries = []
        for key, info in self.entry_widgets.items():
            if '|TOTAL' in key or 'type' in info:
                continue

            entry = info['widget']
            value_str = entry.get().strip()

            if value_str:
                try:
                    value = float(value_str)
                    if value > info['max_mark']:
                        invalid_entries.append(key)
                except ValueError:
                    invalid_entries.append(key)

        if invalid_entries:
            messagebox.showerror(
                t('error', self.language),
                f"يوجد {len(invalid_entries)} درجة غير صحيحة. الرجاء تصحيحها قبل الحفظ."
                if self.language == 'ar' else
                f"There are {len(invalid_entries)} invalid marks. Please correct them before saving.",
                parent=self
            )
            return

        # إذا لم يكن حفظ كمسودة، التحقق من اكتمال درجات الطلاب المنتظمين فقط
        if not as_draft:
            missing_grades = self._check_regular_students_completion()
            if missing_grades:
                msg = "لم يتم إدخال جميع درجات الطلاب المنتظمين:\n\n" if self.language == 'ar' else "Not all regular students have complete grades:\n\n"
                msg += "\n".join(missing_grades[:5])  # عرض أول 5 فقط
                if len(missing_grades) > 5:
                    msg += f"\n... و {len(missing_grades) - 5} طالب آخرين" if self.language == 'ar' else f"\n... and {len(missing_grades) - 5} more students"
                msg += "\n\nاستخدم 'حفظ كمسودة' إذا كنت تريد الحفظ بدون اكتمال الدرجات" if self.language == 'ar' else "\n\nUse 'Save as Draft' if you want to save without complete grades"

                messagebox.showwarning(
                    t('warning', self.language) if hasattr(t('warning', self.language), '__call__') else "تحذير / Warning",
                    msg,
                    parent=self
                )
                return

        # حفظ الدرجات
        for student in self.section.students:
            student.activity_marks = {}
            student.total_mark = 0.0

            for activity in self.course.activities:
                activity_marks = {}

                clos_for_activity = []
                if hasattr(activity, 'measures_clos') and activity.measures_clos:
                    clos_for_activity = [clo for clo in self.course.clos if clo.code in activity.measures_clos]

                for clo in clos_for_activity:
                    entry_key = f"{student.student_id}|{activity.name}|{clo.code}"
                    if entry_key in self.entry_widgets:
                        value_str = self.entry_widgets[entry_key]['widget'].get().strip()
                        if value_str:
                            try:
                                mark = float(value_str)
                                activity_marks[clo.code] = mark
                                student.total_mark += mark
                            except ValueError:
                                pass

                if activity_marks:
                    student.activity_marks[activity.name] = activity_marks

        # حساب درجات المخرجات
        self._calculate_clo_marks()

        # تحديد حالة النجاح
        passing_mark = self.course.info.total_mark * (self.course.info.passing_percentage / 100)
        for student in self.section.students:
            student.passed = student.total_mark >= passing_mark

        # تحديث حالة الإكمال
        # إذا كان حفظ نهائي (ليس مسودة)، تعيين الحالة كمكتمل
        # إذا كان حفظ كمسودة، الحالة تبقى كما هي أو false
        self.section.grades_data_completed = not as_draft

        # حفظ الشعبة
        sm = SectionManager()
        if sm.save_section(self.section):
            # تحديد نوع الرسالة حسب نوع الحفظ
            if as_draft:
                msg = f"📝 تم حفظ الدرجات كمسودة لـ {len(self.section.students)} طالب" if self.language == 'ar' else f"📝 Grades saved as draft for {len(self.section.students)} students"
            else:
                msg = f"✅ تم حفظ درجات {len(self.section.students)} طالب بنجاح" if self.language == 'ar' else f"✅ Successfully saved grades for {len(self.section.students)} students"

            messagebox.showinfo(
                t('success', self.language),
                msg,
                parent=self
            )
        else:
            messagebox.showerror(
                t('error', self.language),
                "فشل حفظ الدرجات" if self.language == 'ar' else "Failed to save grades",
                parent=self
            )

    def _calculate_clo_marks(self):
        """حساب درجات المخرجات لكل طالب"""
        for student in self.section.students:
            student.clo_marks = {}

            # لكل مخرج، نجمع الدرجات من جميع الأنشطة
            for clo in self.course.clos:
                total_clo_mark = 0.0

                for activity_name, marks_dict in student.activity_marks.items():
                    if clo.code in marks_dict:
                        total_clo_mark += marks_dict[clo.code]

                if total_clo_mark > 0:
                    student.clo_marks[clo.code] = total_clo_mark

    def _import_activity_grades(self):
        """استيراد درجات نشاط من Excel"""
        # اختيار النشاط
        activity_names = [a.name for a in self.course.activities]
        if not activity_names:
            messagebox.showwarning(
                t('warning', self.language),
                "لا توجد أنشطة" if self.language == 'ar' else "No activities found",
                parent=self
            )
            return

        # نافذة اختيار النشاط
        select_dialog = tk.Toplevel(self)
        select_dialog.title("اختر النشاط" if self.language == 'ar' else "Select Activity")
        select_dialog.geometry("400x200")
        select_dialog.transient(self)
        select_dialog.grab_set()

        tk.Label(
            select_dialog,
            text="اختر النشاط:" if self.language == 'ar' else "Select Activity:",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main']
        ).pack(pady=20)

        selected_activity = tk.StringVar(value=activity_names[0])
        combo = ttk.Combobox(
            select_dialog,
            textvariable=selected_activity,
            values=activity_names,
            state='readonly',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=30
        )
        combo.pack(pady=10)

        def proceed_import():
            activity_name = selected_activity.get()
            select_dialog.destroy()
            self._do_import_activity(activity_name)

        tk.Button(
            select_dialog,
            text="متابعة" if self.language == 'ar' else "Continue",
            command=proceed_import,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15
        ).pack(pady=10)

    def _do_import_activity(self, activity_name):
        """تنفيذ استيراد درجات نشاط من Excel"""
        file_path = filedialog.askopenfilename(
            title=f"اختر ملف Excel للنشاط: {activity_name}" if self.language == 'ar'
                  else f"Select Excel file for activity: {activity_name}",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ],
            parent=self
        )

        if not file_path:
            return

        try:
            import pandas as pd

            # قراءة ملف Excel
            df = pd.read_excel(file_path)

            # التحقق من الأعمدة المطلوبة
            required_columns = ['Student No']

            # الحصول على المخرجات لهذا النشاط
            activity = next((a for a in self.course.activities if a.name == activity_name), None)
            if not activity:
                messagebox.showerror(
                    t('error', self.language),
                    "لم يتم العثور على النشاط" if self.language == 'ar' else "Activity not found",
                    parent=self
                )
                return

            # المخرجات المطلوبة (فقط التي قيمتها > 0)
            clos_for_activity = []
            if hasattr(activity, 'measures_clos') and activity.measures_clos:
                for clo in self.course.clos:
                    if clo.code in activity.measures_clos:
                        max_mark = self.max_marks.get(activity_name, {}).get(clo.code, 0)
                        if max_mark > 0:
                            clos_for_activity.append(clo.code)

            # التحقق من تنسيق الأعمدة - يدعم تنسيقين:
            # 1. Activity_CLO (مثل: Mid Exam_K1) - من الملف المُنزّل
            # 2. CLO فقط (مثل: K1) - تنسيق مخصص

            # التحقق من التنسيق الأول: Activity_CLO
            format1_columns = [f"{activity_name}_{clo}" for clo in clos_for_activity]
            format1_exists = all(col in df.columns for col in format1_columns)

            # التحقق من التنسيق الثاني: CLO فقط
            format2_exists = all(clo in df.columns for clo in clos_for_activity)

            if not format1_exists and not format2_exists:
                # عرض رسالة خطأ توضح التنسيقات المقبولة
                expected_format1 = ', '.join(format1_columns)
                expected_format2 = ', '.join(['Student No'] + clos_for_activity)

                messagebox.showerror(
                    t('error', self.language),
                    f"الأعمدة المطلوبة مفقودة.\n\nالتنسيق 1 (ملف كامل):\n{expected_format1}\n\nأو التنسيق 2 (نشاط واحد):\n{expected_format2}"
                    if self.language == 'ar' else
                    f"Required columns missing.\n\nFormat 1 (full template):\n{expected_format1}\n\nOr Format 2 (single activity):\n{expected_format2}",
                    parent=self
                )
                return

            # تحديد التنسيق المستخدم
            use_format1 = format1_exists

            # استيراد الدرجات
            imported_count = 0
            errors = []

            for idx, row in df.iterrows():
                student_id = str(row['Student No']).strip()

                # البحث عن الطالب
                for clo_code in clos_for_activity:
                    # تحديد اسم العمود حسب التنسيق
                    column_name = f"{activity_name}_{clo_code}" if use_format1 else clo_code

                    if pd.isna(row[column_name]) or row[column_name] == "":
                        continue

                    entry_key = f"{student_id}|{activity_name}|{clo_code}"
                    if entry_key in self.entry_widgets:
                        try:
                            mark = float(row[column_name])
                            max_mark = self.entry_widgets[entry_key]['max_mark']

                            if mark < 0:
                                errors.append(f"{student_id}: {clo_code} - درجة سالبة")
                            elif mark > max_mark:
                                errors.append(f"{student_id}: {clo_code} - الدرجة ({mark}) أكبر من القصوى ({max_mark})")
                            else:
                                # إدخال الدرجة
                                entry = self.entry_widgets[entry_key]['widget']
                                entry.delete(0, tk.END)
                                entry.insert(0, f"{mark:.1f}")
                                self._validate_entry(entry_key)
                                imported_count += 1
                        except (ValueError, TypeError) as e:
                            errors.append(f"{student_id}: {clo_code} - قيمة غير صحيحة")

            # عرض النتائج
            message = f"تم استيراد {imported_count} درجة بنجاح" if self.language == 'ar' \
                else f"Successfully imported {imported_count} grades"

            if errors:
                message += f"\n\nأخطاء ({len(errors)}):\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    message += f"\n... و {len(errors) - 10} أخطاء أخرى"

            messagebox.showinfo(
                t('success', self.language) if not errors else t('warning', self.language),
                message,
                parent=self
            )

        except ImportError:
            messagebox.showerror(
                t('error', self.language),
                "مكتبة pandas غير مثبتة.\n\nالرجاء تثبيتها باستخدام: pip install pandas openpyxl"
                if self.language == 'ar' else
                "pandas library is not installed.\n\nPlease install it using: pip install pandas openpyxl",
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                t('error', self.language),
                f"فشل استيراد الملف:\n{str(e)}" if self.language == 'ar'
                else f"Failed to import file:\n{str(e)}",
                parent=self
            )

    def _get_excel_column_name(self, n):
        """
        تحويل رقم العمود إلى اسم عمود Excel
        Convert column index to Excel column name (0='A', 25='Z', 26='AA', etc.)
        """
        result = ""
        while n >= 0:
            result = chr(65 + (n % 26)) + result
            n = n // 26 - 1
            if n < 0:
                break
        return result

    def _download_grades_template(self):
        """تحميل نموذج Excel للدرجات"""
        try:
            import pandas as pd

            # بناء بيانات النموذج
            # الأعمدة الأساسية
            columns = ['Seq', 'Student No', 'Student Name', 'Status']

            # إضافة أعمدة الأنشطة والمخرجات
            for activity in self.course.activities:
                # المخرجات لهذا النشاط (فقط التي قيمتها > 0)
                if hasattr(activity, 'measures_clos') and activity.measures_clos:
                    for clo in self.course.clos:
                        if clo.code in activity.measures_clos:
                            max_mark = self.max_marks.get(activity.name, {}).get(clo.code, 0)
                            if max_mark > 0:
                                # عمود بصيغة: Activity_CLO (مثل: Mid Exam_K1)
                                columns.append(f"{activity.name}_{clo.code}")

            # بيانات الطلاب
            data = []
            for student in sorted(self.section.students, key=lambda s: s.seq):
                row = {
                    'Seq': student.seq,
                    'Student No': student.student_id,
                    'Student Name': student.name,
                    'Status': student.status.value if hasattr(student.status, 'value') else student.status
                }

                # إضافة أعمدة فارغة للدرجات
                for col in columns[4:]:  # تخطي الأعمدة الأساسية
                    row[col] = ""

                data.append(row)

            # إنشاء DataFrame
            df = pd.DataFrame(data, columns=columns)

            # حفظ الملف
            file_path = filedialog.asksaveasfilename(
                title="حفظ نموذج Excel" if self.language == 'ar' else "Save Excel Template",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"grades_template_{self.section.section_number}.xlsx",
                parent=self
            )

            if file_path:
                # إنشاء Excel writer مع تنسيق
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Grades')

                    # الحصول على workbook و worksheet
                    workbook = writer.book
                    worksheet = writer.sheets['Grades']

                    # تنسيق العناوين
                    from openpyxl.styles import Font, PatternFill, Alignment

                    header_fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
                    header_font = Font(bold=True, color="FFFFFF")
                    center_aligned = Alignment(horizontal="center", vertical="center")

                    for cell in worksheet[1]:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = center_aligned

                    # ضبط عرض الأعمدة
                    worksheet.column_dimensions['A'].width = 8  # Seq
                    worksheet.column_dimensions['B'].width = 15  # Student No
                    worksheet.column_dimensions['C'].width = 40  # Name
                    worksheet.column_dimensions['D'].width = 12  # Status

                    # أعمدة الدرجات
                    for i in range(4, len(columns)):
                        worksheet.column_dimensions[self._get_excel_column_name(i)].width = 12

                messagebox.showinfo(
                    t('success', self.language),
                    f"تم حفظ النموذج بنجاح:\n{file_path}" if self.language == 'ar'
                    else f"Template saved successfully:\n{file_path}",
                    parent=self
                )

        except ImportError:
            messagebox.showerror(
                t('error', self.language),
                "مكتبة pandas أو openpyxl غير مثبتة.\n\nالرجاء تثبيتها باستخدام: pip install pandas openpyxl"
                if self.language == 'ar' else
                "pandas or openpyxl library is not installed.\n\nPlease install using: pip install pandas openpyxl",
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                t('error', self.language),
                f"فشل حفظ النموذج:\n{str(e)}" if self.language == 'ar'
                else f"Failed to save template:\n{str(e)}",
                parent=self
            )
