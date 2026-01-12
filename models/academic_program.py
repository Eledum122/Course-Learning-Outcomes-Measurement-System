"""
نموذج البرنامج الأكاديمي - Academic Program Model
يحتوي على معلومات البرنامج الأكاديمي ومنسقه
"""

from typing import Dict, Optional
from datetime import datetime
import uuid


class AcademicProgram:
    """نموذج البرنامج الأكاديمي"""

    def __init__(
        self,
        program_name_ar: str,
        program_name_en: str,
        coordinator_id: str = "",  # معرف منسق البرنامج (اختياري، يمكن تحديده لاحقاً)
        university_ar: str = "جامعة تبوك",
        university_en: str = "University of Tabuk",
        college_ar: str = "",
        college_en: str = "",
        department_ar: str = "",
        department_en: str = "",
        program_id: Optional[str] = None
    ):
        """
        تهيئة البرنامج الأكاديمي

        Args:
            program_name_ar: اسم البرنامج بالعربية
            program_name_en: اسم البرنامج بالإنجليزية
            coordinator_id: معرف منسق البرنامج (اختياري، يمكن تحديده لاحقاً من أعضاء القسم)
            university_ar: اسم الجامعة بالعربية
            university_en: اسم الجامعة بالإنجليزية
            college_ar: اسم الكلية بالعربية
            college_en: اسم الكلية بالإنجليزية
            department_ar: اسم القسم بالعربية
            department_en: اسم القسم بالإنجليزية
            program_id: معرف البرنامج (اختياري، يتم إنشاؤه تلقائياً)
        """
        self.program_id = program_id or self._generate_id()

        # معلومات الجامعة والكلية والقسم
        self.university_ar = university_ar
        self.university_en = university_en
        self.college_ar = college_ar
        self.college_en = college_en
        self.department_ar = department_ar
        self.department_en = department_en

        # معلومات البرنامج
        self.program_name_ar = program_name_ar
        self.program_name_en = program_name_en
        self.program_code = ""  # رمز البرنامج (اختياري)

        # منسق البرنامج
        self.coordinator_id = coordinator_id  # user_id لمنسق البرنامج

        # معلومات إضافية
        self.description_ar = ""
        self.description_en = ""
        self.created_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
        self.is_active = True
        self.metadata = {}

    def _generate_id(self) -> str:
        """إنشاء معرف فريد للبرنامج"""
        return f"prog_{uuid.uuid4().hex[:12]}"

    def update_coordinator(self, new_coordinator_id: str):
        """تحديث منسق البرنامج"""
        self.coordinator_id = new_coordinator_id
        self.last_modified = datetime.now().isoformat()

    def activate(self):
        """تفعيل البرنامج"""
        self.is_active = True
        self.last_modified = datetime.now().isoformat()

    def deactivate(self):
        """تعطيل البرنامج"""
        self.is_active = False
        self.last_modified = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """تحويل البرنامج إلى قاموس"""
        return {
            'program_id': self.program_id,
            'university_ar': self.university_ar,
            'university_en': self.university_en,
            'college_ar': self.college_ar,
            'college_en': self.college_en,
            'department_ar': self.department_ar,
            'department_en': self.department_en,
            'program_name_ar': self.program_name_ar,
            'program_name_en': self.program_name_en,
            'program_code': self.program_code,
            'coordinator_id': self.coordinator_id,
            'description_ar': self.description_ar,
            'description_en': self.description_en,
            'created_date': self.created_date,
            'last_modified': self.last_modified,
            'is_active': self.is_active,
            'metadata': self.metadata
        }

    @staticmethod
    def from_dict(data: Dict) -> 'AcademicProgram':
        """إنشاء برنامج من قاموس"""
        program = AcademicProgram(
            program_name_ar=data.get('program_name_ar', ''),
            program_name_en=data.get('program_name_en', ''),
            coordinator_id=data.get('coordinator_id', ''),
            university_ar=data.get('university_ar', 'جامعة تبوك'),
            university_en=data.get('university_en', 'University of Tabuk'),
            college_ar=data.get('college_ar', ''),
            college_en=data.get('college_en', ''),
            department_ar=data.get('department_ar', ''),
            department_en=data.get('department_en', ''),
            program_id=data.get('program_id')
        )
        program.program_code = data.get('program_code', '')
        program.description_ar = data.get('description_ar', '')
        program.description_en = data.get('description_en', '')
        program.created_date = data.get('created_date', program.created_date)
        program.last_modified = data.get('last_modified', program.last_modified)
        program.is_active = data.get('is_active', True)
        program.metadata = data.get('metadata', {})
        return program

    def get_full_hierarchy_ar(self) -> str:
        """الحصول على التسلسل الهرمي الكامل بالعربية"""
        parts = []
        if self.university_ar:
            parts.append(self.university_ar)
        if self.college_ar:
            parts.append(self.college_ar)
        if self.department_ar:
            parts.append(self.department_ar)
        if self.program_name_ar:
            parts.append(self.program_name_ar)
        return " > ".join(parts)

    def get_full_hierarchy_en(self) -> str:
        """الحصول على التسلسل الهرمي الكامل بالإنجليزية"""
        parts = []
        if self.university_en:
            parts.append(self.university_en)
        if self.college_en:
            parts.append(self.college_en)
        if self.department_en:
            parts.append(self.department_en)
        if self.program_name_en:
            parts.append(self.program_name_en)
        return " > ".join(parts)

    def __repr__(self):
        return f"AcademicProgram(id={self.program_id}, name_ar={self.program_name_ar})"
