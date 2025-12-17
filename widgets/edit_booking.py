from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QDateEdit, QComboBox, QPushButton, QMessageBox
)
from database.db import get_reservation_by_id, update_reservation


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

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Дата начала"))
        layout.addWidget(self.date_start)
        layout.addWidget(QLabel("Дата конца"))
        layout.addWidget(self.date_end)
        layout.addWidget(QLabel("Статус"))
        layout.addWidget(self.status_box)
        layout.addWidget(self.save_button)

        self.load_data()

    def load_data(self):
        data = get_reservation_by_id(self.reservation_id)
        if not data:
            QMessageBox.warning(self, "Ошибка", "Бронь не найдена")
            self.reject()
            return

        self.date_start.setDate(
            QDate(
                data["date_start"].year,
                data["date_start"].month,
                data["date_start"].day
            )
        )

        self.date_end.setDate(
            QDate(
                data["date_end"].year,
                data["date_end"].month,
                data["date_end"].day
            )
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
            date_start,
            date_end,
            status
        )

        if ok:
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Ошибка сохранения")

