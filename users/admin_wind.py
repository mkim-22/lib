from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QMessageBox
)
from database.db import get_database_connection

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Администратор библиотеки")
        self.resize(900, 500)

        self.reservations_table = QTableWidget()
        self.reservations_table.setColumnCount(7)
        self.reservations_table.setHorizontalHeaderLabels([
            "Клиент", "Книга", "Жанр", "Автор",
            "Дата выдачи", "Дата возврата", "Статус"
        ])

        self.search_input_field = QLineEdit()
        self.search_input_field.setPlaceholderText("Поиск...")

        self.status_filter_combobox = QComboBox()
        self.status_filter_combobox.addItems([
            "Все", "Забронировано", "Выдано", "Возвращено"
        ])

        self.search_button = QPushButton("Найти")
        self.search_button.clicked.connect(self.load_reservations)

        self.reset_button = QPushButton("Показать все")
        self.reset_button.clicked.connect(self.reset_filters)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_selected_reservation)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.search_input_field)
        top_layout.addWidget(self.status_filter_combobox)
        top_layout.addWidget(self.search_button)
        top_layout.addWidget(self.reset_button)
        top_layout.addWidget(self.delete_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.reservations_table)

        container_widget = QWidget()
        container_widget.setLayout(main_layout)
        self.setCentralWidget(container_widget)

        self.load_reservations()

    def load_reservations(self):
        database_connection = get_database_connection()
        if not database_connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        search_text = self.search_input_field.text()
        selected_status = self.status_filter_combobox.currentText()

        # Используем обычные таблицы вместо reservations_view
        sql_query = """
            SELECT r.id, u.full_name AS client_name, b.title AS book_title,
                   g.name AS genre, a.full_name AS author,
                   r.date_start, r.date_end, r.status
            FROM reservations AS r
            JOIN users AS u ON r.user_id = u.id
            JOIN books AS b ON r.book_id = b.id
            JOIN authors AS a ON b.author_id = a.id
            JOIN genres AS g ON b.genre_id = g.id
            WHERE (u.full_name LIKE %s OR b.title LIKE %s OR a.full_name LIKE %s)
        """
        query_parameters = [f"%{search_text}%"] * 3

        if selected_status != "Все":
            sql_query += " AND r.status = %s"
            query_parameters.append(selected_status)

        try:
            with database_connection.cursor() as database_cursor:
                database_cursor.execute(sql_query, query_parameters)
                query_results = database_cursor.fetchall()
        except Exception as error:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных:\n{error}")
            database_connection.close()
            return

        database_connection.close()

        self.reservations_table.setRowCount(len(query_results))
        self.reservation_ids_list = []

        for row_index, reservation_row in enumerate(query_results):
            self.reservation_ids_list.append(reservation_row["id"])
            self.reservations_table.setItem(row_index, 0, QTableWidgetItem(reservation_row["client_name"]))
            self.reservations_table.setItem(row_index, 1, QTableWidgetItem(reservation_row["book_title"]))
            self.reservations_table.setItem(row_index, 2, QTableWidgetItem(reservation_row["genre"]))
            self.reservations_table.setItem(row_index, 3, QTableWidgetItem(reservation_row["author"]))
            self.reservations_table.setItem(row_index, 4, QTableWidgetItem(str(reservation_row["date_start"])))
            self.reservations_table.setItem(row_index, 5, QTableWidgetItem(str(reservation_row["date_end"])))
            self.reservations_table.setItem(row_index, 6, QTableWidgetItem(reservation_row["status"]))

    def reset_filters(self):
        self.search_input_field.clear()
        self.status_filter_combobox.setCurrentIndex(0)
        self.load_reservations()

    def delete_selected_reservation(self):
        selected_row_index = self.reservations_table.currentRow()
        if selected_row_index == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return

        user_choice = QMessageBox.question(
            self, "Подтверждение",
            "Удалить выбранную запись?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if user_choice != QMessageBox.StandardButton.Yes:
            return

        reservation_id_to_delete = self.reservation_ids_list[selected_row_index]

        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:
            database_cursor.execute(
                "DELETE FROM reservations WHERE id=%s",
                (reservation_id_to_delete,)
            )
        database_connection.close()

        QMessageBox.information(self, "Успех", "Запись удалена")
        self.load_reservations()



