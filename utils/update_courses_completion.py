# -*- coding: utf-8 -*-
"""
أداة تحديث حالة اكتمال المقررات
Updates completion status for all existing courses
"""

import sys
import os

# إضافة المسار الرئيسي
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.course_manager import CourseManager


def update_all_courses_completion():
    """تحديث حالة اكتمال جميع المقررات"""
    course_manager = CourseManager()

    # الحصول على جميع المقررات
    all_courses = course_manager.list_all_courses()

    print(f"Found {len(all_courses)} courses to check...")
    print("=" * 60)

    updated_count = 0
    completed_count = 0

    for course_data in all_courses:
        course_id = course_data['course_id']
        course_code = course_data.get('course_code', 'N/A')

        try:
            # تحميل المقرر
            course = course_manager.load_course(course_id)

            if course:
                # حفظ الحالة القديمة
                old_status = course.stage_3_completed

                # تحديث حالة الاكتمال
                course.update_stage3_completion()

                # حفظ المقرر (بدون استدعاء update_stage3_completion مرة أخرى)
                course.update_modified_date()
                file_path = course_manager._get_course_file_path(course.course_id)

                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(course.to_dict(), f, ensure_ascii=False, indent=2)

                new_status = course.stage_3_completed

                # طباعة النتيجة
                status_icon = "✅" if new_status else "⏳"
                change_text = ""

                if old_status != new_status:
                    updated_count += 1
                    change_text = f" (Changed: {old_status} → {new_status})"

                if new_status:
                    completed_count += 1

                print(f"{status_icon} {course_code} ({course_id}): {new_status}{change_text}")

        except Exception as e:
            print(f"❌ Error processing {course_code} ({course_id}): {str(e)}")

    print("=" * 60)
    print(f"Summary:")
    print(f"  Total courses: {len(all_courses)}")
    print(f"  Completed courses: {completed_count}")
    print(f"  Incomplete courses: {len(all_courses) - completed_count}")
    print(f"  Status updated: {updated_count}")


if __name__ == "__main__":
    # Set UTF-8 encoding for console
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

    print("=" * 60)
    print("Course Completion Status Update Tool")
    print("=" * 60)
    print()

    update_all_courses_completion()

    print()
    print("Done!")
    input("Press Enter to exit...")
