"""
مولد تقرير لوحة البيانات - Dashboard Report Generator
ينشئ ملف PDF يحتوي على مقاييس إحصائية ورسومات بيانية لنتائج الطلاب ونواتج التعلم
"""

import os
import io
from datetime import datetime
from typing import Dict, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from bidi.algorithm import get_display
import arabic_reshaper

from models import Course, CourseSection, Student, CLO
from translations import t
from utils.report_utils import add_report_header, add_page_number_first, add_page_number_with_watermark


class DashboardReportGenerator:
    """مولد تقرير لوحة البيانات"""

    # ألوان جذابة واحترافية
    COLOR_SCHEME = {
        'primary': '#2196F3',      # أزرق
        'success': '#4CAF50',      # أخضر
        'warning': '#FF9800',      # برتقالي
        'danger': '#F44336',       # أحمر
        'purple': '#9C27B0',       # بنفسجي
        'teal': '#009688',         # تركواز
        'indigo': '#3F51B5',       # نيلي
        'pink': '#E91E63',         # وردي
        'light_blue': '#03A9F4',   # أزرق فاتح
        'lime': '#CDDC39',         # ليموني
    }

    def __init__(self, course: Course, section: CourseSection, language: str = 'ar'):
        self.course = course
        self.section = section
        self.language = language
        self.is_rtl = (language == 'ar')

        self._register_fonts()
        self.styles = self._create_styles()
        self._calculate_all_statistics()
        self._configure_matplotlib()

    def _register_fonts(self):
        """تسجيل الخطوط العربية"""
        try:
            font_path = os.path.join('fonts', 'Tajawal-Regular.ttf')
            font_bold_path = os.path.join('fonts', 'Tajawal-Bold.ttf')

            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
            if os.path.exists(font_bold_path):
                pdfmetrics.registerFont(TTFont('Arabic-Bold', font_bold_path))
        except Exception as e:
            print(f"Error registering fonts: {e}")

    def _configure_matplotlib(self):
        """تكوين matplotlib للخطوط العربية"""
        try:
            font_path = os.path.join('fonts', 'Tajawal-Regular.ttf')
            if os.path.exists(font_path):
                font_prop = font_manager.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = font_prop.get_name()
        except Exception as e:
            print(f"Error configuring matplotlib: {e}")

    def _create_styles(self):
        """إنشاء أنماط النصوص"""
        styles = getSampleStyleSheet()

        style_definitions = [
            ('DashboardTitle', 'Arabic-Bold', 20, TA_CENTER, self.COLOR_SCHEME['primary'], 18, 24),
            ('DashboardHeading', 'Arabic-Bold', 14, TA_CENTER, self.COLOR_SCHEME['indigo'], 10, 18),
            ('DashboardNormal', 'Arabic', 10, TA_CENTER, None, 0, 14),
            ('KPI', 'Arabic-Bold', 22, TA_CENTER, self.COLOR_SCHEME['primary'], 0, 28),
            ('KPILabel', 'Arabic', 9, TA_CENTER, colors.HexColor('#555555'), 0, 12),
        ]

        for name, font, size, align, color, space_after, leading in style_definitions:
            if name not in styles:
                style_params = {
                    'name': name,
                    'fontName': font,
                    'fontSize': size,
                    'alignment': align,
                    'leading': leading
                }
                if color:
                    style_params['textColor'] = colors.HexColor(color) if isinstance(color, str) else color
                if space_after:
                    style_params['spaceAfter'] = space_after
                styles.add(ParagraphStyle(**style_params))

        return styles

    def _reshape_text(self, text):
        """إعادة تشكيل النص العربي"""
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        except:
            return text

    def _get_grade_from_percentage(self, percentage):
        """تحويل النسبة المئوية إلى تقدير"""
        if percentage >= 95: return 'A+'
        elif percentage >= 90: return 'A'
        elif percentage >= 85: return 'B+'
        elif percentage >= 80: return 'B'
        elif percentage >= 75: return 'C+'
        elif percentage >= 70: return 'C'
        elif percentage >= 65: return 'D+'
        elif percentage >= 60: return 'D'
        else: return 'F'

    def _calculate_all_statistics(self):
        """حساب جميع الإحصائيات"""
        from models.course import CLOCategory

        # إحصائيات الطلاب
        self.total_students = len(self.section.students)
        self.regular_students = [s for s in self.section.students if s.status.value == "Regular"]
        self.regular_count = len(self.regular_students)
        self.dropped_students = len([s for s in self.section.students if s.status.value == "Dropped"])
        self.prohibited_students = len([s for s in self.section.students if s.status.value == "Prohibited"])
        self.incomplete_students = len([s for s in self.section.students if s.status.value == "Incomplete"])

        # توزيع التقديرات
        self.grade_distribution = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D+': 0, 'D': 0, 'F': 0}
        self.passed_students = 0
        self.failed_students = 0
        self.student_marks = []

        for student in self.regular_students:
            percentage = (student.total_mark / self.course.info.total_mark) * 100 if self.course.info.total_mark > 0 else 0
            grade = self._get_grade_from_percentage(percentage)
            self.grade_distribution[grade] += 1
            self.student_marks.append(student.total_mark)
            if student.passed:
                self.passed_students += 1
            else:
                self.failed_students += 1

        # إحصائيات وصفية
        if self.student_marks:
            self.average_mark = np.mean(self.student_marks)
            self.median_mark = np.median(self.student_marks)
            self.std_dev = np.std(self.student_marks)
            self.min_mark = np.min(self.student_marks)
            self.max_mark = np.max(self.student_marks)
            self.pass_rate = (self.passed_students / self.regular_count * 100) if self.regular_count > 0 else 0
        else:
            self.average_mark = self.median_mark = self.std_dev = self.min_mark = self.max_mark = self.pass_rate = 0

        # حساب إحصائيات المخرجات
        self.clo_results = {}
        for clo in self.course.clos:
            target_level = self.section.clo_target_levels.get(clo.code, clo.target_level)
            total_clo_mark = 0

            if hasattr(self.course, 'topics') and self.course.topics:
                for topic in self.course.topics:
                    if hasattr(topic, 'specifications_table') and topic.specifications_table:
                        for key, mark in topic.specifications_table.items():
                            parts = key.split('|')
                            if len(parts) == 2 and parts[0] == clo.code:
                                total_clo_mark += mark

            if not self.regular_students or total_clo_mark == 0:
                actual_level = 0
                achieved_count = 0
            else:
                criterion_percentage = clo.criterion_for_success if hasattr(clo, 'criterion_for_success') else 60.0
                threshold_mark = total_clo_mark * (criterion_percentage / 100.0)
                achieved_count = sum(1 for s in self.regular_students if s.clo_marks.get(clo.code, 0) >= threshold_mark)
                actual_level = (achieved_count / self.regular_count) * 100

            self.clo_results[clo.code] = {
                'clo': clo,
                'target_level': target_level,
                'actual_level': actual_level,
                'achieved': actual_level >= target_level,
                'total_mark': total_clo_mark,
                'achieved_count': achieved_count
            }

        achieved_clos = sum(1 for result in self.clo_results.values() if result['achieved'])
        total_clos = len(self.clo_results)
        self.clo_achievement_rate = (achieved_clos / total_clos * 100) if total_clos > 0 else 0

    def _create_gauge_chart(self, actual_value, target_value, title):
        """إنشاء مخطط عداد (Gauge Chart) احترافي على شكل نصف دائرة"""
        fig, ax = plt.subplots(figsize=(6, 4.5), subplot_kw={'projection': 'polar'})
        fig.patch.set_facecolor('white')

        actual_percentage = actual_value
        target_percentage = target_value

        # رسم المناطق الملونة الثلاث بألوان أكثر تباينا
        # المنطقة الحمراء (0-50%)
        red_angles = np.linspace(0, np.pi * 0.5, 100)
        ax.fill_between(red_angles, 0.6, 1, color='#DC3545', alpha=0.9)

        # المنطقة الصفراء (50-75%)
        yellow_angles = np.linspace(np.pi * 0.5, np.pi * 0.75, 100)
        ax.fill_between(yellow_angles, 0.6, 1, color='#FFC107', alpha=0.9)

        # المنطقة الخضراء (75-100%)
        green_angles = np.linspace(np.pi * 0.75, np.pi, 100)
        ax.fill_between(green_angles, 0.6, 1, color='#28A745', alpha=0.9)

        # رسم دائرة بيضاء في المنتصف لعمل شكل دونات
        white_angles = np.linspace(0, np.pi, 100)
        ax.fill_between(white_angles, 0, 0.55, color='white')

        # حساب الزوايا
        actual_angle = (actual_percentage / 100) * np.pi
        target_angle = (target_percentage / 100) * np.pi

        # رسم مؤشر الهدف (Target) - خط برتقالي سميك متقطع
        r_target = [0.55, 1.05]
        theta_target = [target_angle, target_angle]
        ax.plot(theta_target, r_target, color='#FF6F00', linewidth=5,
                linestyle='--', zorder=12, alpha=0.9)
        # مثلث للهدف
        ax.plot(target_angle, 1.08, 'v', color='#FF6F00', markersize=14,
                zorder=13, markeredgecolor='white', markeredgewidth=2)

        # رسم مؤشر الفعلي (Actual) - خط أزرق سميك
        r_actual = [0.55, 1.05]
        theta_actual = [actual_angle, actual_angle]
        ax.plot(theta_actual, r_actual, color='#007BFF', linewidth=6,
                zorder=14, solid_capstyle='round', alpha=0.95)
        # دائرة في نهاية المؤشر الفعلي
        ax.plot(actual_angle, 1.08, 'o', color='#007BFF', markersize=16,
                zorder=15, markeredgecolor='white', markeredgewidth=2.5)

        # النصوص - اسم المخرج
        ax.text(np.pi/2, -0.05, title, ha='center', va='center',
                fontsize=18, fontweight='bold', color='#212529')

        # النصوص - القيم
        # القيمة الفعلية
        ax.text(np.pi/2, -0.28, f'{actual_percentage:.1f}%',
                ha='center', va='center', fontsize=24,
                color='#007BFF', fontweight='bold')
        ax.text(np.pi/2, -0.42, 'Actual', ha='center', va='center',
                fontsize=11, color='#007BFF', fontweight='bold')

        # القيمة المستهدفة
        ax.text(np.pi/2, -0.58, f'{target_percentage:.1f}%',
                ha='center', va='center', fontsize=18,
                color='#FF6F00', fontweight='bold')
        ax.text(np.pi/2, -0.70, 'Target', ha='center', va='center',
                fontsize=10, color='#FF6F00')

        # علامات النسب على الحواف بخط أكبر
        for percent in [0, 25, 50, 75, 100]:
            angle = (percent / 100) * np.pi
            ax.text(angle, 1.18, f'{percent}%', ha='center', va='center',
                   fontsize=10, color='#495057', fontweight='bold')

        # رسم خطوط تقسيم رفيعة
        for percent in [0, 25, 50, 75, 100]:
            angle = (percent / 100) * np.pi
            ax.plot([angle, angle], [0.58, 0.62], color='white',
                   linewidth=2, zorder=10)

        # إخفاء المحاور
        ax.set_ylim(0, 1.35)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.spines['polar'].set_visible(False)
        ax.grid(False)

        plt.tight_layout(pad=0.5)

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=140, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        plt.close()

        return Image(img_buffer, width=6*cm, height=5*cm)

    def _create_kpi_card(self, value, label, bg_color, border_color):
        """إنشاء بطاقة KPI"""
        kpi_table = Table([
            [Paragraph(str(value), self.styles['KPI'])],
            [Paragraph(self._reshape_text(label), self.styles['KPILabel'])]
        ])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(border_color)),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        return kpi_table

    def _create_kpi_cards(self):
        """إنشاء بطاقات المؤشرات الرئيسية"""
        kpi_data = [[
            self._create_kpi_card(self.total_students, "Total Students", '#E3F2FD', self.COLOR_SCHEME['primary']),
            self._create_kpi_card(f"{self.pass_rate:.1f}%", "Pass Rate", '#E8F5E9', self.COLOR_SCHEME['success']),
            self._create_kpi_card(f"{self.average_mark:.1f}", "Average Mark", '#FFF3E0', self.COLOR_SCHEME['warning']),
            self._create_kpi_card(f"{self.clo_achievement_rate:.0f}%", "CLO Achievement", '#F3E5F5', self.COLOR_SCHEME['purple']),
        ]]

        kpi_table = Table(kpi_data, colWidths=[5.8*cm]*4)
        kpi_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))

        return kpi_table

    def _create_grade_distribution_chart(self):
        """مخطط توزيع الدرجات"""
        fig, ax = plt.subplots(figsize=(9, 5))

        grades = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']
        counts = [self.grade_distribution[g] for g in grades]
        colors_gradient = ['#1B5E20', '#2E7D32', '#66BB6A', '#81C784',
                          '#FFB74D', '#FFA726', '#FF9800', '#F57C00', '#E53935']

        bars = ax.bar(grades, counts, color=colors_gradient, edgecolor='white', linewidth=2, alpha=0.9)

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_xlabel('Grade', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
        ax.set_title('Grade Distribution', fontsize=14, fontweight='bold', pad=15)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.7)
        ax.set_axisbelow(True)

        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()

        return Image(img_buffer, width=16*cm, height=9*cm)

    def _create_pass_fail_pie_chart(self):
        """مخطط دونات للنجاح/الرسوب (Donut Chart)"""
        fig, ax = plt.subplots(figsize=(7, 7))
        fig.patch.set_facecolor('white')

        sizes = [self.passed_students, self.failed_students]
        labels = ['Pass', 'Fail']
        colors_donut = ['#28A745', '#DC3545']  # أخضر وأحمر قويين
        explode = (0.08, 0.08)

        # رسم الدونات
        wedges, texts, autotexts = ax.pie(
            sizes,
            explode=explode,
            labels=labels,
            colors=colors_donut,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 14, 'fontweight': 'bold', 'color': 'white'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 3, 'antialiased': True},
            pctdistance=0.75
        )

        # تحسين النصوص
        for i, autotext in enumerate(autotexts):
            autotext.set_color('white')
            autotext.set_fontsize(16)
            autotext.set_fontweight('bold')

        # تحسين التسميات
        for i, text in enumerate(texts):
            text.set_fontsize(15)
            text.set_fontweight('bold')
            text.set_color(colors_donut[i])

        # رسم دائرة بيضاء في المنتصف لعمل شكل الدونات
        centre_circle = plt.Circle((0, 0), 0.65, fc='white', linewidth=0)
        ax.add_artist(centre_circle)

        # إضافة النص في المنتصف
        # إجمالي الطلاب المنتظمين
        ax.text(0, 0.15, f'{self.regular_count}', ha='center', va='center',
                fontsize=32, fontweight='bold', color='#212529')
        ax.text(0, -0.1, 'Total Students', ha='center', va='center',
                fontsize=12, color='#6C757D')

        # نسبة النجاح
        ax.text(0, -0.32, f'{self.pass_rate:.1f}%', ha='center', va='center',
                fontsize=20, fontweight='bold', color='#28A745')
        ax.text(0, -0.48, 'Pass Rate', ha='center', va='center',
                fontsize=11, color='#28A745', fontweight='bold')

        ax.set_title('Pass/Fail Distribution', fontsize=16, fontweight='bold',
                    pad=20, color='#212529')

        ax.axis('equal')
        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=130, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        plt.close()

        return Image(img_buffer, width=11*cm, height=11*cm)

    def _create_clo_gauges(self):
        """إنشاء مخططات العداد لجميع المخرجات"""
        elements = []
        clo_codes = sorted(self.clo_results.keys())

        # تنظيم في صفوف (3 أعمدة لكل صف)
        for i in range(0, len(clo_codes), 3):
            row_clos = clo_codes[i:i+3]

            # صف الرسومات
            gauge_row = []
            for clo_code in row_clos:
                result = self.clo_results[clo_code]
                gauge = self._create_gauge_chart(
                    result['actual_level'],
                    result['target_level'],
                    clo_code
                )
                gauge_row.append(gauge)

            # إكمال الصف إذا كان ناقصاً
            while len(gauge_row) < 3:
                gauge_row.append(Paragraph("", self.styles['DashboardNormal']))

            # صف التسميات (CLO names)
            label_row = []
            for clo_code in row_clos:
                result = self.clo_results[clo_code]
                clo = result['clo']

                # إنشاء تسمية واضحة
                label_text = f"<b>{clo_code}</b><br/>{clo.description[:50]}{'...' if len(clo.description) > 50 else ''}"
                label = Paragraph(
                    self._reshape_text(label_text),
                    ParagraphStyle(
                        'CLOLabel',
                        parent=self.styles['DashboardNormal'],
                        fontSize=10,
                        alignment=TA_CENTER,
                        textColor=colors.HexColor('#424242'),
                        leading=14
                    )
                )
                label_row.append(label)

            # إكمال صف التسميات
            while len(label_row) < 3:
                label_row.append(Paragraph("", self.styles['DashboardNormal']))

            # إضافة الصفوف إلى جدول
            gauge_table = Table([gauge_row], colWidths=[8.2*cm]*3)
            gauge_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))

            label_table = Table([label_row], colWidths=[8.2*cm]*3)
            label_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))

            elements.append(gauge_table)
            elements.append(label_table)

        return elements

    def _create_marks_distribution_histogram(self):
        """مخطط توزيع الدرجات"""
        fig, ax = plt.subplots(figsize=(9, 5))

        n, bins, patches = ax.hist(self.student_marks, bins=10, color=self.COLOR_SCHEME['primary'],
                                    alpha=0.7, edgecolor='white', linewidth=1.5)

        passing_mark = self.course.info.total_mark * (self.course.info.passing_percentage / 100)
        for i, patch in enumerate(patches):
            if bins[i] >= passing_mark:
                patch.set_facecolor(self.COLOR_SCHEME['success'])
            else:
                patch.set_facecolor(self.COLOR_SCHEME['danger'])

        ax.axvline(self.average_mark, color=self.COLOR_SCHEME['warning'], linestyle='--', linewidth=2.5,
                  label=f'Average: {self.average_mark:.1f}', alpha=0.8)
        ax.axvline(self.median_mark, color=self.COLOR_SCHEME['purple'], linestyle='--', linewidth=2.5,
                  label=f'Median: {self.median_mark:.1f}', alpha=0.8)

        ax.set_xlabel('Marks', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Marks Distribution', fontsize=14, fontweight='bold', pad=15)
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.7)
        ax.set_axisbelow(True)

        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()

        return Image(img_buffer, width=16*cm, height=9*cm)

    def _create_statistics_table(self):
        """جدول الإحصائيات الوصفية"""
        data = [
            [Paragraph(self._reshape_text("Statistic"), self.styles['DashboardNormal']),
             Paragraph(self._reshape_text("Value"), self.styles['DashboardNormal'])],
            [Paragraph(self._reshape_text("Mean"), self.styles['DashboardNormal']),
             Paragraph(f"{self.average_mark:.2f}", self.styles['DashboardNormal'])],
            [Paragraph(self._reshape_text("Median"), self.styles['DashboardNormal']),
             Paragraph(f"{self.median_mark:.2f}", self.styles['DashboardNormal'])],
            [Paragraph(self._reshape_text("Std Deviation"), self.styles['DashboardNormal']),
             Paragraph(f"{self.std_dev:.2f}", self.styles['DashboardNormal'])],
            [Paragraph(self._reshape_text("Minimum"), self.styles['DashboardNormal']),
             Paragraph(f"{self.min_mark:.2f}", self.styles['DashboardNormal'])],
            [Paragraph(self._reshape_text("Maximum"), self.styles['DashboardNormal']),
             Paragraph(f"{self.max_mark:.2f}", self.styles['DashboardNormal'])],
        ]

        table = Table(data, colWidths=[5*cm, 4.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLOR_SCHEME['indigo'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Arabic-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E8EAF6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#C5CAE9')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))

        return table

    def _create_header(self):
        """رأس التقرير"""
        elements = []

        title = Paragraph(
            self._reshape_text("Dashboard Report - Performance Analytics"),
            self.styles['DashboardTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2*cm))

        course_info = f"{self.course.info.course_code} - {self.course.info.course_title}"
        section_info = f"Section: {self.section.section_number} | Year: {self.section.academic_year} | {self.section.semester.value if hasattr(self.section.semester, 'value') else self.section.semester}"

        info_para = Paragraph(
            self._reshape_text(course_info + "<br/>" + section_info),
            self.styles['DashboardNormal']
        )
        elements.append(info_para)
        elements.append(Spacer(1, 0.4*cm))

        return elements

    def generate_report(self, output_path: str):
        """توليد تقرير PDF"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=1.2*cm,
            leftMargin=1.2*cm,
            topMargin=1.2*cm,
            bottomMargin=1.2*cm
        )

        story = []

        # إضافة ترويسة التقرير
        add_report_header(story, language=self.language, orientation='landscape')

        # الصفحة الأولى
        story.extend(self._create_header())

        # KPIs
        story.append(Paragraph(self._reshape_text("Key Performance Indicators"), self.styles['DashboardHeading']))
        story.append(Spacer(1, 0.2*cm))
        story.append(self._create_kpi_cards())
        story.append(Spacer(1, 0.5*cm))

        # Grade Distribution
        story.append(Paragraph(self._reshape_text("Grade Distribution"), self.styles['DashboardHeading']))
        story.append(Spacer(1, 0.2*cm))
        story.append(self._create_grade_distribution_chart())

        story.append(PageBreak())

        # الصفحة الثانية
        story.append(Paragraph(self._reshape_text("Student Performance Overview"), self.styles['DashboardHeading']))
        story.append(Spacer(1, 0.2*cm))

        # Donut Chart and Statistics side by side with spacing
        overview_data = [[
            self._create_pass_fail_pie_chart(),
            Paragraph("", self.styles['DashboardNormal']),  # مسافة فارغة
            self._create_statistics_table()
        ]]
        overview_table = Table(overview_data, colWidths=[11*cm, 2.5*cm, 10.5*cm])
        overview_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 0.5*cm))

        # Marks Distribution
        story.append(Paragraph(self._reshape_text("Marks Distribution"), self.styles['DashboardHeading']))
        story.append(Spacer(1, 0.2*cm))
        story.append(self._create_marks_distribution_histogram())

        story.append(PageBreak())

        # الصفحة الثالثة - CLO Gauges
        story.append(Paragraph(self._reshape_text("Course Learning Outcomes Achievement"), self.styles['DashboardHeading']))
        story.append(Spacer(1, 0.3*cm))
        story.extend(self._create_clo_gauges())

        # بناء المستند مع أرقام الصفحات والعلامة المائية
        doc.build(story, onFirstPage=add_page_number_first, onLaterPages=add_page_number_with_watermark)
