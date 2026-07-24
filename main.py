import flet as ft
import sqlite3
import jdatetime
import os

# ============================================
# رنگ‌های سفارشی
# ============================================
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

# ============================================
# توابع کمکی
# ============================================
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

# ============================================
# کلاس اصلی برنامه
# ============================================
class DoostiTailoringApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "خیاطی دوستی"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = COLORS["primary"]
        self.page.padding = 0
        self.page.rtl = True
        
        self.page.fonts = {
            "Vazirmatn": "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Regular.ttf",
        }
        self.page.theme = ft.Theme(font_family="Vazirmatn")
        self.font_family = "Vazirmatn"
        
        self.editing_order_id = None
        self.editing_expense_id = None
        self.selected_order_row = None
        self.selected_expense_row = None
        
        self.all_entries = []
        self.info_entries = {}
        self.measure_entries = {}
        
        self.create_database()
        self.migrate_database()
        self.create_modern_ui()
    
    # ============================================
    # دیتابیس
    # ============================================
    def create_database(self):
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
                height REAL, sleeve REAL, shoulder REAL, collar REAL,
                chest REAL, skirt REAL, pants_length REAL, leg REAL,
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
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'clothing_code' not in columns:
            cursor.execute('ALTER TABLE orders ADD COLUMN clothing_code INTEGER')
        conn.commit()
        conn.close()
    
    def check_duplicate_code(self, code, exclude_id=None):
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        if exclude_id:
            cursor.execute('SELECT id FROM orders WHERE clothing_code = ? AND id != ?', (code, exclude_id))
        else:
            cursor.execute('SELECT id FROM orders WHERE clothing_code = ?', (code,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    # ============================================
    # UI اصلی
    # ============================================
    def create_modern_ui(self):
        self.content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.create_header()
        self.create_navigation()
        self.page.add(ft.Column([self.header, self.nav_bar, self.content], expand=True, spacing=0))
        self.show_tab("new_order")
    
    def create_header(self):
        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("خیاطی دوستی  🧵", size=28, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                            ft.Text("سیستم مدیریت سفارشات", size=14, color=COLORS["text_muted"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                    ft.Container(
                        ft.Text(f"📅  {today_shamsi()}", size=14, color=COLORS["text"]),
                        bgcolor=COLORS["secondary"],
                        padding=10,
                        border_radius=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=COLORS["secondary"],
            padding=20,
            height=80,
        )
    
    def create_navigation(self):
        tabs = [
            ("new_order", "ثبت سفارش جدید  📝"),
            ("customers", "مشتریان  👥"),
            ("expenses", "مصارف دوکان  💰"),
            ("report", "گزارش مالی  📊")
        ]
        
        self.nav_buttons = {}
        buttons_row = []
        
        for tab_id, text in tabs:
            btn = ft.ElevatedButton(
                text,
                on_click=lambda e, t=tab_id: self.show_tab(t),
                bgcolor=COLORS["card_bg"],
                color=COLORS["text"],
                height=45,
                expand=True,
            )
            self.nav_buttons[tab_id] = btn
            buttons_row.append(btn)
        
        self.nav_bar = ft.Container(
            content=ft.Row(buttons_row, spacing=10),
            padding=10,
        )
    
    def show_tab(self, tab_id):
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.bgcolor = COLORS["accent"]
                btn.color = COLORS["primary"]
            else:
                btn.bgcolor = COLORS["card_bg"]
                btn.color = COLORS["text"]
        
        self.content.controls.clear()
        
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
        display = f"{text}  {icon}" if icon else text
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(display, size=20, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                    ft.Container(expand=True, height=2, bgcolor=COLORS["accent"]),
                ],
                spacing=15,
            ),
            padding=15,
        )
    
    # ============================================
    # تب ثبت سفارش جدید
    # ============================================
    def create_new_order_tab(self):
        title_text = "ثبت سفارش جدید  📝"
        if self.editing_order_id:
            title_text = f"ویرایش سفارش شماره {self.editing_order_id}  ✏️"
        
        title_container = ft.Container(
            content=ft.Row(
                [
                    ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                    ft.Container(expand=True, height=2, bgcolor=COLORS["accent"]),
                ],
                spacing=15,
            ),
            padding=15,
        )
        self.content.controls.append(title_container)
        
        # ساخت فیلدها
        fields_info = [
            ("اسم", "name"),
            ("تخلص", "surname"),
            ("شماره تلفون", "phone"),
            ("کود لباس (عدد)", "clothing_code"),
            ("مدل لباس", "clothing_type"),
            ("قیمت لباس (افغانی)", "price")
        ]
        
        self.info_entries = {}
        customer_fields = []
        for label, key in fields_info:
            lbl = ft.Text(label, size=15, weight=ft.FontWeight.BOLD, color=COLORS["text"])
            entry = ft.TextField(
                hint_text=label,  # ✅ اصلاح شد: hint_text به جای placeholder_text
                text_size=14,
                height=40,
                border_radius=10,
                bgcolor=COLORS["input_bg"],
                color=COLORS["text"],
                border_color=COLORS["secondary"],
                text_align=ft.TextAlign.RIGHT,
            )
            self.info_entries[key] = entry
            customer_fields.append(lbl)
            customer_fields.append(entry)
        
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
        measure_fields = []
        for label, key in measurements:
            lbl = ft.Text(label, size=15, weight=ft.FontWeight.BOLD, color=COLORS["text"])
            entry = ft.TextField(
                hint_text="0",  # ✅ اصلاح شد
                text_size=14,
                height=40,
                border_radius=10,
                bgcolor=COLORS["input_bg"],
                color=COLORS["text"],
                border_color=COLORS["secondary"],
                text_align=ft.TextAlign.RIGHT,
            )
            self.measure_entries[key] = entry
            measure_fields.append(lbl)
            measure_fields.append(entry)
        
        if self.editing_order_id:
            self._load_order_data()
        
        customer_card = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        ft.Text("اطلاعات مشتری  👤", size=20, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                        bgcolor=COLORS["secondary"],
                        padding=15,
                        border_radius=15,
                    ),
                    ft.Container(
                        ft.Column(customer_fields, spacing=10),
                        padding=20,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
            margin=5,
        )
        
        measure_card = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        ft.Text("اندازه‌ها (سانتی‌متر)  📏", size=20, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                        bgcolor=COLORS["secondary"],
                        padding=15,
                        border_radius=15,
                    ),
                    ft.Container(
                        ft.Column(measure_fields, spacing=10),
                        padding=20,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
            margin=5,
        )
        
        two_columns = ft.ResponsiveRow(
            [
                ft.Container(customer_card, col={"sm": 12, "md": 6, "lg": 6}),
                ft.Container(measure_card, col={"sm": 12, "md": 6, "lg": 6}),
            ],
            spacing=10,
            run_spacing=10,
        )
        
        btn_save_text = "ذخیره سفارش  💾"
        if self.editing_order_id:
            btn_save_text = "بروزرسانی سفارش  💾"
        
        self.btn_save = ft.ElevatedButton(
            btn_save_text,
            on_click=lambda e: self.save_order(),
            bgcolor=COLORS["accent"],
            color=COLORS["primary"],
            height=50,
            expand=True,
        )
        
        self.btn_cancel_edit = ft.ElevatedButton(
            "لغو ویرایش  ❌",
            on_click=lambda e: self.cancel_edit(),
            bgcolor=COLORS["danger"],
            color=COLORS["text"],
            height=50,
            expand=True,
            visible=self.editing_order_id is not None,
        )
        
        btn_frame = ft.Container(
            content=ft.Row([self.btn_cancel_edit, self.btn_save], spacing=10),
            padding=10,
        )
        
        self.content.controls.extend([two_columns, btn_frame])
    
    def _load_order_data(self):
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, customer_name, customer_surname, phone, clothing_code,
                   clothing_type, price, height, sleeve, shoulder, collar,
                   chest, skirt, pants_length, leg
            FROM orders WHERE id = ?
        ''', (self.editing_order_id,))
        order = cursor.fetchone()
        conn.close()
        
        if order:
            self.info_entries["name"].value = order[1] or ''
            self.info_entries["surname"].value = order[2] or ''
            self.info_entries["phone"].value = order[3] or ''
            self.info_entries["clothing_code"].value = str(order[4]) if order[4] else ''
            self.info_entries["clothing_type"].value = order[5] or ''
            self.info_entries["price"].value = str(order[6]) if order[6] else ''
            
            measure_keys = ['height', 'sleeve', 'shoulder', 'collar', 'chest', 'skirt', 'pants_length', 'leg']
            for i, key in enumerate(measure_keys):
                if order[7 + i] is not None:
                    self.measure_entries[key].value = str(order[7 + i])
    
    def save_order(self):
        clothing_code = (self.info_entries["clothing_code"].value or "").strip()
        name = (self.info_entries["name"].value or "").strip()
        surname = (self.info_entries["surname"].value or "").strip()
        phone = (self.info_entries["phone"].value or "").strip()
        clothing_type = (self.info_entries["clothing_type"].value or "").strip()
        price = (self.info_entries["price"].value or "").strip()
        
        if not clothing_code or not name or not surname or not phone or not price:
            self._show_error("لطفاً تمام فیلدهای ضروری را پر کنید!")
            return
        
        try:
            clothing_code_int = int(clothing_code)
            price_f = float(price)
        except ValueError:
            self._show_error("کود لباس و قیمت باید عدد باشند!")
            return
        
        if not clothing_type:
            clothing_type = "نامشخص"
        
        if self.check_duplicate_code(clothing_code_int, self.editing_order_id):
            self._show_error(f"کود لباس {clothing_code_int} قبلاً ثبت شده است!")
            return
        
        measurements = {}
        for key, entry in self.measure_entries.items():
            value = (entry.value or "").strip()
            measurements[key] = float(value) if value else None
        
        conn = sqlite3.connect('doosti.db')
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
                self._show_success("سفارش با موفقیت بروزرسانی شد!")
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
                      measurements['pants_length'], measurements['leg'], order_date))
                conn.commit()
                conn.close()
                self._show_success("سفارش با موفقیت ذخیره شد!")
                self.clear_order_form()
        except Exception as e:
            conn.close()
            self._show_error(f"خطا: {e}")
    
    def clear_order_form(self):
        for entry in self.info_entries.values():
            entry.value = ""
        for entry in self.measure_entries.values():
            entry.value = ""
    
    def cancel_edit(self):
        self.editing_order_id = None
        self.clear_order_form()
        self.show_tab("new_order")
    
    # ============================================
    # تب مشتریان
    # ============================================
    def create_customers_tab(self):
        self.content.controls.append(self.create_section_title("لیست مشتریان", "👥"))
        
        self.content.controls.append(
            ft.Container(
                ft.Text("💡 برای ویرایش یا حذف، روی هر سطر انگشت خود را نگه دارید", 
                       size=12, color=COLORS["text_muted"], text_align=ft.TextAlign.CENTER),
                padding=10,
            )
        )
        
        self.entry_search = ft.TextField(
            hint_text="جستجو با اسم، تخلص، موبایل یا کود لباس...  🔍",  # ✅ اصلاح شد
            text_size=14,
            height=40,
            border_radius=10,
            bgcolor=COLORS["input_bg"],
            color=COLORS["text"],
            border_color=COLORS["secondary"],
            text_align=ft.TextAlign.RIGHT,
            expand=True,
        )
        
        self.btn_search = ft.ElevatedButton(
            "جستجو",
            on_click=lambda e: self.search_customers(),
            bgcolor=COLORS["accent"],
            color=COLORS["primary"],
            height=40,
            width=120,
        )
        
        self.btn_refresh = ft.ElevatedButton(
            "بروزرسانی  🔄",
            on_click=lambda e: self.load_customers(),
            bgcolor=COLORS["secondary"],
            color=COLORS["text"],
            height=40,
            width=140,
        )
        
        search_card = ft.Container(
            content=ft.Row(
                [self.btn_refresh, self.btn_search, self.entry_search],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
            padding=20,
            margin=5,
        )
        self.content.controls.append(search_card)
        
        headers = ["وضعیت", "تاریخ", "قیمت", "مدل", "کود", "موبایل", "تخلص", "اسم", "#"]
        header_row = ft.Row(
            [ft.Text(h, color=COLORS["accent"], weight=ft.FontWeight.BOLD, size=12, expand=True) for h in headers],
            spacing=3,
        )
        
        table_header = ft.Container(
            content=header_row,
            bgcolor=COLORS["secondary"],
            padding=15,
            border_radius=15,
        )
        
        self.table_content = ft.Column(spacing=5)
        
        table_card = ft.Container(
            content=ft.Column([table_header, self.table_content], spacing=0),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
            padding=10,
            margin=5,
        )
        self.content.controls.append(table_card)
        
        self.load_customers()
    
    def load_customers(self):
        self.table_content.controls.clear()
        self.selected_order_row = None
        
        conn = sqlite3.connect('doosti.db')
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
        values = [
            order[8] or "در حال دوخت",
            order[7] or "-",
            f"{order[6]:,.0f}" if order[6] else "0",
            order[5] or "-",
            str(order[4]) if order[4] else "-",
            order[3] or "-",
            order[2] or "-",
            order[1] or "-",
            str(row_number),
        ]
        
        row = ft.Container(
            content=ft.Row(
                [ft.Text(v, color=COLORS["text"], size=12, expand=True) for v in values],
                spacing=3,
            ),
            bgcolor=COLORS["input_bg"],
            border_radius=10,
            padding=15,
            ink=True,
            on_long_press=lambda e, oid=order[0]: self._show_order_context_menu(oid),
            on_click=lambda e, oid=order[0]: self._highlight_order_row(oid, e.control),
        )
        self.table_content.controls.append(row)
    
    def _highlight_order_row(self, order_id, widget):
        if self.selected_order_row == order_id:
            return
        for ctrl in self.table_content.controls:
            ctrl.bgcolor = COLORS["input_bg"]
        widget.bgcolor = COLORS["selected_row"]
        self.selected_order_row = order_id
        self.page.update()
    
    def _show_order_context_menu(self, order_id):
        self.selected_order_row = order_id
        
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        def edit_click(e):
            close_dlg(e)
            self.edit_order(order_id)
        
        def delete_click(e):
            close_dlg(e)
            self.delete_order(order_id)
        
        dlg = ft.AlertDialog(
            title=ft.Text(f"عملیات سفارش شماره {order_id}", size=18, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
            content=ft.Column(
                [
                    ft.ElevatedButton("✏️  ویرایش سفارش", on_click=edit_click, bgcolor=COLORS["accent"], color=COLORS["primary"], height=50, expand=True),
                    ft.ElevatedButton("🗑️  حذف سفارش", on_click=delete_click, bgcolor=COLORS["danger"], color=COLORS["text"], height=50, expand=True),
                    ft.ElevatedButton("❌  انصراف", on_click=close_dlg, bgcolor=COLORS["secondary"], color=COLORS["text"], height=50, expand=True),
                ],
                spacing=10,
                tight=True,
            ),
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    def edit_order(self, order_id):
        self.editing_order_id = order_id
        self.show_tab("new_order")
    
    def delete_order(self, order_id):
        self._show_confirm("تأیید حذف", "آیا از حذف این سفارش اطمینان دارید؟", lambda: self._do_delete_order(order_id))
    
    def _do_delete_order(self, order_id):
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
        conn.close()
        self._show_success("سفارش حذف شد!")
        self.load_customers()
    
    def search_customers(self):
        search_text = (self.entry_search.value or "").strip()
        self.table_content.controls.clear()
        self.selected_order_row = None
        
        if not search_text:
            self.load_customers()
            return
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, customer_name, customer_surname, phone, clothing_code,
                   clothing_type, price, order_date, status
            FROM orders
            WHERE customer_name LIKE ? OR customer_surname LIKE ? OR phone LIKE ?
               OR CAST(clothing_code AS TEXT) LIKE ? OR clothing_type LIKE ?
            ORDER BY id ASC
        ''', (f'%{search_text}%',) * 5)
        orders = cursor.fetchall()
        conn.close()
        
        for idx, order in enumerate(orders):
            self.add_customer_row(order, idx + 1)
        self.page.update()
    
    # ============================================
    # تب مصارف
    # ============================================
    def create_expenses_tab(self):
        self.content.controls.append(self.create_section_title("مصارف دوکان", "💰"))
        
        self.content.controls.append(
            ft.Container(
                ft.Text("💡 برای ویرایش یا حذف، روی هر سطر انگشت خود را نگه دارید", 
                       size=12, color=COLORS["text_muted"], text_align=ft.TextAlign.CENTER),
                padding=10,
            )
        )
        
        title_text = "ثبت مصرف جدید  💰"
        btn_text = "ذخیره  💾"
        if self.editing_expense_id:
            title_text = "ویرایش مصرف  ✏️"
            btn_text = "بروزرسانی  💾"
        
        self.expense_title_label = ft.Text(title_text, size=16, weight=ft.FontWeight.BOLD, color=COLORS["text"])
        
        self.entry_expense_title = ft.TextField(
            hint_text="عنوان مصرف (مثلاً: کرایه دوکان)",  # ✅ اصلاح شد
            text_size=14,
            height=40,
            border_radius=10,
            bgcolor=COLORS["input_bg"],
            color=COLORS["text"],
            border_color=COLORS["secondary"],
            text_align=ft.TextAlign.RIGHT,
            expand=True,
        )
        
        self.entry_expense_amount = ft.TextField(
            hint_text="مبلغ (افغانی)",  # ✅ اصلاح شد
            text_size=14,
            height=40,
            border_radius=10,
            bgcolor=COLORS["input_bg"],
            color=COLORS["text"],
            border_color=COLORS["secondary"],
            text_align=ft.TextAlign.RIGHT,
            width=200,
        )
        
        self.btn_save_expense = ft.ElevatedButton(
            btn_text,
            on_click=lambda e: self.save_expense(),
            bgcolor=COLORS["accent"],
            color=COLORS["primary"],
            height=40,
            width=120,
        )
        
        self.btn_cancel_expense_edit = ft.ElevatedButton(
            "لغو  ❌",
            on_click=lambda e: self.cancel_expense_edit(),
            bgcolor=COLORS["danger"],
            color=COLORS["text"],
            height=40,
            width=100,
            visible=self.editing_expense_id is not None,
        )
        
        if self.editing_expense_id:
            self._load_expense_data()
        
        form_content = ft.Container(
            content=ft.Column(
                [
                    ft.Container(self.expense_title_label, bgcolor=COLORS["secondary"], padding=12, border_radius=15),
                    ft.Container(
                        content=ft.Row([self.btn_cancel_expense_edit, self.btn_save_expense, self.entry_expense_amount, self.entry_expense_title], spacing=10, vertical_alignment=ft.CrossAxisAlignment.END),
                        padding=20,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
            margin=5,
        )
        self.content.controls.append(form_content)
        
        headers = ["تاریخ", "مبلغ", "عنوان", "شماره"]
        header_row = ft.Row(
            [ft.Text(h, color=COLORS["accent"], weight=ft.FontWeight.BOLD, size=13, expand=True) for h in headers],
            spacing=5,
        )
        
        table_header = ft.Container(content=header_row, bgcolor=COLORS["secondary"], padding=15, border_radius=15)
        self.expenses_table_content = ft.Column(spacing=5)
        
        table_card = ft.Container(
            content=ft.Column([table_header, self.expenses_table_content], spacing=0),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
            padding=10,
            margin=5,
        )
        self.content.controls.append(table_card)
        
        self.load_expenses()
    
    def _load_expense_data(self):
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses WHERE id = ?', (self.editing_expense_id,))
        expense = cursor.fetchone()
        conn.close()
        if expense:
            self.entry_expense_title.value = expense[1] or ''
            self.entry_expense_amount.value = str(expense[2]) if expense[2] else ''
    
    def save_expense(self):
        title = (self.entry_expense_title.value or "").strip()
        amount = (self.entry_expense_amount.value or "").strip()
        
        if not title or not amount:
            self._show_error("لطفاً عنوان و مبلغ را وارد کنید!")
            return
        
        try:
            amount_f = float(amount)
        except ValueError:
            self._show_error("مبلغ باید یک عدد باشد!")
            return
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        expense_date = now_shamsi()
        
        try:
            if self.editing_expense_id:
                cursor.execute('UPDATE expenses SET title = ?, amount = ? WHERE id = ?', (title, amount_f, self.editing_expense_id))
                conn.commit()
                conn.close()
                self._show_success("مصرف با موفقیت بروزرسانی شد!")
                self.cancel_expense_edit()
            else:
                cursor.execute('INSERT INTO expenses (title, amount, date) VALUES (?, ?, ?)', (title, amount_f, expense_date))
                conn.commit()
                conn.close()
                self._show_success("مصرف با موفقیت ذخیره شد!")
            
            self.entry_expense_title.value = ""
            self.entry_expense_amount.value = ""
            self.load_expenses()
        except Exception as e:
            conn.close()
            self._show_error(f"خطا: {e}")
    
    def cancel_expense_edit(self):
        self.editing_expense_id = None
        self.entry_expense_title.value = ""
        self.entry_expense_amount.value = ""
        self.show_tab("expenses")
    
    def load_expenses(self):
        self.expenses_table_content.controls.clear()
        self.selected_expense_row = None
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, amount, date FROM expenses ORDER BY id ASC')
        expenses = cursor.fetchall()
        conn.close()
        
        for idx, expense in enumerate(expenses):
            self.add_expense_row(expense, idx + 1)
        self.page.update()
    
    def add_expense_row(self, expense, row_number):
        values = [
            expense[3] or "-",
            f"{expense[2]:,.0f}" if expense[2] else "0",
            expense[1] or "-",
            str(row_number),
        ]
        
        row = ft.Container(
            content=ft.Row([ft.Text(v, color=COLORS["text"], size=13, expand=True) for v in values], spacing=5),
            bgcolor=COLORS["input_bg"],
            border_radius=10,
            padding=15,
            ink=True,
            on_long_press=lambda e, eid=expense[0]: self._show_expense_context_menu(eid),
            on_click=lambda e, eid=expense[0]: self._highlight_expense_row(eid, e.control),
        )
        self.expenses_table_content.controls.append(row)
    
    def _highlight_expense_row(self, expense_id, widget):
        for ctrl in self.expenses_table_content.controls:
            ctrl.bgcolor = COLORS["input_bg"]
        widget.bgcolor = COLORS["selected_row"]
        self.selected_expense_row = expense_id
        self.page.update()
    
    def _show_expense_context_menu(self, expense_id):
        self.selected_expense_row = expense_id
        
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        def edit_click(e):
            close_dlg(e)
            self.edit_expense(expense_id)
        
        def delete_click(e):
            close_dlg(e)
            self.delete_expense(expense_id)
        
        dlg = ft.AlertDialog(
            title=ft.Text(f"عملیات مصرف شماره {expense_id}", size=18, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
            content=ft.Column(
                [
                    ft.ElevatedButton("✏️  ویرایش مصرف", on_click=edit_click, bgcolor=COLORS["accent"], color=COLORS["primary"], height=50, expand=True),
                    ft.ElevatedButton("🗑️  حذف مصرف", on_click=delete_click, bgcolor=COLORS["danger"], color=COLORS["text"], height=50, expand=True),
                    ft.ElevatedButton("❌  انصراف", on_click=close_dlg, bgcolor=COLORS["secondary"], color=COLORS["text"], height=50, expand=True),
                ],
                spacing=10,
                tight=True,
            ),
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    def edit_expense(self, expense_id):
        self.editing_expense_id = expense_id
        self.show_tab("expenses")
    
    def delete_expense(self, expense_id):
        self._show_confirm("تأیید حذف", "آیا از حذف این مصرف اطمینان دارید؟", lambda: self._do_delete_expense(expense_id))
    
    def _do_delete_expense(self, expense_id):
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()
        self._show_success("مصرف حذف شد!")
        self.load_expenses()
    
    # ============================================
    # تب گزارش مالی
    # ============================================
    def create_report_tab(self):
        self.content.controls.append(self.create_section_title("گزارش مالی", "📊"))
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COALESCE(SUM(price), 0) FROM orders')
        total_income = cursor.fetchone()[0]
        cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM expenses')
        total_expenses = cursor.fetchone()[0]
        conn.close()
        net_profit = total_income - total_expenses
        
        self.income_card = self.create_stat_card("مجموع درآمد  💵", f"{total_income:,.0f} افغانی", COLORS["success"])
        self.expenses_card = self.create_stat_card("مجموع مصارف  💸", f"{total_expenses:,.0f} افغانی", COLORS["danger"])
        self.profit_card = self.create_stat_card("سود خالص  📈", f"{net_profit:,.0f} افغانی", COLORS["accent"])
        
        stats_row = ft.ResponsiveRow(
            [
                ft.Container(self.income_card, col={"sm": 12, "md": 4, "lg": 4}),
                ft.Container(self.expenses_card, col={"sm": 12, "md": 4, "lg": 4}),
                ft.Container(self.profit_card, col={"sm": 12, "md": 4, "lg": 4}),
            ],
            spacing=10,
            run_spacing=10,
        )
        
        self.content.controls.append(ft.Container(stats_row, padding=10))
        
        self.btn_calculate = ft.ElevatedButton(
            "محاسبه گزارش  🔄",
            on_click=lambda e: self.calculate_report(),
            bgcolor=COLORS["accent"],
            color=COLORS["primary"],
            height=50,
        )
        self.content.controls.append(ft.Container(self.btn_calculate, padding=10))
    
    def create_stat_card(self, title, value, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=5, bgcolor=color, border_radius=15),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(title, size=14, color=COLORS["text_muted"], text_align=ft.TextAlign.RIGHT),
                                ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color, text_align=ft.TextAlign.RIGHT),
                            ],
                            spacing=10,
                        ),
                        padding=20,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
        )
    
    def calculate_report(self):
        try:
            conn = sqlite3.connect('doosti.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COALESCE(SUM(price), 0) FROM orders')
            total_income = cursor.fetchone()[0]
            cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM expenses')
            total_expenses = cursor.fetchone()[0]
            conn.close()
            net_profit = total_income - total_expenses
            
            self.income_card = self.create_stat_card("مجموع درآمد  💵", f"{total_income:,.0f} افغانی", COLORS["success"])
            self.expenses_card = self.create_stat_card("مجموع مصارف  💸", f"{total_expenses:,.0f} افغانی", COLORS["danger"])
            self.profit_card = self.create_stat_card("سود خالص  📈", f"{net_profit:,.0f} افغانی", COLORS["accent"])
            
            self.show_tab("report")
        except Exception as e:
            print(f"خطا در محاسبه گزارش: {e}")
    
    # ============================================
    # پیام‌ها
    # ============================================
    def _show_error(self, message):
        self.page.overlay.append(ft.SnackBar(content=ft.Text(message, color=COLORS["text"]), bgcolor=COLORS["danger"], action="OK"))
        self.page.update()
    
    def _show_success(self, message):
        self.page.overlay.append(ft.SnackBar(content=ft.Text(message, color=COLORS["text"]), bgcolor=COLORS["success"], action="OK"))
        self.page.update()
    
    def _show_confirm(self, title, message, on_yes):
        def close_dialog(e):
            dlg.open = False
            self.page.update()
        
        def yes_click(e):
            close_dialog(e)
            on_yes()
        
        dlg = ft.AlertDialog(
            title=ft.Text(title, color=COLORS["accent"], weight=ft.FontWeight.BOLD),
            content=ft.Text(message, color=COLORS["text"]),
            actions=[
                ft.TextButton("انصراف", on_click=close_dialog),
                ft.TextButton("بله، حذف کن", on_click=yes_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

# ============================================
# اجرای برنامه
# ============================================
def main(page: ft.Page):
    DoostiTailoringApp(page)

ft.run(main)  # ✅ اصلاح شد: ft.run به جای ft.app
