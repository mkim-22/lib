import pymysql
from pymysql import MySQLError

def get_database_connection():
    """
    Возвращает подключение к базе данных MySQL.
    """
    try:
        database_connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='lib',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return database_connection
    except MySQLError as error:
        print("Ошибка подключения к базе данных:", error)
        return None


# =====================================================
# АВТОРИЗАЦИЯ
# =====================================================
def check_login(login, password):
    db = get_database_connection()
    if not db:
        return None

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT users.id AS user_id,
                       roles.name AS role
                FROM users
                JOIN roles ON users.role_id = roles.id
                WHERE users.login = %s AND users.password = %s
            """, (login, password))
            return cursor.fetchone()
    finally:
        db.close()



def register_client(full_name, login, password):
    db = get_database_connection()
    if not db:
        return False, "Ошибка подключения к БД"

    try:
        with db.cursor() as cursor:
            # Проверка логина
            cursor.execute(
                "SELECT id FROM users WHERE login = %s",
                (login,)
            )
            if cursor.fetchone():
                return False, "Логин уже существует"

            # Получаем id роли client
            cursor.execute(
                "SELECT id FROM roles WHERE name = 'client'"
            )
            role_id = cursor.fetchone()["id"]

            # Создаём пользователя
            cursor.execute("""
                INSERT INTO users (full_name, login, password, role_id)
                VALUES (%s, %s, %s, %s)
            """, (full_name, login, password, role_id))

            return True, "Регистрация успешна"

    except Exception as e:
        print("Ошибка регистрации:", e)
        return False, "Ошибка при регистрации"
    finally:
        db.close()




# =====================================================
# КАТАЛОГ КНИГ (КЛИЕНТ)
# =====================================================
def get_all_books():
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT b.id, b.title,
                       a.full_name AS author,
                       g.name AS genre
                FROM books b
                JOIN authors a ON b.author_id = a.id
                JOIN genres g ON b.genre_id = g.id
            """)
            return cursor.fetchall()
    finally:
        db.close()


def check_book_availability(book_id):
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT total_count -
                (
                    SELECT COUNT(*)
                    FROM reservations
                    WHERE book_id = %s
                    AND status IN ('Забронировано', 'Выдано')
                ) AS available
                FROM books
                WHERE id = %s
            """, (book_id, book_id))
            return cursor.fetchone()
    finally:
        db.close()


def add_reservation(user_id, book_id, date_start, date_end):
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO reservations
                (user_id, book_id, date_start, date_end, status)
                VALUES (%s, %s, %s, %s, 'Забронировано')
            """, (user_id, book_id, date_start, date_end))
            return True
    except Exception as e:
        print("Ошибка бронирования:", e)
        return False
    finally:
        db.close()


def get_user_reservations(user_id):
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT b.title, r.date_start, r.date_end, r.status
                FROM reservations r
                JOIN books b ON r.book_id = b.id
                WHERE r.user_id = %s
            """, (user_id,))
            return cursor.fetchall()
    finally:
        db.close()


# ---------------------------------------------------
# АДМИН: ВСЕ БРОНИРОВАНИЯ
# ---------------------------------------------------
def get_all_reservations():
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT r.id, u.full_name AS client_name, b.title AS book_title,
                       g.name AS genre, a.full_name AS author,
                       r.date_start, r.date_end, r.status
                FROM reservations r
                JOIN users u ON r.user_id = u.id
                JOIN books b ON r.book_id = b.id
                JOIN authors a ON b.author_id = a.id
                JOIN genres g ON b.genre_id = g.id
            """)
            return cursor.fetchall()
    finally:
        db.close()


# ---------------------------------------------------
# ФИЛЬТР ПО СТАТУСУ
# ---------------------------------------------------
def get_reservations_by_status(status):
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT r.id, u.full_name AS client_name, b.title AS book_title,
                       g.name AS genre, a.full_name AS author,
                       r.date_start, r.date_end, r.status
                FROM reservations r
                JOIN users u ON r.user_id = u.id
                JOIN books b ON r.book_id = b.id
                JOIN authors a ON b.author_id = a.id
                JOIN genres g ON b.genre_id = g.id
                WHERE r.status = %s
            """, (status,))
            return cursor.fetchall()
    finally:
        db.close()


# ---------------------------------------------------
# ФИЛЬТР ПО ДАТАМ
# ---------------------------------------------------
def get_reservations_by_date_range(date_from, date_to):
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT r.id, u.full_name AS client_name, b.title AS book_title,
                       g.name AS genre, a.full_name AS author,
                       r.date_start, r.date_end, r.status
                FROM reservations r
                JOIN users u ON r.user_id = u.id
                JOIN books b ON r.book_id = b.id
                JOIN authors a ON b.author_id = a.id
                JOIN genres g ON b.genre_id = g.id
                WHERE r.date_start >= %s AND r.date_end <= %s
            """, (date_from, date_to))
            return cursor.fetchall()
    finally:
        db.close()


# ---------------------------------------------------
# УДАЛЕНИЕ БРОНИ
# ---------------------------------------------------
def delete_reservation(reservation_id):
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM reservations WHERE id = %s", (reservation_id,))
            return True
    except Exception as e:
        print("Ошибка удаления:", e)
        return False
    finally:
        db.close()


# ---------------------------------------------------
# РЕДАКТИРОВАНИЕ БРОНИ
# ---------------------------------------------------
def update_reservation(reservation_id, date_start, date_end, status):
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE reservations
                SET date_start = %s, date_end = %s, status = %s
                WHERE id = %s
            """, (date_start, date_end, status, reservation_id))
            return True
    except Exception as e:
        print("Ошибка обновления:", e)
        return False
    finally:
        db.close()



# =====================================================
# СТАТИСТИКА (РУКОВОДИТЕЛЬ)
# =====================================================
def get_library_statistics():
    db = get_database_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT SUM(total_count) AS total FROM books")
            total = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS issued FROM reservations WHERE status='Выдано'")
            issued = cursor.fetchone()["issued"]

            cursor.execute("SELECT COUNT(*) AS reserved FROM reservations WHERE status='Забронировано'")
            reserved = cursor.fetchone()["reserved"]

            free = total - issued - reserved

            return {
                "total": total,
                "issued": issued,
                "reserved": reserved,
                "free": free
            }
    finally:
        db.close()
