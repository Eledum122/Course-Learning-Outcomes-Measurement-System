"""
نافذة إدارة أعضاء هيئة التدريس
Faculty Management Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import FONTS, COLORS
from models.faculty_member import FacultyMember, ACADEMIC_DEGREES
from managers.faculty_manager import FacultyManager
from managers.academic_program_manager import AcademicProgramManager
from translations import t


class FacultyManagementDialog(tk.Toplevel):
    """نافذة إدارة أعضاء هيئة التدريس"""

    def __init__(self, parent, language: str = 'ar'):
        super().__init__(parent)

        self.language = language
        self.faculty_manager = FacultyManager()
        self.program_manager = AcademicProgramManager()

        # إعداد النافذة
        self.title("إدارة أعضاء هيئة التدريس" if language == 'ar' else "Faculty Management")
        self.geometry("1200x750")
        self.resizable(True, True)

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # إنشاء الواجهة
        self._create_widgets()

        # تحميل البيانات
        self._refresh_table()

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
        title_text = "👨‍🏫 إدارة أعضاء هيئة التدريس" if self.language == 'ar' else "👨‍🏫 Faculty Management"
        tk.Label(
            main_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='white',
            fg='#1976D2'
        ).pack(pady=(0, 20))

        # إطار البحث والجدول
        table_frame = tk.LabelFrame(
            main_frame,
            text="قائمة أعضاء هيئة التدريس" if self.language == 'ar' else "Faculty Members List",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            padx=15,
            pady=15
        )
        table_frame.pack(fill=tk.BOTH, expand=True)

        # شريط البحث
        search_frame = tk.Frame(table_frame, bg='white')
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            search_frame,
            text="🔍 بحث:" if self.language == 'ar' else "🔍 Search:",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._search_members())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=40
        )
        search_entry.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5, fill=tk.X, expand=True)

        # الجدول
        table_container = tk.Frame(table_frame, bg='white')
        table_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side=tk.LEFT if self.language == 'ar' else tk.RIGHT, fill=tk.Y)

        # Treeview
        columns = ('employee_id', 'name', 'degree', 'college', 'department', 'email', 'phone')
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )
        scrollbar.config(command=self.tree.yview)

        # تعريف الأعمدة
        if self.language == 'ar':
            self.tree.heading('employee_id', text='الرقم الوظيفي')
            self.tree.heading('name', text='الاسم')
            self.tree.heading('degree', text='الدرجة العلمية')
            self.tree.heading('college', text='الكلية')
            self.tree.heading('department', text='القسم')
            self.tree.heading('email', text='البريد الإلكتروني')
            self.tree.heading('phone', text='الهاتف')
        else:
            self.tree.heading('employee_id', text='Employee ID')
            self.tree.heading('name', text='Name')
            self.tree.heading('degree', text='Academic Degree')
            self.tree.heading('college', text='College')
            self.tree.heading('department', text='Department')
            self.tree.heading('email', text='Email')
            self.tree.heading('phone', text='Phone')

        # تعيين عرض الأعمدة
        self.tree.column('employee_id', width=100, anchor='center')
        self.tree.column('name', width=180)
        self.tree.column('degree', width=160)
        self.tree.column('college', width=150)
        self.tree.column('department', width=150)
        self.tree.column('email', width=180)
        self.tree.column('phone', width=120)

        self.tree.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, fill=tk.BOTH, expand=True)

        # أزرار الإجراءات على الصف
        tree_buttons_frame = tk.Frame(table_frame, bg='white')
        tree_buttons_frame.pack(pady=(10, 0))

        tk.Button(
            tree_buttons_frame,
            text="➕ إضافة" if self.language == 'ar' else "➕ Add",
            command=self._add_member,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=12,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        tk.Button(
            tree_buttons_frame,
            text="✏ تعديل" if self.language == 'ar' else "✏ Edit",
            command=self._edit_selected,
            bg='#2196F3',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=12,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        tk.Button(
            tree_buttons_frame,
            text="🗑 حذف" if self.language == 'ar' else "🗑 Delete",
            command=self._delete_selected,
            bg='#F44336',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=12,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # عداد الأعضاء
        self.count_label = tk.Label(
            table_frame,
            text="",
            font=FONTS['arabic_small'] if self.language == 'ar' else FONTS['english_small'],
            bg='white',
            fg='#666'
        )
        self.count_label.pack(pady=(5, 0))

        # زر الإغلاق
        close_frame = tk.Frame(main_frame, bg='white')
        close_frame.pack(pady=(15, 0))

        tk.Button(
            close_frame,
            text="✖ إغلاق" if self.language == 'ar' else "✖ Close",
            command=self.destroy,
            bg='#9E9E9E',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=15,
            cursor='hand2'
        ).pack()

    def _refresh_table(self):
        """تحديث الجدول"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)

        # إضافة البيانات
        members = self.faculty_manager.get_all_members()
        for member in members:
            self.tree.insert('', tk.END, values=(
                member.employee_id,
                member.name,
                member.academic_degree,
                member.college_ar or '-',
                member.department_ar or '-',
                member.email or '-',
                member.phone or '-'
            ))

        # تحديث العداد
        count_text = f"إجمالي الأعضاء: {len(members)}" if self.language == 'ar' else f"Total Members: {len(members)}"
        self.count_label.config(text=count_text)

    def _search_members(self):
        """البحث عن أعضاء"""
        query = self.search_var.get()

        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)

        # إضافة النتائج
        results = self.faculty_manager.search_members(query)
        for member in results:
            self.tree.insert('', tk.END, values=(
                member.employee_id,
                member.name,
                member.academic_degree,
                member.college_ar or '-',
                member.department_ar or '-',
                member.email or '-',
                member.phone or '-'
            ))

        # تحديث العداد
        count_text = f"النتائج: {len(results)}" if self.language == 'ar' else f"Results: {len(results)}"
        self.count_label.config(text=count_text)

    def _add_member(self):
        """إضافة عضو جديد"""
        dialog = FacultyMemberFormDialog(
            self,
            self.language,
            self.faculty_manager,
            self.program_manager
        )
        self.wait_window(dialog)
        if dialog.result:
            self._refresh_table()

    def _edit_selected(self):
        """تعديل العضو المحدد"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "تحذير" if self.language == 'ar' else "Warning",
                "يرجى تحديد عضو للتعديل" if self.language == 'ar' else "Please select a member to edit",
                parent=self
            )
            return

        # الحصول على البيانات
        item = self.tree.item(selection[0])
        values = item['values']
        employee_id = str(values[0])  # تحويل إلى نص للتأكد من المطابقة

        # الحصول على بيانات العضو الكاملة
        member = self.faculty_manager.get_member_by_id(employee_id)
        if not member:
            messagebox.showerror(
                "خطأ" if self.language == 'ar' else "Error",
                "لم يتم العثور على العضو" if self.language == 'ar' else "Member not found",
                parent=self
            )
            return

        # فتح نافذة التعديل
        dialog = FacultyMemberFormDialog(
            self,
            self.language,
            self.faculty_manager,
            self.program_manager,
            member
        )
        self.wait_window(dialog)
        if dialog.result:
            self._refresh_table()

    def _delete_selected(self):
        """حذف العضو المحدد"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "تحذير" if self.language == 'ar' else "Warning",
                "يرجى تحديد عضو للحذف" if self.language == 'ar' else "Please select a member to delete",
                parent=self
            )
            return

        # الحصول على البيانات
        item = self.tree.item(selection[0])
        values = item['values']
        employee_id = str(values[0])  # تحويل إلى نص للتأكد من المطابقة
        name = values[1]

        # تأكيد الحذف
        result = messagebox.askyesno(
            "تأكيد الحذف" if self.language == 'ar' else "Confirm Delete",
            f"هل تريد حذف العضو:\n{name} ({employee_id})؟" if self.language == 'ar'
            else f"Do you want to delete:\n{name} ({employee_id})?",
            parent=self
        )

        if result:
            if self.faculty_manager.delete_member(employee_id):
                messagebox.showinfo(
                    "نجاح" if self.language == 'ar' else "Success",
                    "تم حذف العضو بنجاح" if self.language == 'ar' else "Member deleted successfully",
                    parent=self
                )
                self._refresh_table()
            else:
                messagebox.showerror(
                    "خطأ" if self.language == 'ar' else "Error",
                    "فشل حذف العضو" if self.language == 'ar' else "Failed to delete member",
                    parent=self
                )


class FacultyMemberFormDialog(tk.Toplevel):
    """نافذة نموذج إضافة/تعديل عضو هيئة تدريس"""

    def __init__(self, parent, language, faculty_manager, program_manager, member=None):
        super().__init__(parent)

        self.language = language
        self.faculty_manager = faculty_manager
        self.program_manager = program_manager
        self.member = member  # إذا كان التعديل
        self.result = None

        # إعداد النافذة
        title = "تعديل عضو" if member else "إضافة عضو"
        if language == 'en':
            title = "Edit Member" if member else "Add Member"
        self.title(title)
        self.geometry("650x700")
        self.resizable(False, False)

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # إنشاء الواجهة
        self._create_widgets()

        # ملء البيانات إذا كان تعديل
        if member:
            self._fill_data()

        # مركزة النافذة
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # إطار رئيسي مع إمكانية التمرير
        main_canvas = tk.Canvas(self, bg='white')
        scrollbar = tk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # الإطار الرئيسي
        main_frame = tk.Frame(scrollable_frame, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # القسم 1: المعلومات الأساسية
        basic_frame = tk.LabelFrame(
            main_frame,
            text="المعلومات الأساسية" if self.language == 'ar' else "Basic Information",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            padx=15,
            pady=10
        )
        basic_frame.pack(fill=tk.X, pady=(0, 15))

        # الرقم الوظيفي
        self._create_field(basic_frame, "الرقم الوظيفي:" if self.language == 'ar' else "Employee ID:", 'employee_id')

        # الاسم
        self._create_field(basic_frame, "الاسم:" if self.language == 'ar' else "Name:", 'name')

        # الدرجة العلمية
        self._create_combobox(basic_frame, "الدرجة العلمية:" if self.language == 'ar' else "Academic Degree:",
                              'degree', ACADEMIC_DEGREES)

        # التخصص العام
        self._create_field(basic_frame, "التخصص العام:" if self.language == 'ar' else "General Specialization:",
                          'general_spec')

        # التخصص الدقيق
        self._create_field(basic_frame, "التخصص الدقيق:" if self.language == 'ar' else "Specific Specialization:",
                          'specific_spec')

        # القسم 2: معلومات القسم والكلية
        dept_frame = tk.LabelFrame(
            main_frame,
            text="القسم والكلية" if self.language == 'ar' else "Department & College",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            padx=15,
            pady=10
        )
        dept_frame.pack(fill=tk.X, pady=(0, 15))

        # الكلية (عربي)
        colleges_ar = [''] + self.program_manager.get_unique_colleges_ar()
        self._create_combobox(dept_frame, "الكلية (عربي):" if self.language == 'ar' else "College (Arabic):",
                              'college_ar', colleges_ar)

        # الكلية (إنجليزي)
        colleges_en = [''] + self.program_manager.get_unique_colleges_en()
        self._create_combobox(dept_frame, "الكلية (إنجليزي):" if self.language == 'ar' else "College (English):",
                              'college_en', colleges_en)

        # القسم (عربي)
        departments_ar = [''] + self.program_manager.get_unique_departments_ar()
        self._create_combobox(dept_frame, "القسم (عربي):" if self.language == 'ar' else "Department (Arabic):",
                              'department_ar', departments_ar)

        # القسم (إنجليزي)
        departments_en = [''] + self.program_manager.get_unique_departments_en()
        self._create_combobox(dept_frame, "القسم (إنجليزي):" if self.language == 'ar' else "Department (English):",
                              'department_en', departments_en)

        # القسم 3: معلومات الاتصال
        contact_frame = tk.LabelFrame(
            main_frame,
            text="معلومات الاتصال" if self.language == 'ar' else "Contact Information",
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            padx=15,
            pady=10
        )
        contact_frame.pack(fill=tk.X, pady=(0, 15))

        # البريد الإلكتروني
        self._create_field(contact_frame, "البريد الإلكتروني:" if self.language == 'ar' else "Email:", 'email')

        # الهاتف
        self._create_field(contact_frame, "الهاتف:" if self.language == 'ar' else "Phone:", 'phone')

        # رقم المكتب
        self._create_field(contact_frame, "رقم المكتب:" if self.language == 'ar' else "Office Number:", 'office')

        # الحالة
        self.active_var = tk.BooleanVar(value=True)
        active_check = tk.Checkbutton(
            contact_frame,
            text="نشط" if self.language == 'ar' else "Active",
            variable=self.active_var,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white'
        )
        active_check.pack(anchor='e' if self.language == 'ar' else 'w', pady=5)

        # الأزرار
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=(15, 0))

        tk.Button(
            buttons_frame,
            text="💾 حفظ" if self.language == 'ar' else "💾 Save",
            command=self._save,
            bg='#4CAF50',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=12,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="✖ إلغاء" if self.language == 'ar' else "✖ Cancel",
            command=self.destroy,
            bg='#9E9E9E',
            fg='white',
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            width=12,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # حزم Canvas
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_field(self, parent, label_text, field_name):
        """إنشاء حقل إدخال"""
        row = tk.Frame(parent, bg='white')
        row.pack(fill=tk.X, pady=5)

        tk.Label(
            row,
            text=label_text,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            width=18,
            anchor='e' if self.language == 'ar' else 'w'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        entry = tk.Entry(
            row,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main']
        )
        entry.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, fill=tk.X, expand=True, padx=5)

        setattr(self, f'{field_name}_entry', entry)

    def _create_combobox(self, parent, label_text, field_name, values):
        """إنشاء حقل اختيار"""
        row = tk.Frame(parent, bg='white')
        row.pack(fill=tk.X, pady=5)

        tk.Label(
            row,
            text=label_text,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            bg='white',
            width=18,
            anchor='e' if self.language == 'ar' else 'w'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        var = tk.StringVar()
        combo = ttk.Combobox(
            row,
            textvariable=var,
            values=values,
            font=FONTS['arabic_main'] if self.language == 'ar' else FONTS['english_main'],
            state='readonly'
        )
        combo.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, fill=tk.X, expand=True, padx=5)

        setattr(self, f'{field_name}_var', var)
        setattr(self, f'{field_name}_combo', combo)

    def _fill_data(self):
        """ملء البيانات للتعديل"""
        if not self.member:
            return

        self.employee_id_entry.insert(0, self.member.employee_id)
        self.employee_id_entry.config(state='readonly')  # منع تعديل الرقم الوظيفي

        self.name_entry.insert(0, self.member.name)
        self.degree_var.set(self.member.academic_degree)
        self.general_spec_entry.insert(0, self.member.general_specialization)
        self.specific_spec_entry.insert(0, self.member.specific_specialization or '')

        self.college_ar_var.set(self.member.college_ar or '')
        self.college_en_var.set(self.member.college_en or '')
        self.department_ar_var.set(self.member.department_ar or '')
        self.department_en_var.set(self.member.department_en or '')

        self.email_entry.insert(0, self.member.email or '')
        self.phone_entry.insert(0, self.member.phone or '')
        self.office_entry.insert(0, self.member.office_number or '')

        self.active_var.set(self.member.is_active)

    def _save(self):
        """حفظ البيانات"""
        try:
            # التحقق من الحقول المطلوبة
            employee_id = self.employee_id_entry.get().strip()
            name = self.name_entry.get().strip()
            degree = self.degree_var.get().strip()
            general_spec = self.general_spec_entry.get().strip()

            if not employee_id:
                messagebox.showerror(
                    "خطأ" if self.language == 'ar' else "Error",
                    "الرقم الوظيفي مطلوب" if self.language == 'ar' else "Employee ID is required",
                    parent=self
                )
                return

            if not name:
                messagebox.showerror(
                    "خطأ" if self.language == 'ar' else "Error",
                    "الاسم مطلوب" if self.language == 'ar' else "Name is required",
                    parent=self
                )
                return

            if not degree:
                messagebox.showerror(
                    "خطأ" if self.language == 'ar' else "Error",
                    "الدرجة العلمية مطلوبة" if self.language == 'ar' else "Academic degree is required",
                    parent=self
                )
                return

            if not general_spec:
                messagebox.showerror(
                    "خطأ" if self.language == 'ar' else "Error",
                    "التخصص العام مطلوب" if self.language == 'ar' else "General specialization is required",
                    parent=self
                )
                return

            # إنشاء أو تحديث العضو
            if self.member:
                # تحديث
                updated_member = FacultyMember(
                    employee_id=self.member.employee_id,
                    name=name,
                    academic_degree=degree,
                    general_specialization=general_spec,
                    specific_specialization=self.specific_spec_entry.get().strip(),
                    college_ar=self.college_ar_var.get().strip(),
                    college_en=self.college_en_var.get().strip(),
                    department_ar=self.department_ar_var.get().strip(),
                    department_en=self.department_en_var.get().strip(),
                    email=self.email_entry.get().strip(),
                    phone=self.phone_entry.get().strip(),
                    office_number=self.office_entry.get().strip(),
                    is_active=self.active_var.get(),
                    user_id=self.member.user_id,
                    faculty_id=self.member.faculty_id,
                    created_date=self.member.created_date,
                    last_modified=datetime.now().isoformat()
                )

                if self.faculty_manager.update_member(self.member.employee_id, updated_member):
                    messagebox.showinfo(
                        "نجاح" if self.language == 'ar' else "Success",
                        "تم تحديث بيانات العضو بنجاح" if self.language == 'ar' else "Member updated successfully",
                        parent=self
                    )
                    self.result = updated_member
                    self.destroy()
                else:
                    messagebox.showerror(
                        "خطأ" if self.language == 'ar' else "Error",
                        "فشل تحديث البيانات" if self.language == 'ar' else "Failed to update member",
                        parent=self
                    )
            else:
                # إضافة
                new_member = FacultyMember(
                    employee_id=employee_id,
                    name=name,
                    academic_degree=degree,
                    general_specialization=general_spec,
                    specific_specialization=self.specific_spec_entry.get().strip(),
                    college_ar=self.college_ar_var.get().strip(),
                    college_en=self.college_en_var.get().strip(),
                    department_ar=self.department_ar_var.get().strip(),
                    department_en=self.department_en_var.get().strip(),
                    email=self.email_entry.get().strip(),
                    phone=self.phone_entry.get().strip(),
                    office_number=self.office_entry.get().strip(),
                    is_active=self.active_var.get()
                )

                if self.faculty_manager.add_member(new_member):
                    messagebox.showinfo(
                        "نجاح" if self.language == 'ar' else "Success",
                        "تمت إضافة العضو بنجاح" if self.language == 'ar' else "Member added successfully",
                        parent=self
                    )
                    self.result = new_member
                    self.destroy()
                else:
                    messagebox.showerror(
                        "خطأ" if self.language == 'ar' else "Error",
                        "الرقم الوظيفي موجود مسبقاً" if self.language == 'ar' else "Employee ID already exists",
                        parent=self
                    )

        except ValueError as e:
            messagebox.showerror(
                "خطأ" if self.language == 'ar' else "Error",
                str(e),
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                "خطأ" if self.language == 'ar' else "Error",
                f"حدث خطأ غير متوقع: {str(e)}" if self.language == 'ar' else f"Unexpected error: {str(e)}",
                parent=self
            )
