"""
مدير البرامج الأكاديمية - Academic Program Manager
إدارة حفظ وتحميل وإدارة البرامج الأكاديمية
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from models.academic_program import AcademicProgram


class AcademicProgramManager:
    """مدير البرامج الأكاديمية"""

    def __init__(self, data_dir: str = "data/academic_programs"):
        """
        تهيئة مدير البرامج الأكاديمية

        Args:
            data_dir: مسار مجلد البيانات
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.programs_file = self.data_dir / "programs.json"
        self.programs: Dict[str, AcademicProgram] = {}
        self._load_programs()

    def _load_programs(self):
        """تحميل البرامج من الملف"""
        if self.programs_file.exists():
            try:
                with open(self.programs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for program_id, program_data in data.items():
                        self.programs[program_id] = AcademicProgram.from_dict(program_data)
            except Exception as e:
                print(f"Error loading programs: {e}")
                self.programs = {}
        else:
            self.programs = {}

    def _save_programs(self):
        """حفظ البرامج إلى الملف"""
        try:
            data = {program_id: program.to_dict()
                    for program_id, program in self.programs.items()}
            with open(self.programs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving programs: {e}")

    def create_program(self, program: AcademicProgram) -> bool:
        """
        إنشاء برنامج جديد

        Args:
            program: البرنامج الأكاديمي

        Returns:
            True إذا تم الإنشاء بنجاح
        """
        if program.program_id in self.programs:
            return False

        self.programs[program.program_id] = program
        self._save_programs()
        return True

    def update_program(self, program: AcademicProgram) -> bool:
        """
        تحديث برنامج موجود

        Args:
            program: البرنامج الأكاديمي

        Returns:
            True إذا تم التحديث بنجاح
        """
        if program.program_id not in self.programs:
            return False

        self.programs[program.program_id] = program
        self._save_programs()
        return True

    def delete_program(self, program_id: str, cascade: bool = True) -> Dict[str, any]:
        """
        حذف برنامج مع إمكانية الحذف المتسلسل

        Args:
            program_id: معرف البرنامج
            cascade: إذا كان True، سيتم حذف المقررات والمستخدمين المرتبطين

        Returns:
            Dict يحتوي على نتائج الحذف
        """
        result = {
            'success': False,
            'deleted_courses': [],
            'deleted_users': [],
            'errors': []
        }

        if program_id not in self.programs:
            result['errors'].append(f"Program {program_id} not found")
            return result

        program = self.programs[program_id]

        if cascade:
            # حذف المقررات المرتبطة بالبرنامج
            try:
                from managers.course_manager import CourseManager
                course_manager = CourseManager()
                all_courses = course_manager.list_all_courses()

                # البحث عن المقررات المرتبطة بهذا البرنامج
                program_courses = [
                    c for c in all_courses
                    if c.get('program', '') in [program.program_name_ar, program.program_name_en]
                ]

                for course_data in program_courses:
                    course_id = course_data['course_id']
                    # استخدام delete_course_cascade لحذف المقرر والشعب
                    course_result = self.delete_course_cascade(course_manager, course_id)
                    if course_result['success']:
                        result['deleted_courses'].append(course_id)
                        result['deleted_users'].extend(course_result.get('deleted_users', []))
                    else:
                        result['errors'].extend(course_result.get('errors', []))
            except Exception as e:
                result['errors'].append(f"Error deleting courses: {str(e)}")

            # حذف المنسقين المرتبطين بالبرنامج فقط
            try:
                from managers.access_control import AccessControl
                access_control = AccessControl()

                # البحث عن المستخدمين المعينين لهذا البرنامج فقط
                for user in list(access_control.users.values()):
                    if program_id in user.assigned_programs:
                        # إزالة البرنامج من المستخدم
                        user.assigned_programs.remove(program_id)

                        # إذا لم يعد لديه أي برامج أو مقررات أو شعب، حذف المستخدم
                        if (not user.assigned_programs and
                            not user.assigned_courses and
                            not user.assigned_sections and
                            not user.has_role('admin')):
                            access_control.delete_user(user.user_id)
                            result['deleted_users'].append(user.user_id)

                access_control.save_users()
            except Exception as e:
                result['errors'].append(f"Error handling users: {str(e)}")

        # حذف البرنامج نفسه
        try:
            del self.programs[program_id]
            self._save_programs()
            result['success'] = True
        except Exception as e:
            result['errors'].append(f"Error deleting program: {str(e)}")

        return result

    def delete_course_cascade(self, course_manager, course_id: str) -> Dict[str, any]:
        """
        حذف مقرر مع حذف المستخدمين المرتبطين (دالة مساعدة)

        Args:
            course_manager: مدير المقررات
            course_id: معرف المقرر

        Returns:
            Dict يحتوي على نتائج الحذف
        """
        result = {
            'success': False,
            'deleted_users': [],
            'errors': []
        }

        try:
            from managers.access_control import AccessControl
            access_control = AccessControl()

            # حذف المستخدمين المرتبطين بهذا المقرر فقط
            for user in list(access_control.users.values()):
                # التحقق من منسقي المقرر
                if course_id in user.assigned_courses:
                    user.assigned_courses.remove(course_id)

                # التحقق من مدرسي الشعب
                if course_id in user.assigned_sections:
                    del user.assigned_sections[course_id]

                # حذف المستخدم إذا لم يعد لديه أي تعيينات
                if (not user.assigned_programs and
                    not user.assigned_courses and
                    not user.assigned_sections and
                    not user.has_role('admin')):
                    access_control.delete_user(user.user_id)
                    result['deleted_users'].append(user.user_id)

            access_control.save_users()

            # حذف المقرر
            if course_manager.delete_course(course_id):
                result['success'] = True
            else:
                result['errors'].append(f"Failed to delete course {course_id}")

        except Exception as e:
            result['errors'].append(f"Error in cascade delete: {str(e)}")

        return result

    def get_program(self, program_id: str) -> Optional[AcademicProgram]:
        """
        الحصول على برنامج بمعرفه

        Args:
            program_id: معرف البرنامج

        Returns:
            البرنامج الأكاديمي أو None
        """
        return self.programs.get(program_id)

    def get_all_programs(self, active_only: bool = False) -> List[AcademicProgram]:
        """
        الحصول على جميع البرامج

        Args:
            active_only: إرجاع البرامج النشطة فقط

        Returns:
            قائمة البرامج الأكاديمية
        """
        programs = list(self.programs.values())
        if active_only:
            programs = [p for p in programs if p.is_active]
        return programs

    def get_programs_by_coordinator(self, coordinator_id: str) -> List[AcademicProgram]:
        """
        الحصول على البرامج التي يديرها منسق معين

        Args:
            coordinator_id: معرف المنسق

        Returns:
            قائمة البرامج
        """
        return [p for p in self.programs.values() if p.coordinator_id == coordinator_id]

    def get_programs_by_department(self, department_ar: str) -> List[AcademicProgram]:
        """
        الحصول على البرامج في قسم معين

        Args:
            department_ar: اسم القسم بالعربية

        Returns:
            قائمة البرامج
        """
        return [p for p in self.programs.values() if p.department_ar == department_ar]

    def get_programs_by_college(self, college_ar: str) -> List[AcademicProgram]:
        """
        الحصول على البرامج في كلية معينة

        Args:
            college_ar: اسم الكلية بالعربية

        Returns:
            قائمة البرامج
        """
        return [p for p in self.programs.values() if p.college_ar == college_ar]

    def search_programs(self, query: str, language: str = 'ar') -> List[AcademicProgram]:
        """
        البحث عن البرامج

        Args:
            query: نص البحث
            language: اللغة ('ar' أو 'en')

        Returns:
            قائمة البرامج المطابقة
        """
        query = query.lower()
        results = []

        for program in self.programs.values():
            if language == 'ar':
                searchable = f"{program.program_name_ar} {program.department_ar} {program.college_ar}".lower()
            else:
                searchable = f"{program.program_name_en} {program.department_en} {program.college_en}".lower()

            if query in searchable:
                results.append(program)

        return results

    def get_unique_departments(self, language: str = 'ar') -> List[str]:
        """
        الحصول على قائمة الأقسام الفريدة

        Args:
            language: اللغة

        Returns:
            قائمة الأقسام
        """
        if language == 'ar':
            departments = {p.department_ar for p in self.programs.values() if p.department_ar}
        else:
            departments = {p.department_en for p in self.programs.values() if p.department_en}
        return sorted(list(departments))

    def get_unique_colleges(self, language: str = 'ar') -> List[str]:
        """
        الحصول على قائمة الكليات الفريدة

        Args:
            language: اللغة

        Returns:
            قائمة الكليات
        """
        if language == 'ar':
            colleges = {p.college_ar for p in self.programs.values() if p.college_ar}
        else:
            colleges = {p.college_en for p in self.programs.values() if p.college_en}
        return sorted(list(colleges))

    def get_unique_colleges_ar(self) -> List[str]:
        """
        الحصول على قائمة الكليات الفريدة (عربي)

        Returns:
            قائمة الكليات بالعربي
        """
        colleges = {p.college_ar for p in self.programs.values() if p.college_ar}
        return sorted(list(colleges))

    def get_unique_colleges_en(self) -> List[str]:
        """
        الحصول على قائمة الكليات الفريدة (إنجليزي)

        Returns:
            قائمة الكليات بالإنجليزي
        """
        colleges = {p.college_en for p in self.programs.values() if p.college_en}
        return sorted(list(colleges))

    def get_unique_departments_ar(self) -> List[str]:
        """
        الحصول على قائمة الأقسام الفريدة (عربي)

        Returns:
            قائمة الأقسام بالعربي
        """
        departments = {p.department_ar for p in self.programs.values() if p.department_ar}
        return sorted(list(departments))

    def get_unique_departments_en(self) -> List[str]:
        """
        الحصول على قائمة الأقسام الفريدة (إنجليزي)

        Returns:
            قائمة الأقسام بالإنجليزي
        """
        departments = {p.department_en for p in self.programs.values() if p.department_en}
        return sorted(list(departments))

    def get_program_count(self) -> int:
        """الحصول على عدد البرامج"""
        return len(self.programs)

    def get_active_program_count(self) -> int:
        """الحصول على عدد البرامج النشطة"""
        return sum(1 for p in self.programs.values() if p.is_active)


# إنشاء نسخة عامة من المدير
program_manager = AcademicProgramManager()
