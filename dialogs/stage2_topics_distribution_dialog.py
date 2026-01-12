"""
نافذة المرحلة الثانية - الخطوة 2: توزيع درجات المواضيع على المخرجات
Stage 2 Step 2 - Topics Marks Distribution on CLOs
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict
import math

from models.course import Course
from managers.course_manager import CourseManager
from translations import t, get_language
from config import COLORS, FONTS


class Stage2TopicsDistributionDialog(tk.Toplevel):
    """نافذة توزيع درجات المواضيع على مخرجات التعلم"""

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

        # التحقق من وجود مخرجات
        if not self.course.clos:
            msg_ar = "المقرر لا يحتوي على مخرجات تعلم!\n\nالرجاء إضافة المخرجات أولاً."
            msg_en = "Course has no CLOs!\n\nPlease add CLOs first."
            messagebox.showerror(
                t("error", language),
                msg_ar if language == 'ar' else msg_en,
                parent=parent
            )
            self.destroy()
            return

        # التحقق من وجود مواضيع
        if not self.course.topics:
            msg_ar = "المقرر لا يحتوي على موضوعات!\n\nالرجاء إضافة الموضوعات أولاً."
            msg_en = "Course has no topics!\n\nPlease add topics first."
            messagebox.showerror(
                t("error", language),
                msg_ar if language == 'ar' else msg_en,
                parent=parent
            )
            self.destroy()
            return

        # حساب درجات المواضيع تلقائياً إذا لم تكن محسوبة
        self.calculate_topic_marks()

        # تعيين final_mark = mark إذا لم تكن محددة
        for topic in self.course.topics:
            if topic.final_mark == 0:
                topic.final_mark = topic.mark

        # إعداد النافذة
        title_text = "المرحلة الثانية - الخطوة 2: توزيع درجات المواضيع" if language == 'ar' else "Stage 2 - Step 2: Topics Distribution"
        self.title(title_text)

        # حجم النافذة - أكبر لاستيعاب الجدول مع إمكانية التصغير
        window_width = 1200
        window_height = 750
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')
        self.resizable(True, True)  # السماح بتغيير الحجم

        self.transient(parent)
        self.configure(bg='#F8F9FA')
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Dictionary لتخزين Entry widgets
        self.entry_widgets: Dict = {}

        # إنشاء الواجهة
        self.create_widgets()
        self.load_data()

    def calculate_topic_marks(self):
        """حساب درجات المواضيع بناءً على ساعات الاتصال"""
        total_hours = sum(topic.contact_hours for topic in self.course.topics)
        if total_hours == 0:
            return

        total_mark = self.course.info.total_mark
        calculated_marks = []

        # حساب الدرجة لكل موضوع
        for topic in self.course.topics:
            mark = (topic.contact_hours / total_hours) * total_mark
            calculated_marks.append(mark)

        # تقريب الدرجات وضبط المجموع
        rounded_marks = [math.floor(m) for m in calculated_marks]
        current_total = sum(rounded_marks)

        # توزيع الفرق على المواضيع ذات الكسور الأكبر
        diff = int(total_mark - current_total)
        if diff > 0:
            # حساب الكسور
            fractions = [(i, calculated_marks[i] - rounded_marks[i]) for i in range(len(calculated_marks))]
            # ترتيب حسب حجم الكسر تنازلياً
            fractions.sort(key=lambda x: x[1], reverse=True)
            # إضافة واحد لأكبر الكسور
            for i in range(diff):
                idx = fractions[i][0]
                rounded_marks[idx] += 1

        # تعيين الدرجات
        for i, topic in enumerate(self.course.topics):
            if topic.mark == 0:  # فقط إذا لم تكن محسوبة مسبقاً
                topic.mark = float(rounded_marks[i])

    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        is_rtl = (self.language == 'ar')

        # العنوان
        header_frame = tk.Frame(self, bg=COLORS['primary_blue'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_text = f"توزيع درجات المواضيع على المخرجات - {self.course.info.course_code}" if is_rtl else f"Topics Distribution - {self.course.info.course_code}"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            bg=COLORS['primary_blue'],
            fg='white',
            font=FONTS['arabic_header'] if is_rtl else FONTS['english_header']
        )
        title_label.pack(side=tk.RIGHT if is_rtl else tk.LEFT, padx=20, pady=15)

        # الأزرار في الـ header
        self.create_control_buttons(header_frame, is_rtl)

        # المحتوى
        main_frame = tk.Frame(self, bg='#F8F9FA')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # معلومات
        info_text = f"الدرجة الكلية: {self.course.info.total_mark:.0f} | مجموع ساعات الاتصال: {sum(t.contact_hours for t in self.course.topics):.0f}" if is_rtl else f"Total Mark: {self.course.info.total_mark:.0f} | Total Hours: {sum(t.contact_hours for t in self.course.topics):.0f}"
        tk.Label(
            main_frame,
            text=info_text,
            bg='#F8F9FA',
            font=FONTS['arabic_bold'] if is_rtl else FONTS['bold'],
            fg=COLORS['primary_blue']
        ).pack(pady=(0, 10))

        # إطار الجدول مع scrollbars
        table_frame = tk.Frame(main_frame, bg='#F8F9FA')
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas للتمرير
        canvas = tk.Canvas(table_frame, bg='#F8F9FA')
        v_scroll = ttk.Scrollbar(table_frame, orient='vertical', command=canvas.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient='horizontal', command=canvas.xview)

        self.scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Grid layout
        canvas.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # بناء الجدول
        self.create_distribution_table()

    def create_distribution_table(self):
        """إنشاء جدول توزيع الدرجات"""
        is_rtl = (self.language == 'ar')

        # الأعمدة: No, Topic, Contact Hours, Mark, Remark, CLO1, CLO2, ..., Total, Checking
        clo_codes = [clo.code for clo in self.course.clos]

        # رأس الجدول
        row = 0

        # الصف الأول: عناوين العواميد الثابتة
        headers_fixed = ['No.', 'List of Topics', 'Contact\nHours', 'Mark', 'Remark'] if not is_rtl else ['رقم', 'قائمة المواضيع', 'ساعات\nالاتصال', 'الدرجة', 'ملاحظات']

        col = 0
        for header in headers_fixed:
            label = tk.Label(
                self.scrollable_frame,
                text=header,
                bg='#1976D2',
                fg='white',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=1,
                padx=5,
                pady=8
            )
            label.grid(row=row, column=col, sticky='nsew')
            col += 1

        # الصف الثاني من الرأس: CLOs مع درجاتها
        for clo in self.course.clos:
            clo_text = f"{clo.code}\n{clo.mark:.0f}"
            label = tk.Label(
                self.scrollable_frame,
                text=clo_text,
                bg='#9C27B0',
                fg='white',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=1,
                width=8,
                padx=3,
                pady=8
            )
            label.grid(row=row, column=col, sticky='nsew')
            col += 1

        # عمود المجموع
        total_header = 'Topics\nChecking' if not is_rtl else 'فحص\nالموضوعات'
        label = tk.Label(
            self.scrollable_frame,
            text=total_header,
            bg='#4CAF50',
            fg='white',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=1,
            width=10,
            padx=5,
            pady=8
        )
        label.grid(row=row, column=col, sticky='nsew')

        row += 1

        # صفوف المواضيع
        for topic in self.course.topics:
            col = 0

            # رقم الموضوع
            tk.Label(
                self.scrollable_frame,
                text=str(topic.number),
                bg='white',
                relief=tk.RIDGE,
                borderwidth=1,
                width=5
            ).grid(row=row, column=col, sticky='nsew')
            col += 1

            # عنوان الموضوع
            tk.Label(
                self.scrollable_frame,
                text=topic.title,
                bg='white',
                relief=tk.RIDGE,
                borderwidth=1,
                anchor='e' if is_rtl else 'w',
                padx=5
            ).grid(row=row, column=col, sticky='nsew')
            col += 1

            # ساعات الاتصال
            tk.Label(
                self.scrollable_frame,
                text=f"{topic.contact_hours:.0f}",
                bg='white',
                relief=tk.RIDGE,
                borderwidth=1,
                width=8
            ).grid(row=row, column=col, sticky='nsew')
            col += 1

            # الدرجة المحسوبة
            tk.Label(
                self.scrollable_frame,
                text=f"{topic.mark:.0f}",
                bg='#E3F2FD',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=1,
                width=8
            ).grid(row=row, column=col, sticky='nsew')
            col += 1

            # Remark - الدرجة النهائية (قابل للتعديل)
            remark_var = tk.StringVar(value=str(topic.final_mark) if topic.final_mark > 0 else str(topic.mark))
            remark_entry = tk.Entry(
                self.scrollable_frame,
                textvariable=remark_var,
                justify='center',
                width=8,
                relief=tk.RIDGE,
                borderwidth=1,
                bg='#FFF3E0',
                font=FONTS['bold']
            )
            remark_entry.grid(row=row, column=col, sticky='nsew')
            remark_entry.bind('<KeyRelease>', lambda e, t=topic: self.on_final_mark_changed(t, e))

            # حفظ مرجع
            self.entry_widgets[f"remark_{topic.number}"] = remark_entry
            col += 1

            # توزيع على CLOs
            if not hasattr(topic, 'clo_marks_distribution'):
                topic.clo_marks_distribution = {}

            for clo in self.course.clos:
                var = tk.StringVar(value=str(topic.clo_marks_distribution.get(clo.code, '')))
                entry = tk.Entry(
                    self.scrollable_frame,
                    textvariable=var,
                    justify='center',
                    width=8,
                    relief=tk.RIDGE,
                    borderwidth=1,
                    bg='#FFF9C4'
                )
                entry.grid(row=row, column=col, sticky='nsew')
                entry.bind('<KeyRelease>', lambda e, t=topic, c=clo.code: self.on_distribution_changed(t, c, e))

                # حفظ مرجع للـ entry
                self.entry_widgets[f"{topic.number}_{clo.code}"] = entry
                col += 1

            # عمود الفحص
            checking_label = tk.Label(
                self.scrollable_frame,
                text="",
                bg='white',
                relief=tk.RIDGE,
                borderwidth=1,
                width=10
            )
            checking_label.grid(row=row, column=col, sticky='nsew')
            self.entry_widgets[f"check_{topic.number}"] = checking_label

            row += 1

        # صف المجموع
        col = 0

        # Total label
        total_text = 'Total' if not is_rtl else 'المجموع'
        tk.Label(
            self.scrollable_frame,
            text=total_text,
            bg='#E8F5E9',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=2
        ).grid(row=row, column=col, columnspan=3, sticky='nsew')
        col += 3

        # مجموع الدرجات المحسوبة
        total_marks = sum(topic.mark for topic in self.course.topics)
        tk.Label(
            self.scrollable_frame,
            text=f"{total_marks:.0f}",
            bg='#C8E6C9',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=2
        ).grid(row=row, column=col, sticky='nsew')
        col += 1

        # مجموع Remark (final_mark) - مع التحقق
        total_final_marks_label = tk.Label(
            self.scrollable_frame,
            text="",
            bg='white',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=2
        )
        total_final_marks_label.grid(row=row, column=col, sticky='nsew')
        self.entry_widgets["total_final_marks"] = total_final_marks_label
        col += 1

        # مجموع كل CLO
        for clo in self.course.clos:
            clo_total_label = tk.Label(
                self.scrollable_frame,
                text="",
                bg='#C8E6C9',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=2
            )
            clo_total_label.grid(row=row, column=col, sticky='nsew')
            self.entry_widgets[f"total_{clo.code}"] = clo_total_label
            col += 1

        # CLOs Checking
        row += 1
        col = 0

        checking_text = 'CLOs Checking' if not is_rtl else 'فحص المخرجات'
        tk.Label(
            self.scrollable_frame,
            text=checking_text,
            bg='#FFF9C4',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=2
        ).grid(row=row, column=col, columnspan=5, sticky='nsew')
        col += 5

        # فحص كل CLO
        for clo in self.course.clos:
            clo_check_label = tk.Label(
                self.scrollable_frame,
                text="",
                bg='white',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=2
            )
            clo_check_label.grid(row=row, column=col, sticky='nsew')
            self.entry_widgets[f"check_clo_{clo.code}"] = clo_check_label
            col += 1

        # تحديث المجاميع
        self.update_totals()

    def on_distribution_changed(self, topic, clo_code, event):
        """عند تغيير توزيع درجة"""
        try:
            entry = event.widget
            value = entry.get().strip()

            if not hasattr(topic, 'clo_marks_distribution'):
                topic.clo_marks_distribution = {}

            if value:
                topic.clo_marks_distribution[clo_code] = float(value)
            else:
                topic.clo_marks_distribution.pop(clo_code, None)

            self.mark_dirty()
            self.update_totals()
        except ValueError:
            pass

    def on_final_mark_changed(self, topic, event):
        """عند تغيير الدرجة النهائية"""
        try:
            value = event.widget.get().strip()
            if value:
                topic.final_mark = float(value)
            else:
                topic.final_mark = 0.0
            self.mark_dirty()
            self.update_totals()
        except ValueError:
            pass

    def update_totals(self):
        """تحديث المجاميع والفحوصات"""
        # فحص كل موضوع (صف) - يجب أن يساوي final_mark
        for topic in self.course.topics:
            if hasattr(topic, 'clo_marks_distribution'):
                total = sum(topic.clo_marks_distribution.values())
                check_label = self.entry_widgets.get(f"check_{topic.number}")
                if check_label:
                    # التحقق من أن المجموع يساوي الدرجة النهائية (Remark)
                    if abs(total - topic.final_mark) < 0.01:
                        check_label.config(text="Ok", bg='#4CAF50', fg='white')
                    else:
                        check_label.config(text="✗", bg='#F44336', fg='white')

        # تحديث مجموع final_mark
        total_final_marks = sum(topic.final_mark for topic in self.course.topics)
        total_final_label = self.entry_widgets.get("total_final_marks")
        if total_final_label:
            if abs(total_final_marks - self.course.info.total_mark) < 0.01:
                total_final_label.config(
                    text=f"{total_final_marks:.0f}",
                    bg='#4CAF50',
                    fg='white'
                )
            else:
                total_final_label.config(
                    text=f"{total_final_marks:.0f}",
                    bg='#F44336',
                    fg='white'
                )

        # فحص كل CLO (عمود)
        for clo in self.course.clos:
            total = 0
            for topic in self.course.topics:
                if hasattr(topic, 'clo_marks_distribution'):
                    total += topic.clo_marks_distribution.get(clo.code, 0)

            # تحديث المجموع
            total_label = self.entry_widgets.get(f"total_{clo.code}")
            if total_label:
                total_label.config(text=f"{total:.0f}")

            # تحديث الفحص
            check_label = self.entry_widgets.get(f"check_clo_{clo.code}")
            if check_label:
                if abs(total - clo.mark) < 0.01:
                    check_label.config(text="Ok", bg='#4CAF50', fg='white')
                else:
                    check_label.config(text="✗", bg='#F44336', fg='white')

    def create_control_buttons(self, parent, is_rtl):
        """أزرار التحكم في الـ header"""
        # زر Save على اليمين (في الـ header)
        tk.Button(
            parent,
            text="💾 Save",
            command=self.save_distribution,
            bg='#4CAF50',
            fg='white',
            font=FONTS['bold'],
            width=12,
            relief=tk.RAISED,
            cursor='hand2',
            pady=8
        ).pack(side=tk.RIGHT, padx=5, pady=15)

        # زر Save as Draft بجانب Save
        tk.Button(
            parent,
            text="📝 Draft",
            command=self.save_as_draft,
            bg='#FF9800',
            fg='white',
            font=FONTS['bold'],
            width=12,
            relief=tk.RAISED,
            cursor='hand2',
            pady=8
        ).pack(side=tk.RIGHT, padx=5, pady=15)

        # زر Cancel على اليسار (في الـ header)
        tk.Button(
            parent,
            text="✕ Cancel",
            command=self.on_close,
            bg='#757575',
            fg='white',
            font=FONTS['bold'],
            width=12,
            relief=tk.RAISED,
            cursor='hand2',
            pady=8
        ).pack(side=tk.LEFT, padx=10, pady=15)

    def load_data(self):
        """تحميل البيانات"""
        # البيانات محملة بالفعل في create_distribution_table
        pass

    def save_distribution(self):
        """حفظ التوزيع"""
        try:
            # التحقق من المجاميع
            errors = []

            # التحقق من أن مجموع final_mark يساوي الدرجة الكلية
            total_final_marks = sum(topic.final_mark for topic in self.course.topics)
            if abs(total_final_marks - self.course.info.total_mark) > 0.01:
                errors.append(
                    f"⚠️ مجموع درجات Remark ({total_final_marks:.1f}) ≠ الدرجة الكلية ({self.course.info.total_mark:.0f})"
                    if self.language == 'ar' else
                    f"⚠️ Total Remark marks ({total_final_marks:.1f}) ≠ Total mark ({self.course.info.total_mark:.0f})"
                )

            # التحقق من صفوف المواضيع - يجب أن يساوي final_mark
            for topic in self.course.topics:
                if hasattr(topic, 'clo_marks_distribution'):
                    total = sum(topic.clo_marks_distribution.values())
                    if abs(total - topic.final_mark) > 0.01:
                        errors.append(
                            f"الموضوع {topic.number}: المجموع ({total:.1f}) ≠ Remark ({topic.final_mark:.0f})"
                            if self.language == 'ar' else
                            f"Topic {topic.number}: Total ({total:.1f}) ≠ Remark ({topic.final_mark:.0f})"
                        )

            # التحقق من أعمدة المخرجات
            for clo in self.course.clos:
                total = sum(
                    topic.clo_marks_distribution.get(clo.code, 0)
                    for topic in self.course.topics
                    if hasattr(topic, 'clo_marks_distribution')
                )
                if abs(total - clo.mark) > 0.01:
                    errors.append(
                        f"المخرج {clo.code}: المجموع ({total:.1f}) ≠ الدرجة ({clo.mark:.0f})"
                        if self.language == 'ar' else
                        f"CLO {clo.code}: Total ({total:.1f}) ≠ Mark ({clo.mark:.0f})"
                    )

            if errors:
                msg = "\n".join(errors)
                messagebox.showerror(
                    t("error", self.language),
                    ("⚠️ توجد أخطاء في التوزيع:\n\n" + msg) if self.language == 'ar' else ("⚠️ Distribution errors:\n\n" + msg),
                    parent=self
                )
                return

            # حفظ في قاعدة البيانات
            if self.course_manager.save_course(self.course):
                self.is_dirty = False
                messagebox.showinfo(
                    t("success", self.language),
                    t("course_saved_successfully", self.language),
                    parent=self
                )
            else:
                raise Exception("فشل الحفظ" if self.language == 'ar' else "Save failed")

        except Exception as e:
            messagebox.showerror(t("error", self.language), str(e), parent=self)

    def save_as_draft(self):
        """حفظ توزيع الدرجات كمسودة بدون التحقق من الصحة"""
        try:
            # حفظ في قاعدة البيانات مباشرة بدون التحقق
            if self.course_manager.save_course(self.course):
                self.is_dirty = False
                msg_ar = "✅ تم حفظ المسودة بنجاح!\n\nيمكنك المتابعة لاحقاً."
                msg_en = "✅ Draft saved successfully!\n\nYou can continue later."
                messagebox.showinfo(
                    "Draft Saved" if self.language == 'en' else "حفظ المسودة",
                    msg_en if self.language == 'en' else msg_ar,
                    parent=self
                )
            else:
                raise Exception("فشل الحفظ" if self.language == 'ar' else "Save failed")

        except Exception as e:
            messagebox.showerror(t("error", self.language), str(e), parent=self)

    def mark_dirty(self, *args):
        """وضع علامة على وجود تغييرات"""
        self.is_dirty = True

    def on_close(self):
        """معالجة إغلاق النافذة"""
        if self.is_dirty:
            result = messagebox.askyesnocancel(
                t('save_changes_prompt', self.language),
                t('save_changes_prompt_detail', self.language),
                parent=self
            )
            if result is None:
                return
            if result is True:
                self.save_distribution()

        self.destroy()
