from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QComboBox, QDateEdit, QPushButton, QMessageBox
)
from database.db import add_reservation


class AddReservationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить бронь")
        self.resize(300, 250)

        self.user_box = QComboBox()
        self.book_box = QComboBox()
        self.date_start = QDateEdit()
        self.date_end = QDateEdit()

        self.date_start.setCalendarPopup(True)
        self.date_end.setCalendarPopup(True)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Клиент"))
        layout.addWidget(self.user_box)
        layout.addWidget(QLabel("Книга"))
        layout.addWidget(self.book_box)
        layout.addWidget(QLabel("Дата начала"))
        layout.addWidget(self.date_start)
        layout.addWidget(QLabel("Дата конца"))
        layout.addWidget(self.date_end)
        layout.addWidget(self.save_button)

        self.load_data()

    def load_data(self):
        from database.db import get_all_clients, get_all_books

        self.user_box.clear()
        self.book_box.clear()

        for u in get_all_clients():
            self.user_box.addItem(u["full_name"], u["id"])

        for b in get_all_books():
            self.book_box.addItem(b["title"], b["id"])

    def save(self):
        user_id = self.user_box.currentData()
        book_id = self.book_box.currentData()
        date_start = self.date_start.date().toPyDate()
        date_end = self.date_end.date().toPyDate()

        if date_end < date_start:
            QMessageBox.warning(self, "Ошибка", "Дата возврата меньше даты выдачи")
            return

        ok = add_reservation(
            user_id,
            book_id,
            date_start,
            date_end
        )

        if ok:
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить бронь")

