"""
نموذج بيانات ترويسة التقارير
Report Header Data Model
"""

import json
import os
from typing import Dict, Optional


class ReportHeader:
    """إعدادات ترويسة التقارير - Report Header Settings"""

    def __init__(self):
        # مسار شعار الجامعة
        self.logo_path: str = ""

        # النصوص الإنجليزية
        self.university_name_en: str = "University of Tabuk"
        self.faculty_name_en: str = "Faculty of Science"
        self.department_name_en: str = "Department of Statistics"

        # النصوص العربية
        self.university_name_ar: str = "جامعة تبوك"
        self.faculty_name_ar: str = "كلية العلوم"
        self.department_name_ar: str = "قسم الإحصاء"

    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'logo_path': self.logo_path,
            'university_name_en': self.university_name_en,
            'faculty_name_en': self.faculty_name_en,
            'department_name_en': self.department_name_en,
            'university_name_ar': self.university_name_ar,
            'faculty_name_ar': self.faculty_name_ar,
            'department_name_ar': self.department_name_ar
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportHeader':
        """إنشاء من قاموس"""
        header = cls()
        header.logo_path = data.get('logo_path', '')
        header.university_name_en = data.get('university_name_en', 'University of Tabuk')
        header.faculty_name_en = data.get('faculty_name_en', 'Faculty of Science')
        header.department_name_en = data.get('department_name_en', 'Department of Statistics')
        header.university_name_ar = data.get('university_name_ar', 'جامعة تبوك')
        header.faculty_name_ar = data.get('faculty_name_ar', 'كلية العلوم')
        header.department_name_ar = data.get('department_name_ar', 'قسم الإحصاء')
        return header

    def save(self, file_path: str = "data/report_header.json") -> bool:
        """حفظ الإعدادات"""
        try:
            # التأكد من وجود المجلد
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving report header: {e}")
            return False

    @classmethod
    def load(cls, file_path: str = "data/report_header.json") -> 'ReportHeader':
        """تحميل الإعدادات"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading report header: {e}")

        # إرجاع إعدادات افتراضية
        return cls()
