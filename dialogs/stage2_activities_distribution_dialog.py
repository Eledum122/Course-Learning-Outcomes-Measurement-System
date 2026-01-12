"""
نافذة المرحلة الثانية - الخطوة 3: توزيع درجات المواضيع على أنشطة التقييم
Stage 2 Step 3 - Topics Distribution on Assessment Activities
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict

from models.course import Course
from managers.course_manager import CourseManager
from translations import t, get_language
from config import COLORS, FONTS


class Stage2ActivitiesDistributionDialog(tk.Toplevel):
    """نافذة توزيع درجات المواضيع على أنشطة التقييم"""

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
        title_text = "المرحلة الثانية - الخطوة 3: توزيع المواضيع على أنشطة التقييم" if language == 'ar' else "Stage 2 - Step 3: Topics Distribution on Activities"
        self.title(title_text)

        # حجم النافذة مع إمكانية التصغير
        window_width = 1300
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

    def create_widgets(self):
        """إنشاء عناصر الواجهة"""
        is_rtl = (self.language == 'ar')

        # العنوان
        header_frame = tk.Frame(self, bg=COLORS['primary_blue'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_text = f"توزيع المواضيع على أنشطة التقييم - {self.course.info.course_code}" if is_rtl else f"Topics Distribution on Activities - {self.course.info.course_code}"
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
        info_text = f"الدرجة الكلية: {self.course.info.total_mark:.0f} | عدد المواضيع: {len(self.course.topics)} | عدد الأنشطة: {len(self.course.activities)}" if is_rtl else f"Total Mark: {self.course.info.total_mark:.0f} | Topics: {len(self.course.topics)} | Activities: {len(self.course.activities)}"
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

        # رأس الجدول
        row = 0
        col = 0

        # عنوان No.
        tk.Label(
            self.scrollable_frame,
            text='No.' if not is_rtl else 'رقم',
            bg='#1976D2',
            fg='white',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=1,
            width=5,
            padx=5,
            pady=8
        ).grid(row=row, column=col, sticky='nsew')
        col += 1

        # عنوان List of Topics
        tk.Label(
            self.scrollable_frame,
            text='List of Topics' if not is_rtl else 'قائمة المواضيع',
            bg='#1976D2',
            fg='white',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=1,
            padx=10,
            pady=8
        ).grid(row=row, column=col, sticky='nsew')
        col += 1

        # عنوان Mark
        tk.Label(
            self.scrollable_frame,
            text='Mark' if not is_rtl else 'الدرجة',
            bg='#1976D2',
            fg='white',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=1,
            width=8,
            padx=5,
            pady=8
        ).grid(row=row, column=col, sticky='nsew')
        col += 1

        # أعمدة الأنشطة
        for activity in self.course.activities:
            activity_name = activity.name if len(activity.name) <= 15 else activity.name[:12] + "..."
            activity_header = f"{activity_name}\n{activity.mark:.0f}"

            tk.Label(
                self.scrollable_frame,
                text=activity_header,
                bg='#9C27B0',
                fg='white',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=1,
                width=12,
                padx=3,
                pady=8
            ).grid(row=row, column=col, sticky='nsew')
            col += 1

        # عمود Topics Checking
        tk.Label(
            self.scrollable_frame,
            text='Topics\nChecking' if not is_rtl else 'فحص\nالموضوعات',
            bg='#4CAF50',
            fg='white',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=1,
            width=10,
            padx=5,
            pady=8
        ).grid(row=row, column=col, sticky='nsew')

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

            # الدرجة (من final_mark)
            mark_to_display = topic.final_mark if hasattr(topic, 'final_mark') and topic.final_mark > 0 else topic.mark
            tk.Label(
                self.scrollable_frame,
                text=f"{mark_to_display:.0f}",
                bg='#E3F2FD',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=1,
                width=8
            ).grid(row=row, column=col, sticky='nsew')
            col += 1

            # التوزيع على الأنشطة
            if not hasattr(topic, 'activities_distribution'):
                topic.activities_distribution = {}

            for activity in self.course.activities:
                var = tk.StringVar(value=str(topic.activities_distribution.get(activity.name, '')))
                entry = tk.Entry(
                    self.scrollable_frame,
                    textvariable=var,
                    justify='center',
                    width=12,
                    relief=tk.RIDGE,
                    borderwidth=1,
                    bg='#FFF9C4'
                )
                entry.grid(row=row, column=col, sticky='nsew')
                entry.bind('<KeyRelease>', lambda e, t=topic, a=activity.name: self.on_distribution_changed(t, a, e))

                # حفظ مرجع
                self.entry_widgets[f"{topic.number}_{activity.name}"] = entry
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
        ).grid(row=row, column=col, columnspan=2, sticky='nsew')
        col += 2

        # مجموع الدرجات
        total_marks = sum(topic.final_mark if hasattr(topic, 'final_mark') and topic.final_mark > 0 else topic.mark for topic in self.course.topics)
        tk.Label(
            self.scrollable_frame,
            text=f"{total_marks:.0f}",
            bg='#C8E6C9',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=2
        ).grid(row=row, column=col, sticky='nsew')
        col += 1

        # مجموع كل نشاط
        for activity in self.course.activities:
            activity_total_label = tk.Label(
                self.scrollable_frame,
                text="",
                bg='#C8E6C9',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=2
            )
            activity_total_label.grid(row=row, column=col, sticky='nsew')
            self.entry_widgets[f"total_{activity.name}"] = activity_total_label
            col += 1

        row += 1

        # صف Activities Checking
        col = 0

        checking_text = 'Activities Checking' if not is_rtl else 'فحص الأنشطة'
        tk.Label(
            self.scrollable_frame,
            text=checking_text,
            bg='#FFF9C4',
            font=FONTS['bold'],
            relief=tk.RIDGE,
            borderwidth=2
        ).grid(row=row, column=col, columnspan=3, sticky='nsew')
        col += 3

        # فحص كل نشاط
        for activity in self.course.activities:
            activity_check_label = tk.Label(
                self.scrollable_frame,
                text="",
                bg='white',
                font=FONTS['bold'],
                relief=tk.RIDGE,
                borderwidth=2
            )
            activity_check_label.grid(row=row, column=col, sticky='nsew')
            self.entry_widgets[f"check_activity_{activity.name}"] = activity_check_label
            col += 1

        # تحديث المجاميع
        self.update_totals()

    def on_distribution_changed(self, topic, activity_name, event):
        """عند تغيير توزيع درجة"""
        try:
            entry = event.widget
            value = entry.get().strip()

            if not hasattr(topic, 'activities_distribution'):
                topic.activities_distribution = {}

            if value:
                topic.activities_distribution[activity_name] = float(value)
            else:
                topic.activities_distribution.pop(activity_name, None)

            self.mark_dirty()
            self.update_totals()
        except ValueError:
            pass

    def update_totals(self):
        """تحديث المجاميع والفحوصات"""
        # فحص كل موضوع (صف)
        for topic in self.course.topics:
            mark_to_check = topic.final_mark if hasattr(topic, 'final_mark') and topic.final_mark > 0 else topic.mark

            if hasattr(topic, 'activities_distribution'):
                total = sum(topic.activities_distribution.values())
                check_label = self.entry_widgets.get(f"check_{topic.number}")
                if check_label:
                    if abs(total - mark_to_check) < 0.01:
                        check_label.config(text="Ok", bg='#4CAF50', fg='white')
                    else:
                        check_label.config(text="✗", bg='#F44336', fg='white')

        # فحص كل نشاط (عمود)
        for activity in self.course.activities:
            total = 0
            for topic in self.course.topics:
                if hasattr(topic, 'activities_distribution'):
                    total += topic.activities_distribution.get(activity.name, 0)

            # تحديث المجموع
            total_label = self.entry_widgets.get(f"total_{activity.name}")
            if total_label:
                total_label.config(text=f"{total:.0f}")

            # تحديث الفحص
            check_label = self.entry_widgets.get(f"check_activity_{activity.name}")
            if check_label:
                if abs(total - activity.mark) < 0.01:
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

            # التحقق من صفوف المواضيع
            for topic in self.course.topics:
                mark_to_check = topic.final_mark if hasattr(topic, 'final_mark') and topic.final_mark > 0 else topic.mark

                if hasattr(topic, 'activities_distribution'):
                    total = sum(topic.activities_distribution.values())
                    if abs(total - mark_to_check) > 0.01:
                        errors.append(
                            f"الموضوع {topic.number}: المجموع ({total:.1f}) ≠ الدرجة ({mark_to_check:.0f})"
                            if self.language == 'ar' else
                            f"Topic {topic.number}: Total ({total:.1f}) ≠ Mark ({mark_to_check:.0f})"
                        )

            # التحقق من أعمدة الأنشطة
            for activity in self.course.activities:
                total = sum(
                    topic.activities_distribution.get(activity.name, 0)
                    for topic in self.course.topics
                    if hasattr(topic, 'activities_distribution')
                )
                if abs(total - activity.mark) > 0.01:
                    errors.append(
                        f"النشاط {activity.name}: المجموع ({total:.1f}) ≠ الدرجة ({activity.mark:.0f})"
                        if self.language == 'ar' else
                        f"Activity {activity.name}: Total ({total:.1f}) ≠ Mark ({activity.mark:.0f})"
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
        """حفظ توزيع الأنشطة كمسودة بدون التحقق من الصحة"""
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
