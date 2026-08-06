import flet as ft
import sqlite3
import jdatetime
import os

class DoostiApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "خیاطی دوستی"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.GOLD,
                secondary=ft.Colors.BLUE_GREY,
            ),
            font_family="Vazirmatn",
        )
        self.page.direction = ft.TextDirection.RTL
        self.page.padding = 20
        self.page.bgcolor = "#1a2332"
        
        self.editing_order_id = None
        self.editing_expense_id = None
        
        self.create_database()
        self.build_ui()
    
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
                clothing_type TEXT,
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
    
    def build_ui(self):
        today = jdatetime.datetime.now().strftime("%Y/%m/%d")
        
        # فیلدهای فرم سفارش
        self.entry_name = ft.TextField(label="اسم", text_align=ft.TextAlign.RIGHT, rtl=True)
        self.entry_surname = ft.TextField(label="تخلص", text_align=ft.TextAlign.RIGHT, rtl=True)
        self.entry_phone = ft.TextField(label="شماره تلفون", text_align=ft.TextAlign.RIGHT, rtl=True, keyboard_type=ft.KeyboardType.PHONE)
        self.entry_clothing_code = ft.TextField(label="کود لباس (عدد)", text_align=ft.TextAlign.RIGHT, rtl=True, keyboard_type=ft.KeyboardType.NUMBER)
        self.entry_clothing_type = ft.TextField(label="مدل لباس", text_align=ft.TextAlign.RIGHT, rtl=True)
        self.entry_price = ft.TextField(label="قیمت (افغانی)", text_align=ft.TextAlign.RIGHT, rtl=True, keyboard_type=ft.KeyboardType.NUMBER)
        
        # فیلدهای اندازه‌ها
        self.measure_entries = {}
        measurements = [("قد","height"),("آستین","sleeve"),("شانه","shoulder"),
                       ("یخن","collar"),("بغل","chest"),("بردامن","skirt"),
                       ("قد تنبان","pants_length"),("پاچه","leg")]
        
        for label, key in measurements:
            self.measure_entries[key] = ft.TextField(
                label=label, text_align=ft.TextAlign.RIGHT, rtl=True,
                keyboard_type=ft.KeyboardType.NUMBER
            )
        
        # فیلدهای جستجو
        self.entry_search = ft.TextField(
            label="جستجو (اسم، تخلص، موبایل، کود لباس)",
            text_align=ft.TextAlign.RIGHT, rtl=True, expand=True
        )
        
        # فیلدهای مصارف
        self.entry_expense_title = ft.TextField(label="عنوان مصرف", text_align=ft.TextAlign.RIGHT, rtl=True, expand=True)
        self.entry_expense_amount = ft.TextField(label="مبلغ (افغانی)", text_align=ft.TextAlign.RIGHT, rtl=True, keyboard_type=ft.KeyboardType.NUMBER, expand=True)
        
        # کارت‌های گزارش
        self.income_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
        self.expenses_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.RED)
        self.profit_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GOLD)
        
        # ساخت تب‌ها
        self.tab_new_order = self.create_new_order_tab()
        self.tab_customers = self.create_customers_tab()
        self.tab_expenses = self.create_expenses_tab()
        self.tab_report = self.create_report_tab()
        
        # هدر
        header = ft.Container(
            content=ft.Row([
                ft.Text("🧵 خیاطی دوستی", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GOLD),
                ft.Container(expand=True),
                ft.Text(f"📅 {today}", size=14, color=ft.Colors.WHITE),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#2c3e50", padding=15, border_radius=10
        )
        
        # تب‌بار
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="📝 ثبت سفارش", content=self.tab_new_order),
                ft.Tab(text="👥 مشتریان", content=self.tab_customers),
                ft.Tab(text="💰 مصارف", content=self.tab_expenses),
                ft.Tab(text="📊 گزارش", content=self.tab_report),
            ],
            expand=True
        )
        
        self.page.add(
            header,
            ft.Container(content=tabs, expand=True, padding=10)
        )
    
    def create_new_order_tab(self):
        measure_fields = [self.measure_entries[k] for k in self.measure_entries]
        
        return ft.View(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("اطلاعات مشتری 👤", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GOLD),
                self.entry_name, self.entry_surname, self.entry_phone,
                self.entry_clothing_code, self.entry_clothing_type, self.entry_price,
                ft.Divider(),
                ft.Text("اندازه‌ها (سانتی‌متر) 📏", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GOLD),
                *measure_fields,
                ft.Row([
                    ft.ElevatedButton("❌ لغو", color=ft.Colors.WHITE, bgcolor=ft.Colors.RED, on_click=self.cancel_edit, expand=True),
                    ft.ElevatedButton("💾 ذخیره سفارش", color="#1a2332", bgcolor=ft.Colors.GOLD, on_click=self.save_order, expand=True),
                ], spacing=10),
            ]
        )
    
    def create_customers_tab(self):
        self.customers_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
        return ft.View(
            controls=[
                ft.Text("لیست مشتریان 👥", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GOLD),
                ft.Row([
                    self.entry_search,
                    ft.ElevatedButton("🔍 جستجو", bgcolor=ft.Colors.GOLD, color="#1a2332", on_click=self.search_customers),
                    ft.ElevatedButton("🔄 بروزرسانی", bgcolor="#2c3e50", color=ft.Colors.WHITE, on_click=self.load_customers),
                ], spacing=10),
                ft.Container(content=self.customers_list, expand=True),
            ]
        )
    
    def create_expenses_tab(self):
        self.expenses_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
        return ft.View(
            controls=[
                ft.Text("مصارف دوکان 💰", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GOLD),
                ft.Row([self.entry_expense_title, self.entry_expense_amount], spacing=10),
                ft.Row([
                    ft.ElevatedButton("❌ لغو", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=self.cancel_expense_edit, expand=True),
                    ft.ElevatedButton("💾 ذخیره", bgcolor=ft.Colors.GOLD, color="#1a2332", on_click=self.save_expense, expand=True),
                ], spacing=10),
                ft.Container(content=self.expenses_list, expand=True),
            ]
        )
    
    def create_report_tab(self):
        return ft.View(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("گزارش مالی 📊", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GOLD),
                ft.Row([
                    self.stat_card("💵 مجموع درآمد", self.income_value, ft.Colors.GREEN),
                    self.stat_card("💸 مجموع مصارف", self.expenses_value, ft.Colors.RED),
                    self.stat_card("📈 سود خالص", self.profit_value, ft.Colors.GOLD),
                ], spacing=10, wrap=True),
                ft.ElevatedButton("🔄 محاسبه گزارش", bgcolor=ft.Colors.GOLD, color="#1a2332",
                                 on_click=self.calculate_report, width=self.page.width-40 if self.page.width else 300),
            ]
        )
    
    def stat_card(self, title, value, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=14, color=ft.Colors.WHITE70),
                value,
            ], horizontal_alignment=ft.CrossAxisAlignment.END),
            bgcolor="#34495e", padding=20, border_radius=15, expand=True, min_width=150
        )
    
    def save_order(self, e):
        try:
            code = int(self.entry_clothing_code.value or 0)
            price = float(self.entry_price.value or 0)
            name = self.entry_name.value.strip()
            surname = self.entry_surname.value.strip()
            phone = self.entry_phone.value.strip()
            
            if not all([code, price, name, surname, phone]):
                self.show_snackbar("لطفاً تمام فیلدهای ضروری را پر کنید!", ft.Colors.RED)
                return
            
            measurements = {k: float(v.value) if v.value else None for k, v in self.measure_entries.items()}
            order_date = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
            clothing_type = self.entry_clothing_type.value or "نامشخص"
            
            conn = sqlite3.connect('doosti.db')
            cursor = conn.cursor()
            
            if self.editing_order_id:
                cursor.execute('''UPDATE orders SET clothing_code=?, customer_name=?, customer_surname=?,
                    phone=?, clothing_type=?, price=?, height=?, sleeve=?, shoulder=?, collar=?,
                    chest=?, skirt=?, pants_length=?, leg=? WHERE id=?''',
                    (code, name, surname, phone, clothing_type, price,
                     measurements['height'], measurements['sleeve'], measurements['shoulder'],
                     measurements['collar'], measurements['chest'], measurements['skirt'],
                     measurements['pants_length'], measurements['leg'], self.editing_order_id))
                self.show_snackbar("✅ سفارش بروزرسانی شد", ft.Colors.GREEN)
                self.editing_order_id = None
            else:
                cursor.execute('''INSERT INTO orders (clothing_code, customer_name, customer_surname, phone,
                    clothing_type, price, height, sleeve, shoulder, collar, chest, skirt, pants_length, leg, order_date)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (code, name, surname, phone, clothing_type, price,
                     measurements['height'], measurements['sleeve'], measurements['shoulder'],
                     measurements['collar'], measurements['chest'], measurements['skirt'],
                     measurements['pants_length'], measurements['leg'], order_date))
                self.show_snackbar("✅ سفارش ذخیره شد", ft.Colors.GREEN)
            
            conn.commit()
            conn.close()
            self.clear_order_form()
            self.load_customers(None)
        except ValueError:
            self.show_snackbar("❌ کود لباس و قیمت باید عدد باشند!", ft.Colors.RED)
    
    def clear_order_form(self):
        for entry in [self.entry_name, self.entry_surname, self.entry_phone,
                     self.entry_clothing_code, self.entry_clothing_type, self.entry_price]:
            entry.value = ""
        for entry in self.measure_entries.values():
            entry.value = ""
        self.page.update()
    
    def cancel_edit(self, e):
        self.editing_order_id = None
        self.clear_order_form()
    
    def load_customers(self, e):
        self.customers_list.controls.clear()
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, customer_name, customer_surname, phone, clothing_code, clothing_type, price, order_date FROM orders ORDER BY id DESC')
        orders = cursor.fetchall()
        conn.close()
        
        for order in orders:
            row = ft.Container(
                content=ft.Column([
                    ft.Text(f"👤 {order[1]} {order[2]}", weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.WHITE),
                    ft.Text(f"📱 {order[3]}  |  🏷️ کود: {order[4]}", size=13, color=ft.Colors.WHITE70),
                    ft.Text(f"👔 {order[5]}  |  💰 {order[6]:,.0f} افغانی", size=13, color=ft.Colors.GOLD),
                    ft.Row([
                        ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE, on_click=lambda e, oid=order[0]: self.edit_order(oid)),
                        ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=lambda e, oid=order[0]: self.delete_order(oid)),
                    ], alignment=ft.MainAxisAlignment.END),
                ], spacing=5),
                bgcolor="#34495e", padding=15, border_radius=10, margin=ft.margin.only(bottom=10)
            )
            self.customers_list.controls.append(row)
        self.page.update()
    
    def edit_order(self, order_id):
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id=?', (order_id,))
        o = cursor.fetchone()
        conn.close()
        if not o: return
        
        self.editing_order_id = o[0]
        self.entry_name.value = o[1]
        self.entry_surname.value = o[2]
        self.entry_phone.value = o[3]
        self.entry_clothing_code.value = str(o[4]) if o[4] else ""
        self.entry_clothing_type.value = o[5] or ""
        self.entry_price.value = str(o[6])
        
        measure_keys = ['height','sleeve','shoulder','collar','chest','skirt','pants_length','leg']
        for i, key in enumerate(measure_keys):
            self.measure_entries[key].value = str(o[7+i]) if o[7+i] is not None else ""
        
        self.page.update()
        self.show_snackbar("📝 در حالت ویرایش - تغییرات را ذخیره کنید", ft.Colors.GOLD)
    
    def delete_order(self, e):
        order_id = e.control.data if hasattr(e.control, 'data') else None
        # ساده‌سازی: حذف مستقیم
        def confirm_delete(ev):
            conn = sqlite3.connect('doosti.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM orders WHERE id=?', (order_id,))
            conn.commit()
            conn.close()
            self.load_customers(None)
            self.show_snackbar("🗑️ سفارش حذف شد", ft.Colors.RED)
            self.page.overlay.clear()
            self.page.update()
        
        alert = ft.AlertDialog(
            modal=True,
            title=ft.Text("تأیید حذف"),
            content=ft.Text("آیا از حذف این سفارش اطمینان دارید؟"),
            actions=[
                ft.TextButton("لغو", on_click=lambda e: self.close_alert()),
                ft.TextButton("حذف", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        # ذخیره order_id برای دسترسی در confirm
        alert.data = order_id
        self.page.overlay.append(alert)
        alert.open = True
        self.page.update()
    
    def close_alert(self):
        self.page.overlay.clear()
        self.page.update()
    
    def search_customers(self, e):
        search = self.entry_search.value.strip()
        self.customers_list.controls.clear()
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        if not search:
            cursor.execute('SELECT id, customer_name, customer_surname, phone, clothing_code, clothing_type, price, order_date FROM orders ORDER BY id DESC')
        else:
            cursor.execute('''SELECT id, customer_name, customer_surname, phone, clothing_code, clothing_type, price, order_date
                FROM orders WHERE customer_name LIKE ? OR customer_surname LIKE ? OR phone LIKE ?
                OR CAST(clothing_code AS TEXT) LIKE ? ORDER BY id DESC''',
                (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'))
        
        orders = cursor.fetchall()
        conn.close()
        
        for order in orders:
            row = ft.Container(
                content=ft.Column([
                    ft.Text(f"👤 {order[1]} {order[2]}", weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.WHITE),
                    ft.Text(f"📱 {order[3]}  |  🏷️ کود: {order[4]}", size=13, color=ft.Colors.WHITE70),
                    ft.Text(f"👔 {order[5]}  |  💰 {order[6]:,.0f} افغانی", size=13, color=ft.Colors.GOLD),
                ], spacing=5),
                bgcolor="#34495e", padding=15, border_radius=10, margin=ft.margin.only(bottom=10)
            )
            self.customers_list.controls.append(row)
        self.page.update()
    
    def save_expense(self, e):
        title = self.entry_expense_title.value.strip()
        amount = self.entry_expense_amount.value.strip()
        
        if not title or not amount:
            self.show_snackbar("❌ عنوان و مبلغ را وارد کنید!", ft.Colors.RED)
            return
        try:
            amount = float(amount)
        except ValueError:
            self.show_snackbar("❌ مبلغ باید عدد باشد!", ft.Colors.RED)
            return
        
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        date = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        cursor.execute('INSERT INTO expenses (title, amount, date) VALUES (?,?,?)', (title, amount, date))
        conn.commit()
        conn.close()
        
        self.entry_expense_title.value = ""
        self.entry_expense_amount.value = ""
        self.load_expenses(None)
        self.show_snackbar("✅ مصرف ذخیره شد", ft.Colors.GREEN)
    
    def cancel_expense_edit(self, e):
        self.entry_expense_title.value = ""
        self.entry_expense_amount.value = ""
        self.page.update()
    
    def load_expenses(self, e):
        self.expenses_list.controls.clear()
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, amount, date FROM expenses ORDER BY id DESC')
        expenses = cursor.fetchall()
        conn.close()
        
        for exp in expenses:
            row = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(f"💰 {exp[1]}", weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.WHITE),
                        ft.Text(f"📅 {exp[3]}", size=12, color=ft.Colors.WHITE70),
                    ], expand=True),
                    ft.Text(f"{exp[2]:,.0f} افغانی", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="#34495e", padding=15, border_radius=10, margin=ft.margin.only(bottom=10)
            )
            self.expenses_list.controls.append(row)
        self.page.update()
    
    def calculate_report(self, e):
        conn = sqlite3.connect('doosti.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COALESCE(SUM(price),0) FROM orders')
        income = cursor.fetchone()[0]
        cursor.execute('SELECT COALESCE(SUM(amount),0) FROM expenses')
        expenses = cursor.fetchone()[0]
        conn.close()
        
        self.income_value.value = f"{income:,.0f} افغانی"
        self.expenses_value.value = f"{expenses:,.0f} افغانی"
        self.profit_value.value = f"{income-expenses:,.0f} افغانی"
        self.page.update()
    
    def show_snackbar(self, message, color):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
        )
        self.page.snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    DoostiApp(page)


if __name__ == "__main__":
    ft.app(target=main)
