"""
حوار توليد تقرير قياس نواتج تعلم المقرر المجمع
Generate Aggregated CLO Assessment Report Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
import os
import shutil
import tempfile
from datetime import datetime
from models import Course
from managers.section_manager import SectionManager
from config import FONTS
from translations import t


class GenerateAggregatedReportDialog(tk.Toplevel):
    """حوار توليد تقرير قياس نواتج تعلم المقرر المجمع"""

    def __init__(self, parent, course: Course, language: str = 'ar'):
        super().__init__(parent)

        self.course = course
        self.language = language
        self.selected_sections = []

        # إعداد النافذة
        self.title("تقرير قياس نواتج التعلم المجمع" if language == 'ar'
                  else "Aggregated CLO Assessment Report")
        self.geometry("850x700")
        self.resizable(True, True)
        self.configure(bg='#f5f5f5')

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # إنشاء الواجهة
        self._create_widgets()

        # تحميل الشعب
        self._load_sections()

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
        title_text = "تقرير قياس نواتج التعلم المجمع" if self.language == 'ar' \
            else "Aggregated CLO Assessment Report"
        tk.Label(
            header_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='#1976D2',
            fg='white'
        ).pack()

        # إطار معلومات المقرر
        info_frame = tk.Frame(main_frame, bg='white', padx=15, pady=12, relief=tk.SOLID, borderwidth=1)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        info_text = f"{self.course.info.course_code} - {self.course.info.course_title}"
        tk.Label(
            info_frame,
            text=info_text,
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#333'
        ).pack()

        # إطار اختيار الشعب
        selection_frame = tk.LabelFrame(
            main_frame,
            text="  اختر الشعب:  " if self.language == 'ar' else "  Select Sections:  ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#1976D2',
            padx=15,
            pady=15,
            relief=tk.GROOVE,
            borderwidth=2
        )
        selection_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # قائمة الشعب
        list_frame = tk.Frame(selection_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.sections_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            font=('Arial', 10),
            height=15,
            bg='#fafafa',
            fg='#333',
            selectbackground='#1976D2',
            selectforeground='white',
            activestyle='none',
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightcolor='#1976D2',
            highlightbackground='#ddd'
        )
        self.sections_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.config(command=self.sections_listbox.yview)

        # تعليمات
        instructions_frame = tk.Frame(main_frame, bg='#E3F2FD', padx=12, pady=8, relief=tk.SOLID, borderwidth=1)
        instructions_frame.pack(fill=tk.X, pady=(0, 15))

        instructions = "ملاحظة: يمكنك اختيار شعب متعددة. سيتم تجميع النتائج حسب النوع (ذكور/إناث)." \
            if self.language == 'ar' else \
            "Note: You can select multiple sections. Results will be aggregated by gender (Male/Female)."
        tk.Label(
            instructions_frame,
            text=instructions,
            font=('Arial', 9),
            bg='#E3F2FD',
            fg='#1565C0',
            wraplength=750,
            justify='right' if self.language == 'ar' else 'left'
        ).pack()

        # اختيار اللغة
        lang_frame = tk.Frame(main_frame, bg='white', padx=15, pady=12, relief=tk.SOLID, borderwidth=1)
        lang_frame.pack(fill=tk.X, pady=(0, 20))

        lang_label = "لغة التقرير:" if self.language == 'ar' else "Report Language:"
        tk.Label(
            lang_frame,
            text=lang_label,
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#333'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=(0, 15))

        self.report_language_var = tk.StringVar(value='en')
        self.lang_display_var = tk.StringVar(value='English')

        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_display_var,
            values=['English', 'العربية'],
            state='readonly',
            font=('Arial', 10),
            width=20
        )
        lang_combo.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT)
        lang_combo.current(0)

        # تحديث القيمة عند التغيير
        def on_language_change(event):
            selection = self.lang_display_var.get()
            if selection == 'العربية':
                self.report_language_var.set('ar')
            else:
                self.report_language_var.set('en')

        lang_combo.bind('<<ComboboxSelected>>', on_language_change)

        # الأزرار
        buttons_frame = tk.Frame(main_frame, bg='#f5f5f5')
        buttons_frame.pack(pady=(5, 0), fill=tk.X)

        # إطار مركزي للأزرار
        center_buttons = tk.Frame(buttons_frame, bg='#f5f5f5')
        center_buttons.pack()

        # زر توليد التقرير
        generate_text = "Preview & Download Report" if self.language == 'en' else "معاينة وتحميل التقرير"
        self.generate_btn = tk.Button(
            center_buttons,
            text=generate_text,
            command=self._preview_and_download_report,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=28,
            height=2,
            cursor='hand2',
            relief=tk.FLAT,
            borderwidth=0,
            activebackground='#45a049',
            activeforeground='white'
        )
        self.generate_btn.pack(side=tk.LEFT, padx=8)

        # تأثير hover للزر
        self.generate_btn.bind('<Enter>', lambda e: self.generate_btn.config(bg='#45a049'))
        self.generate_btn.bind('<Leave>', lambda e: self.generate_btn.config(bg='#4CAF50'))

        # زر إلغاء
        cancel_text = "Close" if self.language == 'en' else "إغلاق"
        self.close_btn = tk.Button(
            center_buttons,
            text=cancel_text,
            command=self.destroy,
            bg='#757575',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=18,
            height=2,
            cursor='hand2',
            relief=tk.FLAT,
            borderwidth=0,
            activebackground='#616161',
            activeforeground='white'
        )
        self.close_btn.pack(side=tk.LEFT, padx=8)

        # تأثير hover للزر
        self.close_btn.bind('<Enter>', lambda e: self.close_btn.config(bg='#616161'))
        self.close_btn.bind('<Leave>', lambda e: self.close_btn.config(bg='#757575'))

    def _load_sections(self):
        """تحميل الشعب المتاحة"""
        sm = SectionManager()
        sections = sm.get_sections_by_course(self.course.course_id)

        # فرز الشعب حسب السنة والفصل
        sections.sort(key=lambda s: (s.academic_year, s.semester.value, s.section_number))

        for section in sections:
            # عرض معلومات الشعبة بتنسيق أفضل
            semester_value = section.semester.value if hasattr(section.semester, 'value') else section.semester

            # ترجمة الفصل الدراسي
            if self.language == 'ar':
                semester_display = {
                    'First': 'الأول',
                    'Second': 'الثاني',
                    'Summer': 'الصيفي'
                }.get(semester_value, semester_value)
                gender_display = "ذكور" if section.gender_section == 'Male' else "إناث"
                display_text = f"{section.section_number}  |  {section.academic_year} - {semester_display}  |  {gender_display}"
            else:
                semester_display = semester_value
                gender_display = "Male" if section.gender_section == 'Male' else "Female"
                display_text = f"{section.section_number}  |  {section.academic_year} - {semester_display}  |  {gender_display}"

            self.sections_listbox.insert(tk.END, display_text)

        self.all_sections = sections

    def _preview_and_download_report(self):
        """معاينة وتحميل التقرير"""
        # الحصول على الشعب المختارة
        selection_indices = self.sections_listbox.curselection()

        if not selection_indices:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار شعبة واحدة على الأقل" if self.language == 'ar'
                else "Please select at least one section",
                parent=self
            )
            return

        self.selected_sections = [self.all_sections[i] for i in selection_indices]

        # التحقق من وجود شعب ذكور وإناث
        male_sections = [s for s in self.selected_sections if s.gender_section == 'Male']
        female_sections = [s for s in self.selected_sections if s.gender_section == 'Female']

        if not male_sections and not female_sections:
            messagebox.showwarning(
                t('warning', self.language),
                "لا توجد شعب محددة النوع في الاختيار" if self.language == 'ar'
                else "No gender-specified sections in selection",
                parent=self
            )
            return

        # الحصول على لغة التقرير
        report_language = self.report_language_var.get()

        try:
            # توليد التقرير في ملف مؤقت للمعاينة
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()

            # توليد التقرير
            from reports.aggregated_clo_assessment_report import AggregatedCLOAssessmentReport

            report_generator = AggregatedCLOAssessmentReport(
                self.course,
                self.selected_sections,
                report_language
            )
            report_generator.generate_report(temp_path)

            # فتح التقرير للمعاينة
            os.startfile(temp_path)

            # عرض نافذة حوار للتحميل
            if messagebox.askyesno(
                "معاينة التقرير" if self.language == 'ar' else "Preview Report",
                "تم فتح التقرير للمعاينة.\n\nهل تريد حفظ نسخة من التقرير؟"
                if self.language == 'ar' else
                "The report has been opened for preview.\n\nDo you want to save a copy of the report?",
                parent=self
            ):
                # اختيار مكان الحفظ
                default_filename = f"Aggregated_CLO_Report_{self.course.info.course_code}_{datetime.now().strftime('%Y%m%d')}.pdf"

                file_path = filedialog.asksaveasfilename(
                    title="حفظ التقرير" if self.language == 'ar' else "Save Report",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=default_filename,
                    parent=self
                )

                if file_path:
                    # نسخ الملف
                    shutil.copy2(temp_path, file_path)

                    messagebox.showinfo(
                        t('success', self.language),
                        f"تم حفظ التقرير بنجاح:\n{file_path}" if self.language == 'ar'
                        else f"Report saved successfully:\n{file_path}",
                        parent=self
                    )

            # حذف الملف المؤقت بعد فترة
            self.after(5000, lambda: self._cleanup_temp_file(temp_path))

        except Exception as e:
            messagebox.showerror(
                t('error', self.language),
                f"فشل توليد التقرير:\n{str(e)}" if self.language == 'ar'
                else f"Failed to generate report:\n{str(e)}",
                parent=self
            )

    def _cleanup_temp_file(self, file_path):
        """حذف الملف المؤقت"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not delete temporary file: {e}")
