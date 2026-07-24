import flet as ft
import sqlite3
import jdatetime

COLORS = {
    "primary": "#1a2332",
    "secondary": "#2c3e50",
    "accent": "#d4af37",
    "success": "#27ae60",
    "danger": "#e74c3c",
    "text": "#ecf0f1",
    "text_muted": "#95a5a6",
    "card_bg": "#34495e",
    "input_bg": "#2c3e50",
}

DB_FILE = 'doosti.db'

def get_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT, customer_surname TEXT,
        phone TEXT, clothing_code INTEGER UNIQUE,
        clothing_type TEXT, price REAL,
        height REAL, sleeve REAL, shoulder REAL, collar REAL,
        chest REAL, skirt REAL, pants_length REAL, leg REAL,
        order_date TEXT, status TEXT DEFAULT 'در حال دوخت'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, amount REAL, date TEXT
    )''')
    conn.commit()
    conn.close()

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

def make_field(label_text):
    return ft.TextField(
        label=label_text,
        bgcolor=COLORS["input_bg"],
        color=COLORS["text"],
        text_align=ft.TextAlign.RIGHT,
        label_style=ft.TextStyle(color=COLORS["text"], weight=ft.FontWeight.BOLD),
    )

class DoostiApp:
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

        self.editing_order_id = None

        init_db()
        self.build_ui()
        self.show_tab("new_order")

    def build_ui(self):
        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("🧵 خیاطی دوستی", size=26, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                            ft.Text("سیستم مدیریت سفارشات", size=13, color=COLORS["text_muted"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                    ft.Container(
                        ft.Text(f"📅 {today_shamsi()}", size=13, weight=ft.FontWeight.BOLD, color=COLORS["primary"]),
                        bgcolor=COLORS["accent"],
                        padding=10,
                        border_radius=20,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLORS["secondary"],
            padding=15,
        )

        self.nav_bar = ft.Container(
            content=ft.Row(
                [
                    ft.ElevatedButton("📝 سفارش جدید", on_click=lambda e: self.show_tab("new_order"),
                                     bgcolor=COLORS["card_bg"], color=COLORS["text"], expand=True, height=45),
                    ft.ElevatedButton("👥 مشتریان", on_click=lambda e: self.show_tab("customers"),
                                     bgcolor=COLORS["card_bg"], color=COLORS["text"], expand=True, height=45),
                    ft.ElevatedButton("💰 مصارف", on_click=lambda e: self.show_tab("expenses"),
                                     bgcolor=COLORS["card_bg"], color=COLORS["text"], expand=True, height=45),
                    ft.ElevatedButton("📊 گزارش", on_click=lambda e: self.show_tab("report"),
                                     bgcolor=COLORS["card_bg"], color=COLORS["text"], expand=True, height=45),
                ],
                spacing=8,
            ),
            padding=10,
        )

        self.content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.add(ft.Column([self.header, self.nav_bar, self.content], expand=True, spacing=0))

    def show_tab(self, tab_name):
        self.content.controls.clear()
        if tab_name == "new_order":
            self._build_new_order()
        elif tab_name == "customers":
            self._build_customers()
        elif tab_name == "expenses":
            self._build_expenses()
        elif tab_name == "report":
            self._build_report()
        self.page.update()

    def _section_title(self, text):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(text, size=20, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                    ft.Container(expand=True, height=2, bgcolor=COLORS["accent"]),
                ],
                spacing=15,
            ),
            padding=15,
        )

    # ============================================
    # ✅ تب سفارش جدید - دو ستون عمودی (تغییر اصلی)
    # ============================================
    def _build_new_order(self):
        title = f"ویرایش سفارش شماره {self.editing_order_id} ✏️" if self.editing_order_id else "ثبت سفارش جدید 📝"
        self.content.controls.append(self._section_title(title))

        # ساخت فیلدها
        self.f_name = make_field("اسم")
        self.f_surname = make_field("تخلص")
        self.f_phone = make_field("شماره تلفون")
        self.f_code = make_field("کود لباس (عدد)")
        self.f_type = make_field("مدل لباس")
        self.f_price = make_field("قیمت لباس (افغانی)")

        self.f_height = make_field("قد")
        self.f_sleeve = make_field("آستین")
        self.f_shoulder = make_field("شانه")
        self.f_collar = make_field("یخن")
        self.f_chest = make_field("بغل")
        self.f_skirt = make_field("بردامن")
        self.f_pants = make_field("قد تنبان")
        self.f_leg = make_field("پاچه")

        # بارگذاری مقادیر در حالت ویرایش
        if self.editing_order_id:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT * FROM orders WHERE id=?', (self.editing_order_id,))
            o = cur.fetchone()
            conn.close()
            if o:
                self.f_name.value = o[1] or ''
                self.f_surname.value = o[2] or ''
                self.f_phone.value = o[3] or ''
                self.f_code.value = str(o[4]) if o[4] else ''
                self.f_type.value = o[5] or ''
                self.f_price.value = str(o[6]) if o[6] else ''
                self.f_height.value = str(o[7]) if o[7] else ''
                self.f_sleeve.value = str(o[8]) if o[8] else ''
                self.f_shoulder.value = str(o[9]) if o[9] else ''
                self.f_collar.value = str(o[10]) if o[10] else ''
                self.f_chest.value = str(o[11]) if o[11] else ''
                self.f_skirt.value = str(o[12]) if o[12] else ''
                self.f_pants.value = str(o[13]) if o[13] else ''
                self.f_leg.value = str(o[14]) if o[14] else ''

        # ✅ کارت اطلاعات مشتری (ستون سمت راست)
        customer_card = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        ft.Text("اطلاعات مشتری 👤", size=18, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                        bgcolor=COLORS["secondary"],
                        padding=15,
                        border_radius=15,
                    ),
                    ft.Container(
                        ft.Column(
                            [self.f_name, self.f_surname, self.f_phone, self.f_code, self.f_type, self.f_price],
                            spacing=12,
                        ),
                        padding=20,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
            margin=5,
        )

        # ✅ کارت اندازه‌ها (ستون سمت چپ)
        measure_card = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        ft.Text("اندازه‌ها (سانتی‌متر) 📏", size=18, weight=ft.FontWeight.BOLD, color=COLORS["accent"]),
                        bgcolor=COLORS["secondary"],
                        padding=15,
                        border_radius=15,
                    ),
                    ft.Container(
                        ft.Column(
                            [self.f_height, self.f_sleeve, self.f_shoulder, self.f_collar,
                             self.f_chest, self.f_skirt, self.f_pants, self.f_leg],
                            spacing=12,
                        ),
                        padding=20,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
            margin=5,
        )

        # ✅ دو ستون عمودی با ResponsiveRow
        # در دسکتاپ: دو ستون کنار هم
        # در موبایل: دو ستون زیر هم (خودکار)
        two_columns = ft.ResponsiveRow(
            [
                ft.Container(customer_card, col={"sm": 12, "md": 6, "lg": 6}),
                ft.Container(measure_card, col={"sm": 12, "md": 6, "lg": 6}),
            ],
            spacing=10,
            run_spacing=10,
        )

        # دکمه‌ها
        btn_text = "بروزرسانی سفارش 💾" if self.editing_order_id else "ذخیره سفارش 💾"
        buttons = ft.Row(
            [
                ft.ElevatedButton(
                    "لغو ویرایش ❌",
                    on_click=lambda e: self._cancel_edit(),
                    bgcolor=COLORS["danger"],
                    color=COLORS["text"],
                    expand=True,
                    height=50,
                    visible=self.editing_order_id is not None,
                ),
                ft.ElevatedButton(
                    btn_text,
                    on_click=lambda e: self._save_order(),
                    bgcolor=COLORS["accent"],
                    color=COLORS["primary"],
                    expand=True,
                    height=50,
                ),
            ],
            spacing=10,
        )

        self.content.controls.extend([two_columns, ft.Container(buttons, padding=10)])

    def _save_order(self):
        code = self.f_code.value
        name = self.f_name.value
        surname = self.f_surname.value
        phone = self.f_phone.value
        ctype = self.f_type.value or "نامشخص"
        price = self.f_price.value

        if not all([code, name, surname, phone, price]):
            self._snack("❌ لطفاً تمام فیلدهای ضروری را پر کنید!")
            return

        try:
            code_int = int(code)
            price_f = float(price)
        except:
            self._snack("❌ کود لباس و قیمت باید عدد باشند!")
            return

        conn = get_db()
        cur = conn.cursor()

        if self.editing_order_id:
            cur.execute('SELECT id FROM orders WHERE clothing_code=? AND id!=?', (code_int, self.editing_order_id))
        else:
            cur.execute('SELECT id FROM orders WHERE clothing_code=?', (code_int,))

        if cur.fetchone():
            conn.close()
            self._snack(f"❌ کود لباس {code_int} قبلاً ثبت شده است!")
            return

        ms = {
            'height': safe_float(self.f_height.value),
            'sleeve': safe_float(self.f_sleeve.value),
            'shoulder': safe_float(self.f_shoulder.value),
            'collar': safe_float(self.f_collar.value),
            'chest': safe_float(self.f_chest.value),
            'skirt': safe_float(self.f_skirt.value),
            'pants': safe_float(self.f_pants.value),
            'leg': safe_float(self.f_leg.value),
        }

        try:
            if self.editing_order_id:
                cur.execute('''UPDATE orders SET clothing_code=?, customer_name=?, customer_surname=?,
                    phone=?, clothing_type=?, price=?, height=?, sleeve=?, shoulder=?, collar=?,
                    chest=?, skirt=?, pants_length=?, leg=? WHERE id=?''',
                    (code_int, name, surname, phone, ctype, price_f,
                     ms['height'], ms['sleeve'], ms['shoulder'], ms['collar'],
                     ms['chest'], ms['skirt'], ms['pants'], ms['leg'], self.editing_order_id))
            else:
                cur.execute('''INSERT INTO orders (clothing_code, customer_name, customer_surname,
                    phone, clothing_type, price, height, sleeve, shoulder, collar, chest, skirt,
                    pants_length, leg, order_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (code_int, name, surname, phone, ctype, price_f,
                     ms['height'], ms['sleeve'], ms['shoulder'], ms['collar'],
                     ms['chest'], ms['skirt'], ms['pants'], ms['leg'], now_shamsi()))

            conn.commit()
            conn.close()
            self.editing_order_id = None
            self._snack("✅ سفارش با موفقیت ذخیره شد!")
            self.show_tab("new_order")
        except Exception as ex:
            conn.close()
            self._snack(f"❌ خطا: {ex}")

    def _cancel_edit(self):
        self.editing_order_id = None
        self.show_tab("new_order")

    # ============================================
    # تب مشتریان (بدون تغییر اساسی)
    # ============================================
    def _build_customers(self):
        self.content.controls.append(self._section_title("لیست مشتریان 👥"))

        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id, customer_name, customer_surname, phone, clothing_code, clothing_type, price, order_date FROM orders ORDER BY id DESC')
        orders = cur.fetchall()
        conn.close()

        if not orders:
            self.content.controls.append(
                ft.Container(ft.Text("📭 هیچ سفارشی ثبت نشده است", color=COLORS["text_muted"], size=16), padding=30)
            )
        else:
            header = ft.Container(
                content=ft.Row(
                    [
                        ft.Text("شماره", color=COLORS["accent"], weight=ft.FontWeight.BOLD, expand=True, size=12),
                        ft.Text("اسم", color=COLORS["accent"], weight=ft.FontWeight.BOLD, expand=True, size=12),
                        ft.Text("تخلص", color=COLORS["accent"], weight=ft.FontWeight.BOLD, expand=True, size=12),
                        ft.Text("موبایل", color=COLORS["accent"], weight=ft.FontWeight.BOLD, expand=True, size=12),
                        ft.Text("کود", color=COLORS["accent"], weight=ft.FontWeight.BOLD, expand=True, size=12),
                        ft.Text("قیمت", color=COLORS["accent"], weight=ft.FontWeight.BOLD, expand=True, size=12),
                    ],
                    spacing=5,
                ),
                bgcolor=COLORS["secondary"],
                padding=12,
                border_radius=10,
            )
            self.content.controls.append(header)

            for idx, o in enumerate(orders):
                row = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(f"#{idx+1}", color=COLORS["accent"], weight=ft.FontWeight.BOLD, size=13),
                                    ft.Text(f"{o[1]} {o[2]}", color=COLORS["text"], size=13),
                                    ft.Text(f"کود: {o[4]}", color=COLORS["text_muted"], size=12),
                                ],
                                spacing=10,
                            ),
                            ft.Row(
                                [
                                    ft.Text(f"📱 {o[3]}", color=COLORS["text_muted"], size=12),
                                    ft.Text(f"💰 {fmt(o[6])} افغانی", color=COLORS["success"], weight=ft.FontWeight.BOLD, size=14),
                                ],
                                spacing=10,
                            ),
                            ft.Row(
                                [
                                    ft.ElevatedButton("✏️ ویرایش", on_click=lambda e, oid=o[0]: self._edit_order(oid),
                                                    bgcolor=COLORS["accent"], color=COLORS["primary"], height=35),
                                    ft.ElevatedButton("🗑️ حذف", on_click=lambda e, oid=o[0]: self._delete_order(oid),
                                                    bgcolor=COLORS["danger"], color=COLORS["text"], height=35),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=8,
                    ),
                    bgcolor=COLORS["input_bg"],
                    padding=15,
                    margin=5,
                    border_radius=10,
                )
                self.content.controls.append(row)

    def _edit_order(self, order_id):
        self.editing_order_id = order_id
        self.show_tab("new_order")

    def _delete_order(self, order_id):
        conn = get_db()
        conn.execute('DELETE FROM orders WHERE id=?', (order_id,))
        conn.commit()
        conn.close()
        self._snack("✅ سفارش حذف شد!")
        self.show_tab("customers")

    # ============================================
    # تب مصارف (بدون تغییر اساسی)
    # ============================================
    def _build_expenses(self):
        self.content.controls.append(self._section_title("مصارف دوکان 💰"))

        self.f_exp_title = make_field("عنوان مصرف")
        self.f_exp_amount = make_field("مبلغ (افغانی)")

        form_card = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        ft.Text("ثبت مصرف جدید 💰", size=16, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                        bgcolor=COLORS["secondary"],
                        padding=15,
                        border_radius=15,
                    ),
                    ft.Container(
                        ft.Column(
                            [
                                self.f_exp_title,
                                self.f_exp_amount,
                                ft.ElevatedButton("💾 ذخیره", on_click=lambda e: self._save_expense(),
                                                bgcolor=COLORS["accent"], color=COLORS["primary"], expand=True, height=50),
                            ],
                            spacing=12,
                        ),
                        padding=20,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=COLORS["card_bg"],
            border_radius=15,
            margin=10,
        )
        self.content.controls.append(form_card)

        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id, title, amount, date FROM expenses ORDER BY id DESC')
        expenses = cur.fetchall()
        conn.close()

        if expenses:
            for exp in expenses:
                self.content.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(exp[1], weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                                        ft.Text(exp[3] or '', size=11, color=COLORS["text_muted"]),
                                    ],
                                    expand=True,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                                ft.Text(f"{fmt(exp[2])} افغانی", weight=ft.FontWeight.BOLD, color=COLORS["danger"], size=16),
                                ft.ElevatedButton("🗑️", on_click=lambda e, eid=exp[0]: self._delete_expense(eid),
                                                bgcolor=COLORS["danger"], color=COLORS["text"], height=35, width=45),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor=COLORS["card_bg"],
                        border_radius=10,
                        padding=15,
                        margin=5,
                    )
                )

    def _save_expense(self):
        title = self.f_exp_title.value
        amount = self.f_exp_amount.value

        if not title or not amount:
            self._snack("❌ لطفاً عنوان و مبلغ را وارد کنید!")
            return

        try:
            amt = float(amount)
            conn = get_db()
            conn.execute('INSERT INTO expenses (title, amount, date) VALUES (?,?,?)', (title, amt, now_shamsi()))
            conn.commit()
            conn.close()
            self._snack("✅ مصرف با موفقیت ذخیره شد!")
            self.show_tab("expenses")
        except:
            self._snack("❌ مبلغ باید یک عدد باشد!")

    def _delete_expense(self, expense_id):
        conn = get_db()
        conn.execute('DELETE FROM expenses WHERE id=?', (expense_id,))
        conn.commit()
        conn.close()
        self._snack("✅ مصرف حذف شد!")
        self.show_tab("expenses")

    # ============================================
    # تب گزارش (بدون تغییر اساسی)
    # ============================================
    def _build_report(self):
        self.content.controls.append(self._section_title("گزارش مالی 📊"))

        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT COALESCE(SUM(price),0) FROM orders')
        income = cur.fetchone()[0]
        cur.execute('SELECT COALESCE(SUM(amount),0) FROM expenses')
        expenses = cur.fetchone()[0]
        conn.close()

        profit = income - expenses
        profit_color = COLORS["success"] if profit >= 0 else COLORS["danger"]

        cards = ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=5, bgcolor=COLORS["success"], border_radius=2),
                            ft.Text("💵 مجموع درآمد", size=14, color=COLORS["text_muted"], text_align=ft.TextAlign.CENTER),
                            ft.Text(f"{fmt(income)} افغانی", size=22, weight=ft.FontWeight.BOLD, color=COLORS["success"], text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    bgcolor=COLORS["card_bg"],
                    border_radius=15,
                    padding=20,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=5, bgcolor=COLORS["danger"], border_radius=2),
                            ft.Text("💸 مجموع مصارف", size=14, color=COLORS["text_muted"], text_align=ft.TextAlign.CENTER),
                            ft.Text(f"{fmt(expenses)} افغانی", size=22, weight=ft.FontWeight.BOLD, color=COLORS["danger"], text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    bgcolor=COLORS["card_bg"],
                    border_radius=15,
                    padding=20,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=5, bgcolor=COLORS["accent"], border_radius=2),
                            ft.Text("📈 سود خالص", size=14, color=COLORS["text_muted"], text_align=ft.TextAlign.CENTER),
                            ft.Text(f"{fmt(profit)} افغانی", size=22, weight=ft.FontWeight.BOLD, color=profit_color, text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    bgcolor=COLORS["card_bg"],
                    border_radius=15,
                    padding=20,
                    expand=True,
                ),
            ],
            spacing=10,
        )
        self.content.controls.append(cards)

    def _snack(self, message):
        self.page.overlay.append(
            ft.SnackBar(
                content=ft.Text(message, color=COLORS["text"]),
                bgcolor=COLORS["secondary"],
                action="OK",
            )
        )
        self.page.update()

def main(page: ft.Page):
    DoostiApp(page)

ft.app(target=main)
