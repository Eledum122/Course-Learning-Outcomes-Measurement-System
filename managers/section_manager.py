"""
مدير بيانات الشعب
Section Manager - للتعامل مع قاعدة بيانات الشعب
"""

import json
import os
from typing import List, Optional
from models.course_section import CourseSection, Student


class SectionManager:
    """مدير بيانات الشعب"""

    def __init__(self, data_dir: str = "data/sections"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _get_section_file_path(self, section_id: str) -> str:
        """الحصول على مسار ملف الشعبة"""
        return os.path.join(self.data_dir, f"{section_id}.json")

    def save_section(self, section: CourseSection) -> bool:
        """
        حفظ بيانات الشعبة

        Args:
            section: كائن الشعبة

        Returns:
            True إذا تم الحفظ بنجاح
        """
        try:
            section.update_modified_date()
            file_path = self._get_section_file_path(section.section_id)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(section.to_dict(), f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error saving section: {e}")
            return False

    def load_section(self, section_id: str) -> Optional[CourseSection]:
        """
        تحميل بيانات الشعبة

        Args:
            section_id: معرف الشعبة

        Returns:
            كائن الشعبة أو None إذا لم يتم العثور عليها
        """
        try:
            file_path = self._get_section_file_path(section_id)

            if not os.path.exists(file_path):
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return CourseSection.from_dict(data)
        except Exception as e:
            print(f"Error loading section: {e}")
            return None

    def delete_section(self, section_id: str) -> bool:
        """
        حذف الشعبة

        Args:
            section_id: معرف الشعبة

        Returns:
            True إذا تم الحذف بنجاح
        """
        try:
            file_path = self._get_section_file_path(section_id)

            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting section: {e}")
            return False

    def get_all_sections(self) -> List[CourseSection]:
        """
        الحصول على جميع الشعب

        Returns:
            قائمة بجميع الشعب
        """
        sections = []
        try:
            if not os.path.exists(self.data_dir):
                return sections

            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    section_id = filename[:-5]  # إزالة .json
                    section = self.load_section(section_id)
                    if section:
                        sections.append(section)

            # ترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
            sections.sort(key=lambda x: x.created_date, reverse=True)
        except Exception as e:
            print(f"Error getting all sections: {e}")

        return sections

    def get_sections_by_course(self, course_id: str) -> List[CourseSection]:
        """
        الحصول على جميع شعب مقرر محدد

        Args:
            course_id: معرف المقرر

        Returns:
            قائمة بشعب المقرر
        """
        all_sections = self.get_all_sections()
        return [s for s in all_sections if s.course_id == course_id]

    def section_exists(self, section_id: str) -> bool:
        """
        التحقق من وجود الشعبة

        Args:
            section_id: معرف الشعبة

        Returns:
            True إذا كانت الشعبة موجودة
        """
        file_path = self._get_section_file_path(section_id)
        return os.path.exists(file_path)

    def generate_section_id(self, course_id: str, section_number: str,
                          academic_year: str, semester: str) -> str:
        """
        توليد معرف فريد للشعبة

        Args:
            course_id: معرف المقرر
            section_number: رقم الشعبة
            academic_year: السنة الدراسية
            semester: الفصل الدراسي

        Returns:
            معرف الشعبة
        """
        # تنظيف السنة الدراسية من المسافات والشرطات
        clean_year = academic_year.replace('-', '').replace(' ', '')

        # تحويل الفصل الدراسي إلى اختصار
        semester_abbr = {
            'First': '1',
            'Second': '2',
            'Summer': 'S'
        }.get(semester, '1')

        return f"{course_id}_{section_number}_{clean_year}_{semester_abbr}"

    def get_section_summary(self, section: CourseSection) -> dict:
        """
        الحصول على ملخص الشعبة

        Args:
            section: كائن الشعبة

        Returns:
            قاموس يحتوي على ملخص الشعبة
        """
        return {
            'section_id': section.section_id,
            'section_number': section.section_number,
            'academic_year': section.academic_year,
            'semester': section.semester.value if hasattr(section.semester, 'value') else section.semester,
            'course_coordinator': section.course_coordinator,
            'section_instructor': section.section_instructor,
            'students_count': len(section.students),
            'section_data_completed': section.section_data_completed,
            'students_data_completed': section.students_data_completed,
            'grades_data_completed': section.grades_data_completed,
            'created_date': section.created_date,
            'modified_date': section.modified_date
        }
