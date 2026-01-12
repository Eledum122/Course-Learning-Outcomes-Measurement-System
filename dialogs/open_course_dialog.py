import tkinter as tk
from tkinter import ttk, messagebox
from managers.course_manager import CourseManager
from translations import t, get_language
from dialogs.stage1_course_dialog import Stage1CourseDialog
from config import FONTS


class OpenCourseDialog(tk.Toplevel):
    """حوار اختيار وفتح مقرر"""

    def __init__(self, parent, course_manager: CourseManager, current_user, language=None, select_only=False, access_control=None):
        super().__init__(parent)
        self.parent = parent
        self.course_manager = course_manager
        self.current_user = current_user
        self.access_control = access_control
        self.language = language or get_language()
        self.selected_course_id = None
        self.select_only = select_only  # إذا True، فقط اختيار المقرر بدون فتحه

        title_text = t('select_course', self.language) if select_only else t('open_course', self.language)
        self.title(title_text)
        self.geometry('1100x550')
        self.transient(parent)
        self.grab_set()

        # تعيين لون الخلفية
        self.configure(bg='#F8F9FA')

        self.create_widgets()
        self.load_courses()

        # توسيط النافذة
        self.center_window()

    def center_window(self):
        """توسيط النافذة على الشاشة"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        is_rtl = (self.language == 'ar')

        # إطار رئيسي بلون خلفية
        main_frame = tk.Frame(self, bg='#F8F9FA')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # ═══════════════════════════════════════════════════════════
        # إطار البحث - بألوان جذابة
        # ═══════════════════════════════════════════════════════════
        search_frame = tk.LabelFrame(main_frame,
                                    text=t('search', self.language),
                                    font=FONTS['arabic_header'] if is_rtl else FONTS['english_header'],
                                    bg='#E3F2FD', fg='#1565C0',
                                    bd=2, relief=tk.GROOVE)
        search_frame.pack(fill='x', pady=(0, 15))

        # محتوى البحث
        search_content = tk.Frame(search_frame, bg='#E3F2FD')
        search_content.pack(fill='x', padx=15, pady=15)

        # حقل البحث
        search_label = tk.Label(search_content,
                               text=t('search', self.language) + ":",
                               font=FONTS['normal'],
                               bg='#E3F2FD', fg='#1565C0')

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_content,
                                textvariable=self.search_var,
                                font=FONTS['normal'],
                                width=50)
        search_entry.bind('<KeyRelease>', lambda e: self.load_courses())

        clear_btn = tk.Button(search_content,
                             text=t('clear', self.language),
                             font=FONTS['normal'],
                             bg='#FF9800', fg='#FFFFFF',
                             relief=tk.FLAT,
                             cursor='hand2',
                             padx=20, pady=8,
                             command=self.clear_search)

        # ترتيب حسب الاتجاه
        if is_rtl:
            clear_btn.pack(side=tk.LEFT, padx=5)
            search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
            search_label.pack(side=tk.LEFT, padx=5)
        else:
            search_label.pack(side=tk.LEFT, padx=5)
            search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
            clear_btn.pack(side=tk.LEFT, padx=5)

        # ═══════════════════════════════════════════════════════════
        # إطار الجدول - بألوان جذابة
        # ═══════════════════════════════════════════════════════════
        table_frame = tk.LabelFrame(main_frame,
                                   text=t('courses_list', self.language) if hasattr(self, 'language') else "قائمة المقررات / Courses List",
                                   font=FONTS['arabic_header'] if is_rtl else FONTS['english_header'],
                                   bg='#E8F5E9', fg='#2E7D32',
                                   bd=2, relief=tk.GROOVE)
        table_frame.pack(fill='both', expand=True, pady=(0, 15))

        # إنشاء Treeview بدون عمود semester
        cols = ('course_id', 'course_code', 'course_title', 'program', 'academic_year')

        # تنسيق الجدول
        style = ttk.Style()
        style.configure("OpenCourse.Treeview",
                       background="#FFFFFF",
                       foreground="#2E7D32",
                       rowheight=30,
                       fieldbackground="#FFFFFF",
                       font=FONTS['normal'])
        style.map('OpenCourse.Treeview',
                 background=[('selected', '#A5D6A7')])  # أخضر عند التحديد
        style.configure("OpenCourse.Treeview.Heading",
                       font=FONTS['arabic_header'] if is_rtl else FONTS['english_header'],
                       background="#66BB6A",
                       foreground="#FFFFFF")

        self.tree = ttk.Treeview(table_frame,
                                columns=cols,
                                show='headings',
                                height=7,
                                style="OpenCourse.Treeview")

        # تعريف العناوين
        headers = {
            'course_id': 'ID',
            'course_code': t('course_code', self.language),
            'course_title': t('course_title', self.language),
            'program': t('program', self.language),
            'academic_year': t('academic_year', self.language)
        }

        for c in cols:
            self.tree.heading(c, text=headers[c])
            if c == 'course_title':
                self.tree.column(c, width=350)
            elif c == 'course_id':
                self.tree.column(c, width=150)
            elif c == 'program':
                self.tree.column(c, width=200)
            else:
                self.tree.column(c, width=150)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', pady=10)
        hsb.grid(row=1, column=0, sticky='ew', padx=10)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # ═══════════════════════════════════════════════════════════
        # إطار الأزرار - بألوان جذابة
        # ═══════════════════════════════════════════════════════════
        btn_frame = tk.Frame(main_frame, bg='#F8F9FA')
        btn_frame.pack(fill='x', pady=(10, 0))

        # ترتيب الأزرار حسب الاتجاه
        if is_rtl:
            # العربية: الحذف على اليسار
            delete_btn = tk.Button(btn_frame,
                                  text="🗑️ " + t('delete', self.language),
                                  font=FONTS['normal'],
                                  bg='#F44336', fg='#FFFFFF',
                                  relief=tk.FLAT,
                                  cursor='hand2',
                                  padx=20, pady=10,
                                  command=self.delete_selected)
            delete_btn.pack(side=tk.LEFT, padx=5)

            cancel_btn = tk.Button(btn_frame,
                                  text=t('cancel', self.language),
                                  font=FONTS['normal'],
                                  bg='#9E9E9E', fg='#FFFFFF',
                                  relief=tk.FLAT,
                                  cursor='hand2',
                                  padx=20, pady=10,
                                  command=self.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=5)

            refresh_btn = tk.Button(btn_frame,
                                   text="🔄 " + t('refresh', self.language),
                                   font=FONTS['normal'],
                                   bg='#FF9800', fg='#FFFFFF',
                                   relief=tk.FLAT,
                                   cursor='hand2',
                                   padx=20, pady=10,
                                   command=self.load_courses)
            refresh_btn.pack(side=tk.LEFT, padx=5)

            # زر الفتح/الاختيار
            if self.select_only:
                btn_text = "✅ " + ("اختيار" if self.language == 'ar' else "Select")
            else:
                btn_text = "📂 " + t('open_course', self.language)

            open_btn = tk.Button(btn_frame,
                                text=btn_text,
                                font=FONTS['normal'],
                                bg='#4CAF50', fg='#FFFFFF',
                                relief=tk.FLAT,
                                cursor='hand2',
                                padx=20, pady=10,
                                command=self.open_selected)
            open_btn.pack(side=tk.LEFT, padx=5)
        else:
            # الإنجليزية: الفتح على اليمين
            # زر الفتح/الاختيار
            if self.select_only:
                btn_text = "✅ " + ("اختيار" if self.language == 'ar' else "Select")
            else:
                btn_text = "📂 " + t('open_course', self.language)

            open_btn = tk.Button(btn_frame,
                                text=btn_text,
                                font=FONTS['normal'],
                                bg='#4CAF50', fg='#FFFFFF',
                                relief=tk.FLAT,
                                cursor='hand2',
                                padx=20, pady=10,
                                command=self.open_selected)
            open_btn.pack(side=tk.RIGHT, padx=5)

            refresh_btn = tk.Button(btn_frame,
                                   text="🔄 " + t('refresh', self.language),
                                   font=FONTS['normal'],
                                   bg='#FF9800', fg='#FFFFFF',
                                   relief=tk.FLAT,
                                   cursor='hand2',
                                   padx=20, pady=10,
                                   command=self.load_courses)
            refresh_btn.pack(side=tk.RIGHT, padx=5)

            cancel_btn = tk.Button(btn_frame,
                                  text=t('cancel', self.language),
                                  font=FONTS['normal'],
                                  bg='#9E9E9E', fg='#FFFFFF',
                                  relief=tk.FLAT,
                                  cursor='hand2',
                                  padx=20, pady=10,
                                  command=self.destroy)
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            delete_btn = tk.Button(btn_frame,
                                  text="🗑️ " + t('delete', self.language),
                                  font=FONTS['normal'],
                                  bg='#F44336', fg='#FFFFFF',
                                  relief=tk.FLAT,
                                  cursor='hand2',
                                  padx=20, pady=10,
                                  command=self.delete_selected)
            delete_btn.pack(side=tk.RIGHT, padx=5)

    def load_courses(self):
        """Load and optionally filter courses based on search and user permissions."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            # تحميل جميع المقررات
            all_courses = self.course_manager.list_all_courses()

            # تصفية المقررات حسب صلاحيات المستخدم
            if self.current_user.has_role('admin'):
                # المدير يرى جميع المقررات
                courses = all_courses
            elif self.current_user.has_role('program_coordinator'):
                # منسق البرنامج يرى مقررات برامجه فقط
                # نحتاج للحصول على أسماء البرامج من معرفاتها
                from managers.academic_program_manager import AcademicProgramManager
                program_manager = AcademicProgramManager()

                # الحصول على أسماء البرامج المعينة
                assigned_program_names = []
                for program_id in self.current_user.assigned_programs:
                    program = program_manager.get_program(program_id)
                    if program:
                        assigned_program_names.append(program.program_name_ar)
                        assigned_program_names.append(program.program_name_en)

                # تصفية المقررات
                courses = [c for c in all_courses if c.get('program', '') in assigned_program_names]
            elif self.current_user.has_role('course_coordinator'):
                # منسق المقرر يرى مقرراته فقط
                courses = [c for c in all_courses if c['course_id'] in self.current_user.assigned_courses]
            elif self.current_user.has_role('section_instructor'):
                # مدرس الشعبة يرى المقررات التي له فيها شعب
                course_ids = list(self.current_user.assigned_sections.keys())
                courses = [c for c in all_courses if c['course_id'] in course_ids]
            else:
                # المستخدمون الآخرون لا يرون أي مقررات
                courses = []

            # تطبيق البحث
            query = self.search_var.get().strip().lower() if getattr(self, 'search_var', None) else ''
            for c in courses:
                if query:
                    if query in (c.get('course_code','') or '').lower() or \
                       query in (c.get('course_title','') or '').lower() or \
                       query in (c.get('program','') or '').lower():
                        self.tree.insert('', 'end', values=(
                            c['course_id'],
                            c['course_code'],
                            c['course_title'],
                            c['program'],
                            c['academic_year']
                        ))
                else:
                    self.tree.insert('', 'end', values=(
                        c['course_id'],
                        c['course_code'],
                        c['course_title'],
                        c['program'],
                        c['academic_year']
                    ))
        except Exception as e:
            messagebox.showerror(t('error', self.language), str(e), parent=self)

    def clear_search(self):
        """Clear the search entry and reload the list."""
        if getattr(self, 'search_var', None):
            self.search_var.set('')
        self.load_courses()

    def open_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(t('warning', self.language), t('select_course_to_open', self.language), parent=self)
            return
        item = self.tree.item(sel[0])
        course_id = item['values'][0]
        try:
            # حفظ المعرف
            self.selected_course_id = course_id

            if self.select_only:
                # وضع الاختيار فقط: إغلاق النافذة فوراً
                self.destroy()
            else:
                # وضع الفتح: إغلاق النافذة وفتح نافذة المرحلة الأولى
                self.destroy()
                dlg = Stage1CourseDialog(self.parent, self.course_manager, self.current_user, course_id=course_id, language=self.language, access_control=self.access_control)
                self.parent.wait_window(dlg)
        except Exception as e:
            messagebox.showerror(t('error', self.language), str(e), parent=self)

    def delete_selected(self):
        """حذف المقرر المحدد مع رسالة تحذير"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(
                t('warning', self.language),
                "الرجاء تحديد مقرر للحذف / Please select a course to delete",
                parent=self
            )
            return

        item = self.tree.item(sel[0])
        course_id = item['values'][0]
        course_code = item['values'][1]
        course_title = item['values'][2]

        # رسالة تحذير بلغتين
        msg_ar = f"⚠️ تحذير!\n\nهل أنت متأكد من حذف المقرر التالي؟\n\n" \
                f"الكود: {course_code}\n" \
                f"العنوان: {course_title}\n" \
                f"المعرف: {course_id}\n\n" \
                f"سيتم حذف جميع البيانات المرتبطة بهذا المقرر نهائياً!\n" \
                f"هذا الإجراء لا يمكن التراجع عنه!"

        msg_en = f"⚠️ Warning!\n\nAre you sure you want to delete this course?\n\n" \
                f"Code: {course_code}\n" \
                f"Title: {course_title}\n" \
                f"ID: {course_id}\n\n" \
                f"All data related to this course will be permanently deleted!\n" \
                f"This action cannot be undone!"

        # عرض رسالة التحذير
        confirm = messagebox.askyesno(
            "حذف المقرر / Delete Course",
            msg_ar if self.language == 'ar' else msg_en,
            parent=self,
            icon='warning'
        )

        if confirm:
            # تأكيد نهائي
            final_confirm = messagebox.askyesno(
                "تأكيد نهائي / Final Confirmation",
                "هل أنت متأكد تماماً؟ / Are you absolutely sure?",
                parent=self,
                icon='warning'
            )

            if final_confirm:
                try:
                    # حذف المقرر مع الحذف المتسلسل
                    result = self.course_manager.delete_course_cascade(course_id)

                    if result['success']:
                        # إنشاء رسالة تفصيلية
                        success_msg = f"تم حذف المقرر بنجاح / Course deleted successfully\n{course_code}"

                        if result['deleted_users']:
                            users_count = len(result['deleted_users'])
                            success_msg += f"\n\nتم حذف {users_count} مستخدم مرتبط / {users_count} related user(s) deleted"

                        if result['errors']:
                            success_msg += "\n\nتحذيرات / Warnings:\n" + "\n".join(result['errors'])

                        messagebox.showinfo(
                            t('success', self.language) if hasattr(self, 'language') else "نجح / Success",
                            success_msg,
                            parent=self
                        )

                        # إعادة تحميل القائمة
                        self.load_courses()
                    else:
                        error_msg = f"فشل حذف المقرر / Failed to delete course:\n{course_code}"
                        if result['errors']:
                            error_msg += "\n\n" + "\n".join(result['errors'])

                        messagebox.showerror(
                            t('error', self.language),
                            error_msg,
                            parent=self
                        )

                except Exception as e:
                    messagebox.showerror(
                        t('error', self.language),
                        f"فشل حذف المقرر / Failed to delete course:\n{str(e)}",
                        parent=self
                    )
