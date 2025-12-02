from database.connection import  SQLiteConnection
from models.turma import Turma

class TurmaRepository:
    def __init__(self):
        self.conn , self.cursor = SQLiteConnection.get_connection()
    
    def salvar(self, turma: Turma):
        # 1. SALVAR O REGISTRO PRINCIPAL NA TABELA 'turma'
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

    def buscar_por_id(self, id: str) -> Turma | None:
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
    
    def listar(self) -> list[Turma] :

        sql = """
            SELECT * FROM turma;
        """

        self.cursor.execute(sql)
        all_row = self.cursor.fetchall()

        turmas = [Turma(id=row['id'], periodo=row['periodo'], vagas=row['vagas'], curso_codigo=row['curso_codigo']) for row in all_row]
        return turmas

    def deletar(self, id: str):
        sql = """
            DELETE FROM turma WHERE id = ?;
        """
        
        self.cursor.execute(sql, (id, ))
        self.conn.commit()
        print("Deletado com sucesso!")
    
        return True
    
    def atualizar(self, turma: Turma):
        sql = """
            UPDATE turma
            SET  = ?,  = ?
            WHERE id = ?;
        """

        self.cursor.execute(sql, ())
        self.conn.commit()
        print("Atualizado com sucesso!")

        return True