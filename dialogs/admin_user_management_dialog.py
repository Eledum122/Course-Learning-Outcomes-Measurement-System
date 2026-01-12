"""
Admin User Management Dialog - واجهة إدارة المستخدمين للمدير
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
from datetime import datetime

from managers.access_control import AccessControl
from managers.faculty_manager import FacultyManager
from models.user import User
from config import ROLES, COLORS
from translations import t
from utils.audit_logger import log_create_user, log_update_user, log_delete_user


class AdminUserManagementDialog:
    """واجهة إدارة المستخدمين الكاملة"""

    def __init__(self, parent, access_control: AccessControl, language: str = 'ar'):
        """
        تهيئة واجهة إدارة المستخدمين

        Args:
            parent: النافذة الأب
            access_control: مدير التحكم في الصلاحيات
            language: اللغة (ar أو en)
        """
        self.parent = parent
        self.access_control = access_control
        self.language = language
        self.result = None

        # إنشاء النافذة
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(t("user_management", language))
        self.dialog.geometry("1200x700")
        self.dialog.resizable(True, True)

        # جعل النافذة في الواجهة
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # تطبيق الألوان
        self.dialog.configure(bg=COLORS['bg_light'])

        # إنشاء الواجهة
        self._create_widgets()
        self._load_users()

        # وضع النافذة في المنتصف
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # الإطار الرئيسي
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg_light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # العنوان
        title_frame = tk.Frame(main_frame, bg=COLORS['primary'], height=80)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="👥 " + ("إدارة المستخدمين" if self.language == 'ar' else "User Management"),
            font=('Arial', 18, 'bold'),
            bg=COLORS['primary'],
            fg='white'
        )
        title_label.pack(expand=True)

        # إطار الأدوات العلوي
        toolbar_frame = tk.Frame(main_frame, bg=COLORS['bg_light'])
        toolbar_frame.pack(fill=tk.X, pady=(0, 15))

        # شريط البحث
        search_frame = tk.Frame(toolbar_frame, bg=COLORS['bg_light'])
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            search_frame,
            text="🔍 " + ("بحث:" if self.language == 'ar' else "Search:"),
            font=('Arial', 10),
            bg=COLORS['bg_light']
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filter_users())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            width=40
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # أزرار الإجراءات
        buttons_frame = tk.Frame(toolbar_frame, bg=COLORS['bg_light'])
        buttons_frame.pack(side=tk.RIGHT)

        self._create_action_button(
            buttons_frame,
            "➕ " + ("مستخدم جديد" if self.language == 'ar' else "New User"),
            self._add_user,
            COLORS['success']
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            buttons_frame,
            "✏️ " + ("تعديل" if self.language == 'ar' else "Edit"),
            self._edit_user,
            COLORS['primary']
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            buttons_frame,
            "🔑 " + ("تغيير كلمة المرور" if self.language == 'ar' else "Change Password"),
            self._change_password,
            '#9C27B0'  # Purple color
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            buttons_frame,
            "🔄 " + ("التبديل إلى حساب" if self.language == 'ar' else "Switch to Account"),
            self._switch_to_user,
            '#FF9800'  # Orange color
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            buttons_frame,
            "🗑️ " + ("حذف" if self.language == 'ar' else "Delete"),
            self._delete_user,
            COLORS['danger']
        ).pack(side=tk.LEFT, padx=5)

        # جدول المستخدمين
        self._create_users_table(main_frame)

        # إطار التفاصيل
        self._create_details_panel(main_frame)

        # إطار الأزرار السفلي
        bottom_frame = tk.Frame(main_frame, bg=COLORS['bg_light'])
        bottom_frame.pack(fill=tk.X, pady=(15, 0))

        self._create_action_button(
            bottom_frame,
            "📊 " + ("إحصائيات" if self.language == 'ar' else "Statistics"),
            self._show_statistics,
            COLORS['info']
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            bottom_frame,
            "📋 " + ("تصدير القائمة" if self.language == 'ar' else "Export List"),
            self._export_users,
            COLORS['warning']
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            bottom_frame,
            "🔑 " + ("تقرير الحسابات" if self.language == 'ar' else "Accounts Report"),
            self._show_credentials_report,
            '#9C27B0'
        ).pack(side=tk.LEFT, padx=5)

        self._create_action_button(
            bottom_frame,
            "❌ " + ("إغلاق" if self.language == 'ar' else "Close"),
            self.dialog.destroy,
            COLORS['secondary']
        ).pack(side=tk.RIGHT, padx=5)

    def _create_action_button(self, parent, text, command, color):
        """إنشاء زر إجراء"""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Arial', 10, 'bold'),
            bg=color,
            fg='white',
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2'
        )

        # تأثير hover
        button.bind('<Enter>', lambda e: button.config(bg=self._darken_color(color)))
        button.bind('<Leave>', lambda e: button.config(bg=color))

        return button

    def _darken_color(self, color):
        """تغميق اللون قليلاً"""
        # تحويل hex إلى RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        # تغميق بنسبة 20%
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))

        return f'#{r:02x}{g:02x}{b:02x}'

    def _create_users_table(self, parent):
        """إنشاء جدول المستخدمين"""
        # إطار الجدول
        table_frame = tk.Frame(parent, bg='white', relief=tk.SOLID, bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # عناوين الأعمدة
        columns = {
            'ar': ('اسم المستخدم', 'الاسم الكامل', 'البريد', 'الأدوار', 'الحالة', 'آخر دخول'),
            'en': ('Username', 'Full Name', 'Email', 'Roles', 'Status', 'Last Login')
        }

        self.tree = ttk.Treeview(
            table_frame,
            columns=('username', 'fullname', 'email', 'roles', 'status', 'last_login'),
            show='tree headings',
            height=15
        )

        # تكوين الأعمدة
        self.tree.column('#0', width=50, minwidth=50, anchor='center')
        self.tree.column('username', width=150, minwidth=100)
        self.tree.column('fullname', width=200, minwidth=150)
        self.tree.column('email', width=200, minwidth=150)
        self.tree.column('roles', width=200, minwidth=150)
        self.tree.column('status', width=100, minwidth=80, anchor='center')
        self.tree.column('last_login', width=150, minwidth=120)

        # عناوين الأعمدة
        self.tree.heading('#0', text='#')
        for i, col in enumerate(['username', 'fullname', 'email', 'roles', 'status', 'last_login']):
            self.tree.heading(col, text=columns[self.language][i])

        # شريط التمرير
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # التخطيط
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الأحداث
        self.tree.bind('<<TreeviewSelect>>', self._on_user_select)
        self.tree.bind('<Double-1>', lambda e: self._edit_user())

    def _create_details_panel(self, parent):
        """إنشاء لوحة التفاصيل"""
        details_frame = tk.Frame(parent, bg='white', relief=tk.SOLID, bd=1)
        details_frame.pack(fill=tk.X, pady=(0, 0))

        # عنوان اللوحة
        header = tk.Frame(details_frame, bg=COLORS['info'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📝 " + ("تفاصيل المستخدم" if self.language == 'ar' else "User Details"),
            font=('Arial', 11, 'bold'),
            bg=COLORS['info'],
            fg='white'
        ).pack(pady=8)

        # محتوى التفاصيل
        content = tk.Frame(details_frame, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        self.details_label = tk.Label(
            content,
            text=("اختر مستخدماً لعرض التفاصيل" if self.language == 'ar' else "Select a user to view details"),
            font=('Arial', 10),
            bg='white',
            fg=COLORS['text_secondary'],
            justify=tk.RIGHT if self.language == 'ar' else tk.LEFT
        )
        self.details_label.pack(anchor='e' if self.language == 'ar' else 'w')

    def _format_datetime(self, dt_value) -> str:
        """تنسيق قيمة التاريخ والوقت"""
        if not dt_value:
            return '-'
        try:
            if isinstance(dt_value, str):
                dt = datetime.fromisoformat(dt_value)
                return dt.strftime('%Y-%m-%d %H:%M')
            else:
                return dt_value.strftime('%Y-%m-%d %H:%M')
        except:
            return str(dt_value) if dt_value else '-'

    def _load_users(self):
        """تحميل المستخدمين في الجدول"""
        # إعادة تحميل المستخدمين من الملف للحصول على أحدث البيانات
        self.access_control.users.clear()
        self.access_control.load_users()

        # حذف جميع الصفوف الحالية
        for item in self.tree.get_children():
            self.tree.delete(item)

        # إضافة المستخدمين
        users = sorted(self.access_control.users.values(), key=lambda u: u.username)

        for i, user in enumerate(users, 1):
            # تنسيق الأدوار
            roles_text = ', '.join([
                t(f"role_{role}", self.language) for role in user.roles
            ])

            # الحالة
            status = "✅ نشط" if user.is_active else "🔒 معطل"
            if self.language == 'en':
                status = "✅ Active" if user.is_active else "🔒 Disabled"

            # آخر دخول
            last_login = self._format_datetime(user.last_login)

            # إضافة الصف
            self.tree.insert(
                '',
                'end',
                text=str(i),
                values=(
                    user.username,
                    user.full_name,
                    user.email,
                    roles_text,
                    status,
                    last_login
                ),
                tags=('active',) if user.is_active else ('disabled',)
            )

        # تلوين الصفوف
        self.tree.tag_configure('active', background='white')
        self.tree.tag_configure('disabled', background='#f0f0f0', foreground='#999')

    def _filter_users(self):
        """تصفية المستخدمين حسب البحث"""
        search_text = self.search_var.get().lower()

        # حذف جميع الصفوف
        for item in self.tree.get_children():
            self.tree.delete(item)

        # إضافة المستخدمين المطابقين فقط
        users = sorted(self.access_control.users.values(), key=lambda u: u.username)
        counter = 1

        for user in users:
            if (search_text in user.username.lower() or
                search_text in user.full_name.lower() or
                search_text in user.email.lower()):

                roles_text = ', '.join([
                    t(f"role_{role}", self.language) for role in user.roles
                ])

                status = "✅ نشط" if user.is_active else "🔒 معطل"
                if self.language == 'en':
                    status = "✅ Active" if user.is_active else "🔒 Disabled"

                # آخر دخول
                last_login = self._format_datetime(user.last_login)

                self.tree.insert(
                    '',
                    'end',
                    text=str(counter),
                    values=(
                        user.username,
                        user.full_name,
                        user.email,
                        roles_text,
                        status,
                        last_login
                    ),
                    tags=('active',) if user.is_active else ('disabled',)
                )
                counter += 1

    def _on_user_select(self, event):
        """عند اختيار مستخدم"""
        selection = self.tree.selection()
        if not selection:
            return

        # الحصول على اسم المستخدم
        item = self.tree.item(selection[0])
        username = item['values'][0]

        # البحث عن المستخدم
        user = None
        for u in self.access_control.users.values():
            if u.username == username:
                user = u
                break

        if not user:
            return

        # عرض التفاصيل
        details = self._format_user_details(user)
        self.details_label.config(text=details, justify=tk.RIGHT if self.language == 'ar' else tk.LEFT)

    def _format_user_details(self, user: User) -> str:
        """تنسيق تفاصيل المستخدم"""
        # تنسيق التواريخ
        created_date = self._format_datetime(getattr(user, 'created_date', None))
        last_login = self._format_datetime(getattr(user, 'last_login', None))

        if self.language == 'ar':
            details = f"""
المعرف: {user.user_id}
اسم المستخدم: {user.username}
الاسم الكامل: {user.full_name}
البريد الإلكتروني: {user.email}
رقم الهاتف: {getattr(user, 'phone', '-') or '-'}
القسم: {getattr(user, 'department', '-') or '-'}

الأدوار: {', '.join([t(f"role_{role}", self.language) for role in user.roles])}
الحالة: {"نشط" if user.is_active else "معطل"}

تاريخ الإنشاء: {created_date}
آخر دخول: {last_login}
            """
        else:
            details = f"""
ID: {user.user_id}
Username: {user.username}
Full Name: {user.full_name}
Email: {user.email}
Phone: {getattr(user, 'phone', '-') or '-'}
Department: {getattr(user, 'department', '-') or '-'}

Roles: {', '.join([t(f"role_{role}", self.language) for role in user.roles])}
Status: {"Active" if user.is_active else "Disabled"}

Created At: {created_date}
Last Login: {last_login}
            """

        return details.strip()

    def _add_user(self):
        """إضافة مستخدم جديد"""
        dialog = UserEditorDialog(self.dialog, None, self.access_control, self.language)

        if dialog.result:
            self._load_users()
            messagebox.showinfo(
                t("success", self.language),
                t("user_created_success", self.language)
            )

    def _edit_user(self):
        """تعديل مستخدم"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                t("please_select_user", self.language)
            )
            return

        # الحصول على المستخدم
        item = self.tree.item(selection[0])
        username = item['values'][0]

        user = None
        for u in self.access_control.users.values():
            if u.username == username:
                user = u
                break

        if not user:
            return

        # فتح محرر المستخدم
        dialog = UserEditorDialog(self.dialog, user, self.access_control, self.language)

        if dialog.result:
            self._load_users()
            messagebox.showinfo(
                t("success", self.language),
                t("user_updated_success", self.language)
            )

    def _change_password(self):
        """تغيير كلمة مرور مستخدم"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                t("please_select_user", self.language)
            )
            return

        # الحصول على المستخدم
        item = self.tree.item(selection[0])
        username = item['values'][0]

        user = None
        for u in self.access_control.users.values():
            if u.username == username:
                user = u
                break

        if not user:
            return

        # فتح نافذة تغيير كلمة المرور
        dialog = ChangePasswordDialog(self.dialog, user, self.access_control, self.language)

        if dialog.result:
            messagebox.showinfo(
                t("success", self.language),
                ("تم تغيير كلمة المرور بنجاح" if self.language == 'ar' else "Password changed successfully")
            )

    def _delete_user(self):
        """حذف مستخدم"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                t("please_select_user", self.language)
            )
            return

        item = self.tree.item(selection[0])
        username = item['values'][0]

        # منع حذف المستخدم الحالي
        if self.access_control.current_user.username == username:
            messagebox.showerror(
                t("error", self.language),
                t("cannot_delete_current_user", self.language)
            )
            return

        # تأكيد الحذف
        confirm = messagebox.askyesno(
            t("confirm_delete", self.language),
            t("confirm_delete_user", self.language).format(username=username)
        )

        if confirm:
            user = None
            for u in self.access_control.users.values():
                if u.username == username:
                    user = u
                    break

            if user:
                self.access_control.delete_user(user.user_id)

                # تسجيل في سجل التدقيق
                log_delete_user(
                    self.access_control.current_user.username,
                    self.access_control.current_user.user_id,
                    username
                )

                self._load_users()
                messagebox.showinfo(
                    t("success", self.language),
                    t("user_deleted_success", self.language)
                )

    def _switch_to_user(self):
        """التبديل إلى حساب مستخدم آخر (للمدير فقط)"""
        # التحقق من أن المستخدم الحالي هو مدير
        if not self.access_control.current_user.has_role('admin'):
            messagebox.showerror(
                t("error", self.language),
                "هذه الميزة متاحة للمدير فقط" if self.language == 'ar' else "This feature is for admins only"
            )
            return

        # التحقق من تحديد مستخدم
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                t("warning", self.language),
                "الرجاء تحديد مستخدم للتبديل إليه" if self.language == 'ar' else "Please select a user to switch to"
            )
            return

        # الحصول على المستخدم
        item = self.tree.item(selection[0])
        username = item['values'][0]

        # منع التبديل إلى نفس الحساب
        if self.access_control.current_user.username == username:
            messagebox.showinfo(
                t("info", self.language),
                "أنت تستخدم هذا الحساب بالفعل" if self.language == 'ar' else "You are already using this account"
            )
            return

        user = None
        for u in self.access_control.users.values():
            if u.username == username:
                user = u
                break

        if not user:
            return

        # التأكيد من التبديل
        confirm = messagebox.askyesno(
            "تأكيد التبديل" if self.language == 'ar' else "Confirm Switch",
            f"هل تريد التبديل إلى حساب:\n\n"
            f"المستخدم: {username}\n"
            f"الاسم: {user.full_name}\n"
            f"الأدوار: {', '.join(user.roles)}\n\n"
            f"سيتم إغلاق النافذة الحالية وإعادة فتح النظام بحساب المستخدم الجديد.\n"
            f"يمكنك العودة إلى حساب المدير من قائمة المستخدمين."
            if self.language == 'ar' else
            f"Do you want to switch to account:\n\n"
            f"Username: {username}\n"
            f"Name: {user.full_name}\n"
            f"Roles: {', '.join(user.roles)}\n\n"
            f"The current window will be closed and the system will reopen with the new user account.\n"
            f"You can return to the admin account from the user menu."
        )

        if confirm:
            # حفظ معلومات المدير الأصلي للعودة
            original_admin = self.access_control.current_user

            # تسجيل خروج ضمني
            self.access_control.current_user = None

            # تسجيل دخول بالمستخدم الجديد
            self.access_control.current_user = user
            user.last_login = datetime.now().isoformat()
            self.access_control.save_users()

            # إغلاق نافذة إدارة المستخدمين
            self.dialog.destroy()

            # إعادة تشغيل النافذة الرئيسية بالمستخدم الجديد
            messagebox.showinfo(
                "تم التبديل بنجاح" if self.language == 'ar' else "Switched Successfully",
                f"تم التبديل إلى حساب: {user.full_name}\n\n"
                f"ملاحظة: للعودة إلى حساب المدير، اذهب إلى:\n"
                f"قائمة المستخدمين ← التبديل إلى حساب ← admin"
                if self.language == 'ar' else
                f"Switched to account: {user.full_name}\n\n"
                f"Note: To return to admin account, go to:\n"
                f"User Menu → Switch to Account → admin"
            )

            # إعادة تحميل النافذة الرئيسية
            # سنحتاج لإرسال إشارة للنافذة الرئيسية لإعادة التحميل
            self.result = {'action': 'switch_user', 'user': user}

    def _show_statistics(self):
        """عرض إحصائيات المستخدمين"""
        total_users = len(self.access_control.users)
        active_users = sum(1 for u in self.access_control.users.values() if u.is_active)
        disabled_users = total_users - active_users

        # إحصائيات حسب الدور
        role_stats = {}
        for user in self.access_control.users.values():
            for role in user.roles:
                role_stats[role] = role_stats.get(role, 0) + 1

        if self.language == 'ar':
            stats_text = f"""
📊 إحصائيات المستخدمين

إجمالي المستخدمين: {total_users}
المستخدمون النشطون: {active_users}
المستخدمون المعطلون: {disabled_users}

توزيع الأدوار:
"""
            for role, count in role_stats.items():
                stats_text += f"• {t(f'role_{role}', self.language)}: {count}\n"
        else:
            stats_text = f"""
📊 User Statistics

Total Users: {total_users}
Active Users: {active_users}
Disabled Users: {disabled_users}

Role Distribution:
"""
            for role, count in role_stats.items():
                stats_text += f"• {t(f'role_{role}', self.language)}: {count}\n"

        messagebox.showinfo(
            t("statistics", self.language),
            stats_text.strip()
        )

    def _export_users(self):
        """تصدير قائمة المستخدمين"""
        import csv

        # اختيار موقع الحفظ
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # العناوين
                if self.language == 'ar':
                    writer.writerow(['اسم المستخدم', 'الاسم الكامل', 'البريد', 'الأدوار', 'الحالة'])
                else:
                    writer.writerow(['Username', 'Full Name', 'Email', 'Roles', 'Status'])

                # البيانات
                for user in sorted(self.access_control.users.values(), key=lambda u: u.username):
                    roles_text = ', '.join([t(f"role_{role}", self.language) for role in user.roles])
                    status = "نشط" if user.is_active else "معطل"
                    if self.language == 'en':
                        status = "Active" if user.is_active else "Disabled"

                    writer.writerow([
                        user.username,
                        user.full_name,
                        user.email,
                        roles_text,
                        status
                    ])

            messagebox.showinfo(
                t("success", self.language),
                t("export_success", self.language)
            )

        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"Error exporting users: {str(e)}"
            )

    def _show_credentials_report(self):
        """عرض تقرير أسماء المستخدمين وكلمات المرور"""
        # نافذة خيارات التقرير
        options_dialog = tk.Toplevel(self.dialog)
        options_dialog.title("خيارات التقرير" if self.language == 'ar' else "Report Options")
        options_dialog.geometry("400x200")
        options_dialog.resizable(False, False)
        options_dialog.transient(self.dialog)
        options_dialog.grab_set()

        main_frame = tk.Frame(options_dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            main_frame,
            text="🔑 " + ("تقرير حسابات المستخدمين" if self.language == 'ar' else "User Accounts Report"),
            font=('Arial', 14, 'bold'),
            bg='white'
        ).pack(pady=(0, 20))

        # خيار تضمين كلمات المرور
        include_passwords_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            main_frame,
            text="تضمين كلمات المرور" if self.language == 'ar' else "Include Passwords",
            variable=include_passwords_var,
            font=('Arial', 11),
            bg='white'
        ).pack(anchor='w', pady=10)

        tk.Label(
            main_frame,
            text="⚠️ " + ("تحذير: كلمات المرور حساسة!" if self.language == 'ar' else "Warning: Passwords are sensitive!"),
            font=('Arial', 9),
            bg='white',
            fg='red'
        ).pack(pady=10)

        # أزرار
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        def show_report():
            """عرض التقرير في نافذة"""
            options_dialog.destroy()

            # إنشاء نافذة التقرير
            report_dialog = tk.Toplevel(self.dialog)
            report_dialog.title("تقرير الحسابات" if self.language == 'ar' else "Accounts Report")
            report_dialog.geometry("900x600")
            report_dialog.transient(self.dialog)

            # منطقة النص
            text_frame = tk.Frame(report_dialog)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            text_widget = tk.Text(
                text_frame,
                font=('Courier New', 10),
                yscrollcommand=scrollbar.set,
                wrap=tk.WORD
            )
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)

            # إدراج التقرير
            report = self.access_control.generate_users_credentials_report(
                include_passwords=include_passwords_var.get()
            )
            text_widget.insert('1.0', report)
            text_widget.config(state='disabled')

            # أزرار
            btn_frame = tk.Frame(report_dialog)
            btn_frame.pack(fill=tk.X, padx=10, pady=10)

            def export_report():
                """تصدير التقرير إلى ملف"""
                filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
                if filename:
                    if self.access_control.export_users_credentials_to_file(
                        filename,
                        include_passwords=include_passwords_var.get()
                    ):
                        messagebox.showinfo(
                            t("success", self.language),
                            "تم حفظ التقرير بنجاح" if self.language == 'ar' else "Report saved successfully"
                        )

            tk.Button(
                btn_frame,
                text="💾 " + ("حفظ التقرير" if self.language == 'ar' else "Save Report"),
                command=export_report,
                font=('Arial', 10, 'bold'),
                bg=COLORS['success'],
                fg='white',
                padx=20,
                pady=8
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                btn_frame,
                text="❌ " + ("إغلاق" if self.language == 'ar' else "Close"),
                command=report_dialog.destroy,
                font=('Arial', 10),
                bg=COLORS['secondary'],
                fg='white',
                padx=20,
                pady=8
            ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            buttons_frame,
            text="📄 " + ("عرض التقرير" if self.language == 'ar' else "Show Report"),
            command=show_report,
            font=('Arial', 10, 'bold'),
            bg=COLORS['primary'],
            fg='white',
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="❌ " + ("إلغاء" if self.language == 'ar' else "Cancel"),
            command=options_dialog.destroy,
            font=('Arial', 10),
            bg=COLORS['secondary'],
            fg='white',
            padx=20,
            pady=8
        ).pack(side=tk.RIGHT, padx=5)


class UserEditorDialog:
    """محرر بيانات المستخدم"""

    def __init__(self, parent, user: Optional[User], access_control: AccessControl, language: str = 'ar'):
        """
        تهيئة محرر المستخدم

        Args:
            parent: النافذة الأب
            user: المستخدم المراد تعديله (None للمستخدم الجديد)
            access_control: مدير التحكم في الصلاحيات
            language: اللغة
        """
        self.user = user
        self.access_control = access_control
        self.language = language
        self.result = None
        self.faculty_manager = FacultyManager()
        self.selected_faculty = None

        # إنشاء النافذة
        self.dialog = tk.Toplevel(parent)
        is_new = user is None
        title = ("مستخدم جديد" if is_new else "تعديل مستخدم") if language == 'ar' else ("New User" if is_new else "Edit User")
        self.dialog.title(title)
        # زيادة الارتفاع لاستيعاب حقل اختيار عضو هيئة التدريس
        height = "750" if is_new else "650"
        self.dialog.geometry(f"600x{height}")
        self.dialog.resizable(False, False)

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.dialog.configure(bg=COLORS['bg_light'])

        self._create_widgets()

        # ملء البيانات إذا كان تعديل
        if user:
            self._fill_user_data()

        # وضع النافذة في المنتصف
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.dialog.wait_window()

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # تهيئة متغيرات الحقول أولاً قبل إنشاء أي عناصر واجهة
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        self.full_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.department_var = tk.StringVar()

        main_frame = tk.Frame(self.dialog, bg=COLORS['bg_light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # العنوان
        is_new = self.user is None
        title = ("➕ مستخدم جديد" if is_new else "✏️ تعديل مستخدم") if self.language == 'ar' else ("➕ New User" if is_new else "✏️ Edit User")

        tk.Label(
            main_frame,
            text=title,
            font=('Arial', 16, 'bold'),
            bg=COLORS['bg_light'],
            fg=COLORS['primary']
        ).pack(pady=(0, 20))

        # نموذج الإدخال
        form_frame = tk.Frame(main_frame, bg='white', relief=tk.SOLID, bd=1)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # حقول الإدخال
        fields_frame = tk.Frame(form_frame, bg='white')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # اختيار عضو هيئة تدريس (للمستخدم الجديد فقط)
        if not self.user:
            self._create_faculty_selector(fields_frame)

        # اسم المستخدم
        self._create_field(
            fields_frame,
            "اسم المستخدم:" if self.language == 'ar' else "Username:",
            'username'
        )

        # كلمة المرور (للمستخدم الجديد فقط)
        if not self.user:
            self._create_field(
                fields_frame,
                "كلمة المرور:" if self.language == 'ar' else "Password:",
                'password',
                show='*'
            )

            self._create_field(
                fields_frame,
                "تأكيد كلمة المرور:" if self.language == 'ar' else "Confirm Password:",
                'confirm_password',
                show='*'
            )

        # الاسم الكامل
        self._create_field(
            fields_frame,
            "الاسم الكامل:" if self.language == 'ar' else "Full Name:",
            'full_name'
        )

        # البريد الإلكتروني
        self._create_field(
            fields_frame,
            "البريد الإلكتروني:" if self.language == 'ar' else "Email:",
            'email'
        )

        # رقم الهاتف
        self._create_field(
            fields_frame,
            "رقم الهاتف:" if self.language == 'ar' else "Phone:",
            'phone'
        )

        # القسم
        self._create_field(
            fields_frame,
            "القسم:" if self.language == 'ar' else "Department:",
            'department'
        )

        # الأدوار
        self._create_roles_field(fields_frame)

        # الحالة
        self._create_status_field(fields_frame)

        # الأزرار
        buttons_frame = tk.Frame(main_frame, bg=COLORS['bg_light'])
        buttons_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Button(
            buttons_frame,
            text="💾 " + ("حفظ" if self.language == 'ar' else "Save"),
            command=self._save,
            font=('Arial', 11, 'bold'),
            bg=COLORS['success'],
            fg='white',
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.LEFT if self.language == 'en' else tk.RIGHT, padx=5)

        tk.Button(
            buttons_frame,
            text="❌ " + ("إلغاء" if self.language == 'ar' else "Cancel"),
            command=self.dialog.destroy,
            font=('Arial', 11),
            bg=COLORS['secondary'],
            fg='white',
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.LEFT if self.language == 'en' else tk.RIGHT, padx=5)

    def _create_field(self, parent, label_text, field_name, show=None):
        """إنشاء حقل إدخال"""
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(fill=tk.X, pady=8)

        label = tk.Label(
            field_frame,
            text=label_text,
            font=('Arial', 10),
            bg='white',
            anchor='e' if self.language == 'ar' else 'w',
            width=20
        )
        label.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=(0, 10))

        # استخدام المتغير الموجود بدلاً من إنشاء جديد
        var = getattr(self, f'{field_name}_var')
        entry = tk.Entry(
            field_frame,
            textvariable=var,
            font=('Arial', 10),
            show=show
        )
        entry.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, fill=tk.X, expand=True)

        # تفعيل/تعطيل حقل اسم المستخدم
        if field_name == 'username' and self.user:
            entry.config(state='disabled')

    def _create_faculty_selector(self, parent):
        """إنشاء محدد عضو هيئة التدريس"""
        field_frame = tk.Frame(parent, bg='#E3F2FD')
        field_frame.pack(fill=tk.X, pady=8, padx=5)

        label = tk.Label(
            field_frame,
            text=("👨‍🏫 عضو هيئة التدريس:" if self.language == 'ar' else "👨‍🏫 Faculty Member:"),
            font=('Arial', 10, 'bold'),
            bg='#E3F2FD',
            anchor='e' if self.language == 'ar' else 'w',
            width=20
        )
        label.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=(10, 10), pady=8)

        # Combobox لاختيار عضو هيئة التدريس
        members = self.faculty_manager.get_all_members()
        member_names = [""] + [f"{m.employee_id} - {m.name}" for m in members]

        self.faculty_combo = ttk.Combobox(
            field_frame,
            values=member_names,
            font=('Arial', 10),
            state='readonly'
        )
        self.faculty_combo.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
        self.faculty_combo.current(0)
        self.faculty_combo.bind('<<ComboboxSelected>>', self._on_faculty_selected)

        # زر للمساعدة
        help_text = "اختياري: اختر عضو هيئة تدريس لإنشاء حساب مستخدم له تلقائياً" if self.language == 'ar' else "Optional: Select a faculty member to auto-create their user account"
        help_label = tk.Label(
            field_frame,
            text="ℹ️",
            font=('Arial', 12),
            bg='#E3F2FD',
            cursor='hand2'
        )
        help_label.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        # تلميح عند التمرير
        self._create_tooltip(help_label, help_text)

    def _create_tooltip(self, widget, text):
        """إنشاء تلميح عند التمرير"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", relief='solid', borderwidth=1, font=('Arial', 9))
            label.pack()
            widget.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def _on_faculty_selected(self, event=None):
        """عند اختيار عضو هيئة تدريس"""
        selection = self.faculty_combo.get()
        if not selection:
            self.selected_faculty = None
            return

        # الحصول على الرقم الوظيفي من الاختيار
        employee_id = selection.split(" - ")[0]

        # البحث عن عضو هيئة التدريس
        self.selected_faculty = self.faculty_manager.get_member_by_id(employee_id)

        if self.selected_faculty:
            # ملء الحقول تلقائياً
            username = User.generate_username(self.selected_faculty.name, self.selected_faculty.employee_id)
            password = User.generate_password(self.selected_faculty.employee_id)

            self.username_var.set(username)
            self.password_var.set(password)
            self.confirm_password_var.set(password)
            self.full_name_var.set(self.selected_faculty.name)
            self.email_var.set(self.selected_faculty.email)
            self.phone_var.set(self.selected_faculty.phone)
            self.department_var.set(self.selected_faculty.department_ar if self.language == 'ar' else self.selected_faculty.department_en)

    def _create_roles_field(self, parent):
        """إنشاء حقل الأدوار"""
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(fill=tk.X, pady=8)

        label = tk.Label(
            field_frame,
            text=("الأدوار:" if self.language == 'ar' else "Roles:"),
            font=('Arial', 10),
            bg='white',
            anchor='e' if self.language == 'ar' else 'w',
            width=20
        )
        label.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=(0, 10), anchor='n')

        roles_container = tk.Frame(field_frame, bg='white')
        roles_container.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, fill=tk.X, expand=True)

        self.role_vars = {}
        for role, role_info in ROLES.items():
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                roles_container,
                text=t(f"role_{role}", self.language),
                variable=var,
                font=('Arial', 9),
                bg='white'
            )
            cb.pack(anchor='e' if self.language == 'ar' else 'w')
            self.role_vars[role] = var

    def _create_status_field(self, parent):
        """إنشاء حقل الحالة"""
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(fill=tk.X, pady=8)

        label = tk.Label(
            field_frame,
            text=("الحالة:" if self.language == 'ar' else "Status:"),
            font=('Arial', 10),
            bg='white',
            anchor='e' if self.language == 'ar' else 'w',
            width=20
        )
        label.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=(0, 10))

        self.status_var = tk.BooleanVar(value=True)
        cb = tk.Checkbutton(
            field_frame,
            text=("نشط" if self.language == 'ar' else "Active"),
            variable=self.status_var,
            font=('Arial', 10),
            bg='white'
        )
        cb.pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT)

    def _fill_user_data(self):
        """ملء بيانات المستخدم"""
        if not self.user:
            return

        self.username_var.set(self.user.username)
        self.full_name_var.set(self.user.full_name)
        self.email_var.set(self.user.email)
        self.phone_var.set(self.user.phone or '')
        self.department_var.set(self.user.department or '')

        for role in self.user.roles:
            if role in self.role_vars:
                self.role_vars[role].set(True)

        self.status_var.set(self.user.is_active)

    def _save(self):
        """حفظ البيانات"""
        # التحقق من البيانات
        username = self.username_var.get().strip()
        full_name = self.full_name_var.get().strip()
        email = self.email_var.get().strip()

        if not username or not full_name or not email:
            messagebox.showerror(
                t("error", self.language),
                t("required_fields_missing", self.language)
            )
            return

        # التحقق من كلمة المرور للمستخدم الجديد
        if not self.user:
            password = self.password_var.get()
            confirm = self.confirm_password_var.get()

            if not password:
                messagebox.showerror(
                    t("error", self.language),
                    t("password_required", self.language)
                )
                return

            if password != confirm:
                messagebox.showerror(
                    t("error", self.language),
                    t("passwords_dont_match", self.language)
                )
                return

        # جمع الأدوار المختارة
        selected_roles = [role for role, var in self.role_vars.items() if var.get()]

        if not selected_roles:
            messagebox.showerror(
                t("error", self.language),
                t("at_least_one_role_required", self.language)
            )
            return

        # الحفظ
        try:
            if self.user:
                # تحديث مستخدم موجود
                self.user.full_name = full_name
                self.user.email = email
                self.user.phone = self.phone_var.get().strip() or None
                self.user.department = self.department_var.get().strip() or None
                self.user.roles = selected_roles
                self.user.is_active = self.status_var.get()

                self.access_control.update_user(self.user.user_id, self.user.to_dict())

                # تسجيل في سجل التدقيق
                log_update_user(
                    self.access_control.current_user.username,
                    self.access_control.current_user.user_id,
                    username,
                    {
                        'full_name': full_name,
                        'email': email,
                        'roles': selected_roles,
                        'is_active': self.status_var.get()
                    }
                )

            else:
                # إنشاء مستخدم جديد
                employee_id = ""
                faculty_id = ""

                if self.selected_faculty:
                    employee_id = self.selected_faculty.employee_id
                    faculty_id = self.selected_faculty.faculty_id

                user_id = self.access_control.create_user(
                    username=username,
                    password=self.password_var.get(),
                    full_name=full_name,
                    email=email,
                    roles=selected_roles,
                    employee_id=employee_id,
                    faculty_id=faculty_id
                )

                # تسجيل في سجل التدقيق
                log_create_user(
                    self.access_control.current_user.username,
                    self.access_control.current_user.user_id,
                    username,
                    selected_roles
                )

            self.result = True
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"Error saving user: {str(e)}"
            )


class ChangePasswordDialog:
    """نافذة تغيير كلمة المرور"""

    def __init__(self, parent, user: User, access_control: AccessControl, language: str = 'ar'):
        """
        تهيئة نافذة تغيير كلمة المرور

        Args:
            parent: النافذة الأب
            user: المستخدم
            access_control: مدير التحكم في الصلاحيات
            language: اللغة
        """
        self.user = user
        self.access_control = access_control
        self.language = language
        self.result = None

        # إنشاء النافذة
        self.dialog = tk.Toplevel(parent)
        title = "تغيير كلمة المرور" if language == 'ar' else "Change Password"
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.dialog.configure(bg=COLORS['bg_light'])

        self._create_widgets()

        # وضع النافذة في المنتصف
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        self.dialog.wait_window()

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        main_frame = tk.Frame(self.dialog, bg=COLORS['bg_light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # العنوان
        tk.Label(
            main_frame,
            text=f"🔑 {'تغيير كلمة المرور' if self.language == 'ar' else 'Change Password'}",
            font=('Arial', 18, 'bold'),
            bg=COLORS['bg_light'],
            fg=COLORS['primary']
        ).pack(pady=(0, 10))

        # معلومات المستخدم
        info_frame = tk.Frame(main_frame, bg='white', relief=tk.SOLID, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 20), padx=10)

        tk.Label(
            info_frame,
            text=f"{'المستخدم' if self.language == 'ar' else 'User'}: {self.user.username}",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2C3E50'
        ).pack(pady=15)

        tk.Label(
            info_frame,
            text=f"{'الاسم' if self.language == 'ar' else 'Name'}: {self.user.full_name}",
            font=('Arial', 10),
            bg='white',
            fg='#7F8C8D'
        ).pack(pady=(0, 15))

        # نموذج الإدخال
        form_frame = tk.Frame(main_frame, bg='white', relief=tk.SOLID, bd=1)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        fields_frame = tk.Frame(form_frame, bg='white')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # كلمة المرور الجديدة
        self.new_password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        tk.Label(
            fields_frame,
            text="كلمة المرور الجديدة:" if self.language == 'ar' else "New Password:",
            font=('Arial', 11, 'bold'),
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).pack(fill=tk.X, pady=(0, 5))

        new_pass_entry = tk.Entry(
            fields_frame,
            textvariable=self.new_password_var,
            font=('Arial', 11),
            show='*'
        )
        new_pass_entry.pack(fill=tk.X, pady=(0, 15))
        new_pass_entry.focus()

        tk.Label(
            fields_frame,
            text="تأكيد كلمة المرور:" if self.language == 'ar' else "Confirm Password:",
            font=('Arial', 11, 'bold'),
            bg='white',
            anchor='e' if self.language == 'ar' else 'w'
        ).pack(fill=tk.X, pady=(0, 5))

        tk.Entry(
            fields_frame,
            textvariable=self.confirm_password_var,
            font=('Arial', 11),
            show='*'
        ).pack(fill=tk.X, pady=(0, 15))

        # الأزرار
        buttons_frame = tk.Frame(main_frame, bg=COLORS['bg_light'])
        buttons_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Button(
            buttons_frame,
            text="✔️ " + ("حفظ" if self.language == 'ar' else "Save"),
            command=self._save,
            font=('Arial', 12, 'bold'),
            bg=COLORS['success'],
            fg='white',
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="❌ " + ("إلغاء" if self.language == 'ar' else "Cancel"),
            command=self.dialog.destroy,
            font=('Arial', 12, 'bold'),
            bg=COLORS['secondary'],
            fg='white',
            bd=0,
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side=tk.RIGHT if self.language == 'ar' else tk.LEFT, padx=5)

    def _save(self):
        """حفظ كلمة المرور الجديدة"""
        new_password = self.new_password_var.get().strip()
        confirm_password = self.confirm_password_var.get().strip()

        # التحقق من الإدخال
        if not new_password:
            messagebox.showerror(
                t("error", self.language),
                "يرجى إدخال كلمة المرور الجديدة" if self.language == 'ar' else "Please enter new password"
            )
            return

        if len(new_password) < 4:
            messagebox.showerror(
                t("error", self.language),
                "كلمة المرور يجب أن تكون 4 أحرف على الأقل" if self.language == 'ar' else "Password must be at least 4 characters"
            )
            return

        if new_password != confirm_password:
            messagebox.showerror(
                t("error", self.language),
                "كلمتا المرور غير متطابقتين" if self.language == 'ar' else "Passwords do not match"
            )
            return

        try:
            # تحديث كلمة المرور
            self.user.set_password(new_password)
            self.access_control.update_user(self.user)

            # تسجيل في سجل التدقيق
            from utils.audit_logger import log_action
            log_action(
                self.access_control.current_user.username,
                self.access_control.current_user.user_id,
                "change_password",
                f"Changed password for user: {self.user.username}"
            )

            self.result = True
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(
                t("error", self.language),
                f"Error changing password: {str(e)}"
            )
