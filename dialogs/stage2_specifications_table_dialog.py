"""
نافذة المرحلة الثانية - الخطوة 4: جدول المواصفات
Stage 2 Step 4 - Table of Specifications
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict

from models.course import Course
from managers.course_manager import CourseManager
from translations import t, get_language
from config import COLORS, FONTS


class Stage2SpecificationsTableDialog(tk.Toplevel):
    """نافذة جدول المواصفات - ربط المواضيع مع نواتج التعلم مع الأنشطة"""

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

        # التحقق من وجود أنشطة تقييم
        if not self.course.activities:
            msg_ar = "المقرر لا يحتوي على أنشطة تقييم!\n\nالرجاء إضافة أنشطة التقييم أولاً."
            msg_en = "Course has no assessment activities!\n\nPlease add assessment activities first."
            messagebox.showerror(
                t("error", language),
                msg_ar if language == 'ar' else msg_en,
                parent=parent
            )
            self.destroy()
            return

        # إعداد النافذة
        title_text = "المرحلة الثانية - الخطوة 4: جدول المواصفات" if language == 'ar' else "Stage 2 - Step 4: Table of Specifications"
        self.title(title_text)

        # حجم النافذة - الحد الأقصى مع إمكانية التصغير
        self.state('zoomed')  # تكبير النافذة
        self.resizable(True, True)  # السماح بتغيير الحجم

        self.transient(parent)
        self.configure(bg='#F8F9FA')
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Dictionary لتخزين Entry widgets
        self.entry_widgets: Dict = {}

        # Dictionary للأنشطة المرتبطة بكل CLO
        self.clo_activities_map: Dict = {}

        # إنشاء الواجهة
        self.create_widgets()

    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        is_rtl = (self.language == 'ar')

        # العنوان مع الأزرار
        header_frame = tk.Frame(self, bg=COLORS['primary_blue'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_text = f"جدول المواصفات - {self.course.info.course_code}" if is_rtl else f"Table of Specifications - {self.course.info.course_code}"
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

        # المحتوى الرئيسي
        main_container = tk.Frame(self, bg='#F8F9FA')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # تقسيم إلى قسمين: الجدول الرئيسي + الملخص
        # القسم الأيسر: الجدول الرئيسي
        table_frame = tk.Frame(main_container, bg='#F8F9FA')
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # القسم الأيمن: ملخص الأنشطة
        summary_frame = tk.Frame(main_container, bg='#F8F9FA', width=300)
        summary_frame.pack(side=tk.RIGHT, fill=tk.Y)
        summary_frame.pack_propagate(False)

        # بناء الجدول الرئيسي
        self.create_specifications_table(table_frame)

        # بناء ملخص الأنشطة
        self.create_summary_panel(summary_frame, is_rtl)

    def create_specifications_table(self, parent):
        """إنشاء جدول المواصفات الرئيسي"""
        is_rtl = (self.language == 'ar')

        # Canvas مع scrollbars
        self.canvas = tk.Canvas(parent, bg='#F8F9FA')
        v_scroll = ttk.Scrollbar(parent, orient='vertical', command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(parent, orient='horizontal', command=self.canvas.xview)

        self.scrollable_frame = tk.Frame(self.canvas, bg='#FFFFFF')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.update_scrollregion()
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Grid layout
        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # بناء الجدول
        self.build_table()

        # تحديث منطقة التمرير بعد بناء الجدول
        self.after(100, self.update_scrollregion)

    def build_table(self):
        """بناء جدول المواصفات"""
        is_rtl = (self.language == 'ar')

        # بناء قاموس للأنشطة المرتبطة بكل CLO
        # Key: CLO Code, Value: List of Activities
        self.clo_activities_map = {}
        for clo in self.course.clos:
            self.clo_activities_map[clo.code] = []
            for activity in self.course.activities:
                # التحقق من أن هذا النشاط يقيس هذا المخرج
                if clo.code in activity.measures_clos:
                    self.clo_activities_map[clo.code].append(activity)

        # حساب عدد الأعمدة الكلي
        total_columns = 2  # Topic + Mark
        for clo in self.course.clos:
            num_activities_for_clo = len(self.clo_activities_map[clo.code])
            total_columns += num_activities_for_clo + 1  # Activities + Total
        total_columns += 1  # Topics Checking

        row = 0
        col = 0

        # ===== الصف الأول: العنوان الرئيسي =====
        title_text = 'Table of Specifications for' if not is_rtl else 'جدول المواصفات لمقرر'
        tk.Label(
            self.scrollable_frame,
            text=title_text,
            bg='#FFE0B2',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=2,
            pady=5
        ).grid(row=row, column=0, columnspan=total_columns, sticky='nsew')

        row += 1

        # ===== الصف الثاني: رؤوس الأعمدة الرئيسية =====
        col = 0

        # عمود Topic
        tk.Label(
            self.scrollable_frame,
            text='Topic' if not is_rtl else 'الموضوع',
            bg='#FFB74D',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=1,
            width=25,
            pady=8
        ).grid(row=row, column=col, rowspan=2, sticky='nsew')
        col += 1

        # عمود Mark
        tk.Label(
            self.scrollable_frame,
            text='Mark' if not is_rtl else 'الدرجة',
            bg='#FFB74D',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=1,
            width=8,
            pady=8
        ).grid(row=row, column=col, rowspan=2, sticky='nsew')
        col += 1

        # أعمدة CLOs (كل CLO له عمود التوزيع + أعمدة الأنشطة المرتبطة + عمود Total)
        for clo in self.course.clos:
            num_activities_for_clo = len(self.clo_activities_map[clo.code])
            # رأس CLO (يمتد على عمود التوزيع + الأنشطة المرتبطة + عمود Total)
            tk.Label(
                self.scrollable_frame,
                text=f"{clo.code}\n{clo.mark:.0f}",
                bg='#9C27B0',
                fg='white',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=1,
                pady=5
            ).grid(row=row, column=col, columnspan=num_activities_for_clo + 2, sticky='nsew')  # +2 for Distribution + Total
            col += num_activities_for_clo + 2

        # عمود Topics Checking
        tk.Label(
            self.scrollable_frame,
            text='Topics Checking' if not is_rtl else 'فحص الموضوعات',
            bg='#4CAF50',
            fg='white',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=1,
            width=15,
            pady=8
        ).grid(row=row, column=col, rowspan=2, sticky='nsew')

        row += 1

        # ===== الصف الثالث: رؤوس الأنشطة لكل CLO =====
        col = 2  # نبدأ بعد Topic و Mark

        for clo in self.course.clos:
            # عمود توزيع الدرجات (من الخطوة السابقة)
            tk.Label(
                self.scrollable_frame,
                text='Dist' if not is_rtl else 'توزيع',
                bg='#FFE082',
                font=FONTS['small'],
                relief=tk.RIDGE,
                borderwidth=1,
                width=6,
                pady=3
            ).grid(row=row, column=col, sticky='nsew')
            col += 1

            # أعمدة الأنشطة المرتبطة بهذا CLO فقط
            for activity in self.clo_activities_map[clo.code]:
                activity_abbr = activity.name[:3] if len(activity.name) > 3 else activity.name
                tk.Label(
                    self.scrollable_frame,
                    text=f"{activity_abbr}\n{activity.mark:.0f}",
                    bg='#E1BEE7',
                    font=FONTS['small'],
                    relief=tk.RIDGE,
                    borderwidth=1,
                    width=6,
                    pady=3
                ).grid(row=row, column=col, sticky='nsew')
                col += 1

            # عمود Total لهذا CLO
            tk.Label(
                self.scrollable_frame,
                text='Tot\n' + f"{clo.mark:.0f}",
                bg='#BA68C8',
                fg='white',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=1,
                width=6,
                pady=3
            ).grid(row=row, column=col, sticky='nsew')
            col += 1

        row += 1

        # ===== صفوف المواضيع =====
        for topic in self.course.topics:
            col = 0

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

            # درجة الموضوع
            mark_to_display = topic.final_mark if hasattr(topic, 'final_mark') and topic.final_mark > 0 else topic.mark
            tk.Label(
                self.scrollable_frame,
                text=f"{mark_to_display:.0f}",
                bg='#E3F2FD',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=1
            ).grid(row=row, column=col, sticky='nsew')
            col += 1

            # تهيئة specifications_table إذا لم تكن موجودة
            if not hasattr(topic, 'specifications_table'):
                topic.specifications_table = {}

            # لكل CLO
            for clo in self.course.clos:
                # عمود التوزيع (من الخطوة السابقة - للقراءة فقط)
                distribution_mark = topic.clo_marks_distribution.get(clo.code, 0) if hasattr(topic, 'clo_marks_distribution') else 0
                tk.Label(
                    self.scrollable_frame,
                    text=f"{distribution_mark:.0f}" if distribution_mark > 0 else "",
                    bg='#FFF3E0',
                    font=FONTS['bold'],
                    relief=tk.RIDGE,
                    borderwidth=1,
                    fg='#E65100'
                ).grid(row=row, column=col, sticky='nsew')
                col += 1

                # لكل نشاط مرتبط بهذا CLO فقط
                for activity in self.clo_activities_map[clo.code]:
                    # مفتاح: "CLO_Code|Activity_Name"
                    key = f"{clo.code}|{activity.name}"

                    var = tk.StringVar(value=str(topic.specifications_table.get(key, '')))
                    entry = tk.Entry(
                        self.scrollable_frame,
                        textvariable=var,
                        justify='center',
                        width=6,
                        relief=tk.RIDGE,
                        borderwidth=1,
                        bg='#FFF9C4',
                        font=FONTS['small']
                    )
                    entry.grid(row=row, column=col, sticky='nsew')
                    entry.bind('<KeyRelease>', lambda e, t=topic, k=key: self.on_cell_changed(t, k, e))

                    # حفظ مرجع
                    self.entry_widgets[f"{topic.number}_{key}"] = entry
                    col += 1

                # عمود Total لهذا CLO في هذا الموضوع
                total_label = tk.Label(
                    self.scrollable_frame,
                    text="",
                    bg='#E1BEE7',
                    font=FONTS['bold'],
                    relief=tk.RIDGE,
                    borderwidth=1
                )
                total_label.grid(row=row, column=col, sticky='nsew')
                self.entry_widgets[f"{topic.number}_total_{clo.code}"] = total_label
                col += 1

            # عمود Topics Checking
            checking_label = tk.Label(
                self.scrollable_frame,
                text="",
                bg='white',
                relief=tk.RIDGE,
                borderwidth=1
            )
            checking_label.grid(row=row, column=col, sticky='nsew')
            self.entry_widgets[f"check_{topic.number}"] = checking_label

            row += 1

        # ===== صف Total =====
        col = 0

        total_text = 'Total' if not is_rtl else 'المجموع'
        tk.Label(
            self.scrollable_frame,
            text=total_text,
            bg='#C8E6C9',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=2,
            pady=5
        ).grid(row=row, column=col, sticky='nsew')
        col += 1

        # مجموع الدرجات
        total_marks = sum(topic.final_mark if hasattr(topic, 'final_mark') and topic.final_mark > 0 else topic.mark for topic in self.course.topics)
        tk.Label(
            self.scrollable_frame,
            text=f"{total_marks:.0f}",
            bg='#A5D6A7',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=2
        ).grid(row=row, column=col, sticky='nsew')
        col += 1

        # مجاميع الأعمدة
        for clo in self.course.clos:
            # مجموع عمود التوزيع
            distribution_total_label = tk.Label(
                self.scrollable_frame,
                text="",
                bg='#A5D6A7',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=2
            )
            distribution_total_label.grid(row=row, column=col, sticky='nsew')
            self.entry_widgets[f"total_dist_{clo.code}"] = distribution_total_label
            col += 1

            for activity in self.clo_activities_map[clo.code]:
                key = f"{clo.code}|{activity.name}"
                total_label = tk.Label(
                    self.scrollable_frame,
                    text="",
                    bg='#A5D6A7',
                    font=FONTS['bold'],
                    relief=tk.RIDGE,
                    borderwidth=2
                )
                total_label.grid(row=row, column=col, sticky='nsew')
                self.entry_widgets[f"total_col_{key}"] = total_label
                col += 1

            # مجموع CLO
            clo_total_label = tk.Label(
                self.scrollable_frame,
                text="",
                bg='#81C784',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=2
            )
            clo_total_label.grid(row=row, column=col, sticky='nsew')
            self.entry_widgets[f"total_clo_{clo.code}"] = clo_total_label
            col += 1

        # تحديث المجاميع
        self.update_totals()

    def update_scrollregion(self):
        """تحديث منطقة التمرير للكانفاس"""
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_summary_panel(self, parent, is_rtl):
        """إنشاء لوحة ملخص الأنشطة"""
        tk.Label(
            parent,
            text='Exam' if not is_rtl else 'الامتحان',
            bg='#E3F2FD',
            font=FONTS['bold'],
            pady=10
        ).pack(fill=tk.X, padx=5, pady=(0, 5))

        # إطار مع scrollbar
        container = tk.Frame(parent, bg='white', relief=tk.RIDGE, borderwidth=2)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas + Scrollbar للأنشطة
        canvas = tk.Canvas(container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)

        summary_frame = tk.Frame(canvas, bg='white')

        summary_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=summary_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # رأس الجدول
        header_frame = tk.Frame(summary_frame, bg='#1976D2')
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text='Exam' if not is_rtl else 'النشاط',
            bg='#1976D2',
            fg='white',
            font=FONTS['bold'],
            width=18,
            pady=5,
            relief=tk.RIDGE,
            borderwidth=1
        ).pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(
            header_frame,
            text='Mark' if not is_rtl else 'الدرجة',
            bg='#1976D2',
            fg='white',
            font=FONTS['bold'],
            width=8,
            pady=5,
            relief=tk.RIDGE,
            borderwidth=1
        ).pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(
            header_frame,
            text='Total' if not is_rtl else 'المجموع',
            bg='#1976D2',
            fg='white',
            font=FONTS['bold'],
            width=10,
            pady=5,
            relief=tk.RIDGE,
            borderwidth=1
        ).pack(side=tk.LEFT, fill=tk.Y)

        # صفوف الأنشطة
        for activity in self.course.activities:
            row_frame = tk.Frame(summary_frame, bg='white')
            row_frame.pack(fill=tk.X)

            tk.Label(
                row_frame,
                text=activity.name,
                bg='white',
                anchor='e' if is_rtl else 'w',
                padx=5,
                width=18,
                relief=tk.RIDGE,
                borderwidth=1
            ).pack(side=tk.LEFT, fill=tk.Y)

            tk.Label(
                row_frame,
                text=f"{activity.mark:.0f}",
                bg='#E3F2FD',
                font=FONTS['bold'],
                width=8,
                relief=tk.RIDGE,
                borderwidth=1
            ).pack(side=tk.LEFT, fill=tk.Y)

            # عمود المجموع (سيتم تحديثه ديناميكياً)
            total_label = tk.Label(
                row_frame,
                text="0",
                bg='white',
                font=FONTS['bold'],
                width=10,
                relief=tk.RIDGE,
                borderwidth=1
            )
            total_label.pack(side=tk.LEFT, fill=tk.Y)
            self.entry_widgets[f"summary_total_{activity.name}"] = total_label

    def on_cell_changed(self, topic, key, event):
        """عند تغيير قيمة خلية"""
        try:
            entry = event.widget
            value = entry.get().strip()

            if not hasattr(topic, 'specifications_table'):
                topic.specifications_table = {}

            if value:
                topic.specifications_table[key] = float(value)
            else:
                topic.specifications_table.pop(key, None)

            self.mark_dirty()
            self.update_totals()
        except ValueError:
            pass

    def update_totals(self):
        """تحديث المجاميع والفحوصات"""
        # فحص كل موضوع (صف)
        for topic in self.course.topics:
            mark_to_check = topic.final_mark if hasattr(topic, 'final_mark') and topic.final_mark > 0 else topic.mark

            if hasattr(topic, 'specifications_table'):
                # حساب مجموع كل CLO في هذا الموضوع
                for clo in self.course.clos:
                    clo_total = 0
                    # استخدام الأنشطة المرتبطة بهذا CLO فقط
                    for activity in self.clo_activities_map.get(clo.code, []):
                        key = f"{clo.code}|{activity.name}"
                        clo_total += topic.specifications_table.get(key, 0)

                    # تحديث عمود Total
                    total_label = self.entry_widgets.get(f"{topic.number}_total_{clo.code}")
                    if total_label:
                        total_label.config(text=f"{clo_total:.0f}")

                # حساب المجموع الكلي للموضوع
                topic_total = sum(topic.specifications_table.values())

                # فحص الموضوع
                check_label = self.entry_widgets.get(f"check_{topic.number}")
                if check_label:
                    if abs(topic_total - mark_to_check) < 0.01:
                        check_label.config(text="Ok", bg='#4CAF50', fg='white')
                    else:
                        check_label.config(text="✗", bg='#F44336', fg='white')

        # فحص كل عمود (CLO + Activity)
        for clo in self.course.clos:
            clo_grand_total = 0

            # حساب مجموع عمود التوزيع
            dist_total = 0
            for topic in self.course.topics:
                if hasattr(topic, 'clo_marks_distribution'):
                    dist_total += topic.clo_marks_distribution.get(clo.code, 0)

            # تحديث مجموع عمود التوزيع وتغيير اللون عند عدم التطابق
            dist_total_label = self.entry_widgets.get(f"total_dist_{clo.code}")
            if dist_total_label:
                dist_total_label.config(text=f"{dist_total:.0f}")
                # لا حاجة للفحص هنا لأن التوزيع من الخطوة السابقة

            # استخدام الأنشطة المرتبطة بهذا CLO فقط
            for activity in self.clo_activities_map.get(clo.code, []):
                key = f"{clo.code}|{activity.name}"
                col_total = 0

                for topic in self.course.topics:
                    if hasattr(topic, 'specifications_table'):
                        col_total += topic.specifications_table.get(key, 0)

                clo_grand_total += col_total

                # تحديث مجموع العمود
                total_label = self.entry_widgets.get(f"total_col_{key}")
                if total_label:
                    total_label.config(text=f"{col_total:.0f}")

            # تحديث مجموع CLO وتغيير اللون عند عدم التطابق مع عمود التوزيع
            clo_total_label = self.entry_widgets.get(f"total_clo_{clo.code}")
            if clo_total_label:
                clo_total_label.config(text=f"{clo_grand_total:.0f}")

                # مقارنة مجموع CLO مع مجموع التوزيع
                if abs(clo_grand_total - dist_total) < 0.01:
                    # متطابق - اللون الأخضر
                    clo_total_label.config(bg='#81C784', fg='white')
                    if dist_total_label:
                        dist_total_label.config(bg='#A5D6A7', fg='black')
                else:
                    # غير متطابق - اللون الأحمر
                    clo_total_label.config(bg='#F44336', fg='white')
                    if dist_total_label:
                        dist_total_label.config(bg='#F44336', fg='white')

        # تحديث الأنشطة في اللوحة الجانبية
        for activity in self.course.activities:
            activity_total = 0
            # جمع فقط من CLOs التي ترتبط بهذا النشاط
            for clo in self.course.clos:
                if activity in self.clo_activities_map.get(clo.code, []):
                    key = f"{clo.code}|{activity.name}"
                    for topic in self.course.topics:
                        if hasattr(topic, 'specifications_table'):
                            activity_total += topic.specifications_table.get(key, 0)

            # تحديث عمود المجموع مع تغيير اللون
            total_label = self.entry_widgets.get(f"summary_total_{activity.name}")
            if total_label:
                total_label.config(text=f"{activity_total:.0f}")

                # مقارنة المجموع المحسوب مع الدرجة الأصلية
                if abs(activity_total - activity.mark) < 0.01:
                    # متطابق - اللون الأخضر
                    total_label.config(bg='#4CAF50', fg='white')
                else:
                    # غير متطابق - اللون الأحمر
                    total_label.config(bg='#F44336', fg='white')

    def create_control_buttons(self, parent, is_rtl):
        """أزرار التحكم في الـ header"""
        # زر Save على اليمين (في الـ header)
        tk.Button(
            parent,
            text="💾 Save",
            command=self.save_specifications,
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

    def save_specifications(self):
        """حفظ جدول المواصفات"""
        try:
            # التحقق من المجاميع
            topic_errors = []
            clo_errors = []
            activity_errors = []
            distribution_errors = []

            # التحقق من صفوف المواضيع
            for topic in self.course.topics:
                mark_to_check = topic.final_mark if hasattr(topic, 'final_mark') and topic.final_mark > 0 else topic.mark

                if hasattr(topic, 'specifications_table'):
                    total = sum(topic.specifications_table.values())
                    if abs(total - mark_to_check) > 0.01:
                        topic_errors.append(
                            f"  • الموضوع {topic.number}: المجموع الحالي ({total:.1f}) يجب أن يساوي ({mark_to_check:.0f})"
                            if self.language == 'ar' else
                            f"  • Topic {topic.number}: Current total ({total:.1f}) should equal ({mark_to_check:.0f})"
                        )

            # التحقق من أعمدة CLOs
            for clo in self.course.clos:
                clo_total = 0
                for topic in self.course.topics:
                    if hasattr(topic, 'specifications_table'):
                        # استخدام الأنشطة المرتبطة بهذا CLO فقط
                        for activity in self.clo_activities_map.get(clo.code, []):
                            key = f"{clo.code}|{activity.name}"
                            clo_total += topic.specifications_table.get(key, 0)

                if abs(clo_total - clo.mark) > 0.01:
                    clo_errors.append(
                        f"  • المخرج {clo.code}: المجموع الحالي ({clo_total:.1f}) يجب أن يساوي ({clo.mark:.0f})"
                        if self.language == 'ar' else
                        f"  • CLO {clo.code}: Current total ({clo_total:.1f}) should equal ({clo.mark:.0f})"
                    )

            # التحقق من الأنشطة
            for activity in self.course.activities:
                activity_total = 0
                # جمع فقط من CLOs التي ترتبط بهذا النشاط
                for clo in self.course.clos:
                    if activity in self.clo_activities_map.get(clo.code, []):
                        key = f"{clo.code}|{activity.name}"
                        for topic in self.course.topics:
                            if hasattr(topic, 'specifications_table'):
                                activity_total += topic.specifications_table.get(key, 0)

                if abs(activity_total - activity.mark) > 0.01:
                    activity_errors.append(
                        f"  • {activity.name}: المجموع الحالي ({activity_total:.1f}) يجب أن يساوي ({activity.mark:.0f})"
                        if self.language == 'ar' else
                        f"  • {activity.name}: Current total ({activity_total:.1f}) should equal ({activity.mark:.0f})"
                    )

            # التحقق من توزيع الأنشطة لكل موضوع (مقارنة مع الخطوة السابقة)
            for topic in self.course.topics:
                if hasattr(topic, 'activities_distribution') and hasattr(topic, 'specifications_table'):
                    for activity in self.course.activities:
                        # حساب مجموع هذا النشاط عبر جميع CLOs لهذا الموضوع
                        activity_sum_in_table = 0
                        for clo in self.course.clos:
                            if activity in self.clo_activities_map.get(clo.code, []):
                                key = f"{clo.code}|{activity.name}"
                                activity_sum_in_table += topic.specifications_table.get(key, 0)

                        # المقارنة مع التوزيع من الخطوة 3
                        expected_mark = topic.activities_distribution.get(activity.name, 0)
                        if expected_mark > 0 and abs(activity_sum_in_table - expected_mark) > 0.01:
                            distribution_errors.append(
                                f"  • الموضوع {topic.number} - {activity.name}: المجموع المدخل ({activity_sum_in_table:.1f}) يجب أن يساوي التوزيع السابق ({expected_mark:.0f})"
                                if self.language == 'ar' else
                                f"  • Topic {topic.number} - {activity.name}: Entered total ({activity_sum_in_table:.1f}) should match previous distribution ({expected_mark:.0f})"
                            )

            # بناء رسالة الخطأ المنسقة
            if topic_errors or clo_errors or activity_errors or distribution_errors:
                error_sections = []

                if topic_errors:
                    section = ("📋 أخطاء في مجاميع الموضوعات:\n" if self.language == 'ar' else "📋 Topic Total Errors:\n")
                    section += "\n".join(topic_errors)
                    error_sections.append(section)

                if clo_errors:
                    section = ("🎯 أخطاء في مجاميع المخرجات:\n" if self.language == 'ar' else "🎯 CLO Total Errors:\n")
                    section += "\n".join(clo_errors)
                    error_sections.append(section)

                if activity_errors:
                    section = ("📝 أخطاء في مجاميع الأنشطة:\n" if self.language == 'ar' else "📝 Activity Total Errors:\n")
                    section += "\n".join(activity_errors)
                    error_sections.append(section)

                if distribution_errors:
                    section = ("⚠️ أخطاء في توزيع الأنشطة على المخرجات:\n(يجب أن يتطابق مجموع درجات النشاط في كل موضوع مع ما تم إدخاله في الخطوة السابقة)\n"
                              if self.language == 'ar' else
                              "⚠️ Activity Distribution Errors:\n(The sum of activity marks in each topic must match what was entered in the previous step)\n")
                    section += "\n".join(distribution_errors)
                    error_sections.append(section)

                full_message = "\n\n".join(error_sections)

                messagebox.showerror(
                    "أخطاء في جدول المواصفات" if self.language == 'ar' else "Table of Specifications Errors",
                    full_message,
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
        """حفظ جدول المواصفات كمسودة بدون التحقق من الصحة"""
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
                self.save_specifications()

        self.destroy()
