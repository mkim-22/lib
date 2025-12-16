from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QHBoxLayout, QMessageBox, QDateEdit
)
from PyQt6.QtCore import QDate
from database.db import (
    get_all_reservations,
    get_reservations_by_status,
    get_reservations_by_date_range,
    delete_reservation,
    update_reservation
)


class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Администратор библиотеки")
        self.resize(1000, 500)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Клиент", "Книга", "Жанр", "Автор", "Дата выдачи", "Дата возврата", "Статус"]
        )

        # Кнопки фильтров
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Все", "Забронировано", "Выдано", "Возвращено"])
        self.status_combo.currentTextChanged.connect(self.filter_status)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate())
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        btn_filter_date = QPushButton("Фильтр по дате")
        btn_filter_date.clicked.connect(self.filter_date)

        btn_show_all = QPushButton("Показать все")
        btn_show_all.clicked.connect(self.load_data)

        btn_delete = QPushButton("Удалить выбранное")
        btn_delete.clicked.connect(self.delete_selected)

        # Layout
        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.status_combo)
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(btn_filter_date)
        filter_layout.addWidget(btn_show_all)
        filter_layout.addWidget(btn_delete)

        layout.addLayout(filter_layout)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_data()

    def load_data(self):
        self.reservations = get_all_reservations()
        self.populate_table(self.reservations)

    def populate_table(self, data):
        self.table.setRowCount(len(data))
        for i, r in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(r["client_name"]))
            self.table.setItem(i, 2, QTableWidgetItem(r["book_title"]))
            self.table.setItem(i, 3, QTableWidgetItem(r["genre"]))
            self.table.setItem(i, 4, QTableWidgetItem(r["author"]))
            self.table.setItem(i, 5, QTableWidgetItem(str(r["date_start"])))
            self.table.setItem(i, 6, QTableWidgetItem(str(r["date_end"])))
            self.table.setItem(i, 7, QTableWidgetItem(r["status"]))

    def filter_status(self, status):
        if status == "Все":
            self.load_data()
        else:
            self.reservations = get_reservations_by_status(status)
            self.populate_table(self.reservations)

    def filter_date(self):
        from_date = self.date_from.date().toPython()
        to_date = self.date_to.date().toPython()
        self.reservations = get_reservations_by_date_range(from_date, to_date)
        self.populate_table(self.reservations)

    def delete_selected(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return
        reservation_id = int(self.table.item(row, 0).text())
        if delete_reservation(reservation_id):
            QMessageBox.information(self, "Успех", "Запись удалена")
            self.load_data()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось удалить запись")
