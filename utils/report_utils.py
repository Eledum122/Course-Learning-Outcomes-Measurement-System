"""
أدوات مساعدة للتقارير
Report Utilities
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from models.report_header import ReportHeader

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

def reshape_arabic(text):
    """إعادة تشكيل النص العربي للعرض الصحيح في PDF"""
    if not text or not ARABIC_SUPPORT:
        return text
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text


# تسجيل الخطوط العربية
def register_arabic_fonts():
    """تسجيل الخطوط العربية إذا لم تكن مسجلة"""
    try:
        if 'ArabicFont' not in pdfmetrics.getRegisteredFontNames():
            # قائمة الخطوط العربية المتاحة في Windows مرتبة حسب الأفضلية
            font_candidates = [
                ('C:/Windows/Fonts/tahoma.ttf', 'ArabicFont'),
                ('C:/Windows/Fonts/tahomabd.ttf', 'ArabicFont-Bold'),
                ('C:/Windows/Fonts/times.ttf', 'ArabicFont'),
                ('C:/Windows/Fonts/timesbd.ttf', 'ArabicFont-Bold'),
                ('C:/Windows/Fonts/arial.ttf', 'ArabicFont'),
                ('C:/Windows/Fonts/arialbd.ttf', 'ArabicFont-Bold'),
            ]

            # محاولة تسجيل الخط العادي
            for font_path, font_name in font_candidates:
                if 'Bold' not in font_name and os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                    break

            # محاولة تسجيل الخط العريض
            for font_path, font_name in font_candidates:
                if 'Bold' in font_name and os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ArabicFont-Bold', font_path))
                    break

    except Exception as e:
        # سيستخدم Helvetica كخيار احتياطي
        pass


def add_report_header(elements, language='en', orientation='portrait'):
    """
    إضافة ترويسة التقرير

    Args:
        elements: قائمة عناصر التقرير
        language: لغة التقرير ('en' أو 'ar')
        orientation: اتجاه الصفحة ('portrait' أو 'landscape')
    """
    # تسجيل الخطوط العربية
    register_arabic_fonts()

    # تحميل إعدادات الترويسة
    header = ReportHeader.load()

    # تحديد عرض الصفحة
    if orientation == 'landscape':
        page_width = landscape(A4)[0]
    else:
        page_width = A4[0]

    # إنشاء جدول الترويسة
    header_data = []

    # الصف الأول: الشعار والنصوص
    row = []

    # تحديد اسم الخط العربي
    arabic_font = 'ArabicFont' if 'ArabicFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'

    # النصوص العربية (يمين) - مع إعادة التشكيل
    university_ar = reshape_arabic(header.university_name_ar)
    faculty_ar = reshape_arabic(header.faculty_name_ar)
    department_ar = reshape_arabic(header.department_name_ar)

    ar_text = f"""
    <font name="{arabic_font}" size="12"><b>{university_ar}</b></font><br/>
    <font name="{arabic_font}" size="10">{faculty_ar}</font><br/>
    <font name="{arabic_font}" size="10">{department_ar}</font>
    """

    # الشعار (وسط)
    logo_cell = ""
    if header.logo_path and os.path.exists(header.logo_path):
        try:
            logo = RLImage(header.logo_path, width=3*cm, height=3*cm)
            logo_cell = logo
        except:
            logo_cell = ""

    # النصوص الإنجليزية (يسار)
    en_text = f"""
    <font size="12"><b>{header.university_name_en}</b></font><br/>
    <font size="10">{header.faculty_name_en}</font><br/>
    <font size="10">{header.department_name_en}</font>
    """

    # إنشاء الأنماط
    styles = getSampleStyleSheet()

    style_ar = ParagraphStyle(
        'ArabicStyle',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
        fontName=arabic_font,
        textColor=colors.HexColor('#666666')
    )

    style_en = ParagraphStyle(
        'EnglishStyle',
        parent=styles['Normal'],
        alignment=TA_LEFT,
        fontName='Helvetica',
        textColor=colors.HexColor('#666666')
    )

    # بناء الصف
    row = [
        Paragraph(en_text, style_en),
        logo_cell if logo_cell else '',
        Paragraph(ar_text, style_ar)
    ]

    header_data.append(row)

    # إنشاء الجدول
    col_widths = [
        (page_width - 4*cm) / 3,  # English
        3*cm,  # Logo
        (page_width - 4*cm) / 3   # Arabic
    ]

    header_table = Table(header_data, colWidths=col_widths)

    # تنسيق الجدول (بدون padding علوي)
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # إزالة المسافة العلوية
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))

    # إضافة الجدول للعناصر
    elements.append(header_table)

    # خط فاصل - استخدام جدول بخلفية ملونة بدلاً من أحرف
    line_data = [['']]
    line_table = Table(line_data, colWidths=[page_width - 4*cm], rowHeights=[0.1*cm])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1976D2')),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(line_table)

    # مسافة بعد الترويسة
    elements.append(Spacer(1, 0.5*cm))


def create_header_frame_for_canvas(canvas, doc, language='en'):
    """
    إضافة ترويسة للصفحة الأولى فقط باستخدام Canvas
    يستخدم في onFirstPage callback
    """
    # تسجيل الخطوط العربية
    register_arabic_fonts()

    header = ReportHeader.load()

    # تحديد اسم الخط العربي
    arabic_font = 'ArabicFont' if 'ArabicFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'

    # حفظ الحالة
    canvas.saveState()

    # رسم الشعار
    if header.logo_path and os.path.exists(header.logo_path):
        try:
            # رسم الشعار في الوسط العلوي
            canvas.drawImage(
                header.logo_path,
                doc.width / 2 - 1.5*cm,
                doc.height + doc.topMargin - 3*cm,
                width=3*cm,
                height=3*cm,
                preserveAspectRatio=True
            )
        except:
            pass

    # النصوص الإنجليزية (يسار)
    canvas.setFont('Helvetica-Bold', 12)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(
        doc.leftMargin,
        doc.height + doc.topMargin - 1*cm,
        header.university_name_en
    )

    canvas.setFont('Helvetica', 10)
    canvas.drawString(
        doc.leftMargin,
        doc.height + doc.topMargin - 1.5*cm,
        header.faculty_name_en
    )

    canvas.drawString(
        doc.leftMargin,
        doc.height + doc.topMargin - 2*cm,
        header.department_name_en
    )

    # النصوص العربية (يمين) - باستخدام الخط العربي مع إعادة التشكيل
    university_ar = reshape_arabic(header.university_name_ar)
    faculty_ar = reshape_arabic(header.faculty_name_ar)
    department_ar = reshape_arabic(header.department_name_ar)

    canvas.setFont(arabic_font, 12)
    canvas.drawRightString(
        doc.width + doc.leftMargin,
        doc.height + doc.topMargin - 1*cm,
        university_ar
    )

    canvas.setFont(arabic_font, 10)
    canvas.drawRightString(
        doc.width + doc.leftMargin,
        doc.height + doc.topMargin - 1.5*cm,
        faculty_ar
    )

    canvas.drawRightString(
        doc.width + doc.leftMargin,
        doc.height + doc.topMargin - 2*cm,
        department_ar
    )

    # خط فاصل
    canvas.setStrokeColor(colors.HexColor('#1976D2'))
    canvas.setLineWidth(2)
    canvas.line(
        doc.leftMargin,
        doc.height + doc.topMargin - 3.5*cm,
        doc.width + doc.leftMargin,
        doc.height + doc.topMargin - 3.5*cm
    )

    # استعادة الحالة
    canvas.restoreState()


def add_page_number(canvas, doc):
    """
    إضافة رقم الصفحة في أسفل الصفحة
    Add page number at bottom of page

    Args:
        canvas: Canvas object from ReportLab
        doc: Document object from ReportLab
    """
    canvas.saveState()
    page_num = canvas.getPageNumber()

    # تحديد النص بناءً على اللغة
    # Determine text based on page number
    text = f"Page {page_num}"

    # رسم رقم الصفحة في الأسفل في المنتصف
    # Draw page number at bottom center
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawCentredString(
        doc.width / 2 + doc.leftMargin,
        1 * cm,
        text
    )

    canvas.restoreState()


def add_page_number_first(canvas, doc):
    """
    إضافة رقم الصفحة للصفحة الأولى (مع العلامة المائية)
    Add page number to first page (with watermark)

    ملاحظة: الترويسة تُضاف كعنصر في story باستخدام add_report_header()
    Note: Header is added as element in story using add_report_header()

    Args:
        canvas: Canvas object from ReportLab
        doc: Document object from ReportLab
    """
    # إضافة العلامة المائية أولاً (في الخلفية)
    # Add watermark first (in background)
    add_watermark(canvas, doc)

    # ثم إضافة رقم الصفحة
    # Then add page number
    add_page_number(canvas, doc)


def add_page_number_with_watermark(canvas, doc):
    """
    إضافة رقم الصفحة مع العلامة المائية للصفحات اللاحقة
    Add page number with watermark for later pages

    Args:
        canvas: Canvas object from ReportLab
        doc: Document object from ReportLab
    """
    # إضافة العلامة المائية أولاً (في الخلفية)
    # Add watermark first (in background)
    add_watermark(canvas, doc)

    # ثم إضافة رقم الصفحة
    # Then add page number
    add_page_number(canvas, doc)


def add_watermark(canvas, doc):
    """
    إضافة شعار الجامعة كعلامة مائية شفافة في وسط الصفحة
    Add university logo as transparent watermark in center of page

    Args:
        canvas: Canvas object from ReportLab
        doc: Document object from ReportLab
    """
    header = ReportHeader.load()

    # التحقق من وجود الشعار
    if not header.logo_path or not os.path.exists(header.logo_path):
        return

    try:
        canvas.saveState()

        # حساب موقع الوسط
        page_width = doc.width + doc.leftMargin + doc.rightMargin
        page_height = doc.height + doc.topMargin + doc.bottomMargin
        center_x = page_width / 2
        center_y = page_height / 2

        # حجم العلامة المائية (كبير نسبياً)
        watermark_size = 12 * cm

        # تعيين الشفافية (0.1 = 10% شفافية)
        canvas.setFillAlpha(0.1)

        # رسم الشعار في وسط الصفحة
        canvas.drawImage(
            header.logo_path,
            center_x - watermark_size / 2,
            center_y - watermark_size / 2,
            width=watermark_size,
            height=watermark_size,
            preserveAspectRatio=True,
            mask='auto'
        )

        canvas.restoreState()
    except Exception as e:
        # في حالة حدوث خطأ، لا تفعل شيء
        pass
