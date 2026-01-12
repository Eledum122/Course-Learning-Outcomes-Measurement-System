"""
حوار توليد ملف Excel للدرجات
Generate Grades Excel Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import tempfile
import shutil
from typing import Optional

from models import Course, CourseSection
from models.user import User
from managers.course_manager import CourseManager
from managers.section_manager import SectionManager
from managers.access_control import AccessControl
from reports.grades_excel_exporter import GradesExcelExporter
from config import FONTS
from translations import t


class GenerateGradesExcelDialog(tk.Toplevel):
    """حوار توليد ملف Excel للدرجات"""

    def __init__(self, parent, language: str = 'ar', user: User = None, access_control: AccessControl = None):
        super().__init__(parent)

        self.language = language
        self.user = user
        self.access_control = access_control
        self.course: Optional[Course] = None
        self.section: Optional[CourseSection] = None

        # إعداد النافذة
        self.title("توليد ملف Excel للدرجات" if language == 'ar'
                  else "Generate Grades Excel File")
        self.geometry("600x450")
        self.resizable(False, False)

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # إنشاء الواجهة
        self._create_ui()

        # تحميل المقررات
        self._load_courses()

    def _create_ui(self):
        """إنشاء واجهة المستخدم"""
        # الإطار الرئيسي
        main_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # العنوان
        title_text = "توليد ملف Excel للدرجات" if self.language == 'ar' \
            else "Generate Grades Excel File"
        tk.Label(
            main_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='white',
            fg='#1976D2'
        ).pack(pady=(0, 20))

        # تعليمات
        instructions = "اختر المقرر والشعبة لتوليد ملف Excel يحتوي على جدول درجات الطلاب في جميع الأنشطة" if self.language == 'ar' \
            else "Select course and section to generate Excel file with student grades table"
        tk.Label(
            main_frame,
            text=instructions,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            fg='#666',
            wraplength=500,
            justify='right' if self.language == 'ar' else 'left'
        ).pack(pady=(0, 20))

        # إطار اختيار المقرر
        course_frame = tk.LabelFrame(
            main_frame,
            text="اختر المقرر" if self.language == 'ar' else "Select Course",
            font=FONTS['arabic_bold'] if self.language == 'ar' else FONTS['bold'],
            bg='white',
            padx=15,
            pady=15
        )
        course_frame.pack(fill=tk.X, pady=(0, 15))

        # قائمة المقررات
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(
            course_frame,
            textvariable=self.course_var,
            state='readonly',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=50
        )
        self.course_combo.pack(fill=tk.X)
        self.course_combo.bind('<<ComboboxSelected>>', self._on_course_selected)

        # إطار اختيار الشعبة
        section_frame = tk.LabelFrame(
            main_frame,
            text="اختر الشعبة" if self.language == 'ar' else "Select Section",
            font=FONTS['arabic_bold'] if self.language == 'ar' else FONTS['bold'],
            bg='white',
            padx=15,
            pady=15
        )
        section_frame.pack(fill=tk.X, pady=(0, 15))

        # قائمة الشعب
        self.section_var = tk.StringVar()
        self.section_combo = ttk.Combobox(
            section_frame,
            textvariable=self.section_var,
            state='readonly',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=50
        )
        self.section_combo.pack(fill=tk.X)

        # أزرار
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        # زر المعاينة والتحميل
        preview_text = "📊 معاينة وتحميل Excel" if self.language == 'ar' else "📊 Preview & Download Excel"
        tk.Button(
            buttons_frame,
            text=preview_text,
            command=self._preview_and_download_excel,
            font=FONTS['arabic_bold'] if self.language == 'ar' else FONTS['bold'],
            bg='#2E7D32',
            fg='white',
            width=25,
            height=2,
            relief=tk.RAISED,
            borderwidth=2,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر الإلغاء
        cancel_text = "✖ إلغاء" if self.language == 'ar' else "✖ Cancel"
        tk.Button(
            buttons_frame,
            text=cancel_text,
            command=self.destroy,
            font=FONTS['arabic_bold'] if self.language == 'ar' else FONTS['bold'],
            bg='#757575',
            fg='white',
            width=20,
            height=2,
            relief=tk.RAISED,
            borderwidth=2,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

    def _load_courses(self):
        """تحميل قائمة المقررات"""
        cm = CourseManager()
        courses = cm.list_all_courses()

        # الحصول على أسماء البرامج المسموحة لمنسق البرنامج
        allowed_program_names = []
        allowed_course_ids = []
        if self.user and self.access_control:
            allowed_program_names = self.access_control.get_program_names_for_user(self.user)
            allowed_course_ids = self.access_control.get_allowed_course_ids_for_user(self.user)

        course_list = []
        self.courses_dict = {}

        for course_info in courses:
            course_id = course_info['course_id']

            # تصفية حسب معرفات المقررات (منسق مقرر أو مدرس شعبة)
            if allowed_course_ids:
                if course_id not in allowed_course_ids:
                    continue  # تجاوز هذا المقرر

            course = cm.load_course(course_id)
            if course:
                # تصفية المقررات حسب البرنامج الأكاديمي (منسق برنامج)
                if allowed_program_names:
                    course_program = getattr(course.info, 'program', None)
                    if course_program not in allowed_program_names:
                        continue

                display_name = f"{course.info.course_code} - {course.info.course_title}"
                course_list.append(display_name)
                self.courses_dict[display_name] = course

        self.course_combo['values'] = course_list

    def _on_course_selected(self, event=None):
        """عند اختيار مقرر"""
        course_name = self.course_var.get()
        if not course_name:
            return

        self.course = self.courses_dict.get(course_name)
        if not self.course:
            return

        # تحميل الشعب
        self._load_sections()

    def _load_sections(self):
        """تحميل شعب المقرر المختار"""
        self.section_combo.set('')
        self.sections_dict = {}

        if not self.course:
            self.section_combo['values'] = []
            return

        sm = SectionManager()
        sections = sm.get_sections_by_course(self.course.course_id)

        section_list = []
        for section in sections:
            # التحقق من وجود طلاب
            if section.students and len(section.students) > 0:
                display_name = f"الشعبة {section.section_number} - {section.academic_year} - {section.semester.value}" \
                    if self.language == 'ar' else \
                    f"Section {section.section_number} - {section.academic_year} - {section.semester.value}"

                section_list.append(display_name)
                self.sections_dict[display_name] = section

        self.section_combo['values'] = section_list

    def _preview_and_download_excel(self):
        """معاينة وتحميل ملف Excel"""
        # التحقق من اختيار المقرر
        if not self.course:
            messagebox.showerror(
                "خطأ" if self.language == 'ar' else "Error",
                "يجب اختيار المقرر" if self.language == 'ar' else "Please select a course",
                parent=self
            )
            return

        # التحقق من اختيار الشعبة
        section_name = self.section_var.get()
        if not section_name:
            messagebox.showerror(
                "خطأ" if self.language == 'ar' else "Error",
                "يجب اختيار الشعبة" if self.language == 'ar' else "Please select a section",
                parent=self
            )
            return

        self.section = self.sections_dict.get(section_name)
        if not self.section:
            return

        try:
            # توليد ملف Excel في ملف مؤقت للمعاينة
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            temp_path = temp_file.name
            temp_file.close()

            # توليد ملف Excel
            exporter = GradesExcelExporter(self.course, self.section, self.language)
            exporter.generate_excel(temp_path)

            # فتح الملف للمعاينة
            os.startfile(temp_path)

            # عرض نافذة حوار للتحميل
            if messagebox.askyesno(
                "معاينة ملف Excel" if self.language == 'ar' else "Preview Excel File",
                "تم فتح ملف Excel للمعاينة.\n\nهل تريد حفظ نسخة من الملف؟" if self.language == 'ar' else
                "The Excel file has been opened for preview.\n\nDo you want to save a copy of the file?",
                parent=self
            ):
                # اختيار مكان حفظ الملف
                default_filename = f"{self.course.info.course_code}_{self.section.section_number}_grades.xlsx"
                file_path = filedialog.asksaveasfilename(
                    parent=self,
                    title="حفظ ملف Excel" if self.language == 'ar' else "Save Excel File",
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx")],
                    initialfile=default_filename
                )

                if file_path:
                    # نسخ الملف المؤقت إلى الموقع المحدد
                    shutil.copy2(temp_path, file_path)

                    messagebox.showinfo(
                        "تم الحفظ" if self.language == 'ar' else "Saved",
                        f"تم حفظ الملف في:\n{file_path}" if self.language == 'ar' else
                        f"File saved to:\n{file_path}",
                        parent=self
                    )

            # حذف الملف المؤقت بعد فترة
            self.after(5000, lambda: self._cleanup_temp_file(temp_path))

        except Exception as e:
            messagebox.showerror(
                "خطأ" if self.language == 'ar' else "Error",
                f"فشل توليد ملف Excel:\n{str(e)}" if self.language == 'ar' else f"Failed to generate Excel file:\n{str(e)}",
                parent=self
            )

    def _cleanup_temp_file(self, file_path):
        """حذف الملف المؤقت"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass  # تجاهل الأخطاء في حذف الملفات المؤقتة
