"""
نموذج قاعدة البيانات - للتعامل مع ملفات JSON
Database Model - JSON File Handler
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum

# تعريف UserRole enum
class UserRole(Enum):
    ADMIN = "admin"
    PROGRAM_COORDINATOR = "program_coordinator"
    COURSE_COORDINATOR = "course_coordinator"
    SECTION_INSTRUCTOR = "section_instructor"


class User:
    """فئة المستخدم المبسطة"""

    def __init__(self, user_id: str, username: str, password_hash: str,
                 full_name: str, email: str, roles: List[str],
                 employee_id: str = "", faculty_id: str = ""):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.email = email
        self.roles = roles
        self.employee_id = employee_id
        self.faculty_id = faculty_id

        # تحديد الدور الرئيسي
        if "admin" in roles:
            self.role = UserRole.ADMIN
        elif "program_coordinator" in roles:
            self.role = UserRole.PROGRAM_COORDINATOR
        elif "course_coordinator" in roles:
            self.role = UserRole.COURSE_COORDINATOR
        else:
            self.role = UserRole.SECTION_INSTRUCTOR

    @property
    def department(self) -> Optional[str]:
        """القسم - يمكن إضافته لاحقاً"""
        return None


class Database:
    """فئة قاعدة البيانات - للتعامل مع ملفات JSON"""

    def __init__(self, db_path: str = None):
        """
        تهيئة قاعدة البيانات

        Args:
            db_path: مسار قاعدة البيانات (غير مستخدم، للتوافق فقط)
        """
        # تحديد مسار مجلد data
        self.base_path = Path(__file__).parent.parent / "data"
        self.users_file = self.base_path / "users.json"

        # إنشاء المجلد إذا لم يكن موجوداً
        self.base_path.mkdir(parents=True, exist_ok=True)

        # إنشاء ملف المستخدمين إذا لم يكن موجوداً
        if not self.users_file.exists():
            self._create_default_users()

    def _create_default_users(self):
        """إنشاء مستخدمين افتراضيين"""
        import hashlib

        def hash_password(password: str) -> str:
            return hashlib.sha256(password.encode()).hexdigest()

        default_users = {
            "users": [
                {
                    "user_id": "admin_001",
                    "username": "admin",
                    "password_hash": hash_password("admin123"),
                    "full_name": "System Administrator",
                    "email": "admin@example.com",
                    "roles": ["admin"],
                    "employee_id": "",
                    "faculty_id": "",
                    "assigned_programs": [],
                    "assigned_courses": [],
                    "assigned_sections": {},
                    "created_date": "2026-01-11",
                    "last_login": None,
                    "is_active": True,
                    "metadata": {}
                },
                {
                    "user_id": "coord_001",
                    "username": "coordinator",
                    "password_hash": hash_password("coord123"),
                    "full_name": "Program Coordinator",
                    "email": "coordinator@example.com",
                    "roles": ["program_coordinator"],
                    "employee_id": "PC001",
                    "faculty_id": "",
                    "assigned_programs": [],
                    "assigned_courses": [],
                    "assigned_sections": {},
                    "created_date": "2026-01-11",
                    "last_login": None,
                    "is_active": True,
                    "metadata": {}
                },
                {
                    "user_id": "course_001",
                    "username": "course_coord",
                    "password_hash": hash_password("course123"),
                    "full_name": "Course Coordinator",
                    "email": "course@example.com",
                    "roles": ["course_coordinator"],
                    "employee_id": "CC001",
                    "faculty_id": "",
                    "assigned_programs": [],
                    "assigned_courses": [],
                    "assigned_sections": {},
                    "created_date": "2026-01-11",
                    "last_login": None,
                    "is_active": True,
                    "metadata": {}
                },
                {
                    "user_id": "inst_001",
                    "username": "instructor",
                    "password_hash": hash_password("instr123"),
                    "full_name": "Section Instructor",
                    "email": "instructor@example.com",
                    "roles": ["section_instructor"],
                    "employee_id": "SI001",
                    "faculty_id": "",
                    "assigned_programs": [],
                    "assigned_courses": [],
                    "assigned_sections": {},
                    "created_date": "2026-01-11",
                    "last_login": None,
                    "is_active": True,
                    "metadata": {}
                }
            ]
        }

        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=2)

    def load_users(self) -> List[Dict]:
        """تحميل جميع المستخدمين من الملف"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('users', [])
        except FileNotFoundError:
            self._create_default_users()
            return self.load_users()
        except json.JSONDecodeError:
            return []

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        التحقق من بيانات المستخدم

        Args:
            username: اسم المستخدم
            password: كلمة المرور

        Returns:
            كائن المستخدم إذا نجح التحقق، None إذا فشل
        """
        import hashlib

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        users = self.load_users()
        for user_data in users:
            if (user_data.get('username') == username and
                user_data.get('password_hash') == password_hash and
                user_data.get('is_active', True)):

                # إنشاء كائن User
                user = User(
                    user_id=user_data.get('user_id', ''),
                    username=user_data.get('username', ''),
                    password_hash=user_data.get('password_hash', ''),
                    full_name=user_data.get('full_name', ''),
                    email=user_data.get('email', ''),
                    roles=user_data.get('roles', []),
                    employee_id=user_data.get('employee_id', ''),
                    faculty_id=user_data.get('faculty_id', '')
                )

                return user

        return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        الحصول على مستخدم من خلال اسم المستخدم

        Args:
            username: اسم المستخدم

        Returns:
            كائن المستخدم أو None
        """
        users = self.load_users()
        for user_data in users:
            if user_data.get('username') == username:
                user = User(
                    user_id=user_data.get('user_id', ''),
                    username=user_data.get('username', ''),
                    password_hash=user_data.get('password_hash', ''),
                    full_name=user_data.get('full_name', ''),
                    email=user_data.get('email', ''),
                    roles=user_data.get('roles', []),
                    employee_id=user_data.get('employee_id', ''),
                    faculty_id=user_data.get('faculty_id', '')
                )
                return user

        return None

    def get_all_users(self) -> List[User]:
        """الحصول على جميع المستخدمين"""
        users = self.load_users()
        user_objects = []

        for user_data in users:
            user = User(
                user_id=user_data.get('user_id', ''),
                username=user_data.get('username', ''),
                password_hash=user_data.get('password_hash', ''),
                full_name=user_data.get('full_name', ''),
                email=user_data.get('email', ''),
                roles=user_data.get('roles', []),
                employee_id=user_data.get('employee_id', ''),
                faculty_id=user_data.get('faculty_id', '')
            )
            user_objects.append(user)

        return user_objects
