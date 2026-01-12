"""
حوار إدخال بيانات الطلاب - المرحلة الثالثة - الخطوة 2
Stage 3 Step 2: Students Data Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
import os
from models import CourseSection, Student, StudentStatus
from managers.section_manager import SectionManager
from config import FONTS
from translations import t


class Stage3StudentsDataDialog(tk.Toplevel):
    """حوار إدخال بيانات الطلاب"""

    def __init__(self, parent, section: CourseSection, language: str = 'ar'):
        super().__init__(parent)

        self.section = section
        self.language = language

        # إعداد النافذة
        self.title("المرحلة الثالثة - الخطوة 2: بيانات الطلاب" if language == 'ar'
                  else "Stage 3 - Step 2: Students Data")
        self.geometry("900x650")
        self.resizable(True, True)

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # إنشاء الواجهة
        self._create_widgets()

        # تحميل الطلاب الموجودين
        self._load_students()

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
        title_text = f"بيانات الطلاب - الشعبة {self.section.section_number}" if self.language == 'ar' \
            else f"Students Data - Section {self.section.section_number}"
        tk.Label(
            main_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='white',
            fg='#1976D2'
        ).pack(pady=(0, 15))

        # إطار الأزرار العلوية
        top_buttons_frame = tk.Frame(main_frame, bg='white')
        top_buttons_frame.pack(fill=tk.X, pady=(0, 10))

        # زر رفع ملف Excel
        upload_text = "📁 رفع ملف Excel" if self.language == 'ar' else "📁 Upload Excel File"
        tk.Button(
            top_buttons_frame,
            text=upload_text,
            command=self._import_from_excel,
            bg='#2196F3',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=20,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر تحميل نموذج Excel
        template_text = "📥 تحميل نموذج" if self.language == 'ar' else "📥 Download Template"
        tk.Button(
            top_buttons_frame,
            text=template_text,
            command=self._download_template,
            bg='#9C27B0',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=20,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر إضافة طالب يدوياً
        add_text = "➕ إضافة طالب" if self.language == 'ar' else "➕ Add Student"
        tk.Button(
            top_buttons_frame,
            text=add_text,
            command=self._add_student_manual,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=20,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # إطار الجدول
        table_frame = tk.Frame(main_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # شريط التمرير
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الجدول
        columns = ('seq', 'student_id', 'name', 'status')

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            height=20
        )
        scrollbar.config(command=self.tree.yview)

        # تعريف الأعمدة
        if self.language == 'ar':
            headers = {
                'seq': '#',
                'student_id': 'الرقم الجامعي',
                'name': 'الاسم',
                'status': 'الحالة'
            }
        else:
            headers = {
                'seq': 'Seq',
                'student_id': 'Student ID',
                'name': 'Name',
                'status': 'Status'
            }

        # تعيين عناوين الأعمدة وعرضها
        widths = {
            'seq': 50,
            'student_id': 150,
            'name': 400,
            'status': 150
        }

        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor='center' if col in ['seq', 'student_id', 'status'] else 'w')

        self.tree.pack(fill=tk.BOTH, expand=True)

        # ربط حدث النقر المزدوج
        self.tree.bind('<Double-1>', self._on_double_click)

        # إطار المعلومات
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(fill=tk.X, pady=(5, 10))

        total_text = f"إجمالي الطلاب: {len(self.section.students)}" if self.language == 'ar' \
            else f"Total Students: {len(self.section.students)}"
        self.total_label = tk.Label(
            info_frame,
            text=total_text,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            fg='#555'
        )
        self.total_label.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT)

        # الأزرار السفلية
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=(10, 0))

        # زر تحريك لأعلى
        move_up_text = "⬆ تحريك لأعلى" if self.language == 'ar' else "⬆ Move Up"
        tk.Button(
            buttons_frame,
            text=move_up_text,
            command=self._move_student_up,
            bg='#2196F3',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر تحريك لأسفل
        move_down_text = "⬇ تحريك لأسفل" if self.language == 'ar' else "⬇ Move Down"
        tk.Button(
            buttons_frame,
            text=move_down_text,
            command=self._move_student_down,
            bg='#2196F3',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر تعديل
        edit_text = "✏ تعديل" if self.language == 'ar' else "✏ Edit"
        tk.Button(
            buttons_frame,
            text=edit_text,
            command=self._edit_student,
            bg='#FF9800',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر حذف طالب
        delete_text = "حذف" if self.language == 'ar' else "Delete"
        tk.Button(
            buttons_frame,
            text=delete_text,
            command=self._delete_student,
            bg='#F44336',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر حذف الكل
        delete_all_text = "حذف الكل" if self.language == 'ar' else "Delete All"
        tk.Button(
            buttons_frame,
            text=delete_all_text,
            command=self._delete_all_students,
            bg='#D32F2F',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # زر حفظ
        save_text = "حفظ" if self.language == 'ar' else "Save"
        tk.Button(
            buttons_frame,
            text=save_text,
            command=self._save_students,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            cursor='hand2'
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
            width=15,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

    def _load_students(self):
        """تحميل الطلاب في الجدول"""
        # مسح البيانات الحالية
        for item in self.tree.get_children():
            self.tree.delete(item)

        # ترتيب الطلاب حسب seq
        students = sorted(self.section.students, key=lambda s: s.seq)

        # إضافة الطلاب
        for student in students:
            status_display = self._get_status_display(student.status)
            self.tree.insert('', 'end', values=(
                student.seq,
                student.student_id,
                student.name,
                status_display
            ))

        # تحديث العداد
        self._update_total_label()

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

    def _update_total_label(self):
        """تحديث عداد الطلاب"""
        total_text = f"إجمالي الطلاب: {len(self.section.students)}" if self.language == 'ar' \
            else f"Total Students: {len(self.section.students)}"
        self.total_label.config(text=total_text)

    def _import_from_excel(self):
        """استيراد الطلاب من ملف Excel"""
        file_path = filedialog.askopenfilename(
            title="اختر ملف Excel" if self.language == 'ar' else "Select Excel File",
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
            required_columns = ['Student No', 'Student Name', 'Status']
            optional_columns = ['Seq']

            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                messagebox.showerror(
                    t('error', self.language),
                    f"الأعمدة المطلوبة مفقودة: {', '.join(missing_columns)}\n\nالأعمدة المطلوبة: {', '.join(required_columns)}"
                    if self.language == 'ar' else
                    f"Required columns missing: {', '.join(missing_columns)}\n\nRequired columns: {', '.join(required_columns)}",
                    parent=self
                )
                return

            # مسح الطلاب الحاليين أو الإضافة؟
            if self.section.students:
                confirm = messagebox.askyesnocancel(
                    t('confirm', self.language),
                    "هل تريد استبدال الطلاب الحاليين أم الإضافة إليهم؟\n\nنعم = استبدال، لا = إضافة، إلغاء = إلغاء العملية"
                    if self.language == 'ar' else
                    "Do you want to replace current students or add to them?\n\nYes = Replace, No = Add, Cancel = Cancel",
                    parent=self
                )

                if confirm is None:  # Cancel
                    return
                elif confirm:  # Yes - Replace
                    self.section.students = []

            # إضافة الطلاب
            max_seq = max([s.seq for s in self.section.students], default=0)

            for idx, row in df.iterrows():
                student_id = str(row['Student No']).strip()
                name = str(row['Student Name']).strip()
                status_str = str(row['Status']).strip()

                # الحصول على الترتيب
                if 'Seq' in df.columns and pd.notna(row['Seq']):
                    seq = int(row['Seq'])
                else:
                    max_seq += 1
                    seq = max_seq

                # تحويل الحالة
                status_map = {
                    'Regular': StudentStatus.REGULAR,
                    'Dropped': StudentStatus.DROPPED,
                    'Prohibited': StudentStatus.PROHIBITED,
                    'Incomplete': StudentStatus.INCOMPLETE,
                    'منتظم': StudentStatus.REGULAR,
                    'معتذر': StudentStatus.DROPPED,
                    'محروم': StudentStatus.PROHIBITED,
                    'غير مكتمل': StudentStatus.INCOMPLETE
                }

                status = status_map.get(status_str, StudentStatus.REGULAR)

                # إنشاء الطالب
                student = Student(student_id)
                student.name = name
                student.status = status
                student.seq = seq

                self.section.students.append(student)

            # تحديث العرض
            self._load_students()

            messagebox.showinfo(
                t('success', self.language),
                f"تم استيراد {len(df)} طالب بنجاح" if self.language == 'ar'
                else f"Successfully imported {len(df)} students",
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

    def _download_template(self):
        """تحميل نموذج Excel"""
        try:
            import pandas as pd

            # إنشاء بيانات النموذج
            template_data = {
                'Seq': [1, 2, 3],
                'Student No': ['421002649', '421005812', '431002801'],
                'Student Name': ['STUDENT NAME 1', 'STUDENT NAME 2', 'STUDENT NAME 3'],
                'Status': ['Regular', 'Regular', 'Prohibited']
            }

            df = pd.DataFrame(template_data)

            # حفظ الملف
            file_path = filedialog.asksaveasfilename(
                title="حفظ نموذج Excel" if self.language == 'ar' else "Save Excel Template",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile="students_template.xlsx",
                parent=self
            )

            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo(
                    t('success', self.language),
                    f"تم حفظ النموذج بنجاح:\n{file_path}" if self.language == 'ar'
                    else f"Template saved successfully:\n{file_path}",
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
                f"فشل حفظ النموذج:\n{str(e)}" if self.language == 'ar'
                else f"Failed to save template:\n{str(e)}",
                parent=self
            )

    def _add_student_manual(self):
        """إضافة طالب يدوياً"""
        # Create a simple dialog
        dialog = tk.Toplevel(self)
        dialog.title("إضافة طالب" if self.language == 'ar' else "Add Student")
        dialog.geometry("500x300")
        dialog.transient(self)
        dialog.grab_set()

        frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Student ID
        tk.Label(frame, text="الرقم الجامعي:" if self.language == 'ar' else "Student ID:",
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                bg='white').grid(row=0, column=0, sticky='w', pady=5)
        id_entry = tk.Entry(frame, font=FONTS['english_main'], width=30)
        id_entry.grid(row=0, column=1, pady=5, padx=10)

        # Student Name
        tk.Label(frame, text="اسم الطالب:" if self.language == 'ar' else "Student Name:",
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(frame, font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'], width=30)
        name_entry.grid(row=1, column=1, pady=5, padx=10)

        # Status
        tk.Label(frame, text="الحالة:" if self.language == 'ar' else "Status:",
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                bg='white').grid(row=2, column=0, sticky='w', pady=5)

        status_var = tk.StringVar(value="Regular")
        status_values = ["Regular", "Dropped", "Prohibited", "Incomplete"]
        status_combo = ttk.Combobox(frame, textvariable=status_var, values=status_values,
                                   state='readonly', font=FONTS['english_main'], width=28)
        status_combo.grid(row=2, column=1, pady=5, padx=10)

        def add_student():
            student_id = id_entry.get().strip()
            name = name_entry.get().strip()

            if not student_id or not name:
                messagebox.showerror(t('error', self.language),
                                   "الرجاء إدخال جميع البيانات" if self.language == 'ar'
                                   else "Please enter all data", parent=dialog)
                return

            # Create student
            student = Student(student_id)
            student.name = name
            student.status = StudentStatus(status_var.get())
            student.seq = len(self.section.students) + 1

            self.section.students.append(student)
            self._load_students()
            dialog.destroy()

        # Buttons
        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="إضافة" if self.language == 'ar' else "Add",
                 command=add_student, bg='#4CAF50', fg='white',
                 font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="إلغاء" if self.language == 'ar' else "Cancel",
                 command=dialog.destroy, bg='#F44336', fg='white',
                 font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)

    def _on_double_click(self, event):
        """تعديل طالب عند النقر المزدوج"""
        self._edit_student()

    def _edit_student(self):
        """تعديل الطالب المحدد"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار طالب للتعديل" if self.language == 'ar' else "Please select a student to edit",
                parent=self
            )
            return

        item = selection[0]
        values = self.tree.item(item, 'values')
        student_id = values[1]

        # البحث عن الطالب
        student = None
        for s in self.section.students:
            if s.student_id == student_id:
                student = s
                break

        if not student:
            messagebox.showerror(
                t('error', self.language),
                "لم يتم العثور على الطالب" if self.language == 'ar' else "Student not found",
                parent=self
            )
            return

        # إنشاء نافذة التعديل
        dialog = tk.Toplevel(self)
        dialog.title("تعديل بيانات الطالب" if self.language == 'ar' else "Edit Student")
        dialog.geometry("500x300")
        dialog.transient(self)
        dialog.grab_set()

        frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Student ID
        tk.Label(frame, text="الرقم الجامعي:" if self.language == 'ar' else "Student ID:",
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                bg='white').grid(row=0, column=0, sticky='w', pady=5)
        id_entry = tk.Entry(frame, font=FONTS['english_main'], width=30)
        id_entry.insert(0, student.student_id)
        id_entry.grid(row=0, column=1, pady=5, padx=10)

        # Student Name
        tk.Label(frame, text="اسم الطالب:" if self.language == 'ar' else "Student Name:",
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(frame, font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'], width=30)
        name_entry.insert(0, student.name)
        name_entry.grid(row=1, column=1, pady=5, padx=10)

        # Status
        tk.Label(frame, text="الحالة:" if self.language == 'ar' else "Status:",
                font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                bg='white').grid(row=2, column=0, sticky='w', pady=5)

        current_status = student.status.value if hasattr(student.status, 'value') else student.status
        status_var = tk.StringVar(value=current_status)
        status_values = ["Regular", "Dropped", "Prohibited", "Incomplete"]
        status_combo = ttk.Combobox(frame, textvariable=status_var, values=status_values,
                                   state='readonly', font=FONTS['english_main'], width=28)
        status_combo.grid(row=2, column=1, pady=5, padx=10)

        def save_changes():
            new_student_id = id_entry.get().strip()
            new_name = name_entry.get().strip()

            if not new_student_id or not new_name:
                messagebox.showerror(t('error', self.language),
                                   "الرجاء إدخال جميع البيانات" if self.language == 'ar'
                                   else "Please enter all data", parent=dialog)
                return

            # التحقق من عدم تكرار الرقم الجامعي
            if new_student_id != student.student_id:
                for s in self.section.students:
                    if s.student_id == new_student_id:
                        messagebox.showerror(
                            t('error', self.language),
                            "هذا الرقم الجامعي موجود بالفعل" if self.language == 'ar'
                            else "This student ID already exists",
                            parent=dialog
                        )
                        return

            # تحديث بيانات الطالب
            student.student_id = new_student_id
            student.name = new_name
            student.status = StudentStatus(status_var.get())

            self._load_students()
            dialog.destroy()

        # Buttons
        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="حفظ" if self.language == 'ar' else "Save",
                 command=save_changes, bg='#4CAF50', fg='white',
                 font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="إلغاء" if self.language == 'ar' else "Cancel",
                 command=dialog.destroy, bg='#F44336', fg='white',
                 font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)

    def _move_student_up(self):
        """تحريك الطالب المحدد لأعلى"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار طالب للتحريك" if self.language == 'ar' else "Please select a student to move",
                parent=self
            )
            return

        item = selection[0]
        values = self.tree.item(item, 'values')
        student_id = values[1]

        # البحث عن الطالب
        student_index = None
        for idx, s in enumerate(self.section.students):
            if s.student_id == student_id:
                student_index = idx
                break

        if student_index is None:
            return

        # التحقق من إمكانية التحريك لأعلى
        if student_index == 0:
            messagebox.showinfo(
                t('info', self.language),
                "الطالب في أول القائمة" if self.language == 'ar' else "Student is at the top of the list",
                parent=self
            )
            return

        # تبديل الطالب مع الذي قبله
        self.section.students[student_index], self.section.students[student_index - 1] = \
            self.section.students[student_index - 1], self.section.students[student_index]

        # تحديث أرقام التسلسل
        self._update_sequence_numbers()

        # إعادة تحميل الجدول
        self._load_students()

        # إعادة تحديد الطالب في موقعه الجديد
        new_index = student_index - 1
        items = self.tree.get_children()
        if new_index < len(items):
            self.tree.selection_set(items[new_index])
            self.tree.focus(items[new_index])
            self.tree.see(items[new_index])

    def _move_student_down(self):
        """تحريك الطالب المحدد لأسفل"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار طالب للتحريك" if self.language == 'ar' else "Please select a student to move",
                parent=self
            )
            return

        item = selection[0]
        values = self.tree.item(item, 'values')
        student_id = values[1]

        # البحث عن الطالب
        student_index = None
        for idx, s in enumerate(self.section.students):
            if s.student_id == student_id:
                student_index = idx
                break

        if student_index is None:
            return

        # التحقق من إمكانية التحريك لأسفل
        if student_index == len(self.section.students) - 1:
            messagebox.showinfo(
                t('info', self.language),
                "الطالب في آخر القائمة" if self.language == 'ar' else "Student is at the bottom of the list",
                parent=self
            )
            return

        # تبديل الطالب مع الذي بعده
        self.section.students[student_index], self.section.students[student_index + 1] = \
            self.section.students[student_index + 1], self.section.students[student_index]

        # تحديث أرقام التسلسل
        self._update_sequence_numbers()

        # إعادة تحميل الجدول
        self._load_students()

        # إعادة تحديد الطالب في موقعه الجديد
        new_index = student_index + 1
        items = self.tree.get_children()
        if new_index < len(items):
            self.tree.selection_set(items[new_index])
            self.tree.focus(items[new_index])
            self.tree.see(items[new_index])

    def _update_sequence_numbers(self):
        """تحديث أرقام التسلسل لجميع الطلاب"""
        for idx, student in enumerate(self.section.students, 1):
            student.seq = idx

    def _delete_student(self):
        """حذف الطالب المحدد"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء اختيار طالب للحذف" if self.language == 'ar' else "Please select a student to delete",
                parent=self
            )
            return

        item = selection[0]
        values = self.tree.item(item, 'values')
        student_id = values[1]

        # حذف الطالب
        self.section.students = [s for s in self.section.students if s.student_id != student_id]
        self._load_students()

    def _delete_all_students(self):
        """حذف جميع الطلاب"""
        if not self.section.students:
            return

        confirm = messagebox.askyesno(
            t('confirm', self.language),
            f"هل أنت متأكد من حذف جميع الطلاب ({len(self.section.students)} طالب)؟"
            if self.language == 'ar' else
            f"Are you sure you want to delete all students ({len(self.section.students)} students)?",
            parent=self
        )

        if confirm:
            self.section.students = []
            self._load_students()

    def _save_students(self):
        """حفظ بيانات الطلاب"""
        if not self.section.students:
            messagebox.showwarning(
                t('warning', self.language),
                "لا يوجد طلاب للحفظ" if self.language == 'ar' else "No students to save",
                parent=self
            )
            return

        # تحديث حالة الإكمال
        self.section.students_data_completed = True

        # حفظ الشعبة
        sm = SectionManager()
        if sm.save_section(self.section):
            messagebox.showinfo(
                t('success', self.language),
                f"تم حفظ بيانات {len(self.section.students)} طالب بنجاح"
                if self.language == 'ar' else
                f"Successfully saved {len(self.section.students)} students",
                parent=self
            )
        else:
            messagebox.showerror(
                t('error', self.language),
                "فشل حفظ بيانات الطلاب" if self.language == 'ar' else "Failed to save students data",
                parent=self
            )
