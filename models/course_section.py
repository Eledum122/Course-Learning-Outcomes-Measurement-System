"""
نموذج بيانات شعبة المقرر
Course Section Model - Stage 3
"""

from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
from .course import Semester


class StudentStatus(Enum):
    """حالة الطالب - Student Status"""
    REGULAR = "Regular"  # منتظم
    DROPPED = "Dropped"  # معتذر
    PROHIBITED = "Prohibited"  # محروم
    INCOMPLETE = "Incomplete"  # غير مكتمل


class Student:
    """طالب في الشعبة - Student"""

    def __init__(self, student_id: str):
        self.student_id: str = student_id  # الرقم الجامعي للطالب
        self.name: str = ""  # اسم الطالب
        self.status: StudentStatus = StudentStatus.REGULAR  # حالة الطالب
        self.seq: int = 0  # الترتيب في القائمة

        # درجات الطالب في الأنشطة (Activity Name -> Mark)
        self.activity_marks: Dict[str, float] = {}

        # درجات الطالب في المخرجات (CLO Code -> Mark)
        self.clo_marks: Dict[str, float] = {}

        # الدرجة الكلية
        self.total_mark: float = 0.0

        # حالة النجاح
        self.passed: bool = False

    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'student_id': self.student_id,
            'name': self.name,
            'status': self.status.value if isinstance(self.status, StudentStatus) else self.status,
            'seq': self.seq,
            'activity_marks': self.activity_marks,
            'clo_marks': self.clo_marks,
            'total_mark': self.total_mark,
            'passed': self.passed
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Student':
        """إنشاء من قاموس"""
        student = cls(student_id=data.get('student_id', ''))
        student.name = data.get('name', '')

        # تحويل حالة الطالب
        status_value = data.get('status', 'Regular')
        student.status = StudentStatus(status_value) if isinstance(status_value, str) else status_value

        student.seq = data.get('seq', 0)
        student.activity_marks = data.get('activity_marks', {})
        student.clo_marks = data.get('clo_marks', {})
        student.total_mark = data.get('total_mark', 0.0)
        student.passed = data.get('passed', False)
        return student

    def validate(self) -> tuple[bool, str]:
        """التحقق من صحة البيانات"""
        if not self.student_id:
            return False, "يجب إدخال الرقم الجامعي للطالب"
        if not self.name:
            return False, f"يجب إدخال اسم الطالب {self.student_id}"
        return True, ""


class CourseSection:
    """شعبة المقرر - Course Section (Stage 3)"""

    def __init__(self, section_id: str):
        self.section_id: str = section_id  # معرف الشعبة (فريد)
        self.course_id: str = ""  # معرف المقرر المرتبط

        # معلومات الشعبة
        self.section_number: str = ""  # رقم الشعبة
        self.academic_year: str = ""  # السنة الدراسية (e.g., "1445-1446")
        self.semester: Semester = Semester.FIRST  # الفصل الدراسي
        self.course_coordinator: str = ""  # منسق المقرر
        self.section_instructor: str = ""  # مدرس الشعبة
        self.beneficiary_department: str = ""  # القسم المستفيد
        self.beneficiary_faculty: str = ""  # كلية القسم المستفيد
        self.gender_section: str = "Male"  # الشطر: Male (طلاب) أو Female (طالبات)

        # المستويات المستهدفة للمخرجات (CLO Code -> Target Level %)
        # يتم نسخها من المقرر الأساسي أو زيادتها إذا تحقق المستوى السابق
        self.clo_target_levels: Dict[str, float] = {}

        # قائمة الطلاب
        self.students: List[Student] = []

        # الإحصائيات المحسوبة
        self.statistics: Dict = {}

        # حالة الإكمال
        self.section_data_completed: bool = False  # الخطوة 1: بيانات الشعبة
        self.students_data_completed: bool = False  # الخطوة 2: بيانات الطلاب
        self.grades_data_completed: bool = False  # الخطوة 3: درجات الطلاب

        # البيانات الوصفية
        self.created_date: str = datetime.now().isoformat()
        self.modified_date: str = datetime.now().isoformat()
        self.created_by: str = ""

        # ربط مع جدول المواصفات
        self.specifications_table_verified: bool = False

    def update_modified_date(self):
        """تحديث تاريخ التعديل"""
        self.modified_date = datetime.now().isoformat()

    def validate_section_info(self) -> tuple[bool, str]:
        """التحقق من صحة بيانات الشعبة الأساسية"""
        if not self.course_id:
            return False, "يجب ربط الشعبة بمقرر"
        if not self.section_number:
            return False, "يجب إدخال رقم الشعبة"
        if not self.academic_year:
            return False, "يجب إدخال السنة الدراسية"
        if not self.course_coordinator:
            return False, "يجب إدخال اسم منسق المقرر"
        if not self.section_instructor:
            return False, "يجب إدخال اسم مدرس الشعبة"
        return True, ""

    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'section_id': self.section_id,
            'course_id': self.course_id,
            'section_number': self.section_number,
            'academic_year': self.academic_year,
            'semester': self.semester.value if isinstance(self.semester, Semester) else self.semester,
            'course_coordinator': self.course_coordinator,
            'section_instructor': self.section_instructor,
            'beneficiary_department': self.beneficiary_department,
            'beneficiary_faculty': self.beneficiary_faculty,
            'gender_section': self.gender_section,
            'clo_target_levels': self.clo_target_levels,
            'students': [student.to_dict() for student in self.students],
            'statistics': self.statistics,
            'section_data_completed': self.section_data_completed,
            'students_data_completed': self.students_data_completed,
            'grades_data_completed': self.grades_data_completed,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'created_by': self.created_by,
            'specifications_table_verified': self.specifications_table_verified
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CourseSection':
        """إنشاء من قاموس"""
        section = cls(section_id=data.get('section_id', ''))
        section.course_id = data.get('course_id', '')
        section.section_number = data.get('section_number', '')
        section.academic_year = data.get('academic_year', '')

        # تحويل Semester
        semester_value = data.get('semester', 'First')
        section.semester = Semester(semester_value) if isinstance(semester_value, str) else semester_value

        section.course_coordinator = data.get('course_coordinator', '')
        section.section_instructor = data.get('section_instructor', '')
        section.beneficiary_department = data.get('beneficiary_department', '')
        section.beneficiary_faculty = data.get('beneficiary_faculty', '')
        section.gender_section = data.get('gender_section', 'Male')
        section.clo_target_levels = data.get('clo_target_levels', {})
        section.students = [Student.from_dict(std_data) for std_data in data.get('students', [])]
        section.statistics = data.get('statistics', {})
        section.section_data_completed = data.get('section_data_completed', False)
        section.students_data_completed = data.get('students_data_completed', False)
        section.grades_data_completed = data.get('grades_data_completed', False)
        section.created_date = data.get('created_date', section.created_date)
        section.modified_date = data.get('modified_date', section.modified_date)
        section.created_by = data.get('created_by', '')
        section.specifications_table_verified = data.get('specifications_table_verified', False)

        return section

    def __str__(self):
        return f"CourseSection({self.section_number} - {self.academic_year} - {self.semester.value})"

    def __repr__(self):
        return self.__str__()
