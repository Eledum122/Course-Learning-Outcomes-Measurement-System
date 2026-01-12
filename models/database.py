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

    def save_users(self, users_list: List[Dict]) -> bool:
        """
        حفظ قائمة المستخدمين إلى الملف

        Args:
            users_list: قائمة المستخدمين

        Returns:
            True إذا نجح الحفظ، False إذا فشل
        """
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({'users': users_list}, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False

    def add_user(self, username: str, password: str, full_name: str,
                 email: str, roles: List[str], employee_id: str = "") -> bool:
        """
        إضافة مستخدم جديد

        Args:
            username: اسم المستخدم
            password: كلمة المرور
            full_name: الاسم الكامل
            email: البريد الإلكتروني
            roles: قائمة الأدوار
            employee_id: الرقم الوظيفي

        Returns:
            True إذا نجحت الإضافة، False إذا فشلت
        """
        import hashlib
        from datetime import datetime

        # التحقق من عدم وجود اسم المستخدم
        if self.get_user_by_username(username):
            return False

        users = self.load_users()

        # إنشاء معرف فريد
        user_id = f"user_{len(users) + 1:03d}"

        # تشفير كلمة المرور
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # إنشاء المستخدم الجديد
        new_user = {
            "user_id": user_id,
            "username": username,
            "password_hash": password_hash,
            "full_name": full_name,
            "email": email,
            "roles": roles,
            "employee_id": employee_id,
            "faculty_id": "",
            "assigned_programs": [],
            "assigned_courses": [],
            "assigned_sections": {},
            "created_date": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True,
            "metadata": {}
        }

        users.append(new_user)
        return self.save_users(users)

    def update_user(self, user_id: str, full_name: str = None, email: str = None,
                    roles: List[str] = None, employee_id: str = None,
                    is_active: bool = None) -> bool:
        """
        تحديث بيانات مستخدم

        Args:
            user_id: معرف المستخدم
            full_name: الاسم الكامل (اختياري)
            email: البريد الإلكتروني (اختياري)
            roles: قائمة الأدوار (اختياري)
            employee_id: الرقم الوظيفي (اختياري)
            is_active: حالة التفعيل (اختياري)

        Returns:
            True إذا نجح التحديث، False إذا فشل
        """
        users = self.load_users()
        user_found = False

        for user in users:
            if user.get('user_id') == user_id:
                user_found = True
                if full_name is not None:
                    user['full_name'] = full_name
                if email is not None:
                    user['email'] = email
                if roles is not None:
                    user['roles'] = roles
                if employee_id is not None:
                    user['employee_id'] = employee_id
                if is_active is not None:
                    user['is_active'] = is_active
                break

        if user_found:
            return self.save_users(users)
        return False

    def delete_user(self, user_id: str) -> bool:
        """
        حذف مستخدم

        Args:
            user_id: معرف المستخدم

        Returns:
            True إذا نجح الحذف، False إذا فشل
        """
        users = self.load_users()
        original_count = len(users)

        # حذف المستخدم من القائمة
        users = [u for u in users if u.get('user_id') != user_id]

        if len(users) < original_count:
            return self.save_users(users)
        return False

    def change_password(self, user_id: str, new_password: str) -> bool:
        """
        تغيير كلمة مرور المستخدم

        Args:
            user_id: معرف المستخدم
            new_password: كلمة المرور الجديدة

        Returns:
            True إذا نجح التغيير، False إذا فشل
        """
        import hashlib

        users = self.load_users()
        user_found = False

        for user in users:
            if user.get('user_id') == user_id:
                user_found = True
                user['password_hash'] = hashlib.sha256(new_password.encode()).hexdigest()
                break

        if user_found:
            return self.save_users(users)
        return False

    # ═══════════════════════════════════════════════════════════════
    # إدارة البرامج الأكاديمية / Programs Management
    # ═══════════════════════════════════════════════════════════════

    def load_programs(self) -> List[Dict]:
        """تحميل جميع البرامج من الملف"""
        programs_file = self.base_path / "programs.json"
        try:
            with open(programs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('programs', [])
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_programs(self, programs_list: List[Dict]) -> bool:
        """
        حفظ قائمة البرامج إلى الملف

        Args:
            programs_list: قائمة البرامج

        Returns:
            True إذا نجح الحفظ، False إذا فشل
        """
        programs_file = self.base_path / "programs.json"
        try:
            with open(programs_file, 'w', encoding='utf-8') as f:
                json.dump({'programs': programs_list}, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving programs: {e}")
            return False

    def get_all_programs(self) -> List[Dict]:
        """الحصول على جميع البرامج"""
        return self.load_programs()

    def get_program_by_code(self, program_code: str) -> Optional[Dict]:
        """
        الحصول على برنامج من خلال الرمز

        Args:
            program_code: رمز البرنامج

        Returns:
            بيانات البرنامج أو None
        """
        programs = self.load_programs()
        for program in programs:
            if program.get('program_code') == program_code:
                return program
        return None

    def add_program(self, program_code: str, program_name_ar: str, program_name_en: str,
                   university_ar: str = "", university_en: str = "",
                   college_ar: str = "", college_en: str = "",
                   department_ar: str = "", department_en: str = "",
                   description_ar: str = "", description_en: str = "",
                   coordinator_id: str = "") -> bool:
        """
        إضافة برنامج جديد

        Args:
            program_code: رمز البرنامج
            program_name_ar: اسم البرنامج بالعربية
            program_name_en: اسم البرنامج بالإنجليزية
            university_ar: الجامعة بالعربية
            university_en: الجامعة بالإنجليزية
            college_ar: الكلية بالعربية
            college_en: الكلية بالإنجليزية
            department_ar: القسم بالعربية
            department_en: القسم بالإنجليزية
            description_ar: الوصف بالعربية
            description_en: الوصف بالإنجليزية
            coordinator_id: معرف منسق البرنامج

        Returns:
            True إذا نجحت الإضافة، False إذا فشلت
        """
        from datetime import datetime

        # التحقق من عدم وجود رمز البرنامج
        if self.get_program_by_code(program_code):
            return False

        programs = self.load_programs()

        # إنشاء معرف فريد
        program_id = f"prog_{len(programs) + 1:03d}"

        # إنشاء البرنامج الجديد
        new_program = {
            "program_id": program_id,
            "program_code": program_code,
            "program_name_ar": program_name_ar,
            "program_name_en": program_name_en,
            "university_ar": university_ar,
            "university_en": university_en,
            "college_ar": college_ar,
            "college_en": college_en,
            "department_ar": department_ar,
            "department_en": department_en,
            "description_ar": description_ar,
            "description_en": description_en,
            "coordinator_id": coordinator_id,
            "created_date": datetime.now().isoformat(),
            "is_active": True,
            "plos": [],
            "courses": [],
            "metadata": {}
        }

        programs.append(new_program)
        return self.save_programs(programs)

    def update_program(self, program_id: str, program_name_ar: str = None,
                      program_name_en: str = None, university_ar: str = None,
                      university_en: str = None, college_ar: str = None,
                      college_en: str = None, department_ar: str = None,
                      department_en: str = None, description_ar: str = None,
                      description_en: str = None, coordinator_id: str = None,
                      is_active: bool = None) -> bool:
        """
        تحديث بيانات برنامج

        Args:
            program_id: معرف البرنامج
            program_name_ar: اسم البرنامج بالعربية (اختياري)
            program_name_en: اسم البرنامج بالإنجليزية (اختياري)
            university_ar: الجامعة بالعربية (اختياري)
            university_en: الجامعة بالإنجليزية (اختياري)
            college_ar: الكلية بالعربية (اختياري)
            college_en: الكلية بالإنجليزية (اختياري)
            department_ar: القسم بالعربية (اختياري)
            department_en: القسم بالإنجليزية (اختياري)
            description_ar: الوصف بالعربية (اختياري)
            description_en: الوصف بالإنجليزية (اختياري)
            coordinator_id: معرف المنسق (اختياري)
            is_active: حالة التفعيل (اختياري)

        Returns:
            True إذا نجح التحديث، False إذا فشل
        """
        programs = self.load_programs()
        program_found = False

        for program in programs:
            if program.get('program_id') == program_id:
                program_found = True
                if program_name_ar is not None:
                    program['program_name_ar'] = program_name_ar
                if program_name_en is not None:
                    program['program_name_en'] = program_name_en
                if university_ar is not None:
                    program['university_ar'] = university_ar
                if university_en is not None:
                    program['university_en'] = university_en
                if college_ar is not None:
                    program['college_ar'] = college_ar
                if college_en is not None:
                    program['college_en'] = college_en
                if department_ar is not None:
                    program['department_ar'] = department_ar
                if department_en is not None:
                    program['department_en'] = department_en
                if description_ar is not None:
                    program['description_ar'] = description_ar
                if description_en is not None:
                    program['description_en'] = description_en
                if coordinator_id is not None:
                    program['coordinator_id'] = coordinator_id
                if is_active is not None:
                    program['is_active'] = is_active
                break

        if program_found:
            return self.save_programs(programs)
        return False

    def delete_program(self, program_id: str) -> bool:
        """
        حذف برنامج

        Args:
            program_id: معرف البرنامج

        Returns:
            True إذا نجح الحذف، False إذا فشل
        """
        programs = self.load_programs()
        original_count = len(programs)

        # حذف البرنامج من القائمة
        programs = [p for p in programs if p.get('program_id') != program_id]

        if len(programs) < original_count:
            return self.save_programs(programs)
        return False
