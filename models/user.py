"""
نموذج المستخدم
User Model
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional


class User:
    """فئة المستخدم"""
    
    def __init__(self, user_id: str, username: str, password_hash: str = None,
                 full_name: str = "", email: str = "", roles: List[str] = None,
                 employee_id: str = "", faculty_id: str = ""):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.email = email
        self.roles = roles or []
        self.employee_id = employee_id  # الرقم الوظيفي
        self.faculty_id = faculty_id  # معرف عضو هيئة التدريس
        self.created_date = datetime.now().isoformat()
        self.last_login = None
        self.is_active = True

        # ربط المستخدم بالبرامج والمقررات والشعب
        self.assigned_programs: List[str] = []  # قائمة معرفات البرامج الأكاديمية (لمنسق البرنامج)
        self.assigned_courses: List[str] = []  # قائمة معرفات المقررات المعين عليها (لمنسق المقرر)
        self.assigned_sections: Dict[str, List[str]] = {}  # {course_id: [section_names]} للمدرسين

        self.metadata = {}
    
    @staticmethod
    def hash_password(password: str) -> str:
        """تشفير كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generate_username(name: str, employee_id: str) -> str:
        """
        توليد اسم المستخدم من الاسم والرقم الوظيفي

        القاعدة: الحرف الأول من الاسم (capital) + الرقم الوظيفي
        مثال: حسين يوسف + 12345 = H12345

        Args:
            name: الاسم الكامل
            employee_id: الرقم الوظيفي

        Returns:
            اسم المستخدم
        """
        if not name or not employee_id:
            return ""

        # الحصول على الحرف الأول من الاسم
        first_char = name.strip()[0].upper()

        # دمج الحرف الأول مع الرقم الوظيفي
        return f"{first_char}{employee_id.strip()}"

    @staticmethod
    def generate_password(employee_id: str) -> str:
        """
        توليد كلمة المرور من الرقم الوظيفي

        القاعدة: الرقم الوظيفي مبدوءاً بصفر
        مثال: 12345 -> 012345

        Args:
            employee_id: الرقم الوظيفي

        Returns:
            كلمة المرور
        """
        if not employee_id:
            return ""

        return f"0{employee_id.strip()}"
    
    def verify_password(self, password: str) -> bool:
        """التحقق من كلمة المرور"""
        return self.password_hash == self.hash_password(password)
    
    def add_role(self, role: str) -> bool:
        """إضافة دور"""
        if role not in self.roles:
            self.roles.append(role)
            return True
        return False
    
    def remove_role(self, role: str) -> bool:
        """إزالة دور"""
        if role in self.roles:
            self.roles.remove(role)
            return True
        return False
    
    def has_role(self, role: str) -> bool:
        """التحقق من وجود دور"""
        return role in self.roles

    def assign_program(self, program_id: str) -> bool:
        """تعيين برنامج أكاديمي للمستخدم (منسق برنامج)"""
        if program_id not in self.assigned_programs:
            self.assigned_programs.append(program_id)
            return True
        return False

    def unassign_program(self, program_id: str) -> bool:
        """إلغاء تعيين برنامج أكاديمي"""
        if program_id in self.assigned_programs:
            self.assigned_programs.remove(program_id)
            return True
        return False

    def get_assigned_programs(self) -> List[str]:
        """الحصول على البرامج الأكاديمية المعينة للمستخدم"""
        return self.assigned_programs.copy()

    def has_access_to_program(self, program_id: str) -> bool:
        """التحقق من وصول المستخدم للبرنامج الأكاديمي"""
        if 'admin' in self.roles:
            return True
        if 'program_coordinator' in self.roles and program_id in self.assigned_programs:
            return True
        return False

    def assign_course(self, course_id: str) -> bool:
        """تعيين مقرر للمستخدم (منسق مقرر)"""
        if course_id not in self.assigned_courses:
            self.assigned_courses.append(course_id)
            return True
        return False

    def unassign_course(self, course_id: str) -> bool:
        """إلغاء تعيين مقرر"""
        if course_id in self.assigned_courses:
            self.assigned_courses.remove(course_id)
            # إزالة جميع الشعب المرتبطة بهذا المقرر
            if course_id in self.assigned_sections:
                del self.assigned_sections[course_id]
            return True
        return False

    def assign_section(self, course_id: str, section_name: str) -> bool:
        """تعيين شعبة للمستخدم (مدرس شعبة)"""
        if course_id not in self.assigned_sections:
            self.assigned_sections[course_id] = []

        if section_name not in self.assigned_sections[course_id]:
            self.assigned_sections[course_id].append(section_name)
            return True
        return False

    def unassign_section(self, course_id: str, section_name: str) -> bool:
        """إلغاء تعيين شعبة"""
        if course_id in self.assigned_sections:
            if section_name in self.assigned_sections[course_id]:
                self.assigned_sections[course_id].remove(section_name)
                # إزالة المقرر من القاموس إذا لم يتبق له شعب
                if not self.assigned_sections[course_id]:
                    del self.assigned_sections[course_id]
                return True
        return False

    def get_assigned_courses(self) -> List[str]:
        """الحصول على المقررات المعينة للمستخدم"""
        return self.assigned_courses.copy()

    def get_assigned_sections(self, course_id: str = None) -> Dict[str, List[str]]:
        """الحصول على الشعب المعينة للمستخدم

        Args:
            course_id: معرف المقرر (اختياري). إذا تم تحديده، يُرجع شعب هذا المقرر فقط

        Returns:
            قاموس {course_id: [section_names]} أو قائمة الشعب لمقرر محدد
        """
        if course_id:
            return self.assigned_sections.get(course_id, [])
        return self.assigned_sections.copy()

    def has_access_to_course(self, course_id: str) -> bool:
        """التحقق من وصول المستخدم للمقرر"""
        if 'admin' in self.roles:
            return True
        if 'course_coordinator' in self.roles and course_id in self.assigned_courses:
            return True
        if 'section_instructor' in self.roles and course_id in self.assigned_sections:
            return True
        return False

    def can_manage_course_in_program(self, program_name: str) -> bool:
        """
        التحقق من إمكانية إدارة (إنشاء/تعديل) مقررات في برنامج أكاديمي معين

        Args:
            program_name: اسم البرنامج الأكاديمي (عربي أو انجليزي)

        Returns:
            True إذا كان المستخدم يستطيع إدارة مقررات البرنامج
        """
        if 'admin' in self.roles:
            return True

        if 'program_coordinator' in self.roles:
            # منسق البرنامج يستطيع إدارة مقررات برامجه فقط
            # نحتاج للتحقق من أن البرنامج موجود في assigned_programs
            # سيتم تمرير program_id للمقارنة من الخارج
            return True  # سيتم التحقق الدقيق في الكود المستدعي

        return False

    def has_access_to_section(self, course_id: str, section_name: str) -> bool:
        """التحقق من وصول المستخدم للشعبة"""
        if 'admin' in self.roles:
            return True
        if 'course_coordinator' in self.roles and course_id in self.assigned_courses:
            return True
        if 'section_instructor' in self.roles:
            if course_id in self.assigned_sections:
                if section_name in self.assigned_sections[course_id]:
                    return True
        return False

    def update_last_login(self):
        """تحديث آخر تسجيل دخول"""
        self.last_login = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password_hash': self.password_hash,
            'full_name': self.full_name,
            'email': self.email,
            'roles': self.roles,
            'employee_id': self.employee_id,
            'faculty_id': self.faculty_id,
            'assigned_programs': self.assigned_programs,
            'assigned_courses': self.assigned_courses,
            'assigned_sections': self.assigned_sections,
            'created_date': self.created_date,
            'last_login': self.last_login,
            'is_active': self.is_active,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """إنشاء من قاموس"""
        user = cls(
            user_id=data.get('user_id'),
            username=data.get('username'),
            password_hash=data.get('password_hash'),
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            roles=data.get('roles', []),
            employee_id=data.get('employee_id', ''),
            faculty_id=data.get('faculty_id', '')
        )
        user.assigned_programs = data.get('assigned_programs', [])
        user.assigned_courses = data.get('assigned_courses', [])
        user.assigned_sections = data.get('assigned_sections', {})
        user.created_date = data.get('created_date', user.created_date)
        user.last_login = data.get('last_login')
        user.is_active = data.get('is_active', True)
        user.metadata = data.get('metadata', {})
        return user
    
    def __str__(self):
        return f"User({self.username}, roles={self.roles})"
    
    def __repr__(self):
        return self.__str__()
