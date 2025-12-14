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
