from database.connection import  SQLiteConnection

class FrequenciaRepository:
    def __init__(self):
        self.conn, self.cursor = SQLiteConnection.get_connection()

    def create(self, dados: dict):
        sql = "INSERT INTO frequencia (matricula_id, data, presenca) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (dados["matricula_id"], dados["data"], dados["presenca"]))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_by_matricula(self, matricula_id: int):
        self.cursor.execute("SELECT * FROM frequencia WHERE matricula_id = ?", (matricula_id,))
        return [dict(r) for r in self.cursor.fetchall()]