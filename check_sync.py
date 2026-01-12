"""
التحقق من التزامن بين بيانات الفصل الدراسي والشعب
Check synchronization between semester data and sections
"""

from managers.course_manager import CourseManager
from managers.section_manager import SectionManager

def check_sync():
    cm = CourseManager()
    sm = SectionManager()

    course = cm.load_course("course_20251225_104426")
    if not course:
        print("Course not found")
        return

    print(f"Course: {course.info.course_code}")
    print("="*60)

    semester_data = course.get_semester_data("1447", "First")

    print("\nSemester Data - K1 Target Level:")
    if semester_data and semester_data.clo_target_levels:
        print(f"  {semester_data.clo_target_levels.get('K1', 'N/A')}%")
    else:
        print("  No data")

    sections = sm.get_sections_by_course(course.course_id)

    print(f"\nSections ({len(sections)} total):")
    for section in sections:
        section_semester = section.semester.value if hasattr(section.semester, 'value') else section.semester
        if section.academic_year == "1447" and section_semester == "First":
            k1_level = section.clo_target_levels.get('K1', 'N/A') if section.clo_target_levels else 'Empty'
            print(f"  Section {section.section_number}: K1 = {k1_level}%")

    print("\n" + "="*60)

    if semester_data and semester_data.clo_target_levels:
        semester_k1 = semester_data.clo_target_levels.get('K1')
        all_synced = True

        for section in sections:
            section_semester = section.semester.value if hasattr(section.semester, 'value') else section.semester
            if section.academic_year == "1447" and section_semester == "First":
                section_k1 = section.clo_target_levels.get('K1') if section.clo_target_levels else None
                if section_k1 != semester_k1:
                    all_synced = False
                    print(f"\n[WARNING] Section {section.section_number} is NOT synced!")
                    print(f"  Semester data: {semester_k1}%")
                    print(f"  Section data: {section_k1}%")

        if all_synced:
            print("\n[OK] All sections are synced with semester data!")
        else:
            print("\n[INFO] Run the program and save semester data to auto-sync all sections")

if __name__ == '__main__':
    check_sync()
