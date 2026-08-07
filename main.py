import flet as ft
import sqlite3
import jdatetime

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

DB_FILE = 'doosti.db'

def get_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def fmt(n):
    try: return f"{float(n):,.0f}"
    except: return "0"

def today_shamsi():
    return jdatetime.datetime.now().strftime("%Y/%m/%d")

def now_shamsi():
    return jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")

def safe_float(v):
    try: return float(v) if v and str(v).strip() else None
    except: return None

def make_field(label_text, hint=""):
    return ft.TextField(
        label=label_text,
        hint_text=hint if hint else label_text,
        bgcolor=COLORS["input_bg"],
        color=COLORS["text"],
        text_align="right",
        border_color=COLORS["secondary"],
        text_size=14,
        label_style=ft.TextStyle(color=COLORS["text"], weight="bold", size=14),
        height=40,
        border_radius=10,
    )


class DoostiTailoringApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "خیاطی دوستی"
        self.page.theme_mode = "dark"
        self.page.bgcolor = COLORS["primary"]
        self.page.padding = 0
        self.page.rtl = True
        
        self.page.fonts = {
            "Vazirmatn": "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Regular.ttf",
            "Vazirmatn-Bold": "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Bold.ttf",
        }
        self.page.theme = ft.Theme(font_family="Vazirmatn")
        self.font_family = "Vazirmatn"
        
        self.editing_order_id = None
        self.editing_expense_id = None
        self.selected_order_row = None
        self.selected_expense_row = None
        
        self.create_database()
        self.migrate_database()
        self.create_modern_ui()
    
    def create_database(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL, customer_surname TEXT NOT NULL,
            phone TEXT NOT NULL, clothing_code INTEGER UNIQUE,
            clothing_type TEXT NOT NULL, price REAL NOT NULL,
            height REAL, sleeve REAL, shoulder REAL, collar REAL,
            chest REAL, skirt REAL, pants_length REAL, leg REAL,
            order_date TEXT, status TEXT DEFAULT 'در حال دوخت'
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, amount REAL NOT NULL, date TEXT
        )''')
        conn.commit()
        conn.close()
    
    def migrate_database(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'clothing_code' not in columns:
            cursor.execute('ALTER TABLE orders ADD COLUMN clothing_code INTEGER')
        conn.commit()
        conn.close()
    
    def check_duplicate_code(self, code, exclude_id=None):
        conn = get_db()
        cursor = conn.cursor()
        if exclude_id:
            cursor.execute('SELECT id FROM orders WHERE clothing_code = ? AND id != ?', (code, exclude_id))
        else:
            cursor.execute('SELECT id FROM orders WHERE clothing_code = ?', (code,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def create_modern_ui(self):
        self.create_header()
        self.create_navigation()
        self.content = ft.Column(scroll="auto", expand=True)
        self.page.add(ft.Column([self.header, self.nav_bar, self.content], expand=True, spacing=0))
        self.show_tab("new_order")
    
    def create_header(self):
        self.header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("خیاطی دوستی  🧵", size=24, weight="bold", color=COLORS["accent"], font_family="Vazirmatn-Bold"),
                    ft.Text("سیستم مدیریت سفارشات", size=12, color=COLORS["text_muted"], font_family="Vazirmatn"),
                ], horizontal_alignment="end"),
                ft.Container(
                    ft.Text(f"📅 {today_shamsi()}", size=12, weight="bold", color=COLORS["text"], font_family="Vazirmatn"),
                    bgcolor=COLORS["secondary"], padding=8, border_radius=10,
                ),
            ], alignment="spaceBetween", vertical_alignment="center"),
            bgcolor=COLORS["secondary"], padding=15,
        )
    
    def create_navigation(self):
        tabs = [
            ("new_order", "📝 سفارش"),
            ("customers", "👥 مشتریان"),
            ("expenses", "💰 مصارف"),
            ("report", "📊 گزارش")
        ]
        self.nav_buttons = {}
        buttons = []
        for tab_id, text in tabs:
            btn = ft.ElevatedButton(text, on_click=lambda e, t=tab_id: self.show_tab(t),
                bgcolor=COLORS["card_bg"], color=COLORS["text"], height=45, expand=True,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12),
                                    text_style=ft.TextStyle(weight="bold", size=13)))
            buttons.append(btn)
            self.nav_buttons[tab_id] = btn
        self.nav_bar = ft.Container(content=ft.Row(buttons, spacing=6), padding=8)
    
    def show_tab(self, tab_id):
        self.content.controls.clear()
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.bgcolor = COLORS["accent"]
                btn.color = COLORS["primary"]
            else:
                btn.bgcolor = COLORS["card_bg"]
                btn.color = COLORS["text"]
        
        if tab_id == "new_order": self.create_new_order_tab()
        elif tab_id == "customers": self.create_customers_tab()
        elif tab_id == "expenses": self.create_expenses_tab()
        elif tab_id == "report": self.create_report_tab()
        self.page.update()
    
    # ✅ عنوان بخش با wrap برای موبایل
    def create_section_title(self, text, icon=""):
        display = f"{text}  {icon}" if icon else text
        return ft.Container(
            content=ft.Column([
                ft.Text(display, size=18, weight="bold", color=COLORS["accent"],
                       font_family="Vazirmatn-Bold", text_align="right", no_wrap=False),
                ft.Container(height=2, bgcolor=COLORS["accent"], border_radius=2),
            ], spacing=8, horizontal_alignment="stretch"),
            padding=15,
        )
    
    def create_new_order_tab(self):
        title_text = "ثبت سفارش جدید  📝"
        btn_text = "ذخیره سفارش  💾"
        if self.editing_order_id:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT clothing_code FROM orders WHERE id=?', (self.editing_order_id,))
            row = cur.fetchone()
            conn.close()
            title_text = f"ویرایش سفارش شماره {row[0] if row and row[0] else self.editing_order_id}  ✏️"
            btn_text = "بروزرسانی سفارش  💾"
        
        self.order_title_label = ft.Text(title_text, size=18, weight="bold", color=COLORS["accent"],
                                        font_family="Vazirmatn-Bold", text_align="right", no_wrap=False)
        self.content.controls.append(ft.Container(
            content=ft.Column([self.order_title_label, ft.Container(height=2, bgcolor=COLORS["accent"], border_radius=2)],
                             spacing=8, horizontal_alignment="stretch"),
            padding=15))
        
        self.entry_name = make_field("اسم", "نام مشتری")
        self.entry_surname = make_field("تخلص", "تخلص مشتری")
        self.entry_phone = make_field("شماره تلفون", "شماره تلفون")
        self.entry_clothing_code = make_field("کود لباس (عدد)", "کود منحصر به فرد")
        self.entry_clothing_type = make_field("مدل لباس", "مدل لباس")
        self.entry_price = make_field("قیمت لباس (افغانی)", "قیمت")
        
        self.measure_entries = {}
        for label, key in [("قد", "height"), ("آستین", "sleeve"), ("شانه", "shoulder"), ("یخن", "collar"),
                           ("بغل", "chest"), ("بردامن", "skirt"), ("قد تنبان", "pants_length"), ("پاچه", "leg")]:
            self.measure_entries[key] = make_field(label, "0")
        
        if self.editing_order_id:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT customer_name, customer_surname, phone, clothing_code, clothing_type, price, height, sleeve, shoulder, collar, chest, skirt, pants_length, leg FROM orders WHERE id=?', (self.editing_order_id,))
            o = cur.fetchone()
            conn.close()
            if o:
                self.entry_name.value, self.entry_surname.value, self.entry_phone.value = o[0] or '', o[1] or '', o[2] or ''
                self.entry_clothing_code.value, self.entry_clothing_type.value, self.entry_price.value = str(o[3]) if o[3] else '', o[4] or '', str(o[5]) if o[5] else ''
                self.measure_entries['height'].value, self.measure_entries['sleeve'].value = str(o[6]) if o[6] else '', str(o[7]) if o[7] else ''
                self.measure_entries['shoulder'].value, self.measure_entries['collar'].value = str(o[8]) if o[8] else '', str(o[9]) if o[9] else ''
                self.measure_entries['chest'].value, self.measure_entries['skirt'].value = str(o[10]) if o[10] else '', str(o[11]) if o[11] else ''
                self.measure_entries['pants_length'].value, self.measure_entries['leg'].value = str(o[12]) if o[12] else '', str(o[13]) if o[13] else ''
        
        customer_card = ft.Container(
            content=ft.Column([
                ft.Container(ft.Text("اطلاعات مشتری  👤", size=16, weight="bold", color=COLORS["accent"],
                                    font_family="Vazirmatn-Bold", text_align="right"),
                           bgcolor=COLORS["secondary"], padding=12, border_radius=15),
                ft.Container(ft.Column([self.entry_name, self.entry_surname, self.entry_phone,
                                       self.entry_clothing_code, self.entry_clothing_type, self.entry_price],
                                      spacing=12), padding=15),
            ], spacing=0),
            bgcolor=COLORS["card_bg"], border_radius=15)
        
        measure_card = ft.Container(
            content=ft.Column([
                ft.Container(ft.Text("اندازه‌ها (سانتی‌متر)  📏", size=16, weight="bold", color=COLORS["accent"],
                                    font_family="Vazirmatn-Bold", text_align="right"),
                           bgcolor=COLORS["secondary"], padding=12, border_radius=15),
                ft.Container(ft.Column([self.measure_entries['height'], self.measure_entries['sleeve'],
                                       self.measure_entries['shoulder'], self.measure_entries['collar'],
                                       self.measure_entries['chest'], self.measure_entries['skirt'],
                                       self.measure_entries['pants_length'], self.measure_entries['leg']],
                                      spacing=12), padding=15),
            ], spacing=0),
            bgcolor=COLORS["card_bg"], border_radius=15)
        
        self.content.controls.append(ft.ResponsiveRow([
            ft.Container(customer_card, col={"sm": 12, "md": 6, "lg": 6}),
            ft.Container(measure_card, col={"sm": 12, "md": 6, "lg": 6}),
        ], spacing=10, run_spacing=10))
        
        self.btn_save = ft.ElevatedButton(btn_text, on_click=lambda e: self.save_order(),
            bgcolor=COLORS["accent"], color=COLORS["primary"], height=50, expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12),
                                text_style=ft.TextStyle(weight="bold", size=15)))
        self.btn_cancel_edit = ft.ElevatedButton("لغو ویرایش  ❌", on_click=lambda e: self.cancel_edit(),
            bgcolor=COLORS["danger"], color=COLORS["text"], height=50, expand=True,
            visible=self.editing_order_id is not None,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12),
                                text_style=ft.TextStyle(weight="bold", size=14)))
        self.content.controls.append(ft.Container(ft.Row([self.btn_cancel_edit, self.btn_save], spacing=10), padding=10))
    
    def save_order(self):
        clothing_code = (self.entry_clothing_code.value or "").strip()
        name = (self.entry_name.value or "").strip()
        surname = (self.entry_surname.value or "").strip()
        phone = (self.entry_phone.value or "").strip()
        clothing_type = (self.entry_clothing_type.value or "").strip() or "نامشخص"
        price = (self.entry_price.value or "").strip()
        
        if not all([clothing_code, name, surname, phone, price]):
            self._show_dialog("خطا", "لطفاً تمام فیلدهای ضروری را پر کنید!")
            return
        try:
            clothing_code_int, price_f = int(clothing_code), float(price)
        except ValueError:
            self._show_dialog("خطا", "کود لباس و قیمت باید عدد باشند!")
            return
        
        if self.check_duplicate_code(clothing_code_int, self.editing_order_id):
            self._show_dialog("خطا", f"کود لباس {clothing_code_int} قبلاً ثبت شده است!")
            return
        
        measurements = {key: safe_float(entry.value) for key, entry in self.measure_entries.items()}
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            if self.editing_order_id:
                cursor.execute('UPDATE orders SET clothing_code=?, customer_name=?, customer_surname=?, phone=?, clothing_type=?, price=?, height=?, sleeve=?, shoulder=?, collar=?, chest=?, skirt=?, pants_length=?, leg=? WHERE id=?',
                    (clothing_code_int, name, surname, phone, clothing_type, price_f,
                     measurements['height'], measurements['sleeve'], measurements['shoulder'],
                     measurements['collar'], measurements['chest'], measurements['skirt'],
                     measurements['pants_length'], measurements['leg'], self.editing_order_id))
            else:
                cursor.execute('INSERT INTO orders (clothing_code, customer_name, customer_surname, phone, clothing_type, price, height, sleeve, shoulder, collar, chest, skirt, pants_length, leg, order_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (clothing_code_int, name, surname, phone, clothing_type, price_f,
                     measurements['height'], measurements['sleeve'], measurements['shoulder'],
                     measurements['collar'], measurements['chest'], measurements['skirt'],
                     measurements['pants_length'], measurements['leg'], now_shamsi()))
            conn.commit()
            conn.close()
            self._show_dialog("موفقیت", "سفارش با موفقیت ذخیره/بروزرسانی شد!")
            self.cancel_edit()
        except Exception as e:
            conn.close()
            self._show_dialog("خطا", f"خطا در ذخیره: {e}")
    
    def clear_order_form(self):
        for entry in [self.entry_clothing_code, self.entry_name, self.entry_surname, self.entry_phone,
                     self.entry_clothing_type, self.entry_price] + list(self.measure_entries.values()):
            entry.value = ""
        self.page.update()
    
    def cancel_edit(self):
        self.editing_order_id = None
        self.clear_order_form()
        self.show_tab("new_order")
    
    # ✅ تب مشتریان - فیلد جستجو بالا، دکمه‌ها زیر آن، RTL کامل
    def create_customers_tab(self):
        self.content.controls.append(self.create_section_title("لیست مشتریان", "👥"))
        
        # ✅ فیلد جستجو در بالا (تمام عرض)
        self.entry_search = make_field("جستجو با اسم، تخلص، موبایل یا کود لباس...  🔍", "جستجو...")
        
        # ✅ دکمه‌های جستجو و بروزرسانی زیر فیلد جستجو
        self.btn_search = ft.ElevatedButton("🔍 جستجو", on_click=lambda e: self.search_customers(),
            bgcolor=COLORS["accent"], color=COLORS["primary"], height=45, expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10),
                                text_style=ft.TextStyle(weight="bold", size=14)))
        self.btn_refresh = ft.ElevatedButton("🔄 بروزرسانی", on_click=lambda e: self.load_customers(),
            bgcolor=COLORS["secondary"], color=COLORS["text"], height=45, expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10),
                                text_style=ft.TextStyle(weight="bold", size=14)))
        
        # ✅ چیدمان: فیلد بالا، دکمه‌ها زیر آن
        search_card = ft.Container(
            content=ft.Column([
                self.entry_search,
                ft.Row([self.btn_search, self.btn_refresh], spacing=10),
            ], spacing=12),
            bgcolor=COLORS["card_bg"], border_radius=15, padding=15, margin=5)
        self.content.controls.append(search_card)
        
        # ✅ لیست مشتریان به صورت کارت‌های عمودی (RTL)
        self.table_content = ft.Column(spacing=8)
        self.content.controls.append(ft.Container(self.table_content, padding=5))
        self.load_customers()
    
    def load_customers(self):
        self.table_content.controls.clear()
        self.selected_order_row = None
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, customer_name, customer_surname, phone, clothing_code, clothing_type, price, order_date, status FROM orders ORDER BY id ASC')
        orders = cursor.fetchall()
        conn.close()
        for idx, order in enumerate(orders):
            self.add_customer_row(order, idx + 1)
        self.page.update()
    
    # ✅ کارت مشتری RTL - اطلاعات عمودی و خوانا در موبایل
    def add_customer_row(self, order, row_number):
        order_id, name, surname, phone, code, ctype, price, date, status = order
        
        # ✅ کارت با اطلاعات عمودی - RTL
        card = ft.Container(
            content=ft.Column([
                # ردیف اول: شماره و نام
                ft.Row([
                    ft.Text(f"#{row_number}", size=14, weight="bold", color=COLORS["accent"]),
                    ft.Text(f"{name} {surname}", size=15, weight="bold", color=COLORS["text"],
                           expand=True, text_align="right"),
                ], alignment="spaceBetween"),
                
                ft.Divider(height=1, color=COLORS["secondary"]),
                
                # اطلاعات با label:value
                ft.Row([
                    ft.Text("📱 تلفون:", size=12, weight="bold", color=COLORS["text_muted"], width=80),
                    ft.Text(phone or "-", size=13, color=COLORS["text"], expand=True, text_align="right"),
                ]),
                ft.Row([
                    ft.Text("👔 کود لباس:", size=12, weight="bold", color=COLORS["text_muted"], width=80),
                    ft.Text(str(code) if code else "-", size=13, color=COLORS["text"], expand=True, text_align="right"),
                ]),
                ft.Row([
                    ft.Text("🧵 مدل:", size=12, weight="bold", color=COLORS["text_muted"], width=80),
                    ft.Text(ctype or "-", size=13, color=COLORS["text"], expand=True, text_align="right"),
                ]),
                ft.Row([
                    ft.Text("💰 قیمت:", size=12, weight="bold", color=COLORS["text_muted"], width=80),
                    ft.Text(f"{fmt(price)} افغانی", size=14, weight="bold", color=COLORS["success"],
                           expand=True, text_align="right"),
                ]),
                ft.Row([
                    ft.Text("📅 تاریخ:", size=12, weight="bold", color=COLORS["text_muted"], width=80),
                    ft.Text(date or "-", size=13, color=COLORS["text"], expand=True, text_align="right"),
                ]),
                ft.Row([
                    ft.Text("📌 وضعیت:", size=12, weight="bold", color=COLORS["text_muted"], width=80),
                    ft.Text(status or "در حال دوخت", size=13, color=COLORS["text"], expand=True, text_align="right"),
                ]),
                
                ft.Divider(height=1, color=COLORS["secondary"]),
                
                # دکمه‌های عملیات
                ft.Row([
                    ft.ElevatedButton("✏️ ویرایش", on_click=lambda e, oid=order_id: self.edit_order(oid),
                        bgcolor=COLORS["accent"], color=COLORS["primary"], height=38, expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8),
                                            text_style=ft.TextStyle(weight="bold", size=13))),
                    ft.ElevatedButton("🗑️ حذف", on_click=lambda e, oid=order_id: self.confirm_delete_order(oid),
                        bgcolor=COLORS["danger"], color=COLORS["text"], height=38, expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8),
                                            text_style=ft.TextStyle(weight="bold", size=13))),
                ], spacing=10),
            ], spacing=8),
            bgcolor=COLORS["input_bg"] if self.selected_order_row != order_id else COLORS["selected_row"],
            padding=15, border_radius=12,
            border=ft.border.all(2, COLORS["accent"] if self.selected_order_row == order_id else COLORS["secondary"]),
            on_click=lambda e, oid=order_id: self.select_order_row(oid))
        
        self.table_content.controls.append(card)
    
    def select_order_row(self, order_id):
        self.selected_order_row = order_id
        self.load_customers()
    
    def edit_order(self, order_id):
        self.editing_order_id = order_id
        self.show_tab("new_order")
    
    def confirm_delete_order(self, order_id):
        self.selected_order_row = order_id
        self._show_confirm_dialog("تأیید حذف", "آیا از حذف این سفارش اطمینان دارید؟",
                                 lambda: self.delete_order(order_id))
    
    def delete_order(self, order_id):
        conn = get_db()
        conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
        conn.close()
        self._show_dialog("موفقیت", "سفارش حذف شد!")
        self.selected_order_row = None
        self.load_customers()
    
    def search_customers(self):
        search_text = (self.entry_search.value or "").strip()
        self.table_content.controls.clear()
        self.selected_order_row = None
        if not search_text:
            self.load_customers()
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, customer_name, customer_surname, phone, clothing_code, clothing_type, price, order_date, status FROM orders WHERE customer_name LIKE ? OR customer_surname LIKE ? OR phone LIKE ? OR CAST(clothing_code AS TEXT) LIKE ? OR clothing_type LIKE ? ORDER BY id ASC',
            (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
        orders = cursor.fetchall()
        conn.close()
        for idx, order in enumerate(orders):
            self.add_customer_row(order, idx + 1)
        self.page.update()
    
    # ✅ تب مصارف - RTL کامل
    def create_expenses_tab(self):
        self.content.controls.append(self.create_section_title("مصارف دوکان", "💰"))
        
        title_text = "ویرایش مصرف  ✏️" if self.editing_expense_id else "ثبت مصرف جدید  💰"
        btn_text = "بروزرسانی  💾" if self.editing_expense_id else "ذخیره  💾"
        self.expense_title_label = ft.Text(title_text, size=16, weight="bold", color=COLORS["text"],
                                          font_family="Vazirmatn-Bold", text_align="right")
        self.entry_expense_title = make_field("عنوان مصرف", "مثلاً: کرایه دوکان")
        self.entry_expense_amount = make_field("مبلغ (افغانی)", "مبلغ مصرف")
        
        if self.editing_expense_id:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT title, amount FROM expenses WHERE id=?', (self.editing_expense_id,))
            e = cur.fetchone()
            conn.close()
            if e:
                self.entry_expense_title.value, self.entry_expense_amount.value = e[0] or '', str(e[1]) if e[1] else ''
        
        self.btn_save_expense = ft.ElevatedButton(btn_text, on_click=lambda e: self.save_expense(),
            bgcolor=COLORS["accent"], color=COLORS["primary"], height=45, expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10),
                                text_style=ft.TextStyle(weight="bold", size=14)))
        self.btn_cancel_expense_edit = ft.ElevatedButton("لغو  ❌", on_click=lambda e: self.cancel_expense_edit(),
            bgcolor=COLORS["danger"], color=COLORS["text"], height=45, expand=True,
            visible=self.editing_expense_id is not None,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10),
                                text_style=ft.TextStyle(weight="bold", size=14)))
        
        self.content.controls.append(ft.Container(
            content=ft.Column([
                ft.Container(self.expense_title_label, bgcolor=COLORS["secondary"], padding=12, border_radius=15),
                ft.Container(ft.Column([
                    self.entry_expense_title,
                    self.entry_expense_amount,
                    ft.Row([self.btn_cancel_expense_edit, self.btn_save_expense], spacing=10),
                ], spacing=12), padding=15),
            ], spacing=0),
            bgcolor=COLORS["card_bg"], border_radius=15, margin=5))
        
        # ✅ لیست مصارف به صورت کارت‌های عمودی (RTL)
        self.expenses_table_content = ft.Column(spacing=8)
        self.content.controls.append(ft.Container(self.expenses_table_content, padding=5))
        self.load_expenses()
    
    def save_expense(self):
        title = (self.entry_expense_title.value or "").strip()
        amount = (self.entry_expense_amount.value or "").strip()
        if not title or not amount:
            self._show_dialog("خطا", "لطفاً عنوان و مبلغ را وارد کنید!")
            return
        try:
            amount_f = float(amount)
        except ValueError:
            self._show_dialog("خطا", "مبلغ باید یک عدد باشد!")
            return
        
        conn = get_db()
        cursor = conn.cursor()
        try:
            if self.editing_expense_id:
                cursor.execute('UPDATE expenses SET title = ?, amount = ? WHERE id = ?',
                    (title, amount_f, self.editing_expense_id))
            else:
                cursor.execute('INSERT INTO expenses (title, amount, date) VALUES (?, ?, ?)',
                    (title, amount_f, now_shamsi()))
            conn.commit()
            conn.close()
            self._show_dialog("موفقیت", "مصرف با موفقیت ذخیره/بروزرسانی شد!")
            self.entry_expense_title.value, self.entry_expense_amount.value = "", ""
            self.cancel_expense_edit()
        except Exception as e:
            conn.close()
            self._show_dialog("خطا", f"خطا: {e}")
    
    def cancel_expense_edit(self):
        self.editing_expense_id = None
        self.entry_expense_title.value, self.entry_expense_amount.value = "", ""
        self.show_tab("expenses")
    
    def load_expenses(self):
        self.expenses_table_content.controls.clear()
        self.selected_expense_row = None
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, amount, date FROM expenses ORDER BY id ASC')
        expenses = cursor.fetchall()
        conn.close()
        for idx, expense in enumerate(expenses):
            self.add_expense_row(expense, idx + 1)
        self.page.update()
    
    # ✅ کارت مصرف RTL - اطلاعات عمودی و خوانا
    def add_expense_row(self, expense, row_number):
        exp_id, title, amount, date = expense
        
        card = ft.Container(
            content=ft.Column([
                # ردیف اول: شماره و عنوان
                ft.Row([
                    ft.Text(f"#{row_number}", size=14, weight="bold", color=COLORS["danger"]),
                    ft.Text(title or "-", size=15, weight="bold", color=COLORS["text"],
                           expand=True, text_align="right"),
                ], alignment="spaceBetween"),
                
                ft.Divider(height=1, color=COLORS["secondary"]),
                
                # مبلغ
                ft.Row([
                    ft.Text("💰 مبلغ:", size=12, weight="bold", color=COLORS["text_muted"], width=70),
                    ft.Text(f"{fmt(amount)} افغانی", size=15, weight="bold", color=COLORS["danger"],
                           expand=True, text_align="right"),
                ]),
                
                # تاریخ
                ft.Row([
                    ft.Text("📅 تاریخ:", size=12, weight="bold", color=COLORS["text_muted"], width=70),
                    ft.Text(date or "-", size=13, color=COLORS["text"], expand=True, text_align="right"),
                ]),
                
                ft.Divider(height=1, color=COLORS["secondary"]),
                
                # دکمه‌ها
                ft.Row([
                    ft.ElevatedButton("✏️ ویرایش", on_click=lambda e, eid=exp_id: self.edit_expense(eid),
                        bgcolor=COLORS["accent"], color=COLORS["primary"], height=38, expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8),
                                            text_style=ft.TextStyle(weight="bold", size=13))),
                    ft.ElevatedButton("🗑️ حذف", on_click=lambda e, eid=exp_id: self.confirm_delete_expense(eid),
                        bgcolor=COLORS["danger"], color=COLORS["text"], height=38, expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8),
                                            text_style=ft.TextStyle(weight="bold", size=13))),
                ], spacing=10),
            ], spacing=8),
            bgcolor=COLORS["input_bg"] if self.selected_expense_row != exp_id else COLORS["selected_row"],
            padding=15, border_radius=12,
            border=ft.border.all(2, COLORS["danger"] if self.selected_expense_row == exp_id else COLORS["secondary"]),
            on_click=lambda e, eid=exp_id: self.select_expense_row(eid))
        
        self.expenses_table_content.controls.append(card)
    
    def select_expense_row(self, expense_id):
        self.selected_expense_row = expense_id
        self.load_expenses()
    
    def edit_expense(self, expense_id):
        self.editing_expense_id = expense_id
        self.show_tab("expenses")
    
    def confirm_delete_expense(self, expense_id):
        self.selected_expense_row = expense_id
        self._show_confirm_dialog("تأیید حذف", "آیا از حذف این مصرف اطمینان دارید؟",
                                 lambda: self.delete_expense(expense_id))
    
    def delete_expense(self, expense_id):
        conn = get_db()
        conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()
        self._show_dialog("موفقیت", "مصرف حذف شد!")
        self.selected_expense_row = None
        self.load_expenses()
    
    def create_report_tab(self):
        self.content.controls.append(self.create_section_title("گزارش مالی", "📊"))
        self.income_value = ft.Text("0 افغانی", size=22, weight="bold", color=COLORS["success"],
                                   font_family="Vazirmatn-Bold", text_align="right")
        self.expenses_value = ft.Text("0 افغانی", size=22, weight="bold", color=COLORS["danger"],
                                     font_family="Vazirmatn-Bold", text_align="right")
        self.profit_value = ft.Text("0 افغانی", size=22, weight="bold", color=COLORS["accent"],
                                   font_family="Vazirmatn-Bold", text_align="right")
        
        income_card = self.create_stat_card("💵 مجموع درآمد", self.income_value, COLORS["success"])
        expenses_card = self.create_stat_card("💸 مجموع مصارف", self.expenses_value, COLORS["danger"])
        profit_card = self.create_stat_card("📈 سود خالص", self.profit_value, COLORS["accent"])
        
        self.content.controls.append(ft.ResponsiveRow([
            ft.Container(income_card, col={"sm": 12, "md": 4, "lg": 4}),
            ft.Container(expenses_card, col={"sm": 12, "md": 4, "lg": 4}),
            ft.Container(profit_card, col={"sm": 12, "md": 4, "lg": 4}),
        ], spacing=10, run_spacing=10))
        
        self.content.controls.append(ft.Container(
            ft.ElevatedButton("محاسبه گزارش  🔄", on_click=lambda e: self.calculate_report(),
                bgcolor=COLORS["accent"], color=COLORS["primary"], height=50,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12),
                                    text_style=ft.TextStyle(weight="bold", size=16))),
            padding=20))
        self.calculate_report()
    
    def create_stat_card(self, title, value_widget, color):
        return ft.Container(
            content=ft.Column([
                ft.Container(height=5, bgcolor=color, border_radius=15),
                ft.Container(ft.Column([
                    ft.Text(title, size=13, color=COLORS["text_muted"], font_family="Vazirmatn",
                           text_align="right"),
                    value_widget,
                ], spacing=10, horizontal_alignment="end"), padding=20),
            ], spacing=0),
            bgcolor=COLORS["card_bg"], border_radius=15)
    
    def calculate_report(self):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT COALESCE(SUM(price), 0) FROM orders')
            total_income = cursor.fetchone()[0]
            cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM expenses')
            total_expenses = cursor.fetchone()[0]
            conn.close()
            
            net_profit = total_income - total_expenses
            self.income_value.value = f"{total_income:,.0f} افغانی"
            self.expenses_value.value = f"{total_expenses:,.0f} افغانی"
            self.profit_value.value = f"{net_profit:,.0f} افغانی"
            self.profit_value.color = COLORS["success"] if net_profit >= 0 else COLORS["danger"]
            self.page.update()
        except Exception as e:
            self.income_value.value, self.expenses_value.value, self.profit_value.value = "0 افغانی", "0 افغانی", "0 افغانی"
            self.page.update()
    
    def _show_dialog(self, title, message):
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        dlg = ft.AlertDialog(
            title=ft.Text(title, font_family="Vazirmatn-Bold", weight="bold"),
            content=ft.Text(message, font_family="Vazirmatn"),
            actions=[ft.TextButton("باشه", on_click=close_dlg)],
            actions_alignment="end")
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    def _show_confirm_dialog(self, title, message, on_confirm):
        dlg = None
        def on_yes(e):
            dlg.open = False
            self.page.update()
            on_confirm()
        def on_no(e):
            dlg.open = False
            self.page.update()
        dlg = ft.AlertDialog(
            title=ft.Text(title, font_family="Vazirmatn-Bold", weight="bold"),
            content=ft.Text(message, font_family="Vazirmatn"),
            actions=[ft.TextButton("بله", on_click=on_yes), ft.TextButton("خیر", on_click=on_no)],
            actions_alignment="end")
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

def main(page: ft.Page):
    DoostiTailoringApp(page)

ft.run(main)
