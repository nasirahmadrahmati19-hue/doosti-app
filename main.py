import customtkinter as ctk
from tkinter import messagebox, Menu
import sqlite3
from datetime import datetime
import jdatetime
import os

# تنظیمات ظاهری
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# رنگ‌های سفارشی
COLORS = {
    "primary": "#1a2332",
    "secondary": "#2c3e50",
    "accent": "#d4af37",
    "success": "#27ae60",
    "danger": "#e74c3c",
    "warning": "#f39c12",
    "text": "#ecf0f1",
    "text_muted": "#95a5a6",
    "card_bg": "#34495e",
    "input_bg": "#2c3e50",
    "selected_row": "#3d566e"
}

class DoostiTailoringApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("خیاطی دوستی")
        self.geometry("1200x800")
        self.configure(fg_color=COLORS["primary"])
        
        self.editing_order_id = None
        self.editing_expense_id = None
        self.selected_order_row = None
        self.selected_order_widget = None
        self.selected_expense_row = None
        self.selected_expense_widget = None
        
        self.all_entries = []
        
        self.load_fonts()
        self.create_database()
        self.migrate_database()
        self.create_modern_ui()
        
        self.after(100, self.calculate_report)
    
    def load_fonts(self):
        """بارگذاری فونت‌های فارسی"""
        try:
            if os.path.exists("fonts"):
                font_files = [
                    "fonts/Vazirmatn-Regular.ttf",
                    "fonts/Vazirmatn-Bold.ttf",
                    "fonts/Vazirmatn-Medium.ttf"
                ]
                for font_file in font_files:
                    if os.path.exists(font_file):
                        self.load_font(font_file)
                self.font_family = "Vazirmatn"
            else:
                self.font_family = "Tahoma"
        except:
            self.font_family = "Tahoma"
    
    def load_font(self, font_path):
        """بارگذاری یک فایل فونت"""
        try:
            import ctypes
            ctypes.windll.gdi32.AddFontResourceW(font_path)
        except:
            pass
    
    def create_database(self):
        """ایجاد جداول دیتابیس"""
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_surname TEXT NOT NULL,
                phone TEXT NOT NULL,
                clothing_code INTEGER UNIQUE,
                clothing_type TEXT NOT NULL,
                price REAL NOT NULL,
                height REAL,
                sleeve REAL,
                shoulder REAL,
                collar REAL,
                chest REAL,
                skirt REAL,
                pants_length REAL,
                leg REAL,
                order_date TEXT,
                status TEXT DEFAULT 'در حال دوخت'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def migrate_database(self):
        """انتقال دیتابیس قدیمی به ساختار جدید"""
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'clothing_code' not in columns:
            cursor.execute('ALTER TABLE orders ADD COLUMN clothing_code INTEGER')
        
        conn.commit()
        conn.close()
    
    def check_duplicate_code(self, code, exclude_id=None):
        """بررسی تکراری نبودن کود لباس"""
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        if exclude_id:
            cursor.execute(
                'SELECT id FROM orders WHERE clothing_code = ? AND id != ?',
                (code, exclude_id)
            )
        else:
            cursor.execute(
                'SELECT id FROM orders WHERE clothing_code = ?',
                (code,)
            )
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def create_modern_ui(self):
        """ایجاد رابط کاربری مدرن"""
        self.create_header()
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        self.create_navigation()
        self.create_tab_content()
        self.show_tab("new_order")
    
    def create_header(self):
        """ایجاد هدر مدرن - RTL با تاریخ شمسی"""
        header = ctk.CTkFrame(self, fg_color=COLORS["secondary"], height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        today = jdatetime.datetime.now().strftime("%Y/%m/%d")
        date_label = ctk.CTkLabel(
            header_content,
            text=f"{today}  📅",
            font=ctk.CTkFont(family=self.font_family, size=14),
            text_color=COLORS["text"]
        )
        date_label.pack(side="right")
        
        subtitle = ctk.CTkLabel(
            header_content,
            text="سیستم مدیریت سفارشات",
            font=ctk.CTkFont(family=self.font_family, size=14),
            text_color=COLORS["text_muted"]
        )
        subtitle.pack(side="right", padx=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_content,
            text="خیاطی دوستی  🧵",
            font=ctk.CTkFont(family=self.font_family, size=28, weight="bold"),
            text_color=COLORS["accent"]
        )
        title_label.pack(side="right")
    
    def create_navigation(self):
        """ایجاد منوی ناوبری مدرن - RTL"""
        nav_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(0, 20))
        
        self.nav_buttons = {}
        tabs = [
            ("new_order", "ثبت سفارش جدید  📝"),
            ("customers", "مشتریان  👥"),
            ("expenses", "مصارف دوکان  💰"),
            ("report", "گزارش مالی  📊")
        ]
        
        for i, (tab_id, text) in enumerate(tabs):
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                font=ctk.CTkFont(family=self.font_family, size=15, weight="bold"),
                fg_color=COLORS["card_bg"],
                hover_color=COLORS["accent"],
                text_color=COLORS["text"],
                corner_radius=12,
                height=45,
                command=lambda t=tab_id: self.show_tab(t)
            )
            btn.pack(side="right", padx=(10, 0))
            self.nav_buttons[tab_id] = btn
    
    def create_tab_content(self):
        """ایجاد محتوای تب‌ها"""
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        self.tabs = {}
        self.create_new_order_tab()
        self.create_customers_tab()
        self.create_expenses_tab()
        self.create_report_tab()
    
    def show_tab(self, tab_id):
        """نمایش تب انتخاب شده"""
        for tab in self.tabs.values():
            tab.pack_forget()
        
        self.tabs[tab_id].pack(fill="both", expand=True)
        
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.configure(fg_color=COLORS["accent"], text_color=COLORS["primary"])
            else:
                btn.configure(fg_color=COLORS["card_bg"], text_color=COLORS["text"])
    
    def create_section_title(self, parent, text, icon=""):
        """ایجاد عنوان بخش مدرن - RTL"""
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        
        separator = ctk.CTkFrame(title_frame, fg_color=COLORS["accent"], height=2)
        separator.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        title = ctk.CTkLabel(
            title_frame,
            text=f"{text}  {icon}" if icon else text,
            font=ctk.CTkFont(family=self.font_family, size=20, weight="bold"),
            text_color=COLORS["accent"]
        )
        title.pack(side="right")
        
        return title_frame
    
    def create_new_order_tab(self):
        """ایجاد تب ثبت سفارش جدید - تقسیم‌بندی عمودی"""
        tab = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tabs["new_order"] = tab
        
        self.order_title_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.order_title_frame.pack(fill="x", pady=(0, 15))
        
        separator = ctk.CTkFrame(self.order_title_frame, fg_color=COLORS["accent"], height=2)
        separator.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        self.order_title_label = ctk.CTkLabel(
            self.order_title_frame,
            text="ثبت سفارش جدید  📝",
            font=ctk.CTkFont(family=self.font_family, size=20, weight="bold"),
            text_color=COLORS["accent"]
        )
        self.order_title_label.pack(side="right")
        
        # کانتینر اصلی دو ستونه
        main_container = ctk.CTkFrame(tab, fg_color="transparent")
        main_container.pack(fill="both", expand=True, pady=(0, 15))
        
        # ============================================
        # ستون سمت چپ: اندازه‌ها
        # ============================================
        left_column = ctk.CTkFrame(main_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        measure_card = ctk.CTkFrame(left_column, fg_color=COLORS["card_bg"], corner_radius=15)
        measure_card.pack(fill="both", expand=True)
        
        card_header2 = ctk.CTkFrame(measure_card, fg_color=COLORS["secondary"], corner_radius=15)
        card_header2.pack(fill="x")
        
        ctk.CTkLabel(
            card_header2,
            text="اندازه‌ها (سانتی‌متر)  📏",
            font=ctk.CTkFont(family=self.font_family, size=20, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=15, padx=20, anchor="e")
        
        measure_content = ctk.CTkScrollableFrame(measure_card, fg_color="transparent")
        measure_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        measurements = [
            ("قد", "height"),
            ("آستین", "sleeve"),
            ("شانه", "shoulder"),
            ("یخن", "collar"),
            ("بغل", "chest"),
            ("بردامن", "skirt"),
            ("قد تنبان", "pants_length"),
            ("پاچه", "leg")
        ]
        
        self.measure_entries = {}
        
        for row_idx, (label, key) in enumerate(measurements):
            field_frame = ctk.CTkFrame(measure_content, fg_color="transparent")
            field_frame.grid(row=row_idx, column=0, padx=5, pady=8, sticky="ew")
            
            # ✅ فونت ضخیم‌تر و روشن‌تر برای نام فیلدها
            lbl = ctk.CTkLabel(
                field_frame,
                text=label,
                font=ctk.CTkFont(family=self.font_family, size=15, weight="bold"),
                text_color=COLORS["text"]
            )
            lbl.pack(anchor="e", pady=(0, 5))
            
            entry = ctk.CTkEntry(
                field_frame,
                placeholder_text="0",
                font=ctk.CTkFont(family=self.font_family, size=14),
                height=40,
                corner_radius=10,
                fg_color=COLORS["input_bg"],
                border_color=COLORS["secondary"],
                text_color=COLORS["text"]
            )
            entry.pack(fill="x")
            self.measure_entries[key] = entry
            
            def on_enter(event, e=entry):
                try:
                    current_index = self.all_entries.index(e)
                    if current_index < len(self.all_entries) - 1:
                        self.all_entries[current_index + 1].focus()
                except ValueError:
                    pass
                return "break"
            
            entry.bind("<Return>", on_enter)
            self.all_entries.append(entry)
        
        measure_content.grid_columnconfigure(0, weight=1)
        
        # ============================================
        # ستون سمت راست: اطلاعات مشتری
        # ============================================
        right_column = ctk.CTkFrame(main_container, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        customer_card = ctk.CTkFrame(right_column, fg_color=COLORS["card_bg"], corner_radius=15)
        customer_card.pack(fill="both", expand=True)
        
        card_header = ctk.CTkFrame(customer_card, fg_color=COLORS["secondary"], corner_radius=15)
        card_header.pack(fill="x")
        
        ctk.CTkLabel(
            card_header,
            text="اطلاعات مشتری  👤",
            font=ctk.CTkFont(family=self.font_family, size=20, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(pady=15, padx=20, anchor="e")
        
        card_content = ctk.CTkScrollableFrame(customer_card, fg_color="transparent")
        card_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        fields_info = [
            ("اسم", "name"),
            ("تخلص", "surname"),
            ("شماره تلفون", "phone"),
            ("کود لباس (عدد)", "clothing_code"),
            ("مدل لباس", "clothing_type"),
            ("قیمت لباس (افغانی)", "price")
        ]
        
        self.info_entries = {}
        
        for label, key in fields_info:
            field_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            field_frame.pack(fill="x", pady=(0, 15))
            
            # ✅ فونت ضخیم‌تر و روشن‌تر برای نام فیلدها
            lbl = ctk.CTkLabel(
                field_frame,
                text=label,
                font=ctk.CTkFont(family=self.font_family, size=15, weight="bold"),
                text_color=COLORS["text"]
            )
            lbl.pack(anchor="e", pady=(0, 5))
            
            entry = ctk.CTkEntry(
                field_frame,
                placeholder_text=label,
                font=ctk.CTkFont(family=self.font_family, size=14),
                height=40,
                corner_radius=10,
                fg_color=COLORS["input_bg"],
                border_color=COLORS["secondary"],
                text_color=COLORS["text"]
            )
            entry.pack(fill="x")
            self.info_entries[key] = entry
            
            def on_enter(event, e=entry):
                try:
                    current_index = self.all_entries.index(e)
                    if current_index < len(self.all_entries) - 1:
                        self.all_entries[current_index + 1].focus()
                except ValueError:
                    pass
                return "break"
            
            entry.bind("<Return>", on_enter)
            self.all_entries.append(entry)
        
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        self.btn_cancel_edit = ctk.CTkButton(
            btn_frame,
            text="لغو ویرایش  ❌",
            font=ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            text_color=COLORS["text"],
            corner_radius=12,
            height=50,
            command=self.cancel_edit
        )
        self.btn_cancel_edit.pack(side="right", padx=(10, 0), fill="x", expand=True)
        
        self.btn_save = ctk.CTkButton(
            btn_frame,
            text="ذخیره سفارش  💾",
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color="#b8941f",
            text_color=COLORS["primary"],
            corner_radius=12,
            height=50,
            command=self.save_order
        )
        self.btn_save.pack(side="right", fill="x", expand=True)
        
        self.entry_name = self.info_entries["name"]
        self.entry_surname = self.info_entries["surname"]
        self.entry_phone = self.info_entries["phone"]
        self.entry_clothing_code = self.info_entries["clothing_code"]
        self.entry_clothing_type = self.info_entries["clothing_type"]
        self.entry_price = self.info_entries["price"]
    
    def create_modern_entry(self, parent, placeholder, width=200):
        """ایجاد ورودی مدرن با قابلیت Enter"""
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            font=ctk.CTkFont(family=self.font_family, size=14),
            width=width,
            height=40,
            corner_radius=10,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["secondary"],
            text_color=COLORS["text"]
        )
        
        self.all_entries.append(entry)
        
        def on_enter(event):
            try:
                current_index = self.all_entries.index(event.widget)
                if current_index < len(self.all_entries) - 1:
                    self.all_entries[current_index + 1].focus()
            except ValueError:
                pass
            return "break"
        
        entry.bind("<Return>", on_enter)
        
        return entry
    
    def create_customers_tab(self):
        """ایجاد تب مشتریان - RTL"""
        tab = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tabs["customers"] = tab
        
        self.create_section_title(tab, "لیست مشتریان", "👥")
        
        search_card = ctk.CTkFrame(tab, fg_color=COLORS["card_bg"], corner_radius=15)
        search_card.pack(fill="x", pady=(0, 20), padx=5)
        
        search_content = ctk.CTkFrame(search_card, fg_color="transparent")
        search_content.pack(fill="x", padx=20, pady=20)
        
        self.btn_refresh = ctk.CTkButton(
            search_content,
            text="بروزرسانی  🔄",
            font=ctk.CTkFont(family=self.font_family, size=14),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["accent"],
            text_color=COLORS["text"],
            corner_radius=10,
            height=40,
            width=120,
            command=self.load_customers
        )
        self.btn_refresh.pack(side="right")
        
        self.btn_search = ctk.CTkButton(
            search_content,
            text="جستجو",
            font=ctk.CTkFont(family=self.font_family, size=14),
            fg_color=COLORS["accent"],
            hover_color="#b8941f",
            text_color=COLORS["primary"],
            corner_radius=10,
            height=40,
            width=120,
            command=self.search_customers
        )
        self.btn_search.pack(side="right", padx=(10, 0))
        
        self.entry_search = self.create_modern_entry(
            search_content, 
            "جستجو با اسم، تخلص، موبایل یا کود لباس...  🔍", 
            width=400
        )
        self.entry_search.pack(side="right", padx=(15, 0))
        
        table_card = ctk.CTkFrame(tab, fg_color=COLORS["card_bg"], corner_radius=15)
        table_card.pack(fill="both", expand=True, padx=5)
        
        table_header = ctk.CTkFrame(table_card, fg_color=COLORS["secondary"], corner_radius=15)
        table_header.pack(fill="x")
        
        headers = ["وضعیت", "تاریخ", "قیمت", "مدل لباس", "کود لباس", "موبایل", "تخلص", "اسم", "شماره"]
        
        header_grid = ctk.CTkFrame(table_header, fg_color="transparent")
        header_grid.pack(fill="x", padx=20, pady=15)
        
        for i in range(9):
            header_grid.grid_columnconfigure(i, weight=1, uniform="column")
        
        for i, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_grid,
                text=header,
                font=ctk.CTkFont(family=self.font_family, size=13, weight="bold"),
                text_color=COLORS["accent"]
            )
            lbl.grid(row=0, column=i, sticky="nsew", padx=2)
        
        self.table_content = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.table_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_customers()
    
    def create_expenses_tab(self):
        """ایجاد تب مصارف - RTL"""
        tab = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tabs["expenses"] = tab
        
        self.create_section_title(tab, "مصارف دوکان", "💰")
        
        form_card = ctk.CTkFrame(tab, fg_color=COLORS["card_bg"], corner_radius=15)
        form_card.pack(fill="x", pady=(0, 20), padx=5)
        
        card_header = ctk.CTkFrame(form_card, fg_color=COLORS["secondary"], corner_radius=15)
        card_header.pack(fill="x")
        
        self.expense_title_label = ctk.CTkLabel(
            card_header,
            text="ثبت مصرف جدید  💰",
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold"),
            text_color=COLORS["text"]
        )
        self.expense_title_label.pack(pady=12, padx=20, anchor="e")
        
        form_content = ctk.CTkFrame(form_card, fg_color="transparent")
        form_content.pack(fill="x", padx=20, pady=20)
        
        self.btn_save_expense = ctk.CTkButton(
            form_content,
            text="ذخیره  💾",
            font=ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color="#b8941f",
            text_color=COLORS["primary"],
            corner_radius=10,
            height=40,
            width=120,
            command=self.save_expense
        )
        self.btn_save_expense.pack(side="right")
        
        self.btn_cancel_expense_edit = ctk.CTkButton(
            form_content,
            text="لغو  ❌",
            font=ctk.CTkFont(family=self.font_family, size=14),
            fg_color=COLORS["danger"],
            hover_color="#c0392b",
            text_color=COLORS["text"],
            corner_radius=10,
            height=40,
            width=100,
            command=self.cancel_expense_edit
        )
        self.btn_cancel_expense_edit.pack(side="right", padx=(10, 0))
        
        amount_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        amount_frame.pack(side="right", padx=(15, 0))
        
        ctk.CTkLabel(
            amount_frame,
            text="مبلغ",
            font=ctk.CTkFont(family=self.font_family, size=12),
            text_color=COLORS["text_muted"]
        ).pack(anchor="e", pady=(0, 3))
        
        self.entry_expense_amount = ctk.CTkEntry(
            amount_frame,
            placeholder_text="مبلغ (افغانی)",
            font=ctk.CTkFont(family=self.font_family, size=14),
            width=200,
            height=40,
            corner_radius=10,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["secondary"],
            text_color=COLORS["text"]
        )
        self.entry_expense_amount.pack()
        
        title_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        title_frame.pack(side="right", padx=(15, 0))
        
        ctk.CTkLabel(
            title_frame,
            text="عنوان مصرف",
            font=ctk.CTkFont(family=self.font_family, size=12),
            text_color=COLORS["text_muted"]
        ).pack(anchor="e", pady=(0, 3))
        
        self.entry_expense_title = ctk.CTkEntry(
            title_frame,
            placeholder_text="عنوان مصرف (مثلاً: کرایه دوکان)",
            font=ctk.CTkFont(family=self.font_family, size=14),
            width=350,
            height=40,
            corner_radius=10,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["secondary"],
            text_color=COLORS["text"]
        )
        self.entry_expense_title.pack()
        
        table_card = ctk.CTkFrame(tab, fg_color=COLORS["card_bg"], corner_radius=15)
        table_card.pack(fill="both", expand=True, padx=5)
        
        table_header = ctk.CTkFrame(table_card, fg_color=COLORS["secondary"], corner_radius=15)
        table_header.pack(fill="x")
        
        headers = ["تاریخ", "مبلغ", "عنوان", "شماره"]
        
        header_grid = ctk.CTkFrame(table_header, fg_color="transparent")
        header_grid.pack(fill="x", padx=20, pady=15)
        
        for i in range(4):
            header_grid.grid_columnconfigure(i, weight=1, uniform="column")
        
        for i, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_grid,
                text=header,
                font=ctk.CTkFont(family=self.font_family, size=13, weight="bold"),
                text_color=COLORS["accent"]
            )
            lbl.grid(row=0, column=i, sticky="nsew", padx=2)
        
        self.expenses_table_content = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.expenses_table_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_expenses()
    
    def create_report_tab(self):
        """ایجاد تب گزارش مالی - RTL"""
        tab = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.tabs["report"] = tab
        
        self.create_section_title(tab, "گزارش مالی", "📊")
        
        stats_frame = ctk.CTkFrame(tab, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        self.profit_card = self.create_stat_card(
            stats_frame, "سود خالص  📈", "0 افغانی", COLORS["accent"]
        )
        self.profit_card.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        self.expenses_card = self.create_stat_card(
            stats_frame, "مجموع مصارف  💸", "0 افغانی", COLORS["danger"]
        )
        self.expenses_card.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        self.income_card = self.create_stat_card(
            stats_frame, "مجموع درآمد  💵", "0 افغانی", COLORS["success"]
        )
        self.income_card.pack(side="right", fill="x", expand=True)
        
        self.btn_calculate = ctk.CTkButton(
            tab,
            text="محاسبه گزارش  🔄",
            font=ctk.CTkFont(family=self.font_family, size=16, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color="#b8941f",
            text_color=COLORS["primary"],
            corner_radius=12,
            height=50,
            command=self.calculate_report
        )
        self.btn_calculate.pack(pady=20, fill="x", padx=5)
    
    def create_stat_card(self, parent, title, value, color):
        """ایجاد کارت آماری - RTL"""
        card = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=15)
        
        color_bar = ctk.CTkFrame(card, fg_color=color, height=5, corner_radius=15)
        color_bar.pack(fill="x")
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=25)
        
        value_label = ctk.CTkLabel(
            content,
            text=value,
            font=ctk.CTkFont(family=self.font_family, size=24, weight="bold"),
            text_color=color
        )
        value_label.pack(anchor="e", pady=(10, 0))
        
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=ctk.CTkFont(family=self.font_family, size=14),
            text_color=COLORS["text_muted"]
        )
        title_label.pack(anchor="e")
        
        if "درآمد" in title:
            self.income_value = value_label
        elif "مصارف" in title:
            self.expenses_value = value_label
        else:
            self.profit_value = value_label
        
        return card
    
    def show_order_context_menu(self, event, order_id, row_widget):
        """نمایش منوی راست‌کلیک برای سفارش"""
        self.select_order_row(order_id, row_widget)
        
        menu = Menu(self, tearoff=0, bg=COLORS["card_bg"], fg=COLORS["text"],
                   activebackground=COLORS["accent"], activeforeground=COLORS["primary"],
                   font=(self.font_family, 12))
        
        menu.add_command(label="✏️  ویرایش سفارش", command=self.edit_selected_order)
        menu.add_command(label="🗑️  حذف سفارش", command=self.delete_order)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def show_expense_context_menu(self, event, expense_id, row_widget):
        """نمایش منوی راست‌کلیک برای مصرف"""
        self.select_expense_row(expense_id, row_widget)
        
        menu = Menu(self, tearoff=0, bg=COLORS["card_bg"], fg=COLORS["text"],
                   activebackground=COLORS["accent"], activeforeground=COLORS["primary"],
                   font=(self.font_family, 12))
        
        menu.add_command(label="✏️  ویرایش مصرف", command=self.edit_selected_expense)
        menu.add_command(label="🗑️  حذف مصرف", command=self.delete_expense)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def save_order(self):
        """ذخیره سفارش جدید یا بروزرسانی"""
        clothing_code = self.entry_clothing_code.get().strip()
        name = self.entry_name.get().strip()
        surname = self.entry_surname.get().strip()
        phone = self.entry_phone.get().strip()
        clothing_type = self.entry_clothing_type.get().strip()
        price = self.entry_price.get().strip()
        
        if not clothing_code or not name or not surname or not phone or not price:
            messagebox.showerror("خطا", "لطفاً تمام فیلدهای ضروری را پر کنید!")
            return
        
        try:
            clothing_code = int(clothing_code)
            price = float(price)
        except ValueError:
            messagebox.showerror("خطا", "کود لباس و قیمت باید عدد باشند!")
            return
        
        if not clothing_type:
            clothing_type = "نامشخص"
        
        if self.check_duplicate_code(clothing_code, self.editing_order_id):
            messagebox.showerror(
                "خطا", 
                f"کود لباس {clothing_code} قبلاً ثبت شده است!\nلطفاً یک کود منحصر به فرد وارد کنید."
            )
            return
        
        measurements = {}
        for key, entry in self.measure_entries.items():
            value = entry.get().strip()
            measurements[key] = float(value) if value else None
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        order_date = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        
        if self.editing_order_id:
            cursor.execute('''
                UPDATE orders SET
                    clothing_code = ?, customer_name = ?, customer_surname = ?,
                    phone = ?, clothing_type = ?, price = ?,
                    height = ?, sleeve = ?, shoulder = ?, collar = ?,
                    chest = ?, skirt = ?, pants_length = ?, leg = ?
                WHERE id = ?
            ''', (clothing_code, name, surname, phone, clothing_type, price,
                  measurements['height'], measurements['sleeve'], measurements['shoulder'],
                  measurements['collar'], measurements['chest'], measurements['skirt'],
                  measurements['pants_length'], measurements['leg'],
                  self.editing_order_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("موفقیت", "سفارش با موفقیت بروزرسانی شد!")
            self.cancel_edit()
        else:
            cursor.execute('''
                INSERT INTO orders (clothing_code, customer_name, customer_surname, phone,
                                  clothing_type, price, height, sleeve, shoulder, collar,
                                  chest, skirt, pants_length, leg, order_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (clothing_code, name, surname, phone, clothing_type, price,
                  measurements['height'], measurements['sleeve'], measurements['shoulder'],
                  measurements['collar'], measurements['chest'], measurements['skirt'],
                  measurements['pants_length'], measurements['leg'],
                  order_date))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("موفقیت", "سفارش با موفقیت ذخیره شد!")
            self.clear_order_form()
        
        self.load_customers()
    
    def clear_order_form(self):
        """پاک کردن فرم سفارش"""
        self.entry_clothing_code.delete(0, "end")
        self.entry_name.delete(0, "end")
        self.entry_surname.delete(0, "end")
        self.entry_phone.delete(0, "end")
        self.entry_clothing_type.delete(0, "end")
        self.entry_price.delete(0, "end")
        
        for entry in self.measure_entries.values():
            entry.delete(0, "end")
    
    def cancel_edit(self):
        """لغو حالت ویرایش یا پاک کردن فرم"""
        self.editing_order_id = None
        self.clear_order_form()
        self.order_title_label.configure(text="ثبت سفارش جدید  📝")
        self.btn_save.configure(text="ذخیره سفارش  💾")
    
    def load_customers(self):
        """بارگذاری لیست مشتریان"""
        for widget in self.table_content.winfo_children():
            widget.destroy()
        
        self.selected_order_row = None
        self.selected_order_widget = None
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, customer_name, customer_surname, phone, clothing_code,
                   clothing_type, price, order_date, status
            FROM orders
            ORDER BY id ASC
        ''')
        
        orders = cursor.fetchall()
        conn.close()
        
        for idx, order in enumerate(orders):
            row_number = idx + 1
            self.add_customer_row(order, row_number)
    
    def add_customer_row(self, order, row_number):
        """اضافه کردن ردیف مشتری"""
        row = ctk.CTkFrame(self.table_content, fg_color=COLORS["input_bg"], corner_radius=10)
        row.pack(fill="x", pady=5)
        
        row_grid = ctk.CTkFrame(row, fg_color="transparent")
        row_grid.pack(fill="x", padx=15, pady=12)
        
        for i in range(9):
            row_grid.grid_columnconfigure(i, weight=1, uniform="column")
        
        values = [
            order[8],
            order[7],
            f"{order[6]:,.0f}",
            order[5],
            str(order[4]) if order[4] else "-",
            order[3],
            order[2],
            order[1],
            str(row_number)
        ]
        
        for i, value in enumerate(values):
            lbl = ctk.CTkLabel(
                row_grid,
                text=str(value) if value else "-",
                font=ctk.CTkFont(family=self.font_family, size=13),
                text_color=COLORS["text"]
            )
            lbl.grid(row=0, column=i, sticky="nsew", padx=2)
        
        def on_left_click(event):
            self.select_order_row(order[0], row)
        
        def on_right_click(event):
            self.show_order_context_menu(event, order[0], row)
        
        for widget in row.winfo_children():
            widget.bind("<Button-1>", on_left_click)
            widget.bind("<Button-3>", on_right_click)
            for child in widget.winfo_children():
                child.bind("<Button-1>", on_left_click)
                child.bind("<Button-3>", on_right_click)
    
    def select_order_row(self, order_id, widget):
        """انتخاب یک ردیف سفارش"""
        if self.selected_order_widget:
            self.selected_order_widget.configure(fg_color=COLORS["input_bg"])
        
        widget.configure(fg_color=COLORS["selected_row"])
        
        self.selected_order_row = order_id
        self.selected_order_widget = widget
    
    def edit_selected_order(self):
        """ویرایش سفارش انتخاب شده"""
        if not self.selected_order_row:
            messagebox.showwarning("هشدار", "لطفاً ابتدا یک سفارش را انتخاب کنید!")
            return
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, customer_name, customer_surname, phone, clothing_code,
                   clothing_type, price, height, sleeve, shoulder, collar,
                   chest, skirt, pants_length, leg
            FROM orders WHERE id = ?
        ''', (self.selected_order_row,))
        order = cursor.fetchone()
        conn.close()
        
        if not order:
            messagebox.showerror("خطا", "سفارش پیدا نشد!")
            return
        
        self.editing_order_id = order[0]
        
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, order[1])
        
        self.entry_surname.delete(0, "end")
        self.entry_surname.insert(0, order[2])
        
        self.entry_phone.delete(0, "end")
        self.entry_phone.insert(0, order[3])
        
        self.entry_clothing_code.delete(0, "end")
        if order[4]:
            self.entry_clothing_code.insert(0, str(order[4]))
        
        self.entry_clothing_type.delete(0, "end")
        self.entry_clothing_type.insert(0, order[5])
        
        self.entry_price.delete(0, "end")
        self.entry_price.insert(0, str(order[6]))
        
        measure_keys = ['height', 'sleeve', 'shoulder', 'collar', 'chest', 'skirt', 'pants_length', 'leg']
        for i, key in enumerate(measure_keys):
            self.measure_entries[key].delete(0, "end")
            if order[7 + i] is not None:
                self.measure_entries[key].insert(0, str(order[7 + i]))
        
        code_display = order[4] if order[4] else order[0]
        self.order_title_label.configure(text=f"ویرایش سفارش شماره {code_display}  ✏️")
        self.btn_save.configure(text="بروزرسانی سفارش  💾")
        
        self.show_tab("new_order")
    
    def delete_order(self):
        """حذف سفارش انتخاب شده"""
        if not self.selected_order_row:
            messagebox.showwarning("هشدار", "لطفاً ابتدا یک سفارش را انتخاب کنید!")
            return
        
        confirm = messagebox.askyesno(
            "تأیید حذف", 
            "آیا از حذف این سفارش اطمینان دارید؟"
        )
        
        if confirm:
            conn = sqlite3.connect('doosti.db')
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM orders WHERE id = ?', (self.selected_order_row,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("موفقیت", "سفارش حذف شد!")
            self.selected_order_row = None
            self.selected_order_widget = None
            self.load_customers()
    
    def search_customers(self):
        """جستجو در مشتریان"""
        search_text = self.entry_search.get().strip()
        
        for widget in self.table_content.winfo_children():
            widget.destroy()
        
        self.selected_order_row = None
        self.selected_order_widget = None
        
        if not search_text:
            self.load_customers()
            return
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, customer_name, customer_surname, phone, clothing_code,
                   clothing_type, price, order_date, status
            FROM orders
            WHERE customer_name LIKE ? 
               OR customer_surname LIKE ? 
               OR phone LIKE ?
               OR CAST(clothing_code AS TEXT) LIKE ?
               OR clothing_type LIKE ?
            ORDER BY id ASC
        ''', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', 
              f'%{search_text}%', f'%{search_text}%'))
        
        orders = cursor.fetchall()
        conn.close()
        
        for idx, order in enumerate(orders):
            row_number = idx + 1
            self.add_customer_row(order, row_number)
    
    def save_expense(self):
        """ذخیره مصرف جدید یا بروزرسانی"""
        title = self.entry_expense_title.get().strip()
        amount = self.entry_expense_amount.get().strip()
        
        if not title or not amount:
            messagebox.showerror("خطا", "لطفاً عنوان و مبلغ را وارد کنید!")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("خطا", "مبلغ باید یک عدد باشد!")
            return
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        expense_date = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        
        if self.editing_expense_id:
            cursor.execute('''
                UPDATE expenses SET title = ?, amount = ?
                WHERE id = ?
            ''', (title, amount, self.editing_expense_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("موفقیت", "مصرف با موفقیت بروزرسانی شد!")
            self.cancel_expense_edit()
        else:
            cursor.execute('''
                INSERT INTO expenses (title, amount, date)
                VALUES (?, ?, ?)
            ''', (title, amount, expense_date))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("موفقیت", "مصرف با موفقیت ذخیره شد!")
        
        self.entry_expense_title.delete(0, "end")
        self.entry_expense_amount.delete(0, "end")
        
        self.load_expenses()
    
    def cancel_expense_edit(self):
        """لغو ویرایش مصرف"""
        self.editing_expense_id = None
        self.entry_expense_title.delete(0, "end")
        self.entry_expense_amount.delete(0, "end")
        self.expense_title_label.configure(text="ثبت مصرف جدید  💰")
        self.btn_save_expense.configure(text="ذخیره  💾")
    
    def load_expenses(self):
        """بارگذاری لیست مصارف"""
        for widget in self.expenses_table_content.winfo_children():
            widget.destroy()
        
        self.selected_expense_row = None
        self.selected_expense_widget = None
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, title, amount, date FROM expenses ORDER BY id ASC')
        expenses = cursor.fetchall()
        conn.close()
        
        for idx, expense in enumerate(expenses):
            row_number = idx + 1
            self.add_expense_row(expense, row_number)
    
    def add_expense_row(self, expense, row_number):
        """اضافه کردن ردیف مصرف"""
        row = ctk.CTkFrame(self.expenses_table_content, fg_color=COLORS["input_bg"], corner_radius=10)
        row.pack(fill="x", pady=5)
        
        row_grid = ctk.CTkFrame(row, fg_color="transparent")
        row_grid.pack(fill="x", padx=15, pady=12)
        
        for i in range(4):
            row_grid.grid_columnconfigure(i, weight=1, uniform="column")
        
        values = [
            expense[3],
            f"{expense[2]:,.0f}",
            expense[1],
            str(row_number)
        ]
        
        for i, value in enumerate(values):
            lbl = ctk.CTkLabel(
                row_grid,
                text=str(value) if value else "-",
                font=ctk.CTkFont(family=self.font_family, size=13),
                text_color=COLORS["text"]
            )
            lbl.grid(row=0, column=i, sticky="nsew", padx=2)
        
        def on_left_click(event):
            self.select_expense_row(expense[0], row)
        
        def on_right_click(event):
            self.show_expense_context_menu(event, expense[0], row)
        
        for widget in row.winfo_children():
            widget.bind("<Button-1>", on_left_click)
            widget.bind("<Button-3>", on_right_click)
            for child in widget.winfo_children():
                child.bind("<Button-1>", on_left_click)
                child.bind("<Button-3>", on_right_click)
    
    def select_expense_row(self, expense_id, widget):
        """انتخاب یک ردیف مصرف"""
        if self.selected_expense_widget:
            self.selected_expense_widget.configure(fg_color=COLORS["input_bg"])
        
        widget.configure(fg_color=COLORS["selected_row"])
        
        self.selected_expense_row = expense_id
        self.selected_expense_widget = widget
    
    def edit_selected_expense(self):
        """ویرایش مصرف انتخاب شده"""
        if not self.selected_expense_row:
            messagebox.showwarning("هشدار", "لطفاً ابتدا یک مصرف را انتخاب کنید!")
            return
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM expenses WHERE id = ?', (self.selected_expense_row,))
        expense = cursor.fetchone()
        conn.close()
        
        if not expense:
            messagebox.showerror("خطا", "مصرف پیدا نشد!")
            return
        
        self.editing_expense_id = expense[0]
        
        self.entry_expense_title.delete(0, "end")
        self.entry_expense_title.insert(0, expense[1])
        
        self.entry_expense_amount.delete(0, "end")
        self.entry_expense_amount.insert(0, str(expense[2]))
        
        self.expense_title_label.configure(text=f"ویرایش مصرف  ✏️")
        self.btn_save_expense.configure(text="بروزرسانی  💾")
    
    def delete_expense(self):
        """حذف مصرف انتخاب شده"""
        if not self.selected_expense_row:
            messagebox.showwarning("هشدار", "لطفاً ابتدا یک مصرف را انتخاب کنید!")
            return
        
        confirm = messagebox.askyesno(
            "تأیید حذف", 
            "آیا از حذف این مصرف اطمینان دارید؟"
        )
        
        if confirm:
            conn = sqlite3.connect('doosti.db')
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM expenses WHERE id = ?', (self.selected_expense_row,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("موفقیت", "مصرف حذف شد!")
            self.selected_expense_row = None
            self.selected_expense_widget = None
            self.load_expenses()
    
    def calculate_report(self):
        """محاسبه گزارش مالی"""
        try:
            conn = sqlite3.connect('doosti.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT COALESCE(SUM(price), 0) FROM orders')
            total_income = cursor.fetchone()[0]
            
            cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM expenses')
            total_expenses = cursor.fetchone()[0]
            
            conn.close()
            
            net_profit = total_income - total_expenses
            
            self.income_value.configure(text=f"{total_income:,.0f} افغانی")
            self.expenses_value.configure(text=f"{total_expenses:,.0f} افغانی")
            self.profit_value.configure(text=f"{net_profit:,.0f} افغانی")
            
        except Exception as e:
            print(f"خطا در محاسبه گزارش: {e}")
            self.income_value.configure(text="0 افغانی")
            self.expenses_value.configure(text="0 افغانی")
            self.profit_value.configure(text="0 افغانی")

if __name__ == "__main__":
    app = DoostiTailoringApp()
    app.mainloop()