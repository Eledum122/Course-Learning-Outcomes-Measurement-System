"""
وحدة إدارة الصلاحيات
Permissions Management Module

This module provides helper functions for checking and filtering data
based on user roles and permissions.

Roles hierarchy:
1. Admin (مدير النظام): Full access to everything
2. Program Coordinator (منسق البرنامج): Access only to their assigned programs
3. Course Coordinator (منسق المقرر): Access only to their assigned courses and sections
4. Section Instructor (مدرس الشعبة): Access only to their assigned sections
"""

from typing import List, Dict, Optional
from models.database import Database, User, UserRole


class PermissionsHelper:
    """Helper class for managing user permissions"""

    def __init__(self, db: Database, user: User):
        """
        Initialize permissions helper

        Args:
            db: Database instance
            user: Current user object
        """
        self.db = db
        self.user = user
        self._user_data = None

    @property
    def user_data(self) -> Dict:
        """Get fresh user data from database"""
        if self._user_data is None:
            users = self.db.load_users()
            for u in users:
                if u.get('user_id') == self.user.user_id:
                    self._user_data = u
                    break
            if self._user_data is None:
                self._user_data = {}
        return self._user_data

    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.user.role == UserRole.ADMIN

    def is_program_coordinator(self) -> bool:
        """Check if user is program coordinator"""
        return self.user.role == UserRole.PROGRAM_COORDINATOR

    def is_course_coordinator(self) -> bool:
        """Check if user is course coordinator"""
        return self.user.role == UserRole.COURSE_COORDINATOR

    def is_section_instructor(self) -> bool:
        """Check if user is section instructor"""
        return self.user.role == UserRole.SECTION_INSTRUCTOR

    # ═══════════════════════════════════════════════════════════════
    # Programs Permissions
    # ═══════════════════════════════════════════════════════════════

    def get_accessible_programs(self) -> List[Dict]:
        """
        Get list of programs accessible to the user

        Returns:
            List of program dictionaries
        """
        all_programs = self.db.get_all_programs()

        if self.is_admin():
            # Admin can see all programs
            return all_programs

        if self.is_program_coordinator():
            # Program coordinator can see only assigned programs
            assigned_programs = self.user_data.get('assigned_programs', [])
            return [p for p in all_programs if p.get('program_id') in assigned_programs]

        if self.is_course_coordinator():
            # Course coordinator can see programs of their courses
            accessible_courses = self.get_accessible_courses()
            program_ids = set(c.get('program_id') for c in accessible_courses)
            return [p for p in all_programs if p.get('program_id') in program_ids]

        if self.is_section_instructor():
            # Section instructor can see programs of their sections' courses
            accessible_sections = self.get_accessible_sections()
            course_ids = set(s.get('course_id') for s in accessible_sections)
            all_courses = self.db.get_all_courses()
            program_ids = set(c.get('program_id') for c in all_courses if c.get('course_id') in course_ids)
            return [p for p in all_programs if p.get('program_id') in program_ids]

        return []

    def can_access_program(self, program_id: str) -> bool:
        """
        Check if user can access a specific program

        Args:
            program_id: Program ID to check

        Returns:
            True if user can access the program
        """
        accessible_programs = self.get_accessible_programs()
        return any(p.get('program_id') == program_id for p in accessible_programs)

    def can_edit_program(self, program_id: str) -> bool:
        """
        Check if user can edit a specific program

        Args:
            program_id: Program ID to check

        Returns:
            True if user can edit the program
        """
        if self.is_admin():
            return True

        if self.is_program_coordinator():
            assigned_programs = self.user_data.get('assigned_programs', [])
            return program_id in assigned_programs

        return False

    # ═══════════════════════════════════════════════════════════════
    # Courses Permissions
    # ═══════════════════════════════════════════════════════════════

    def get_accessible_courses(self) -> List[Dict]:
        """
        Get list of courses accessible to the user

        Returns:
            List of course dictionaries
        """
        all_courses = self.db.get_all_courses()

        if self.is_admin():
            # Admin can see all courses
            return all_courses

        if self.is_program_coordinator():
            # Program coordinator can see courses in their programs
            assigned_programs = self.user_data.get('assigned_programs', [])
            return [c for c in all_courses if c.get('program_id') in assigned_programs]

        if self.is_course_coordinator():
            # Course coordinator can see their assigned courses
            # or courses where they are the coordinator
            assigned_courses = self.user_data.get('assigned_courses', [])
            return [c for c in all_courses
                   if c.get('course_id') in assigned_courses
                   or c.get('coordinator_id') == self.user.user_id]

        if self.is_section_instructor():
            # Section instructor can see courses where they have sections
            assigned_sections = self.user_data.get('assigned_sections', {})
            course_ids = set(assigned_sections.keys())
            return [c for c in all_courses if c.get('course_id') in course_ids]

        return []

    def can_access_course(self, course_id: str) -> bool:
        """
        Check if user can access a specific course

        Args:
            course_id: Course ID to check

        Returns:
            True if user can access the course
        """
        accessible_courses = self.get_accessible_courses()
        return any(c.get('course_id') == course_id for c in accessible_courses)

    def can_edit_course(self, course_id: str) -> bool:
        """
        Check if user can edit a specific course

        Args:
            course_id: Course ID to check

        Returns:
            True if user can edit the course
        """
        if self.is_admin():
            return True

        if self.is_program_coordinator():
            # Can edit courses in their programs
            course = self.db.get_course_by_id(course_id) if hasattr(self.db, 'get_course_by_id') else None
            if course is None:
                # Fallback: find course manually
                for c in self.db.get_all_courses():
                    if c.get('course_id') == course_id:
                        course = c
                        break
            if course:
                assigned_programs = self.user_data.get('assigned_programs', [])
                return course.get('program_id') in assigned_programs
            return False

        if self.is_course_coordinator():
            assigned_courses = self.user_data.get('assigned_courses', [])
            # Can edit their assigned courses
            if course_id in assigned_courses:
                return True
            # Or if they're the coordinator
            for c in self.db.get_all_courses():
                if c.get('course_id') == course_id and c.get('coordinator_id') == self.user.user_id:
                    return True
            return False

        return False

    # ═══════════════════════════════════════════════════════════════
    # Sections Permissions
    # ═══════════════════════════════════════════════════════════════

    def get_accessible_sections(self) -> List[Dict]:
        """
        Get list of sections accessible to the user

        Returns:
            List of section dictionaries
        """
        # Load sections from file
        import json
        from pathlib import Path
        sections_file = Path(__file__).parent.parent / 'data' / 'sections.json'
        try:
            with open(sections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_sections = data.get('sections', [])
        except:
            all_sections = []

        if self.is_admin():
            # Admin can see all sections
            return all_sections

        if self.is_program_coordinator():
            # Program coordinator can see sections of courses in their programs
            accessible_courses = self.get_accessible_courses()
            course_ids = set(c.get('course_id') for c in accessible_courses)
            return [s for s in all_sections if s.get('course_id') in course_ids]

        if self.is_course_coordinator():
            # Course coordinator can see sections of their courses
            accessible_courses = self.get_accessible_courses()
            course_ids = set(c.get('course_id') for c in accessible_courses)
            return [s for s in all_sections if s.get('course_id') in course_ids]

        if self.is_section_instructor():
            # Section instructor can only see their assigned sections
            assigned_sections = self.user_data.get('assigned_sections', {})
            result = []
            for s in all_sections:
                course_id = s.get('course_id')
                section_number = s.get('section_number')
                if course_id in assigned_sections:
                    if section_number in assigned_sections[course_id]:
                        result.append(s)
            return result

        return []

    def can_access_section(self, course_id: str, section_number: str) -> bool:
        """
        Check if user can access a specific section

        Args:
            course_id: Course ID
            section_number: Section number

        Returns:
            True if user can access the section
        """
        accessible_sections = self.get_accessible_sections()
        return any(s.get('course_id') == course_id and s.get('section_number') == section_number
                  for s in accessible_sections)

    def can_edit_section(self, course_id: str, section_number: str) -> bool:
        """
        Check if user can edit a specific section (enter grades, etc.)

        Args:
            course_id: Course ID
            section_number: Section number

        Returns:
            True if user can edit the section
        """
        if self.is_admin():
            return True

        if self.is_program_coordinator():
            # Can edit sections in their program's courses
            return self.can_access_section(course_id, section_number)

        if self.is_course_coordinator():
            # Can edit sections of their courses
            return self.can_access_section(course_id, section_number)

        if self.is_section_instructor():
            # Can only edit their assigned sections
            assigned_sections = self.user_data.get('assigned_sections', {})
            if course_id in assigned_sections:
                return section_number in assigned_sections[course_id]
            return False

        return False

    # ═══════════════════════════════════════════════════════════════
    # Helper Methods for Filtering
    # ═══════════════════════════════════════════════════════════════

    def filter_programs(self, programs: List[Dict]) -> List[Dict]:
        """Filter list of programs based on user permissions"""
        if self.is_admin():
            return programs

        accessible_ids = set(p.get('program_id') for p in self.get_accessible_programs())
        return [p for p in programs if p.get('program_id') in accessible_ids]

    def filter_courses(self, courses: List[Dict]) -> List[Dict]:
        """Filter list of courses based on user permissions"""
        if self.is_admin():
            return courses

        accessible_ids = set(c.get('course_id') for c in self.get_accessible_courses())
        return [c for c in courses if c.get('course_id') in accessible_ids]

    def filter_sections(self, sections: List[Dict]) -> List[Dict]:
        """Filter list of sections based on user permissions"""
        if self.is_admin():
            return sections

        accessible = self.get_accessible_sections()
        result = []
        for s in sections:
            for a in accessible:
                if (s.get('course_id') == a.get('course_id') and
                    s.get('section_number') == a.get('section_number')):
                    result.append(s)
                    break
        return result

    # ═══════════════════════════════════════════════════════════════
    # Display Role Information
    # ═══════════════════════════════════════════════════════════════

    def get_role_display_name(self, lang: str = 'ar') -> str:
        """Get display name for user's role"""
        role_names = {
            UserRole.ADMIN: {'ar': 'مدير النظام', 'en': 'System Admin'},
            UserRole.PROGRAM_COORDINATOR: {'ar': 'منسق البرنامج', 'en': 'Program Coordinator'},
            UserRole.COURSE_COORDINATOR: {'ar': 'منسق المقرر', 'en': 'Course Coordinator'},
            UserRole.SECTION_INSTRUCTOR: {'ar': 'مدرس الشعبة', 'en': 'Section Instructor'},
        }
        return role_names.get(self.user.role, {}).get(lang, 'Unknown')

    def get_permissions_summary(self, lang: str = 'ar') -> Dict:
        """Get summary of user's permissions"""
        programs = self.get_accessible_programs()
        courses = self.get_accessible_courses()
        sections = self.get_accessible_sections()

        return {
            'role': self.get_role_display_name(lang),
            'programs_count': len(programs),
            'courses_count': len(courses),
            'sections_count': len(sections),
            'can_manage_users': self.is_admin(),
            'can_manage_programs': self.is_admin() or self.is_program_coordinator(),
            'can_manage_courses': self.is_admin() or self.is_program_coordinator() or self.is_course_coordinator(),
            'can_enter_grades': True,  # All roles can enter grades for their sections
        }


def get_permissions_helper(db: Database, user: User) -> PermissionsHelper:
    """
    Factory function to create a PermissionsHelper instance

    Args:
        db: Database instance
        user: Current user object

    Returns:
        PermissionsHelper instance
    """
    return PermissionsHelper(db, user)
