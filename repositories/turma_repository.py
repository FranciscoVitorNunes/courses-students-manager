from database.connection import  SQLiteConnection
from models.turma import Turma

class TurmaRepository:
    def __init__(self):
        self.conn , self.cursor = SQLiteConnection.get_connection()
    
    def create(self, turma: Turma):
        sql_turma = """
            INSERT INTO turma(id, periodo, vagas, curso_codigo) VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(sql_turma, (turma.id, turma.periodo, turma.vagas, turma.curso.codigo))
        
        sql_horario = """
            INSERT INTO horario_turma(turma_id, dia, intervalo) VALUES (?, ?, ?)
        """
        
        dados_horarios = []
        
        for dia, intervalo in turma.horarios.items():
            dados_horarios.append((turma.id, dia, intervalo))

        if dados_horarios:
            self.cursor.executemany(sql_horario, dados_horarios)

        self.conn.commit()
        
        print("Turma e horários criados com sucesso!")

    def get_by_id(self, id: str) -> Turma | None:
        sql = """
            SELECT * FROM turma WHERE id = ?;
        """

        self.cursor.execute(sql, (id, ))
        row = self.cursor.fetchone()

        if row is None:
            return None
        
        sql = """
        SELECT dia, intervalo FROM horario_turma WHERE turma_id = ?
        """
        self.cursor.execute(sql, (id, ))
        all_horarios = self.cursor.fetchall()

        horarios_dict = {}
        for h in all_horarios:
            horarios_dict[h['dia']] = h['intervalo']

        return {
        "id": row["id"],
        "periodo": row["periodo"],
        "vagas": row["vagas"],
        "curso_codigo": row["curso_codigo"],
        "horarios": horarios_dict
        }
    
    def list_all(self) -> list[dict]:
            sql_turmas = """SELECT id, periodo, vagas, curso_codigo FROM turma;"""
            self.cursor.execute(sql_turmas)
            turmas_rows = self.cursor.fetchall()

            if not turmas_rows:
                return []

            sql_horarios = """SELECT turma_id, dia, intervalo FROM horario_turma;"""
            self.cursor.execute(sql_horarios)
            all_horarios_rows = self.cursor.fetchall()
            
            horarios_por_turma = {}
            for h_row in all_horarios_rows:
                turma_id = h_row['turma_id']
                if turma_id not in horarios_por_turma:
                    horarios_por_turma[turma_id] = {}
                horarios_por_turma[turma_id][h_row['dia']] = h_row['intervalo']
                
            turmas_completas_em_dados = []
            for row in turmas_rows:
                turma_id = row['id']
                
                turma_dict = {
                    "id": turma_id,
                    "periodo": row["periodo"],
                    "vagas": row["vagas"],
                    "curso_codigo": row["curso_codigo"],
                    "horarios": horarios_por_turma.get(turma_id, {})
                }
                turmas_completas_em_dados.append(turma_dict)
                
            return turmas_completas_em_dados

    def delete(self, id: str):
        sql_horarios = "DELETE FROM horario_turma WHERE turma_id = ?"
        self.cursor.execute(sql_horarios, (id,))

        sql = """
            DELETE FROM turma WHERE id = ?;
        """
        
        self.cursor.execute(sql, (id, ))
        self.conn.commit()
        print("Deletado com sucesso!")
    
        return True
    
    def update(self, turma: Turma):
        sql = """
            UPDATE turma
            SET  = ?,  = ?
            WHERE id = ?;
        """

        self.cursor.execute(sql, ())
        self.conn.commit()
        print("Atualizado com sucesso!")

        return True