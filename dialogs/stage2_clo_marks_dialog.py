"""
نافذة المرحلة الثانية - توزيع الدرجات على مخرجات التعلم
Stage 2 Dialog - CLO Marks Distribution
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from datetime import datetime

from models.course import Course, CLO
from managers.course_manager import CourseManager
from translations import t, get_language
from config import COLORS, FONTS


class Stage2CLOMarksDialog(tk.Toplevel):
    """نافذة توزيع الدرجات على مخرجات التعلم - المرحلة الثانية"""

    def __init__(self, parent, course_manager: CourseManager, current_user, course_id: str, language: str = 'ar'):
        super().__init__(parent)
        self.parent = parent
        self.course_manager = course_manager
        self.current_user = current_user
        self.course_id = course_id
        self.language = language
        self.course: Optional[Course] = None
        self.is_dirty = False

        # تحميل المقرر
        self.course = self.course_manager.load_course(self.course_id)
        if not self.course:
            messagebox.showerror(
                t("error", language),
                t("error_loading_course", language),
                parent=parent
            )
            self.destroy()
            return

        # التحقق من وجود مخرجات تعلم
        if not self.course.clos:
            msg_ar = "المقرر لا يحتوي على مخرجات تعلم!\n\nالرجاء إضافة مخرجات التعلم أولاً في المرحلة الأولى."
            msg_en = "Course has no learning outcomes!\n\nPlease add CLOs in Stage 1 first."
            messagebox.showerror(
                t("error", language),
                msg_ar if language == 'ar' else msg_en,
                parent=parent
            )
            self.destroy()
            return

        # إعداد النافذة
        title_text = "المرحلة الثانية - توزيع الدرجات على المخرجات" if language == 'ar' else "Stage 2 - CLO Marks Distribution"
        self.title(title_text)

        # حجم النافذة
        window_width = 1000
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        self.transient(parent)
        self.configure(bg='#F8F9FA')

        # منع إغلاق النافذة بالضغط على X بدون حفظ
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # إنشاء الواجهة
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        is_rtl = (self.language == 'ar')

        # ═══════════════════════════════════════════════════════════
        # العنوان الرئيسي
        # ═══════════════════════════════════════════════════════════
        header_frame = tk.Frame(self, bg=COLORS['primary_blue'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_text = f"المرحلة الثانية: توزيع الدرجات - {self.course.info.course_code}" if is_rtl else f"Stage 2: Marks Distribution - {self.course.info.course_code}"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            bg=COLORS['primary_blue'],
            fg='white',
            font=FONTS['arabic_header'] if is_rtl else FONTS['english_header']
        )
        title_label.pack(side=tk.RIGHT if is_rtl else tk.LEFT, padx=20, pady=20)

        # ═══════════════════════════════════════════════════════════
        # المحتوى الرئيسي
        # ═══════════════════════════════════════════════════════════
        main_frame = tk.Frame(self, bg='#F8F9FA')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # القسم الأول: معلومات المقرر
        self.create_course_info_section(main_frame, is_rtl)

        # القسم الثاني: جدول توزيع الدرجات
        self.create_marks_table_section(main_frame, is_rtl)

        # القسم الثالث: أزرار التحكم
        self.create_control_buttons(main_frame, is_rtl)

    def create_course_info_section(self, parent, is_rtl):
        """قسم معلومات المقرر والدرجة الكلية"""
        info_frame = tk.LabelFrame(
            parent,
            text="  " + ("معلومات المقرر" if is_rtl else "Course Information") + "  ",
            bg='#E3F2FD',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            fg=COLORS['primary_blue']
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))

        # Grid داخل الإطار
        content_frame = tk.Frame(info_frame, bg='#E3F2FD')
        content_frame.pack(fill=tk.X, padx=15, pady=15)

        row = 0

        # اسم المقرر
        tk.Label(
            content_frame,
            text=("اسم المقرر:" if is_rtl else "Course Title:"),
            bg='#E3F2FD',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            anchor='e' if is_rtl else 'w'
        ).grid(row=row, column=1 if is_rtl else 0, sticky='e' if is_rtl else 'w', padx=10, pady=5)

        tk.Label(
            content_frame,
            text=self.course.info.course_title,
            bg='#E3F2FD',
            font=FONTS['arabic'] if is_rtl else FONTS['normal'],
            anchor='e' if is_rtl else 'w'
        ).grid(row=row, column=0 if is_rtl else 1, sticky='ew', padx=10, pady=5)

        row += 1

        # الدرجة الكلية للمقرر
        tk.Label(
            content_frame,
            text=("الدرجة الكلية للمقرر:" if is_rtl else "Total Course Mark:"),
            bg='#E3F2FD',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            anchor='e' if is_rtl else 'w'
        ).grid(row=row, column=1 if is_rtl else 0, sticky='e' if is_rtl else 'w', padx=10, pady=5)

        self.total_mark_var = tk.DoubleVar(value=self.course.info.total_mark)
        total_mark_entry = tk.Entry(
            content_frame,
            textvariable=self.total_mark_var,
            font=FONTS['normal'],
            width=15,
            justify='center'
        )
        total_mark_entry.grid(row=row, column=0 if is_rtl else 1, sticky='w' if is_rtl else 'e', padx=10, pady=5)
        total_mark_entry.bind('<KeyRelease>', self.mark_dirty)

        row += 1

        # نسبة النجاح
        tk.Label(
            content_frame,
            text=("نسبة النجاح في المقرر (%):" if is_rtl else "Passing Percentage (%):"),
            bg='#E3F2FD',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            anchor='e' if is_rtl else 'w'
        ).grid(row=row, column=1 if is_rtl else 0, sticky='e' if is_rtl else 'w', padx=10, pady=5)

        self.passing_percentage_var = tk.DoubleVar(value=self.course.info.passing_percentage)
        passing_entry = tk.Entry(
            content_frame,
            textvariable=self.passing_percentage_var,
            font=FONTS['normal'],
            width=15,
            justify='center'
        )
        passing_entry.grid(row=row, column=0 if is_rtl else 1, sticky='w' if is_rtl else 'e', padx=10, pady=5)
        passing_entry.bind('<KeyRelease>', self.mark_dirty)

        # توسيع العمود الثاني
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

    def create_marks_table_section(self, parent, is_rtl):
        """قسم جدول توزيع الدرجات"""
        table_frame = tk.LabelFrame(
            parent,
            text="  " + ("توزيع الدرجات على مخرجات التعلم" if is_rtl else "CLO Marks Distribution") + "  ",
            bg='#F3E5F5',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            fg='#6A1B9A'
        )
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # إنشاء Treeview
        columns = ('code', 'category', 'description', 'mark', 'criterion', 'target')

        if is_rtl:
            headers = ['المستوى المستهدف %', 'معيار النجاح %', 'الدرجة', 'الوصف', 'الفئة', 'الكود']
        else:
            headers = ['Code', 'Category', 'Description', 'Mark', 'Criterion %', 'Target %']

        tree_container = tk.Frame(table_frame, bg='#F3E5F5')
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_container, orient='vertical')
        h_scroll = ttk.Scrollbar(tree_container, orient='horizontal')

        self.clo_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show='headings',
            height=10,
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        v_scroll.config(command=self.clo_tree.yview)
        h_scroll.config(command=self.clo_tree.xview)

        # تعيين العناوين
        for i, col in enumerate(columns):
            idx = len(columns) - 1 - i if is_rtl else i
            self.clo_tree.heading(col, text=headers[idx])

        # تعيين عرض الأعمدة
        self.clo_tree.column('code', width=80, anchor='center')
        self.clo_tree.column('category', width=100, anchor='center')
        self.clo_tree.column('description', width=300, anchor='e' if is_rtl else 'w')
        self.clo_tree.column('mark', width=100, anchor='center')
        self.clo_tree.column('criterion', width=120, anchor='center')
        self.clo_tree.column('target', width=120, anchor='center')

        # Grid layout
        self.clo_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # ربط حدث النقر المزدوج
        self.clo_tree.bind('<Double-Button-1>', self.edit_clo_marks)

        # تسمية توضيحية
        hint_text = "💡 انقر نقراً مزدوجاً على مخرج لتعديل الدرجات" if is_rtl else "💡 Double-click on a CLO to edit marks"
        tk.Label(
            table_frame,
            text=hint_text,
            bg='#F3E5F5',
            font=FONTS['small'],
            fg='#6A1B9A'
        ).pack(pady=(0, 10))

        # عرض مجموع الدرجات
        summary_frame = tk.Frame(table_frame, bg='#F3E5F5')
        summary_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.total_label = tk.Label(
            summary_frame,
            text="",
            bg='#F3E5F5',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            fg=COLORS['primary_blue']
        )
        self.total_label.pack(side=tk.RIGHT if is_rtl else tk.LEFT, padx=10)

    def create_control_buttons(self, parent, is_rtl):
        """أزرار التحكم"""
        btn_frame = tk.Frame(parent, bg='#F8F9FA')
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        if is_rtl:
            # زر الحفظ
            save_btn = tk.Button(
                btn_frame,
                text="💾 " + t("save", self.language),
                command=self.save_marks,
                bg='#4CAF50',
                fg='white',
                font=FONTS['arabic_bold'],
                width=20,
                height=2,
                relief=tk.RAISED,
                cursor='hand2'
            )
            save_btn.pack(side=tk.RIGHT, padx=5)

            # زر الإلغاء
            cancel_btn = tk.Button(
                btn_frame,
                text="❌ " + t("cancel", self.language),
                command=self.on_close,
                bg='#9E9E9E',
                fg='white',
                font=FONTS['arabic_bold'],
                width=20,
                height=2,
                relief=tk.RAISED,
                cursor='hand2'
            )
            cancel_btn.pack(side=tk.RIGHT, padx=5)
        else:
            # زر الإلغاء
            cancel_btn = tk.Button(
                btn_frame,
                text="❌ " + t("cancel", self.language),
                command=self.on_close,
                bg='#9E9E9E',
                fg='white',
                font=FONTS['bold'],
                width=20,
                height=2,
                relief=tk.RAISED,
                cursor='hand2'
            )
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            # زر الحفظ
            save_btn = tk.Button(
                btn_frame,
                text="💾 " + t("save", self.language),
                command=self.save_marks,
                bg='#4CAF50',
                fg='white',
                font=FONTS['bold'],
                width=20,
                height=2,
                relief=tk.RAISED,
                cursor='hand2'
            )
            save_btn.pack(side=tk.RIGHT, padx=5)

    def load_data(self):
        """تحميل البيانات إلى الجدول"""
        # مسح الجدول
        for item in self.clo_tree.get_children():
            self.clo_tree.delete(item)

        # إضافة البيانات
        for clo in self.course.clos:
            category_ar = {
                'Knowledge': 'المعرفة',
                'Skills': 'المهارات',
                'Values': 'القيم'
            }.get(clo.category.value if hasattr(clo.category, 'value') else clo.category, str(clo.category))

            category_text = category_ar if self.language == 'ar' else (clo.category.value if hasattr(clo.category, 'value') else clo.category)

            self.clo_tree.insert('', 'end', values=(
                clo.code,
                category_text,
                clo.description,
                f"{clo.mark:.1f}",
                f"{clo.criterion_for_success:.1f}",
                f"{clo.target_level:.1f}"
            ))

        self.update_total()

    def update_total(self):
        """تحديث مجموع الدرجات"""
        total = sum(clo.mark for clo in self.course.clos)
        target_total = self.total_mark_var.get()

        if abs(total - target_total) < 0.01:
            color = '#4CAF50'  # أخضر
            status = "✅"
        else:
            color = '#F44336'  # أحمر
            status = "⚠️"

        if self.language == 'ar':
            text = f"{status} مجموع الدرجات: {total:.1f} / {target_total:.1f}"
        else:
            text = f"{status} Total Marks: {total:.1f} / {target_total:.1f}"

        self.total_label.config(text=text, fg=color)

    def edit_clo_marks(self, event):
        """تحرير درجات المخرج"""
        selection = self.clo_tree.selection()
        if not selection:
            return

        item = self.clo_tree.item(selection[0])
        values = item['values']
        clo_code = values[0]

        # البحث عن المخرج
        clo = next((c for c in self.course.clos if c.code == clo_code), None)
        if not clo:
            return

        # فتح نافذة تحرير
        self.open_edit_dialog(clo)

    def open_edit_dialog(self, clo: CLO):
        """فتح نافذة تحرير درجات المخرج"""
        is_rtl = (self.language == 'ar')

        dialog = tk.Toplevel(self)
        dialog.title(f"{t('edit', self.language)} - {clo.code}")
        dialog.geometry('500x400')
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg='#F8F9FA')

        # توسيط النافذة
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')

        # المحتوى
        main_frame = tk.Frame(dialog, bg='#F8F9FA')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # العنوان
        title_text = f"تعديل المخرج: {clo.code}" if is_rtl else f"Edit CLO: {clo.code}"
        tk.Label(
            main_frame,
            text=title_text,
            bg='#F8F9FA',
            font=FONTS['arabic_header'] if is_rtl else FONTS['header'],
            fg=COLORS['primary_blue']
        ).pack(pady=(0, 20))

        # الحقول
        fields_frame = tk.Frame(main_frame, bg='#F8F9FA')
        fields_frame.pack(fill=tk.BOTH, expand=True)

        row = 0

        # الدرجة
        tk.Label(
            fields_frame,
            text=("الدرجة:" if is_rtl else "Mark:"),
            bg='#F8F9FA',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            anchor='e' if is_rtl else 'w'
        ).grid(row=row, column=1 if is_rtl else 0, sticky='e' if is_rtl else 'w', padx=10, pady=10)

        mark_var = tk.DoubleVar(value=clo.mark)
        mark_entry = tk.Entry(
            fields_frame,
            textvariable=mark_var,
            font=FONTS['normal'],
            width=20,
            justify='center'
        )
        mark_entry.grid(row=row, column=0 if is_rtl else 1, sticky='ew', padx=10, pady=10)

        row += 1

        # معيار النجاح
        tk.Label(
            fields_frame,
            text=("معيار النجاح (%):" if is_rtl else "Criterion for Success (%):"),
            bg='#F8F9FA',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            anchor='e' if is_rtl else 'w'
        ).grid(row=row, column=1 if is_rtl else 0, sticky='e' if is_rtl else 'w', padx=10, pady=10)

        criterion_var = tk.DoubleVar(value=clo.criterion_for_success)
        criterion_entry = tk.Entry(
            fields_frame,
            textvariable=criterion_var,
            font=FONTS['normal'],
            width=20,
            justify='center'
        )
        criterion_entry.grid(row=row, column=0 if is_rtl else 1, sticky='ew', padx=10, pady=10)

        row += 1

        # المستوى المستهدف
        tk.Label(
            fields_frame,
            text=("المستوى المستهدف (%):" if is_rtl else "Target Level (%):"),
            bg='#F8F9FA',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            anchor='e' if is_rtl else 'w'
        ).grid(row=row, column=1 if is_rtl else 0, sticky='e' if is_rtl else 'w', padx=10, pady=10)

        target_var = tk.DoubleVar(value=clo.target_level)
        target_entry = tk.Entry(
            fields_frame,
            textvariable=target_var,
            font=FONTS['normal'],
            width=20,
            justify='center'
        )
        target_entry.grid(row=row, column=0 if is_rtl else 1, sticky='ew', padx=10, pady=10)

        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)

        # ملاحظة
        passing_pct = self.passing_percentage_var.get()
        note_text = f"⚠️ ملاحظة: معيار النجاح يجب ألا يقل عن نسبة النجاح في المقرر ({passing_pct:.0f}%)" if is_rtl else f"⚠️ Note: Criterion must not be less than course passing percentage ({passing_pct:.0f}%)"
        tk.Label(
            main_frame,
            text=note_text,
            bg='#F8F9FA',
            font=FONTS['small'],
            fg='#FF6B00',
            wraplength=450,
            justify='right' if is_rtl else 'left'
        ).pack(pady=15)

        # الأزرار
        btn_frame = tk.Frame(main_frame, bg='#F8F9FA')
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        def save_and_close():
            try:
                new_mark = mark_var.get()
                new_criterion = criterion_var.get()
                new_target = target_var.get()

                # التحقق من الصحة
                if new_mark <= 0:
                    raise ValueError(t("mark_must_be_positive", self.language) if self.language == 'ar' else "Mark must be positive")

                if new_criterion < passing_pct:
                    msg = f"معيار النجاح يجب ألا يقل عن {passing_pct:.0f}%" if is_rtl else f"Criterion must be at least {passing_pct:.0f}%"
                    raise ValueError(msg)

                if not (0 <= new_criterion <= 100):
                    raise ValueError("Criterion must be between 0 and 100")

                if not (0 <= new_target <= 100):
                    raise ValueError("Target must be between 0 and 100")

                # حفظ القيم
                clo.mark = new_mark
                clo.criterion_for_success = new_criterion
                clo.target_level = new_target

                self.mark_dirty()
                self.load_data()
                dialog.destroy()

            except ValueError as e:
                messagebox.showerror(t("error", self.language), str(e), parent=dialog)

        if is_rtl:
            tk.Button(
                btn_frame,
                text="💾 " + t("save", self.language),
                command=save_and_close,
                bg='#4CAF50',
                fg='white',
                font=FONTS['arabic_bold'],
                width=15,
                cursor='hand2'
            ).pack(side=tk.RIGHT, padx=5)

            tk.Button(
                btn_frame,
                text="❌ " + t("cancel", self.language),
                command=dialog.destroy,
                bg='#9E9E9E',
                fg='white',
                font=FONTS['arabic_bold'],
                width=15,
                cursor='hand2'
            ).pack(side=tk.RIGHT, padx=5)
        else:
            tk.Button(
                btn_frame,
                text="❌ " + t("cancel", self.language),
                command=dialog.destroy,
                bg='#9E9E9E',
                fg='white',
                font=FONTS['bold'],
                width=15,
                cursor='hand2'
            ).pack(side=tk.RIGHT, padx=5)

            tk.Button(
                btn_frame,
                text="💾 " + t("save", self.language),
                command=save_and_close,
                bg='#4CAF50',
                fg='white',
                font=FONTS['bold'],
                width=15,
                cursor='hand2'
            ).pack(side=tk.RIGHT, padx=5)

    def save_marks(self):
        """حفظ توزيع الدرجات"""
        try:
            # الحصول على القيم
            total_mark = self.total_mark_var.get()
            passing_pct = self.passing_percentage_var.get()

            # التحقق من الصحة
            if total_mark <= 0:
                raise ValueError("الدرجة الكلية يجب أن تكون أكبر من صفر" if self.language == 'ar' else "Total mark must be positive")

            if not (0 <= passing_pct <= 100):
                raise ValueError("نسبة النجاح يجب أن تكون بين 0 و 100" if self.language == 'ar' else "Passing percentage must be between 0 and 100")

            # التحقق من مجموع الدرجات
            total_clo_marks = sum(clo.mark for clo in self.course.clos)
            if abs(total_clo_marks - total_mark) > 0.01:
                msg_ar = f"⚠️ تحذير!\n\nمجموع درجات المخرجات ({total_clo_marks:.1f}) لا يساوي الدرجة الكلية ({total_mark:.1f})\n\nالرجاء التأكد من توزيع الدرجات بشكل صحيح."
                msg_en = f"⚠️ Warning!\n\nSum of CLO marks ({total_clo_marks:.1f}) does not equal total mark ({total_mark:.1f})\n\nPlease ensure marks are distributed correctly."
                raise ValueError(msg_ar if self.language == 'ar' else msg_en)

            # التحقق من معايير النجاح
            for clo in self.course.clos:
                if clo.criterion_for_success < passing_pct:
                    msg_ar = f"⚠️ المخرج {clo.code}: معيار النجاح ({clo.criterion_for_success:.0f}%) أقل من نسبة النجاح في المقرر ({passing_pct:.0f}%)"
                    msg_en = f"⚠️ CLO {clo.code}: Criterion ({clo.criterion_for_success:.0f}%) is less than course passing percentage ({passing_pct:.0f}%)"
                    raise ValueError(msg_ar if self.language == 'ar' else msg_en)

            # حفظ في الكائن
            self.course.info.total_mark = total_mark
            self.course.info.passing_percentage = passing_pct

            # حفظ في قاعدة البيانات
            if self.course_manager.save_course(self.course):
                self.is_dirty = False
                messagebox.showinfo(
                    t("success", self.language),
                    t("course_saved_successfully", self.language),
                    parent=self
                )
            else:
                raise Exception("فشل حفظ المقرر" if self.language == 'ar' else "Failed to save course")

        except ValueError as e:
            messagebox.showwarning(t("warning", self.language), str(e), parent=self)
        except Exception as e:
            messagebox.showerror(t("error", self.language), str(e), parent=self)

    def mark_dirty(self, *args):
        """وضع علامة على وجود تغييرات"""
        self.is_dirty = True
        self.update_total()

    def on_close(self):
        """معالجة إغلاق النافذة"""
        if self.is_dirty:
            result = messagebox.askyesnocancel(
                t('save_changes_prompt', self.language),
                t('save_changes_prompt_detail', self.language),
                parent=self
            )
            if result is None:  # إلغاء
                return
            if result is True:  # حفظ
                self.save_marks()

        self.destroy()
