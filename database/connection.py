import sqlite3
import os

class SQLiteConnection:
    """Gerencia a conexão SQLite e fornece (connection, cursor)."""
    _connection = None
    _cursor = None
    _database_file = "banco_dados.db"

    @classmethod
    def get_connection(cls):
        """Retorna uma tupla (connection, cursor). Cria a conexão na primeira chamada."""
        if cls._connection is None:
            print("🚨 BANCO REAL:", os.path.abspath(cls._database_file))
            cls._connection = sqlite3.connect(cls._database_file, check_same_thread=False)
            cls._connection.row_factory = sqlite3.Row
            cls._connection.execute("PRAGMA foreign_keys = ON;")
            cls._cursor = cls._connection.cursor()

        return cls._connection, cls._cursor

    @classmethod
    def close_connection(cls):
        """Fecha a conexão, se aberta."""
        if cls._cursor:
            cls._cursor.close()
            cls._cursor = None
        if cls._connection:
            cls._connection.close()
            cls._connection = None


