"""
نموذج بيانات المقرر الدراسي
Course Model - Stage 1
"""

from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import os
import glob
import json


class Semester(Enum):
    """فصول الدراسة"""
    FIRST = "First"
    SECOND = "Second"
    SUMMER = "Summer"


class CLOCategory(Enum):
    """فئات نواتج التعلم"""
    KNOWLEDGE = "Knowledge"  # المعرفة
    SKILLS = "Skills"  # المهارات
    VALUES = "Values"  # القيم


class CourseInfo:
    """معلومات المقرر الأساسية - Course Information"""
    
    def __init__(self):
        self.course_title: str = ""  # اسم المقرر
        self.course_code: str = ""  # رمز المقرر
        self.sections: str = ""  # الشعب
        self.program: str = ""  # البرنامج
        self.academic_year: str = ""  # العام الأكاديمي (e.g., "1445")
        self.semester: Semester = Semester.FIRST  # الفصل الدراسي
        self.course_instructor: str = ""  # مدرس المقرر
        self.course_coordinator: str = ""  # منسق المقرر
        self.version: str = ""  # الإصدار
        self.department: str = ""  # القسم
        self.faculty: str = ""  # الكلية
        self.taught_outside_department: bool = False  # هل يُدرس المقرر خارج القسم
        self.other_departments: str = ""  # الأقسام الأخرى المستفيدة من المقرر
        self.other_departments_faculty: str = ""  # كلية القسم المستفيد
        self.date: str = datetime.now().strftime("%Y-%m-%d")  # التاريخ

        # معلومات المرحلة الثانية
        self.total_mark: float = 100.0  # الدرجة الكلية للمقرر
        self.passing_percentage: float = 60.0  # نسبة النجاح في المقرر (%)

        # حالة الاعتماد
        self.is_approved: bool = False
        self.approved_by: str = ""
        self.approved_date: str = ""
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'course_title': self.course_title,
            'course_code': self.course_code,
            'sections': self.sections,
            'program': self.program,
            'academic_year': self.academic_year,
            'semester': self.semester.value if isinstance(self.semester, Semester) else self.semester,
            'course_instructor': self.course_instructor,
            'course_coordinator': self.course_coordinator,
            'version': self.version,
            'department': self.department,
            'faculty': self.faculty,
            'taught_outside_department': self.taught_outside_department,
            'other_departments': self.other_departments,
            'other_departments_faculty': self.other_departments_faculty,
            'date': self.date,
            'total_mark': self.total_mark,
            'passing_percentage': self.passing_percentage,
            'is_approved': self.is_approved,
            'approved_by': self.approved_by,
            'approved_date': self.approved_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CourseInfo':
        """إنشاء من قاموس"""
        info = cls()
        info.course_title = data.get('course_title', '')
        info.course_code = data.get('course_code', '')
        info.sections = data.get('sections', '')
        info.program = data.get('program', '')
        info.academic_year = data.get('academic_year', '')
        semester_value = data.get('semester', 'First')
        info.semester = Semester(semester_value) if isinstance(semester_value, str) else semester_value
        info.course_instructor = data.get('course_instructor', '')
        info.course_coordinator = data.get('course_coordinator', '')
        info.version = data.get('version', '')
        info.department = data.get('department', '')
        info.faculty = data.get('faculty', '')
        info.taught_outside_department = data.get('taught_outside_department', False)
        info.other_departments = data.get('other_departments', '')
        info.other_departments_faculty = data.get('other_departments_faculty', '')
        info.date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
        info.total_mark = data.get('total_mark', 100.0)
        info.passing_percentage = data.get('passing_percentage', 60.0)
        info.is_approved = data.get('is_approved', False)
        info.approved_by = data.get('approved_by', '')
        info.approved_date = data.get('approved_date', '')
        return info
    
    def validate(self) -> tuple[bool, str]:
        """التحقق من صحة البيانات (التحقق الكامل لجميع الحقول بما في ذلك حقول المرحلة الثانية)"""
        if not self.course_title:
            return False, "يجب إدخال اسم المقرر"
        if not self.course_code:
            return False, "يجب إدخال رمز المقرر"
        if not self.sections:
            return False, "يجب إدخال الشعب"
        if not self.program:
            return False, "يجب إدخال البرنامج"
        if not self.academic_year:
            return False, "يجب إدخال العام الأكاديمي"
        if not self.course_instructor:
            return False, "يجب إدخال مدرس المقرر"
        if not self.course_coordinator:
            return False, "يجب إدخال منسق المقرر"
        # الإصدار، القسم، الكلية اختياريان لكن من الأفضل التحذير إن لم تُملأ
        if not self.version:
            return False, "يجب إدخال الإصدار"
        if not self.department:
            return False, "يجب إدخال القسم"
        if not self.faculty:
            return False, "يجب إدخال الكلية"
        return True, ""

    def validate_stage1(self) -> tuple[bool, str]:
        """التحقق من صحة معلومات المقرر في المرحلة الأولى (قيود مخففة).
        في المرحلة الأولى نطلب فقط أن يحتوي المقرر على اسم ورمز.
        """
        if not self.course_title:
            return False, "يجب إدخال اسم المقرر"
        if not self.course_code:
            return False, "يجب إدخال رمز المقرر"
        return True, ""


class CLO:
    """ناتج تعلم المقرر - Course Learning Outcome"""
    
    def __init__(self, code: str, category: CLOCategory):
        self.code: str = code  # الكود (مثل K1, S1, V1)
        self.category: CLOCategory = category  # الفئة
        self.description: str = ""  # الوصف
        self.aligned_plos: str = ""  # PLOs المرتبطة
        self.mark: float = 0.0  # الدرجة الكلية للمخرج
        self.criterion_for_success: float = 60.0  # معيار النجاح (%)
        self.target_level: float = 70.0  # المستوى المستهدف (%)
        
        # نتائج القياس (يتم حسابها لاحقاً)
        self.actual_level: float = 0.0  # المستوى الفعلي
        self.achievement_status: str = ""  # حالة التحقيق
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'code': self.code,
            'category': self.category.value if isinstance(self.category, CLOCategory) else self.category,
            'description': self.description,
            'aligned_plos': self.aligned_plos,
            'mark': self.mark,
            'criterion_for_success': self.criterion_for_success,
            'target_level': self.target_level,
            'actual_level': self.actual_level,
            'achievement_status': self.achievement_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CLO':
        """إنشاء من قاموس"""
        category_value = data.get('category', 'Knowledge')
        category = CLOCategory(category_value) if isinstance(category_value, str) else category_value
        
        clo = cls(
            code=data.get('code', ''),
            category=category
        )
        clo.description = data.get('description', '')
        clo.aligned_plos = data.get('aligned_plos', '')
        clo.mark = data.get('mark', 0.0)
        clo.criterion_for_success = data.get('criterion_for_success', 60.0)
        clo.target_level = data.get('target_level', 70.0)
        clo.actual_level = data.get('actual_level', 0.0)
        clo.achievement_status = data.get('achievement_status', '')
        return clo
    
    def validate(self) -> tuple[bool, str]:
        """التحقق من صحة البيانات (التحقق العام يشمل حقول المرحلة الثانية أيضاً)"""
        if not self.code:
            return False, "يجب إدخال كود المخرج"
        if not self.description:
            return False, f"يجب إدخال وصف المخرج {self.code}"
        if self.mark <= 0:
            return False, f"يجب أن تكون درجة المخرج {self.code} أكبر من صفر"
        if not (0 <= self.criterion_for_success <= 100):
            return False, f"معيار النجاح للمخرج {self.code} يجب أن يكون بين 0 و 100"
        if not (0 <= self.target_level <= 100):
            return False, f"المستوى المستهدف للمخرج {self.code} يجب أن يكون بين 0 و 100"
        return True, ""

    def validate_stage1(self) -> tuple[bool, str]:
        """التحقق من صحة المخرج ضمن المرحلة الأولى (أقل قيود: كود ووصف فقط)"""
        if not self.code:
            return False, "يجب إدخال كود المخرج"
        if not self.description:
            return False, f"يجب إدخال وصف المخرج {self.code}"
        return True, ""

class Topic:
    """موضوع من موضوعات المقرر - Course Topic"""
    
    def __init__(self, number: int):
        self.number: int = number  # رقم الموضوع
        self.title: str = ""  # عنوان الموضوع
        self.contact_hours: float = 0.0  # ساعات الاتصال
        self.mark: float = 0.0  # الدرجة المحسوبة للموضوع
        self.final_mark: float = 0.0  # الدرجة النهائية بعد التعديلات (Remark)
        self.remark: str = ""  # ملاحظات

        # توزيع الموضوع على نواتج التعلم (CLO Code -> Hours)
        self.clo_distribution: Dict[str, float] = {}

        # توزيع درجات الموضوع على نواتج التعلم (CLO Code -> Marks)
        self.clo_marks_distribution: Dict[str, float] = {}

        # توزيع درجات الموضوع على أنشطة التقييم (Activity Title -> Marks)
        self.activities_distribution: Dict[str, float] = {}

        # جدول المواصفات - ربط الموضوع مع CLOs والأنشطة (Key: "CLO_Code|Activity_Name" -> Mark)
        self.specifications_table: Dict[str, float] = {}
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'number': self.number,
            'title': self.title,
            'contact_hours': self.contact_hours,
            'mark': self.mark,
            'final_mark': self.final_mark,
            'remark': self.remark,
            'clo_distribution': self.clo_distribution,
            'clo_marks_distribution': self.clo_marks_distribution,
            'activities_distribution': self.activities_distribution,
            'specifications_table': self.specifications_table
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Topic':
        """إنشاء من قاموس"""
        topic = cls(number=data.get('number', 0))
        topic.title = data.get('title', '')
        topic.contact_hours = data.get('contact_hours', 0.0)
        topic.mark = data.get('mark', 0.0)
        topic.final_mark = data.get('final_mark', 0.0)
        topic.remark = data.get('remark', '')
        topic.clo_distribution = data.get('clo_distribution', {})
        topic.clo_marks_distribution = data.get('clo_marks_distribution', {})
        topic.activities_distribution = data.get('activities_distribution', {})
        topic.specifications_table = data.get('specifications_table', {})
        return topic
    
    def validate(self) -> tuple[bool, str]:
        """التحقق من صحة البيانات"""
        if not self.title:
            return False, f"يجب إدخال عنوان الموضوع رقم {self.number}"
        if self.contact_hours <= 0:
            return False, f"يجب أن تكون ساعات الاتصال للموضوع {self.number} أكبر من صفر"
        if self.mark < 0:
            return False, f"درجة الموضوع {self.number} لا يمكن أن تكون سالبة"
        
        # التحقق من توزيع الساعات على CLOs
        total_hours = sum(self.clo_distribution.values())
        if total_hours > 0 and abs(total_hours - self.contact_hours) > 0.01:
            return False, f"مجموع ساعات توزيع الموضوع {self.number} على المخرجات لا يساوي ساعات الاتصال"
        
        return True, ""


class AssessmentActivity:
    """نشاط تقييم - Assessment Activity"""
    
    def __init__(self, name: str):
        self.name: str = name  # اسم النشاط
        self.mark: float = 0.0  # الدرجة الكلية للنشاط
        self.percentage: float = 0.0  # النسبة المئوية من المجموع الكلي
        self.timing: str = ""  # توقيت التقييم
        
        # توزيع النشاط على الموضوعات (Topic Number -> Mark)
        self.topic_distribution: Dict[int, float] = {}
        
        # نواتج التعلم التي يقيسها هذا النشاط
        self.measures_clos: List[str] = []  # قائمة أكواد CLOs
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'name': self.name,
            'mark': self.mark,
            'percentage': self.percentage,
            'timing': self.timing,
            'topic_distribution': {str(k): v for k, v in self.topic_distribution.items()},
            'measures_clos': self.measures_clos
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AssessmentActivity':
        """إنشاء من قاموس"""
        activity = cls(name=data.get('name', ''))
        activity.mark = data.get('mark', 0.0)
        activity.percentage = data.get('percentage', 0.0)
        activity.timing = data.get('timing', '')
        activity.topic_distribution = {int(k): v for k, v in data.get('topic_distribution', {}).items()}
        activity.measures_clos = data.get('measures_clos', [])
        return activity
    
    def validate(self) -> tuple[bool, str]:
        """التحقق من صحة البيانات (التحقق العام للمرحلتين)"""
        if not self.name:
            return False, "يجب إدخال اسم النشاط"
        if self.mark <= 0:
            return False, f"يجب أن تكون درجة النشاط {self.name} أكبر من صفر"
        if not (0 <= self.percentage <= 100):
            return False, f"النسبة المئوية للنشاط {self.name} يجب أن تكون بين 0 و 100"
        if not self.measures_clos:
            return False, f"يجب تحديد المخرجات التي يقيسها النشاط {self.name}"
        return True, ""

    def validate_stage1(self) -> tuple[bool, str]:
        """التحقق من صحة النشاط في المرحلة الأولى (نحتاج الاسم، النسبة، وربط بمخرج واحد على الأقل)"""
        if not self.name:
            return False, "يجب إدخال اسم النشاط"
        if not (0 <= self.percentage <= 100):
            return False, f"النسبة المئوية للنشاط {self.name} يجب أن تكون بين 0 و 100"
        if not self.measures_clos:
            return False, f"يجب ربط النشاط {self.name} بمخرج واحد على الأقل"
        return True, ""

class TableOfSpecifications:
    """جدول المواصفات - Table of Specifications
    يربط الموضوعات بنواتج التعلم وأنشطة التقييم
    """
    
    def __init__(self):
        # بنية: {topic_number: {clo_code: {activity_name: mark}}}
        self.specifications: Dict[int, Dict[str, Dict[str, float]]] = {}
    
    def set_specification(self, topic_number: int, clo_code: str, 
                         activity_name: str, mark: float):
        """تعيين قيمة في جدول المواصفات"""
        if topic_number not in self.specifications:
            self.specifications[topic_number] = {}
        if clo_code not in self.specifications[topic_number]:
            self.specifications[topic_number][clo_code] = {}
        self.specifications[topic_number][clo_code][activity_name] = mark
    
    def get_specification(self, topic_number: int, clo_code: str, 
                         activity_name: str) -> float:
        """الحصول على قيمة من جدول المواصفات"""
        return self.specifications.get(topic_number, {}).get(clo_code, {}).get(activity_name, 0.0)
    
    def get_topic_total_for_activity(self, topic_number: int, activity_name: str) -> float:
        """حساب مجموع درجات موضوع معين لنشاط محدد"""
        total = 0.0
        if topic_number in self.specifications:
            for clo_marks in self.specifications[topic_number].values():
                total += clo_marks.get(activity_name, 0.0)
        return total
    
    def get_clo_total_for_activity(self, clo_code: str, activity_name: str) -> float:
        """حساب مجموع درجات مخرج معين لنشاط محدد"""
        total = 0.0
        for topic_clos in self.specifications.values():
            if clo_code in topic_clos:
                total += topic_clos[clo_code].get(activity_name, 0.0)
        return total
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'specifications': {
                str(topic): {
                    clo: activities
                    for clo, activities in clo_dict.items()
                }
                for topic, clo_dict in self.specifications.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TableOfSpecifications':
        """إنشاء من قاموس"""
        table = cls()
        specs_data = data.get('specifications', {})
        table.specifications = {
            int(topic): clo_dict
            for topic, clo_dict in specs_data.items()
        }
        return table


class SemesterData:
    """بيانات الفصل الدراسي - Semester Data
    يحتوي على معلومات منسق المقرر والمدرسين والمستويات المستهدفة لفصل دراسي محدد
    """

    def __init__(self, academic_year: str, semester: Semester):
        self.academic_year: str = academic_year  # السنة الدراسية
        self.semester: Semester = semester  # الفصل الدراسي
        self.course_coordinator: str = ""  # منسق المقرر للفصل
        self.instructors: List[str] = []  # قائمة مدرسي الشعب
        self.clo_target_levels: Dict[str, float] = {}  # المستويات المستهدفة

    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'academic_year': self.academic_year,
            'semester': self.semester.value if isinstance(self.semester, Semester) else self.semester,
            'course_coordinator': self.course_coordinator,
            'instructors': self.instructors,
            'clo_target_levels': self.clo_target_levels
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SemesterData':
        """إنشاء من قاموس"""
        semester_value = data.get('semester', 'First')
        semester = Semester(semester_value) if isinstance(semester_value, str) else semester_value

        semester_data = cls(
            academic_year=data.get('academic_year', ''),
            semester=semester
        )
        semester_data.course_coordinator = data.get('course_coordinator', '')
        semester_data.instructors = data.get('instructors', [])
        semester_data.clo_target_levels = data.get('clo_target_levels', {})
        return semester_data


class Course:
    """نموذج المقرر الدراسي الكامل - Complete Course Model"""

    def __init__(self, course_id: str):
        self.course_id: str = course_id  # معرف فريد للمقرر
        self.created_date: str = datetime.now().isoformat()
        self.modified_date: str = datetime.now().isoformat()
        self.created_by: str = ""  # Program Manager

        # المكونات الرئيسية
        self.info: CourseInfo = CourseInfo()
        self.clos: List[CLO] = []
        self.topics: List[Topic] = []
        self.activities: List[AssessmentActivity] = []
        self.table_of_specifications: TableOfSpecifications = TableOfSpecifications()

        # المستويات المستهدفة للمخرجات حسب الفصل الدراسي
        # البنية: {academic_year: {semester: {clo_code: target_level}}}
        # مثال: {"1445-1446": {"First": {"K1": 70.0, "K2": 65.0}}}
        self.semester_clo_targets: Dict[str, Dict[str, Dict[str, float]]] = {}

        # بيانات الفصول الدراسية - Semester Data
        # البنية: {academic_year_semester: SemesterData}
        # مثال: {"1445-1446_First": SemesterData(...)}
        self.semester_data: Dict[str, 'SemesterData'] = {}

        # حالة المقرر في النظام
        self.stage_1_completed: bool = False  # مكتمل من Program Manager
        self.stage_1_approved: bool = False  # معتمد من Course Coordinator
        self.stage_2_completed: bool = False  # مكتمل من Course Coordinator
        self.stage_2_approved: bool = False  # معتمد
        self.stage_3_completed: bool = False  # مكتمل من Course Instructor

        # بيانات إضافية
        self.metadata: Dict = {}
    
    def add_clo(self, clo: CLO) -> bool:
        """إضافة ناتج تعلم"""
        # التحقق من عدم تكرار الكود
        if any(c.code == clo.code for c in self.clos):
            return False
        self.clos.append(clo)
        self.update_modified_date()
        return True
    
    def remove_clo(self, clo_code: str) -> bool:
        """حذف ناتج تعلم"""
        self.clos = [c for c in self.clos if c.code != clo_code]
        self.update_modified_date()
        return True
    
    def get_clo(self, clo_code: str) -> Optional[CLO]:
        """الحصول على ناتج تعلم محدد"""
        for clo in self.clos:
            if clo.code == clo_code:
                return clo
        return None
    
    def get_clos_by_category(self, category: CLOCategory) -> List[CLO]:
        """الحصول على نواتج التعلم حسب الفئة"""
        return [c for c in self.clos if c.category == category]
    
    def add_topic(self, topic: Topic) -> bool:
        """إضافة موضوع"""
        # التحقق من عدم تكرار الرقم
        if any(t.number == topic.number for t in self.topics):
            return False
        self.topics.append(topic)
        self.topics.sort(key=lambda t: t.number)
        self.update_modified_date()
        return True
    
    def remove_topic(self, topic_number: int) -> bool:
        """حذف موضوع"""
        self.topics = [t for t in self.topics if t.number != topic_number]
        self.update_modified_date()
        return True
    
    def get_topic(self, topic_number: int) -> Optional[Topic]:
        """الحصول على موضوع محدد"""
        for topic in self.topics:
            if topic.number == topic_number:
                return topic
        return None
    
    def add_activity(self, activity: AssessmentActivity) -> bool:
        """إضافة نشاط تقييم"""
        # التحقق من عدم تكرار الاسم
        if any(a.name == activity.name for a in self.activities):
            return False
        self.activities.append(activity)
        self.update_modified_date()
        return True

    def update_activity(self, old_name: str, new_activity: AssessmentActivity) -> bool:
        """تعديل نشاط تقييم قائم - تحديث باسم ونطاق النشاط مع التحقق من التعارضات."""
        for i, a in enumerate(self.activities):
            if a.name == old_name:
                # إذا تم تغيير الاسم فتأكد من عدم وجود تعارض
                if new_activity.name != old_name and any(x.name == new_activity.name for x in self.activities):
                    return False
                self.activities[i] = new_activity
                self.update_modified_date()
                return True
        return False
    
    def remove_activity(self, activity_name: str) -> bool:
        """حذف نشاط تقييم"""
        self.activities = [a for a in self.activities if a.name != activity_name]
        self.update_modified_date()
        return True
    
    def get_activity(self, activity_name: str) -> Optional[AssessmentActivity]:
        """الحصول على نشاط تقييم محدد"""
        for activity in self.activities:
            if activity.name == activity_name:
                return activity
        return None
    
    def get_semester_target_levels(self, academic_year: str, semester: str) -> Dict[str, float]:
        """الحصول على المستويات المستهدفة لفصل دراسي محدد"""
        if academic_year in self.semester_clo_targets:
            if semester in self.semester_clo_targets[academic_year]:
                return self.semester_clo_targets[academic_year][semester]
        # إرجاع المستويات الافتراضية من المقرر
        return {clo.code: clo.target_level for clo in self.clos}

    def set_semester_target_levels(self, academic_year: str, semester: str, targets: Dict[str, float]):
        """تعيين المستويات المستهدفة لفصل دراسي محدد"""
        if academic_year not in self.semester_clo_targets:
            self.semester_clo_targets[academic_year] = {}
        self.semester_clo_targets[academic_year][semester] = targets
        self.update_modified_date()

    def get_semester_data(self, academic_year: str, semester: str) -> Optional['SemesterData']:
        """الحصول على بيانات فصل دراسي محدد"""
        key = f"{academic_year}_{semester}"
        return self.semester_data.get(key)

    def set_semester_data(self, semester_data: 'SemesterData'):
        """تعيين أو تحديث بيانات فصل دراسي"""
        semester_str = semester_data.semester.value if isinstance(semester_data.semester, Semester) else semester_data.semester
        key = f"{semester_data.academic_year}_{semester_str}"
        self.semester_data[key] = semester_data

        # تحديث المستويات المستهدفة أيضاً
        self.set_semester_target_levels(
            semester_data.academic_year,
            semester_str,
            semester_data.clo_target_levels
        )
        self.update_modified_date()

    def calculate_totals(self) -> Dict[str, float]:
        """حساب المجاميع المختلفة"""
        totals = {
            'total_contact_hours': sum(t.contact_hours for t in self.topics),
            'total_topic_marks': sum(t.mark for t in self.topics),
            'total_activity_marks': sum(a.mark for a in self.activities),
            'total_clo_marks': sum(c.mark for c in self.clos),
            'knowledge_marks': sum(c.mark for c in self.clos if c.category == CLOCategory.KNOWLEDGE),
            'skills_marks': sum(c.mark for c in self.clos if c.category == CLOCategory.SKILLS),
            'values_marks': sum(c.mark for c in self.clos if c.category == CLOCategory.VALUES)
        }
        return totals
    
    def validate_stage1(self) -> tuple[bool, List[str]]:
        """التحقق من صحة بيانات المرحلة الأولى"""
        errors = []
        
        # التحقق من معلومات المقرر (النسخة الخاصة بالمرحلة الأولى)
        is_valid, error = self.info.validate_stage1()
        if not is_valid:
            errors.append(error)
        
        # التحقق من وجود نواتج تعلم
        if not self.clos:
            errors.append("يجب إضافة نواتج تعلم للمقرر")
        
        # التحقق من نواتج التعلم (المرحلة الأولى: تحقق مبسط)
        for clo in self.clos:
            is_valid, error = clo.validate_stage1()
            if not is_valid:
                errors.append(error)
        
        # التحقق من وجود موضوعات
        if not self.topics:
            errors.append("يجب إضافة موضوعات للمقرر")
        
        # التحقق من الموضوعات
        for topic in self.topics:
            is_valid, error = topic.validate()
            if not is_valid:
                errors.append(error)
        
        # التحقق من وجود أنشطة تقييم
        if not self.activities:
            errors.append("يجب إضافة أنشطة تقييم للمقرر")
        
        # التحقق من أنشطة التقييم (المرحلة الأولى: تحقق أن الأنشطة لها نسبة وربط بمخرجات)
        for activity in self.activities:
            is_valid, error = activity.validate_stage1()
            if not is_valid:
                errors.append(error)

        # يجب أن يكون مجموع النسب المئوية للأنشطة = 100
        total_percentage = sum(a.percentage for a in self.activities)
        if abs(total_percentage - 100) > 0.01:
            errors.append(f"مجموع النسب المئوية لأنشطة التقييم يجب أن يساوي 100% (الحالي: {total_percentage}%)")
        
        return len(errors) == 0, errors
    
    def update_modified_date(self):
        """تحديث تاريخ التعديل"""
        self.modified_date = datetime.now().isoformat()
    
    def mark_stage1_completed(self, completed_by: str):
        """تعليم المرحلة الأولى كمكتملة"""
        self.stage_1_completed = True
        self.metadata['stage_1_completed_by'] = completed_by
        self.metadata['stage_1_completed_date'] = datetime.now().isoformat()
        self.update_modified_date()
    
    def mark_stage1_approved(self, approved_by: str):
        """اعتماد المرحلة الأولى"""
        self.stage_1_approved = True
        self.info.is_approved = True
        self.info.approved_by = approved_by
        self.info.approved_date = datetime.now().isoformat()
        self.metadata['stage_1_approved_by'] = approved_by
        self.metadata['stage_1_approved_date'] = datetime.now().isoformat()
        self.update_modified_date()

    def check_stage3_completion(self) -> bool:
        """
        فحص ما إذا كانت المرحلة الثالثة مكتملة

        المرحلة الثالثة تعتبر مكتملة عندما:
        1. يوجد فصل دراسي واحد على الأقل
        2. كل فصل دراسي لديه شعب
        3. كل شعبة لديها طلاب
        4. تم إدخال الدرجات لجميع الطلاب في جميع الأنشطة

        Returns:
            True إذا كانت المرحلة الثالثة مكتملة
        """
        # التحقق من وجود فصول دراسية
        if not self.semester_data:
            return False

        # التحقق من وجود أنشطة
        if not self.activities:
            return False

        # جمع أسماء جميع الأنشطة
        activity_names = [activity.name for activity in self.activities]

        # التحقق من كل فصل دراسي
        has_any_section = False
        for semester_key, semester in self.semester_data.items():
            # استخراج السنة والفصل
            parts = semester_key.split('_')
            if len(parts) != 2:
                continue

            year = parts[0]
            semester_num = '1' if parts[1] == 'First' else '2'

            # البحث عن ملفات الشعب لهذا الفصل
            sections_path = os.path.join('data', 'sections', f'{self.course_id}_*_{year}_{semester_num}.json')
            section_files = glob.glob(sections_path)

            # إذا لم نجد شعب لهذا الفصل، نعتبرها غير مكتملة
            if not section_files:
                return False

            has_any_section = True

            # التحقق من كل ملف شعبة
            for section_file in section_files:
                try:
                    with open(section_file, 'r', encoding='utf-8') as f:
                        section_data = json.load(f)

                    # التحقق من وجود طلاب منتظمين
                    students = section_data.get('students', [])
                    regular_students = [s for s in students if s.get('status') == 'Regular']

                    if not regular_students:
                        # إذا لم يكن هناك طلاب منتظمين، الشعبة تعتبر غير مكتملة
                        return False

                    # التحقق من إدخال درجات الطلاب المنتظمين فقط في جميع الأنشطة
                    for student in regular_students:
                        activity_marks = student.get('activity_marks', {})

                        # التحقق من وجود درجات لجميع الأنشطة
                        for activity_name in activity_names:
                            if activity_name not in activity_marks:
                                return False

                            # التحقق من وجود درجات في النشاط (يجب أن يكون dict غير فارغ)
                            marks = activity_marks[activity_name]
                            if not marks or not isinstance(marks, dict):
                                return False

                            # التحقق من وجود قيم فعلية (ليست None أو فارغة)
                            if not any(v is not None and v != '' for v in marks.values()):
                                return False

                except Exception as e:
                    # في حالة وجود خطأ في قراءة الملف، نعتبر الشعبة غير مكتملة
                    return False

        # إذا لم نجد أي شعب على الإطلاق
        if not has_any_section:
            return False

        return True

    def update_stage3_completion(self):
        """تحديث حالة اكتمال المرحلة الثالثة تلقائياً"""
        self.stage_3_completed = self.check_stage3_completion()
        if self.stage_3_completed and 'stage_3_completed_date' not in self.metadata:
            self.metadata['stage_3_completed_date'] = datetime.now().isoformat()
        self.update_modified_date()
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            'course_id': self.course_id,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'created_by': self.created_by,
            'info': self.info.to_dict(),
            'clos': [clo.to_dict() for clo in self.clos],
            'topics': [topic.to_dict() for topic in self.topics],
            'activities': [activity.to_dict() for activity in self.activities],
            'table_of_specifications': self.table_of_specifications.to_dict(),
            'semester_clo_targets': self.semester_clo_targets,
            'semester_data': {key: sd.to_dict() for key, sd in self.semester_data.items()},
            'stage_1_completed': self.stage_1_completed,
            'stage_1_approved': self.stage_1_approved,
            'stage_2_completed': self.stage_2_completed,
            'stage_2_approved': self.stage_2_approved,
            'stage_3_completed': self.stage_3_completed,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Course':
        """إنشاء من قاموس"""
        course = cls(course_id=data.get('course_id', ''))
        course.created_date = data.get('created_date', course.created_date)
        course.modified_date = data.get('modified_date', course.modified_date)
        course.created_by = data.get('created_by', '')
        
        course.info = CourseInfo.from_dict(data.get('info', {}))
        course.clos = [CLO.from_dict(clo_data) for clo_data in data.get('clos', [])]
        course.topics = [Topic.from_dict(topic_data) for topic_data in data.get('topics', [])]
        course.activities = [AssessmentActivity.from_dict(act_data) 
                           for act_data in data.get('activities', [])]
        course.table_of_specifications = TableOfSpecifications.from_dict(
            data.get('table_of_specifications', {})
        )
        course.semester_clo_targets = data.get('semester_clo_targets', {})

        # تحميل بيانات الفصول الدراسية
        semester_data_dict = data.get('semester_data', {})
        course.semester_data = {
            key: SemesterData.from_dict(sd_data)
            for key, sd_data in semester_data_dict.items()
        }

        course.stage_1_completed = data.get('stage_1_completed', False)
        course.stage_1_approved = data.get('stage_1_approved', False)
        course.stage_2_completed = data.get('stage_2_completed', False)
        course.stage_2_approved = data.get('stage_2_approved', False)
        course.stage_3_completed = data.get('stage_3_completed', False)
        course.metadata = data.get('metadata', {})
        
        return course
    
    def __str__(self):
        return f"Course({self.info.course_code} - {self.info.course_title})"
    
    def __repr__(self):
        return self.__str__()