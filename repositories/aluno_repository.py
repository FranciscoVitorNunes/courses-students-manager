from database.connection import  SQLiteConnection
from models import Aluno

class AlunoRepository:
    def __init__(self):
        self.conn , self.cursor = SQLiteConnection.get_connection()
    
    def salvar(self, aluno: Aluno):
        sql= """
            INSERT INTO aluno(matricula, nome, email, cr) VALUES (?, ?, ?, ?)
        """

        self.cursor.execute(sql, (aluno.matricula, aluno.nome, aluno.email, aluno.cr))
        self.conn.commit()
        print("Aluno criado com sucesso!")

    def buscar_por_matricula(self, matricula: str) -> Aluno | None:
        sql = """
            SELECT * FROM aluno WHERE matricula = ?;
        """

        self.cursor.execute(sql, (matricula, ))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Aluno(matricula=row['matricula'], nome=row['nome'], email=row['email'])
    
    def listar(self) -> list[Aluno] :

        sql = """
            SELECT * FROM aluno;
        """

        self.cursor.execute(sql)
        all_row = self.cursor.fetchall()

        alunos = [Aluno(matricula=row['matricula'], nome=row['nome'], email=row['email']) for row in all_row]
        return alunos
    
    def deletar(self, matricula: str):
        sql = """
            DELETE FROM aluno WHERE matricula = ?;
        """
        
        self.cursor.execute(sql, (matricula, ))
        self.conn.commit()
        print("Deletado com sucesso!")
    
        return 
    
    def atualizar(self, aluno: Aluno):
        sql = """
            UPDATE aluno
            SET nome = ?, email = ?
            WHERE matricula = ?;
        """

        self.cursor.execute(sql, (aluno.nome, aluno.email, aluno.matricula))
        self.conn.commit()
        print("Atualizado com sucesso!")