from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from database.db import get_database_connection

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)

        self.login_input_field = QLineEdit()
        self.login_input_field.setPlaceholderText("Логин")

        self.password_input_field = QLineEdit()
        self.password_input_field.setPlaceholderText("Пароль")
        self.password_input_field.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.perform_login)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Вход в систему"))
        layout.addWidget(self.login_input_field)
        layout.addWidget(self.password_input_field)
        layout.addWidget(self.login_button)

    def perform_login(self):
        entered_login = self.login_input_field.text()
        entered_password = self.password_input_field.text()

        database_connection = get_database_connection()
        if not database_connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        with database_connection.cursor() as database_cursor:
            database_cursor.execute("""
                SELECT roles.name AS user_role
                FROM users AS users_table
                JOIN roles AS roles ON users_table.role_id = roles.id
                WHERE users_table.login=%s AND users_table.password=%s
            """, (entered_login, entered_password))

            query_result = database_cursor.fetchone()

        database_connection.close()

        if query_result:
            self.open_window_for_role(query_result["user_role"])
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def open_window_for_role(self, user_role):
        self.close()

        if user_role == "admin":
            from users.admin_wind import AdminWindow
            self.role_window = AdminWindow()
        elif user_role == "manager":
            from users.manager_wind import ManagerWindow
            self.role_window = ManagerWindow()
        else:
            from users.client_wind import ClientWindow
            self.role_window = ClientWindow()

        self.role_window.show()
