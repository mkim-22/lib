from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QTabWidget, QMessageBox
)
from datetime import date, timedelta
from database.db import get_all_books, check_book_availability, add_reservation, get_user_reservations
from PyQt6.QtWidgets import QPushButton



class ClientWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        self.setWindowTitle("Клиент библиотеки")
        self.resize(900, 500)

        # --- Central widget + layout ---
        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)

        # --- Кнопка выхода ---
        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)

        # --- Tabs ---
        self.tab_widget = QTabWidget()
        self.catalog_tab = QWidget()
        self.my_reservations_tab = QWidget()

        self.tab_widget.addTab(self.catalog_tab, "Каталог книг")
        self.tab_widget.addTab(self.my_reservations_tab, "Мои бронирования")

        # --- Добавляем в layout ---
        self.verticalLayout.addWidget(self.logout_button)
        self.verticalLayout.addWidget(self.tab_widget)

        self.setCentralWidget(self.centralwidget)

        # --- Инициализация вкладок ---
        self.init_catalog_tab()
        self.init_reservations_tab()



    # ----------------- КАТАЛОГ -----------------
    def init_catalog_tab(self):
        layout = QVBoxLayout()
        self.catalog_table = QTableWidget()
        self.catalog_table.setColumnCount(4)
        self.catalog_table.setHorizontalHeaderLabels(
            ["Название", "Автор", "Жанр", "Доступно"]
        )

        btn_reserve = QPushButton("Забронировать книгу")
        btn_reserve.clicked.connect(self.reserve_selected_book)

        layout.addWidget(self.catalog_table)
        layout.addWidget(btn_reserve)
        self.catalog_tab.setLayout(layout)
        self.load_catalog_books()

    from database.db import check_book_availability

    def load_catalog_books(self):
        books = get_all_books()
        self.catalog_table.setRowCount(len(books))
        self.book_ids = []

        for i, b in enumerate(books):
            self.book_ids.append(b["id"])

            available = check_book_availability(b["id"])["available"]

            self.catalog_table.setItem(i, 0, QTableWidgetItem(b["title"]))
            self.catalog_table.setItem(i, 1, QTableWidgetItem(b["author"]))
            self.catalog_table.setItem(i, 2, QTableWidgetItem(b["genre"]))
            self.catalog_table.setItem(i, 3, QTableWidgetItem(str(available)))

    def reserve_selected_book(self):
        row = self.catalog_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return

        book_id = self.book_ids[row]
        avail = check_book_availability(book_id)

        if avail["available"] <= 0:
            QMessageBox.warning(self, "Недоступно", "Книга недоступна")
            return

        start = date.today()
        end = start + timedelta(days=14)
        if add_reservation(self.user_id, book_id, start, end):
            QMessageBox.information(self, "Успех", "Книга забронирована")
            self.load_my_reservations()
            self.load_catalog_books()

        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось забронировать книгу")

    # ----------------- МОИ БРОНИ -----------------
    def init_reservations_tab(self):
        layout = QVBoxLayout()
        self.my_table = QTableWidget()
        self.my_table.setColumnCount(4)
        self.my_table.setHorizontalHeaderLabels(["Книга", "Дата начала", "Дата конца", "Статус"])
        layout.addWidget(self.my_table)
        self.my_reservations_tab.setLayout(layout)
        self.load_my_reservations()

    def load_my_reservations(self):
        reservations = get_user_reservations(self.user_id)
        self.my_table.setRowCount(len(reservations))
        for i, r in enumerate(reservations):
            self.my_table.setItem(i, 0, QTableWidgetItem(r["title"]))
            self.my_table.setItem(i, 1, QTableWidgetItem(str(r["date_start"])))
            self.my_table.setItem(i, 2, QTableWidgetItem(str(r["date_end"])))
            self.my_table.setItem(i, 3, QTableWidgetItem(r["status"]))

    def logout(self):
        from auth.login_wind import LoginWindow
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

