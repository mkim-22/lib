from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from database.db import register_client


class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setFixedSize(300, 250)

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("ФИО")

        self.login = QLineEdit()
        self.login.setPlaceholderText("Логин")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        btn_register = QPushButton("Зарегистрироваться")
        btn_register.clicked.connect(self.register)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("ФИО"))
        layout.addWidget(self.full_name)
        layout.addWidget(QLabel("Логин"))
        layout.addWidget(self.login)
        layout.addWidget(QLabel("Пароль"))
        layout.addWidget(self.password)
        layout.addWidget(btn_register)

    def register(self):
        if not self.full_name.text() or not self.login.text() or not self.password.text():
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        success, message = register_client(
            self.full_name.text(),
            self.login.text(),
            self.password.text()
        )

        if success:
            QMessageBox.information(self, "Успех", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", message)
