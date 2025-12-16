from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database.db import check_login
from auth.reg_wind import RegisterDialog



class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")

        self.login = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        btn = QPushButton("Войти")
        btn.clicked.connect(self.auth)

        self.register_btn = QPushButton("Регистрация")
        self.register_btn.clicked.connect(self.open_register)


        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Логин"))
        layout.addWidget(self.login)
        layout.addWidget(QLabel("Пароль"))
        layout.addWidget(self.password)
        layout.addWidget(btn)
        layout.addWidget(self.register_btn)

    def auth(self):
        result = check_login(
            self.login.text(),
            self.password.text()
        )

        if not result:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return

        user_id = result["user_id"]
        role = result["role"]

        self.close()

        if role == "admin":
            from users.admin_wind import AdminWindow
            self.w = AdminWindow()
        elif role == "manager":
            from users.manager_wind import ManagerWindow
            self.w = ManagerWindow()
        else:
            from users.client_wind import ClientWindow
            self.w = ClientWindow(user_id)

        self.w.show()

    def open_register(self):
        dialog = RegisterDialog()
        dialog.exec()


