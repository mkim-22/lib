from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from database.db import get_library_statistics


class ManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Руководитель библиотеки")
        self.resize(400, 300)

        self.total_label = QLabel()
        self.issued_label = QLabel()
        self.free_label = QLabel()
        self.active_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.total_label)
        layout.addWidget(self.issued_label)
        layout.addWidget(self.free_label)
        layout.addWidget(self.active_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_statistics()

    def load_statistics(self):
        stats = get_library_statistics()
        self.total_label.setText(f"Общее количество книг: {stats['total']}")
        self.issued_label.setText(f"Выдано книг: {stats['issued']}")
        self.free_label.setText(f"Свободные книги: {stats['free']}")
        self.active_label.setText(f"Активные бронирования: {stats['reserved']}")
