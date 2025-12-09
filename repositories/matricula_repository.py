from database.connection import  SQLiteConnection
from models.matricula import Matricula

class MatriculaRepository:
    def __init__(self):
        self.conn , self.cursor = SQLiteConnection.get_connection()
    

    def get_by_id(self, id: int):
        self.cursor.execute("SELECT * FROM matricula WHERE id = ?", (id,))
        row = self.cursor.fetchone()
        if not row:
            return None
        return dict(row)
    
    def salvar(self, matricula: Matricula):
        sql= """
            INSERT INTO matricula(aluno_matricula, turma_id) VALUES (?, ?)
        """

        self.cursor.execute(sql, (matricula.aluno.matricula, matricula.turma.id))
        self.conn.commit()
        print("Matrícula realizada com sucesso!")
    
    def buscar_por_aluno_e_turma(self, aluno_matricula: str, turma_id: str) -> bool:
        """Retorna True se matricula existir"""
        sql= """
            SELECT * FROM matricula WHERE aluno_matricula = ? AND turma_id = ?
        """

        self.cursor.execute(sql, (aluno_matricula, turma_id))
        row = self.cursor.fetchone()

        return row is not None
    
    def contar_matriculas_por_turma(self, turma_id: int) -> int:

        sql = """
            SELECT COUNT(*) FROM matricula WHERE turma_id = ?
        """
        
        self.cursor.execute(sql, (turma_id,))
        
        contagem = self.cursor.fetchone()[0]
        
        return contagem

    def listar_turmas_por_aluno(self, aluno_matricula: str) -> list[str]:
        sql = """
            SELECT turma_id FROM matricula WHERE aluno_matricula = ?;
        """

        self.cursor.execute(sql, (aluno_matricula, ))
        all_row = self.cursor.fetchall()

        turmasIDs = [row['turma_id'] for row in all_row]
        return turmasIDs