import sqlite3

class SQlitteConnection:
    _connection = None
    _cursor = None
    _database_file = "banco_dados.db"

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            cls._connection = sqlite3.connect(cls._database_file)

            cls._connection.row_factory = sqlite3.Row

            cls._curso = cls._connection.cursor

            return cls._connection, cls._cursor


