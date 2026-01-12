"""
مدير بيانات المقررات
Course Manager
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from models.course import Course, CourseInfo, CLO, Topic, AssessmentActivity, CLOCategory


class CourseManager:
    """مدير عمليات المقررات الدراسية"""
    
    def __init__(self, data_dir: str = "data/courses"):
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """التأكد من وجود مجلد البيانات"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_course_file_path(self, course_id: str) -> str:
        """الحصول على مسار ملف المقرر"""
        return os.path.join(self.data_dir, f"{course_id}.json")
    
    def create_course(self, course_id: str, created_by: str) -> Course:
        """إنشاء مقرر جديد"""
        if self.course_exists(course_id):
            raise ValueError(f"المقرر {course_id} موجود بالفعل")
        
        course = Course(course_id)
        course.created_by = created_by
        self.save_course(course)
        return course
    
    def save_course(self, course: Course) -> bool:
        """حفظ المقرر"""
        try:
            # تحديث حالة اكتمال المرحلة الثالثة تلقائياً
            course.update_stage3_completion()

            course.update_modified_date()
            file_path = self._get_course_file_path(course.course_id)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(course.to_dict(), f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"خطأ في حفظ المقرر: {e}")
            return False
    
    def load_course(self, course_id: str) -> Optional[Course]:
        """تحميل مقرر"""
        try:
            file_path = self._get_course_file_path(course_id)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Course.from_dict(data)
        except Exception as e:
            print(f"خطأ في تحميل المقرر: {e}")
            return None
    
    def course_exists(self, course_id: str) -> bool:
        """التحقق من وجود المقرر"""
        file_path = self._get_course_file_path(course_id)
        return os.path.exists(file_path)
    
    def delete_course(self, course_id: str) -> bool:
        """حذف مقرر"""
        try:
            file_path = self._get_course_file_path(course_id)

            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"خطأ في حذف المقرر: {e}")
            return False

    def delete_course_cascade(self, course_id: str) -> dict:
        """
        حذف مقرر مع حذف المستخدمين المرتبطين

        Args:
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
            if self.delete_course(course_id):
                result['success'] = True
            else:
                result['errors'].append(f"Failed to delete course {course_id}")

        except Exception as e:
            result['errors'].append(f"Error in cascade delete: {str(e)}")

        return result
    
    def list_all_courses(self) -> List[Dict]:
        """الحصول على قائمة بجميع المقررات"""
        courses = []
        
        try:
            if not os.path.exists(self.data_dir):
                return courses
            
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    course_id = filename[:-5]  # إزالة .json
                    course = self.load_course(course_id)
                    
                    if course:
                        # تحديد الحالة
                        status = 'draft'  # افتراضياً
                        if course.stage_1_approved:
                            status = 'approved'
                        elif course.stage_1_completed:
                            status = 'completed'
                        elif course.stage_2_completed:
                            status = 'active'
                        
                        courses.append({
                            'course_id': course.course_id,
                            'course_code': course.info.course_code,
                            'course_title': course.info.course_title,
                            'program': course.info.program,
                            'academic_year': course.info.academic_year,
                            'semester': course.info.semester.value if hasattr(course.info.semester, 'value') else course.info.semester,
                            'created_date': course.created_date,
                            'modified_date': course.modified_date,
                            'stage_1_completed': course.stage_1_completed,
                            'stage_1_approved': course.stage_1_approved,
                            'created_by': course.created_by,
                            'status': status
                        })
            
            # ترتيب حسب تاريخ التعديل
            courses.sort(key=lambda x: x['modified_date'], reverse=True)
            
        except Exception as e:
            print(f"خطأ في قراءة قائمة المقررات: {e}")
        
        return courses
    
    def get_courses_by_program(self, program: str) -> List[Dict]:
        """الحصول على المقررات حسب البرنامج"""
        all_courses = self.list_all_courses()
        return [c for c in all_courses if c['program'] == program]
    
    def get_courses_by_semester(self, academic_year: str, semester: str) -> List[Dict]:
        """الحصول على المقررات حسب الفصل الدراسي"""
        all_courses = self.list_all_courses()
        return [c for c in all_courses 
                if c['academic_year'] == academic_year and c['semester'] == semester]
    
    def get_pending_approval_courses(self) -> List[Dict]:
        """الحصول على المقررات المكتملة بانتظار الاعتماد"""
        all_courses = self.list_all_courses()
        return [c for c in all_courses 
                if c['stage_1_completed'] and not c['stage_1_approved']]
    
    def search_courses(self, search_term: str) -> List[Dict]:
        """البحث عن مقررات"""
        all_courses = self.list_all_courses()
        search_term = search_term.lower()
        
        return [c for c in all_courses 
                if search_term in c['course_code'].lower() 
                or search_term in c['course_title'].lower()
                or search_term in c['program'].lower()]
    
    def update_course_info(self, course_id: str, info: CourseInfo) -> bool:
        """تحديث معلومات المقرر"""
        course = self.load_course(course_id)
        if not course:
            return False
        
        course.info = info
        return self.save_course(course)
    
    def add_clo_to_course(self, course_id: str, clo: CLO) -> bool:
        """إضافة ناتج تعلم لمقرر"""
        course = self.load_course(course_id)
        if not course:
            return False
        
        if not course.add_clo(clo):
            return False
        
        return self.save_course(course)
    
    def remove_clo_from_course(self, course_id: str, clo_code: str) -> bool:
        """حذف ناتج تعلم من مقرر"""
        course = self.load_course(course_id)
        if not course:
            return False
        
        course.remove_clo(clo_code)
        return self.save_course(course)
    
    def add_topic_to_course(self, course_id: str, topic: Topic) -> bool:
        """إضافة موضوع لمقرر"""
        course = self.load_course(course_id)
        if not course:
            return False
        
        if not course.add_topic(topic):
            return False
        
        return self.save_course(course)
    
    def remove_topic_from_course(self, course_id: str, topic_number: int) -> bool:
        """حذف موضوع من مقرر"""
        course = self.load_course(course_id)
        if not course:
            return False
        
        course.remove_topic(topic_number)
        return self.save_course(course)
    
    def add_activity_to_course(self, course_id: str, activity: AssessmentActivity) -> bool:
        """إضافة نشاط تقييم لمقرر"""
        course = self.load_course(course_id)
        if not course:
            return False
        
        if not course.add_activity(activity):
            return False
        
        return self.save_course(course)
    
    def remove_activity_from_course(self, course_id: str, activity_name: str) -> bool:
        """حذف نشاط تقييم من مقرر"""
        course = self.load_course(course_id)
        if not course:
            return False
        
        course.remove_activity(activity_name)
        return self.save_course(course)
    
    def complete_stage1(self, course_id: str, completed_by: str) -> tuple[bool, str]:
        """إكمال المرحلة الأولى"""
        course = self.load_course(course_id)
        if not course:
            return False, "المقرر غير موجود"
        
        # التحقق من صحة البيانات
        is_valid, errors = course.validate_stage1()
        if not is_valid:
            return False, "\n".join(errors)
        
        # تعليم المرحلة كمكتملة
        course.mark_stage1_completed(completed_by)
        
        if self.save_course(course):
            return True, "تم إكمال المرحلة الأولى بنجاح"
        else:
            return False, "خطأ في حفظ البيانات"
    
    def approve_stage1(self, course_id: str, approved_by: str) -> tuple[bool, str]:
        """اعتماد المرحلة الأولى"""
        course = self.load_course(course_id)
        if not course:
            return False, "المقرر غير موجود"
        
        if not course.stage_1_completed:
            return False, "يجب إكمال المرحلة الأولى قبل اعتمادها"
        
        # اعتماد المرحلة
        course.mark_stage1_approved(approved_by)
        
        if self.save_course(course):
            return True, "تم اعتماد المرحلة الأولى بنجاح"
        else:
            return False, "خطأ في حفظ البيانات"
    
    def reject_stage1(self, course_id: str, rejected_by: str, reason: str) -> tuple[bool, str]:
        """رفض اعتماد المرحلة الأولى"""
        course = self.load_course(course_id)
        if not course:
            return False, "المقرر غير موجود"
        
        # إلغاء الإكمال
        course.stage_1_completed = False
        course.metadata['stage_1_rejected_by'] = rejected_by
        course.metadata['stage_1_rejected_date'] = datetime.now().isoformat()
        course.metadata['stage_1_rejection_reason'] = reason
        
        if self.save_course(course):
            return True, "تم رفض المرحلة الأولى"
        else:
            return False, "خطأ في حفظ البيانات"
    
    def get_course_statistics(self, course_id: str) -> Optional[Dict]:
        """الحصول على إحصائيات المقرر"""
        course = self.load_course(course_id)
        if not course:
            return None
        
        totals = course.calculate_totals()
        
        stats = {
            'course_code': course.info.course_code,
            'course_title': course.info.course_title,
            'number_of_clos': len(course.clos),
            'number_of_topics': len(course.topics),
            'number_of_activities': len(course.activities),
            'total_contact_hours': totals['total_contact_hours'],
            'clo_breakdown': {
                'knowledge': {
                    'count': len(course.get_clos_by_category(CLOCategory.KNOWLEDGE)),
                    'marks': totals['knowledge_marks']
                },
                'skills': {
                    'count': len(course.get_clos_by_category(CLOCategory.SKILLS)),
                    'marks': totals['skills_marks']
                },
                'values': {
                    'count': len(course.get_clos_by_category(CLOCategory.VALUES)),
                    'marks': totals['values_marks']
                }
            },
            'stage_status': {
                'stage_1_completed': course.stage_1_completed,
                'stage_1_approved': course.stage_1_approved,
                'stage_2_completed': course.stage_2_completed,
                'stage_2_approved': course.stage_2_approved,
                'stage_3_completed': course.stage_3_completed
            }
        }
        
        return stats
    
    def export_course_to_dict(self, course_id: str) -> Optional[Dict]:
        """تصدير المقرر كقاموس كامل"""
        course = self.load_course(course_id)
        if not course:
            return None
        
        return course.to_dict()
    
    def import_course_from_dict(self, data: Dict, force: bool = False) -> tuple[bool, str]:
        """استيراد مقرر من قاموس"""
        try:
            course = Course.from_dict(data)
            course_id = course.course_id
            
            if self.course_exists(course_id) and not force:
                return False, f"المقرر {course_id} موجود بالفعل. استخدم force=True للكتابة فوقه"
            
            if self.save_course(course):
                return True, "تم استيراد المقرر بنجاح"
            else:
                return False, "خطأ في حفظ المقرر"
                
        except Exception as e:
            return False, f"خطأ في استيراد المقرر: {str(e)}"
