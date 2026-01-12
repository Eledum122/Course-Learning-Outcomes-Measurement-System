"""
نموذج بيانات عضو هيئة التدريس
Faculty Member Model
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, List
from datetime import datetime


@dataclass
class FacultyMember:
    """عضو هيئة التدريس"""

    employee_id: str  # الرقم الوظيفي
    name: str  # الاسم
    academic_degree: str  # الدرجة العلمية
    general_specialization: str  # التخصص العام
    specific_specialization: str  # التخصص الدقيق

    # معلومات القسم والكلية
    department_ar: str = ""  # القسم (عربي)
    department_en: str = ""  # القسم (إنجليزي)
    college_ar: str = ""  # الكلية (عربي)
    college_en: str = ""  # الكلية (إنجليزي)

    # معلومات إضافية
    email: str = ""  # البريد الإلكتروني
    phone: str = ""  # رقم الهاتف
    office_number: str = ""  # رقم المكتب
    is_active: bool = True  # حالة العضو
    user_id: str = ""  # معرف المستخدم في النظام (إذا كان لديه حساب)

    # حقول تلقائية
    faculty_id: str = field(default="")  # معرف فريد للعضو
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """التحقق من صحة البيانات"""
        if not self.employee_id or not self.employee_id.strip():
            raise ValueError("الرقم الوظيفي مطلوب / Employee ID is required")

        if not self.name or not self.name.strip():
            raise ValueError("الاسم مطلوب / Name is required")

        # تنظيف البيانات
        self.employee_id = self.employee_id.strip()
        self.name = self.name.strip()
        self.academic_degree = self.academic_degree.strip()
        self.general_specialization = self.general_specialization.strip()
        self.specific_specialization = self.specific_specialization.strip()

        # توليد faculty_id إذا لم يكن موجوداً
        if not self.faculty_id:
            import uuid
            self.faculty_id = f"fac_{uuid.uuid4().hex[:12]}"

    def to_dict(self):
        """تحويل إلى قاموس"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """إنشاء من قاموس"""
        return cls(
            employee_id=data.get('employee_id', ''),
            name=data.get('name', ''),
            academic_degree=data.get('academic_degree', ''),
            general_specialization=data.get('general_specialization', ''),
            specific_specialization=data.get('specific_specialization', ''),
            department_ar=data.get('department_ar', ''),
            department_en=data.get('department_en', ''),
            college_ar=data.get('college_ar', ''),
            college_en=data.get('college_en', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            office_number=data.get('office_number', ''),
            is_active=data.get('is_active', True),
            user_id=data.get('user_id', ''),
            faculty_id=data.get('faculty_id', ''),
            created_date=data.get('created_date', datetime.now().isoformat()),
            last_modified=data.get('last_modified', datetime.now().isoformat())
        )

    def get_display_name(self):
        """الحصول على الاسم للعرض (مع الدرجة العلمية)"""
        if self.academic_degree:
            return f"{self.employee_id} - {self.name} ({self.academic_degree})"
        return f"{self.employee_id} - {self.name}"

    def __str__(self):
        return self.get_display_name()

    def __repr__(self):
        return f"FacultyMember(employee_id='{self.employee_id}', name='{self.name}', degree='{self.academic_degree}')"


# الدرجات العلمية المتاحة
ACADEMIC_DEGREES = [
    "أستاذ / Professor",
    "أستاذ مشارك / Associate Professor",
    "أستاذ مساعد / Assistant Professor",
    "محاضر / Lecturer",
    "معيد / Teaching Assistant",
    "مدرس / Instructor"
]
