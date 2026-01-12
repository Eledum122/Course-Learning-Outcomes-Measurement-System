"""
لوحة التحكم الرئيسية
Main Dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import COLORS, FONTS
from assets.icons import get_icon, format_with_icon
from assets.widgets import (EnhancedButton, CardFrame, InfoLabel, 
                           StatusBadge, SectionHeader, Separator)
from translations import t


class Dashboard(tk.Frame):
    """لوحة التحكم الرئيسية"""
    
    def __init__(self, parent, user, access_control, course_manager):
        """
        إنشاء لوحة التحكم
        
        Args:
            parent: النافذة الأم
            user: المستخدم الحالي
            access_control: نظام التحكم بالصلاحيات
            course_manager: مدير المقررات
        """
        super().__init__(parent, bg=COLORS['bg_main'])
        
        self.user = user
        self.access_control = access_control
        self.course_manager = course_manager
        
        # إنشاء المحتوى
        self.create_content()
    
    def create_content(self):
        """إنشاء محتوى لوحة التحكم"""
        # حاوية قابلة للتمرير
        canvas = tk.Canvas(self, bg=COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_main'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # التخطيط
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # المحتوى الرئيسي
        main_content = tk.Frame(scrollable_frame, bg=COLORS['bg_main'])
        main_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # 1. العنوان الترحيبي
        self.create_welcome_section(main_content)
        
        # 2. الإحصائيات السريعة
        self.create_stats_section(main_content)
        
        # 3. الإجراءات السريعة
        self.create_quick_actions_section(main_content)
        
        # 4. المقررات الأخيرة
        self.create_recent_courses_section(main_content)
        
        # 5. التنبيهات والإشعارات
        self.create_notifications_section(main_content)
    
    def create_welcome_section(self, parent):
        """إنشاء قسم الترحيب"""
        welcome_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        
        # العنوان الرئيسي
        title_text = format_with_icon(
            f"مرحباً، {self.user.full_name}",
            'user'
        )
        title_label = tk.Label(
            welcome_frame,
            text=title_text,
            bg=COLORS['bg_main'],
            fg=COLORS['primary_green'],
            font=FONTS['arabic_title']
        )
        title_label.pack(anchor=tk.W)
        
        # معلومات المستخدم
        info_frame = tk.Frame(welcome_frame, bg=COLORS['bg_main'])
        info_frame.pack(anchor=tk.W, pady=(5, 0))
        
        # الأدوار
        roles_text = format_with_icon(
            f"الدور: {', '.join([self._get_role_name(role) for role in self.user.roles])}",
            'permissions'
        )
        roles_label = tk.Label(
            info_frame,
            text=roles_text,
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            font=FONTS['arabic_main']
        )
        roles_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # التاريخ
        date_text = format_with_icon(
            f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}",
            'calendar'
        )
        date_label = tk.Label(
            info_frame,
            text=date_text,
            bg=COLORS['bg_main'],
            fg=COLORS['text_secondary'],
            font=FONTS['arabic_main']
        )
        date_label.pack(side=tk.LEFT)
        
        # خط فاصل
        Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
    
    def create_stats_section(self, parent):
        """إنشاء قسم الإحصائيات"""
        SectionHeader(parent, "نظرة عامة", icon='chart').pack(fill=tk.X, pady=(0, 15))
        
        stats_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # الحصول على الإحصائيات
        all_courses = self.course_manager.list_all_courses()
        total_courses = len(all_courses)
        active_courses = sum(1 for c in all_courses if c.get('status') == 'active')
        completed_courses = sum(1 for c in all_courses if c.get('status') == 'completed')
        
        # البطاقات الإحصائية
        stats = [
            {
                'title': 'إجمالي المقررات',
                'value': str(total_courses),
                'icon': 'course',
                'color': COLORS['stage1_color']
            },
            {
                'title': 'المقررات النشطة',
                'value': str(active_courses),
                'icon': 'active',
                'color': COLORS['status_active']
            },
            {
                'title': 'المقررات المكتملة',
                'value': str(completed_courses),
                'icon': 'completed',
                'color': COLORS['status_completed']
            },
            {
                'title': 'التقارير',
                'value': '0',
                'icon': 'report',
                'color': COLORS['primary_gold']
            },
        ]
        
        for i, stat in enumerate(stats):
            col = i % 4
            stat_card = self.create_stat_card(
                stats_frame,
                stat['title'],
                stat['value'],
                stat['icon'],
                stat['color']
            )
            stat_card.grid(row=0, column=col, padx=5, sticky='ew')
        
        # جعل الأعمدة متساوية العرض
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1, uniform='stats')
    
    def create_stat_card(self, parent, title, value, icon, color):
        """إنشاء بطاقة إحصائية"""
        card = tk.Frame(
            parent,
            bg=color,
            relief=tk.RAISED,
            borderwidth=1
        )
        
        # الأيقونة
        icon_label = tk.Label(
            card,
            text=get_icon(icon, ''),
            bg=color,
            fg=COLORS['text_white'],
            font=('Arial', 30)
        )
        icon_label.pack(pady=(15, 5))
        
        # القيمة
        value_label = tk.Label(
            card,
            text=value,
            bg=color,
            fg=COLORS['text_white'],
            font=('Arial', 24, 'bold')
        )
        value_label.pack()
        
        # العنوان
        title_label = tk.Label(
            card,
            text=title,
            bg=color,
            fg=COLORS['text_white'],
            font=FONTS['arabic_main']
        )
        title_label.pack(pady=(5, 15))
        
        return card
    
    def create_quick_actions_section(self, parent):
        """إنشاء قسم الإجراءات السريعة"""
        SectionHeader(parent, "الإجراءات السريعة", icon='menu').pack(fill=tk.X, pady=(0, 15))
        
        actions_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        actions_frame.pack(fill=tk.X, pady=(0, 20))
        
        # الأزرار السريعة
        actions = []
        
        # زر إنشاء مقرر جديد (فقط لمدير البرنامج)
        if self.access_control.has_permission(self.user.user_id, 'create_course_master'):
            actions.append({
                'text': 'إنشاء مقرر جديد',
                'icon': 'new_course',
                'command': self.on_new_course,
                'style': 'primary'
            })
        
        # زر فتح مقرر
        actions.append({
            'text': 'فتح مقرر',
            'icon': 'open_file',
            'command': self.on_open_course,
            'style': 'secondary'
        })
        
        # زر عرض التقارير
        actions.append({
            'text': 'عرض التقارير',
            'icon': 'report',
            'command': self.on_view_reports,
            'style': 'info'
        })
        
        # زر الإعدادات
        actions.append({
            'text': 'الإعدادات',
            'icon': 'settings',
            'command': self.on_settings,
            'style': 'secondary'
        })
        
        # إنشاء الأزرار
        for i, action in enumerate(actions):
            btn = EnhancedButton(
                actions_frame,
                text=action['text'],
                icon=action['icon'],
                command=action['command'],
                style=action['style'],
                width=20
            )
            btn.grid(row=0, column=i, padx=5, sticky='ew')
        
        # جعل الأعمدة متساوية العرض
        for i in range(len(actions)):
            actions_frame.grid_columnconfigure(i, weight=1)
    
    def create_recent_courses_section(self, parent):
        """إنشاء قسم المقررات الأخيرة"""
        SectionHeader(parent, "المقررات الأخيرة", icon='course_list').pack(fill=tk.X, pady=(0, 15))
        
        # بطاقة المقررات
        courses_card = CardFrame(parent)
        courses_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # قائمة المقررات
        courses_frame = tk.Frame(courses_card.content_frame, bg=COLORS['bg_main'])
        courses_frame.pack(fill=tk.BOTH, expand=True)
        
        # الحصول على آخر المقررات
        all_courses = self.course_manager.list_all_courses()
        recent_courses = sorted(
            all_courses,
            key=lambda x: x.get('modified_date', ''),
            reverse=True
        )[:5]  # آخر 5 مقررات
        
        if recent_courses:
            # عناوين الأعمدة
            headers = ['رمز المقرر', 'اسم المقرر', 'البرنامج', 'الحالة', 'آخر تحديث', 'الإجراءات']
            for col, header in enumerate(headers):
                header_label = tk.Label(
                    courses_frame,
                    text=header,
                    bg=COLORS['bg_secondary'],
                    fg=COLORS['text_primary'],
                    font=FONTS['arabic_header'],
                    borderwidth=1,
                    relief=tk.SOLID,
                    padx=10,
                    pady=8
                )
                header_label.grid(row=0, column=col, sticky='ew')
            
            # البيانات
            for row, course in enumerate(recent_courses, start=1):
                # رمز المقرر
                code_label = tk.Label(
                    courses_frame,
                    text=course.get('course_code', 'N/A'),
                    bg=COLORS['bg_main'],
                    fg=COLORS['text_primary'],
                    font=FONTS['arabic_main'],
                    borderwidth=1,
                    relief=tk.SOLID,
                    padx=10,
                    pady=8
                )
                code_label.grid(row=row, column=0, sticky='ew')
                
                # اسم المقرر
                title_label = tk.Label(
                    courses_frame,
                    text=course.get('course_title', 'N/A'),
                    bg=COLORS['bg_main'],
                    fg=COLORS['text_primary'],
                    font=FONTS['arabic_main'],
                    borderwidth=1,
                    relief=tk.SOLID,
                    padx=10,
                    pady=8,
                    anchor=tk.W
                )
                title_label.grid(row=row, column=1, sticky='ew')
                
                # البرنامج
                program_label = tk.Label(
                    courses_frame,
                    text=course.get('program', 'N/A'),
                    bg=COLORS['bg_main'],
                    fg=COLORS['text_primary'],
                    font=FONTS['arabic_main'],
                    borderwidth=1,
                    relief=tk.SOLID,
                    padx=10,
                    pady=8
                )
                program_label.grid(row=row, column=2, sticky='ew')
                
                # الحالة
                status_frame = tk.Frame(
                    courses_frame,
                    bg=COLORS['bg_main'],
                    borderwidth=1,
                    relief=tk.SOLID
                )
                status_frame.grid(row=row, column=3, sticky='ew')
                
                status_badge = StatusBadge(
                    status_frame,
                    status=course.get('status', 'draft')
                )
                status_badge.pack(pady=5)
                
                # آخر تحديث
                modified_date = course.get('modified_date', '')
                if modified_date and len(modified_date) >= 10:
                    display_date = modified_date[:10]
                else:
                    display_date = 'N/A'
                
                updated_label = tk.Label(
                    courses_frame,
                    text=display_date,
                    bg=COLORS['bg_main'],
                    fg=COLORS['text_secondary'],
                    font=FONTS['arabic_small'],
                    borderwidth=1,
                    relief=tk.SOLID,
                    padx=10,
                    pady=8
                )
                updated_label.grid(row=row, column=4, sticky='ew')
                
                # الإجراءات
                actions_frame = tk.Frame(
                    courses_frame,
                    bg=COLORS['bg_main'],
                    borderwidth=1,
                    relief=tk.SOLID
                )
                actions_frame.grid(row=row, column=5, sticky='ew')
                
                open_btn = EnhancedButton(
                    actions_frame,
                    text='فتح',
                    icon='open_file',
                    command=lambda c=course: self.on_open_specific_course(c),
                    style='info',
                    width=10
                )
                open_btn.pack(pady=5, padx=5)
            
            # جعل الأعمدة قابلة للتوسع
            for col in range(len(headers)):
                courses_frame.grid_columnconfigure(col, weight=1)
        
        else:
            # لا توجد مقررات
            no_courses_label = InfoLabel(
                courses_frame,
                text="لا توجد مقررات حتى الآن",
                icon_type='info'
            )
            no_courses_label.pack(pady=50)
    
    def create_notifications_section(self, parent):
        """إنشاء قسم التنبيهات"""
        SectionHeader(parent, "التنبيهات والإشعارات", icon='notification').pack(fill=tk.X, pady=(0, 15))
        
        # بطاقة التنبيهات
        notif_card = CardFrame(parent)
        notif_card.pack(fill=tk.BOTH, expand=True)
        
        # رسائل تنبيهية
        InfoLabel(
            notif_card.content_frame,
            text="مرحباً بك في نظام قياس مخرجات التعلم",
            icon_type='success'
        ).pack(anchor=tk.W, pady=5)
        
        InfoLabel(
            notif_card.content_frame,
            text="لديك صلاحية الوصول إلى جميع المقررات",
            icon_type='info'
        ).pack(anchor=tk.W, pady=5)
        
        if self.access_control.has_permission(self.user.user_id, 'create_course_master'):
            InfoLabel(
                notif_card.content_frame,
                text="يمكنك إنشاء مقررات جديدة من قائمة الإجراءات السريعة",
                icon_type='info'
            ).pack(anchor=tk.W, pady=5)
    
    def _get_role_name(self, role):
        """الحصول على اسم الدور بالعربية"""
        role_names = {
            'program_manager': 'مدير البرنامج',
            'course_coordinator': 'منسق المقرر',
            'course_instructor': 'أستاذ المقرر',
            'quality_officer': 'مسؤول الجودة',
            'admin': 'مدير النظام',
        }
        return role_names.get(role, role)
    
    # ═══════════════════════════════════════════════════════════════
    # دوال معالجة الأحداث
    # ═══════════════════════════════════════════════════════════════
    
    def on_new_course(self):
        """إنشاء مقرر جديد"""
        messagebox.showinfo("إنشاء مقرر", "سيتم فتح نافذة إنشاء مقرر جديد")
    
    def on_open_course(self):
        """فتح مقرر"""
        messagebox.showinfo("فتح مقرر", "سيتم فتح نافذة اختيار المقرر")
    
    def on_view_reports(self):
        """عرض التقارير"""
        messagebox.showinfo("التقارير", "سيتم فتح صفحة التقارير")
    
    def on_settings(self):
        """الإعدادات"""
        messagebox.showinfo("الإعدادات", "سيتم فتح نافذة الإعدادات")
    
    def on_open_specific_course(self, course):
        """فتح مقرر محدد"""
        messagebox.showinfo(
            "فتح المقرر",
            f"سيتم فتح المقرر: {course.get('course_title')}"
        )
