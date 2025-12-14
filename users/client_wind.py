from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QTabWidget, QMessageBox
)
from database.db import get_connection
from datetime import date, timedelta

class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Клиент библиотеки")
        self.resize(900, 500)

        self.tab_widget = QTabWidget()
        self.catalog_tab = QWidget()
        self.my_reservations_tab = QWidget()

        self.tab_widget.addTab(self.catalog_tab, "Каталог книг")
        self.tab_widget.addTab(self.my_reservations_tab, "Мои бронирования")

        self.initialize_catalog_tab()
        self.initialize_reservations_tab()

        self.setCentralWidget(self.tab_widget)

    # ---------- КАТАЛОГ ----------
    def initialize_catalog_tab(self):
        layout = QVBoxLayout()

        self.catalog_table = QTableWidget()
        self.catalog_table.setColumnCount(3)
        self.catalog_table.setHorizontalHeaderLabels(["Название", "Автор", "Жанр"])

        self.reserve_book_button = QPushButton("Забронировать книгу")
        self.reserve_book_button.clicked.connect(self.reserve_selected_book)

        layout.addWidget(self.catalog_table)
        layout.addWidget(self.reserve_book_button)
        self.catalog_tab.setLayout(layout)

        self.load_catalog_books()

    def load_catalog_books(self):
        database_connection = get_connection()
        with database_connection.cursor() as database_cursor:
            database_cursor.execute("""
                SELECT b.id, b.title, a.full_name AS author, g.name AS genre
                FROM books AS b
                JOIN authors AS a ON b.author_id = a.id
                JOIN genres AS g ON b.genre_id = g.id
            """)
            query_results = database_cursor.fetchall()
        database_connection.close()

        self.catalog_table.setRowCount(len(query_results))
        self.catalog_book_ids_list = []

        for row_index, book_row in enumerate(query_results):
            self.catalog_book_ids_list.append(book_row["id"])
            self.catalog_table.setItem(row_index, 0, QTableWidgetItem(book_row["title"]))
            self.catalog_table.setItem(row_index, 1, QTableWidgetItem(book_row["author"]))
            self.catalog_table.setItem(row_index, 2, QTableWidgetItem(book_row["genre"]))

    def reserve_selected_book(self):
        selected_row_index = self.catalog_table.currentRow()
        if selected_row_index == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу")
            return

        book_id_to_reserve = self.catalog_book_ids_list[selected_row_index]
        start_date = date.today()
        end_date = start_date + timedelta(days=14)

        database_connection = get_connection()
        with database_connection.cursor() as database_cursor:
            database_cursor.execute("""
                SELECT total_count -
                (
                    SELECT COUNT(*) FROM reservations
                    WHERE book_id=%s AND status IN ('Забронировано','Выдано')
                ) AS available_count
                FROM books WHERE id=%s
            """, (book_id_to_reserve, book_id_to_reserve))
            availability_result = database_cursor.fetchone()
            if availability_result["available_count"] <= 0:
                QMessageBox.warning(self, "Недоступно", "Книга недоступна")
                return

            # Для упрощения берем user_id = 3 (client1) или 4 (client2)
            database_cursor.execute("""
                INSERT INTO reservations (user_id, book_id, date_start, date_end, status)
                VALUES (3, %s, %s, %s, 'Забронировано')
            """, (book_id_to_reserve, start_date, end_date))

        database_connection.close()
        QMessageBox.information(self, "Успех", "Книга забронирована")
        self.load_my_reservations()

    # ---------- МОИ БРОНИРОВАНИЯ ----------
    def initialize_reservations_tab(self):
        layout = QVBoxLayout()
        self.my_reservations_table = QTableWidget()
        self.my_reservations_table.setColumnCount(4)
        self.my_reservations_table.setHorizontalHeaderLabels(["Книга", "Дата начала", "Дата конца", "Статус"])
        layout.addWidget(self.my_reservations_table)
        self.my_reservations_tab.setLayout(layout)

        self.load_my_reservations()

    def load_my_reservations(self):
        database_connection = get_connection()
        with database_connection.cursor() as database_cursor:
            database_cursor.execute("""
                SELECT b.title, r.date_start, r.date_end, r.status
                FROM reservations AS r
                JOIN books AS b ON r.book_id = b.id
                WHERE r.user_id = 3
            """)
            query_results = database_cursor.fetchall()
        database_connection.close()

        self.my_reservations_table.setRowCount(len(query_results))
        for row_index, reservation_row in enumerate(query_results):
            self.my_reservations_table.setItem(row_index, 0, QTableWidgetItem(reservation_row["title"]))
            self.my_reservations_table.setItem(row_index, 1, QTableWidgetItem(str(reservation_row["date_start"])))
            self.my_reservations_table.setItem(row_index, 2, QTableWidgetItem(str(reservation_row["date_end"])))
            self.my_reservations_table.setItem(row_index, 3, QTableWidgetItem(reservation_row["status"]))
