from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from database.db import get_database_connection

class ManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Руководитель библиотеки")
        self.resize(400, 300)

        self.total_books_label = QLabel()
        self.issued_books_label = QLabel()
        self.free_books_label = QLabel()
        self.active_reservations_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.total_books_label)
        layout.addWidget(self.issued_books_label)
        layout.addWidget(self.free_books_label)
        layout.addWidget(self.active_reservations_label)

        container_widget = QWidget()
        container_widget.setLayout(layout)
        self.setCentralWidget(container_widget)

        self.load_library_statistics()

    def load_library_statistics(self):
        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:
            database_cursor.execute("SELECT SUM(total_count) AS total_books FROM books")
            total_books = database_cursor.fetchone()["total_books"]

            database_cursor.execute("SELECT COUNT(*) AS issued_books FROM reservations WHERE status='Выдано'")
            issued_books = database_cursor.fetchone()["issued_books"]

            database_cursor.execute("SELECT COUNT(*) AS active_reservations FROM reservations WHERE status='Забронировано'")
            active_reservations = database_cursor.fetchone()["active_reservations"]

            free_books = total_books - issued_books - active_reservations

        database_connection.close()

        self.total_books_label.setText(f"Общее количество книг: {total_books}")
        self.issued_books_label.setText(f"Выдано книг: {issued_books}")
        self.free_books_label.setText(f"Свободные книги: {free_books}")
        self.active_reservations_label.setText(f"Активные бронирования: {active_reservations}")
