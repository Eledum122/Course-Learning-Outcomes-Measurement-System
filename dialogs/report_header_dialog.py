"""
حوار إعدادات ترويسة التقارير
Report Header Settings Dialog
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
from models.report_header import ReportHeader
from config import FONTS
from translations import t


class ReportHeaderDialog(tk.Toplevel):
    """حوار تحرير إعدادات ترويسة التقارير"""

    def __init__(self, parent, language: str = 'ar'):
        super().__init__(parent)

        self.language = language
        self.header = ReportHeader.load()
        self.logo_image = None

        # إعداد النافذة
        self.title("إعدادات ترويسة التقارير" if language == 'ar' else "Report Header Settings")
        self.geometry("900x700")
        self.resizable(True, True)
        self.configure(bg='#f5f5f5')

        # جعل النافذة modal
        self.transient(parent)
        self.grab_set()

        # إنشاء الواجهة
        self._create_widgets()

        # تحميل البيانات
        self._load_data()

        # مركزة النافذة
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """إنشاء عناصر الواجهة"""
        # الإطار الرئيسي
        main_frame = tk.Frame(self, bg='#f5f5f5', padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # إطار العنوان
        header_frame = tk.Frame(main_frame, bg='#1976D2', padx=20, pady=15)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_text = "إعدادات ترويسة التقارير" if self.language == 'ar' else "Report Header Settings"
        tk.Label(
            header_frame,
            text=title_text,
            font=FONTS['arabic_header'] if self.language == 'ar' else FONTS['english_header'],
            bg='#1976D2',
            fg='white'
        ).pack()

        # إطار للمحتوى القابل للتمرير والأزرار
        content_container = tk.Frame(main_frame, bg='#f5f5f5')
        content_container.pack(fill=tk.BOTH, expand=True)

        # إطار المحتوى القابل للتمرير
        scroll_frame = tk.Frame(content_container, bg='#f5f5f5')
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(scroll_frame, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg='#f5f5f5')

        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=content_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # تحديث عرض النافذة عند تغيير الحجم
        def on_canvas_configure(event):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)

        # قسم معاينة الترويسة
        self._create_preview_section(content_frame)

        # قسم الشعار
        self._create_logo_section(content_frame)

        # قسم النصوص الإنجليزية
        self._create_english_section(content_frame)

        # قسم النصوص العربية
        self._create_arabic_section(content_frame)

        # إطار الأزرار - خارج منطقة التمرير
        buttons_container = tk.Frame(content_container, bg='#f5f5f5')
        buttons_container.pack(fill=tk.X, pady=(10, 0))

        # الأزرار
        self._create_buttons(buttons_container)

    def _create_preview_section(self, parent):
        """إنشاء قسم معاينة الترويسة"""
        preview_frame = tk.LabelFrame(
            parent,
            text="  معاينة الترويسة  " if self.language == 'ar' else "  Header Preview  ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#1976D2',
            padx=15,
            pady=15,
            relief=tk.GROOVE,
            borderwidth=2
        )
        preview_frame.pack(fill=tk.X, pady=(0, 20))

        # إطار المعاينة
        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg='white',
            height=150,
            highlightthickness=1,
            highlightbackground='#ddd'
        )
        self.preview_canvas.pack(fill=tk.X, padx=10, pady=10)

    def _create_logo_section(self, parent):
        """إنشاء قسم الشعار"""
        logo_frame = tk.LabelFrame(
            parent,
            text="  شعار الجامعة  " if self.language == 'ar' else "  University Logo  ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#1976D2',
            padx=15,
            pady=15,
            relief=tk.GROOVE,
            borderwidth=2
        )
        logo_frame.pack(fill=tk.X, pady=(0, 20))

        # إطار عرض الشعار
        logo_display_frame = tk.Frame(logo_frame, bg='#f5f5f5', relief=tk.SUNKEN, borderwidth=1)
        logo_display_frame.pack(fill=tk.X, pady=(0, 10))

        self.logo_label = tk.Label(
            logo_display_frame,
            text="لم يتم تحميل شعار" if self.language == 'ar' else "No logo loaded",
            bg='#f5f5f5',
            fg='#999',
            font=('Arial', 10),
            width=50,
            height=10
        )
        self.logo_label.pack(padx=20, pady=20)

        # أزرار الشعار
        buttons_frame = tk.Frame(logo_frame, bg='white')
        buttons_frame.pack(fill=tk.X)

        # زر تحميل شعار
        upload_text = "📁 تحميل شعار" if self.language == 'ar' else "📁 Upload Logo"
        tk.Button(
            buttons_frame,
            text=upload_text,
            command=self._upload_logo,
            bg='#2196F3',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=20,
            height=2,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#1976D2'
        ).pack(side=tk.LEFT if self.language == 'en' else tk.RIGHT, padx=5)

        # زر حذف شعار
        remove_text = "🗑 حذف الشعار" if self.language == 'ar' else "🗑 Remove Logo"
        tk.Button(
            buttons_frame,
            text=remove_text,
            command=self._remove_logo,
            bg='#F44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=20,
            height=2,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#D32F2F'
        ).pack(side=tk.LEFT if self.language == 'en' else tk.RIGHT, padx=5)

    def _create_english_section(self, parent):
        """إنشاء قسم النصوص الإنجليزية"""
        english_frame = tk.LabelFrame(
            parent,
            text="  English Text  ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#1976D2',
            padx=15,
            pady=15,
            relief=tk.GROOVE,
            borderwidth=2
        )
        english_frame.pack(fill=tk.X, pady=(0, 20))

        # University Name
        self._create_field(english_frame, "University Name:", 'university_en')

        # Faculty Name
        self._create_field(english_frame, "Faculty Name:", 'faculty_en')

        # Department Name
        self._create_field(english_frame, "Department Name:", 'department_en')

    def _create_arabic_section(self, parent):
        """إنشاء قسم النصوص العربية"""
        arabic_frame = tk.LabelFrame(
            parent,
            text="  النصوص العربية  ",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#1976D2',
            padx=15,
            pady=15,
            relief=tk.GROOVE,
            borderwidth=2
        )
        arabic_frame.pack(fill=tk.X, pady=(0, 20))

        # اسم الجامعة
        self._create_field(arabic_frame, "اسم الجامعة:", 'university_ar', rtl=True)

        # اسم الكلية
        self._create_field(arabic_frame, "اسم الكلية:", 'faculty_ar', rtl=True)

        # اسم القسم
        self._create_field(arabic_frame, "اسم القسم:", 'department_ar', rtl=True)

    def _create_field(self, parent, label_text, field_name, rtl=False):
        """إنشاء حقل إدخال"""
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(fill=tk.X, pady=5)

        label = tk.Label(
            field_frame,
            text=label_text,
            font=('Arial', 10),
            bg='white',
            fg='#333',
            width=20,
            anchor='e' if rtl else 'w'
        )

        entry = ttk.Entry(field_frame, font=('Arial', 10))

        if rtl:
            label.pack(side=tk.RIGHT, padx=(10, 5))
            entry.pack(side=tk.RIGHT, padx=(5, 10), fill=tk.X, expand=True)
        else:
            label.pack(side=tk.LEFT, padx=(5, 10))
            entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

        # حفظ المرجع
        if not hasattr(self, 'entries'):
            self.entries = {}
        self.entries[field_name] = entry

        # ربط حدث التغيير لتحديث المعاينة
        entry.bind('<KeyRelease>', lambda e: self._update_preview())

    def _create_buttons(self, parent):
        """إنشاء الأزرار"""
        # خط فاصل
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=(5, 10))

        # إطار مركزي للأزرار
        center_buttons = tk.Frame(parent, bg='#f5f5f5')
        center_buttons.pack()

        # زر الحفظ
        save_text = "حفظ" if self.language == 'ar' else "Save"
        save_btn = tk.Button(
            center_buttons,
            text=save_text,
            command=self._save,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=20,
            height=2,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#45a049'
        )
        save_btn.pack(side=tk.LEFT, padx=8)
        save_btn.bind('<Enter>', lambda e: save_btn.config(bg='#45a049'))
        save_btn.bind('<Leave>', lambda e: save_btn.config(bg='#4CAF50'))

        # زر الإلغاء
        cancel_text = "إلغاء" if self.language == 'ar' else "Cancel"
        cancel_btn = tk.Button(
            center_buttons,
            text=cancel_text,
            command=self.destroy,
            bg='#757575',
            fg='white',
            font=('Arial', 11, 'bold'),
            width=20,
            height=2,
            cursor='hand2',
            relief=tk.FLAT,
            activebackground='#616161'
        )
        cancel_btn.pack(side=tk.LEFT, padx=8)
        cancel_btn.bind('<Enter>', lambda e: cancel_btn.config(bg='#616161'))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.config(bg='#757575'))

    def _load_data(self):
        """تحميل البيانات"""
        # تحميل النصوص
        self.entries['university_en'].insert(0, self.header.university_name_en)
        self.entries['faculty_en'].insert(0, self.header.faculty_name_en)
        self.entries['department_en'].insert(0, self.header.department_name_en)
        self.entries['university_ar'].insert(0, self.header.university_name_ar)
        self.entries['faculty_ar'].insert(0, self.header.faculty_name_ar)
        self.entries['department_ar'].insert(0, self.header.department_name_ar)

        # تحميل الشعار
        if self.header.logo_path and os.path.exists(self.header.logo_path):
            self._display_logo(self.header.logo_path)

        # تحديث المعاينة
        self._update_preview()

    def _upload_logo(self):
        """تحميل شعار جديد"""
        file_path = filedialog.askopenfilename(
            title="اختر صورة الشعار" if self.language == 'ar' else "Select Logo Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ],
            parent=self
        )

        if file_path:
            try:
                # نسخ الصورة إلى مجلد البيانات
                os.makedirs("data/images", exist_ok=True)
                filename = os.path.basename(file_path)
                dest_path = os.path.join("data/images", f"logo_{filename}")
                shutil.copy2(file_path, dest_path)

                # حفظ المسار
                self.header.logo_path = dest_path

                # عرض الشعار
                self._display_logo(dest_path)

                # تحديث المعاينة
                self._update_preview()

            except Exception as e:
                messagebox.showerror(
                    t('error', self.language),
                    f"فشل تحميل الشعار:\n{str(e)}" if self.language == 'ar'
                    else f"Failed to upload logo:\n{str(e)}",
                    parent=self
                )

    def _remove_logo(self):
        """حذف الشعار"""
        self.header.logo_path = ""
        self.logo_label.config(
            image='',
            text="لم يتم تحميل شعار" if self.language == 'ar' else "No logo loaded"
        )
        self.logo_image = None
        self._update_preview()

    def _display_logo(self, image_path):
        """عرض الشعار"""
        try:
            # فتح الصورة
            image = Image.open(image_path)

            # تغيير حجم الصورة
            image.thumbnail((200, 200), Image.Resampling.LANCZOS)

            # تحويل لـ PhotoImage
            self.logo_image = ImageTk.PhotoImage(image)

            # عرض الصورة
            self.logo_label.config(image=self.logo_image, text='')

        except Exception as e:
            messagebox.showerror(
                t('error', self.language),
                f"فشل عرض الشعار:\n{str(e)}" if self.language == 'ar'
                else f"Failed to display logo:\n{str(e)}",
                parent=self
            )

    def _update_preview(self):
        """تحديث معاينة الترويسة"""
        # مسح المعاينة القديمة
        self.preview_canvas.delete("all")

        canvas_width = self.preview_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 800

        # حساب المواقع
        center_x = canvas_width / 2
        left_text_x = 50
        right_text_x = canvas_width - 50

        # رسم النصوص الإنجليزية (يسار)
        self.preview_canvas.create_text(
            left_text_x, 40,
            text=self.entries['university_en'].get(),
            font=('Arial', 11),
            fill='#666',
            anchor='w'
        )
        self.preview_canvas.create_text(
            left_text_x, 65,
            text=self.entries['faculty_en'].get(),
            font=('Arial', 10),
            fill='#666',
            anchor='w'
        )
        self.preview_canvas.create_text(
            left_text_x, 90,
            text=self.entries['department_en'].get(),
            font=('Arial', 10),
            fill='#666',
            anchor='w'
        )

        # رسم الشعار في المنتصف
        if self.header.logo_path and os.path.exists(self.header.logo_path):
            try:
                logo_img = Image.open(self.header.logo_path)
                logo_img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)

                # حفظ المرجع
                self.preview_logo = logo_photo

                # رسم الشعار في المنتصف تماماً
                self.preview_canvas.create_image(center_x, 75, image=logo_photo)
            except:
                pass

        # رسم النصوص العربية (يمين)
        self.preview_canvas.create_text(
            right_text_x, 40,
            text=self.entries['university_ar'].get(),
            font=('Arial', 11),
            fill='#666',
            anchor='e'
        )
        self.preview_canvas.create_text(
            right_text_x, 65,
            text=self.entries['faculty_ar'].get(),
            font=('Arial', 10),
            fill='#666',
            anchor='e'
        )
        self.preview_canvas.create_text(
            right_text_x, 90,
            text=self.entries['department_ar'].get(),
            font=('Arial', 10),
            fill='#666',
            anchor='e'
        )

        # خط فاصل
        self.preview_canvas.create_line(
            20, 130, canvas_width - 20, 130,
            fill='#1976D2',
            width=2
        )

    def _save(self):
        """حفظ الإعدادات"""
        # تحديث البيانات
        self.header.university_name_en = self.entries['university_en'].get().strip()
        self.header.faculty_name_en = self.entries['faculty_en'].get().strip()
        self.header.department_name_en = self.entries['department_en'].get().strip()
        self.header.university_name_ar = self.entries['university_ar'].get().strip()
        self.header.faculty_name_ar = self.entries['faculty_ar'].get().strip()
        self.header.department_name_ar = self.entries['department_ar'].get().strip()

        # حفظ
        if self.header.save():
            messagebox.showinfo(
                t('success', self.language),
                "تم حفظ الإعدادات بنجاح" if self.language == 'ar'
                else "Settings saved successfully",
                parent=self
            )
            self.destroy()
        else:
            messagebox.showerror(
                t('error', self.language),
                "فشل حفظ الإعدادات" if self.language == 'ar'
                else "Failed to save settings",
                parent=self
            )
