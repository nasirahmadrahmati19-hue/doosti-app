import flet as ft
import sqlite3
import jdatetime

# تنظیمات ظاهری - رنگ‌های دقیق مطابق کد اصلی
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
    try:
        return f"{float(n):,.0f}"
    except:
        return "0"

def today_shamsi():
    return jdatetime.datetime.now().strftime("%Y/%m/%d")

def now_shamsi():
    return jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")

def safe_float(v):
    try:
        return float(v) if v and str(v).strip() else None
    except:
        return None

def make_field(label_text, hint=""):
    return ft.TextField(
        label=label_text,
        hint_text=hint if hint else label_text,
        bgcolor=COLORS["input_bg"],
        color=COLORS["text"],
        text_align=ft.TextAlign.RIGHT,
        border_color=COLORS["secondary"],
        text_size=14,
        label_style=ft.TextStyle(color=COLORS["text"], weight=ft.FontWeight.BOLD, size=14),
        height=40,
        border_radius=10,
    )


class DoostiTailoringApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "خیاطی دوستی"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = COLORS["primary"]
        self.page.padding = 0
        self.page.rtl = True
        
        # فونت فارسی Vazirmatn
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
    
    # ============================================
    # دیتابیس - دقیقاً مطابق کد اصلی
    # ============================================
    def create_database(self):
        conn = get_db()
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
    
    # ============================================
    # ساخت UI - دقیقاً مطابق کد اصلی
    # ============================================
    def create_modern_ui(self):
        self.create_header()
        self.create_navigation()
        self.content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.add(ft.Column([
            self.header,
            self.nav_bar,
            self.content
        ], expand=True, spacing=0))
        self.show_tab("new_order")
    
    def create_header(self):
        """ایجاد هدر مدرن - RTL با تاریخ شمسی - مطابق کد اصلی"""
        self.header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("خیاطی دوستی  🧵", 
                           size=28, weight=ft.FontWeight.BOLD, color=COLORS["accent"],
                           font_family="Vazirmatn-Bold"),
                    ft.Text("سیستم مدیریت سفارشات", 
                           size=14, color=COLORS["text_muted"],
                           font_family="Vazirmatn"),
                ], horizontal_alignment=ft.CrossAxisAlignment.END),
                ft.Container(
                    ft.Text(f"📅  {today_shamsi()}", 
                           size=14, weight=ft.FontWeight.BOLD, color=COLORS["text"],
                           font_family="Vazirmatn"),
                    bgcolor=COLORS["secondary"],
                    padding=10,
                    border_radius=10,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COLORS["secondary"],
               padding=20,
            height=80,
        )
    
    def create_navigation(self):
        """ایجاد منوی ناوبری مدرن - RTL - مطابق کد اصلی"""
        tabs = [
            ("new_order", "ثبت سفارش  📝"),
            ("customers", "مشتریان  👥"),
            ("expenses", "مصارف  💰"),
            ("report", "گزارش  📊")
        ]
        
        self.nav_buttons = {}
        buttons = []
        for tab_id, text in tabs:
            btn = ft.ElevatedButton(
                text,
                on_click=lambda e, t=tab_id: self.show_tab(t),
                bgcolor=COLORS["card_bg"],
                color=COLORS["text"],
                height=45,
                expand=True,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=12),
                    text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14)
                ),
            )
            buttons.append(btn)
            self.nav_buttons[tab_id] = btn
        
        self.nav_bar = ft.Container(
            content=ft.Row(buttons, spacing=8),
            padding=10,
        )
    
    def show_tab(self, tab_id):
        """نمایش تب انتخاب شده - تغییر رنگ دکمه مطابق کد اصلی"""
        self.content.controls.clear()
        
        # تغییر رنگ دکمه‌ها مطابق کد اصلی
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.bgcolor = COLORS["accent"]
                btn.color = COLORS["primary"]
            else:
                btn.bgcolor = COLORS["card_bg"]
                btn.color = COLORS["text"]
        
        if tab_id == "new_order":
            self.create_new_order_tab()
        elif tab_id == "customers":
            self.create_customers_tab()
        elif tab_id == "expenses":
            self.create_expenses_tab()
        elif tab_id == "report":
            self.create_report_tab()
        
        self.page.update()
    
    def create_section_title(self, text, icon=""):
        """ایجاد عنوان بخش مدرن - RTL - مطابق کد اصلی"""
        display = f"{text}  {icon}" if icon else text
        return ft.Container(
            content=ft.Row([
                ft.Text(display, size=20, weight=ft.FontWeight.BOLD, color=COLORS["accent"],
                       font_family="Vazirmatn-Bold"),
                ft.Container(expand=True, height=2, bgcolor=COLORS["accent"]),
            ], spacing=15),
            padding=15,
        )
    
    # ============================================
    # تب ۱: ثبت سفارش جدید - دو ستون عمودی
    # ============================================
    def create_new_order_tab(self):
        """ایجاد تب ثبت سفارش - دو ستون عمودی مطابق کد اصلی"""
        
        # عنوان - تغییر می‌کند در حالت ویرایش
        title_text = "ثبت سفارش جدید  📝"
        btn_text = "ذخیره سفارش  💾"
        
        if self.editing_order_id:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT clothing_code FROM orders WHERE id=?', (self.editing_order_id,))
            row = cur.fetchone()
            conn.close()
            if row and row[0]:
                title_text = f"ویرایش سفارش شماره {row[0]}  ✏️"
            else:
                title_text = f"ویرایش سفارش شماره {self.editing_order_id}  ✏️"
            btn_text = "بروزرسانی سفارش  💾"
        
        self.order_title_label = ft.Text(
            title_text, size=20, weight=ft.FontWeight.BOLD, color=COLORS["accent"],
            font_family="Vazirmatn-Bold"
        )
        
        title_container = ft.Container(
            content=ft.Row([
                self.order_title_label,
                ft.Container(expand=True, height=2, bgcolor=COLORS["accent"]),
            ], spacing=15),
            padding=15,
        )
        self.content.controls.append(title_container)
        
        # ساخت فیلدها - مطابق کد اصلی
        self.entry_name = make_field("اسم", "نام مشتری")
        self.entry_surname = make_field("تخلص", "تخلص مشتری")
        self.entry_phone = make_field("شماره تلفون", "شماره تلفون")
        self.entry_clothing_code = make_field("کود لباس (عدد)", "کود منحصر به فرد")
        self.entry_clothing_type = make_field("مدل لباس", "مدل لباس")
        self.entry_price = make_field("قیمت لباس (افغانی)", "قیمت")
        
        # اندازه‌ها - مطابق کد اصلی
        self.measure_entries = {}
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
        for label, key in measurements:
            self.measure_entries[key] = make_field(label, "0")
        
        # بارگذاری مقادیر در حالت ویرایش
        if self.editing_order_id:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('''SELECT customer_name, customer_surname, phone, clothing_code,
                clothing_type, price, height, sleeve, shoulder, collar,
                chest, skirt, pants_length, leg FROM orders WHERE id=?''', 
                (self.editing_order_id,))
            o = cur.fetchone()
            conn.close()
            if o:
                self.entry_name.value = o[0] or ''
                self.entry_surname.value = o[1] or ''
                self.entry_phone.value = o[2] or ''
                self.entry_clothing_code.value = str(o[3]) if o[3] else ''
                self.entry_clothing_type.value = o[4] or ''
                self.entry_price.value = str(o[5]) if o[5] else ''
                self.measure_entries['height'].value = str(o[6]) if o[6] else ''
                self.measure_entries['sleeve'].value = str(o[7]) if o[7] else ''
                self.measure_entries['shoulder'].value = str(o[8]) if o[8] else ''
                self.measure_entries['collar'].value = str(o[9]) if o[9] else ''
                self.measure_entries['chest'].value = str(o[10]) if o[10] else ''
                self.measure_entries['skirt'].value = str(o[11]) if o[11] else ''
                self.measure_entries['pants_length'].value = str(o[12]) if o[12] else ''
                self.measure_entries['leg'].value = str(o[13]) if o[13] else ''
        
        # ============================================
        # ستون سمت راست: اطلاعات مشتری (RTL - در راست قرار می‌گیرد)
        # ============================================
        customer_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    ft.Text("اطلاعات مشتری  👤", size=18, weight=ft.FontWeight.BOLD, 
                           color=COLORS["accent"], font_family="Vazirmatn-Bold"),
                    bgcolor=COLORS["secondary"], padding=15, border_radius=15
                ),
                ft.Container(
                    ft.Column([
                        self.entry_name,
                        self.entry_surname,
                        self.entry_phone,
                        self.entry_clothing_code,
                        self.entry_clothing_type,
                        self.entry_price,
                    ], spacing=15),
                    padding=20,
                ),
            ], spacing=0),
            bgcolor=COLORS["card_bg"], border_radius=15,
        )
        
        # ============================================
        # ستون سمت چپ: اندازه‌ها (RTL - در چپ قرار می‌گیرد)
        # ============================================
        measure_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    ft.Text("اندازه‌ها (سانتی‌متر)  📏", size=18, weight=ft.FontWeight.BOLD, 
                           color=COLORS["accent"], font_family="Vazirmatn-Bold"),
                    bgcolor=COLORS["secondary"], padding=15, border_radius=15
                ),
                ft.Container(
                    ft.Column([
                        self.measure_entries['height'],
                        self.measure_entries['sleeve'],
                        self.measure_entries['shoulder'],
                        self.measure_entries['collar'],
                        self.measure_entries['chest'],
                        self.measure_entries['skirt'],
                        self.measure_entries['pants_length'],
                        self.measure_entries['leg'],
                    ], spacing=15),
                    padding=20,
                ),
            ], spacing=0),
            bgcolor=COLORS["card_bg"], border_radius=15,
        )
        
        # دو ستون عمودی - مطابق کد اصلی
        # در RTL: ستون اول سمت راست، ستون دوم سمت چپ
        two_columns = ft.ResponsiveRow([
            ft.Container(customer_card, col={"sm": 12, "md": 6, "lg": 6}),
            ft.Container(measure_card, col={"sm": 12, "md": 6, "lg": 6}),
        ], spacing=10, run_spacing=10)
        
        self.content.controls.append(two_columns)
        
        # ============================================
        # دکمه‌ها - مطابق کد اصلی
        # ============================================
        self.btn_save = ft.ElevatedButton(
            btn_text,
            on_click=lambda e: self.save_order(),
            bgcolor=COLORS["accent"],
            color=COLORS["primary"],
            height=50,
            expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=16)
            ),
        )
        
        self.btn_cancel_edit = ft.ElevatedButton(
            "لغو ویرایش  ❌",
            on_click=lambda e: self.cancel_edit(),
            bgcolor=COLORS["danger"],
            color=COLORS["text"],
            height=50,
            expand=True,
            visible=self.editing_order_id is not None,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14)
            ),
        )
        
        btn_frame = ft.Row([
            self.btn_cancel_edit,
            self.btn_save,
        ], spacing=10)
        
        self.content.controls.append(ft.Container(btn_frame, padding=10))
    
    def save_order(self):
        """ذخیره سفارش - دقیقاً مطابق کد اصلی"""
        clothing_code = (self.entry_clothing_code.value or "").strip()
        name = (self.entry_name.value or "").strip()
        surname = (self.entry_surname.value or "").strip()
        phone = (self.entry_phone.value or "").strip()
        clothing_type = (self.entry_clothing_type.value or "").strip()
        price = (self.entry_price.value or "").strip()
        
        if not all([clothing_code, name, surname, phone, price]):
            self._show_dialog("خطا", "لطفاً تمام فیلدهای ضروری را پر کنید!")
            return
        
        try:
            clothing_code_int = int(clothing_code)
            price_f = float(price)
        except ValueError:
            self._show_dialog("خطا", "کود لباس و قیمت باید عدد باشند!")
            return
        
        if not clothing_type:
            clothing_type = "نامشخص"
        
        if self.check_duplicate_code(clothing_code_int, self.editing_order_id):
            self._show_dialog("خطا", 
                f"کود لباس {clothing_code_int} قبلاً ثبت شده است!\nلطفاً یک کود منحصر به فرد وارد کنید.")
            return
        
        measurements = {}
        for key, entry in self.measure_entries.items():
            value = (entry.value or "").strip()
            measurements[key] = float(value) if value else None
        
        conn = get_db()
        cursor = conn.cursor()
        order_date = now_shamsi()
        
        try:
            if self.editing_order_id:
                cursor.execute('''
                    UPDATE orders SET
                        clothing_code = ?, customer_name = ?, customer_surname = ?,
                        phone = ?, clothing_type = ?, price = ?,
                        height = ?, sleeve = ?, shoulder = ?, collar = ?,
                        chest = ?, skirt = ?, pants_length = ?, leg = ?
                    WHERE id = ?
                ''', (clothing_code_int, name, surname, phone, clothing_type, price_f,
                      measurements['height'], measurements['sleeve'], measurements['shoulder'],
                      measurements['collar'], measurements['chest'], measurements['skirt'],
                      measurements['pants_length'], measurements['leg'],
                      self.editing_order_id))
                conn.commit()
                conn.close()
                self._show_dialog("موفقیت", "سفارش با موفقیت بروزرسانی شد!")
                self.cancel_edit()
            else:
                cursor.execute('''
                    INSERT INTO orders (clothing_code, customer_name, customer_surname, phone,
                                      clothing_type, price, height, sleeve, shoulder, collar,
                                      chest, skirt, pants_length, leg, order_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (clothing_code_int, name, surname, phone, clothing_type, price_f,
                      measurements['height'], measurements['sleeve'], measurements['shoulder'],
                      measurements['collar'], measurements['chest'], measurements['skirt'],
                      measurements['pants_length'], measurements['leg'],
                      order_date))
                conn.commit()
                conn.close()
                self._show_dialog("موفقیت", "سفارش با موفقیت ذخیره شد!")
                self.clear_order_form()
        except Exception as e:
            conn.close()
            self._show_dialog("خطا", f"خطا در ذخیره: {e}")
    
    def clear_order_form(self):
        """پاک کردن فرم سفارش - مطابق کد اصلی"""
        self.entry_clothing_code.value = ""
        self.entry_name.value = ""
        self.entry_surname.value = ""
        self.entry_phone.value = ""
        self.entry_clothing_type.value = ""
        self.entry_price.value = ""
        for entry in self.measure_entries.values():
            entry.value = ""
        self.page.update()
    
    def cancel_edit(self):
        """لغو ویرایش - مطابق کد اصلی"""
        self.editing_order_id = None
        self.clear_order_form()
        self.show_tab("new_order")
    
    # ============================================
    # تب ۲: مشتریان - جدول با هدر طلایی
    # ============================================
    def create_customers_tab(self):
        """ایجاد تب مشتریان - مطابق کد اصلی"""
        self.content.controls.append(self.create_section_title("لیست مشتریان", "👥"))
        
        # کارت جستجو - مطابق کد اصلی
        self.entry_search = make_field(
            "جستجو با اسم، تخلص، موبایل یا کود لباس...  🔍",
            "جستجو..."
        )
        
        self.btn_search = ft.ElevatedButton(
            "جستجو",
            on_click=lambda e: self.search_customers(),
            bgcolor=COLORS["accent"],
            color=COLORS["primary"],
            height=40,
            width=100,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )
        
        self.btn_refresh = ft.ElevatedButton(
            "بروزرسانی  🔄",
            on_click=lambda e: self.load_customers(),
            bgcolor=COLORS["secondary"],
            color=COLORS["text"],
            height=40,
            width=130,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )
        
        search_card = ft.Container(
            content=ft.Row([
                self.btn_refresh,
                self.btn_search,
                ft.Container(self.entry_search, expand=True),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.END),
            bgcolor=COLORS["card_bg"], border_radius=15, padding=20, margin=5,
        )
        self.content.controls.append(search_card)
        
        # جدول - مطابق کد اصلی
        headers = ["وضعیت", "تاریخ", "قیمت", "مدل لباس", "کود لباس", "موبایل", "تخلص", "اسم", "شماره"]
        
        table_header = ft.Container(
            content=ft.Row([
                ft.Text(h, color=COLORS["accent"], weight=ft.FontWeight.BOLD, expand=True, size=12)
                for h in headers
            ], spacing=2),
            bgcolor=COLORS["secondary"], padding=15, border_radius=15,
        )
        self.content.controls.append(table_header)
        
        self.table_content = ft.Column(spacing=5)
        self.content.controls.append(ft.Container(self.table_content, padding=10))
        
        self.load_customers()
    
    def load_customers(self):
        """بارگذاری لیست مشتریان - مطابق کد اصلی"""
        self.table_content.controls.clear()
        self.selected_order_row = None
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, customer_name, customer_surname, phone, clothing_code,
                   clothing_type, price, order_date, status
            FROM orders ORDER BY id ASC
        ''')
        orders = cursor.fetchall()
        conn.close()
        
        for idx, order in enumerate(orders):
            self.add_customer_row(order, idx + 1)
        
        self.page.update()
    
    def add_customer_row(self, order, row_number):
        """اضافه کردن ردیف مشتری - مطابق کد اصلی
        در موبایل راست‌کلیک نداریم، پس دکمه‌های ویرایش/حذف اضافه می‌کنیم"""
        
        values = [
            order[8] or "در حال دوخت",
            order[7] or "-",
            fmt(order[6]),
            order[5] or "-",
            str(order[4]) if order[4] else "-",
            order[3] or "-",
            order[2] or "-",
            order[1] or "-",
            str(row_number)
        ]
        
        row = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(v, color=COLORS["text"], expand=True, size=12)
                    for v in values
                ], spacing=2),
                ft.Row([
                    ft.ElevatedButton(
                        "✏️ ویرایش",
                        on_click=lambda e, oid=order[0]: self.edit_order(oid),
                        bgcolor=COLORS["accent"], color=COLORS["primary"],
                        height=32, width=110,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        "🗑️ حذف",
                        on_click=lambda e, oid=order[0]: self.confirm_delete_order(oid),
                        bgcolor=COLORS["danger"], color=COLORS["text"],
                        height=32, width=110,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ], spacing=10),
            ], spacing=8),
            bgcolor=COLORS["input_bg"],
            padding=15,
            border_radius=10,
            on_click=lambda e, oid=order[0]: self.select_order_row(oid),
        )
        
        # تغییر رنگ در حالت انتخاب
        if self.selected_order_row == order[0]:
            row.bgcolor = COLORS["selected_row"]
        
        self.table_content.controls.append(row)
    
    def select_order_row(self, order_id):
        """انتخاب یک ردیف سفارش - مطابق کد اصلی"""
        self.selected_order_row = order_id
        self.load_customers()
    
    def edit_order(self, order_id):
        """ویرایش سفارش - مطابق کد اصلی"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, customer_name, customer_surname, phone, clothing_code,
                   clothing_type, price, height, sleeve, shoulder, collar,
                   chest, skirt, pants_length, leg
            FROM orders WHERE id = ?
        ''', (order_id,))
        order = cursor.fetchone()
        conn.close()
        
        if not order:
            self._show_dialog("خطا", "سفارش پیدا نشد!")
            return
        
        self.editing_order_id = order[0]
        self.show_tab("new_order")
    
    def confirm_delete_order(self, order_id):
        """تأیید حذف سفارش - معادل messagebox.askyesno"""
        self.selected_order_row = order_id
        self._show_confirm_dialog(
            "تأیید حذف",
            "آیا از حذف این سفارش اطمینان دارید؟",
            lambda: self.delete_order(order_id)
        )
    
    def delete_order(self, order_id):
        """حذف سفارش - مطابق کد اصلی"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
        conn.close()
        
        self._show_dialog("موفقیت", "سفارش حذف شد!")
        self.selected_order_row = None
        self.load_customers()
    
    def search_customers(self):
        """جستجو در مشتریان - مطابق کد اصلی"""
        search_text = (self.entry_search.value or "").strip()
        self.table_content.controls.clear()
        self.selected_order_row = None
        
        if not search_text:
            self.load_customers()
            return
        
        conn = get_db()
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
            self.add_customer_row(order, idx + 1)
        
        self.page.update()
    
    # ============================================
    # تب ۳: مصارف دوکان - مطابق کد اصلی
    # ============================================
    def create_expenses_tab(self):
        """ایجاد تب مصارف - مطابق کد اصلی"""
        self.content.controls.append(self.create_section_title("مصارف دوکان", "💰"))
        
        title_text = "ثبت مصرف جدید  💰"
        btn_text = "ذخیره  💾"
        
        if self.editing_expense_id:
            title_text = "ویرایش مصرف  ✏️"
            btn_text = "بروزرسانی  💾"
        
        self.expense_title_label = ft.Text(
            title_text, size=16, weight=ft.FontWeight.BOLD, color=COLORS["text"],
            font_family="Vazirmatn-Bold"
        )
        
        self.entry_expense_title = make_field("عنوان مصرف", "مثلاً: کرایه دوکان")
        self.entry_expense_amount = make_field("مبلغ (افغانی)", "مبلغ مصرف")
        
        # بارگذاری مقادیر در حالت ویرایش
        if self.editing_expense_id:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT title, amount FROM expenses WHERE id=?', (self.editing_expense_id,))
            e = cur.fetchone()
            conn.close()
            if e:
                self.entry_expense_title.value = e[0] or ''
                self.entry_expense_amount.value = str(e[1]) if e[1] else ''
        
        self.btn_save_expense = ft.ElevatedButton(
            btn_text,
            on_click=lambda e: self.save_expense(),
            bgcolor=COLORS["accent"],
            color=COLORS["primary"],
            height=40,
            width=120,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14)
            ),
        )
        
        self.btn_cancel_expense_edit = ft.ElevatedButton(
            "لغو  ❌",
            on_click=lambda e: self.cancel_expense_edit(),
            bgcolor=COLORS["danger"],
            color=COLORS["text"],
            height=40,
            width=100,
            visible=self.editing_expense_id is not None,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )
        
        form_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    self.expense_title_label,
                    bgcolor=COLORS["secondary"], padding=15, border_radius=15
                ),
                ft.Container(
                    ft.Column([
                        ft.Row([
                            ft.Container(self.entry_expense_title, expand=True),
                            ft.Container(self.entry_expense_amount, expand=True),
                        ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.END),
                        ft.Row([
                            self.btn_cancel_expense_edit,
                            self.btn_save_expense,
                        ], spacing=10),
                    ], spacing=15),
                    padding=20,
                ),
            ], spacing=0),
            bgcolor=COLORS["card_bg"], border_radius=15, margin=5,
        )
        self.content.controls.append(form_card)
        
        # جدول مصارف - مطابق کد اصلی
        headers = ["تاریخ", "مبلغ", "عنوان", "شماره"]
        
        table_header = ft.Container(
            content=ft.Row([
                ft.Text(h, color=COLORS["accent"], weight=ft.FontWeight.BOLD, expand=True, size=13)
                for h in headers
            ], spacing=2),
            bgcolor=COLORS["secondary"], padding=15, border_radius=15,
        )
        self.content.controls.append(table_header)
        
        self.expenses_table_content = ft.Column(spacing=5)
        self.content.controls.append(ft.Container(self.expenses_table_content, padding=10))
        
        self.load_expenses()
    
    def save_expense(self):
        """ذخیره مصرف - مطابق کد اصلی"""
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
        expense_date = now_shamsi()
        
        try:
            if self.editing_expense_id:
                cursor.execute('''
                    UPDATE expenses SET title = ?, amount = ?
                    WHERE id = ?
                ''', (title, amount_f, self.editing_expense_id))
                conn.commit()
                conn.close()
                self._show_dialog("موفقیت", "مصرف با موفقیت بروزرسانی شد!")
                self.cancel_expense_edit()
            else:
                cursor.execute('''
                    INSERT INTO expenses (title, amount, date)
                    VALUES (?, ?, ?)
                ''', (title, amount_f, expense_date))
                conn.commit()
                conn.close()
                self._show_dialog("موفقیت", "مصرف با موفقیت ذخیره شد!")
            
            self.entry_expense_title.value = ""
            self.entry_expense_amount.value = ""
            self.load_expenses()
        except Exception as e:
            conn.close()
            self._show_dialog("خطا", f"خطا: {e}")
    
    def cancel_expense_edit(self):
        """لغو ویرایش مصرف - مطابق کد اصلی"""
        self.editing_expense_id = None
        self.entry_expense_title.value = ""
        self.entry_expense_amount.value = ""
        self.show_tab("expenses")
    
    def load_expenses(self):
        """بارگذاری لیست مصارف - مطابق کد اصلی"""
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
    
    def add_expense_row(self, expense, row_number):
        """اضافه کردن ردیف مصرف - مطابق کد اصلی"""
        values = [
            expense[3] or "-",
            fmt(expense[2]),
            expense[1] or "-",
            str(row_number)
        ]
        
        row = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(v, color=COLORS["text"], expand=True, size=13)
                    for v in values
                ], spacing=2),
                ft.Row([
                    ft.ElevatedButton(
                        "✏️ ویرایش",
                        on_click=lambda e, eid=expense[0]: self.edit_expense(eid),
                        bgcolor=COLORS["accent"], color=COLORS["primary"],
                        height=32, width=110,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        "🗑️ حذف",
                        on_click=lambda e, eid=expense[0]: self.confirm_delete_expense(eid),
                        bgcolor=COLORS["danger"], color=COLORS["text"],
                        height=32, width=110,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ], spacing=10),
            ], spacing=8),
            bgcolor=COLORS["input_bg"],
            padding=15,
            border_radius=10,
            on_click=lambda e, eid=expense[0]: self.select_expense_row(eid),
        )
        
        if self.selected_expense_row == expense[0]:
            row.bgcolor = COLORS["selected_row"]
        
        self.expenses_table_content.controls.append(row)
    
    def select_expense_row(self, expense_id):
        """انتخاب یک ردیف مصرف - مطابق کد اصلی"""
        self.selected_expense_row = expense_id
        self.load_expenses()
    
    def edit_expense(self, expense_id):
        """ویرایش مصرف - مطابق کد اصلی"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
        expense = cursor.fetchone()
        conn.close()
        
        if not expense:
            self._show_dialog("خطا", "مصرف پیدا نشد!")
            return
        
        self.editing_expense_id = expense[0]
        self.show_tab("expenses")
    
    def confirm_delete_expense(self, expense_id):
        """تأیید حذف مصرف - معادل messagebox.askyesno"""
        self.selected_expense_row = expense_id
        self._show_confirm_dialog(
            "تأیید حذف",
            "آیا از حذف این مصرف اطمینان دارید؟",
            lambda: self.delete_expense(expense_id)
        )
    
    def delete_expense(self, expense_id):
        """حذف مصرف - مطابق کد اصلی"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()
        
        self._show_dialog("موفقیت", "مصرف حذف شد!")
        self.selected_expense_row = None
        self.load_expenses()
    
    # ============================================
    # تب ۴: گزارش مالی - مطابق کد اصلی
    # ============================================
    def create_report_tab(self):
        """ایجاد تب گزارش مالی - مطابق کد اصلی"""
        self.content.controls.append(self.create_section_title("گزارش مالی", "📊"))
        
        self.income_value = ft.Text("0 افغانی", size=22, weight=ft.FontWeight.BOLD, 
                                   color=COLORS["success"], font_family="Vazirmatn-Bold")
        self.expenses_value = ft.Text("0 افغانی", size=22, weight=ft.FontWeight.BOLD, 
                                     color=COLORS["danger"], font_family="Vazirmatn-Bold")
        self.profit_value = ft.Text("0 افغانی", size=22, weight=ft.FontWeight.BOLD, 
                                   color=COLORS["accent"], font_family="Vazirmatn-Bold")
        
        income_card = self.create_stat_card("مجموع درآمد  💵", self.income_value, COLORS["success"])
        expenses_card = self.create_stat_card("مجموع مصارف  💸", self.expenses_value, COLORS["danger"])
        profit_card = self.create_stat_card("سود خالص  📈", self.profit_value, COLORS["accent"])
        
        stats_frame = ft.ResponsiveRow([
            ft.Container(income_card, col={"sm": 12, "md": 4, "lg": 4}),
            ft.Container(expenses_card, col={"sm": 12, "md": 4, "lg": 4}),
            ft.Container(profit_card, col={"sm": 12, "md": 4, "lg": 4}),
        ], spacing=10, run_spacing=10)
        
        self.content.controls.append(stats_frame)
        
        self.btn_calculate = ft.ElevatedButton(
            "محاسبه گزارش  🔄",
            on_click=lambda e: self.calculate_report(),
            bgcolor=COLORS["accent"],
            color=COLORS["primary"],
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=16)
            ),
        )
        
        self.content.controls.append(ft.Container(self.btn_calculate, padding=20))
        
        # محاسبه اولیه
        self.calculate_report()
    
    def create_stat_card(self, title, value_widget, color):
        """ایجاد کارت آماری - مطابق کد اصلی"""
        return ft.Container(
            content=ft.Column([
                ft.Container(height=5, bgcolor=color, border_radius=15),
                ft.Container(
                    ft.Column([
                        ft.Text(title, size=13, color=COLORS["text_muted"],
                               font_family="Vazirmatn"),
                        value_widget,
                    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.END),
                    padding=20,
                ),
            ], spacing=0),
            bgcolor=COLORS["card_bg"], border_radius=15,
        )
    
    def calculate_report(self):
        """محاسبه گزارش مالی - مطابق کد اصلی"""
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
            
            if net_profit >= 0:
                self.profit_value.color = COLORS["success"]
            else:
                self.profit_value.color = COLORS["danger"]
            
            self.page.update()
            
        except Exception as e:
            print(f"خطا در محاسبه گزارش: {e}")
            self.income_value.value = "0 افغانی"
            self.expenses_value.value = "0 افغانی"
            self.profit_value.value = "0 افغانی"
            self.page.update()
    
    # ============================================
    # Dialog ها - معادل messagebox
    # ============================================
    def _show_dialog(self, title, message):
        """نمایش پیام - معادل messagebox"""
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text(title, font_family="Vazirmatn-Bold", weight=ft.FontWeight.BOLD),
            content=ft.Text(message, font_family="Vazirmatn"),
            actions=[
                ft.TextButton("باشه", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    def _show_confirm_dialog(self, title, message, on_confirm):
        """نمایش تأیید - معادل messagebox.askyesno"""
        dlg = None
        
        def on_yes(e):
            dlg.open = False
            self.page.update()
            on_confirm()
        
        def on_no(e):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text(title, font_family="Vazirmatn-Bold", weight=ft.FontWeight.BOLD),
            content=ft.Text(message, font_family="Vazirmatn"),
            actions=[
                ft.TextButton("بله", on_click=on_yes),
                ft.TextButton("خیر", on_click=on_no),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()


def main(page: ft.Page):
    DoostiTailoringApp(page)

ft.app(target=main)
