"""
نافذة توليد تقرير لوحة البيانات
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime

from models.user import User
from managers.course_manager import CourseManager
from managers.section_manager import SectionManager
from managers.access_control import AccessControl
from reports.dashboard_report_generator import DashboardReportGenerator
from translations import t, get_language
from config import FONTS


class GenerateDashboardDialog(tk.Toplevel):
    """نافذة توليد تقرير لوحة البيانات"""

    def __init__(self, parent, language='ar', user: User = None, access_control: AccessControl = None):
        super().__init__(parent)

        self.language = language
        self.user = user
        self.access_control = access_control
        self.course = None
        self.section = None

        self.title("Dashboard Report" if language == 'en' else "تقرير لوحة البيانات")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()

        # تكوين الخطوط
        self.font_main = FONTS['arabic_main'] if language == 'ar' else FONTS['english_main']
        self.font_heading = FONTS['arabic_header'] if language == 'ar' else FONTS['english_header']

        self._create_widgets()
        self._load_courses()

        # توسيط النافذة
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # إطار رئيسي
        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # العنوان
        title_text = "Generate Dashboard Report" if self.language == 'en' else "توليد تقرير لوحة البيانات"
        title_label = tk.Label(
            main_frame,
            text=title_text,
            font=self.font_heading,
            bg='white',
            fg='#1976D2'
        )
        title_label.pack(pady=(0, 20))

        # وصف التقرير
        desc_text = ("This report includes statistical metrics, KPIs, and beautiful charts\n"
                    "for student results and course learning outcomes.") if self.language == 'en' else \
                   ("يتضمن هذا التقرير مقاييس إحصائية ومؤشرات أداء رئيسية ورسومات بيانية جميلة\n"
                    "لنتائج الطلاب ونواتج تعلم المقرر.")

        desc_label = tk.Label(
            main_frame,
            text=desc_text,
            font=self.font_main,
            bg='white',
            fg='#555555',
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20))

        # إطار اختيار المقرر
        course_frame = tk.LabelFrame(
            main_frame,
            text="Select Course" if self.language == 'en' else "اختر المقرر",
            font=self.font_main,
            bg='white',
            padx=10,
            pady=10
        )
        course_frame.pack(fill=tk.X, pady=(0, 15))

        self.course_combo = ttk.Combobox(
            course_frame,
            font=self.font_main,
            state='readonly',
            width=50
        )
        self.course_combo.pack(pady=5)
        self.course_combo.bind('<<ComboboxSelected>>', self._on_course_selected)

        # إطار اختيار الشعبة
        section_frame = tk.LabelFrame(
            main_frame,
            text="Select Section" if self.language == 'en' else "اختر الشعبة",
            font=self.font_main,
            bg='white',
            padx=10,
            pady=10
        )
        section_frame.pack(fill=tk.X, pady=(0, 20))

        self.section_combo = ttk.Combobox(
            section_frame,
            font=self.font_main,
            state='readonly',
            width=50
        )
        self.section_combo.pack(pady=5)

        # إطار الأزرار
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=20)

        # زر التوليد
        generate_text = "Generate Report" if self.language == 'en' else "توليد التقرير"
        generate_btn = tk.Button(
            button_frame,
            text=generate_text,
            command=self._generate_report,
            font=self.font_main,
            bg='#1976D2',
            fg='white',
            width=20,
            height=2,
            cursor='hand2'
        )
        generate_btn.pack(side=tk.LEFT, padx=10)

        # زر الإلغاء
        cancel_text = "Cancel" if self.language == 'en' else "إلغاء"
        cancel_btn = tk.Button(
            button_frame,
            text=cancel_text,
            command=self.destroy,
            font=self.font_main,
            bg='#757575',
            fg='white',
            width=20,
            height=2,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def _load_courses(self):
        """تحميل قائمة المقررات"""
        try:
            cm = CourseManager()
            courses_data = cm.list_all_courses()
            courses = [c['course_id'] for c in courses_data]

            if not courses:
                messagebox.showwarning(
                    t('warning', self.language),
                    "No courses found. Please create a course first." if self.language == 'en'
                    else "لا توجد مقررات. يرجى إنشاء مقرر أولاً.",
                    parent=self
                )
                return

            # الحصول على أسماء البرامج المسموحة لمنسق البرنامج
            allowed_program_names = []
            allowed_course_ids = []
            if self.user and self.access_control:
                allowed_program_names = self.access_control.get_program_names_for_user(self.user)
                allowed_course_ids = self.access_control.get_allowed_course_ids_for_user(self.user)

            self.courses_dict = {}
            for course_id in courses:
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
                    self.courses_dict[display_name] = course

            self.course_combo['values'] = list(self.courses_dict.keys())

            if len(self.courses_dict) > 0:
                self.course_combo.current(0)
                self._on_course_selected(None)

        except Exception as e:
            messagebox.showerror(
                t('error', self.language),
                f"Error loading courses: {str(e)}",
                parent=self
            )

    def _on_course_selected(self, event):
        """معالج حدث اختيار المقرر"""
        selected = self.course_combo.get()
        if not selected:
            return

        self.course = self.courses_dict[selected]

        # تحميل الشعب
        try:
            sm = SectionManager()
            sections = sm.get_sections_by_course(self.course.course_id)

            if not sections:
                messagebox.showwarning(
                    t('warning', self.language),
                    "No sections found for this course." if self.language == 'en'
                    else "لا توجد شعب لهذا المقرر.",
                    parent=self
                )
                self.section_combo['values'] = []
                return

            self.sections_dict = {}
            for section in sections:
                if section.grades_data_completed:
                    display_name = f"{section.section_number} - {section.academic_year} - {section.semester.value if hasattr(section.semester, 'value') else section.semester}"
                    self.sections_dict[display_name] = section

            if not self.sections_dict:
                messagebox.showwarning(
                    t('warning', self.language),
                    "No sections with completed grades found." if self.language == 'en'
                    else "لا توجد شعب مكتملة الدرجات.",
                    parent=self
                )
                self.section_combo['values'] = []
                return

            self.section_combo['values'] = list(self.sections_dict.keys())

            if len(self.sections_dict) > 0:
                self.section_combo.current(0)

        except Exception as e:
            messagebox.showerror(
                t('error', self.language),
                f"Error loading sections: {str(e)}",
                parent=self
            )

    def _generate_report(self):
        """توليد التقرير"""
        # التحقق من الاختيارات
        if not self.course_combo.get():
            messagebox.showwarning(
                t('warning', self.language),
                "Please select a course." if self.language == 'en' else "يرجى اختيار مقرر.",
                parent=self
            )
            return

        if not self.section_combo.get():
            messagebox.showwarning(
                t('warning', self.language),
                "Please select a section." if self.language == 'en' else "يرجى اختيار شعبة.",
                parent=self
            )
            return

        selected_section = self.section_combo.get()
        if not hasattr(self, 'sections_dict') or selected_section not in self.sections_dict:
            messagebox.showwarning(
                t('warning', self.language),
                "Invalid section selected." if self.language == 'en' else "الشعبة المحددة غير صالحة.",
                parent=self
            )
            return

        self.section = self.sections_dict[selected_section]

        # التحقق من وجود طلاب منتظمين
        regular_students = [s for s in self.section.students if s.status.value == "Regular"]
        if not regular_students:
            messagebox.showwarning(
                t('warning', self.language),
                "No regular students found in this section." if self.language == 'en'
                else "لا يوجد طلاب منتظمين في هذه الشعبة.",
                parent=self
            )
            return

        try:
            # إنشاء ملف مؤقت للمعاينة في مجلد المستخدم
            user_home = os.path.expanduser("~")
            temp_dir = os.path.join(user_home, "Documents")

            if not os.path.exists(temp_dir):
                temp_dir = user_home

            temp_filename = f"Dashboard_Report_{self.course.info.course_code}_{self.section.section_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            temp_path = os.path.join(temp_dir, temp_filename)

            # توليد التقرير في الملف المؤقت
            generator = DashboardReportGenerator(
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
                "The report has been opened for preview.\nWould you like to save the report?"
                if self.language == 'en' else
                "تم فتح التقرير للمعاينة.\nهل تريد حفظ التقرير؟",
                parent=self
            )

            if save_dialog:
                file_path = filedialog.asksaveasfilename(
                    title="Save Dashboard Report" if self.language == 'en' else "حفظ تقرير لوحة البيانات",
                    defaultextension=".pdf",
                    filetypes=[
                        ("PDF files", "*.pdf"),
                        ("All files", "*.*")
                    ],
                    initialfile=f"Dashboard_Report_{self.course.info.course_code}_{self.section.section_number}.pdf",
                    parent=self
                )

                if file_path:
                    import shutil
                    shutil.copy2(temp_path, file_path)
                    messagebox.showinfo(
                        t('success', self.language),
                        "Report saved successfully!" if self.language == 'en'
                        else "تم حفظ التقرير بنجاح!",
                        parent=self
                    )
                    self.destroy()

        except Exception as e:
            messagebox.showerror(
                t('error', self.language),
                f"Error generating report: {str(e)}",
                parent=self
            )
