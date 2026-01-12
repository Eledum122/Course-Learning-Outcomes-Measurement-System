"""
حوار توليد تقرير إنجاز الطلاب في المخرجات
Generate Students CLO Achievement Report Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Optional, List

from models import Course, CourseSection
from models.user import User
from managers.course_manager import CourseManager
from managers.section_manager import SectionManager
from managers.access_control import AccessControl
from reports.clo_students_achievement_report import CLOStudentsAchievementReport
from config import FONTS
from translations import t


class GenerateStudentsAchievementDialog(tk.Toplevel):
    """حوار توليد تقرير إنجاز الطلاب في المخرجات"""

    def __init__(self, parent, language: str = 'ar', user: User = None, access_control: AccessControl = None):
        super().__init__(parent)

        self.language = language
        self.user = user
        self.access_control = access_control
        self.course: Optional[Course] = None
        self.selected_sections: List[CourseSection] = []

        # إعداد النافذة
        self.title("توليد تقرير إنجاز الطلاب في المخرجات" if language == 'ar'
                  else "Generate Students CLO Achievement Report")
        self.geometry("700x600")
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
        title_text = "توليد تقرير إنجاز الطلاب في المخرجات" if self.language == 'ar' \
            else "Generate Students CLO Achievement Report"
        tk.Label(
            main_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='white',
            fg='#1976D2'
        ).pack(pady=(0, 20))

        # تعليمات
        instructions = "اختر المقرر والشعب لتوليد تقرير تفصيلي بإنجاز الطلاب في كل مخرج" if self.language == 'ar' \
            else "Select course and sections to generate detailed student achievement report"
        tk.Label(
            main_frame,
            text=instructions,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            fg='#666',
            wraplength=600,
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
            width=60
        )
        self.course_combo.pack(fill=tk.X)
        self.course_combo.bind('<<ComboboxSelected>>', self._on_course_selected)

        # إطار اختيار الشعب
        sections_frame = tk.LabelFrame(
            main_frame,
            text="اختر الشعب (يمكن اختيار أكثر من شعبة)" if self.language == 'ar' else "Select Sections (Multiple Selection)",
            font=FONTS['arabic_bold'] if self.language == 'ar' else FONTS['bold'],
            bg='white',
            padx=15,
            pady=15
        )
        sections_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # قائمة الشعب (Listbox مع إمكانية اختيار متعدد)
        listbox_frame = tk.Frame(sections_frame, bg='white')
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.LEFT if self.language == 'ar' else tk.RIGHT, fill=tk.Y)

        self.sections_listbox = tk.Listbox(
            listbox_frame,
            selectmode=tk.MULTIPLE,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            height=8,
            yscrollcommand=scrollbar.set
        )
        self.sections_listbox.pack(side=tk.LEFT if self.language == 'ar' else tk.RIGHT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.sections_listbox.yview)

        # ملاحظة
        note = "ملاحظة: اضغط Ctrl واختر لاختيار شعب متعددة" if self.language == 'ar' \
            else "Note: Hold Ctrl and click to select multiple sections"
        tk.Label(
            sections_frame,
            text=note,
            font=('Arial', 9, 'italic'),
            bg='white',
            fg='#888'
        ).pack(pady=(5, 0))

        # أزرار
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        # زر المعاينة والتحميل
        preview_text = "👁 معاينة وتحميل التقرير" if self.language == 'ar' else "👁 Preview & Download Report"
        tk.Button(
            buttons_frame,
            text=preview_text,
            command=self._preview_and_download_report,
            font=FONTS['arabic_bold'] if self.language == 'ar' else FONTS['bold'],
            bg='#1976D2',
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
        self.sections_listbox.delete(0, tk.END)
        self.sections_dict = {}

        if not self.course:
            return

        sm = SectionManager()
        sections = sm.get_sections_by_course(self.course.course_id)

        for section in sections:
            # التحقق من وجود طلاب ودرجات
            if section.students and len(section.students) > 0:
                display_name = f"الشعبة {section.section_number} - {section.academic_year} - {section.semester.value}" \
                    if self.language == 'ar' else \
                    f"Section {section.section_number} - {section.academic_year} - {section.semester.value}"

                self.sections_listbox.insert(tk.END, display_name)
                self.sections_dict[display_name] = section

    def _preview_and_download_report(self):
        """معاينة وتحميل التقرير"""
        # التحقق من اختيار المقرر
        if not self.course:
            messagebox.showerror(
                "خطأ" if self.language == 'ar' else "Error",
                "يجب اختيار المقرر" if self.language == 'ar' else "Please select a course",
                parent=self
            )
            return

        # الحصول على الشعب المختارة
        selected_indices = self.sections_listbox.curselection()
        if not selected_indices:
            messagebox.showerror(
                "خطأ" if self.language == 'ar' else "Error",
                "يجب اختيار شعبة واحدة على الأقل" if self.language == 'ar' else "Please select at least one section",
                parent=self
            )
            return

        self.selected_sections = []
        for index in selected_indices:
            section_name = self.sections_listbox.get(index)
            section = self.sections_dict.get(section_name)
            if section:
                self.selected_sections.append(section)

        try:
            # توليد التقرير في ملف مؤقت للمعاينة
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()

            # توليد التقرير
            report_generator = CLOStudentsAchievementReport(
                self.course,
                self.selected_sections,
                self.language
            )
            report_generator.generate_report(temp_path)

            # فتح التقرير للمعاينة
            os.startfile(temp_path)

            # عرض نافذة حوار للتحميل
            if messagebox.askyesno(
                "معاينة التقرير" if self.language == 'ar' else "Preview Report",
                "تم فتح التقرير للمعاينة.\n\nهل تريد حفظ نسخة من التقرير؟" if self.language == 'ar' else
                "The report has been opened for preview.\n\nDo you want to save a copy of the report?",
                parent=self
            ):
                # اختيار مكان حفظ الملف
                default_filename = f"{self.course.info.course_code}_students_achievement_report.pdf"
                file_path = filedialog.asksaveasfilename(
                    parent=self,
                    title="حفظ التقرير" if self.language == 'ar' else "Save Report",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=default_filename
                )

                if file_path:
                    # نسخ الملف المؤقت إلى الموقع المحدد
                    import shutil
                    shutil.copy2(temp_path, file_path)

                    messagebox.showinfo(
                        "تم الحفظ" if self.language == 'ar' else "Saved",
                        f"تم حفظ التقرير في:\n{file_path}" if self.language == 'ar' else
                        f"Report saved to:\n{file_path}",
                        parent=self
                    )

            # حذف الملف المؤقت بعد فترة
            self.after(5000, lambda: self._cleanup_temp_file(temp_path))

        except Exception as e:
            messagebox.showerror(
                "خطأ" if self.language == 'ar' else "Error",
                f"فشل توليد التقرير:\n{str(e)}" if self.language == 'ar' else f"Failed to generate report:\n{str(e)}",
                parent=self
            )

    def _cleanup_temp_file(self, file_path):
        """حذف الملف المؤقت"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass  # تجاهل الأخطاء في حذف الملفات المؤقتة
