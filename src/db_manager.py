"""
Файл с классом для работы с БД.
"""
import sqlite3


class DatabaseManager:

    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)

    def read_table(self, table):
        return self.connection.cursor().execute(f'SELECT * FROM {table}')

    def insert_df(self):
        """
        через pd.to_sql надо
        :return:
        """
        pass
