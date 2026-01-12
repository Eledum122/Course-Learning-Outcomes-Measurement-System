"""
حوار توليد تقرير قياس مخرجات التعلم
Generate CLO Assessment Report Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Optional

from models import Course, CourseSection
from models.user import User
from managers.course_manager import CourseManager
from managers.section_manager import SectionManager
from managers.access_control import AccessControl
from reports.clo_assessment_report_generator import CLOAssessmentReportGenerator
from config import FONTS
from translations import t


class GenerateCLOReportDialog(tk.Toplevel):
    """حوار توليد تقرير قياس مخرجات التعلم"""

    def __init__(self, parent, language: str = 'ar', user: User = None, access_control: AccessControl = None):
        super().__init__(parent)

        self.language = language
        self.user = user
        self.access_control = access_control
        self.course: Optional[Course] = None
        self.section: Optional[CourseSection] = None

        # إعداد النافذة
        self.title("توليد تقرير قياس مخرجات التعلم" if language == 'ar'
                  else "Generate CLO Assessment Report")
        self.geometry("600x500")
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
        title_text = "توليد تقرير قياس مخرجات التعلم" if self.language == 'ar' \
            else "Generate CLO Assessment Report"
        tk.Label(
            main_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='white',
            fg='#1976D2'
        ).pack(pady=(0, 20))

        # تعليمات
        instructions = "اختر المقرر والشعبة لتوليد تقرير قياس مخرجات التعلم" if self.language == 'ar' \
            else "Select course and section to generate CLO assessment report"
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
        self.section_combo.bind('<<ComboboxSelected>>', self._on_section_selected)

        # معلومات الشعبة المحددة
        self.info_label = tk.Label(
            main_frame,
            text="",
            font=FONTS['arabic_small'] if self.language == 'ar' else FONTS['english_small'],
            bg='white',
            fg='#666',
            justify='right' if self.language == 'ar' else 'left'
        )
        self.info_label.pack(pady=(0, 20))

        # إطار الأزرار
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(fill=tk.X)

        # زر توليد التقرير
        generate_text = "توليد التقرير" if self.language == 'ar' else "Generate Report"
        tk.Button(
            buttons_frame,
            text=generate_text,
            command=self._generate_report,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=18,
            cursor='hand2',
            pady=10
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر إلغاء
        cancel_text = "إلغاء" if self.language == 'ar' else "Cancel"
        tk.Button(
            buttons_frame,
            text=cancel_text,
            command=self.destroy,
            bg='#F44336',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=12,
            cursor='hand2',
            pady=10
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

    def _load_courses(self):
        """تحميل قائمة المقررات"""
        cm = CourseManager()
        courses_data = cm.list_all_courses()
        courses = [c['course_id'] for c in courses_data]

        # الحصول على أسماء البرامج المسموحة لمنسق البرنامج
        allowed_program_names = []
        allowed_course_ids = []
        if self.user and self.access_control:
            allowed_program_names = self.access_control.get_program_names_for_user(self.user)
            allowed_course_ids = self.access_control.get_allowed_course_ids_for_user(self.user)

        # إعداد قائمة المقررات
        course_list = []
        self.courses_dict = {}

        for course_id in courses:
            course = cm.load_course(course_id)
            if course:
                # تصفية حسب معرفات المقررات (منسق مقرر أو مدرس شعبة)
                if allowed_course_ids:
                    if course_id not in allowed_course_ids:
                        continue  # تجاوز هذا المقرر

                # تصفية المقررات حسب البرنامج الأكاديمي (منسق برنامج)
                if allowed_program_names:
                    course_program = getattr(course.info, 'program', None)
                    if course_program not in allowed_program_names:
                        continue  # تجاوز هذا المقرر

                display_name = f"{course.info.course_code} - {course.info.course_title}"
                course_list.append(display_name)
                self.courses_dict[display_name] = course

        self.course_combo['values'] = course_list

    def _on_course_selected(self, event=None):
        """عند اختيار مقرر"""
        selected = self.course_var.get()
        if selected in self.courses_dict:
            self.course = self.courses_dict[selected]
            self._load_sections()
        else:
            self.course = None
            self.section_combo['values'] = []
            self.section = None
            self.info_label.config(text="")

    def _load_sections(self):
        """تحميل شعب المقرر المحدد"""
        if not self.course:
            return

        sm = SectionManager()
        sections = sm.get_sections_by_course(self.course.course_id)

        # إعداد قائمة الشعب
        section_list = []
        self.sections_dict = {}

        for section in sections:
            display_name = f"{section.section_number} - {section.academic_year} - {section.semester.value if hasattr(section.semester, 'value') else section.semester}"
            section_list.append(display_name)
            self.sections_dict[display_name] = section

        self.section_combo['values'] = section_list

        if not section_list:
            messagebox.showinfo(
                t('info', self.language),
                "لا توجد شعب لهذا المقرر" if self.language == 'ar' else "No sections found for this course",
                parent=self
            )

    def _on_section_selected(self, event=None):
        """عند اختيار شعبة"""
        selected = self.section_var.get()
        if selected in self.sections_dict:
            self.section = self.sections_dict[selected]
            self._update_section_info()
        else:
            self.section = None
            self.info_label.config(text="")

    def _update_section_info(self):
        """تحديث معلومات الشعبة المحددة"""
        if not self.section:
            return

        # التحقق من اكتمال البيانات
        if not self.section.grades_data_completed:
            info_text = "⚠ لم يتم إكمال إدخال درجات الطلاب لهذه الشعبة" if self.language == 'ar' \
                else "⚠ Grades data not completed for this section"
            self.info_label.config(text=info_text, fg='#F44336')
        else:
            total_students = len(self.section.students)
            regular_students = len([s for s in self.section.students if s.status.value == "Regular"])

            info_text = f"عدد الطلاب: {total_students} (منتظم: {regular_students})" if self.language == 'ar' \
                else f"Students: {total_students} (Regular: {regular_students})"

            self.info_label.config(text=info_text, fg='#4CAF50')

    def _generate_report(self):
        """توليد التقرير"""
        # التحقق من اختيار المقرر والشعبة
        if not self.course:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار مقرر" if self.language == 'ar' else "Please select a course",
                parent=self
            )
            return

        if not self.section:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار شعبة" if self.language == 'ar' else "Please select a section",
                parent=self
            )
            return

        # التحقق من اكتمال البيانات
        if not self.section.grades_data_completed:
            messagebox.showerror(
                t('error', self.language),
                "يجب إكمال إدخال درجات الطلاب قبل توليد التقرير" if self.language == 'ar'
                else "Grades data must be completed before generating report",
                parent=self
            )
            return

        try:
            # إنشاء ملف مؤقت للمعاينة في مجلد المستخدم
            import tempfile
            # استخدام مجلد المستندات بدلاً من temp
            user_home = os.path.expanduser("~")
            temp_dir = os.path.join(user_home, "Documents")

            # التأكد من وجود المجلد
            if not os.path.exists(temp_dir):
                temp_dir = user_home

            temp_filename = f"CLO_Assessment_Preview_{self.course.info.course_code}_{self.section.section_number}.pdf"
            temp_path = os.path.join(temp_dir, temp_filename)

            # توليد التقرير في الملف المؤقت
            generator = CLOAssessmentReportGenerator(
                course=self.course,
                section=self.section,
                language=self.language
            )

            generator.generate_report(temp_path)

            # فتح الملف المؤقت للمعاينة
            os.startfile(temp_path)

            # سؤال المستخدم عن حفظ التقرير
            save_dialog = messagebox.askyesno(
                t('info', self.language),
                "تم فتح التقرير للمعاينة.\nهل تريد حفظ التقرير؟" if self.language == 'ar'
                else "Report preview has been opened.\nDo you want to save the report?",
                parent=self
            )

            if save_dialog:
                # اختيار مسار حفظ الملف
                default_filename = f"CLO_Assessment_{self.course.info.course_code}_{self.section.section_number}_{self.section.academic_year}.pdf"

                file_path = filedialog.asksaveasfilename(
                    title="حفظ التقرير" if self.language == 'ar' else "Save Report",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=default_filename,
                    parent=self
                )

                if file_path:
                    # نسخ الملف المؤقت إلى المسار المحدد
                    import shutil
                    shutil.copy2(temp_path, file_path)

                    messagebox.showinfo(
                        t('success', self.language),
                        f"تم حفظ التقرير بنجاح:\n{file_path}" if self.language == 'ar'
                        else f"Report saved successfully:\n{file_path}",
                        parent=self
                    )

        except Exception as e:
            messagebox.showerror(
                t('error', self.language),
                f"فشل توليد التقرير:\n{str(e)}" if self.language == 'ar'
                else f"Failed to generate report:\n{str(e)}",
                parent=self
            )
