from database.connection import  SQLiteConnection
from schemas.aluno_schema import AlunoSchema, UpdateAlunoSchema

class AlunoRepository:
    def __init__(self):
        self.conn , self.cursor = SQLiteConnection.get_connection()
    
    def salvar(self, aluno: AlunoSchema):
        sql= """
            INSERT INTO aluno(matricula, nome, email, cr) VALUES (?, ?, ?, ?)
        """

        self.cursor.execute(sql, (aluno.matricula, aluno.nome, aluno.email, aluno.cr))
        self.conn.commit()
        print("Aluno criado com sucesso!")

    def buscar_por_matricula(self, matricula: str) -> AlunoSchema | None:
        sql = """
            SELECT * FROM aluno WHERE matricula = ?;
        """

        self.cursor.execute(sql, (matricula, ))
        row = self.cursor.fetchone()
        print("debugg row ==>", row)
        if row is None:
            return None

        return  AlunoSchema(
                matricula=row['matricula'], 
                nome=row['nome'], 
                email=row['email'], 
                cr=row['cr']
            ) 
    
    def listar(self) -> list[AlunoSchema] :
        sql = """
            SELECT * FROM aluno;
        """

        self.cursor.execute(sql)
        all_row = self.cursor.fetchall()

        alunos = [
            AlunoSchema(
                matricula=row['matricula'], 
                nome=row['nome'], 
                email=row['email'], 
                cr=row['cr']
            ) 
                for row in all_row
        ]
        return alunos
    
    def deletar(self, matricula: str):
        sql = """
            DELETE FROM aluno WHERE matricula = ?;
        """
        
        self.cursor.execute(sql, (matricula, ))
        self.conn.commit()
        print("Deletado com sucesso!")
    
        return 
    
    def atualizar(self, matricula: str,dados: dict):
        campos = []
        valores = []

        if "nome" in dados:
            campos.append("nome = ?")
            valores.append(dados["nome"])

        if "email" in dados:
            campos.append("email = ?")
            valores.append(dados["email"])

        if "cr" in dados:
            campos.append("cr = ?")
            valores.append(dados["cr"])

        if not campos:
            return False 

        sql = f"""
            UPDATE aluno
            SET {", ".join(campos)}
            WHERE matricula = ?;
        """
        valores.append(matricula)

        self.cursor.execute(sql, tuple(valores))
        self.conn.commit()

        self.cursor.execute("SELECT changes();")
        alterados = self.cursor.fetchone()[0]

        return alterados > 0