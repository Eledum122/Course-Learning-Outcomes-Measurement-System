"""
نظام التحكم في الصلاحيات
Access Control System
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User
from config import ROLES, USERS_FILE


class AccessControl:
    """نظام التحكم في الصلاحيات"""

    def __init__(self, session_timeout_minutes: int = 120):
        """
        تهيئة نظام التحكم في الصلاحيات

        Args:
            session_timeout_minutes: مدة انتهاء الجلسة بالدقائق (افتراضياً ساعتين)
        """
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        self.section_assignments = {}

        # إدارة الجلسات
        self.session_timeout_minutes = session_timeout_minutes
        self.last_activity_time: Optional[datetime] = None
        self.session_start_time: Optional[datetime] = None

        self.load_users()
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة المستخدمين
    # ═══════════════════════════════════════════════════════════════
    
    def load_users(self):
        """تحميل المستخدمين من الملف"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_data in data.get('users', []):
                        user = User.from_dict(user_data)
                        self.users[user.user_id] = user
            except Exception as e:
                print(f"Error loading users: {e}")
        else:
            # إنشاء مستخدم افتراضي (admin)
            self.create_default_admin()
    
    def save_users(self):
        """حفظ المستخدمين إلى الملف"""
        try:
            data = {
                'users': [user.to_dict() for user in self.users.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            # إنشاء المجلد إذا لم يكن موجوداً
            os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
            
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def create_default_admin(self):
        """إنشاء مستخدم مدير افتراضي"""
        admin = User(
            user_id='admin_001',
            username='admin',
            password_hash=User.hash_password('admin123'),
            full_name='System Administrator',
            email='admin@tabuk.edu.sa',
            roles=['admin']
        )
        self.users[admin.user_id] = admin
        self.save_users()
        print("Default admin user created: admin / admin123")
    
    def create_user(self, username: str, password: str, full_name: str,
                   email: str, roles: List[str], employee_id: str = "",
                   faculty_id: str = "") -> Optional[User]:
        """إنشاء مستخدم جديد"""
        # التحقق من عدم تكرار اسم المستخدم
        for user in self.users.values():
            if user.username == username:
                return None

        # إنشاء معرف فريد
        user_id = f"user_{len(self.users) + 1:03d}"

        # إنشاء المستخدم
        user = User(
            user_id=user_id,
            username=username,
            password_hash=User.hash_password(password),
            full_name=full_name,
            email=email,
            roles=roles,
            employee_id=employee_id,
            faculty_id=faculty_id
        )

        self.users[user_id] = user
        self.save_users()
        return user

    def create_user_from_faculty(self, faculty_member, roles: List[str]) -> Optional[User]:
        """
        إنشاء مستخدم من عضو هيئة تدريس

        Args:
            faculty_member: عضو هيئة التدريس (FacultyMember)
            roles: أدوار المستخدم

        Returns:
            المستخدم المُنشأ أو None إذا فشل
        """
        # توليد اسم المستخدم وكلمة المرور
        username = User.generate_username(faculty_member.name, faculty_member.employee_id)
        password = User.generate_password(faculty_member.employee_id)

        # التحقق من عدم وجود مستخدم بنفس اسم المستخدم
        if self.get_user_by_username(username):
            return None

        # إنشاء المستخدم
        return self.create_user(
            username=username,
            password=password,
            full_name=faculty_member.name,
            email=faculty_member.email,
            roles=roles,
            employee_id=faculty_member.employee_id,
            faculty_id=faculty_member.faculty_id
        )
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """تحديث بيانات مستخدم"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        if 'password' in kwargs:
            user.password_hash = User.hash_password(kwargs['password'])
        if 'full_name' in kwargs:
            user.full_name = kwargs['full_name']
        if 'email' in kwargs:
            user.email = kwargs['email']
        if 'roles' in kwargs:
            user.roles = kwargs['roles']
        if 'is_active' in kwargs:
            user.is_active = kwargs['is_active']
        
        self.save_users()
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """حذف مستخدم"""
        if user_id in self.users:
            del self.users[user_id]
            self.save_users()
            return True
        return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """الحصول على مستخدم بالمعرف"""
        return self.users.get(user_id)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """الحصول على مستخدم بالمعرف (اسم بديل)"""
        return self.get_user(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """الحصول على مستخدم باسم المستخدم"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_user_by_employee_id(self, employee_id: str) -> Optional[User]:
        """الحصول على مستخدم بالرقم الوظيفي"""
        for user in self.users.values():
            if user.employee_id == employee_id:
                return user
        return None

    def get_user_by_faculty_id(self, faculty_id: str) -> Optional[User]:
        """الحصول على مستخدم بمعرف عضو هيئة التدريس"""
        for user in self.users.values():
            if user.faculty_id == faculty_id:
                return user
        return None
    
    def get_all_users(self) -> List[User]:
        """الحصول على جميع المستخدمين"""
        return list(self.users.values())
    
    # ═══════════════════════════════════════════════════════════════
    # المصادقة والتخويل
    # ═══════════════════════════════════════════════════════════════
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """المصادقة على المستخدم"""
        user = self.get_user_by_username(username)
        
        if user and user.is_active and user.verify_password(password):
            user.update_last_login()
            self.current_user = user
            self.save_users()
            return user
        
        return None
    
    def logout(self):
        """تسجيل الخروج"""
        # استخدام end_session بدلاً من تعيين current_user مباشرة
        self.end_session()
    
    def is_authenticated(self) -> bool:
        """التحقق من تسجيل الدخول"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[User]:
        """الحصول على المستخدم الحالي"""
        return self.current_user
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة الأدوار والصلاحيات
    # ═══════════════════════════════════════════════════════════════
    
    def assign_role(self, user_id: str, role: str) -> bool:
        """تعيين دور للمستخدم"""
        if role not in ROLES:
            return False
        
        user = self.get_user(user_id)
        if user:
            result = user.add_role(role)
            if result:
                self.save_users()
            return result
        
        return False
    
    def remove_role(self, user_id: str, role: str) -> bool:
        """إزالة دور من المستخدم"""
        user = self.get_user(user_id)
        if user:
            result = user.remove_role(role)
            if result:
                self.save_users()
            return result
        
        return False
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """التحقق من صلاحية المستخدم"""
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return False
        
        # المدير لديه جميع الصلاحيات
        if 'admin' in user.roles:
            return True
        
        # التحقق من الصلاحيات حسب الدور
        for role in user.roles:
            if role in ROLES:
                role_permissions = ROLES[role].get('permissions', [])
                if '*' in role_permissions or permission in role_permissions:
                    return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """الحصول على قائمة صلاحيات المستخدم"""
        permissions = set()
        user = self.get_user(user_id)
        
        if not user:
            return []
        
        # المدير لديه جميع الصلاحيات
        if 'admin' in user.roles:
            return ['*']
        
        # جمع الصلاحيات من جميع الأدوار
        for role in user.roles:
            if role in ROLES:
                permissions.update(ROLES[role].get('permissions', []))
        
        return list(permissions)
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة تعيينات الشعب
    # ═══════════════════════════════════════════════════════════════
    
    def assign_section(self, user_id: str, course_id: str, section_id: str) -> bool:
        """تعيين شعبة لأستاذ"""
        key = f"{course_id}_{section_id}"
        self.section_assignments[key] = user_id
        return True
    
    def unassign_section(self, course_id: str, section_id: str) -> bool:
        """إلغاء تعيين شعبة"""
        key = f"{course_id}_{section_id}"
        if key in self.section_assignments:
            del self.section_assignments[key]
            return True
        return False
    
    def can_edit_section(self, user_id: str, course_id: str, section_id: str) -> bool:
        """التحقق من صلاحية تعديل الشعبة"""
        # المنسق أو المدير يمكنهم عرض/تعديل جميع الشعب
        if self.has_permission(user_id, 'view_all_sections'):
            return True
        
        # الأستاذ المسؤول عن الشعبة
        key = f"{course_id}_{section_id}"
        return self.section_assignments.get(key) == user_id
    
    def get_accessible_sections(self, user_id: str, course_id: str) -> List[str]:
        """الحصول على الشعب التي يمكن للمستخدم الوصول إليها"""
        # إذا كان منسق أو مدير، يمكنه الوصول لجميع الشعب
        if self.has_permission(user_id, 'view_all_sections'):
            return ['*']  # جميع الشعب
        
        # البحث عن الشعب المعينة للأستاذ
        accessible = []
        for key, assigned_user in self.section_assignments.items():
            if assigned_user == user_id and key.startswith(f"{course_id}_"):
                section_id = key.split('_', 1)[1]
                accessible.append(section_id)
        
        return accessible
    
    def get_user_sections(self, user_id: str) -> Dict[str, List[str]]:
        """الحصول على جميع الشعب المعينة للمستخدم"""
        user_sections = {}
        for key, assigned_user in self.section_assignments.items():
            if assigned_user == user_id:
                course_id, section_id = key.split('_', 1)
                if course_id not in user_sections:
                    user_sections[course_id] = []
                user_sections[course_id].append(section_id)
        
        return user_sections
    
    # ═══════════════════════════════════════════════════════════════
    # دوال مساعدة
    # ═══════════════════════════════════════════════════════════════
    
    def get_users_by_role(self, role: str) -> List[User]:
        """الحصول على جميع المستخدمين بدور معين"""
        return [user for user in self.users.values() if user.has_role(role)]
    
    def search_users(self, query: str) -> List[User]:
        """البحث عن مستخدمين"""
        query = query.lower()
        results = []

        for user in self.users.values():
            if (query in user.username.lower() or
                query in user.full_name.lower() or
                query in user.email.lower()):
                results.append(user)

        return results

    # ═══════════════════════════════════════════════════════════════
    # إدارة الجلسات
    # ═══════════════════════════════════════════════════════════════

    def start_session(self, user: User):
        """
        بدء جلسة جديدة للمستخدم

        Args:
            user: المستخدم الذي سيبدأ الجلسة
        """
        self.current_user = user
        self.session_start_time = datetime.now()
        self.last_activity_time = datetime.now()

        # تسجيل في سجل التدقيق
        try:
            from utils.audit_logger import log_login
            log_login(user.username, user.user_id, success=True)
        except:
            pass

    def end_session(self):
        """إنهاء الجلسة الحالية"""
        if self.current_user:
            # تسجيل في سجل التدقيق
            try:
                from utils.audit_logger import log_logout
                log_logout(self.current_user.username, self.current_user.user_id)
            except:
                pass

        self.current_user = None
        self.session_start_time = None
        self.last_activity_time = None

    def update_activity(self):
        """تحديث وقت آخر نشاط"""
        self.last_activity_time = datetime.now()

    def is_session_expired(self) -> bool:
        """
        التحقق من انتهاء صلاحية الجلسة

        Returns:
            True إذا انتهت صلاحية الجلسة، False إذا لا تزال صالحة
        """
        if not self.current_user or not self.last_activity_time:
            return True

        time_since_activity = datetime.now() - self.last_activity_time
        return time_since_activity.total_seconds() / 60 > self.session_timeout_minutes

    def get_session_info(self) -> Optional[Dict[str, any]]:
        """
        الحصول على معلومات الجلسة الحالية

        Returns:
            قاموس بمعلومات الجلسة أو None
        """
        if not self.current_user:
            return None

        time_remaining = timedelta(minutes=self.session_timeout_minutes)
        if self.last_activity_time:
            time_since_activity = datetime.now() - self.last_activity_time
            time_remaining -= time_since_activity

        return {
            'user_id': self.current_user.user_id,
            'username': self.current_user.username,
            'full_name': self.current_user.full_name,
            'session_start': self.session_start_time.isoformat() if self.session_start_time else None,
            'last_activity': self.last_activity_time.isoformat() if self.last_activity_time else None,
            'time_remaining_minutes': max(0, int(time_remaining.total_seconds() / 60)),
            'is_expired': self.is_session_expired()
        }

    def check_session_and_refresh(self) -> bool:
        """
        التحقق من صلاحية الجلسة وتحديثها

        Returns:
            True إذا كانت الجلسة صالحة، False إذا انتهت
        """
        if self.is_session_expired():
            self.end_session()
            return False

        self.update_activity()
        return True

    def get_session_duration(self) -> Optional[timedelta]:
        """
        الحصول على مدة الجلسة الحالية

        Returns:
            المدة منذ بداية الجلسة أو None
        """
        if not self.session_start_time:
            return None

        return datetime.now() - self.session_start_time

    # ═══════════════════════════════════════════════════════════════
    # إدارة صلاحيات البرامج والمقررات
    # ═══════════════════════════════════════════════════════════════

    def can_access_program(self, user_id: str, program_id: str, program_coordinator_id: str = None) -> bool:
        """
        التحقق من صلاحية الوصول إلى برنامج أكاديمي

        Args:
            user_id: معرف المستخدم
            program_id: معرف البرنامج
            program_coordinator_id: معرف منسق البرنامج (faculty_id)

        Returns:
            True إذا كان لديه صلاحية الوصول
        """
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return False

        # المدير لديه وصول لجميع البرامج
        if 'admin' in user.roles:
            return True

        # منسق البرنامج لديه وصول للبرنامج الذي يشرف عليه
        if 'program_coordinator' in user.roles and program_coordinator_id:
            # التحقق من أن المستخدم هو منسق هذا البرنامج
            if user.faculty_id == program_coordinator_id:
                return True

        return False

    def get_accessible_programs(self, user_id: str, all_programs: list) -> list:
        """
        الحصول على البرامج التي يمكن للمستخدم الوصول إليها

        Args:
            user_id: معرف المستخدم
            all_programs: قائمة جميع البرامج

        Returns:
            قائمة البرامج المتاحة للمستخدم
        """
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return []

        # المدير لديه وصول لجميع البرامج
        if 'admin' in user.roles:
            return all_programs

        # منسق البرنامج يرى البرامج التي يشرف عليها فقط
        if 'program_coordinator' in user.roles:
            accessible = []
            for program in all_programs:
                if hasattr(program, 'coordinator_id') and program.coordinator_id == user.faculty_id:
                    accessible.append(program)
            return accessible

        return []

    def can_access_course(self, user_id: str, course, program_id: str = None) -> bool:
        """
        التحقق من صلاحية الوصول إلى مقرر

        Args:
            user_id: معرف المستخدم
            course: المقرر
            program_id: معرف البرنامج (اختياري)

        Returns:
            True إذا كان لديه صلاحية الوصول
        """
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return False

        # المدير لديه وصول لجميع المقررات
        if 'admin' in user.roles:
            return True

        # منسق البرنامج لديه وصول لجميع مقررات البرنامج
        if 'program_coordinator' in user.roles and program_id:
            # يجب التحقق من أن المستخدم منسق لهذا البرنامج
            # سيتم استخدام دالة can_access_program للتحقق
            pass

        # منسق المقرر لديه وصول للمقرر الذي يشرف عليه
        if 'course_coordinator' in user.roles:
            if hasattr(course, 'coordinator_id') and course.coordinator_id == user.faculty_id:
                return True

        # مدرس الشعبة لديه وصول للمقرر الذي يدرس فيه
        if 'instructor' in user.roles:
            # سيتم فحص الشعب المعينة له
            pass

        return False

    def get_accessible_courses(self, user_id: str, all_courses: list, program_id: str = None) -> list:
        """
        الحصول على المقررات التي يمكن للمستخدم الوصول إليها

        Args:
            user_id: معرف المستخدم
            all_courses: قائمة جميع المقررات
            program_id: معرف البرنامج (اختياري للتصفية)

        Returns:
            قائمة المقررات المتاحة للمستخدم
        """
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return []

        # المدير لديه وصول لجميع المقررات
        if 'admin' in user.roles:
            return all_courses

        accessible = []

        # منسق البرنامج يرى جميع مقررات البرنامج
        if 'program_coordinator' in user.roles and program_id:
            # جميع مقررات البرنامج
            for course in all_courses:
                if hasattr(course, 'program') and course.program == program_id:
                    accessible.append(course)
            return accessible

        # منسق المقرر يرى المقررات التي يشرف عليها
        if 'course_coordinator' in user.roles:
            for course in all_courses:
                if hasattr(course, 'coordinator_id') and course.coordinator_id == user.faculty_id:
                    accessible.append(course)

        # مدرس الشعبة يرى المقررات التي يدرس فيها
        if 'instructor' in user.roles:
            # سيتم فحص الشعب المعينة له
            pass

        return accessible

    def generate_users_credentials_report(self, include_passwords: bool = False) -> str:
        """
        توليد تقرير بأسماء المستخدمين وبياناتهم

        Args:
            include_passwords: هل يتم تضمين كلمات المرور (افتراضياً False)

        Returns:
            نص التقرير
        """
        from models.user import User

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("تقرير أسماء المستخدمين وبياناتهم")
        report_lines.append("User Accounts and Credentials Report")
        report_lines.append("=" * 80)
        report_lines.append("")

        # ترتيب المستخدمين حسب الدور
        users_by_role = {
            'admin': [],
            'program_coordinator': [],
            'course_coordinator': [],
            'instructor': [],
            'other': []
        }

        for user in self.users.values():
            if 'admin' in user.roles:
                users_by_role['admin'].append(user)
            elif 'program_coordinator' in user.roles:
                users_by_role['program_coordinator'].append(user)
            elif 'course_coordinator' in user.roles:
                users_by_role['course_coordinator'].append(user)
            elif 'instructor' in user.roles:
                users_by_role['instructor'].append(user)
            else:
                users_by_role['other'].append(user)

        # طباعة المستخدمين حسب الدور
        role_names = {
            'admin': 'مديرو النظام / System Administrators',
            'program_coordinator': 'منسقو البرامج / Program Coordinators',
            'course_coordinator': 'منسقو المقررات / Course Coordinators',
            'instructor': 'مدرسو الشعب / Instructors',
            'other': 'مستخدمون آخرون / Other Users'
        }

        for role_key, role_name in role_names.items():
            users = users_by_role[role_key]
            if not users:
                continue

            report_lines.append("")
            report_lines.append("-" * 80)
            report_lines.append(f"📋 {role_name}")
            report_lines.append("-" * 80)
            report_lines.append("")

            for user in sorted(users, key=lambda u: u.username):
                report_lines.append(f"👤 الاسم الكامل / Full Name: {user.full_name}")
                report_lines.append(f"   اسم المستخدم / Username: {user.username}")

                # كلمة المرور - فقط للمستخدمين الجدد الذين لديهم employee_id
                if include_passwords and user.employee_id:
                    password = User.generate_password(user.employee_id)
                    report_lines.append(f"   كلمة المرور / Password: {password}")

                if user.employee_id:
                    report_lines.append(f"   الرقم الوظيفي / Employee ID: {user.employee_id}")

                report_lines.append(f"   البريد / Email: {user.email}")
                report_lines.append(f"   الحالة / Status: {'نشط / Active' if user.is_active else 'معطل / Disabled'}")
                report_lines.append("")

        report_lines.append("=" * 80)
        report_lines.append(f"إجمالي المستخدمين / Total Users: {len(self.users)}")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def export_users_credentials_to_file(self, filename: str, include_passwords: bool = False) -> bool:
        """
        تصدير تقرير المستخدمين إلى ملف

        Args:
            filename: اسم الملف
            include_passwords: هل يتم تضمين كلمات المرور

        Returns:
            True إذا نجح التصدير
        """
        try:
            report = self.generate_users_credentials_report(include_passwords)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            return True
        except Exception as e:
            print(f"Error exporting users report: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════
    # إدارة تعيينات البرامج والمقررات والشعب
    # ═══════════════════════════════════════════════════════════════

    def assign_user_to_program(self, user_id: str, program_id: str) -> bool:
        """
        تعيين مستخدم لبرنامج أكاديمي (منسق برنامج)

        Args:
            user_id: معرف المستخدم
            program_id: معرف البرنامج الأكاديمي

        Returns:
            True إذا نجح التعيين، False خلاف ذلك
        """
        user = self.get_user(user_id)
        if user:
            result = user.assign_program(program_id)
            if result:
                self.save_users()
            return result
        return False

    def unassign_user_from_program(self, user_id: str, program_id: str) -> bool:
        """
        إلغاء تعيين مستخدم من برنامج أكاديمي

        Args:
            user_id: معرف المستخدم
            program_id: معرف البرنامج الأكاديمي

        Returns:
            True إذا نجح الإلغاء، False خلاف ذلك
        """
        user = self.get_user(user_id)
        if user:
            result = user.unassign_program(program_id)
            if result:
                self.save_users()
            return result
        return False

    def get_users_by_program(self, program_id: str) -> List[User]:
        """
        الحصول على جميع المستخدمين المعينين لبرنامج أكاديمي معين

        Args:
            program_id: معرف البرنامج الأكاديمي

        Returns:
            قائمة المستخدمين المعينين للبرنامج
        """
        users = []
        for user in self.users.values():
            if user.has_access_to_program(program_id):
                users.append(user)
        return users

    def get_program_coordinator_by_program(self, program_id: str) -> Optional[User]:
        """
        الحصول على منسق البرنامج الأكاديمي

        Args:
            program_id: معرف البرنامج الأكاديمي

        Returns:
            المستخدم المعين كمنسق للبرنامج أو None
        """
        for user in self.users.values():
            if 'program_coordinator' in user.roles:
                if program_id in user.assigned_programs:
                    return user
        return None

    def assign_user_to_course(self, user_id: str, course_id: str) -> bool:
        """
        تعيين مستخدم لمقرر (منسق مقرر)

        Args:
            user_id: معرف المستخدم
            course_id: معرف المقرر

        Returns:
            True إذا نجح التعيين، False خلاف ذلك
        """
        user = self.get_user(user_id)
        if user:
            result = user.assign_course(course_id)
            if result:
                self.save_users()
            return result
        return False

    def unassign_user_from_course(self, user_id: str, course_id: str) -> bool:
        """
        إلغاء تعيين مستخدم من مقرر

        Args:
            user_id: معرف المستخدم
            course_id: معرف المقرر

        Returns:
            True إذا نجح الإلغاء، False خلاف ذلك
        """
        user = self.get_user(user_id)
        if user:
            result = user.unassign_course(course_id)
            if result:
                self.save_users()
            return result
        return False

    def assign_user_to_section(self, user_id: str, course_id: str, section_name: str) -> bool:
        """
        تعيين مستخدم لشعبة (مدرس شعبة)

        Args:
            user_id: معرف المستخدم
            course_id: معرف المقرر
            section_name: اسم الشعبة

        Returns:
            True إذا نجح التعيين، False خلاف ذلك
        """
        user = self.get_user(user_id)
        if user:
            result = user.assign_section(course_id, section_name)
            if result:
                self.save_users()
            return result
        return False

    def unassign_user_from_section(self, user_id: str, course_id: str, section_name: str) -> bool:
        """
        إلغاء تعيين مستخدم من شعبة

        Args:
            user_id: معرف المستخدم
            course_id: معرف المقرر
            section_name: اسم الشعبة

        Returns:
            True إذا نجح الإلغاء، False خلاف ذلك
        """
        user = self.get_user(user_id)
        if user:
            result = user.unassign_section(course_id, section_name)
            if result:
                self.save_users()
            return result
        return False

    def get_users_by_course(self, course_id: str) -> List[User]:
        """
        الحصول على جميع المستخدمين المعينين لمقرر معين

        Args:
            course_id: معرف المقرر

        Returns:
            قائمة المستخدمين المعينين للمقرر
        """
        users = []
        for user in self.users.values():
            if user.has_access_to_course(course_id):
                users.append(user)
        return users

    def get_users_by_section(self, course_id: str, section_name: str) -> List[User]:
        """
        الحصول على جميع المستخدمين المعينين لشعبة معينة

        Args:
            course_id: معرف المقرر
            section_name: اسم الشعبة

        Returns:
            قائمة المستخدمين المعينين للشعبة
        """
        users = []
        for user in self.users.values():
            if user.has_access_to_section(course_id, section_name):
                users.append(user)
        return users

    def get_course_coordinator_by_course(self, course_id: str) -> Optional[User]:
        """
        الحصول على منسق المقرر

        Args:
            course_id: معرف المقرر

        Returns:
            المستخدم المعين كمنسق للمقرر أو None
        """
        for user in self.users.values():
            if 'course_coordinator' in user.roles:
                if course_id in user.assigned_courses:
                    return user
        return None

    def get_section_instructors_by_section(self, course_id: str, section_name: str) -> List[User]:
        """
        الحصول على مدرسي شعبة معينة

        Args:
            course_id: معرف المقرر
            section_name: اسم الشعبة

        Returns:
            قائمة المستخدمين المعينين كمدرسين للشعبة
        """
        instructors = []
        for user in self.users.values():
            if 'section_instructor' in user.roles:
                if course_id in user.assigned_sections:
                    if section_name in user.assigned_sections[course_id]:
                        instructors.append(user)
        return instructors

    def user_can_manage_course_for_program(self, user_id: str, program_id: str) -> bool:
        """
        التحقق من إمكانية إدارة مقررات برنامج أكاديمي معين

        Args:
            user_id: معرف المستخدم
            program_id: معرف البرنامج الأكاديمي

        Returns:
            True إذا كان المستخدم يستطيع إدارة مقررات البرنامج
        """
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return False

        # المدير يستطيع إدارة مقررات جميع البرامج
        if user.has_role('admin'):
            return True

        # منسق البرنامج يستطيع إدارة مقررات برنامجه فقط
        if user.has_role('program_coordinator'):
            return user.has_access_to_program(program_id)

        return False

    def get_program_names_for_user(self, user: User) -> List[str]:
        """
        الحصول على أسماء البرامج الأكاديمية للمستخدم (عربي وإنجليزي)

        Args:
            user: المستخدم

        Returns:
            قائمة بأسماء البرامج (عربي وإنجليزي)
        """
        if not user or user.has_role('admin'):
            return []  # المدير يرى كل شيء

        if not user.has_role('program_coordinator'):
            return []  # ليس منسق برنامج

        program_names = []

        # قراءة ملف البرامج
        programs_file = os.path.join('data', 'academic_programs', 'programs.json')
        if os.path.exists(programs_file):
            try:
                with open(programs_file, 'r', encoding='utf-8') as f:
                    programs_data = json.load(f)

                for program_id in user.assigned_programs:
                    if program_id in programs_data:
                        program = programs_data[program_id]
                        # إضافة الاسم العربي والإنجليزي
                        if 'program_name_ar' in program:
                            program_names.append(program['program_name_ar'])
                        if 'program_name_en' in program:
                            program_names.append(program['program_name_en'])
            except Exception as e:
                print(f"Error loading programs: {e}")

        return program_names

    def get_allowed_course_ids_for_user(self, user: User) -> List[str]:
        """
        الحصول على معرفات المقررات المسموحة للمستخدم

        Args:
            user: المستخدم

        Returns:
            قائمة بمعرفات المقررات المسموحة (فارغة للمدير = يرى كل شيء)
        """
        if not user or user.has_role('admin'):
            return []  # المدير يرى كل شيء - قائمة فارغة تعني لا توجد قيود

        # منسق مقرر - المقررات المسندة له فقط
        if user.has_role('course_coordinator'):
            return user.assigned_courses.copy()

        # منسق برنامج - سيتم التصفية حسب اسم البرنامج في الكود المستدعي
        # لذلك نرجع قائمة فارغة (لا توجد قيود على مستوى معرفات المقررات)
        if user.has_role('program_coordinator'):
            return []

        # مدرس شعبة - المقررات التي لديه شعب فيها
        if user.has_role('section_instructor'):
            return list(user.assigned_sections.keys())

        return []

    def __str__(self):
        return f"AccessControl(users={len(self.users)}, current_user={self.current_user})"
