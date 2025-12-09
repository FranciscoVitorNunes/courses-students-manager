from database.connection import  SQLiteConnection

class NotaRepository:
    def __init__(self):
        self.conn , self.cursor = SQLiteConnection.get_connection()

    def get_by_matricula(self, matricula_id: int):
        self.cursor.execute("SELECT * FROM nota WHERE matricula_id = ?", (matricula_id,))
        return [dict(r) for r in self.cursor.fetchall()]

