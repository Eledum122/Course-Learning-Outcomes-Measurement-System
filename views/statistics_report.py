"""
تقرير الإحصائيات الشاملة
Comprehensive Statistics Report
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict
from datetime import datetime
from models import Course
from managers.course_manager import CourseManager
from managers.access_control import AccessControl
from managers.academic_program_manager import AcademicProgramManager
from managers.section_manager import SectionManager
from config import FONTS, COLORS
from translations import t, get_language


class StatisticsReport(tk.Frame):
    """صفحة تقرير الإحصائيات الشاملة"""

    def __init__(self, parent, user, access_control: AccessControl):
        super().__init__(parent, bg='#F0F4F8')
        self.user = user
        self.access_control = access_control
        self.course_manager = CourseManager()
        self.program_manager = AcademicProgramManager()
        self.section_manager = SectionManager()
        self.language = get_language()
        self.is_rtl = (self.language == 'ar')

        self.create_ui()

    def text(self, ar_text, en_text):
        """دالة مساعدة للحصول على النص حسب اللغة"""
        return ar_text if self.is_rtl else en_text

    def create_ui(self):
        """إنشاء واجهة المستخدم"""
        # إطار رئيسي مع شريط تمرير
        main_container = tk.Frame(self, bg='#F0F4F8')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Canvas مع شريط تمرير
        canvas = tk.Canvas(main_container, bg='#F0F4F8', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F0F4F8')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ربط عجلة الماوس
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # المحتوى
        self.create_content(scrollable_frame)

    def create_content(self, parent):
        """إنشاء محتوى التقرير"""
        # العنوان الرئيسي
        self.create_header(parent)

        # ملخص عام
        self.create_summary_section(parent)

        # تقرير البرامج
        self.create_programs_section(parent)

        # تقرير الشعب
        self.create_sections_section(parent)

        # إحصائيات المستخدمين (للمدير فقط)
        if self.user.has_role('admin'):
            self.create_users_section(parent)

    def create_header(self, parent):
        """إنشاء رأس التقرير"""
        header_frame = tk.Frame(parent, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        # العنوان
        title = self.text(
            "📊 تقرير الإحصائيات الشاملة",
            "📊 Comprehensive Statistics Report"
        )
        tk.Label(
            header_frame,
            text=title,
            font=('Arial', 24, 'bold'),
            bg='#FFFFFF',
            fg='#2D3748'
        ).pack(pady=20)

        # معلومات التقرير
        info_frame = tk.Frame(header_frame, bg='#F7FAFC')
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # التاريخ والوقت
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d %H:%M')

        tk.Label(
            info_frame,
            text=f"📅 {self.text('تاريخ التقرير', 'Report Date')}: {date_str}",
            font=('Arial', 11),
            bg='#F7FAFC',
            fg='#4A5568',
            anchor=tk.E if self.is_rtl else tk.W
        ).pack(fill=tk.X, padx=15, pady=5)

        # المستخدم
        user_name = f"{self.user.full_name} ({self.user.user_id})"
        tk.Label(
            info_frame,
            text=f"👤 {self.text('المستخدم', 'User')}: {user_name}",
            font=('Arial', 11),
            bg='#F7FAFC',
            fg='#4A5568',
            anchor=tk.E if self.is_rtl else tk.W
        ).pack(fill=tk.X, padx=15, pady=5)

        # الصلاحيات
        roles = ', '.join(self.user.roles) if isinstance(self.user.roles, list) else str(self.user.roles)
        tk.Label(
            info_frame,
            text=f"🔑 {self.text('الصلاحيات', 'Roles')}: {roles}",
            font=('Arial', 11),
            bg='#F7FAFC',
            fg='#4A5568',
            anchor=tk.E if self.is_rtl else tk.W
        ).pack(fill=tk.X, padx=15, pady=5)

    def create_summary_section(self, parent):
        """إنشاء قسم الملخص العام"""
        section_frame = self.create_section_frame(
            parent,
            self.text("📈 الملخص العام", "📈 General Summary")
        )

        # جمع البيانات حسب الصلاحيات
        stats = self.gather_statistics()

        # عرض الإحصائيات في شبكة
        grid_frame = tk.Frame(section_frame, bg='#FFFFFF')
        grid_frame.pack(fill=tk.X, padx=20, pady=10)

        # الصف الأول
        row1 = tk.Frame(grid_frame, bg='#FFFFFF')
        row1.pack(fill=tk.X, pady=5)

        self.create_stat_card(row1, "🎓", self.text("البرامج الأكاديمية", "Academic Programs"),
                             stats['total_programs'], "#667EEA")
        self.create_stat_card(row1, "📚", self.text("المقررات", "Courses"),
                             stats['total_courses'], "#48BB78")
        self.create_stat_card(row1, "👥", self.text("الشعب", "Sections"),
                             stats['total_sections'], "#9F7AEA")

        # الصف الثاني
        row2 = tk.Frame(grid_frame, bg='#FFFFFF')
        row2.pack(fill=tk.X, pady=5)

        self.create_stat_card(row2, "✅", self.text("مقررات مكتملة", "Completed Courses"),
                             stats['completed_courses'], "#38B2AC")
        self.create_stat_card(row2, "⏳", self.text("مقررات قيد العمل", "In Progress"),
                             stats['in_progress_courses'], "#F6AD55")
        completion_rate = f"{stats['completion_rate']:.1f}%"
        self.create_stat_card(row2, "📊", self.text("نسبة الإنجاز", "Completion Rate"),
                             completion_rate, "#ED8936")

        # الصف الثالث - إحصائيات الشعب
        row3 = tk.Frame(grid_frame, bg='#FFFFFF')
        row3.pack(fill=tk.X, pady=5)

        self.create_stat_card(row3, "👨‍🎓", self.text("إجمالي الطلاب", "Total Students"),
                             stats['total_students'], "#4299E1")
        self.create_stat_card(row3, "📝", self.text("طلاب منتظمون", "Regular Students"),
                             stats['regular_students'], "#48BB78")
        self.create_stat_card(row3, "📋", self.text("أنشطة التقييم", "Assessment Activities"),
                             stats['total_activities'], "#805AD5")

    def create_programs_section(self, parent):
        """إنشاء قسم تقرير البرامج"""
        section_frame = self.create_section_frame(
            parent,
            self.text("🎓 تفاصيل البرامج الأكاديمية", "🎓 Academic Programs Details")
        )

        # الحصول على البرامج حسب الصلاحيات
        programs = self.get_accessible_programs()

        if not programs:
            tk.Label(
                section_frame,
                text=self.text("لا توجد برامج متاحة", "No programs available"),
                font=('Arial', 12),
                bg='#FFFFFF',
                fg='#718096'
            ).pack(pady=20)
            return

        # جدول البرامج
        table_frame = tk.Frame(section_frame, bg='#FFFFFF')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # رأس الجدول
        headers = [
            self.text("البرنامج", "Program"),
            self.text("القسم", "Department"),
            self.text("الكلية", "Faculty"),
            self.text("المقررات", "Courses"),
            self.text("المكتملة", "Completed"),
            self.text("الشعب", "Sections"),
            self.text("الطلاب", "Students")
        ]

        # عرض كل عمود بالبكسل
        column_widths_chars = [20, 22, 18, 10, 12, 10, 10]

        header_row = tk.Frame(table_frame, bg='#EDF2F7')
        header_row.pack(fill=tk.X, pady=(0, 2))

        # تكوين الأعمدة
        for i in range(len(headers)):
            header_row.grid_columnconfigure(i, weight=1, minsize=column_widths_chars[i]*8)

        for i, header in enumerate(headers):
            col_index = len(headers) - 1 - i if self.is_rtl else i
            tk.Label(
                header_row,
                text=header,
                font=('Arial', 11, 'bold'),
                bg='#EDF2F7',
                fg='#2D3748',
                anchor=tk.CENTER
            ).grid(row=0, column=col_index, sticky='nsew', padx=2, pady=8)

        # صفوف البيانات
        for program in programs:
            self.create_program_row(table_frame, program)

    def create_program_row(self, parent, program):
        """إنشاء صف بيانات برنامج"""
        # جمع إحصائيات البرنامج
        stats = self.get_program_statistics(program)

        row = tk.Frame(parent, bg='#FFFFFF', relief=tk.RIDGE, bd=1)
        row.pack(fill=tk.X, pady=1)

        # البيانات
        program_name = program.program_name_ar if self.is_rtl else program.program_name_en
        department = program.department_ar if self.is_rtl else program.department_en
        faculty = program.college_ar if self.is_rtl else program.college_en

        data = [
            program_name,
            department,
            faculty,
            str(stats['courses']),
            str(stats['completed']),
            str(stats['sections']),
            str(stats['students'])
        ]

        column_widths_chars = [20, 22, 18, 10, 12, 10, 10]

        # تكوين الأعمدة
        for i in range(len(data)):
            row.grid_columnconfigure(i, weight=1, minsize=column_widths_chars[i]*8)

        for i, value in enumerate(data):
            col_index = len(data) - 1 - i if self.is_rtl else i
            label = tk.Label(
                row,
                text=value,
                font=('Arial', 10),
                bg='#FFFFFF',
                fg='#2D3748',
                anchor=tk.CENTER
            )
            label.grid(row=0, column=col_index, sticky='nsew', padx=2, pady=8)

    def create_courses_section(self, parent):
        """إنشاء قسم تقرير المقررات"""
        section_frame = self.create_section_frame(
            parent,
            self.text("📚 تفاصيل المقررات", "📚 Courses Details")
        )

        # الحصول على المقررات حسب الصلاحيات
        courses = self.get_accessible_courses()

        if not courses:
            tk.Label(
                section_frame,
                text=self.text("لا توجد مقررات متاحة", "No courses available"),
                font=('Arial', 12),
                bg='#FFFFFF',
                fg='#718096'
            ).pack(pady=20)
            return

        # جدول المقررات
        table_frame = tk.Frame(section_frame, bg='#FFFFFF')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # رأس الجدول
        headers = [
            self.text("رمز المقرر", "Course Code"),
            self.text("اسم المقرر", "Course Name"),
            self.text("البرنامج", "Program"),
            self.text("المخرجات", "CLOs"),
            self.text("الأنشطة", "Activities"),
            self.text("الشعب", "Sections"),
            self.text("الحالة", "Status")
        ]

        # عرض كل عمود
        column_widths = [12, 25, 20, 8, 10, 8, 15]

        header_row = tk.Frame(table_frame, bg='#EDF2F7', height=40)
        header_row.pack(fill=tk.X, pady=(0, 2))

        for i, header in enumerate(headers):
            tk.Label(
                header_row,
                text=header,
                font=('Arial', 11, 'bold'),
                bg='#EDF2F7',
                fg='#2D3748',
                anchor=tk.CENTER,
                width=column_widths[i]
            ).pack(side=tk.RIGHT if self.is_rtl else tk.LEFT, padx=3, pady=8)

        # صفوف البيانات
        for course_data in courses[:20]:  # عرض أول 20 مقرر
            self.create_course_row(table_frame, course_data)

        # رسالة إذا كان هناك المزيد
        if len(courses) > 20:
            tk.Label(
                table_frame,
                text=self.text(f"... و {len(courses) - 20} مقرر آخر", f"... and {len(courses) - 20} more courses"),
                font=('Arial', 10, 'italic'),
                bg='#FFFFFF',
                fg='#718096'
            ).pack(pady=10)

    def create_course_row(self, parent, course_data):
        """إنشاء صف بيانات مقرر"""
        try:
            course = self.course_manager.load_course(course_data['course_id'])
            if not course:
                return

            row = tk.Frame(parent, bg='#FFFFFF', relief=tk.RIDGE, bd=1)
            row.pack(fill=tk.X, pady=1)

            # البيانات
            course_code = course.info.course_code
            course_name = course.info.course_name_ar[:30] if self.is_rtl else course.info.course_name_en[:30]
            program = course_data.get('program', 'N/A')[:20]
            clos_count = len(course.clos)
            activities_count = len(course.activities)
            sections_count = len(self.section_manager.get_sections_by_course(course.course_id))

            # تحديد الحالة
            if course.stage_3_completed:
                status = self.text("✅ مكتمل", "✅ Completed")
                status_color = "#48BB78"
            elif course.stage_2_completed:
                status = self.text("📝 المرحلة 3", "📝 Stage 3")
                status_color = "#4299E1"
            elif course.stage_1_completed:
                status = self.text("📋 المرحلة 2", "📋 Stage 2")
                status_color = "#F6AD55"
            else:
                status = self.text("⏳ المرحلة 1", "⏳ Stage 1")
                status_color = "#718096"

            data = [
                course_code,
                course_name,
                program,
                str(clos_count),
                str(activities_count),
                str(sections_count),
                status
            ]

            colors = ['#2D3748'] * 6 + [status_color]
            column_widths = [12, 25, 20, 8, 10, 8, 15]

            for i, (value, color) in enumerate(zip(data, colors)):
                label = tk.Label(
                    row,
                    text=value,
                    font=('Arial', 9),
                    bg='#FFFFFF',
                    fg=color,
                    anchor=tk.CENTER,
                    width=column_widths[i]
                )
                label.pack(side=tk.RIGHT if self.is_rtl else tk.LEFT, padx=3, pady=6)

        except Exception as e:
            pass

    def create_sections_section(self, parent):
        """إنشاء قسم تقرير الشعب"""
        section_frame = self.create_section_frame(
            parent,
            self.text("👥 تفاصيل الشعب", "👥 Sections Details")
        )

        # الحصول على الشعب حسب الصلاحيات
        sections = self.get_accessible_sections()

        if not sections:
            tk.Label(
                section_frame,
                text=self.text("لا توجد شعب متاحة", "No sections available"),
                font=('Arial', 12),
                bg='#FFFFFF',
                fg='#718096'
            ).pack(pady=20)
            return

        # ملخص إحصائيات الشعب
        summary_frame = tk.Frame(section_frame, bg='#F7FAFC')
        summary_frame.pack(fill=tk.X, padx=20, pady=10)

        total_students = sum(len(s.students) for s in sections)
        regular_students = sum(len([st for st in s.students if st.status.value == 'Regular']) for s in sections)
        completed_sections = sum(1 for s in sections if s.grades_data_completed)

        summary_row = tk.Frame(summary_frame, bg='#F7FAFC')
        summary_row.pack(fill=tk.X, pady=10)

        self.create_mini_stat_box(summary_row, self.text("إجمالي الشعب", "Total Sections"),
                                 len(sections), "#667EEA")
        self.create_mini_stat_box(summary_row, self.text("شعب مكتملة", "Completed Sections"),
                                 completed_sections, "#48BB78")
        self.create_mini_stat_box(summary_row, self.text("إجمالي الطلاب", "Total Students"),
                                 total_students, "#4299E1")
        self.create_mini_stat_box(summary_row, self.text("طلاب منتظمون", "Regular Students"),
                                 regular_students, "#38B2AC")

        # تجميع الشعب حسب البرنامج
        programs_sections = {}
        for section in sections:
            # الحصول على اسم البرنامج من المقرر مباشرة
            program_name = None
            try:
                course = self.course_manager.load_course(section.course_id)
                if course and hasattr(course, 'info') and hasattr(course.info, 'program'):
                    program_name = course.info.program
            except Exception as e:
                print(f"Error loading course for section {section.section_id}: {e}")

            if not program_name:
                # إذا لم يتم العثور على البرنامج، استخدم "غير مصنف"
                program_name = self.text("غير مصنف", "Unclassified")

            if program_name not in programs_sections:
                programs_sections[program_name] = []
            programs_sections[program_name].append(section)

        # إنشاء جدول لكل برنامج
        for program_name, program_sections in programs_sections.items():
            # إطار البرنامج
            program_frame = tk.Frame(section_frame, bg='#FFFFFF', relief=tk.RIDGE, bd=1)
            program_frame.pack(fill=tk.X, padx=20, pady=15)

            # عنوان البرنامج
            title_frame = tk.Frame(program_frame, bg='#667EEA')
            title_frame.pack(fill=tk.X)

            tk.Label(
                title_frame,
                text=f"📚 {program_name} ({len(program_sections)} {self.text('شعبة', 'sections')})",
                font=('Arial', 12, 'bold'),
                bg='#667EEA',
                fg='#FFFFFF',
                pady=10
            ).pack()

            # جدول الشعب
            table_frame = tk.Frame(program_frame, bg='#FFFFFF')
            table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # رأس الجدول
            headers = [
                self.text("رقم الشعبة", "Section #"),
                self.text("المقرر", "Course"),
                self.text("العام/الفصل", "Year/Sem"),
                self.text("المنسق", "Coordinator"),
                self.text("الطلاب", "Students"),
                self.text("منتظمون", "Regular"),
                self.text("الحالة", "Status")
            ]

            # عرض كل عمود بالبكسل
            column_widths_chars = [10, 10, 12, 18, 10, 10, 14]

            header_row = tk.Frame(table_frame, bg='#EDF2F7')
            header_row.pack(fill=tk.X, pady=(0, 2))

            # تكوين الأعمدة
            for i in range(len(headers)):
                header_row.grid_columnconfigure(i, weight=1, minsize=column_widths_chars[i]*8)

            for i, header in enumerate(headers):
                col_index = len(headers) - 1 - i if self.is_rtl else i
                tk.Label(
                    header_row,
                    text=header,
                    font=('Arial', 11, 'bold'),
                    bg='#EDF2F7',
                    fg='#2D3748',
                    anchor=tk.CENTER
                ).grid(row=0, column=col_index, sticky='nsew', padx=2, pady=8)

            # صفوف البيانات
            for section in program_sections:
                self.create_section_row(table_frame, section)

    def create_section_row(self, parent, section):
        """إنشاء صف بيانات شعبة"""
        row = tk.Frame(parent, bg='#FFFFFF', relief=tk.RIDGE, bd=1)
        row.pack(fill=tk.X, pady=1)

        # البيانات
        section_number = section.section_number

        # الحصول على رمز المقرر
        try:
            course = self.course_manager.load_course(section.course_id)
            course_code = course.info.course_code if course else section.course_id[:10]
        except:
            course_code = section.course_id[:10]

        year_sem = f"{section.academic_year}/{section.semester.value if hasattr(section.semester, 'value') else section.semester}"
        coordinator = section.course_coordinator.split(' - ')[0] if ' - ' in section.course_coordinator else section.course_coordinator[:15]

        total_students = len(section.students)
        regular_students = len([s for s in section.students if s.status.value == 'Regular'])

        # الحالة
        if section.grades_data_completed:
            status = self.text("✅ مكتمل", "✅ Complete")
            status_color = "#48BB78"
        else:
            status = self.text("⏳ قيد العمل", "⏳ In Progress")
            status_color = "#F6AD55"

        data = [
            section_number,
            course_code,
            year_sem,
            coordinator,
            str(total_students),
            str(regular_students),
            status
        ]

        colors = ['#2D3748'] * 6 + [status_color]
        column_widths_chars = [10, 10, 12, 18, 10, 10, 14]

        # تكوين الأعمدة
        for i in range(len(data)):
            row.grid_columnconfigure(i, weight=1, minsize=column_widths_chars[i]*8)

        for i, (value, color) in enumerate(zip(data, colors)):
            col_index = len(data) - 1 - i if self.is_rtl else i
            label = tk.Label(
                row,
                text=value,
                font=('Arial', 9),
                bg='#FFFFFF',
                fg=color,
                anchor=tk.CENTER
            )
            label.grid(row=0, column=col_index, sticky='nsew', padx=2, pady=6)

    def create_users_section(self, parent):
        """إنشاء قسم إحصائيات المستخدمين (للمدير فقط)"""
        section_frame = self.create_section_frame(
            parent,
            self.text("👥 إحصائيات المستخدمين", "👥 Users Statistics")
        )

        users = list(self.access_control.users.values())

        # إحصائيات حسب الأدوار
        stats_frame = tk.Frame(section_frame, bg='#FFFFFF')
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        roles_count = {
            'admin': 0,
            'program_coordinator': 0,
            'course_coordinator': 0,
            'section_instructor': 0
        }

        for user in users:
            for role in user.roles:
                role_str = role.value if hasattr(role, 'value') else str(role)
                if role_str in roles_count:
                    roles_count[role_str] += 1

        row = tk.Frame(stats_frame, bg='#FFFFFF')
        row.pack(fill=tk.X, pady=10)

        self.create_mini_stat_box(row, self.text("إجمالي المستخدمين", "Total Users"),
                                 len(users), "#667EEA")
        self.create_mini_stat_box(row, self.text("المدراء", "Admins"),
                                 roles_count['admin'], "#E53E3E")
        self.create_mini_stat_box(row, self.text("منسقو البرامج", "Program Coordinators"),
                                 roles_count['program_coordinator'], "#48BB78")
        self.create_mini_stat_box(row, self.text("منسقو المقررات", "Course Coordinators"),
                                 roles_count['course_coordinator'], "#4299E1")
        self.create_mini_stat_box(row, self.text("مدرسو الشعب", "Section Instructors"),
                                 roles_count['section_instructor'], "#9F7AEA")

    # ==================== دوال مساعدة ====================

    def create_section_frame(self, parent, title):
        """إنشاء إطار قسم"""
        section = tk.Frame(parent, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # العنوان
        tk.Label(
            section,
            text=title,
            font=('Arial', 16, 'bold'),
            bg='#FFFFFF',
            fg='#2D3748',
            anchor=tk.E if self.is_rtl else tk.W
        ).pack(fill=tk.X, padx=20, pady=(15, 10))

        # خط فاصل
        tk.Frame(section, bg='#E2E8F0', height=2).pack(fill=tk.X, padx=20, pady=(0, 10))

        return section

    def create_stat_card(self, parent, icon, label, value, color):
        """إنشاء بطاقة إحصائية"""
        card = tk.Frame(parent, bg='#FFFFFF', relief=tk.RIDGE, bd=1)
        card.pack(side=tk.RIGHT if self.is_rtl else tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(
            card,
            text=f"{icon} {label}",
            font=('Arial', 10),
            bg='#FFFFFF',
            fg='#718096'
        ).pack(pady=(10, 5))

        tk.Label(
            card,
            text=str(value),
            font=('Arial', 24, 'bold'),
            bg='#FFFFFF',
            fg=color
        ).pack(pady=(0, 10))

    def create_mini_stat_box(self, parent, label, value, color):
        """إنشاء صندوق إحصائيات صغير"""
        box = tk.Frame(parent, bg='#F7FAFC', relief=tk.RIDGE, bd=1)
        box.pack(side=tk.RIGHT if self.is_rtl else tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(
            box,
            text=label,
            font=('Arial', 9),
            bg='#F7FAFC',
            fg='#718096'
        ).pack(pady=(8, 2))

        tk.Label(
            box,
            text=str(value),
            font=('Arial', 18, 'bold'),
            bg='#F7FAFC',
            fg=color
        ).pack(pady=(0, 8))

    def gather_statistics(self):
        """جمع الإحصائيات العامة حسب الصلاحيات"""
        stats = {
            'total_programs': 0,
            'total_courses': 0,
            'total_sections': 0,
            'completed_courses': 0,
            'in_progress_courses': 0,
            'completion_rate': 0.0,
            'total_students': 0,
            'regular_students': 0,
            'total_activities': 0
        }

        # البرامج
        programs = self.get_accessible_programs()
        stats['total_programs'] = len(programs)

        # المقررات
        courses = self.get_accessible_courses()
        stats['total_courses'] = len(courses)

        for course_data in courses:
            try:
                course = self.course_manager.load_course(course_data['course_id'])
                if course:
                    if course.stage_3_completed:
                        stats['completed_courses'] += 1
                    elif course.stage_1_completed or course.stage_2_completed:
                        stats['in_progress_courses'] += 1

                    stats['total_activities'] += len(course.activities)
            except:
                pass

        # نسبة الإنجاز
        if stats['total_courses'] > 0:
            stats['completion_rate'] = (stats['completed_courses'] / stats['total_courses']) * 100

        # الشعب والطلاب
        sections = self.get_accessible_sections()
        stats['total_sections'] = len(sections)

        for section in sections:
            stats['total_students'] += len(section.students)
            stats['regular_students'] += len([s for s in section.students if s.status.value == 'Regular'])

        return stats

    def get_accessible_programs(self):
        """الحصول على البرامج المتاحة حسب الصلاحيات"""
        all_programs = self.program_manager.get_all_programs()

        if self.user.has_role('admin'):
            return all_programs

        # منسق برنامج - البرامج المسندة فقط
        if self.user.has_role('program_coordinator'):
            return [p for p in all_programs if p.program_id in self.user.assigned_programs]

        # منسق مقرر أو مدرس - البرامج التي لديه مقررات فيها
        accessible_program_names = set()
        for course_data in self.get_accessible_courses():
            accessible_program_names.add(course_data.get('program', ''))

        return [p for p in all_programs
                if p.program_name_ar in accessible_program_names
                or p.program_name_en in accessible_program_names]

    def get_accessible_courses(self):
        """الحصول على المقررات المتاحة حسب الصلاحيات"""
        all_courses = self.course_manager.list_all_courses()

        if self.user.has_role('admin'):
            return all_courses

        # منسق برنامج
        if self.user.has_role('program_coordinator'):
            accessible_courses = []
            for program_id in self.user.assigned_programs:
                program = self.program_manager.get_program(program_id)
                if program:
                    program_courses = [c for c in all_courses
                                     if c.get('program', '') in [program.program_name_ar, program.program_name_en]]
                    accessible_courses.extend(program_courses)
            return accessible_courses

        # منسق مقرر أو مدرس
        return [c for c in all_courses if c['course_id'] in self.user.assigned_courses
                or c['course_id'] in self.user.assigned_sections.keys()]

    def get_accessible_sections(self):
        """الحصول على الشعب المتاحة حسب الصلاحيات"""
        all_sections = self.section_manager.get_all_sections()

        if self.user.has_role('admin'):
            return all_sections

        # منسق برنامج - جميع شعب المقررات في البرامج المسندة
        if self.user.has_role('program_coordinator'):
            accessible_courses = self.get_accessible_courses()
            course_ids = [c['course_id'] for c in accessible_courses]
            return [s for s in all_sections if s.course_id in course_ids]

        # منسق مقرر - جميع شعب المقرر
        if self.user.has_role('course_coordinator'):
            return [s for s in all_sections if s.course_id in self.user.assigned_courses]

        # مدرس شعبة - الشعب المسندة فقط
        accessible_section_ids = []
        for course_id, sections in self.user.assigned_sections.items():
            for section_num in sections:
                # إيجاد الشعبة
                section = next((s for s in all_sections
                              if s.course_id == course_id and s.section_number == section_num), None)
                if section:
                    accessible_section_ids.append(section.section_id)

        return [s for s in all_sections if s.section_id in accessible_section_ids]

    def get_program_statistics(self, program):
        """حساب إحصائيات برنامج معين"""
        all_courses = self.course_manager.list_all_courses()
        program_courses = [c for c in all_courses
                         if c.get('program', '') in [program.program_name_ar, program.program_name_en]]

        stats = {
            'courses': len(program_courses),
            'completed': 0,
            'sections': 0,
            'students': 0
        }

        for course_data in program_courses:
            try:
                course = self.course_manager.load_course(course_data['course_id'])
                if course and course.stage_3_completed:
                    stats['completed'] += 1

                sections = self.section_manager.get_sections_by_course(course_data['course_id'])
                stats['sections'] += len(sections)

                for section in sections:
                    stats['students'] += len(section.students)
            except:
                pass

        return stats
