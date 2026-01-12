"""
سكريبت لتحديث المستويات المستهدفة في جميع الشعب من بيانات الفصل الدراسي
Update CLO target levels in all sections from semester data
"""

from managers.section_manager import SectionManager
from managers.course_manager import CourseManager

def update_all_sections():
    """تحديث المستويات المستهدفة في جميع الشعب"""
    cm = CourseManager()
    sm = SectionManager()

    # الحصول على جميع المقررات
    courses_info = cm.list_all_courses()

    total_sections = 0
    updated_sections = 0

    for course_info in courses_info:
        # تحميل المقرر الكامل
        course = cm.load_course(course_info['course_id'])
        if not course:
            continue
        print(f"\nProcessing course: {course.info.course_code} - {course.info.course_title}")

        # الحصول على جميع شعب هذا المقرر
        sections = sm.get_sections_by_course(course.course_id)

        for section in sections:
            total_sections += 1
            print(f"  Section {section.section_number} ({section.academic_year}, {section.semester.value})")

            # الحصول على بيانات الفصل الدراسي
            semester_data = course.get_semester_data(
                section.academic_year,
                section.semester.value if hasattr(section.semester, 'value') else section.semester
            )

            if semester_data and semester_data.clo_target_levels:
                # تحديث المستويات المستهدفة
                section.clo_target_levels = semester_data.clo_target_levels.copy()
                print(f"    [OK] Updated target levels: {semester_data.clo_target_levels}")
                updated_sections += 1

                # حفظ الشعبة
                if sm.save_section(section):
                    print(f"    [OK] Section saved successfully")
                else:
                    print(f"    [ERROR] Failed to save section")
            else:
                # استخدام المستويات الافتراضية من CLOs
                if course.clos:
                    section.clo_target_levels = {clo.code: clo.target_level for clo in course.clos}
                    print(f"    [INFO] Using default levels from CLOs: {section.clo_target_levels}")
                    updated_sections += 1

                    # حفظ الشعبة
                    if sm.save_section(section):
                        print(f"    [OK] Section saved successfully")
                    else:
                        print(f"    [ERROR] Failed to save section")
                else:
                    print(f"    [WARNING] No semester data and no CLOs found")

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total sections processed: {total_sections}")
    print(f"  Sections updated: {updated_sections}")
    print(f"{'='*60}")

if __name__ == '__main__':
    print("Starting update of CLO target levels in all sections...")
    print("="*60)
    update_all_sections()
    print("\nUpdate completed!")
    input("\nPress Enter to exit...")
