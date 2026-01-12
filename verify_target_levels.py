"""
سكريبت للتحقق من المستويات المستهدفة في التقرير
Verify target levels in report
"""

from managers.section_manager import SectionManager
from managers.course_manager import CourseManager

def verify_target_levels():
    """التحقق من المستويات المستهدفة"""
    sm = SectionManager()
    cm = CourseManager()

    # تحميل جميع الشعب
    sections = sm.get_all_sections()

    if not sections:
        print("No sections found")
        return

    print(f"Found {len(sections)} sections\n")
    print("="*60)

    for section in sections:
        if not section:
            continue

        # تحميل المقرر
        course = cm.load_course(section.course_id)
        if not course:
            continue

        print(f"\nCourse: {course.info.course_code} - {course.info.course_title}")
        print(f"Section: {section.section_number} ({section.academic_year}, {section.semester.value if hasattr(section.semester, 'value') else section.semester})")

        # عرض المستويات المستهدفة من الشعبة
        print(f"\nTarget levels in section.clo_target_levels:")
        if section.clo_target_levels:
            for clo_code, target in section.clo_target_levels.items():
                print(f"  {clo_code}: {target}%")
        else:
            print("  (empty)")

        # عرض المستويات المستهدفة من بيانات الفصل الدراسي
        semester_data = course.get_semester_data(
            section.academic_year,
            section.semester.value if hasattr(section.semester, 'value') else section.semester
        )

        print(f"\nTarget levels in semester_data:")
        if semester_data and semester_data.clo_target_levels:
            for clo_code, target in semester_data.clo_target_levels.items():
                print(f"  {clo_code}: {target}%")
        else:
            print("  (no semester data)")

        # عرض المستويات الافتراضية من CLOs
        print(f"\nDefault levels from CLOs:")
        if course.clos:
            for clo in course.clos:
                print(f"  {clo.code}: {clo.target_level}%")
        else:
            print("  (no CLOs)")

        print("="*60)

if __name__ == '__main__':
    print("Verifying CLO target levels...")
    print("="*60)
    verify_target_levels()
    print("\nVerification completed!")
