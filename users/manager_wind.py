from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from database.db import get_library_statistics

from PyQt6.QtWidgets import QPushButton, QDateEdit, QFileDialog, QMessageBox
from PyQt6.QtCore import QDate
from datetime import datetime
from datetime import timedelta
from database.db import get_statistics_by_period


class ManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Руководитель библиотеки")
        self.resize(400, 300)

        self.total_label = QLabel()
        self.issued_label = QLabel()
        self.free_label = QLabel()
        self.active_label = QLabel()

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())

        self.calc_button = QPushButton("Рассчитать за период")
        self.calc_button.clicked.connect(self.calculate_period)

        self.export_button = QPushButton("Выгрузить отчет (TXT)")
        self.export_button.clicked.connect(self.export_report)

        layout = QVBoxLayout()
        layout.addWidget(self.total_label)
        layout.addWidget(self.issued_label)
        layout.addWidget(self.free_label)
        layout.addWidget(self.active_label)

        layout.addWidget(QLabel("Дата с:"))
        layout.addWidget(self.date_from)
        layout.addWidget(QLabel("Дата по:"))
        layout.addWidget(self.date_to)
        layout.addWidget(self.calc_button)
        layout.addWidget(self.export_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_statistics()

    def calculate_period(self):
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()

        stats = get_statistics_by_period(date_from, date_to)

        # защита от None
        for key in ["issued", "reserved", "returned"]:
            if stats[key] is None:
                stats[key] = 0

        days = (date_to - date_from).days + 1
        avg_per_day = round(stats["total"] / days, 2) if days > 0 else 0

        self.period_stats = stats
        self.period_stats["avg"] = avg_per_day
        self.period_stats["days"] = days

        QMessageBox.information(
            self,
            "Статистика за период",
            f"Период: {days} дней\n\n"
            f"Всего операций: {stats['total']}\n"
            f"Выдано: {stats['issued']}\n"
            f"Забронировано: {stats['reserved']}\n"
            f"Возвращено: {stats['returned']}\n\n"
            f"Среднее количество книг в день: {avg_per_day}"
        )

    def export_report(self):
        if not hasattr(self, "period_stats"):
            QMessageBox.warning(self, "Ошибка", "Сначала выполните расчет")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчет",
            "library_report.txt",
            "Text Files (*.txt)"
        )

        if not file_path:
            return

        stats = self.period_stats

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("ОТЧЕТ БИБЛИОТЕКИ\n")
            file.write(f"Дата формирования: {datetime.now()}\n\n")
            file.write(f"Период: {self.date_from.date().toString()} — {self.date_to.date().toString()}\n\n")
            file.write(f"Всего операций: {stats['total']}\n")
            file.write(f"Выдано книг: {stats['issued']}\n")
            file.write(f"Забронировано: {stats['reserved']}\n")
            file.write(f"Возвращено: {stats['returned']}\n")
            file.write(f"Период (дней): {stats['days']}\n")
            file.write(f"Среднее количество книг в день: {stats['avg']}\n")

        QMessageBox.information(self, "Успех", "Отчет сохранен")

    def load_statistics(self):
        stats = get_library_statistics()
        self.total_label.setText(f"Общее количество книг: {stats['total']}")
        self.issued_label.setText(f"Выдано книг: {stats['issued']}")
        self.free_label.setText(f"Свободные книги: {stats['free']}")
        self.active_label.setText(f"Активные бронирования: {stats['reserved']}")
