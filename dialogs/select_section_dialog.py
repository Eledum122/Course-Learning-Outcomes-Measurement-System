"""
حوار اختيار الشعبة للتعديل
Select Section Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from models import Course, CourseSection
from managers.section_manager import SectionManager
from config import FONTS
from translations import t


class SelectSectionDialog(tk.Toplevel):
    """حوار اختيار شعبة من الشعب الموجودة"""

    def __init__(self, parent, course: Course, language: str = 'ar', user=None):
        super().__init__(parent)

        self.course = course
        self.language = language
        self.selected_section = None
        self.user = user  # معلومات المستخدم لتطبيق الصلاحيات

        # إعداد النافذة
        self.title("اختيار الشعبة" if language == 'ar' else "Select Section")
        self.geometry("1000x650")
        self.resizable(True, True)

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # إنشاء الواجهة
        self._create_widgets()

        # مركزة النافذة
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # الإطار الرئيسي
        main_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # العنوان
        title_text = f"شعب المقرر: {self.course.info.course_code}" if self.language == 'ar' else f"Course Sections: {self.course.info.course_code}"
        tk.Label(
            main_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='white',
            fg='#1976D2'
        ).pack(pady=(0, 20))

        # معلومات
        info_text = "اختر شعبة للتعديل عليها أو أنشئ شعبة جديدة" if self.language == 'ar' else "Select a section to edit or create a new one"
        tk.Label(
            main_frame,
            text=info_text,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            fg='#666'
        ).pack(pady=(0, 15))

        # إطار الجدول
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # شريط التمرير
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الجدول
        columns = ('section_number', 'academic_year', 'semester', 'coordinator', 'instructor', 'students', 'status')

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )
        scrollbar.config(command=self.tree.yview)

        # تعريف الأعمدة
        if self.language == 'ar':
            headers = {
                'section_number': 'رقم الشعبة',
                'academic_year': 'السنة الدراسية',
                'semester': 'الفصل الدراسي',
                'coordinator': 'المنسق',
                'instructor': 'المدرس',
                'students': 'عدد الطلاب',
                'status': 'الحالة'
            }
        else:
            headers = {
                'section_number': 'Section #',
                'academic_year': 'Academic Year',
                'semester': 'Semester',
                'coordinator': 'Coordinator',
                'instructor': 'Instructor',
                'students': 'Students',
                'status': 'Status'
            }

        # تعيين عناوين الأعمدة وعرضها
        widths = {
            'section_number': 100,
            'academic_year': 120,
            'semester': 100,
            'coordinator': 150,
            'instructor': 150,
            'students': 80,
            'status': 100
        }

        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor='center')

        self.tree.pack(fill=tk.BOTH, expand=True)

        # تحميل البيانات
        self._load_sections()

        # ربط حدث النقر المزدوج
        self.tree.bind('<Double-1>', self._on_double_click)

        # الأزرار - صفين لوضوح أفضل
        buttons_container = tk.Frame(main_frame, bg='white')
        buttons_container.pack(pady=(15, 10))

        # التحقق من صلاحيات المستخدم
        is_section_instructor = (self.user and
                                not self.user.has_role('admin') and
                                not self.user.has_role('program_coordinator') and
                                not self.user.has_role('course_coordinator'))

        # التحقق من صلاحية منسق البرنامج أو منسق المقرر
        is_coordinator = (self.user and
                         (self.user.has_role('program_coordinator') or
                          self.user.has_role('course_coordinator')))

        # الصف الأول - الأزرار الرئيسية (للمنسقين والمدير فقط)
        if not is_section_instructor:
            buttons_row1 = tk.Frame(buttons_container, bg='white')
            buttons_row1.pack(pady=(0, 10))

            # زر شعبة جديدة
            new_text = "➕ شعبة جديدة" if self.language == 'ar' else "➕ New Section"
            tk.Button(
                buttons_row1,
                text=new_text,
                command=self._new_section,
                bg='#2196F3',
                fg='white',
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                width=18,
                height=2,
                cursor='hand2',
                relief=tk.RAISED,
                borderwidth=2
            ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=8)

            # زر تعديل
            edit_text = "✏ تعديل بيانات الشعبة" if self.language == 'ar' else "✏ Edit Section Info"
            tk.Button(
                buttons_row1,
                text=edit_text,
                command=self._edit_section,
                bg='#4CAF50',
                fg='white',
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                width=20,
                height=2,
                cursor='hand2',
                relief=tk.RAISED,
                borderwidth=2
            ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=8)

            # زر حذف
            delete_text = "🗑 حذف" if self.language == 'ar' else "🗑 Delete"
            tk.Button(
                buttons_row1,
                text=delete_text,
                command=self._delete_section,
                bg='#F44336',
                fg='white',
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                width=18,
                height=2,
                cursor='hand2',
                relief=tk.RAISED,
                borderwidth=2
            ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=8)

        # الصف الثاني - أزرار البيانات (مدرس الشعبة فقط - ليس للمنسقين)
        if not is_coordinator and is_section_instructor:
            buttons_row2 = tk.Frame(buttons_container, bg='white')
            buttons_row2.pack()

            # زر إدخال الطلاب
            students_text = "👥 إدخال الطلاب" if self.language == 'ar' else "👥 Enter Students"
            tk.Button(
                buttons_row2,
                text=students_text,
                command=self._enter_students,
                bg='#FF9800',
                fg='white',
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                width=20,
                height=2,
                cursor='hand2',
                relief=tk.RAISED,
                borderwidth=2
            ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=8)

            # زر إدخال الدرجات
            grades_text = "📊 إدخال الدرجات" if self.language == 'ar' else "📊 Enter Grades"
            tk.Button(
                buttons_row2,
                text=grades_text,
                command=self._enter_grades,
                bg='#00BCD4',
                fg='white',
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                width=20,
                height=2,
                cursor='hand2',
                relief=tk.RAISED,
                borderwidth=2
            ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=8)

        # زر إغلاق - متاح للجميع
        buttons_row_close = tk.Frame(buttons_container, bg='white')
        buttons_row_close.pack(pady=(10, 0))

        close_text = "✖ إغلاق" if self.language == 'ar' else "✖ Close"
        tk.Button(
            buttons_row_close,
            text=close_text,
            command=self.destroy,
            bg='#757575',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=18,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=2
        ).pack(padx=8)

    def _load_sections(self):
        """تحميل الشعب من قاعدة البيانات"""
        sm = SectionManager()
        sections = sm.get_sections_by_course(self.course.course_id)

        # تصفية الشعب حسب صلاحيات المستخدم
        if self.user:
            # إذا كان مدرس شعبة فقط، عرض الشعب التي يدرسها فقط
            if (not self.user.has_role('admin') and
                not self.user.has_role('program_coordinator') and
                not self.user.has_role('course_coordinator')):
                # تصفية الشعب المسندة للمستخدم
                if hasattr(self.user, 'assigned_sections') and self.course.course_id in self.user.assigned_sections:
                    assigned_section_numbers = self.user.assigned_sections[self.course.course_id]
                    sections = [s for s in sections if s.section_number in assigned_section_numbers]
                else:
                    sections = []  # لا توجد شعب مسندة

        # مسح البيانات الحالية
        for item in self.tree.get_children():
            self.tree.delete(item)

        # إضافة الشعب
        for section in sections:
            # تحديد حالة الإكمال
            if section.grades_data_completed:
                status = "مكتمل" if self.language == 'ar' else "Completed"
            elif section.students_data_completed:
                status = "طلاب" if self.language == 'ar' else "Students"
            elif section.section_data_completed:
                status = "شعبة" if self.language == 'ar' else "Section"
            else:
                status = "جديد" if self.language == 'ar' else "New"

            semester_value = section.semester.value if hasattr(section.semester, 'value') else section.semester

            # ترجمة الفصل الدراسي
            semester_display = {
                'First': 'الأول' if self.language == 'ar' else 'First',
                'Second': 'الثاني' if self.language == 'ar' else 'Second',
                'Summer': 'الصيفي' if self.language == 'ar' else 'Summer'
            }.get(semester_value, semester_value)

            self.tree.insert('', 'end', values=(
                section.section_number,
                section.academic_year,
                semester_display,
                section.course_coordinator,
                section.section_instructor,
                len(section.students),
                status
            ), tags=(section.section_id,))

        # عرض رسالة إذا لم توجد شعب
        if not sections:
            no_data_text = "لا توجد شعب لهذا المقرر" if self.language == 'ar' else "No sections found for this course"
            self.tree.insert('', 'end', values=(no_data_text, '', '', '', '', '', ''))

    def _on_double_click(self, event):
        """معالجة النقر المزدوج - فتح الشعبة للتعديل"""
        self._edit_section()

    def _new_section(self):
        """إنشاء شعبة جديدة"""
        # التحقق من وجود بيانات فصل دراسي (منسق ومدرسين)
        # نعرض رسالة تنبيه إذا لم تكن هناك بيانات
        has_semester_data = False
        if hasattr(self.course, 'semester_data') and self.course.semester_data:
            for semester_key, semester_data in self.course.semester_data.items():
                if semester_data.course_coordinator and semester_data.instructors:
                    has_semester_data = True
                    break

        if not has_semester_data:
            messagebox.showwarning(
                "تحذير" if self.language == 'ar' else "Warning",
                "يجب إدخال بيانات الفصل الدراسي أولاً (منسق المقرر ومدرسي المقرر) من خلال:\n\n"
                "الإدارة ← إدارة بيانات الفصل الدراسي\n\n"
                "قم بإدخال السنة الدراسية والفصل، ثم حدد المنسق والمدرسين، واحفظ البيانات."
                if self.language == 'ar' else
                "You must enter semester data first (course coordinator and instructors) through:\n\n"
                "Management → Semester Management\n\n"
                "Enter the academic year and semester, then select coordinator and instructors, and save the data.",
                parent=self
            )
            return

        from dialogs.stage3_section_info_dialog import Stage3SectionInfoDialog

        dlg = Stage3SectionInfoDialog(self, self.course, language=self.language)
        self.wait_window(dlg)

        # تحديث القائمة
        self._load_sections()

    def _edit_section(self):
        """تعديل الشعبة المحددة"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار شعبة للتعديل" if self.language == 'ar' else "Please select a section to edit",
                parent=self
            )
            return

        # الحصول على معرف الشعبة
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if not tags:
            return

        section_id = tags[0]

        # تحميل الشعبة
        sm = SectionManager()
        section = sm.load_section(section_id)

        if not section:
            messagebox.showerror(
                t('error', self.language),
                "فشل تحميل بيانات الشعبة" if self.language == 'ar' else "Failed to load section data",
                parent=self
            )
            return

        # فتح نافذة التعديل
        from dialogs.stage3_section_info_dialog import Stage3SectionInfoDialog

        dlg = Stage3SectionInfoDialog(self, self.course, language=self.language, section=section)
        self.wait_window(dlg)

        # تحديث القائمة
        self._load_sections()

    def _delete_section(self):
        """حذف الشعبة المحددة"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار شعبة للحذف" if self.language == 'ar' else "Please select a section to delete",
                parent=self
            )
            return

        # تأكيد الحذف
        confirm = messagebox.askyesno(
            t('confirm', self.language),
            "هل أنت متأكد من حذف هذه الشعبة؟\n\nسيتم حذف جميع البيانات المرتبطة بها!"
            if self.language == 'ar' else
            "Are you sure you want to delete this section?\n\nAll associated data will be deleted!",
            parent=self
        )

        if not confirm:
            return

        # الحصول على معرف الشعبة
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if not tags:
            return

        section_id = tags[0]

        # حذف الشعبة
        sm = SectionManager()
        if sm.delete_section(section_id):
            messagebox.showinfo(
                t('success', self.language),
                "تم حذف الشعبة بنجاح" if self.language == 'ar' else "Section deleted successfully",
                parent=self
            )
            # تحديث القائمة
            self._load_sections()
        else:
            messagebox.showerror(
                t('error', self.language),
                "فشل حذف الشعبة" if self.language == 'ar' else "Failed to delete section",
                parent=self
            )

    def _enter_students(self):
        """إدخال بيانات الطلاب للشعبة المحددة"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار شعبة لإدخال الطلاب" if self.language == 'ar' else "Please select a section to enter students",
                parent=self
            )
            return

        # الحصول على معرف الشعبة
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if not tags:
            return

        section_id = tags[0]

        # تحميل الشعبة
        sm = SectionManager()
        section = sm.load_section(section_id)

        if not section:
            messagebox.showerror(
                t('error', self.language),
                "فشل تحميل بيانات الشعبة" if self.language == 'ar' else "Failed to load section data",
                parent=self
            )
            return

        # التحقق من اكتمال بيانات الشعبة
        if not section.section_data_completed:
            messagebox.showwarning(
                t('warning', self.language),
                "يجب إكمال بيانات الشعبة أولاً" if self.language == 'ar' else "Please complete section data first",
                parent=self
            )
            return

        # فتح نافذة إدخال الطلاب
        from dialogs.stage3_students_data_dialog import Stage3StudentsDataDialog

        dlg = Stage3StudentsDataDialog(self, section, language=self.language)
        self.wait_window(dlg)

        # تحديث القائمة
        self._load_sections()

    def _enter_grades(self):
        """إدخال درجات الطلاب للشعبة المحددة"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار شعبة لإدخال الدرجات" if self.language == 'ar' else "Please select a section to enter grades",
                parent=self
            )
            return

        # الحصول على معرف الشعبة
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        if not tags:
            return

        section_id = tags[0]

        # تحميل الشعبة
        sm = SectionManager()
        section = sm.load_section(section_id)

        if not section:
            messagebox.showerror(
                t('error', self.language),
                "فشل تحميل بيانات الشعبة" if self.language == 'ar' else "Failed to load section data",
                parent=self
            )
            return

        # التحقق من اكتمال بيانات الطلاب
        if not section.students_data_completed:
            messagebox.showwarning(
                t('warning', self.language),
                "يجب إدخال بيانات الطلاب أولاً" if self.language == 'ar' else "Please enter students data first",
                parent=self
            )
            return

        if not section.students:
            messagebox.showwarning(
                t('warning', self.language),
                "لا يوجد طلاب في هذه الشعبة" if self.language == 'ar' else "No students in this section",
                parent=self
            )
            return

        # فتح نافذة إدخال الدرجات
        from dialogs.stage3_grades_entry_dialog import Stage3GradesEntryDialog

        dlg = Stage3GradesEntryDialog(self, section, language=self.language)
        self.wait_window(dlg)

        # تحديث القائمة
        self._load_sections()
