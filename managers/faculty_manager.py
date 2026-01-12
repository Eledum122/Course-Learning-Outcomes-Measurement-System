"""
مدير بيانات أعضاء هيئة التدريس
Faculty Members Manager
"""

import json
import os
from typing import List, Optional
from models.faculty_member import FacultyMember


class FacultyManager:
    """مدير بيانات أعضاء هيئة التدريس"""

    def __init__(self, data_dir: str = "data"):
        """
        تهيئة المدير

        Args:
            data_dir: مسار مجلد البيانات
        """
        self.data_dir = data_dir
        self.file_path = os.path.join(data_dir, "faculty_members.json")
        self.members: List[FacultyMember] = []

        # إنشاء مجلد البيانات إذا لم يكن موجوداً
        os.makedirs(data_dir, exist_ok=True)

        # تحميل البيانات
        self.load_members()

    def load_members(self):
        """تحميل قائمة الأعضاء من الملف"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.members = [FacultyMember.from_dict(member_data) for member_data in data]
                print(f"✓ Loaded {len(self.members)} faculty members")
            else:
                self.members = []
                print("! No faculty members file found, starting fresh")
        except Exception as e:
            print(f"✗ Error loading faculty members: {e}")
            self.members = []

    def save_members(self) -> bool:
        """
        حفظ قائمة الأعضاء إلى الملف

        Returns:
            True إذا تم الحفظ بنجاح
        """
        try:
            data = [member.to_dict() for member in self.members]
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Saved {len(self.members)} faculty members")
            return True
        except Exception as e:
            print(f"✗ Error saving faculty members: {e}")
            return False

    def add_member(self, member: FacultyMember) -> bool:
        """
        إضافة عضو جديد

        Args:
            member: بيانات العضو

        Returns:
            True إذا تمت الإضافة بنجاح
        """
        # التحقق من عدم وجود عضو بنفس الرقم الوظيفي
        if self.get_member_by_id(member.employee_id):
            print(f"✗ Employee ID {member.employee_id} already exists")
            return False

        self.members.append(member)
        return self.save_members()

    def update_member(self, employee_id: str, updated_member: FacultyMember) -> bool:
        """
        تحديث بيانات عضو

        Args:
            employee_id: الرقم الوظيفي للعضو المراد تحديثه
            updated_member: البيانات الجديدة

        Returns:
            True إذا تم التحديث بنجاح
        """
        for i, member in enumerate(self.members):
            if member.employee_id == employee_id:
                self.members[i] = updated_member
                return self.save_members()

        print(f"✗ Employee ID {employee_id} not found")
        return False

    def delete_member(self, employee_id: str) -> bool:
        """
        حذف عضو

        Args:
            employee_id: الرقم الوظيفي

        Returns:
            True إذا تم الحذف بنجاح
        """
        original_count = len(self.members)
        self.members = [m for m in self.members if m.employee_id != employee_id]

        if len(self.members) < original_count:
            return self.save_members()

        print(f"✗ Employee ID {employee_id} not found")
        return False

    def get_member_by_id(self, employee_id: str) -> Optional[FacultyMember]:
        """
        الحصول على عضو بالرقم الوظيفي

        Args:
            employee_id: الرقم الوظيفي

        Returns:
            بيانات العضو أو None
        """
        for member in self.members:
            if member.employee_id == employee_id:
                return member
        return None

    def get_member_by_name(self, name: str) -> Optional[FacultyMember]:
        """
        الحصول على عضو بالاسم

        Args:
            name: اسم عضو هيئة التدريس

        Returns:
            بيانات العضو أو None
        """
        name_lower = name.lower().strip()
        for member in self.members:
            if member.name.lower().strip() == name_lower:
                return member
        return None

    def search_members(self, query: str) -> List[FacultyMember]:
        """
        البحث عن أعضاء

        Args:
            query: نص البحث (في الرقم الوظيفي أو الاسم)

        Returns:
            قائمة الأعضاء المطابقة
        """
        query = query.lower().strip()
        if not query:
            return self.members

        results = []
        for member in self.members:
            if (query in member.employee_id.lower() or
                query in member.name.lower() or
                query in member.academic_degree.lower() or
                query in member.general_specialization.lower() or
                query in member.specific_specialization.lower() or
                query in getattr(member, 'department_ar', '').lower() or
                query in getattr(member, 'college_ar', '').lower()):
                results.append(member)

        return results

    def get_members_by_department(self, department_ar: str, active_only: bool = False) -> List[FacultyMember]:
        """
        الحصول على الأعضاء في قسم معين

        Args:
            department_ar: اسم القسم بالعربية
            active_only: إرجاع الأعضاء النشطين فقط

        Returns:
            قائمة الأعضاء
        """
        members = [m for m in self.members if getattr(m, 'department_ar', '') == department_ar]
        if active_only:
            members = [m for m in members if getattr(m, 'is_active', True)]
        return members

    def get_unique_departments(self) -> List[str]:
        """
        الحصول على قائمة الأقسام الفريدة

        Returns:
            قائمة الأقسام
        """
        departments = {getattr(m, 'department_ar', '') for m in self.members if getattr(m, 'department_ar', '')}
        return sorted(list(departments))

    def get_unique_colleges(self) -> List[str]:
        """
        الحصول على قائمة الكليات الفريدة

        Returns:
            قائمة الكليات
        """
        colleges = {getattr(m, 'college_ar', '') for m in self.members if getattr(m, 'college_ar', '')}
        return sorted(list(colleges))

    def get_all_members(self) -> List[FacultyMember]:
        """
        الحصول على جميع الأعضاء

        Returns:
            قائمة جميع الأعضاء
        """
        return sorted(self.members, key=lambda m: m.name)

    def get_members_for_combobox(self) -> List[str]:
        """
        الحصول على قائمة الأعضاء بصيغة مناسبة للـ Combobox

        Returns:
            قائمة نصوص للعرض في Combobox
        """
        return [member.get_display_name() for member in sorted(self.members, key=lambda m: m.name)]

    def get_member_by_display_name(self, display_name: str) -> Optional[FacultyMember]:
        """
        الحصول على عضو من اسم العرض

        Args:
            display_name: اسم العرض (الصيغة: "الرقم - الاسم (الدرجة)")

        Returns:
            بيانات العضو أو None
        """
        # استخراج الرقم الوظيفي من اسم العرض
        if ' - ' in display_name:
            employee_id = display_name.split(' - ')[0].strip()
            return self.get_member_by_id(employee_id)
        return None

    def get_count(self) -> int:
        """
        الحصول على عدد الأعضاء

        Returns:
            عدد الأعضاء
        """
        return len(self.members)
