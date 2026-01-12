"""
النافذة الرئيسية للتطبيق
Main Application Window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import COLORS, FONTS, WINDOW, ROLES, get_role_color, get_role_icon
from translations import t, set_language, get_language
from managers.access_control import AccessControl
from managers.course_manager import CourseManager
from dialogs.stage1_course_dialog import Stage1CourseDialog
from assets.icons import get_icon, format_with_icon
from assets.widgets import EnhancedButton, CardFrame, IconButton


class MainWindow:
    """النافذة الرئيسية"""
    
    def __init__(self, user, access_control):
        self.root = tk.Tk()
        self.user = user
        self.access_control = access_control
        self.current_course = None
        self.course_manager = CourseManager()
        
        # إعداد النافذة
        self.setup_window()
        
        # إنشاء الواجهة
        self.create_menu_bar()
        self.create_header()
        self.create_main_content()
        self.create_statusbar()
        
        # عرض لوحة التحكم
        self.show_dashboard()
    
    def setup_window(self):
        """إعداد النافذة"""
        # عنوان النافذة
        self.root.title(WINDOW['title_ar'] if get_language() == 'ar' else WINDOW['title_en'])

        # جعل النافذة في وضع ملء الشاشة
        self.root.state('zoomed')  # للويندوز - فتح النافذة بأقصى حجم

        # حجم النافذة الافتراضي (في حالة عدم استخدام zoomed)
        self.root.geometry(f"{WINDOW['width']}x{WINDOW['height']}")
        self.root.minsize(WINDOW['min_width'], WINDOW['min_height'])

        # لون الخلفية
        self.root.configure(bg=COLORS['bg_main'])

        # أيقونة النافذة (يمكن إضافتها لاحقاً)
        # self.root.iconbitmap('icon.ico')
    
    def center_window(self):
        """وضع النافذة في المنتصف"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def create_menu_bar(self):
        """إنشاء شريط قوائم مبسط وجذاب"""
        # حذف القائمة القديمة إن وجدت
        self.root.config(menu=None)

        menubar = tk.Menu(
            self.root,
            font=('Arial', 13, 'bold'),  # خط أكبر وأوضح
            bg='#FFFFFF',
            fg='#2C3E50',
            activebackground='#3498DB',
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.root.config(menu=menubar)

        lang = get_language()

        # التحقق من الصلاحيات - هل هو مدرس شعبة فقط؟
        is_section_instructor_only = (not self.user.has_role('admin') and
                                     not self.user.has_role('program_coordinator') and
                                     not self.user.has_role('course_coordinator'))

        # ═══════════════════════════════════════════════════════════
        # 1️⃣ قائمة الرئيسية / Home
        # ═══════════════════════════════════════════════════════════
        home_menu = tk.Menu(
            menubar,
            tearoff=0,
            font=('Arial', 12),
            bg='#FFFFFF',
            fg='#2C3E50',
            activebackground='#3498DB',
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            borderwidth=0
        )
        menubar.add_cascade(
            label="🏠 " + ("الرئيسية" if lang == 'ar' else "Home"),
            menu=home_menu,
            foreground='#3498DB'
        )

        home_menu.add_command(
            label="  🏠  " + ("لوحة التحكم" if lang == 'ar' else "Dashboard") + "    ",
            command=self.show_dashboard,
            accelerator='Ctrl+H',
            compound=tk.LEFT
        )

        # القوائم الفرعية - للمنسقين والمدير فقط
        if not is_section_instructor_only:
            home_menu.add_separator()

            if self.access_control.has_permission(self.user.user_id, 'create_course_master'):
                home_menu.add_command(
                    label="  ➕  " + ("مقرر جديد" if lang == 'ar' else "New Course") + "    ",
                    command=self.new_course,
                    accelerator='Ctrl+N',
                    compound=tk.LEFT
                )

            home_menu.add_command(
                label="  📂  " + ("فتح/تحرير مقرر" if lang == 'ar' else "Open/Edit Course") + "    ",
                command=self.open_course,
                accelerator='Ctrl+O',
                compound=tk.LEFT
            )

            home_menu.add_separator()
        else:
            # مدرس الشعبة - فاصل واحد فقط
            home_menu.add_separator()

        home_menu.add_command(
            label="  🚪  " + ("خروج" if lang == 'ar' else "Exit") + "    ",
            command=self.exit_application,
            accelerator='Alt+F4',
            compound=tk.LEFT
        )

        # ═══════════════════════════════════════════════════════════
        # 2️⃣ قائمة إعداد المقرر / Course Setup
        # ═══════════════════════════════════════════════════════════
        # إخفاء القائمة عن مدرس الشعبة
        if not is_section_instructor_only:
            setup_menu = tk.Menu(
                menubar,
                tearoff=0,
                font=('Arial', 12),
                bg='#FFFFFF',
                fg='#2C3E50',
                activebackground='#E67E22',
                activeforeground='#FFFFFF',
                relief=tk.FLAT,
                borderwidth=0
            )
            menubar.add_cascade(
                label="📝 " + ("إعداد المقرر" if lang == 'ar' else "Course Setup"),
                menu=setup_menu,
                foreground='#E67E22'
            )

            # المرحلة 2: إعداد المقرر
            setup_menu.add_command(
                label="  2️⃣  " + ("المرحلة 2.1: توزيع درجات المخرجات" if lang == 'ar' else "Stage 2.1: CLO Marks") + "    ",
                command=self.open_stage2,
                accelerator='Ctrl+2',
                compound=tk.LEFT
            )

            setup_menu.add_command(
                label="  2️⃣  " + ("المرحلة 2.2: توزيع المواضيع على المخرجات" if lang == 'ar' else "Stage 2.2: Topics to CLOs") + "    ",
                command=self.open_stage2_step2,
                accelerator='Ctrl+Shift+2',
                compound=tk.LEFT
            )

            setup_menu.add_command(
                label="  2️⃣  " + ("المرحلة 2.3: توزيع المواضيع على الأنشطة" if lang == 'ar' else "Stage 2.3: Topics to Activities") + "    ",
                command=self.open_stage2_step3,
                accelerator='Ctrl+3',
                compound=tk.LEFT
            )

            setup_menu.add_command(
                label="  2️⃣  " + ("المرحلة 2.4: جدول المواصفات" if lang == 'ar' else "Stage 2.4: Table of Specifications") + "    ",
                command=self.open_stage2_step4,
                accelerator='Ctrl+4',
                compound=tk.LEFT
            )

        # ═══════════════════════════════════════════════════════════
        # 3️⃣ قائمة الشعب / Sections
        # ═══════════════════════════════════════════════════════════
        sections_menu = tk.Menu(
            menubar,
            tearoff=0,
            font=('Arial', 12),
            bg='#FFFFFF',
            fg='#2C3E50',
            activebackground='#9B59B6',
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            borderwidth=0
        )
        menubar.add_cascade(
            label="👥 " + ("الشعب" if lang == 'ar' else "Sections"),
            menu=sections_menu,
            foreground='#9B59B6'
        )

        # التحقق من الصلاحيات - هل هو مدرس شعبة فقط؟
        is_section_instructor_only = (not self.user.has_role('admin') and
                                     not self.user.has_role('program_coordinator') and
                                     not self.user.has_role('course_coordinator'))

        # البيانات التحضيرية (تأتي قبل إنشاء الشعب)
        # Faculty Management - للمدير ومنسق البرنامج فقط
        if self.user.has_role('admin') or self.user.has_role('program_coordinator'):
            sections_menu.add_command(
                label="  👨‍🏫  " + ("إدارة أعضاء هيئة التدريس" if lang == 'ar' else "Faculty Management") + "    ",
                command=self.open_faculty_management,
                accelerator='Ctrl+F',
                compound=tk.LEFT
            )

        # Semester Management - للمنسقين والمدير فقط
        if not is_section_instructor_only:
            sections_menu.add_command(
                label="  📅  " + ("إدارة بيانات الفصل الدراسي" if lang == 'ar' else "Semester Management") + "    ",
                command=self.open_semester_management,
                accelerator='Ctrl+M',
                compound=tk.LEFT
            )

            sections_menu.add_separator()

        # إنشاء وإدارة الشعب
        sections_menu.add_command(
            label="  3️⃣  " + ("المرحلة 3: إدخال بيانات الشعبة" if lang == 'ar' else "Stage 3: Section Data Entry") + "    ",
            command=self.open_stage3_step1,
            accelerator='Ctrl+5',
            compound=tk.LEFT
        )

        # ═══════════════════════════════════════════════════════════
        # 4️⃣ قائمة التقارير / Reports
        # ═══════════════════════════════════════════════════════════
        reports_menu = tk.Menu(
            menubar,
            tearoff=0,
            font=('Arial', 12),
            bg='#FFFFFF',
            fg='#2C3E50',
            activebackground='#27AE60',
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            borderwidth=0
        )
        menubar.add_cascade(
            label="📊 " + ("التقارير" if lang == 'ar' else "Reports"),
            menu=reports_menu,
            foreground='#27AE60'
        )

        # تقارير المقرر - متاحة للجميع
        reports_menu.add_command(
            label="  📄  " + ("تقرير معلومات المقرر (قراءة فقط)" if lang == 'ar' and is_section_instructor_only else "تقرير معلومات المقرر" if lang == 'ar' else "Course Info Report (Read-only)" if is_section_instructor_only else "Course Info Report") + "    ",
            command=self.generate_course_report,
            accelerator='Ctrl+R',
            compound=tk.LEFT
        )

        reports_menu.add_command(
            label="  📊  " + ("تقرير لوحة البيانات" if lang == 'ar' else "Dashboard Report") + "    ",
            command=self.generate_dashboard_report,
            accelerator='Ctrl+Shift+D',
            compound=tk.LEFT
        )

        reports_menu.add_separator()

        # تقارير الأنشطة
        reports_menu.add_command(
            label="  📝  " + ("أوراق الأنشطة" if lang == 'ar' else "Activity Sheets") + "    ",
            command=self.generate_activity_sheets,
            accelerator='Ctrl+Shift+A',
            compound=tk.LEFT
        )

        reports_menu.add_separator()

        # تقارير قياس المخرجات
        reports_menu.add_command(
            label="  📈  " + ("تقرير قياس المخرجات (شعبة)" if lang == 'ar' else "CLO Assessment (Section)") + "    ",
            command=self.generate_clo_assessment_report,
            accelerator='Ctrl+Shift+C',
            compound=tk.LEFT
        )

        reports_menu.add_command(
            label="  👥  " + ("تقرير إنجاز الطلاب (شعبة)" if lang == 'ar' else "Students Achievement (Section)") + "    ",
            command=self.generate_students_achievement_report,
            accelerator='Ctrl+Shift+S',
            compound=tk.LEFT
        )

        reports_menu.add_command(
            label="  📈  " + ("تقرير قياس المخرجات (مجمع)" if lang == 'ar' else "CLO Assessment (Aggregated)") + "    ",
            command=self.generate_aggregated_clo_report,
            accelerator='Ctrl+Shift+G',
            compound=tk.LEFT
        )

        reports_menu.add_separator()

        # التصدير
        reports_menu.add_command(
            label="  📊  " + ("تصدير جدول الدرجات Excel" if lang == 'ar' else "Export Grades to Excel") + "    ",
            command=self.export_grades_excel,
            accelerator='Ctrl+E',
            compound=tk.LEFT
        )

        reports_menu.add_separator()

        # تقرير الإحصائيات الشاملة
        reports_menu.add_command(
            label="  📊  " + ("تقرير الإحصائيات الشاملة" if lang == 'ar' else "Statistics Report") + "    ",
            command=self.show_statistics_report,
            accelerator='Ctrl+Shift+R',
            compound=tk.LEFT
        )

        # ═══════════════════════════════════════════════════════════
        # 5️⃣ قائمة الإعدادات / Settings
        # ═══════════════════════════════════════════════════════════
        settings_menu = tk.Menu(
            menubar,
            tearoff=0,
            font=('Arial', 12),
            bg='#FFFFFF',
            fg='#2C3E50',
            activebackground='#16A085',
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            borderwidth=0
        )
        menubar.add_cascade(
            label="⚙ " + ("الإعدادات" if lang == 'ar' else "Settings"),
            menu=settings_menu,
            foreground='#16A085'
        )

        settings_menu.add_command(
            label="  🌐  " + ("تغيير اللغة" if lang == 'ar' else "Change Language") + "    ",
            command=self.toggle_language,
            accelerator='Ctrl+L',
            compound=tk.LEFT
        )

        settings_menu.add_separator()

        settings_menu.add_command(
            label="  🖼  " + ("ترويسة التقارير" if lang == 'ar' else "Report Header") + "    ",
            command=self.open_report_header_settings,
            compound=tk.LEFT
        )

        # ═══════════════════════════════════════════════════════════
        # 6️⃣ قائمة الإدارة (Admin فقط)
        # ═══════════════════════════════════════════════════════════
        if self.user.has_role('admin'):
            admin_menu = tk.Menu(
                menubar,
                tearoff=0,
                font=('Arial', 12),
                bg='#FFFFFF',
                fg='#2C3E50',
                activebackground='#C0392B',
                activeforeground='#FFFFFF',
                relief=tk.FLAT,
                borderwidth=0
            )
            menubar.add_cascade(
                label="🛡️ " + ("الإدارة" if lang == 'ar' else "Admin"),
                menu=admin_menu,
                foreground='#C0392B'
            )

            # إدارة البيانات الأساسية
            admin_menu.add_command(
                label="  👥  " + ("إدارة المستخدمين" if lang == 'ar' else "User Management") + "    ",
                command=self.show_user_management,
                accelerator='Ctrl+U',
                compound=tk.LEFT
            )

            admin_menu.add_command(
                label="  🎓  " + ("إدارة البرامج الأكاديمية" if lang == 'ar' else "Academic Programs") + "    ",
                command=self.show_academic_programs,
                accelerator='Ctrl+P',
                compound=tk.LEFT
            )

            admin_menu.add_command(
                label="  👨‍🏫  " + ("إدارة أعضاء هيئة التدريس" if lang == 'ar' else "Faculty Management") + "    ",
                command=self.show_faculty_management,
                compound=tk.LEFT
            )

            admin_menu.add_separator()

            # النسخ الاحتياطي والأمان
            admin_menu.add_command(
                label="  💾  " + ("النسخ الاحتياطي والاستعادة" if lang == 'ar' else "Backup & Restore") + "    ",
                command=self.show_backup_management,
                accelerator='Ctrl+B',
                compound=tk.LEFT
            )

            admin_menu.add_command(
                label="  📋  " + ("سجل التدقيق" if lang == 'ar' else "Audit Log") + "    ",
                command=self.show_audit_log,
                compound=tk.LEFT
            )

            admin_menu.add_separator()

            # إعدادات النظام
            admin_menu.add_command(
                label="  ⚙️  " + ("إعدادات النظام" if lang == 'ar' else "System Settings") + "    ",
                command=self.show_system_settings,
                compound=tk.LEFT
            )

        # ═══════════════════════════════════════════════════════════
        # 7️⃣ قائمة المساعدة / Help
        # ═══════════════════════════════════════════════════════════
        help_menu = tk.Menu(
            menubar,
            tearoff=0,
            font=('Arial', 12),
            bg='#FFFFFF',
            fg='#2C3E50',
            activebackground='#E74C3C',
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            borderwidth=0
        )
        menubar.add_cascade(
            label="❓ " + ("مساعدة" if lang == 'ar' else "Help"),
            menu=help_menu,
            foreground='#E74C3C'
        )

        help_menu.add_command(
            label="  📖  " + ("دليل الاستخدام" if lang == 'ar' else "User Guide") + "    ",
            command=self.show_help,
            accelerator='F1',
            compound=tk.LEFT
        )

        help_menu.add_separator()

        help_menu.add_command(
            label="  ℹ️  " + ("حول البرنامج" if lang == 'ar' else "About") + "    ",
            command=self.show_about,
            compound=tk.LEFT
        )

        # ربط اختصارات لوحة المفاتيح
        self.root.bind('<Control-h>', lambda e: self.show_dashboard())
        self.root.bind('<Control-n>', lambda e: self.new_course())
        self.root.bind('<Control-o>', lambda e: self.open_course())
        self.root.bind('<Control-Key-1>', lambda e: self.open_stage1_for_editing())
        self.root.bind('<Control-Key-2>', lambda e: self.open_stage2())
        self.root.bind('<Control-Key-5>', lambda e: self.open_stage3_step1())
        self.root.bind('<Control-r>', lambda e: self.generate_course_report())
        self.root.bind('<Control-e>', lambda e: self.export_grades_excel())
        self.root.bind('<Control-Shift-G>', lambda e: self.generate_aggregated_clo_report())
        self.root.bind('<Control-Shift-R>', lambda e: self.show_statistics_report())
        self.root.bind('<F1>', lambda e: self.show_help())

        # اختصارات قائمة Admin
        if self.user.has_role('admin'):
            self.root.bind('<Control-u>', lambda e: self.show_user_management())
            self.root.bind('<Control-p>', lambda e: self.show_academic_programs())
            self.root.bind('<Control-b>', lambda e: self.show_backup_management())
    
    def create_header(self):
        """إنشاء ترويسة بسيطة"""
        lang = get_language()
        is_rtl = (lang == 'ar')

        header_frame = tk.Frame(
            self.root,
            bg=COLORS['primary_green'],
            height=70
        )
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # المحتوى
        content = tk.Frame(header_frame, bg=COLORS['primary_green'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)

        # العنوان - في اليمين للعربية، اليسار للإنجليزية
        title_frame = tk.Frame(content, bg=COLORS['primary_green'])
        title_frame.pack(side='right' if is_rtl else 'left')

        # استخدام الترجمة للعنوان
        title_text = t('app_title', lang)
        tk.Label(
            title_frame,
            text=f"📚 {title_text}",
            font=('Arial', 16, 'bold'),
            bg=COLORS['primary_green'],
            fg='#FFFFFF'
        ).pack()

        # معلومات المستخدم والأزرار - في اليسار للعربية، اليمين للإنجليزية
        controls_frame = tk.Frame(content, bg=COLORS['primary_green'])
        controls_frame.pack(side='left' if is_rtl else 'right')

        # معلومات المستخدم
        user_frame = tk.Frame(controls_frame, bg=COLORS['primary_green'])
        user_frame.pack(side='right' if is_rtl else 'left', padx=(15 if is_rtl else 0, 0 if is_rtl else 15))

        tk.Label(
            user_frame,
            text=f"👤 {self.user.full_name}",
            font=('Arial', 11, 'bold'),
            bg=COLORS['primary_green'],
            fg='#FFFFFF'
        ).pack(anchor=tk.E if is_rtl else tk.W)

        # زر تبديل اللغة
        lang_btn = tk.Button(
            controls_frame,
            text="🌐 EN" if is_rtl else "🌐 عربي",
            font=('Arial', 10, 'bold'),
            bg='#FFFFFF',
            fg=COLORS['primary_green'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.toggle_language
        )
        lang_btn.pack(side='right' if is_rtl else 'left', padx=(10 if is_rtl else 0, 0 if is_rtl else 10))

        # زر تسجيل الخروج
        logout_text = t('logout', lang)
        logout_btn = tk.Button(
            controls_frame,
            text=f"🚪 {logout_text}",
            font=('Arial', 10, 'bold'),
            bg='#FFFFFF',
            fg=COLORS['primary_green'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.logout
        )
        logout_btn.pack(side='right' if is_rtl else 'left')
    
    def create_main_content(self):
        """إنشاء المحتوى الرئيسي"""
        # إطار المحتوى الرئيسي - هذا هو الذي سيحتوي على Dashboard والصفحات الأخرى
        self.content_frame = tk.Frame(self.root, bg=COLORS['bg_main'])
        self.content_frame.pack(fill='both', expand=True, padx=0, pady=0)
    
    def create_statusbar(self):
        """إنشاء شريط حالة بسيط"""
        lang = get_language()
        is_rtl = (lang == 'ar')

        statusbar = tk.Frame(self.root, bg='#F7FAFC', height=35)
        statusbar.pack(side='bottom', fill='x')
        statusbar.pack_propagate(False)

        # محتوى شريط الحالة
        content = tk.Frame(statusbar, bg='#F7FAFC')
        content.pack(fill=tk.BOTH, expand=True, padx=30)

        # الحالة - في اليسار للعربية، اليمين للإنجليزية
        self.status_label = tk.Label(
            content,
            text=t('ready', lang),
            font=('Arial', 9),
            bg='#F7FAFC',
            fg='#718096',
            anchor='e' if is_rtl else 'w'
        )
        self.status_label.pack(side='right' if is_rtl else 'left')

        # زر العودة إلى المدير (يظهر فقط للمستخدمين غير المدير)
        if not self.user.has_role('admin'):
            return_btn = tk.Button(
                content,
                text="🔙 " + ("العودة إلى حساب المدير" if is_rtl else "Return to Admin Account"),
                font=('Arial', 9, 'bold'),
                bg='#4299E1',
                fg='white',
                bd=0,
                padx=15,
                pady=5,
                cursor='hand2',
                command=self.return_to_admin
            )
            return_btn.pack(side='left' if is_rtl else 'right', padx=10)

        # الوقت - في اليمين للعربية، اليسار للإنجليزية
        self.time_label = tk.Label(
            content,
            text="",
            font=('Arial', 9),
            bg='#F7FAFC',
            fg='#718096',
            anchor='w' if is_rtl else 'e'
        )
        self.time_label.pack(side='left' if is_rtl else 'right')

        self.update_time()
    
    def update_time(self):
        """تحديث الوقت"""
        from datetime import datetime
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def return_to_admin(self):
        """العودة إلى حساب المدير"""
        try:
            # البحث عن حساب المدير
            admin_user = None
            for user in self.access_control.users.values():
                if user.has_role('admin') and user.username == 'admin':
                    admin_user = user
                    break

            if not admin_user:
                messagebox.showerror(
                    t('error', get_language()),
                    "لم يتم العثور على حساب المدير" if get_language() == 'ar' else "Admin account not found"
                )
                return

            # التأكيد من العودة
            confirm = messagebox.askyesno(
                "تأكيد العودة" if get_language() == 'ar' else "Confirm Return",
                f"هل تريد العودة إلى حساب المدير؟\n\n"
                f"المستخدم الحالي: {self.user.username} ({self.user.full_name})\n"
                f"سيتم التبديل إلى: admin (System Administrator)"
                if get_language() == 'ar' else
                f"Do you want to return to admin account?\n\n"
                f"Current user: {self.user.username} ({self.user.full_name})\n"
                f"Switching to: admin (System Administrator)"
            )

            if confirm:
                # تحديث المستخدم الحالي
                self.user = admin_user
                self.access_control.current_user = admin_user
                from datetime import datetime
                admin_user.last_login = datetime.now().isoformat()
                self.access_control.save_users()

                # إعادة إنشاء النافذة الرئيسية
                self.root.destroy()
                from views.main_window import MainWindow
                new_window = MainWindow(admin_user, self.access_control)
                new_window.run()
        except Exception as e:
            messagebox.showerror(
                t('error', get_language()),
                f"خطأ في العودة إلى حساب المدير: {str(e)}"
            )

    # ═══════════════════════════════════════════════════════════════
    # وظائف القوائم والأزرار
    # ═══════════════════════════════════════════════════════════════
    
    def new_course(self):
        """مقرر جديد - افتح نموذج إدخال بيانات المرحلة الأولى"""
        try:
            # إنشاء مدير المقررات ثم فتح نافذة إدخال البيانات
            cm = CourseManager()
            dlg = Stage1CourseDialog(self.root, cm, self.user, course_id=None, language=get_language(), access_control=self.access_control)
            # الانتظار حتى يُغلق الحوار
            self.root.wait_window(dlg)

            # بعد الإغلاق، تعيين المقرر الحالي إن تم حفظه فعلاً
            if hasattr(dlg, 'course_saved') and dlg.course_saved and hasattr(dlg, 'course_id') and dlg.course_id:
                self.current_course = dlg.course_id
                # تحديث لوحة التحكم
                self.show_dashboard()
                messagebox.showinfo(
                    t('info'),
                    f"تم إنشاء المقرر الجديد: {dlg.course_id}",
                    parent=self.root
                )
        except Exception as e:
            messagebox.showerror(t('error'), str(e), parent=self.root)
    
    def open_course(self):
        """فتح مقرر - افتح حوار اختيار المقرر"""
        try:
            cm = CourseManager()
            from dialogs.open_course_dialog import OpenCourseDialog
            dlg = OpenCourseDialog(self.root, cm, self.user, language=get_language(), access_control=self.access_control)
            self.root.wait_window(dlg)
            if getattr(dlg, 'selected_course_id', None):
                self.current_course = dlg.selected_course_id
                self.show_dashboard()
        except Exception as e:
            messagebox.showerror(t('error'), str(e), parent=self.root)

    def open_course_id(self, course_id: str):
        """افتح مقرر مباشرة بواسطة المعرف (تستخدم في قائمة المقررات الأخيرة)"""
        try:
            cm = CourseManager()
            if not cm.course_exists(course_id):
                messagebox.showerror(t('error'), t('course_not_found'), parent=self.root)
                return
            dlg = Stage1CourseDialog(self.root, cm, self.user, course_id=course_id, language=get_language(), access_control=self.access_control)
            self.root.wait_window(dlg)
            if getattr(dlg, 'course_id', None):
                self.current_course = dlg.course_id
                self.show_dashboard()
        except Exception as e:
            messagebox.showerror(t('error'), str(e), parent=self.root)
    
    def close_course(self):
        """إغلاق المقرر"""
        self.current_course = None
        self.show_dashboard()

    def generate_course_report(self):
        """توليد تقرير معلومات المقرر"""
        try:
            from datetime import datetime
            import os
            import subprocess
            from reports.stage1_report_generator import Stage1ReportGenerator
            from dialogs.open_course_dialog import OpenCourseDialog

            lang = get_language()
            cm = CourseManager()

            # فتح نافذة اختيار المقرر (وضع الاختيار فقط)
            dlg = OpenCourseDialog(self.root, cm, self.user, language=lang, select_only=True, access_control=self.access_control)
            self.root.wait_window(dlg)

            # التحقق من اختيار مقرر
            if not hasattr(dlg, 'selected_course_id') or not dlg.selected_course_id:
                return  # المستخدم ألغى العملية

            # تحميل المقرر المختار
            course = cm.load_course(dlg.selected_course_id)

            if not course:
                messagebox.showerror(
                    t('error', lang),
                    t('error_loading_course', lang),
                    parent=self.root
                )
                return

            # التحقق من وجود كود المقرر
            if not course.info.course_code:
                msg_ar = "المقرر لا يحتوي على كود. الرجاء إدخال كود المقرر أولاً."
                msg_en = "Course does not have a code. Please enter the course code first."
                messagebox.showwarning(
                    t('warning', lang),
                    msg_ar if lang == 'ar' else msg_en,
                    parent=self.root
                )
                return

            # إنشاء اسم الملف
            course_code = course.info.course_code or "course"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{course_code}_Report_{timestamp}.pdf"

            # مسار مجلد التقارير
            reports_dir = os.path.join("reports", "generated")
            os.makedirs(reports_dir, exist_ok=True)
            output_path = os.path.join(reports_dir, filename)

            # توليد التقرير
            generator = Stage1ReportGenerator(course, lang)

            if generator.generate_report(output_path):
                msg_ar = f"✅ تم توليد التقرير بنجاح!\n\nتم حفظ التقرير في:\n{output_path}\n\nهل تريد فتح التقرير الآن؟"
                msg_en = f"✅ Report generated successfully!\n\nReport saved to:\n{output_path}\n\nDo you want to open the report now?"

                result = messagebox.askyesno(
                    t("success", lang),
                    msg_ar if lang == 'ar' else msg_en,
                    parent=self.root
                )

                if result:
                    # فتح الملف
                    os.startfile(os.path.abspath(output_path))
            else:
                msg_ar = "❌ فشل توليد التقرير"
                msg_en = "❌ Failed to generate report"
                messagebox.showerror(
                    t("error", lang),
                    msg_ar if lang == 'ar' else msg_en,
                    parent=self.root
                )

        except Exception as e:
            messagebox.showerror(
                t('error', get_language()),
                f"Error generating report:\n\n{str(e)}",
                parent=self.root
            )

    def generate_activity_sheets(self):
        """توليد تقارير أوراق الأنشطة"""
        try:
            from datetime import datetime
            from dialogs.open_course_dialog import OpenCourseDialog
            from reports.activity_sheet_generator import generate_activity_sheet

            lang = get_language()
            cm = CourseManager()

            # فتح نافذة اختيار المقرر
            dlg = OpenCourseDialog(self.root, cm, self.user, language=lang, select_only=True, access_control=self.access_control)
            self.root.wait_window(dlg)

            # التحقق من اختيار مقرر
            if not hasattr(dlg, 'selected_course_id') or not dlg.selected_course_id:
                return

            # تحميل المقرر
            course = cm.load_course(dlg.selected_course_id)
            if not course:
                messagebox.showerror(
                    t('error', lang),
                    t('error_loading_course', lang),
                    parent=self.root
                )
                return

            # التحقق من وجود أنشطة
            if not course.activities or len(course.activities) == 0:
                msg_ar = "المقرر لا يحتوي على أنشطة. الرجاء إضافة الأنشطة أولاً في المرحلة الأولى."
                msg_en = "Course does not have activities. Please add activities first in Stage 1."
                messagebox.showwarning(
                    t('warning', lang),
                    msg_ar if lang == 'ar' else msg_en,
                    parent=self.root
                )
                return

            # التحقق من وجود جدول المواصفات
            has_specifications = False
            for topic in course.topics:
                if hasattr(topic, 'specifications_table') and topic.specifications_table:
                    has_specifications = True
                    break

            if not has_specifications:
                msg_ar = "لم يتم بناء جدول المواصفات لهذا المقرر.\n\nالرجاء إكمال المرحلة الثانية - الخطوة 4: جدول المواصفات أولاً."
                msg_en = "Table of Specifications has not been created for this course.\n\nPlease complete Stage 2 - Step 4: Table of Specifications first."
                messagebox.showwarning(
                    t('warning', lang),
                    msg_ar if lang == 'ar' else msg_en,
                    parent=self.root
                )
                return

            # إنشاء نافذة اختيار الأنشطة
            activity_selection_dialog = tk.Toplevel(self.root)
            activity_selection_dialog.title("Select Activities" if lang == 'en' else "اختر الأنشطة")
            activity_selection_dialog.geometry("500x400")
            activity_selection_dialog.transient(self.root)
            activity_selection_dialog.grab_set()

            # المحتوى
            main_frame = tk.Frame(activity_selection_dialog, bg='white', padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)

            # العنوان
            title_text = "اختر الأنشطة التي تريد توليد تقارير لها:" if lang == 'ar' else "Select activities to generate reports for:"
            tk.Label(
                main_frame,
                text=title_text,
                font=FONTS['arabic_main'] if lang == 'ar' else FONTS['english_main'],
                bg='white'
            ).pack(pady=(0, 10))

            # قائمة الأنشطة مع checkboxes
            activities_frame = tk.Frame(main_frame, bg='white')
            activities_frame.pack(fill=tk.BOTH, expand=True)

            activity_vars = {}
            for activity in course.activities:
                var = tk.BooleanVar(value=True)  # محدد افتراضياً
                activity_vars[activity.name] = var

                ttk.Checkbutton(
                    activities_frame,
                    text=f"{activity.name} ({activity.mark:.0f} marks)",
                    variable=var
                ).pack(anchor='w', pady=2)

            # الأزرار
            buttons_frame = tk.Frame(main_frame, bg='white')
            buttons_frame.pack(pady=(10, 0))

            def preview_selected():
                """معاينة التقرير للنشاط الأول المحدد"""
                selected_activities = [name for name, var in activity_vars.items() if var.get()]

                if not selected_activities:
                    messagebox.showwarning(
                        t('warning', lang),
                        "الرجاء اختيار نشاط واحد على الأقل" if lang == 'ar' else "Please select at least one activity",
                        parent=activity_selection_dialog
                    )
                    return

                # معاينة أول نشاط محدد
                activity_name = selected_activities[0]

                # مسار مجلد المعاينة
                preview_dir = os.path.join("reports", "generated", "preview")
                os.makedirs(preview_dir, exist_ok=True)

                course_code = course.info.course_code or "course"
                filename = f"{course_code}_{activity_name.replace(' ', '_')}_preview.pdf"
                output_path = os.path.join(preview_dir, filename)

                if generate_activity_sheet(course, activity_name, output_path, lang):
                    # فتح التقرير للمعاينة
                    os.startfile(os.path.abspath(output_path))
                else:
                    messagebox.showerror(
                        t("error", lang),
                        "فشل توليد المعاينة" if lang == 'ar' else "Failed to generate preview",
                        parent=activity_selection_dialog
                    )

            def generate_selected():
                """توليد التقارير للأنشطة المحددة"""
                selected_activities = [name for name, var in activity_vars.items() if var.get()]

                if not selected_activities:
                    messagebox.showwarning(
                        t('warning', lang),
                        "الرجاء اختيار نشاط واحد على الأقل" if lang == 'ar' else "Please select at least one activity",
                        parent=activity_selection_dialog
                    )
                    return

                activity_selection_dialog.destroy()

                # مسار مجلد التقارير
                reports_dir = os.path.join("reports", "generated", "activity_sheets")
                os.makedirs(reports_dir, exist_ok=True)

                course_code = course.info.course_code or "course"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                generated_files = []
                failed_files = []

                # توليد تقرير لكل نشاط محدد
                for activity_name in selected_activities:
                    filename = f"{course_code}_{activity_name.replace(' ', '_')}_{timestamp}.pdf"
                    output_path = os.path.join(reports_dir, filename)

                    if generate_activity_sheet(course, activity_name, output_path, lang):
                        generated_files.append((activity_name, output_path))
                    else:
                        failed_files.append(activity_name)

                # عرض النتيجة
                if generated_files:
                    msg_ar = f"✅ تم توليد {len(generated_files)} تقرير بنجاح!\n\nتم حفظ التقارير في:\n{reports_dir}\n\nهل تريد فتح المجلد الآن؟"
                    msg_en = f"✅ {len(generated_files)} report(s) generated successfully!\n\nReports saved to:\n{reports_dir}\n\nDo you want to open the folder now?"

                    result = messagebox.askyesno(
                        t("success", lang),
                        msg_ar if lang == 'ar' else msg_en,
                        parent=self.root
                    )

                    if result:
                        # فتح المجلد
                        os.startfile(os.path.abspath(reports_dir))
                elif failed_files:
                    msg_ar = f"❌ فشل توليد التقارير للأنشطة التالية:\n" + "\n".join(failed_files)
                    msg_en = f"❌ Failed to generate reports for the following activities:\n" + "\n".join(failed_files)
                    messagebox.showerror(
                        t("error", lang),
                        msg_ar if lang == 'ar' else msg_en,
                        parent=self.root
                    )

            tk.Button(
                buttons_frame,
                text="👁 " + ("معاينة" if lang == 'ar' else "Preview"),
                command=preview_selected,
                bg='#2196F3',
                fg='white',
                font=FONTS['bold'],
                width=15,
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                buttons_frame,
                text="✓ " + ("توليد" if lang == 'ar' else "Generate"),
                command=generate_selected,
                bg=COLORS['btn_primary'],
                fg='white',
                font=FONTS['bold'],
                width=15,
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                buttons_frame,
                text="✕ " + ("إلغاء" if lang == 'ar' else "Cancel"),
                command=activity_selection_dialog.destroy,
                bg=COLORS['btn_secondary'],
                fg='white',
                font=FONTS['bold'],
                width=15,
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror(
                t('error', get_language()),
                f"Error generating activity sheets:\n\n{str(e)}",
                parent=self.root
            )

    def open_stage1_for_editing(self):
        """فتح المرحلة الأولى لتحرير مقرر"""
        try:
            from dialogs.open_course_dialog import OpenCourseDialog
            from dialogs.stage1_course_dialog import Stage1CourseDialog

            lang = get_language()
            cm = CourseManager()

            # فتح نافذة اختيار المقرر
            dlg = OpenCourseDialog(self.root, cm, self.user, language=lang, select_only=True, access_control=self.access_control)
            self.root.wait_window(dlg)

            # التحقق من اختيار مقرر
            if not hasattr(dlg, 'selected_course_id') or not dlg.selected_course_id:
                return

            # فتح نافذة المرحلة الأولى
            stage1_dlg = Stage1CourseDialog(self.root, cm, self.user, course_id=dlg.selected_course_id, language=lang, access_control=self.access_control)
            self.root.wait_window(stage1_dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def open_stage1(self):
        """فتح المرحلة الأولى"""
        # استدعاء دالة التحرير
        self.open_stage1_for_editing()

    def open_stage2(self):
        """فتح المرحلة الثانية - توزيع الدرجات"""
        try:
            from dialogs.open_course_dialog import OpenCourseDialog
            from dialogs.stage2_clo_marks_dialog import Stage2CLOMarksDialog

            lang = get_language()
            cm = CourseManager()

            # فتح نافذة اختيار المقرر
            dlg = OpenCourseDialog(self.root, cm, self.user, language=lang, select_only=True, access_control=self.access_control)
            self.root.wait_window(dlg)

            # التحقق من اختيار مقرر
            if not hasattr(dlg, 'selected_course_id') or not dlg.selected_course_id:
                return

            # فتح نافذة المرحلة الثانية
            stage2_dlg = Stage2CLOMarksDialog(self.root, cm, self.user, course_id=dlg.selected_course_id, language=lang)
            self.root.wait_window(stage2_dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def open_stage2_step2(self):
        """فتح المرحلة الثانية - الخطوة 2: توزيع المواضيع"""
        try:
            from dialogs.open_course_dialog import OpenCourseDialog
            from dialogs.stage2_topics_distribution_dialog import Stage2TopicsDistributionDialog

            lang = get_language()
            cm = CourseManager()

            # فتح نافذة اختيار المقرر
            dlg = OpenCourseDialog(self.root, cm, self.user, language=lang, select_only=True, access_control=self.access_control)
            self.root.wait_window(dlg)

            # التحقق من اختيار مقرر
            if not hasattr(dlg, 'selected_course_id') or not dlg.selected_course_id:
                return

            # فتح نافذة المرحلة الثانية - الخطوة 2
            stage2_step2_dlg = Stage2TopicsDistributionDialog(self.root, cm, self.user, course_id=dlg.selected_course_id, language=lang)
            self.root.wait_window(stage2_step2_dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def open_stage2_step3(self):
        """فتح المرحلة الثانية - الخطوة 3: توزيع المواضيع على الأنشطة"""
        try:
            from dialogs.open_course_dialog import OpenCourseDialog
            from dialogs.stage2_activities_distribution_dialog import Stage2ActivitiesDistributionDialog

            lang = get_language()
            cm = CourseManager()

            # فتح نافذة اختيار المقرر
            dlg = OpenCourseDialog(self.root, cm, self.user, language=lang, select_only=True, access_control=self.access_control)
            self.root.wait_window(dlg)

            # التحقق من اختيار مقرر
            if not hasattr(dlg, 'selected_course_id') or not dlg.selected_course_id:
                return

            # فتح نافذة المرحلة الثانية - الخطوة 3
            stage2_step3_dlg = Stage2ActivitiesDistributionDialog(self.root, cm, self.user, course_id=dlg.selected_course_id, language=lang)
            self.root.wait_window(stage2_step3_dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def open_stage2_step4(self):
        """فتح المرحلة الثانية - الخطوة 4: جدول المواصفات"""
        try:
            from dialogs.open_course_dialog import OpenCourseDialog
            from dialogs.stage2_specifications_table_dialog import Stage2SpecificationsTableDialog

            lang = get_language()
            cm = CourseManager()

            # فتح نافذة اختيار المقرر
            dlg = OpenCourseDialog(self.root, cm, self.user, language=lang, select_only=True, access_control=self.access_control)
            self.root.wait_window(dlg)

            # التحقق من اختيار مقرر
            if not hasattr(dlg, 'selected_course_id') or not dlg.selected_course_id:
                return

            # فتح نافذة المرحلة الثانية - الخطوة 4
            stage2_step4_dlg = Stage2SpecificationsTableDialog(self.root, cm, self.user, course_id=dlg.selected_course_id, language=lang)
            self.root.wait_window(stage2_step4_dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def open_stage3_step1(self):
        """فتح المرحلة الثالثة - الخطوة 1: بيانات الشعبة"""
        lang = get_language()
        try:
            from managers.course_manager import CourseManager
            from dialogs.open_course_dialog import OpenCourseDialog
            from dialogs.select_section_dialog import SelectSectionDialog

            cm = CourseManager()

            # فتح نافذة اختيار المقرر
            dlg = OpenCourseDialog(self.root, cm, self.user, language=lang, select_only=True, access_control=self.access_control)
            self.root.wait_window(dlg)

            # التحقق من اختيار مقرر
            if not hasattr(dlg, 'selected_course_id') or not dlg.selected_course_id:
                return

            # تحميل المقرر
            course = cm.load_course(dlg.selected_course_id)
            if not course:
                messagebox.showerror(
                    t('error', lang),
                    t('error_loading_course', lang),
                    parent=self.root
                )
                return

            # فتح نافذة اختيار/إنشاء الشعبة
            select_section_dlg = SelectSectionDialog(self.root, course, language=lang, user=self.user)
            self.root.wait_window(select_section_dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def open_semester_management(self):
        """فتح نافذة إدارة بيانات الفصل الدراسي"""
        lang = get_language()
        try:
            from managers.course_manager import CourseManager
            from dialogs.open_course_dialog import OpenCourseDialog
            from dialogs.semester_management_dialog import SemesterManagementDialog

            cm = CourseManager()

            # فتح نافذة اختيار المقرر
            dlg = OpenCourseDialog(self.root, cm, self.user, language=lang, select_only=True, access_control=self.access_control)
            self.root.wait_window(dlg)

            # التحقق من اختيار مقرر
            if not hasattr(dlg, 'selected_course_id') or not dlg.selected_course_id:
                return

            # تحميل المقرر
            course = cm.load_course(dlg.selected_course_id)
            if not course:
                messagebox.showerror(
                    t('error', lang),
                    t('error_loading_course', lang),
                    parent=self.root
                )
                return

            # فتح نافذة إدارة الفصل الدراسي
            semester_dlg = SemesterManagementDialog(self.root, course, language=lang)
            self.root.wait_window(semester_dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def open_faculty_management(self):
        """فتح نافذة إدارة أعضاء هيئة التدريس"""
        lang = get_language()
        try:
            from dialogs.faculty_management_dialog import FacultyManagementDialog

            # فتح نافذة إدارة أعضاء هيئة التدريس
            faculty_dlg = FacultyManagementDialog(self.root, language=lang)
            self.root.wait_window(faculty_dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def open_stage3(self):
        """فتح المرحلة الثالثة"""
        messagebox.showinfo(
            t('stage_3'),
            "سيتم فتح واجهة المرحلة الثالثة",
            parent=self.root
        )

    def generate_clo_assessment_report(self):
        """توليد تقرير قياس مخرجات التعلم"""
        try:
            from dialogs.generate_clo_report_dialog import GenerateCLOReportDialog

            lang = get_language()

            dlg = GenerateCLOReportDialog(self.root, language=lang, user=self.user, access_control=self.access_control)
            self.root.wait_window(dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def generate_dashboard_report(self):
        """توليد تقرير لوحة البيانات"""
        try:
            from dialogs.generate_dashboard_dialog import GenerateDashboardDialog

            lang = get_language()

            dlg = GenerateDashboardDialog(self.root, language=lang, user=self.user, access_control=self.access_control)
            self.root.wait_window(dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def generate_students_achievement_report(self):
        """توليد تقرير إنجاز الطلاب في المخرجات"""
        try:
            from dialogs.generate_students_achievement_dialog import GenerateStudentsAchievementDialog

            lang = get_language()

            dlg = GenerateStudentsAchievementDialog(self.root, language=lang, user=self.user, access_control=self.access_control)
            self.root.wait_window(dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def export_grades_excel(self):
        """تصدير جدول الدرجات إلى Excel"""
        try:
            from dialogs.generate_grades_excel_dialog import GenerateGradesExcelDialog

            lang = get_language()

            dlg = GenerateGradesExcelDialog(self.root, language=lang, user=self.user, access_control=self.access_control)
            self.root.wait_window(dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def generate_aggregated_clo_report(self):
        """توليد تقرير قياس نواتج التعلم المجمع"""
        try:
            from dialogs.course_selection_dialog import CourseSelectionDialog
            from dialogs.generate_aggregated_report_dialog import GenerateAggregatedReportDialog

            lang = get_language()

            # اختيار المقرر
            course_dlg = CourseSelectionDialog(self.root, language=lang, user=self.user, access_control=self.access_control)
            self.root.wait_window(course_dlg)

            if course_dlg.selected_course:
                # فتح حوار توليد التقرير
                report_dlg = GenerateAggregatedReportDialog(
                    self.root,
                    course_dlg.selected_course,
                    language=lang
                )
                self.root.wait_window(report_dlg)

        except Exception as e:
            messagebox.showerror(t('error', get_language()), str(e), parent=self.root)

    def manage_users(self):
        """إدارة المستخدمين"""
        messagebox.showinfo(
            t('manage_users'),
            "سيتم فتح نافذة إدارة المستخدمين",
            parent=self.root
        )
    
    def generate_report(self):
        """إنشاء تقرير"""
        messagebox.showinfo(
            t('generate_report'),
            "سيتم فتح نافذة إنشاء التقارير",
            parent=self.root
        )
    
    def show_help(self):
        """عرض المساعدة"""
        messagebox.showinfo(
            t('help'),
            "دليل استخدام التطبيق",
            parent=self.root
        )
    
    def show_about(self):
        """عرض حول"""
        about_text = f"""
        {t('app_title')}
        {t('version')}: {WINDOW['title_en'].split('Version ')[-1]}
        
        Developed by: Dr. Hussein Youssef Abdelazim
        Department of Statistics
        University of Tabuk
        
        © 2024 All Rights Reserved
        """
        messagebox.showinfo(
            t('about'),
            about_text,
            parent=self.root
        )
    
    def open_report_header_settings(self):
        """فتح إعدادات ترويسة التقارير"""
        from dialogs.report_header_dialog import ReportHeaderDialog

        dialog = ReportHeaderDialog(self.root, language=get_language())
        self.root.wait_window(dialog)

    def toggle_language(self):
        """تبديل اللغة"""
        current_lang = get_language()
        new_lang = 'en' if current_lang == 'ar' else 'ar'

        # تأكيد التبديل
        msg_ar = f"هل تريد تبديل اللغة إلى {'الإنجليزية' if new_lang == 'en' else 'العربية'}؟\nسيتم إعادة تشغيل النافذة."
        msg_en = f"Do you want to switch language to {'English' if new_lang == 'en' else 'Arabic'}?\nThe window will be restarted."

        if messagebox.askyesno(
            "تبديل اللغة / Language Switch",
            msg_ar if current_lang == 'ar' else msg_en,
            parent=self.root
        ):
            set_language(new_lang)

            # إعادة تشغيل النافذة
            self.root.destroy()
            MainWindow(self.user, self.access_control).run()
    
    def logout(self):
        """تسجيل الخروج"""
        if messagebox.askyesno(
            t('logout'),
            "هل تريد تسجيل الخروج؟",
            parent=self.root
        ):
            self.access_control.logout()
            self.root.destroy()
    
    def exit_application(self):
        """الخروج من التطبيق"""
        if messagebox.askyesno(
            t('exit'),
            "هل تريد الخروج من التطبيق؟",
            parent=self.root
        ):
            self.root.quit()
    
    def show_dashboard(self):
        """عرض لوحة التحكم حسب الصلاحيات"""
        # مسح المحتوى الحالي
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # إنشاء لوحة التحكم حسب الصلاحيات
        from views.dashboard_role_based import RoleBasedDashboard
        self.dashboard = RoleBasedDashboard(
            self.content_frame,
            self.user,
            self.access_control,
            self.course_manager,
            self  # تمرير MainWindow نفسها
        )
        self.dashboard.pack(fill=tk.BOTH, expand=True)

        # تحديث شريط الحالة
        self.status_label.config(text=t('main_dashboard'))

    def refresh_dashboard(self):
        """تحديث لوحة التحكم دون إعادة إنشاء النافذة بالكامل"""
        if hasattr(self, 'dashboard') and self.dashboard.winfo_exists():
            # إعادة تحميل البيانات فقط
            self.dashboard.destroy()
            self.show_dashboard()
        else:
            self.show_dashboard()

    def show_statistics_report(self):
        """عرض تقرير الإحصائيات الشاملة في نافذة منفصلة"""
        # إنشاء نافذة جديدة
        report_window = tk.Toplevel(self.root)

        # إعداد النافذة
        lang = get_language()
        title = "📊 تقرير الإحصائيات الشاملة" if lang == 'ar' else "📊 Comprehensive Statistics Report"
        report_window.title(title)

        # جعل النافذة في وضع ملء الشاشة
        report_window.state('zoomed')  # للويندوز

        # أو استخدم هذا للتوافق مع أنظمة أخرى:
        # report_window.attributes('-fullscreen', True)

        # جعل النافذة في المقدمة
        report_window.lift()
        report_window.focus_force()

        # إضافة زر للخروج من وضع الشاشة الكاملة
        top_bar = tk.Frame(report_window, bg='#2C3E50', height=40)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        close_btn = tk.Button(
            top_bar,
            text="✕ " + ("إغلاق" if lang == 'ar' else "Close"),
            command=report_window.destroy,
            bg='#E74C3C',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=5
        )
        close_btn.pack(side=tk.RIGHT if lang == 'ar' else tk.LEFT, padx=10, pady=5)

        # إنشاء إطار للمحتوى مع scrollbar
        main_frame = tk.Frame(report_window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # إنشاء تقرير الإحصائيات
        from views.statistics_report import StatisticsReport
        report = StatisticsReport(
            main_frame,
            self.user,
            self.access_control
        )
        report.pack(fill=tk.BOTH, expand=True)

    # ═══════════════════════════════════════════════════════════════
    # دوال قائمة الإدارة (Admin)
    # ═══════════════════════════════════════════════════════════════

    def show_user_management(self):
        """عرض واجهة إدارة المستخدمين"""
        try:
            from dialogs.admin_user_management_dialog import AdminUserManagementDialog
            dialog = AdminUserManagementDialog(
                self.root,
                self.access_control,
                language=get_language()
            )

            # الانتظار حتى يتم إغلاق النافذة
            self.root.wait_window(dialog.dialog)

            # التحقق من وجود نتيجة (تبديل مستخدم)
            if hasattr(dialog, 'result') and dialog.result and dialog.result.get('action') == 'switch_user':
                new_user = dialog.result.get('user')
                if new_user:
                    # تحديث المستخدم الحالي
                    self.user = new_user
                    self.access_control.current_user = new_user

                    # إعادة إنشاء النافذة الرئيسية بالمستخدم الجديد
                    self.root.destroy()
                    from views.main_window import MainWindow
                    new_window = MainWindow(new_user, self.access_control)
                    new_window.run()
        except Exception as e:
            messagebox.showerror(
                t('error', get_language()),
                f"Error opening user management: {str(e)}"
            )

    def show_academic_programs(self):
        """عرض واجهة إدارة البرامج الأكاديمية"""
        try:
            from dialogs.academic_programs_dialog import AcademicProgramsDialog
            dialog = AcademicProgramsDialog(
                self.root,
                self.access_control,
                language=get_language(),
                main_window=self
            )
        except Exception as e:
            messagebox.showerror(
                t('error', get_language()),
                f"Error opening academic programs: {str(e)}"
            )

    def show_faculty_management(self):
        """عرض واجهة إدارة أعضاء هيئة التدريس"""
        try:
            from dialogs.faculty_management_dialog import FacultyManagementDialog
            dialog = FacultyManagementDialog(
                self.root,
                language=get_language()
            )
        except Exception as e:
            messagebox.showerror(
                t('error', get_language()),
                f"Error opening faculty management: {str(e)}"
            )

    def show_backup_management(self):
        """عرض واجهة النسخ الاحتياطي"""
        from managers.backup_manager import backup_manager
        from tkinter import simpledialog

        lang = get_language()

        # قائمة خيارات
        choice = messagebox.askquestion(
            ("النسخ الاحتياطي" if lang == 'ar' else "Backup"),
            ("هل تريد إنشاء نسخة احتياطية جديدة؟\n\nنعم = إنشاء نسخة\nلا = استعادة من نسخة" if lang == 'ar' else "Do you want to create a new backup?\n\nYes = Create backup\nNo = Restore backup"),
            icon='question'
        )

        if choice == 'yes':
            # إنشاء نسخة احتياطية
            description = simpledialog.askstring(
                ("وصف النسخة" if lang == 'ar' else "Backup Description"),
                ("أدخل وصفاً للنسخة الاحتياطية (اختياري):" if lang == 'ar' else "Enter a description for the backup (optional):"),
                parent=self.root
            )

            backup_path = backup_manager.create_backup(
                backup_type='manual',
                description=description or ''
            )

            if backup_path:
                # تسجيل في سجل التدقيق
                from utils.audit_logger import log_backup
                log_backup(
                    self.user.username,
                    self.user.user_id,
                    backup_type='manual'
                )

                messagebox.showinfo(
                    t('success', lang),
                    ("تم إنشاء النسخة الاحتياطية بنجاح!\n\nالموقع: " if lang == 'ar' else "Backup created successfully!\n\nLocation: ") + backup_path
                )
            else:
                messagebox.showerror(
                    t('error', lang),
                    ("فشل إنشاء النسخة الاحتياطية!" if lang == 'ar' else "Failed to create backup!")
                )
        else:
            # استعادة من نسخة
            from tkinter import filedialog
            backup_file = filedialog.askopenfilename(
                title=("اختر ملف النسخة الاحتياطية" if lang == 'ar' else "Select backup file"),
                filetypes=[("Backup files", "*.zip"), ("All files", "*.*")]
            )

            if backup_file:
                confirm = messagebox.askyesno(
                    ("تأكيد الاستعادة" if lang == 'ar' else "Confirm Restore"),
                    ("⚠️ تحذير!\n\nستحل هذه النسخة محل جميع البيانات الحالية.\nهل أنت متأكد؟" if lang == 'ar' else "⚠️ Warning!\n\nThis will replace all current data.\nAre you sure?"),
                    icon='warning'
                )

                if confirm:
                    success = backup_manager.restore_backup(backup_file)

                    if success:
                        # تسجيل في سجل التدقيق
                        from utils.audit_logger import log_restore
                        log_restore(
                            self.user.username,
                            self.user.user_id,
                            backup_file
                        )

                        messagebox.showinfo(
                            t('success', lang),
                            ("تمت الاستعادة بنجاح!\n\nسيتم إعادة تشغيل البرنامج." if lang == 'ar' else "Restore successful!\n\nThe application will restart.")
                        )

                        # إعادة تشغيل البرنامج
                        self.root.destroy()
                        import sys
                        import os
                        os.execl(sys.executable, sys.executable, *sys.argv)
                    else:
                        messagebox.showerror(
                            t('error', lang),
                            ("فشلت عملية الاستعادة!" if lang == 'ar' else "Restore failed!")
                        )

    def show_audit_log(self):
        """عرض سجل التدقيق"""
        from utils.audit_logger import audit_logger
        from tkinter import scrolledtext

        lang = get_language()

        # إنشاء نافذة
        log_window = tk.Toplevel(self.root)
        log_window.title(("سجل التدقيق" if lang == 'ar' else "Audit Log"))
        log_window.geometry("900x600")

        # عنوان
        header = tk.Frame(log_window, bg='#34495E', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📋 " + ("سجل التدقيق" if lang == 'ar' else "Audit Log"),
            font=('Arial', 16, 'bold'),
            bg='#34495E',
            fg='white'
        ).pack(expand=True)

        # منطقة النص
        text_area = scrolledtext.ScrolledText(
            log_window,
            wrap=tk.WORD,
            font=('Courier New', 9),
            bg='#2C3E50',
            fg='#ECF0F1'
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # الحصول على آخر 100 سجل
        logs = audit_logger.get_recent_logs(limit=100)

        if logs:
            for log in reversed(logs):  # عرض الأحدث أولاً
                timestamp = log.get('timestamp', '')
                action = log.get('action', 'unknown')
                username = log.get('username', 'N/A')
                status = log.get('status', 'unknown')

                # لون حسب الحالة
                if status == 'success':
                    status_icon = '✅'
                elif status == 'failed':
                    status_icon = '❌'
                else:
                    status_icon = '⚠️'

                log_line = f"[{timestamp}] {status_icon} {action.upper()} - User: {username}\n"
                text_area.insert(tk.END, log_line)

                # التفاصيل
                details = log.get('details', {})
                if details:
                    text_area.insert(tk.END, f"  Details: {details}\n")

                text_area.insert(tk.END, "\n")
        else:
            text_area.insert(tk.END, ("لا توجد سجلات" if lang == 'ar' else "No logs found"))

        text_area.config(state=tk.DISABLED)

        # زر إغلاق
        tk.Button(
            log_window,
            text=("إغلاق" if lang == 'ar' else "Close"),
            command=log_window.destroy,
            font=('Arial', 10),
            bg='#E74C3C',
            fg='white',
            padx=30,
            pady=8
        ).pack(pady=10)

    def show_system_settings(self):
        """عرض إعدادات النظام"""
        from managers.backup_manager import backup_manager
        from utils.audit_logger import audit_logger

        lang = get_language()

        # إنشاء نافذة
        settings_window = tk.Toplevel(self.root)
        settings_window.title(("إعدادات النظام" if lang == 'ar' else "System Settings"))
        settings_window.geometry("600x500")
        settings_window.configure(bg='#ECF0F1')

        # عنوان
        header = tk.Frame(settings_window, bg='#2C3E50', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚙️ " + ("إعدادات النظام" if lang == 'ar' else "System Settings"),
            font=('Arial', 16, 'bold'),
            bg='#2C3E50',
            fg='white'
        ).pack(expand=True)

        # محتوى
        content = tk.Frame(settings_window, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # إحصائيات النسخ الاحتياطي
        backup_stats = backup_manager.get_statistics()
        audit_stats = audit_logger.get_statistics()

        stats_text = ""
        if lang == 'ar':
            stats_text = f"""
📊 إحصائيات النظام

النسخ الاحتياطي:
• إجمالي النسخ: {backup_stats.get('total_backups', 0)}
• نسخ تلقائية: {backup_stats.get('auto_backups', 0)}
• نسخ يدوية: {backup_stats.get('manual_backups', 0)}
• الحجم الإجمالي: {backup_stats.get('total_size_mb', 0)} MB

سجل التدقيق:
• إجمالي السجلات: {audit_stats.get('total_entries', 0)}
• عمليات ناجحة: {audit_stats.get('successful_operations', 0)}
• عمليات فاشلة: {audit_stats.get('failed_operations', 0)}
• المستخدمون الفريدون: {audit_stats.get('unique_users', 0)}
            """
        else:
            stats_text = f"""
📊 System Statistics

Backups:
• Total backups: {backup_stats.get('total_backups', 0)}
• Auto backups: {backup_stats.get('auto_backups', 0)}
• Manual backups: {backup_stats.get('manual_backups', 0)}
• Total size: {backup_stats.get('total_size_mb', 0)} MB

Audit Log:
• Total entries: {audit_stats.get('total_entries', 0)}
• Successful operations: {audit_stats.get('successful_operations', 0)}
• Failed operations: {audit_stats.get('failed_operations', 0)}
• Unique users: {audit_stats.get('unique_users', 0)}
            """

        tk.Label(
            content,
            text=stats_text.strip(),
            font=('Arial', 10),
            bg='white',
            justify=tk.RIGHT if lang == 'ar' else tk.LEFT,
            anchor='e' if lang == 'ar' else 'w'
        ).pack(fill=tk.BOTH, expand=True, pady=20)

        # زر إغلاق
        tk.Button(
            settings_window,
            text=("إغلاق" if lang == 'ar' else "Close"),
            command=settings_window.destroy,
            font=('Arial', 10),
            bg='#95A5A6',
            fg='white',
            padx=30,
            pady=8
        ).pack(pady=10)

    def run(self):
        """تشغيل النافذة"""
        self.root.mainloop()


if __name__ == '__main__':
    # للاختبار فقط
    from models.user import User
    test_user = User(
        user_id='test_001',
        username='test',
        full_name='Test User',
        email='test@tabuk.edu.sa',
        roles=['admin']
    )
    access_control = AccessControl()
    access_control.current_user = test_user
    
    app = MainWindow(test_user, access_control)
    app.run()
