# -*- coding: utf-8 -*-
"""
لوحة التحكم الحديثة - تصميم احترافي متطور
Modern Dashboard - Professional Advanced Design
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import COLORS, FONTS


class ModernDashboard(tk.Frame):
    """لوحة تحكم حديثة بتصميم احترافي متطور"""

    def __init__(self, parent, user, access_control, course_manager, main_window):
        super().__init__(parent, bg='#F0F4F8')

        self.user = user
        self.access_control = access_control
        self.course_manager = course_manager
        self.main_window = main_window

        self.create_ui()

    def create_ui(self):
        """إنشاء الواجهة"""
        # ═══════════════════════════════════════════════════════════
        # 1. القسم الترحيبي العلوي مع تدرج لوني
        # ═══════════════════════════════════════════════════════════
        header = tk.Frame(self, bg='#FFFFFF', height=140)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # إضافة شريط تدرج لوني في الأعلى
        gradient_bar = tk.Frame(header, bg='#667EEA', height=6)
        gradient_bar.pack(fill=tk.X)

        # محتوى الترويسة
        header_content = tk.Frame(header, bg='#FFFFFF')
        header_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # الإطار الأيسر - الترحيب
        left_frame = tk.Frame(header_content, bg='#FFFFFF')
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # تحديد التحية حسب الوقت
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "صباح الخير"
            icon = "☀"
        elif 12 <= hour < 17:
            greeting = "مساء الخير"
            icon = "☁"
        elif 17 <= hour < 21:
            greeting = "مساء الخير"
            icon = "◐"
        else:
            greeting = "مساء الخير"
            icon = "★"

        # العنوان مع الأيقونة
        title = tk.Label(
            left_frame,
            text=f"{icon}  {greeting}، {self.user.full_name}",
            font=('Segoe UI', 26, 'bold'),
            bg='#FFFFFF',
            fg='#1A202C'
        )
        title.pack(anchor=tk.W)

        # النص الفرعي
        subtitle = tk.Label(
            left_frame,
            text="لوحة التحكم الرئيسية - نظام قياس مخرجات التعلم (CLOs)",
            font=('Segoe UI', 13),
            bg='#FFFFFF',
            fg='#718096'
        )
        subtitle.pack(anchor=tk.W, pady=(8, 0))

        # الإطار الأيمن - التاريخ والوقت
        right_frame = tk.Frame(header_content, bg='#FFFFFF')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # التاريخ
        date_str = datetime.now().strftime("%A, %d %B %Y")
        date_label = tk.Label(
            right_frame,
            text=f"📅  {date_str}",
            font=('Segoe UI', 12),
            bg='#FFFFFF',
            fg='#4A5568'
        )
        date_label.pack(anchor=tk.E)

        # الوقت (سيتم تحديثه)
        self.time_label = tk.Label(
            right_frame,
            text="",
            font=('Segoe UI', 11),
            bg='#FFFFFF',
            fg='#718096'
        )
        self.time_label.pack(anchor=tk.E, pady=(5, 0))
        self.update_time()

        # ═══════════════════════════════════════════════════════════
        # 2. حاوية قابلة للتمرير للمحتوى
        # ═══════════════════════════════════════════════════════════
        main_canvas = tk.Canvas(self, bg='#F0F4F8', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#F0F4F8')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ربط عجلة الماوس بالتمرير
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ═══════════════════════════════════════════════════════════
        # 3. بطاقات الإحصائيات المحسّنة
        # ═══════════════════════════════════════════════════════════
        stats_container = tk.Frame(scrollable_frame, bg='#F0F4F8')
        stats_container.pack(fill=tk.X, padx=40, pady=25)

        # الحصول على الإحصائيات
        all_courses = self.course_manager.list_all_courses()
        total = len(all_courses)
        active = len([c for c in all_courses if c.get('status') == 'active'])
        completed = len([c for c in all_courses if c.get('status') == 'completed'])
        draft = len([c for c in all_courses if c.get('status') == 'draft'])

        # Grid للبطاقات
        for i in range(4):
            stats_container.columnconfigure(i, weight=1)

        # البطاقات مع تدرجات لونية
        stats = [
            ("📚", "إجمالي المقررات", total, "#667EEA", "#5A67D8", "+12% من الشهر الماضي"),
            ("✓", "مقررات نشطة", active, "#48BB78", "#38A169", "جاهزة للاستخدام"),
            ("●", "مقررات مكتملة", completed, "#F6AD55", "#ED8936", "تم إنجازها"),
            ("✎", "مسودات", draft, "#A0AEC0", "#718096", "قيد العمل")
        ]

        for i, (icon, label, value, color1, color2, desc) in enumerate(stats):
            self.create_enhanced_stat_card(stats_container, icon, label, value,
                                          color1, color2, desc, i)

        # ═══════════════════════════════════════════════════════════
        # 4. قسم الإجراءات السريعة والاختصارات
        # ═══════════════════════════════════════════════════════════
        actions_section = tk.Frame(scrollable_frame, bg='#F0F4F8')
        actions_section.pack(fill=tk.X, padx=40, pady=(0, 25))

        # عنوان القسم
        section_header = tk.Frame(actions_section, bg='#F0F4F8')
        section_header.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            section_header,
            text="⚡ إجراءات سريعة",
            font=('Segoe UI', 18, 'bold'),
            bg='#F0F4F8',
            fg='#1A202C'
        ).pack(side=tk.LEFT)

        # حاوية الأزرار
        buttons_container = tk.Frame(actions_section, bg='#F0F4F8')
        buttons_container.pack(fill=tk.X)

        # Grid للأزرار (3 أعمدة)
        for i in range(3):
            buttons_container.columnconfigure(i, weight=1)

        # الصف الأول من الأزرار
        action_buttons = []

        if self.access_control.has_permission(self.user.user_id, 'create_course_master'):
            action_buttons.append(
                ("+", "مقرر جديد", "إنشاء مقرر دراسي جديد", "#667EEA", self.main_window.new_course)
            )

        action_buttons.extend([
            ("◉", "فتح مقرر", "فتح مقرر موجود للتعديل", "#48BB78", self.main_window.open_course),
            ("📅", "إدارة الفصول", "إدارة بيانات الفصول الدراسية", "#FF6B6B", self.main_window.open_semester_management),
            ("▣", "التقارير", "عرض وتوليد التقارير", "#F6AD55", self.main_window.generate_course_report)
        ])

        for i, (icon, title, desc, color, command) in enumerate(action_buttons):
            self.create_action_card(buttons_container, icon, title, desc, color, command, i, 0)

        # الصف الثاني من الأزرار - اختصارات المراحل
        stages_buttons = [
            ("1", "المرحلة الأولى", "معلومات المقرر والمخرجات", "#9B59B6",
             self.main_window.open_stage1_for_editing),
            ("2", "المرحلة الثانية", "توزيع الدرجات والمواصفات", "#3498DB",
             self.main_window.open_stage2),
            ("3", "المرحلة الثالثة", "بيانات الشعب والطلاب", "#E74C3C",
             self.main_window.open_stage3_step1)
        ]

        for i, (icon, title, desc, color, command) in enumerate(stages_buttons):
            self.create_action_card(buttons_container, icon, title, desc, color, command, i, 1)

        # ═══════════════════════════════════════════════════════════
        # 5. قسم المقررات الأخيرة والإشعارات (صفين متجاورين)
        # ═══════════════════════════════════════════════════════════
        bottom_section = tk.Frame(scrollable_frame, bg='#F0F4F8')
        bottom_section.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 40))

        # Grid للأعمدة
        bottom_section.columnconfigure(0, weight=2)  # المقررات الأخيرة (أوسع)
        bottom_section.columnconfigure(1, weight=1)  # الإشعارات (أضيق)

        # القسم الأيسر - المقررات الأخيرة
        courses_frame = tk.Frame(bottom_section, bg='#FFFFFF', relief=tk.FLAT, bd=0)
        courses_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 15))
        courses_frame.config(highlightthickness=1, highlightbackground='#E2E8F0')

        # عنوان الجدول
        courses_header = tk.Frame(courses_frame, bg='#F7FAFC', height=60)
        courses_header.pack(fill=tk.X)
        courses_header.pack_propagate(False)

        tk.Label(
            courses_header,
            text="📚  المقررات الأخيرة",
            font=('Segoe UI', 16, 'bold'),
            bg='#F7FAFC',
            fg='#1A202C'
        ).pack(side=tk.LEFT, padx=30, pady=15)

        # الجدول
        self.create_modern_table(courses_frame, all_courses[:8])

        # القسم الأيمن - الإشعارات والتنبيهات
        notifications_frame = tk.Frame(bottom_section, bg='#FFFFFF', relief=tk.FLAT, bd=0)
        notifications_frame.grid(row=0, column=1, sticky='nsew')
        notifications_frame.config(highlightthickness=1, highlightbackground='#E2E8F0')

        # عنوان الإشعارات
        notif_header = tk.Frame(notifications_frame, bg='#F7FAFC', height=60)
        notif_header.pack(fill=tk.X)
        notif_header.pack_propagate(False)

        tk.Label(
            notif_header,
            text="♦  الإشعارات",
            font=('Segoe UI', 16, 'bold'),
            bg='#F7FAFC',
            fg='#1A202C'
        ).pack(side=tk.LEFT, padx=25, pady=15)

        # محتوى الإشعارات
        self.create_notifications_section(notifications_frame)

    def create_enhanced_stat_card(self, parent, icon, label, value, color1, color2, desc, column):
        """إنشاء بطاقة إحصائية محسّنة مع تدرج لوني"""
        card = tk.Frame(
            parent,
            bg='#FFFFFF',
            relief=tk.FLAT,
            bd=0
        )
        card.grid(row=0, column=column, padx=10, sticky='ew')

        # إضافة ظل وحدود
        card.config(highlightthickness=1, highlightbackground='#E2E8F0')

        # شريط ملون في الأعلى
        color_bar = tk.Frame(card, bg=color1, height=5)
        color_bar.pack(fill=tk.X)

        # المحتوى
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # الأيقونة والقيمة في صف واحد
        top_row = tk.Frame(content, bg='#FFFFFF')
        top_row.pack(fill=tk.X)

        # الأيقونة
        icon_label = tk.Label(
            top_row,
            text=icon,
            font=('Segoe UI', 42),
            bg='#FFFFFF'
        )
        icon_label.pack(side=tk.LEFT)

        # القيمة
        value_label = tk.Label(
            top_row,
            text=str(value),
            font=('Segoe UI', 38, 'bold'),
            bg='#FFFFFF',
            fg=color1
        )
        value_label.pack(side=tk.RIGHT, pady=5)

        # التسمية
        label_label = tk.Label(
            content,
            text=label,
            font=('Segoe UI', 12, 'bold'),
            bg='#FFFFFF',
            fg='#2D3748'
        )
        label_label.pack(anchor=tk.W, pady=(15, 5))

        # الوصف
        desc_label = tk.Label(
            content,
            text=desc,
            font=('Segoe UI', 9),
            bg='#FFFFFF',
            fg='#A0AEC0'
        )
        desc_label.pack(anchor=tk.W)

        # تأثير Hover محسّن
        def on_enter(e):
            card.config(highlightbackground=color1, highlightthickness=2)
            color_bar.config(height=6)
            # رفع البطاقة قليلاً
            card.config(relief=tk.RAISED)

        def on_leave(e):
            card.config(highlightbackground='#E2E8F0', highlightthickness=1)
            color_bar.config(height=5)
            card.config(relief=tk.FLAT)

        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        for widget in [content, icon_label, value_label, label_label, desc_label, top_row]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)

    def create_action_card(self, parent, icon, title, desc, color, command, column, row):
        """إنشاء بطاقة إجراء سريع محسّنة"""
        card = tk.Frame(
            parent,
            bg='#FFFFFF',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2'
        )
        card.grid(row=row, column=column, padx=10, pady=8, sticky='ew')

        # حدود
        card.config(highlightthickness=1, highlightbackground='#E2E8F0')

        # شريط ملون جانبي
        side_bar = tk.Frame(card, bg=color, width=5)
        side_bar.pack(side=tk.LEFT, fill=tk.Y)

        # المحتوى
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=18)

        # الصف العلوي - الأيقونة والعنوان
        top_row = tk.Frame(content, bg='#FFFFFF')
        top_row.pack(fill=tk.X)

        # الأيقونة
        icon_label = tk.Label(
            top_row,
            text=icon,
            font=('Segoe UI', 28),
            bg='#FFFFFF'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 12))

        # العنوان
        title_label = tk.Label(
            top_row,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            bg='#FFFFFF',
            fg='#1A202C'
        )
        title_label.pack(side=tk.LEFT, anchor=tk.W)

        # الوصف
        desc_label = tk.Label(
            content,
            text=desc,
            font=('Segoe UI', 10),
            bg='#FFFFFF',
            fg='#718096'
        )
        desc_label.pack(anchor=tk.W, pady=(8, 0), padx=(42, 0))

        # تأثير Hover
        def on_enter(e):
            card.config(bg='#F7FAFC', highlightbackground=color, highlightthickness=2)
            content.config(bg='#F7FAFC')
            top_row.config(bg='#F7FAFC')
            icon_label.config(bg='#F7FAFC')
            title_label.config(bg='#F7FAFC', fg=color)
            desc_label.config(bg='#F7FAFC')
            side_bar.config(width=6)

        def on_leave(e):
            card.config(bg='#FFFFFF', highlightbackground='#E2E8F0', highlightthickness=1)
            content.config(bg='#FFFFFF')
            top_row.config(bg='#FFFFFF')
            icon_label.config(bg='#FFFFFF')
            title_label.config(bg='#FFFFFF', fg='#1A202C')
            desc_label.config(bg='#FFFFFF')
            side_bar.config(width=5)

        def on_click(e):
            command()

        # ربط الأحداث
        for widget in [card, content, top_row, icon_label, title_label, desc_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Button-1>', on_click)
            widget.config(cursor='hand2')

    def create_modern_table(self, parent, courses):
        """إنشاء جدول حديث للمقررات"""
        # حاوية الجدول مع تمرير
        table_container = tk.Frame(parent, bg='#FFFFFF')
        table_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Canvas للتمرير
        canvas = tk.Canvas(table_container, bg='#FFFFFF', highlightthickness=0, height=400)
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not courses:
            # رسالة عدم وجود مقررات
            empty_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
            empty_frame.pack(fill=tk.BOTH, expand=True, pady=80)

            tk.Label(
                empty_frame,
                text="📚",
                font=('Segoe UI', 56),
                bg='#FFFFFF',
                fg='#CBD5E0'
            ).pack()

            tk.Label(
                empty_frame,
                text="لا توجد مقررات حتى الآن",
                font=('Segoe UI', 15, 'bold'),
                bg='#FFFFFF',
                fg='#A0AEC0'
            ).pack(pady=(15, 5))

            tk.Label(
                empty_frame,
                text="ابدأ بإنشاء مقرر جديد من الأزرار أعلاه",
                font=('Segoe UI', 11),
                bg='#FFFFFF',
                fg='#CBD5E0'
            ).pack()
            return

        # رأس الجدول
        header = tk.Frame(scrollable_frame, bg='#F7FAFC', height=50)
        header.pack(fill=tk.X, padx=20)
        header.pack_propagate(False)

        headers_data = [
            ("كود المقرر", 0.18),
            ("اسم المقرر", 0.35),
            ("البرنامج", 0.22),
            ("الحالة", 0.15),
            ("آخر تحديث", 0.10)
        ]

        x_pos = 0
        for text, width in headers_data:
            tk.Label(
                header,
                text=text,
                font=('Segoe UI', 11, 'bold'),
                bg='#F7FAFC',
                fg='#4A5568',
                anchor=tk.W
            ).place(relx=x_pos, rely=0.5, anchor=tk.W, relwidth=width)
            x_pos += width

        # صفوف الجدول
        for i, course in enumerate(courses):
            row_bg = '#FFFFFF' if i % 2 == 0 else '#F7FAFC'
            row = tk.Frame(scrollable_frame, bg=row_bg, height=65)
            row.pack(fill=tk.X, padx=20)
            row.pack_propagate(False)

            # خط فاصل خفيف
            separator = None
            if i > 0:
                separator = tk.Frame(row, bg='#E2E8F0', height=1)
                separator.place(relx=0, rely=0, relwidth=1)

            # كود المقرر
            code_label = tk.Label(
                row,
                text=course.get('course_code', 'N/A'),
                font=('Segoe UI', 11, 'bold'),
                bg=row_bg,
                fg='#667EEA',
                anchor=tk.W
            )
            code_label.place(relx=0, rely=0.5, anchor=tk.W, relwidth=0.18)

            # اسم المقرر
            title_label = tk.Label(
                row,
                text=course.get('course_title', 'N/A')[:40] + ('...' if len(course.get('course_title', '')) > 40 else ''),
                font=('Segoe UI', 10),
                bg=row_bg,
                fg='#2D3748',
                anchor=tk.W
            )
            title_label.place(relx=0.18, rely=0.5, anchor=tk.W, relwidth=0.35)

            # البرنامج
            program_label = tk.Label(
                row,
                text=course.get('program', 'N/A')[:25] + ('...' if len(course.get('program', '')) > 25 else ''),
                font=('Segoe UI', 10),
                bg=row_bg,
                fg='#718096',
                anchor=tk.W
            )
            program_label.place(relx=0.53, rely=0.5, anchor=tk.W, relwidth=0.22)

            # الحالة
            status = course.get('status', 'draft')
            status_colors = {
                'draft': ('#FED7D7', '#C53030', '✎ مسودة'),
                'active': ('#C6F6D5', '#2F855A', '✓ نشط'),
                'completed': ('#BEE3F8', '#2C5282', '● مكتمل'),
                'approved': ('#B2F5EA', '#234E52', '✓ معتمد')
            }
            bg_color, fg_color, text = status_colors.get(status, ('#E2E8F0', '#4A5568', '• ' + status))

            status_label = tk.Label(
                row,
                text=text,
                font=('Segoe UI', 9, 'bold'),
                bg=bg_color,
                fg=fg_color,
                padx=10,
                pady=5
            )
            status_label.place(relx=0.75, rely=0.5, anchor=tk.W)

            # آخر تحديث
            modified = course.get('modified_date', '')
            date_str = modified[:10] if modified and len(modified) >= 10 else 'N/A'
            date_label = tk.Label(
                row,
                text=date_str,
                font=('Segoe UI', 9),
                bg=row_bg,
                fg='#A0AEC0',
                anchor=tk.W
            )
            date_label.place(relx=0.90, rely=0.5, anchor=tk.W, relwidth=0.10)

            # تأثير Hover للصف
            def on_enter(e, r=row, original_bg=row_bg):
                r.config(bg='#EDF2F7')
                for widget in r.winfo_children():
                    if isinstance(widget, tk.Label) and widget != status_label:
                        widget.config(bg='#EDF2F7')

            def on_leave(e, r=row, original_bg=row_bg):
                r.config(bg=original_bg)
                for widget in r.winfo_children():
                    if isinstance(widget, tk.Label) and widget != status_label:
                        widget.config(bg=original_bg)

            def on_click(e, cid=course.get('course_id')):
                self.main_window.open_course_id(cid)

            row.bind('<Enter>', on_enter)
            row.bind('<Leave>', on_leave)
            row.bind('<Button-1>', on_click)
            row.config(cursor='hand2')

            for widget in row.winfo_children():
                if widget != status_label and widget != separator:
                    widget.bind('<Enter>', on_enter)
                    widget.bind('<Leave>', on_leave)
                    widget.bind('<Button-1>', on_click)
                    widget.config(cursor='hand2')

    def create_notifications_section(self, parent):
        """إنشاء قسم الإشعارات والتنبيهات"""
        # حاوية قابلة للتمرير
        canvas = tk.Canvas(parent, bg='#FFFFFF', highlightthickness=0, height=400)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # إشعارات تجريبية
        notifications = [
            {
                'icon': '✓',
                'title': 'تم إكمال المقرر',
                'desc': 'تم إكمال مقرر "الإحصاء التطبيقي"',
                'time': 'منذ ساعتين',
                'color': '#48BB78'
            },
            {
                'icon': '✎',
                'title': 'مسودة جديدة',
                'desc': 'تم إنشاء مسودة مقرر جديد',
                'time': 'منذ 5 ساعات',
                'color': '#ED8936'
            },
            {
                'icon': '▣',
                'title': 'تقرير جاهز',
                'desc': 'تقرير المخرجات جاهز للمراجعة',
                'time': 'أمس',
                'color': '#667EEA'
            },
            {
                'icon': 'i',
                'title': 'تحديث النظام',
                'desc': 'تحديث جديد متوفر للنظام',
                'time': 'منذ يومين',
                'color': '#4299E1'
            },
            {
                'icon': '●',
                'title': 'تذكير',
                'desc': 'موعد مراجعة المقررات قريب',
                'time': 'منذ 3 أيام',
                'color': '#9B59B6'
            }
        ]

        for i, notif in enumerate(notifications):
            self.create_notification_item(scrollable_frame, notif, i == 0)

    def create_notification_item(self, parent, notif, is_first):
        """إنشاء عنصر إشعار"""
        # الإطار
        item = tk.Frame(parent, bg='#FFFFFF', cursor='hand2')
        item.pack(fill=tk.X, padx=20, pady=(15 if is_first else 10, 0))

        # الأيقونة
        icon_frame = tk.Frame(item, bg=notif['color'], width=45, height=45)
        icon_frame.pack(side=tk.LEFT, padx=(0, 12))
        icon_frame.pack_propagate(False)

        tk.Label(
            icon_frame,
            text=notif['icon'],
            font=('Segoe UI', 18),
            bg=notif['color'],
            fg='#FFFFFF'
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # المحتوى
        content = tk.Frame(item, bg='#FFFFFF')
        content.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # العنوان
        title_label = tk.Label(
            content,
            text=notif['title'],
            font=('Segoe UI', 11, 'bold'),
            bg='#FFFFFF',
            fg='#2D3748',
            anchor=tk.W
        )
        title_label.pack(anchor=tk.W)

        # الوصف
        desc_label = tk.Label(
            content,
            text=notif['desc'],
            font=('Segoe UI', 9),
            bg='#FFFFFF',
            fg='#718096',
            anchor=tk.W,
            wraplength=200
        )
        desc_label.pack(anchor=tk.W, pady=(3, 0))

        # الوقت
        time_label = tk.Label(
            content,
            text=notif['time'],
            font=('Segoe UI', 8),
            bg='#FFFFFF',
            fg='#A0AEC0',
            anchor=tk.W
        )
        time_label.pack(anchor=tk.W, pady=(5, 0))

        # خط فاصل
        separator = tk.Frame(parent, bg='#E2E8F0', height=1)
        separator.pack(fill=tk.X, padx=20, pady=(10, 0))

        # تأثير Hover
        def on_enter(e):
            item.config(bg='#F7FAFC')
            content.config(bg='#F7FAFC')
            title_label.config(bg='#F7FAFC')
            desc_label.config(bg='#F7FAFC')
            time_label.config(bg='#F7FAFC')

        def on_leave(e):
            item.config(bg='#FFFFFF')
            content.config(bg='#FFFFFF')
            title_label.config(bg='#FFFFFF')
            desc_label.config(bg='#FFFFFF')
            time_label.config(bg='#FFFFFF')

        item.bind('<Enter>', on_enter)
        item.bind('<Leave>', on_leave)
        for widget in [content, title_label, desc_label, time_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)

    def update_time(self):
        """تحديث الوقت الحالي"""
        current_time = datetime.now().strftime('•  %I:%M:%S %p')
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)
