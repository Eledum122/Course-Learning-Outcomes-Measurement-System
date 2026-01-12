"""
ملف الإعدادات الأساسية للتطبيق
Configuration File for CLOs Measurement System
"""

import os

# ═══════════════════════════════════════════════════════════════
# معلومات التطبيق / Application Information
# ═══════════════════════════════════════════════════════════════
APP_NAME_AR = "نظام قياس مخرجات التعلم للمقررات الدراسية"
APP_NAME_EN = "Course Learning Outcomes Measurement System"
VERSION = "1.0"
AUTHOR = "Hussein Youssef Abdelazim"
INSTITUTION = "University of Tabuk"

# ═══════════════════════════════════════════════════════════════
# ألوان جامعة تبوك / University of Tabuk Colors
# ═══════════════════════════════════════════════════════════════
COLORS = {
    # الألوان الرئيسية
    'primary_green': '#2D5F3F',      # الأخضر الداكن
    'primary_gold': '#D4AF37',       # الذهبي
    'primary_blue': '#1976D2',       # الأزرق الأساسي
    'light_green': '#4A8B5C',        # أخضر فاتح
    'light_gold': '#F5E6B3',         # ذهبي فاتح
    
    # ألوان الخلفية
    'bg_main': '#FFFFFF',            # أبيض
    'bg': '#FFFFFF',                 # اسم مختصر لخلفية التطبيق
    'bg_light': '#F5F5F5',           # رمادي فاتح جداً (للواجهات)
    'bg_secondary': '#F5F5F5',       # رمادي فاتح جداً
    'bg_header': '#2D5F3F',          # أخضر داكن للترويسة
    
    # ألوان النصوص
    'text_primary': '#000000',       # أسود
    'text_secondary': '#666666',     # رمادي
    'text_white': '#FFFFFF',         # أبيض
    'text_success': '#28A745',       # أخضر للنجاح
    'text_error': '#DC3545',         # أحمر للخطأ
    'text_warning': '#FFC107',       # برتقالي للتحذير
    
    # ألوان الأزرار
    'btn_primary': '#2D5F3F',        # أخضر
    'btn_primary_hover': '#3D7F4F',  # أخضر أفتح عند التمرير
    'btn_secondary': '#D4AF37',      # ذهبي
    'btn_secondary_hover': '#E5C050', # ذهبي أفتح
    'btn_success': '#28A745',
    'btn_danger': '#DC3545',
    'btn_info': '#17A2B8',

    # ألوان مختصرة للأزرار (للتوافق)
    'primary': '#2D5F3F',            # أخضر
    'secondary': '#D4AF37',          # ذهبي
    'success': '#28A745',            # أخضر للنجاح
    'danger': '#DC3545',             # أحمر للخطر
    'info': '#17A2B8',               # أزرق للمعلومات
    'warning': '#FFC107',            # برتقالي للتحذير
    
    # ألوان الحدود
    'border_light': '#DDDDDD',
    'border_medium': '#CCCCCC',
    'border_dark': '#999999',
    
    # ألوان خاصة بالمراحل
    'stage1_color': '#3498DB',       # أزرق للمرحلة الأولى
    'stage2_color': '#E74C3C',       # أحمر للمرحلة الثانية
    'stage3_color': '#2ECC71',       # أخضر للمرحلة الثالثة
    
    # ألوان حالة البيانات
    'status_draft': '#95A5A6',       # رمادي - مسودة
    'status_active': '#3498DB',      # أزرق - نشط
    'status_completed': '#2ECC71',   # أخضر - مكتمل
    'status_locked': '#E67E22',      # برتقالي - مغلق
    'status_approved': '#27AE60',    # أخضر غامق - معتمد
}

# ═══════════════════════════════════════════════════════════════
# الخطوط / Fonts
# ═══════════════════════════════════════════════════════════════
FONTS = {
    'arabic_main': ('Arial', 12),
    'arabic_header': ('Arial', 16, 'bold'),
    'arabic_title': ('Arial', 20, 'bold'),
    'arabic_small': ('Arial', 10),
    'arabic': ('Arial', 12),
    'arabic_bold': ('Arial', 12, 'bold'),

    'english_main': ('Segoe UI', 11),
    'english_header': ('Segoe UI', 14, 'bold'),
    'english_title': ('Segoe UI', 18, 'bold'),
    'english_small': ('Segoe UI', 9),

    'mixed': ('Arial', 11),          # للنصوص المختلطة
    'normal': ('Arial', 12),
    'bold': ('Arial', 12, 'bold'),
    'header': ('Arial', 16, 'bold'),
    'small': ('Arial', 10),
    'monospace': ('Courier New', 10), # للأكواد
}

# ═══════════════════════════════════════════════════════════════
# المسارات / Paths
# ═══════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
COURSES_DIR = os.path.join(DATA_DIR, 'courses')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
BACKUPS_DIR = os.path.join(DATA_DIR, 'backups')

# إنشاء المجلدات إذا لم تكن موجودة
for directory in [DATA_DIR, COURSES_DIR, LOGS_DIR, REPORTS_DIR, BACKUPS_DIR]:
    os.makedirs(directory, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# إعدادات النافذة / Window Settings
# ═══════════════════════════════════════════════════════════════
WINDOW = {
    'width': 1400,
    'height': 800,
    'min_width': 1200,
    'min_height': 700,
    'title_ar': f"{APP_NAME_AR} - الإصدار {VERSION}",
    'title_en': f"{APP_NAME_EN} - Version {VERSION}",
}

# ═══════════════════════════════════════════════════════════════
# أدوار المستخدمين / User Roles
# ═══════════════════════════════════════════════════════════════
ROLES = {
    'program_manager': {
        'name_ar': 'مدير البرنامج',
        'name_en': 'Program Manager',
        'permissions': [
            'create_course_master',
            'update_course_master',
            'delete_course_master',
            'approve_course_master',
            'view_all_courses',
            'view_all_reports',
            'manage_users'
        ],
        'color': '#8E44AD',
        'icon': '👔'
    },
    'course_coordinator': {
        'name_ar': 'منسق المقرر',
        'name_en': 'Course Coordinator',
        'permissions': [
            'create_measurement_framework',
            'update_measurement_framework',
            'view_course_master',
            'view_all_sections',
            'generate_consolidated_reports'
        ],
        'color': '#E74C3C',
        'icon': '📊'
    },
    'course_instructor': {
        'name_ar': 'أستاذ المقرر',
        'name_en': 'Course Instructor',
        'permissions': [
            'create_section',
            'update_section',
            'delete_own_section',
            'add_students',
            'enter_grades',
            'generate_section_report',
            'view_own_section',
            'view_measurement_framework'
        ],
        'color': '#3498DB',
        'icon': '👨‍🏫'
    },
    'department_head': {
        'name_ar': 'رئيس القسم',
        'name_en': 'Department Head',
        'permissions': [
            'view_all_courses',
            'view_all_sections',
            'view_all_reports',
            'approve_course_master'
        ],
        'color': '#16A085',
        'icon': '👤'
    },
    'admin': {
        'name_ar': 'مدير النظام',
        'name_en': 'System Administrator',
        'permissions': ['*'],  # جميع الصلاحيات
        'color': '#C0392B',
        'icon': '⚙️'
    }
}

# ═══════════════════════════════════════════════════════════════
# حالات المراحل / Stage Statuses
# ═══════════════════════════════════════════════════════════════
STAGE_STATUSES = {
    'draft': {
        'name_ar': 'مسودة',
        'name_en': 'Draft',
        'color': COLORS['status_draft']
    },
    'active': {
        'name_ar': 'نشط',
        'name_en': 'Active',
        'color': COLORS['status_active']
    },
    'completed': {
        'name_ar': 'مكتمل',
        'name_en': 'Completed',
        'color': COLORS['status_completed']
    },
    'locked': {
        'name_ar': 'مغلق',
        'name_en': 'Locked',
        'color': COLORS['status_locked']
    },
    'approved': {
        'name_ar': 'معتمد',
        'name_en': 'Approved',
        'color': COLORS['status_approved']
    }
}

# ═══════════════════════════════════════════════════════════════
# إعدادات قاعدة البيانات / Database Settings
# ═══════════════════════════════════════════════════════════════
DB_CONFIG = {
    'type': 'json',  # يمكن تغييرها لاحقاً إلى sqlite أو mysql
    'auto_backup': True,
    'backup_interval': 24,  # ساعات
    'max_backups': 30,      # عدد النسخ الاحتياطية
}

# ═══════════════════════════════════════════════════════════════
# إعدادات التحقق / Validation Settings
# ═══════════════════════════════════════════════════════════════
VALIDATION = {
    'max_clos_knowledge': 10,
    'max_clos_skills': 10,
    'max_clos_values': 10,
    'max_topics': 20,
    'max_activities': 15,
    'total_marks': 100,
    'max_students_per_section': 200,
    'min_criterion_success': 50,
    'max_criterion_success': 100,
    'min_target_level': 50,
    'max_target_level': 100,
}

# ═══════════════════════════════════════════════════════════════
# الإعدادات الافتراضية للمقرر / Default Course Settings
# ═══════════════════════════════════════════════════════════════
DEFAULTS = {
    'criterion_for_success': 60,    # معيار النجاح الافتراضي
    'target_level': 70,             # المستوى المستهدف الافتراضي
    'semester_weeks': 15,           # عدد أسابيع الفصل
    'contact_hours_per_week': 3,    # ساعات الاتصال الأسبوعية
}

# ═══════════════════════════════════════════════════════════════
# إعدادات التقارير / Report Settings
# ═══════════════════════════════════════════════════════════════
REPORT_CONFIG = {
    'formats': ['pdf', 'excel', 'word'],
    'default_format': 'pdf',
    'include_charts': True,
    'include_statistics': True,
    'include_recommendations': True,
}

# ═══════════════════════════════════════════════════════════════
# دالة للحصول على اللون حسب الحالة
# ═══════════════════════════════════════════════════════════════
def get_status_color(status):
    """الحصول على لون الحالة"""
    return STAGE_STATUSES.get(status, {}).get('color', COLORS['text_secondary'])

def get_role_color(role):
    """الحصول على لون الدور"""
    return ROLES.get(role, {}).get('color', COLORS['text_secondary'])

def get_role_icon(role):
    """الحصول على أيقونة الدور"""
    return ROLES.get(role, {}).get('icon', '👤')

# ═══════════════════════════════════════════════════════════════
# إعدادات السجلات / Logging Settings
# ═══════════════════════════════════════════════════════════════
LOGGING = {
    'enabled': True,
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'file': os.path.join(LOGS_DIR, 'app.log'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
}

# ═══════════════════════════════════════════════════════════════
# اللغة الافتراضية / Default Language
# ═══════════════════════════════════════════════════════════════
DEFAULT_LANGUAGE = 'en'  # 'ar' or 'en'
