"""
نماذج البيانات
Data Models
"""

from models.user import User
from models.course import (
    Course, CourseInfo, CLO, Topic, AssessmentActivity,
    TableOfSpecifications, Semester, CLOCategory
)
from models.course_section import CourseSection, Student, StudentStatus

__all__ = [
    'User',
    'Course',
    'CourseInfo',
    'CLO',
    'Topic',
    'AssessmentActivity',
    'TableOfSpecifications',
    'Semester',
    'CLOCategory',
    'CourseSection',
    'Student',
    'StudentStatus'
]
