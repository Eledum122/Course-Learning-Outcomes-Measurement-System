"""
فحص بنية activity_marks
Debug activity marks structure
"""

from managers.course_manager import CourseManager
from managers.section_manager import SectionManager

def debug_marks():
    cm = CourseManager()
    sm = SectionManager()

    course = cm.load_course("course_20251225_104426")
    sections = sm.get_sections_by_course(course.course_id)

    section = sections[0]
    print(f"Section: {section.section_number}")
    print(f"Students: {len(section.students)}\n")

    for student in section.students[:1]:  # أول طالب فقط
        print(f"Student: {student.name}")
        print(f"Student ID: {student.student_id}")
        print(f"\nActivity Marks:")
        print(f"Type: {type(student.activity_marks)}")
        print(f"Content: {student.activity_marks}")

        for key, value in student.activity_marks.items():
            print(f"  {key}: {value} (type: {type(value)})")

if __name__ == '__main__':
    debug_marks()
