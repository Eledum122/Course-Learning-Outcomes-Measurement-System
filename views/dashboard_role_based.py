# -*- coding: utf-8 -*-
"""
لوحة التحكم حسب الصلاحيات - تعرض معلومات مخصصة لكل دور
Role-Based Dashboard - Shows customized information for each role
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import COLORS, FONTS
from managers.academic_program_manager import AcademicProgramManager
from translations import get_language


class RoleBasedDashboard(tk.Frame):
    """لوحة تحكم تفاعلية حسب صلاحيات المستخدم"""

    def __init__(self, parent, user, access_control, course_manager, main_window):
        super().__init__(parent, bg='#F0F4F8')

        self.user = user
        self.access_control = access_control
        self.course_manager = course_manager
        self.main_window = main_window
        self.program_manager = AcademicProgramManager()
        self.language = get_language()
        self.is_rtl = (self.language == 'ar')

        self.create_ui()

    def text(self, ar_text, en_text):
        """دالة مساعدة للحصول على النص حسب اللغة"""
        return ar_text if self.is_rtl else en_text

    def create_ui(self):
        """إنشاء الواجهة"""
        # ═══════════════════════════════════════════════════════════
        # 1. القسم الترحيبي العلوي
        # ═══════════════════════════════════════════════════════════
        self.create_header()

        # ═══════════════════════════════════════════════════════════
        # 2. حاوية قابلة للتمرير
        # ═══════════════════════════════════════════════════════════
        main_canvas = tk.Canvas(self, bg='#F0F4F8', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = tk.Frame(main_canvas, bg='#F0F4F8')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ربط عجلة الماوس بالتمرير
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ═══════════════════════════════════════════════════════════
        # 3. المحتوى حسب الدور
        # ═══════════════════════════════════════════════════════════
        self.create_role_content()

    def create_header(self):
        """إنشاء القسم الترحيبي"""
        header = tk.Frame(self, bg='#FFFFFF', height=120)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # شريط تدرج لوني
        gradient_bar = tk.Frame(header, bg='#667EEA', height=4)
        gradient_bar.pack(fill=tk.X)

        # محتوى الترويسة
        header_content = tk.Frame(header, bg='#FFFFFF')
        header_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=15)

        # الترحيب
        left_frame = tk.Frame(header_content, bg='#FFFFFF')
        left_frame.pack(side=tk.RIGHT if self.is_rtl else tk.LEFT, fill=tk.Y)

        # التحية حسب الوقت
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting_ar, greeting_en, icon = "صباح الخير", "Good Morning", "☀️"
        elif 12 <= hour < 17:
            greeting_ar, greeting_en, icon = "مساء الخير", "Good Afternoon", "☁️"
        else:
            greeting_ar, greeting_en, icon = "مساء الخير", "Good Evening", "🌙"

        greeting = self.text(greeting_ar, greeting_en)

        # العنوان
        title = tk.Label(
            left_frame,
            text=f"{icon}  {greeting}, {self.user.full_name}" if not self.is_rtl else f"{icon}  {greeting}، {self.user.full_name}",
            font=('Arial', 22, 'bold'),
            bg='#FFFFFF',
            fg='#1A202C'
        )
        title.pack(anchor=tk.E if self.is_rtl else tk.W)

        # الدور
        role_text = self.get_role_display()
        subtitle = tk.Label(
            left_frame,
            text=f"🎯 {role_text}",
            font=('Arial', 11),
            bg='#FFFFFF',
            fg='#667EEA'
        )
        subtitle.pack(anchor=tk.E if self.is_rtl else tk.W, pady=(5, 0))

        # التاريخ والوقت
        right_frame = tk.Frame(header_content, bg='#FFFFFF')
        right_frame.pack(side=tk.LEFT if self.is_rtl else tk.RIGHT, fill=tk.Y)

        date_str = datetime.now().strftime("%d %B %Y")
        date_label = tk.Label(
            right_frame,
            text=f"📅  {date_str}",
            font=('Arial', 11),
            bg='#FFFFFF',
            fg='#4A5568'
        )
        date_label.pack(anchor=tk.W if self.is_rtl else tk.E)

    def get_role_display(self):
        """الحصول على نص عرض الدور"""
        if self.user.has_role('admin'):
            return self.text("مدير النظام - صلاحيات كاملة", "System Administrator - Full Access")
        elif self.user.has_role('program_coordinator'):
            return self.text("منسق برنامج أكاديمي", "Academic Program Coordinator")
        elif self.user.has_role('course_coordinator'):
            return self.text("منسق مقرر", "Course Coordinator")
        elif self.user.has_role('section_instructor'):
            return self.text("مدرس شعبة", "Section Instructor")
        return self.text("مستخدم", "User")

    def create_role_content(self):
        """إنشاء المحتوى حسب الدور"""
        if self.user.has_role('admin'):
            self.create_admin_dashboard()
        elif self.user.has_role('program_coordinator'):
            self.create_program_coordinator_dashboard()
        elif self.user.has_role('course_coordinator'):
            self.create_course_coordinator_dashboard()
        elif self.user.has_role('section_instructor'):
            self.create_section_instructor_dashboard()

    # ═══════════════════════════════════════════════════════════
    # لوحة تحكم المدير
    # ═══════════════════════════════════════════════════════════

    def create_admin_dashboard(self):
        """لوحة تحكم المدير - عرض شامل"""
        container = tk.Frame(self.scrollable_frame, bg='#F0F4F8')
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # بطاقات الإحصائيات
        stats_frame = tk.Frame(container, bg='#F0F4F8')
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        # إحصائيات عامة
        programs = self.program_manager.get_all_programs()
        courses = self.course_manager.list_all_courses()
        users = len(self.access_control.users)

        self.create_stat_card(stats_frame,
                             self.text("البرامج الأكاديمية", "Academic Programs"),
                             len(programs), "🎓", "#667EEA", 0)
        self.create_stat_card(stats_frame,
                             self.text("المقررات", "Courses"),
                             len(courses), "📚", "#48BB78", 1)
        self.create_stat_card(stats_frame,
                             self.text("المستخدمين", "Users"),
                             users, "👥", "#F6AD55", 2)

        # قائمة البرامج الأكاديمية
        self.create_section_title(container, f"📋 {self.text('البرامج الأكاديمية', 'Academic Programs')}")
        self.create_programs_list(container, programs)

    def create_program_coordinator_dashboard(self):
        """لوحة تحكم منسق البرنامج"""
        container = tk.Frame(self.scrollable_frame, bg='#F0F4F8')
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # الحصول على البرامج المعينة
        all_programs = self.program_manager.get_all_programs()
        my_programs = [p for p in all_programs if p.program_id in self.user.assigned_programs]

        if not my_programs:
            self.create_empty_message(container,
                                     self.text("لم يتم تعيين أي برامج أكاديمية لك",
                                              "No academic programs have been assigned to you"))
            return

        # بطاقات الإحصائيات
        stats_frame = tk.Frame(container, bg='#F0F4F8')
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        # حساب إحصائيات المقررات
        all_courses = self.course_manager.list_all_courses()
        program_names = [p.program_name_ar for p in my_programs] + [p.program_name_en for p in my_programs]
        my_courses = [c for c in all_courses if c.get('program', '') in program_names]

        self.create_stat_card(stats_frame,
                             self.text("برامجي", "My Programs"),
                             len(my_programs), "🎓", "#667EEA", 0)
        self.create_stat_card(stats_frame,
                             self.text("المقررات", "Courses"),
                             len(my_courses), "📚", "#48BB78", 1)
        self.create_stat_card(stats_frame,
                             self.text("الشعب", "Sections"),
                             self.count_sections_for_courses(my_courses), "👥", "#F6AD55", 2)

        # عرض البرامج
        self.create_section_title(container, f"🎯 {self.text('برامجي الأكاديمية', 'My Academic Programs')}")
        self.create_programs_detail_list(container, my_programs)

    def create_course_coordinator_dashboard(self):
        """لوحة تحكم منسق المقرر"""
        container = tk.Frame(self.scrollable_frame, bg='#F0F4F8')
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # الحصول على المقررات المعينة
        all_courses = self.course_manager.list_all_courses()
        my_courses = [c for c in all_courses if c['course_id'] in self.user.assigned_courses]

        if not my_courses:
            self.create_empty_message(container,
                                     self.text("لم يتم تعيين أي مقررات لك",
                                              "No courses have been assigned to you"))
            return

        # بطاقات الإحصائيات
        stats_frame = tk.Frame(container, bg='#F0F4F8')
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        self.create_stat_card(stats_frame,
                             self.text("مقرراتي", "My Courses"),
                             len(my_courses), "📚", "#667EEA", 0)
        self.create_stat_card(stats_frame,
                             self.text("الشعب", "Sections"),
                             self.count_sections_for_courses(my_courses), "👥", "#48BB78", 1)

        # عرض المقررات
        self.create_section_title(container, f"📚 {self.text('مقرراتي', 'My Courses')}")
        self.create_courses_detail_list(container, my_courses)

    def create_section_instructor_dashboard(self):
        """لوحة تحكم مدرس الشعبة"""
        container = tk.Frame(self.scrollable_frame, bg='#F0F4F8')
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # الحصول على الشعب المعينة
        if not self.user.assigned_sections:
            self.create_empty_message(container,
                                     self.text("لم يتم تعيين أي شعب لك",
                                              "No sections have been assigned to you"))
            return

        # حساب عدد الشعب
        total_sections = sum(len(sections) for sections in self.user.assigned_sections.values())

        # بطاقات الإحصائيات
        stats_frame = tk.Frame(container, bg='#F0F4F8')
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        self.create_stat_card(stats_frame,
                             self.text("المقررات", "Courses"),
                             len(self.user.assigned_sections), "📚", "#667EEA", 0)
        self.create_stat_card(stats_frame,
                             self.text("شعبي", "My Sections"),
                             total_sections, "👥", "#48BB78", 1)

        # عرض الشعب
        self.create_section_title(container, f"👥 {self.text('شعبي الدراسية', 'My Sections')}")
        self.create_sections_detail_list(container)

    # ═══════════════════════════════════════════════════════════
    # مكونات الواجهة
    # ═══════════════════════════════════════════════════════════

    def create_stat_card(self, parent, title, value, icon, color, column):
        """إنشاء بطاقة إحصائية"""
        card = tk.Frame(parent, bg='#FFFFFF', relief=tk.FLAT, bd=0)
        card.grid(row=0, column=column, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(column, weight=1)

        # إضافة ظل (محاكاة)
        shadow = tk.Frame(card, bg='#E2E8F0', height=2)
        shadow.pack(side=tk.BOTTOM, fill=tk.X)

        # المحتوى
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # الأيقونة والقيمة
        icon_label = tk.Label(
            content,
            text=icon,
            font=('Arial', 32),
            bg='#FFFFFF'
        )
        icon_label.pack()

        value_label = tk.Label(
            content,
            text=str(value),
            font=('Arial', 28, 'bold'),
            bg='#FFFFFF',
            fg=color
        )
        value_label.pack()

        title_label = tk.Label(
            content,
            text=title,
            font=('Arial', 12),
            bg='#FFFFFF',
            fg='#718096'
        )
        title_label.pack()

    def create_mini_stat(self, parent, label, value, color):
        """إنشاء إحصائية صغيرة مضمنة"""
        stat_frame = tk.Frame(parent, bg='#F7FAFC')
        stat_frame.pack(side=tk.RIGHT if self.is_rtl else tk.LEFT, padx=8)

        value_label = tk.Label(
            stat_frame,
            text=str(value),
            font=('Arial', 14, 'bold'),
            bg='#F7FAFC',
            fg=color
        )
        value_label.pack()

        label_label = tk.Label(
            stat_frame,
            text=label,
            font=('Arial', 9),
            bg='#F7FAFC',
            fg='#718096'
        )
        label_label.pack()

    def create_section_title(self, parent, title):
        """إنشاء عنوان قسم"""
        title_frame = tk.Frame(parent, bg='#F0F4F8')
        title_frame.pack(fill=tk.X, pady=(20, 10))

        title_label = tk.Label(
            title_frame,
            text=title,
            font=('Arial', 18, 'bold'),
            bg='#F0F4F8',
            fg='#2D3748'
        )
        title_label.pack(anchor=tk.E if self.is_rtl else tk.W)

        # خط فاصل
        separator = tk.Frame(title_frame, bg='#667EEA', height=3)
        separator.pack(fill=tk.X, pady=(5, 0))

    def create_empty_message(self, parent, message):
        """إنشاء رسالة فارغة"""
        card = tk.Frame(parent, bg='#FFFFFF', relief=tk.FLAT)
        card.pack(fill=tk.BOTH, expand=True, pady=20)

        icon = tk.Label(
            card,
            text="📭",
            font=('Arial', 64),
            bg='#FFFFFF'
        )
        icon.pack(pady=(40, 20))

        msg = tk.Label(
            card,
            text=message,
            font=('Arial', 16),
            bg='#FFFFFF',
            fg='#718096'
        )
        msg.pack(pady=(0, 40))

    def create_programs_list(self, parent, programs):
        """إنشاء قائمة البرامج (مدير النظام)"""
        for program in programs:
            self.create_program_card(parent, program, detailed=False)

    def create_programs_detail_list(self, parent, programs):
        """إنشاء قائمة البرامج المفصلة"""
        for program in programs:
            self.create_program_card(parent, program, detailed=True)

    def create_program_card(self, parent, program, detailed=False):
        """إنشاء بطاقة برنامج"""
        card = tk.Frame(parent, bg='#FFFFFF', relief=tk.FLAT)
        card.pack(fill=tk.X, pady=10)

        # المحتوى
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # العنوان
        program_name = program.program_name_ar if self.is_rtl else program.program_name_en
        title = tk.Label(
            content,
            text=f"🎓 {program_name}",
            font=('Arial', 14, 'bold'),
            bg='#FFFFFF',
            fg='#2D3748',
            anchor=tk.E if self.is_rtl else tk.W
        )
        title.pack(fill=tk.X)

        # التفاصيل الأساسية
        details_frame = tk.Frame(content, bg='#FFFFFF')
        details_frame.pack(fill=tk.X, pady=(10, 0))

        dept = program.department_ar if self.is_rtl else program.department_en
        college = program.college_ar if self.is_rtl else program.college_en
        info_text = f"📌 {dept} | 🏛️ {college}"

        if program.coordinator_id:
            # الحصول على اسم المنسق من user_id
            coordinator = self.access_control.get_user(program.coordinator_id)
            if coordinator:
                coord_label = self.text("المنسق", "Coordinator")
                info_text += f" | 👤 {coord_label}: {coordinator.full_name}"

        details = tk.Label(
            details_frame,
            text=info_text,
            font=('Arial', 10),
            bg='#FFFFFF',
            fg='#718096',
            anchor=tk.E if self.is_rtl else tk.W
        )
        details.pack(fill=tk.X)

        # إحصائيات المقررات (للمدير أو التفصيلي)
        all_courses = self.course_manager.list_all_courses()
        program_courses = [c for c in all_courses
                         if c.get('program', '') in [program.program_name_ar, program.program_name_en]]

        if program_courses or detailed:
            # إطار الإحصائيات
            stats_frame = tk.Frame(content, bg='#F7FAFC')
            stats_frame.pack(fill=tk.X, pady=(10, 0))

            # حساب الإحصائيات
            total_courses = len(program_courses)
            completed_courses = 0
            active_courses = 0
            total_sections = 0

            # استيراد مدير الشعب
            from managers.section_manager import SectionManager
            section_manager = SectionManager()

            for course_data in program_courses:
                try:
                    course = self.course_manager.load_course(course_data['course_id'])
                    if course:
                        # حساب حالة المقرر
                        if course.stage_3_completed:
                            completed_courses += 1
                        elif course.stage_1_completed:
                            active_courses += 1

                        # حساب الشعب من الملفات المنفصلة
                        course_sections = section_manager.get_sections_by_course(course_data['course_id'])
                        total_sections += len(course_sections)
                except:
                    pass

            incomplete_courses = total_courses - completed_courses

            # عرض الإحصائيات في صفوف
            stats_container = tk.Frame(stats_frame, bg='#F7FAFC')
            stats_container.pack(fill=tk.X, padx=15, pady=10)

            # الصف الأول: المقررات
            row1 = tk.Frame(stats_container, bg='#F7FAFC')
            row1.pack(fill=tk.X, pady=(0, 8))

            self.create_mini_stat(row1,
                                 f"📚 {self.text('إجمالي المقررات', 'Total Courses')}",
                                 total_courses, "#667EEA")
            self.create_mini_stat(row1,
                                 f"✅ {self.text('مكتملة', 'Completed')}",
                                 completed_courses, "#48BB78")
            self.create_mini_stat(row1,
                                 f"⏳ {self.text('غير مكتملة', 'Incomplete')}",
                                 incomplete_courses, "#F6AD55")

            # الصف الثاني: الشعب ونسبة الإنجاز
            row2 = tk.Frame(stats_container, bg='#F7FAFC')
            row2.pack(fill=tk.X)

            self.create_mini_stat(row2,
                                 f"👥 {self.text('الشعب', 'Sections')}",
                                 total_sections, "#9F7AEA")

            # نسبة الإنجاز
            completion_rate = (completed_courses / total_courses * 100) if total_courses > 0 else 0
            self.create_mini_stat(row2,
                                 f"📊 {self.text('نسبة الإنجاز', 'Completion Rate')}",
                                 f"{completion_rate:.0f}%",
                                 "#38B2AC" if completion_rate >= 50 else "#F6AD55")

    def create_courses_detail_list(self, parent, courses):
        """إنشاء قائمة المقررات المفصلة"""
        for course in courses:
            self.create_course_card(parent, course)

    def create_course_card(self, parent, course):
        """إنشاء بطاقة مقرر"""
        card = tk.Frame(parent, bg='#FFFFFF', relief=tk.FLAT)
        card.pack(fill=tk.X, pady=10)

        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # العنوان
        title = tk.Label(
            content,
            text=f"📚 {course.get('course_code', 'N/A')} - {course.get('course_title', 'N/A')}",
            font=('Arial', 14, 'bold'),
            bg='#FFFFFF',
            fg='#2D3748',
            anchor=tk.E if self.is_rtl else tk.W
        )
        title.pack(fill=tk.X)

        # التفاصيل
        program_label = self.text("البرنامج", "Program")
        year_label = self.text("العام الدراسي", "Academic Year")
        info_text = f"🎓 {course.get('program', 'N/A')} | 📅 {course.get('academic_year', 'N/A')}"
        details = tk.Label(
            content,
            text=info_text,
            font=('Arial', 10),
            bg='#FFFFFF',
            fg='#718096',
            anchor=tk.E if self.is_rtl else tk.W
        )
        details.pack(fill=tk.X, pady=(5, 0))

    def create_sections_detail_list(self, parent):
        """إنشاء قائمة الشعب المفصلة"""
        for course_id, sections in self.user.assigned_sections.items():
            # تحميل معلومات المقرر
            try:
                course = self.course_manager.load_course(course_id)
                if course:
                    self.create_instructor_course_card(parent, course, sections)
            except:
                pass

    def create_instructor_course_card(self, parent, course, sections):
        """إنشاء بطاقة مقرر لمدرس الشعبة"""
        card = tk.Frame(parent, bg='#FFFFFF', relief=tk.FLAT)
        card.pack(fill=tk.X, pady=10)

        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # العنوان
        title = tk.Label(
            content,
            text=f"📚 {course.info.course_code} - {course.info.course_title}",
            font=('Arial', 14, 'bold'),
            bg='#FFFFFF',
            fg='#2D3748',
            anchor=tk.E if self.is_rtl else tk.W
        )
        title.pack(fill=tk.X)

        # الشعب
        sections_text = "، ".join(sections) if self.is_rtl else ", ".join(sections)
        my_sections_label = self.text("شعبي", "My Sections")
        sections_label = tk.Label(
            content,
            text=f"👥 {my_sections_label}: {sections_text}",
            font=('Arial', 11, 'bold'),
            bg='#FFFFFF',
            fg='#667EEA',
            anchor=tk.E if self.is_rtl else tk.W
        )
        sections_label.pack(fill=tk.X, pady=(5, 0))

    def count_sections_for_courses(self, courses):
        """حساب عدد الشعب في مجموعة مقررات"""
        from managers.section_manager import SectionManager
        section_manager = SectionManager()

        total = 0
        for course_data in courses:
            try:
                # حساب الشعب من الملفات المنفصلة
                course_sections = section_manager.get_sections_by_course(course_data['course_id'])
                total += len(course_sections)
            except:
                pass
        return total

    def update_time(self):
        """تحديث الوقت"""
        # يمكن إضافة تحديث الوقت هنا إذا لزم الأمر
        pass
