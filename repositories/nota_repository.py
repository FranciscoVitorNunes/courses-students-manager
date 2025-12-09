from database.connection import  SQLiteConnection

class NotaRepository:
    def __init__(self):
        self.conn , self.cursor = SQLiteConnection.get_connection()

    def get_by_matricula(self, matricula_id: int):
        self.cursor.execute("SELECT * FROM nota WHERE matricula_id = ?", (matricula_id,))
        return [dict(r) for r in self.cursor.fetchall()]

    def create(self, dados: dict):
        sql = "INSERT INTO nota (matricula_id, avaliacao, nota) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (dados["matricula_id"], dados["avaliacao"], dados["nota"]))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def delete(self, id: int):
        self.cursor.execute("DELETE FROM nota WHERE id = ?", (id,))
        self.conn.commit()
        self.cursor.execute("SELECT changes();")
        return self.cursor.fetchone()[0] > 0