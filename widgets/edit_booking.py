from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QDateEdit, QComboBox, QPushButton, QMessageBox
)
from database.db import (
    get_reservation_by_id,
    update_reservation,
    get_all_clients,
    get_all_books
)


class EditReservationDialog(QDialog):
    def __init__(self, reservation_id):
        super().__init__()
        self.reservation_id = reservation_id
        self.setWindowTitle("Редактировать бронь")

        self.status_box = QComboBox()
        self.status_box.addItems(
            ["Забронировано", "Выдано", "Возвращено"]
        )

        self.date_start = QDateEdit()
        self.date_end = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_end.setCalendarPopup(True)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save)

        self.client_box = QComboBox()
        self.book_box = QComboBox()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Клиент"))
        layout.addWidget(self.client_box)

        layout.addWidget(QLabel("Книга"))
        layout.addWidget(self.book_box)

        layout.addWidget(QLabel("Дата начала"))
        layout.addWidget(self.date_start)
        layout.addWidget(QLabel("Дата конца"))
        layout.addWidget(self.date_end)
        layout.addWidget(QLabel("Статус"))
        layout.addWidget(self.status_box)
        layout.addWidget(self.save_button)

        self.load_data()

    def load_data(self):
        # клиенты
        for c in get_all_clients():
            self.client_box.addItem(c["full_name"], c["id"])

        # книги
        for b in get_all_books():
            self.book_box.addItem(b["title"], b["id"])

        data = get_reservation_by_id(self.reservation_id)

        # установить текущего клиента
        index = self.client_box.findData(data["user_id"])
        self.client_box.setCurrentIndex(index)

        # установить текущую книгу
        index = self.book_box.findData(data["book_id"])
        self.book_box.setCurrentIndex(index)

        self.date_start.setDate(
            QDate.fromString(str(data["date_start"]), "yyyy-MM-dd")
        )
        self.date_end.setDate(
            QDate.fromString(str(data["date_end"]), "yyyy-MM-dd")
        )

        self.status_box.setCurrentText(data["status"])

    def save(self):
        date_start = self.date_start.date().toPyDate()
        date_end = self.date_end.date().toPyDate()
        status = self.status_box.currentText()

        if date_end < date_start:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Дата возврата меньше даты выдачи"
            )
            return

        ok = update_reservation(
            self.reservation_id,
            self.client_box.currentData(),
            self.book_box.currentData(),
            self.date_start.date().toPyDate(),
            self.date_end.date().toPyDate(),
            self.status_box.currentText()
        )

        if ok:
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Ошибка сохранения")

