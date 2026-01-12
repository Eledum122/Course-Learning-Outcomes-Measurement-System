"""
واجهة إدارة البرامج الأكاديمية - Academic Programs Management Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, List
from datetime import datetime

from models.academic_program import AcademicProgram
from managers.academic_program_manager import program_manager
from managers.access_control import AccessControl
from config import COLORS
from translations import t, get_language


class AcademicProgramsDialog:
    """واجهة إدارة البرامج الأكاديمية"""

    def __init__(self, parent, access_control: AccessControl, language: str = 'ar', main_window=None):
        """تهيئة الواجهة"""
        self.parent = parent
        self.access_control = access_control
        self.language = language
        self.program_manager = program_manager
        self.main_window = main_window

        # إنشاء النافذة
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(t("academic_programs_management", language))
        self.dialog.geometry("1100x650")
        self.dialog.resizable(True, True)

        # جعل النافذة في الواجهة
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # تطبيق الألوان
        self.dialog.configure(bg=COLORS['bg_light'])

        # إنشاء الواجهة
        self._create_widgets()
        self._load_programs()

        # وضع النافذة في المنتصف
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # الإطار الرئيسي
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg_light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # العنوان
        title_frame = tk.Frame(main_frame, bg=COLORS['primary'], height=80)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🎓 " + t("academic_programs_management", self.language),
            font=('Arial', 18, 'bold'),
            bg=COLORS['primary'],
            fg='white'
        )
        title_label.pack(expand=True)

        # شريط الأدوات
        toolbar_frame = tk.Frame(main_frame, bg=COLORS['bg_light'])
        toolbar_frame.pack(fill=tk.X, pady=(0, 15))

        # شريط البحث
        search_frame = tk.Frame(toolbar_frame, bg=COLORS['bg_light'])
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            search_frame,
            text="🔍 " + t("search", self.language) + ":",
            font=('Arial', 10),
            bg=COLORS['bg_light']
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filter_programs())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            width=40
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # أزرار الإجراءات
        buttons_frame = tk.Frame(toolbar_frame, bg=COLORS['bg_light'])
        buttons_frame.pack(side=tk.RIGHT)

        self._create_action_button(
            buttons_frame,
            "➕ " + t("new_program", self.language),
            self._add_program,
            COLORS['success']
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            buttons_frame,
            "✏️ " + t("edit", self.language),
            self._edit_program,
            COLORS['primary']
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            buttons_frame,
            "👤 " + t("assign_coordinator", self.language),
            self._assign_coordinator,
            COLORS['info']
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            buttons_frame,
            "🗑️ " + t("delete", self.language),
            self._delete_program,
            COLORS['danger']
        ).pack(side=tk.LEFT, padx=5)

        # جدول البرامج
        self._create_programs_table(main_frame)

        # إطار الأزرار السفلي
        bottom_frame = tk.Frame(main_frame, bg=COLORS['bg_light'])
        bottom_frame.pack(fill=tk.X, pady=(20, 0))

        # زر الإحصائيات
        stats_btn = tk.Button(
            bottom_frame,
            text="📊 " + t("statistics", self.language),
            command=self._show_statistics,
            font=('Arial', 11, 'bold'),
            bg=COLORS['info'],
            fg='white',
            padx=25,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2',
            borderwidth=0
        )
        stats_btn.pack(side=tk.LEFT, padx=5)

        # زر الإغلاق
        close_btn = tk.Button(
            bottom_frame,
            text="❌ " + t("close", self.language),
            command=self.dialog.destroy,
            font=('Arial', 11, 'bold'),
            bg='#FFB74D',
            fg='white',
            padx=25,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2',
            borderwidth=0
        )
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _create_action_button(self, parent, text, command, color):
        """إنشاء زر إجراء"""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Arial', 10, 'bold'),
            bg=color,
            fg='white',
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2',
            borderwidth=0
        )

        # تأثير عند المرور
        def on_enter(e):
            button['bg'] = self._darken_color(color)

        def on_leave(e):
            button['bg'] = color

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

        return button

    def _darken_color(self, color):
        """تغميق اللون"""
        try:
            # إزالة # وتحويل إلى RGB
            color = color.lstrip('#')
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            # تغميق بنسبة 20%
            r = int(r * 0.8)
            g = int(g * 0.8)
            b = int(b * 0.8)
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return color

    def _create_programs_table(self, parent):
        """إنشاء جدول البرامج"""
        # إطار الجدول
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True)

        # شريط التمرير
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        # الجدول
        columns = ('program_name', 'college', 'department', 'coordinator', 'status')

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='tree headings',
            height=20,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # تعريف الأعمدة
        self.tree.heading('#0', text='#')
        self.tree.heading('program_name', text=t("program_name", self.language))
        self.tree.heading('college', text=t("college", self.language))
        self.tree.heading('department', text=t("department", self.language))
        self.tree.heading('coordinator', text=t("program_coordinator", self.language))
        self.tree.heading('status', text=t("status", self.language))

        # عرض الأعمدة
        self.tree.column('#0', width=50, anchor='center')
        self.tree.column('program_name', width=300, anchor='center' if self.language == 'ar' else 'w')
        self.tree.column('college', width=200, anchor='center' if self.language == 'ar' else 'w')
        self.tree.column('department', width=200, anchor='center' if self.language == 'ar' else 'w')
        self.tree.column('coordinator', width=200, anchor='center' if self.language == 'ar' else 'w')
        self.tree.column('status', width=100, anchor='center')

        # حدث النقر المزدوج
        self.tree.bind('<Double-Button-1>', lambda e: self._edit_program())

        # ترتيب العناصر
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _load_programs(self):
        """تحميل البرامج في الجدول"""
        # حذف جميع الصفوف
        for item in self.tree.get_children():
            self.tree.delete(item)

        # تحميل البرامج حسب صلاحيات المستخدم
        current_user = self.access_control.get_current_user()

        if current_user and current_user.has_role('admin'):
            # المدير يرى جميع البرامج
            programs = self.program_manager.get_all_programs()
        elif current_user and current_user.has_role('program_coordinator'):
            # منسق البرنامج يرى البرامج المعينة له فقط
            all_programs = self.program_manager.get_all_programs()
            programs = [p for p in all_programs if p.program_id in current_user.assigned_programs]
        else:
            # المستخدمون الآخرون لا يرون أي برامج
            programs = []

        # الحصول على مدير أعضاء هيئة التدريس
        from managers.faculty_manager import FacultyManager
        faculty_manager = FacultyManager()

        for i, program in enumerate(programs, 1):
            # اسم البرنامج
            program_name = program.program_name_ar if self.language == 'ar' else program.program_name_en

            # الكلية والقسم
            college = program.college_ar if self.language == 'ar' else program.college_en
            department = program.department_ar if self.language == 'ar' else program.department_en

            # المنسق
            coordinator_name = "-"
            if program.coordinator_id:
                # البحث عن المنسق في أعضاء هيئة التدريس
                for member in faculty_manager.get_all_members():
                    if member.faculty_id == program.coordinator_id:
                        coordinator_name = member.name
                        break

            # الحالة
            status = "✅ " + t("active", self.language) if program.is_active else "🔒 " + t("inactive", self.language)

            # إضافة الصف
            self.tree.insert(
                '',
                'end',
                text=str(i),
                values=(program_name, college, department, coordinator_name, status),
                tags=(program.program_id,)
            )

    def _filter_programs(self):
        """تصفية البرامج حسب البحث"""
        query = self.search_var.get().strip()

        if not query:
            self._load_programs()
            return

        # حذف جميع الصفوف
        for item in self.tree.get_children():
            self.tree.delete(item)

        # البحث في البرامج
        programs = self.program_manager.search_programs(query, self.language)

        # الحصول على مدير أعضاء هيئة التدريس
        from managers.faculty_manager import FacultyManager
        faculty_manager = FacultyManager()

        counter = 0
        for program in programs:
            counter += 1

            # اسم البرنامج
            program_name = program.program_name_ar if self.language == 'ar' else program.program_name_en

            # الكلية والقسم
            college = program.college_ar if self.language == 'ar' else program.college_en
            department = program.department_ar if self.language == 'ar' else program.department_en

            # المنسق
            coordinator_name = "-"
            if program.coordinator_id:
                # البحث عن المنسق في أعضاء هيئة التدريس
                for member in faculty_manager.get_all_members():
                    if member.faculty_id == program.coordinator_id:
                        coordinator_name = member.name
                        break

            # الحالة
            status = "✅ " + t("active", self.language) if program.is_active else "🔒 " + t("inactive", self.language)

            # إضافة الصف
            self.tree.insert(
                '',
                'end',
                text=str(counter),
                values=(program_name, college, department, coordinator_name, status),
                tags=(program.program_id,)
            )

    def _get_selected_program(self) -> Optional[AcademicProgram]:
        """الحصول على البرنامج المحدد"""
        selection = self.tree.selection()
        if not selection:
            return None

        item = self.tree.item(selection[0])
        program_id = item['tags'][0] if item['tags'] else None

        if program_id:
            return self.program_manager.get_program(program_id)
        return None

    def _add_program(self):
        """إضافة برنامج جديد"""
        dialog = ProgramEditorDialog(
            self.dialog,
            None,
            self.access_control,
            self.language
        )
        self.dialog.wait_window(dialog.dialog)

        if dialog.result:
            if self.program_manager.create_program(dialog.result):
                messagebox.showinfo(
                    t("success", self.language),
                    t("program_created_success", self.language)
                )
                self._load_programs()
            else:
                messagebox.showerror(
                    t("error", self.language),
                    t("program_create_failed", self.language)
                )

    def _edit_program(self):
        """تعديل برنامج"""
        program = self._get_selected_program()
        if not program:
            messagebox.showwarning(
                t("warning", self.language),
                t("please_select_program", self.language)
            )
            return

        dialog = ProgramEditorDialog(
            self.dialog,
            program,
            self.access_control,
            self.language
        )
        self.dialog.wait_window(dialog.dialog)

        if dialog.result:
            if self.program_manager.update_program(dialog.result):
                messagebox.showinfo(
                    t("success", self.language),
                    t("program_updated_success", self.language)
                )
                self._load_programs()
            else:
                messagebox.showerror(
                    t("error", self.language),
                    t("program_update_failed", self.language)
                )

    def _delete_program(self):
        """حذف برنامج"""
        program = self._get_selected_program()
        if not program:
            messagebox.showwarning(
                t("warning", self.language),
                t("please_select_program", self.language)
            )
            return

        # تأكيد الحذف
        program_name = program.program_name_ar if self.language == 'ar' else program.program_name_en
        confirm = messagebox.askyesno(
            t("confirm_delete", self.language),
            t("confirm_delete_program", self.language) + f"\n\n{program_name}"
        )

        if confirm:
            # استخدام الحذف المتسلسل
            result = self.program_manager.delete_program(program.program_id, cascade=True)

            if result['success']:
                # إنشاء رسالة تفصيلية بنتائج الحذف
                message = t("program_deleted_success", self.language)

                if result['deleted_courses']:
                    courses_text = t("deleted_courses", self.language) if self.language == 'ar' else "Deleted courses"
                    message += f"\n\n{courses_text}: {len(result['deleted_courses'])}"

                if result['deleted_users']:
                    users_text = t("deleted_users", self.language) if self.language == 'ar' else "Deleted users"
                    message += f"\n{users_text}: {len(result['deleted_users'])}"

                if result['errors']:
                    errors_text = t("warnings", self.language) if self.language == 'ar' else "Warnings"
                    message += f"\n\n{errors_text}:\n" + "\n".join(result['errors'])

                messagebox.showinfo(
                    t("success", self.language),
                    message
                )
                self._load_programs()

                # تحديث لوحة التحكم الرئيسية
                if hasattr(self, 'main_window') and self.main_window:
                    self.main_window.refresh_dashboard()
            else:
                error_msg = t("program_delete_failed", self.language)
                if result['errors']:
                    error_msg += "\n\n" + "\n".join(result['errors'])

                messagebox.showerror(
                    t("error", self.language),
                    error_msg
                )

    def _assign_coordinator(self):
        """تعيين منسق للبرنامج"""
        try:
            program = self._get_selected_program()
            if not program:
                messagebox.showwarning(
                    t("warning", self.language),
                    t("please_select_program", self.language)
                )
                return

            # فتح نافذة تعيين المنسق
            dialog = AssignCoordinatorDialog(
                self.dialog,
                program,
                self.program_manager,
                self.access_control,
                self.language
            )

            if dialog.result:
                self._load_programs()
        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"Error opening coordinator assignment dialog: {str(e)}"
            )

    def _show_statistics(self):
        """عرض الإحصائيات"""
        total_programs = self.program_manager.get_program_count()
        active_programs = self.program_manager.get_active_program_count()
        departments = self.program_manager.get_unique_departments(self.language)
        colleges = self.program_manager.get_unique_colleges(self.language)

        if self.language == 'ar':
            stats = f"""
إحصائيات البرامج الأكاديمية:

عدد البرامج الكلي: {total_programs}
البرامج النشطة: {active_programs}
البرامج المعطلة: {total_programs - active_programs}

عدد الكليات: {len(colleges)}
عدد الأقسام: {len(departments)}
            """
        else:
            stats = f"""
Academic Programs Statistics:

Total Programs: {total_programs}
Active Programs: {active_programs}
Inactive Programs: {total_programs - active_programs}

Number of Colleges: {len(colleges)}
Number of Departments: {len(departments)}
            """

        messagebox.showinfo(t("statistics", self.language), stats.strip())


class ProgramEditorDialog:
    """نافذة محرر البرنامج الأكاديمي"""

    def __init__(
        self,
        parent,
        program: Optional[AcademicProgram],
        access_control: AccessControl,
        language: str = 'ar'
    ):
        """تهيئة المحرر"""
        self.parent = parent
        self.program = program
        self.access_control = access_control
        self.language = language
        self.result = None

        # إنشاء النافذة
        self.dialog = tk.Toplevel(parent)
        title = t("edit_program", language) if program else t("new_program", language)
        self.dialog.title(title)
        self.dialog.geometry("700x800")
        self.dialog.configure(bg=COLORS['bg_light'])

        # جعل النافذة في الواجهة
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # الحقول
        self.fields = {}

        # إنشاء الواجهة
        self._create_widgets()

        if program:
            self._fill_program_data()

        # وضع النافذة في المنتصف
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # الإطار الرئيسي
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg_light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # العنوان
        title_text = t("edit_program", self.language) if self.program else t("new_program", self.language)
        title_label = tk.Label(
            main_frame,
            text="🎓 " + title_text,
            font=('Arial', 16, 'bold'),
            bg=COLORS['bg_light'],
            fg=COLORS['primary']
        )
        title_label.pack(pady=(0, 20))

        # إطار الحقول مع شريط تمرير
        canvas = tk.Canvas(main_frame, bg=COLORS['bg_light'])
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_light'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # الحقول
        self._create_field(scrollable_frame, "university_ar", t("university_ar", self.language))
        self._create_field(scrollable_frame, "university_en", t("university_en", self.language))
        self._create_field(scrollable_frame, "college_ar", t("college_ar", self.language))
        self._create_field(scrollable_frame, "college_en", t("college_en", self.language))
        self._create_field(scrollable_frame, "department_ar", t("department_ar", self.language))
        self._create_field(scrollable_frame, "department_en", t("department_en", self.language))
        self._create_field(scrollable_frame, "program_name_ar", t("program_name_ar", self.language))
        self._create_field(scrollable_frame, "program_name_en", t("program_name_en", self.language))
        self._create_field(scrollable_frame, "program_code", t("program_code", self.language))

        # ملاحظة: تم إزالة حقل المنسق من هنا
        # سيتم تعيين المنسق من خلال نافذة منفصلة بعد إضافة أعضاء القسم

        # الوصف
        self._create_description_field(scrollable_frame, "description_ar", t("description_ar", self.language))
        self._create_description_field(scrollable_frame, "description_en", t("description_en", self.language))

        # الحالة
        self._create_status_field(scrollable_frame)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # أزرار الحفظ والإلغاء
        buttons_frame = tk.Frame(main_frame, bg=COLORS['bg_light'])
        buttons_frame.pack(fill=tk.X, pady=(20, 0))

        save_button = tk.Button(
            buttons_frame,
            text="✓ " + t("save", self.language),
            command=self._save,
            font=('Arial', 11, 'bold'),
            bg=COLORS['success'],
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2'
        )
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(
            buttons_frame,
            text="✗ " + t("cancel", self.language),
            command=self.dialog.destroy,
            font=('Arial', 11, 'bold'),
            bg=COLORS['secondary'],
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2'
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)

    def _create_field(self, parent, field_name, label_text):
        """إنشاء حقل إدخال"""
        frame = tk.Frame(parent, bg=COLORS['bg_light'])
        frame.pack(fill=tk.X, pady=8)

        label = tk.Label(
            frame,
            text=label_text + ":",
            font=('Arial', 10, 'bold'),
            bg=COLORS['bg_light'],
            width=20,
            anchor='e' if self.language == 'ar' else 'w'
        )
        label.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

        entry = tk.Entry(
            frame,
            font=('Arial', 10),
            width=40
        )
        entry.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.fields[field_name] = entry

    def _create_description_field(self, parent, field_name, label_text):
        """إنشاء حقل وصف متعدد الأسطر"""
        frame = tk.Frame(parent, bg=COLORS['bg_light'])
        frame.pack(fill=tk.X, pady=8)

        label = tk.Label(
            frame,
            text=label_text + ":",
            font=('Arial', 10, 'bold'),
            bg=COLORS['bg_light'],
            anchor='e' if self.language == 'ar' else 'w'
        )
        label.pack(anchor='e' if self.language == 'ar' else 'w', padx=10)

        text_widget = tk.Text(
            frame,
            font=('Arial', 10),
            width=50,
            height=3,
            wrap=tk.WORD
        )
        text_widget.pack(padx=10, pady=5, fill=tk.X, expand=True)

        self.fields[field_name] = text_widget


    def _create_status_field(self, parent):
        """إنشاء حقل الحالة"""
        frame = tk.Frame(parent, bg=COLORS['bg_light'])
        frame.pack(fill=tk.X, pady=8)

        label = tk.Label(
            frame,
            text=t("status", self.language) + ":",
            font=('Arial', 10, 'bold'),
            bg=COLORS['bg_light'],
            width=20,
            anchor='e' if self.language == 'ar' else 'w'
        )
        label.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

        self.is_active_var = tk.BooleanVar(value=True)
        active_check = tk.Checkbutton(
            frame,
            text=t("active", self.language),
            variable=self.is_active_var,
            font=('Arial', 10),
            bg=COLORS['bg_light']
        )
        active_check.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=10)

    def _fill_program_data(self):
        """ملء بيانات البرنامج للتعديل"""
        if not self.program:
            return

        # الحقول النصية
        text_fields = [
            'university_ar', 'university_en', 'college_ar', 'college_en',
            'department_ar', 'department_en', 'program_name_ar',
            'program_name_en', 'program_code'
        ]

        for field in text_fields:
            value = getattr(self.program, field, '')
            if field in self.fields:
                self.fields[field].insert(0, value)

        # الوصف
        if 'description_ar' in self.fields:
            self.fields['description_ar'].insert('1.0', self.program.description_ar)
        if 'description_en' in self.fields:
            self.fields['description_en'].insert('1.0', self.program.description_en)

        # الحالة
        self.is_active_var.set(self.program.is_active)

    def _save(self):
        """حفظ البرنامج"""
        # التحقق من الحقول المطلوبة
        required_fields = {
            'program_name_ar': t("program_name_ar", self.language),
            'program_name_en': t("program_name_en", self.language)
        }

        for field, label in required_fields.items():
            value = self.fields[field].get().strip()
            if not value:
                messagebox.showerror(
                    t("error", self.language),
                    f"{t('field_required', self.language)}: {label}"
                )
                return

        # إنشاء أو تحديث البرنامج
        if self.program:
            # تحديث
            self.program.university_ar = self.fields['university_ar'].get().strip()
            self.program.university_en = self.fields['university_en'].get().strip()
            self.program.college_ar = self.fields['college_ar'].get().strip()
            self.program.college_en = self.fields['college_en'].get().strip()
            self.program.department_ar = self.fields['department_ar'].get().strip()
            self.program.department_en = self.fields['department_en'].get().strip()
            self.program.program_name_ar = self.fields['program_name_ar'].get().strip()
            self.program.program_name_en = self.fields['program_name_en'].get().strip()
            self.program.program_code = self.fields['program_code'].get().strip()
            # لا نقوم بتحديث المنسق هنا - سيتم من خلال نافذة منفصلة
            self.program.description_ar = self.fields['description_ar'].get('1.0', tk.END).strip()
            self.program.description_en = self.fields['description_en'].get('1.0', tk.END).strip()
            self.program.is_active = self.is_active_var.get()
            self.program.last_modified = datetime.now().isoformat()
            self.result = self.program
        else:
            # إنشاء جديد - بدون منسق
            self.result = AcademicProgram(
                program_name_ar=self.fields['program_name_ar'].get().strip(),
                program_name_en=self.fields['program_name_en'].get().strip(),
                coordinator_id="",  # بدون منسق
                university_ar=self.fields['university_ar'].get().strip(),
                university_en=self.fields['university_en'].get().strip(),
                college_ar=self.fields['college_ar'].get().strip(),
                college_en=self.fields['college_en'].get().strip(),
                department_ar=self.fields['department_ar'].get().strip(),
                department_en=self.fields['department_en'].get().strip()
            )
            self.result.program_code = self.fields['program_code'].get().strip()
            self.result.description_ar = self.fields['description_ar'].get('1.0', tk.END).strip()
            self.result.description_en = self.fields['description_en'].get('1.0', tk.END).strip()
            self.result.is_active = self.is_active_var.get()

        self.dialog.destroy()


class AssignCoordinatorDialog:
    """نافذة تعيين منسق البرنامج"""

    def __init__(self, parent, program, program_manager, access_control=None, language='ar'):
        """
        تهيئة النافذة

        Args:
            parent: النافذة الأب
            program: البرنامج المراد تعيين منسق له
            program_manager: مدير البرامج
            access_control: مدير التحكم بالصلاحيات (اختياري)
            language: لغة الواجهة
        """
        self.parent = parent
        self.program = program
        self.program_manager = program_manager
        self.access_control = access_control
        self.language = language
        self.result = None

        # إنشاء النافذة
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(t("assign_coordinator", language))
        self.dialog.geometry("700x650")
        self.dialog.resizable(True, True)

        # جعل النافذة modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # بناء الواجهة
        self._build_ui()

        # مركزة النافذة
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # انتظار إغلاق النافذة
        self.dialog.wait_window()

    def _build_ui(self):
        """بناء واجهة المستخدم"""
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg_light'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # العنوان
        title_text = t("assign_coordinator", self.language)
        tk.Label(
            main_frame,
            text=title_text,
            font=('Arial', 14, 'bold'),
            bg=COLORS['bg_light'],
            fg=COLORS['primary']
        ).pack(pady=(0, 15))

        # معلومات البرنامج
        info_frame = tk.LabelFrame(
            main_frame,
            text=t("program_info", self.language),
            font=('Arial', 10, 'bold'),
            bg=COLORS['bg_light'],
            padx=15,
            pady=10
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))

        program_name = self.program.program_name_ar if self.language == 'ar' else self.program.program_name_en
        department = self.program.department_ar if self.language == 'ar' else self.program.department_en
        college = self.program.college_ar if self.language == 'ar' else self.program.college_en

        tk.Label(
            info_frame,
            text=f"{t('program_name', self.language)}: {program_name}",
            font=('Arial', 10),
            bg=COLORS['bg_light'],
            anchor='e' if self.language == 'ar' else 'w'
        ).pack(fill=tk.X, pady=2)

        tk.Label(
            info_frame,
            text=f"{t('college', self.language)}: {college}",
            font=('Arial', 10),
            bg=COLORS['bg_light'],
            anchor='e' if self.language == 'ar' else 'w'
        ).pack(fill=tk.X, pady=2)

        tk.Label(
            info_frame,
            text=f"{t('department', self.language)}: {department}",
            font=('Arial', 10),
            bg=COLORS['bg_light'],
            anchor='e' if self.language == 'ar' else 'w'
        ).pack(fill=tk.X, pady=2)

        # قائمة أعضاء القسم
        faculty_frame = tk.LabelFrame(
            main_frame,
            text=t("select_coordinator_for_program", self.language),
            font=('Arial', 10, 'bold'),
            bg=COLORS['bg_light'],
            padx=15,
            pady=10
        )
        faculty_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # الحصول على أعضاء القسم
        from managers.faculty_manager import FacultyManager
        faculty_manager = FacultyManager()

        self.faculty_members = faculty_manager.get_members_by_department(
            self.program.department_ar,
            active_only=True
        )

        if not self.faculty_members:
            tk.Label(
                faculty_frame,
                text=t("no_faculty_in_department", self.language),
                font=('Arial', 10),
                bg=COLORS['bg_light'],
                fg=COLORS['danger']
            ).pack(pady=20)
            return

        # جدول الأعضاء
        columns = ('employee_id', 'name', 'degree')
        self.tree = ttk.Treeview(
            faculty_frame,
            columns=columns,
            show='headings',
            selectmode='browse',
            height=12
        )

        # تعريف الأعمدة
        if self.language == 'ar':
            self.tree.heading('employee_id', text='الرقم الوظيفي')
            self.tree.heading('name', text='الاسم')
            self.tree.heading('degree', text='الدرجة العلمية')
        else:
            self.tree.heading('employee_id', text='Employee ID')
            self.tree.heading('name', text='Name')
            self.tree.heading('degree', text='Academic Degree')

        self.tree.column('employee_id', width=100, anchor='center')
        self.tree.column('name', width=250)
        self.tree.column('degree', width=200)

        # إضافة البيانات
        for member in self.faculty_members:
            self.tree.insert('', tk.END, values=(
                member.employee_id,
                member.name,
                member.academic_degree
            ))

        # Scrollbar
        scrollbar = ttk.Scrollbar(faculty_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # تحديد المنسق الحالي إن وُجد
        if self.program.coordinator_id:
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                # البحث عن العضو بالـ faculty_id
                for member in self.faculty_members:
                    if member.faculty_id == self.program.coordinator_id and member.employee_id == str(values[0]):
                        self.tree.selection_set(item)
                        self.tree.see(item)
                        break

        # الأزرار
        buttons_frame = tk.Frame(main_frame, bg=COLORS['bg_light'])
        buttons_frame.pack(fill=tk.X)

        tk.Button(
            buttons_frame,
            text="✓ " + t("assign", self.language),
            command=self._assign,
            bg=COLORS['success'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5,
            relief='flat',
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="✗ " + t("cancel", self.language),
            command=self.dialog.destroy,
            bg=COLORS['secondary'],
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5,
            relief='flat',
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

    def _assign(self):
        """تعيين المنسق المحدد"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                t("select_member_first", self.language),
                parent=self.dialog
            )
            return

        # الحصول على بيانات العضو المحدد
        values = self.tree.item(selection[0])['values']
        employee_id = str(values[0])  # تحويل إلى نص للتأكد من المطابقة

        # البحث عن العضو
        selected_member = None
        for member in self.faculty_members:
            if member.employee_id == employee_id:
                selected_member = member
                break

        if not selected_member:
            messagebox.showerror(
                t("error", self.language),
                t("member_not_found", self.language),
                parent=self.dialog
            )
            return

        # تحديث البرنامج
        self.program.coordinator_id = selected_member.faculty_id
        self.program.last_modified = datetime.now().isoformat()

        # إنشاء أو تحديث حساب المستخدم إذا كان access_control متاح
        user_created = False
        username = ""
        password = ""

        if self.access_control:
            from models.user import User

            # التحقق من وجود حساب للعضو
            existing_user = self.access_control.get_user_by_faculty_id(selected_member.faculty_id)

            if existing_user:
                # إضافة دور منسق البرنامج إذا لم يكن موجوداً
                if 'program_coordinator' not in existing_user.roles:
                    existing_user.add_role('program_coordinator')
                    self.access_control.save_users()
                    username = existing_user.username
                    password = "[كلمة المرور الحالية]"

                # ربط المستخدم بالبرنامج الأكاديمي
                self.access_control.assign_user_to_program(existing_user.user_id, self.program.program_id)
            else:
                # إنشاء حساب جديد
                username = User.generate_username(selected_member.name, selected_member.employee_id)
                password = User.generate_password(selected_member.employee_id)

                new_user = self.access_control.create_user_from_faculty(
                    selected_member,
                    roles=['program_coordinator']
                )

                if new_user:
                    user_created = True
                    # ربط المستخدم الجديد بالبرنامج الأكاديمي
                    self.access_control.assign_user_to_program(new_user.user_id, self.program.program_id)

        # حفظ التغييرات
        if self.program_manager.update_program(self.program):
            success_message = t("coordinator_assigned", self.language)

            # إضافة معلومات الحساب إلى الرسالة
            if user_created and username and password:
                if self.language == 'ar':
                    success_message += f"\n\n✅ تم إنشاء حساب مستخدم:\n"
                    success_message += f"اسم المستخدم: {username}\n"
                    success_message += f"كلمة المرور: {password}\n\n"
                    success_message += "⚠️ يُرجى حفظ هذه المعلومات!"
                else:
                    success_message += f"\n\n✅ User account created:\n"
                    success_message += f"Username: {username}\n"
                    success_message += f"Password: {password}\n\n"
                    success_message += "⚠️ Please save this information!"

            messagebox.showinfo(
                t("success", self.language),
                success_message,
                parent=self.dialog
            )
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror(
                t("error", self.language),
                t("coordinator_assignment_failed", self.language),
                parent=self.dialog
            )
