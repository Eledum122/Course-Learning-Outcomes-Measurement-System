"""
مكونات واجهة المستخدم المحسّنة
Enhanced UI Widgets and Components
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# إضافة المسار الأساسي
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import COLORS, FONTS
from assets.icons import get_icon, format_with_icon


class EnhancedButton(tk.Button):
    """زر محسّن مع تأثيرات بصرية"""
    
    def __init__(self, parent, text="", icon=None, command=None, 
                 style='primary', width=None, **kwargs):
        """
        إنشاء زر محسّن
        
        Args:
            parent: الحاوية الأب
            text: نص الزر
            icon: اسم الأيقونة
            command: الأمر المنفذ
            style: نمط الزر (primary, secondary, success, danger, warning, info)
            width: العرض
        """
        # إضافة الأيقونة إلى النص إذا وجدت
        if icon:
            text = format_with_icon(text, icon)
        
        # تحديد الألوان حسب النمط
        style_colors = {
            'primary': {
                'bg': COLORS['btn_primary'],
                'hover': COLORS['btn_primary_hover'],
                'fg': COLORS['text_white']
            },
            'secondary': {
                'bg': COLORS['btn_secondary'],
                'hover': COLORS['btn_secondary_hover'],
                'fg': COLORS['text_primary']
            },
            'success': {
                'bg': COLORS['btn_success'],
                'hover': '#32CD32',
                'fg': COLORS['text_white']
            },
            'danger': {
                'bg': COLORS['btn_danger'],
                'hover': '#E85D6A',
                'fg': COLORS['text_white']
            },
            'warning': {
                'bg': COLORS['text_warning'],
                'hover': '#FFD54F',
                'fg': COLORS['text_primary']
            },
            'info': {
                'bg': COLORS['btn_info'],
                'hover': '#3FB8CE',
                'fg': COLORS['text_white']
            },
        }
        
        colors = style_colors.get(style, style_colors['primary'])
        
        # الإعدادات الافتراضية
        default_kwargs = {
            'bg': colors['bg'],
            'fg': colors['fg'],
            'font': FONTS['arabic_main'],
            'relief': tk.FLAT,
            'cursor': 'hand2',
            'padx': 20,
            'pady': 10,
            'borderwidth': 0,
        }
        
        # دمج الإعدادات المخصصة
        default_kwargs.update(kwargs)
        
        if width:
            default_kwargs['width'] = width
        
        # إنشاء الزر
        super().__init__(parent, text=text, command=command, **default_kwargs)
        
        # حفظ الألوان للاستخدام في التأثيرات
        self.normal_bg = colors['bg']
        self.hover_bg = colors['hover']
        
        # ربط الأحداث
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
    
    def _on_enter(self, event):
        """عند تمرير الفأرة"""
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """عند خروج الفأرة"""
        self.config(bg=self.normal_bg)
    
    def _on_press(self, event):
        """عند الضغط"""
        self.config(relief=tk.SUNKEN)
    
    def _on_release(self, event):
        """عند الإفلات"""
        self.config(relief=tk.FLAT)


class IconButton(tk.Button):
    """زر أيقونة فقط"""
    
    def __init__(self, parent, icon_name, command=None, tooltip=None, 
                 size=24, **kwargs):
        """
        إنشاء زر أيقونة
        
        Args:
            parent: الحاوية الأب
            icon_name: اسم الأيقونة
            command: الأمر المنفذ
            tooltip: نص التلميح
            size: حجم الزر
        """
        icon = get_icon(icon_name, '')
        
        default_kwargs = {
            'text': icon,
            'bg': COLORS['bg_main'],
            'fg': COLORS['text_primary'],
            'font': ('Arial', size),
            'relief': tk.FLAT,
            'cursor': 'hand2',
            'borderwidth': 0,
            'padx': 5,
            'pady': 5,
        }
        
        default_kwargs.update(kwargs)
        
        super().__init__(parent, command=command, **default_kwargs)
        
        # تأثيرات بصرية
        self.bind('<Enter>', lambda e: self.config(bg=COLORS['bg_secondary']))
        self.bind('<Leave>', lambda e: self.config(bg=COLORS['bg_main']))
        
        # إضافة تلميح إذا وجد
        if tooltip:
            self.tooltip = ToolTip(self, tooltip)


class CardFrame(tk.Frame):
    """إطار بشكل بطاقة مع ظل"""
    
    def __init__(self, parent, title=None, title_icon=None, **kwargs):
        """
        إنشاء إطار بطاقة
        
        Args:
            parent: الحاوية الأب
            title: عنوان البطاقة
            title_icon: أيقونة العنوان
        """
        # الإعدادات الافتراضية
        default_kwargs = {
            'bg': COLORS['bg_main'],
            'relief': tk.RAISED,
            'borderwidth': 1,
            'highlightbackground': COLORS['border_light'],
            'highlightthickness': 1,
        }
        
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)
        
        # إضافة عنوان إذا وجد
        if title:
            title_text = title
            if title_icon:
                title_text = format_with_icon(title, title_icon)
            
            title_label = tk.Label(
                self,
                text=title_text,
                bg=COLORS['bg_header'],
                fg=COLORS['text_white'],
                font=FONTS['arabic_header'],
                pady=10,
                padx=15
            )
            title_label.pack(side=tk.TOP, fill=tk.X)
            
            # إطار المحتوى
            self.content_frame = tk.Frame(
                self,
                bg=COLORS['bg_main'],
                padx=15,
                pady=15
            )
            self.content_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.content_frame = self


class InfoLabel(tk.Label):
    """تسمية معلومات مع أيقونة"""
    
    def __init__(self, parent, text="", icon=None, icon_type='info', **kwargs):
        """
        إنشاء تسمية معلومات
        
        Args:
            parent: الحاوية الأب
            text: النص
            icon: اسم الأيقونة المخصصة
            icon_type: نوع الأيقونة (info, success, warning, error)
        """
        # تحديد الأيقونة
        if icon is None:
            icon_map = {
                'info': 'info',
                'success': 'success',
                'warning': 'warning',
                'error': 'error'
            }
            icon = icon_map.get(icon_type, 'info')
        
        # تنسيق النص
        formatted_text = format_with_icon(text, icon)
        
        # تحديد اللون
        color_map = {
            'info': COLORS['btn_info'],
            'success': COLORS['btn_success'],
            'warning': COLORS['text_warning'],
            'error': COLORS['btn_danger']
        }
        
        fg_color = color_map.get(icon_type, COLORS['text_primary'])
        
        default_kwargs = {
            'text': formatted_text,
            'bg': COLORS['bg_main'],
            'fg': fg_color,
            'font': FONTS['arabic_main'],
            'anchor': tk.W,
            'justify': tk.LEFT,
        }
        
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)


class StatusBadge(tk.Label):
    """شارة الحالة"""
    
    def __init__(self, parent, status='active', **kwargs):
        """
        إنشاء شارة حالة
        
        Args:
            parent: الحاوية الأب
            status: الحالة (draft, active, completed, locked, approved, pending)
        """
        # تحديد النص والألوان حسب الحالة
        status_config = {
            'draft': {
                'text': 'مسودة',
                'icon': 'draft',
                'bg': COLORS['status_draft'],
            },
            'active': {
                'text': 'نشط',
                'icon': 'active',
                'bg': COLORS['status_active'],
            },
            'completed': {
                'text': 'مكتمل',
                'icon': 'completed',
                'bg': COLORS['status_completed'],
            },
            'locked': {
                'text': 'مغلق',
                'icon': 'locked',
                'bg': COLORS['status_locked'],
            },
            'approved': {
                'text': 'معتمد',
                'icon': 'approved',
                'bg': COLORS['status_approved'],
            },
            'pending': {
                'text': 'قيد الانتظار',
                'icon': 'pending',
                'bg': COLORS['text_warning'],
            }
        }
        
        config = status_config.get(status, status_config['active'])
        text = format_with_icon(config['text'], config['icon'])
        
        default_kwargs = {
            'text': text,
            'bg': config['bg'],
            'fg': COLORS['text_white'],
            'font': FONTS['arabic_small'],
            'padx': 10,
            'pady': 5,
            'relief': tk.FLAT,
        }
        
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)


class ToolTip:
    """تلميح أداة"""
    
    def __init__(self, widget, text):
        """
        إنشاء تلميح
        
        Args:
            widget: الأداة
            text: نص التلميح
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        # ربط الأحداث
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """عرض التلميح"""
        if self.tooltip_window or not self.text:
            return
        
        # إنشاء نافذة التلميح
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tw,
            text=self.text,
            bg='#FFFFDD',
            fg=COLORS['text_primary'],
            font=FONTS['arabic_small'],
            relief=tk.SOLID,
            borderwidth=1,
            padx=8,
            pady=5
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        """إخفاء التلميح"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class SearchEntry(tk.Frame):
    """حقل بحث محسّن"""
    
    def __init__(self, parent, placeholder="بحث...", on_search=None, **kwargs):
        """
        إنشاء حقل بحث
        
        Args:
            parent: الحاوية الأب
            placeholder: النص التوضيحي
            on_search: دالة البحث
        """
        super().__init__(parent, bg=COLORS['bg_main'])
        
        # حقل الإدخال
        self.entry = tk.Entry(
            self,
            font=FONTS['arabic_main'],
            relief=tk.SOLID,
            borderwidth=1,
            **kwargs
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # زر البحث
        search_btn = IconButton(
            self,
            'search',
            command=on_search if on_search else self._on_search
        )
        search_btn.pack(side=tk.LEFT)
        
        # النص التوضيحي
        self.placeholder = placeholder
        self.entry.insert(0, placeholder)
        self.entry.config(fg=COLORS['text_secondary'])
        
        # ربط الأحداث
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<Return>', lambda e: self._on_search())
    
    def _on_focus_in(self, event):
        """عند التركيز على الحقل"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=COLORS['text_primary'])
    
    def _on_focus_out(self, event):
        """عند فقدان التركيز"""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=COLORS['text_secondary'])
    
    def _on_search(self):
        """تنفيذ البحث"""
        search_text = self.get_search_text()
        if search_text:
            print(f"Searching for: {search_text}")
    
    def get_search_text(self):
        """الحصول على نص البحث"""
        text = self.entry.get()
        return text if text != self.placeholder else ""
    
    def clear(self):
        """مسح حقل البحث"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg=COLORS['text_secondary'])


class SectionHeader(tk.Frame):
    """عنوان قسم"""
    
    def __init__(self, parent, text, icon=None, **kwargs):
        """
        إنشاء عنوان قسم
        
        Args:
            parent: الحاوية الأب
            text: النص
            icon: الأيقونة
        """
        super().__init__(parent, bg=COLORS['bg_secondary'], **kwargs)
        
        # تنسيق النص
        if icon:
            text = format_with_icon(text, icon)
        
        # التسمية
        label = tk.Label(
            self,
            text=text,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            font=FONTS['arabic_header'],
            anchor=tk.W,
            padx=15,
            pady=10
        )
        label.pack(fill=tk.X)
        
        # خط فاصل
        separator = tk.Frame(self, bg=COLORS['primary_green'], height=2)
        separator.pack(fill=tk.X)


class Separator(tk.Frame):
    """خط فاصل"""
    
    def __init__(self, parent, orient='horizontal', **kwargs):
        """
        إنشاء خط فاصل
        
        Args:
            parent: الحاوية الأب
            orient: الاتجاه (horizontal, vertical)
        """
        if orient == 'horizontal':
            super().__init__(parent, height=1, bg=COLORS['border_light'], **kwargs)
        else:
            super().__init__(parent, width=1, bg=COLORS['border_light'], **kwargs)
