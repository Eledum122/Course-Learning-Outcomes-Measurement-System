"""
ملف الأيقونات والرموز التعبيرية
Icons and Emoji Configuration
"""

# ═══════════════════════════════════════════════════════════════
# الأيقونات الرئيسية / Main Icons
# ═══════════════════════════════════════════════════════════════
ICONS = {
    # أيقونات الملفات
    'new_file': '📄',
    'open_file': '📂',
    'save': '💾',
    'save_all': '💾',
    'close': '✖',
    'print': '🖨',
    'export': '📤',
    'import': '📥',
    
    # أيقونات المقررات
    'course': '📚',
    'new_course': '➕',
    'edit_course': '✏',
    'delete_course': '🗑',
    'course_info': 'ℹ',
    'course_list': '📋',
    
    # أيقونات المراحل
    'stage1': '①',
    'stage2': '②',
    'stage3': '③',
    'stages': '📊',
    
    # أيقونات المستخدمين
    'user': '👤',
    'users': '👥',
    'login': '🔑',
    'logout': '🚪',
    'profile': '👤',
    'permissions': '🔐',
    
    # أيقونات الأدوار
    'program_manager': '👔',
    'course_coordinator': '📊',
    'course_instructor': '👨‍🏫',
    'quality_officer': '✅',
    'admin': '⚙',
    
    # أيقونات الأنشطة
    'clo': '🎯',
    'topic': '📖',
    'activity': '📝',
    'assessment': '✅',
    'exam': '📝',
    'quiz': '❓',
    'assignment': '📄',
    'lab': '🔬',
    'presentation': '🎤',
    
    # أيقونات الطلاب
    'student': '👨‍🎓',
    'students': '👨‍🎓👩‍🎓',
    'grades': '💯',
    'attendance': '📅',
    
    # أيقونات التقارير
    'report': '📊',
    'reports': '📈',
    'chart': '📊',
    'statistics': '📈',
    'analytics': '📉',
    
    # أيقونات الحالة
    'success': '✅',
    'error': '❌',
    'warning': '⚠',
    'info': 'ℹ',
    'question': '❓',
    'check': '✔',
    'cross': '✖',
    
    # أيقونات الإجراءات
    'add': '➕',
    'edit': '✏',
    'delete': '🗑',
    'view': '👁',
    'search': '🔍',
    'filter': '🔽',
    'refresh': '🔄',
    'settings': '⚙',
    'help': '❓',
    
    # أيقونات التنقل
    'home': '🏠',
    'back': '⬅',
    'forward': '➡',
    'up': '⬆',
    'down': '⬇',
    'menu': '☰',
    
    # أيقونات حالة المقرر
    'draft': '📝',
    'active': '✅',
    'completed': '✔',
    'locked': '🔒',
    'approved': '✓',
    'pending': '⏳',
    
    # أيقونات النظام
    'database': '🗄',
    'backup': '💾',
    'restore': '♻',
    'update': '🔄',
    'sync': '🔄',
    'download': '⬇',
    'upload': '⬆',
    
    # أيقونات اللغة
    'language': '🌐',
    'arabic': '🇸🇦',
    'english': '🇬🇧',
    
    # أيقونات الوقت
    'calendar': '📅',
    'clock': '🕐',
    'timer': '⏱',
    'date': '📆',
    
    # أيقونات الجامعة
    'university': '🏛',
    'department': '🏢',
    'faculty': '🎓',
    'program': '📚',
    
    # أيقونات متنوعة
    'star': '⭐',
    'favorite': '💛',
    'notification': '🔔',
    'mail': '✉',
    'phone': '📞',
    'location': '📍',
    'link': '🔗',
    'attachment': '📎',
    'folder': '📁',
    'document': '📄',
    'image': '🖼',
    'video': '🎬',
}

# ═══════════════════════════════════════════════════════════════
# الرموز الخاصة بالأزرار / Button Symbols
# ═══════════════════════════════════════════════════════════════
BUTTON_SYMBOLS = {
    'primary': '▶',
    'secondary': '◀',
    'success': '✓',
    'danger': '✗',
    'warning': '!',
    'info': 'ℹ',
}

# ═══════════════════════════════════════════════════════════════
# الألوان المرتبطة بالأيقونات / Icon Colors
# ═══════════════════════════════════════════════════════════════
ICON_COLORS = {
    'success': '#28A745',
    'error': '#DC3545',
    'warning': '#FFC107',
    'info': '#17A2B8',
    'primary': '#2D5F3F',
    'secondary': '#D4AF37',
}


def get_icon(name, fallback=''):
    """
    الحصول على أيقونة حسب الاسم
    Get icon by name
    
    Args:
        name: اسم الأيقونة
        fallback: القيمة الافتراضية إذا لم توجد الأيقونة
        
    Returns:
        str: الأيقونة أو القيمة الافتراضية
    """
    return ICONS.get(name, fallback)


def get_button_symbol(button_type='primary'):
    """
    الحصول على رمز الزر
    Get button symbol
    
    Args:
        button_type: نوع الزر
        
    Returns:
        str: رمز الزر
    """
    return BUTTON_SYMBOLS.get(button_type, '')


def format_with_icon(text, icon_name):
    """
    تنسيق النص مع الأيقونة
    Format text with icon
    
    Args:
        text: النص
        icon_name: اسم الأيقونة
        
    Returns:
        str: النص المنسق
    """
    icon = get_icon(icon_name, '')
    if icon:
        return f"{icon} {text}"
    return text


def get_status_icon(status):
    """
    الحصول على أيقونة الحالة
    Get status icon
    
    Args:
        status: الحالة
        
    Returns:
        str: أيقونة الحالة
    """
    status_icons = {
        'draft': get_icon('draft'),
        'active': get_icon('active'),
        'completed': get_icon('completed'),
        'locked': get_icon('locked'),
        'approved': get_icon('approved'),
        'pending': get_icon('pending'),
    }
    return status_icons.get(status, '')


def get_role_icon(role):
    """
    الحصول على أيقونة الدور
    Get role icon
    
    Args:
        role: الدور
        
    Returns:
        str: أيقونة الدور
    """
    role_icons = {
        'program_manager': get_icon('program_manager'),
        'course_coordinator': get_icon('course_coordinator'),
        'course_instructor': get_icon('course_instructor'),
        'quality_officer': get_icon('quality_officer'),
        'admin': get_icon('admin'),
    }
    return role_icons.get(role, get_icon('user'))


def get_stage_icon(stage_number):
    """
    الحصول على أيقونة المرحلة
    Get stage icon
    
    Args:
        stage_number: رقم المرحلة (1, 2, 3)
        
    Returns:
        str: أيقونة المرحلة
    """
    stage_icons = {
        1: get_icon('stage1'),
        2: get_icon('stage2'),
        3: get_icon('stage3'),
    }
    return stage_icons.get(stage_number, '')
