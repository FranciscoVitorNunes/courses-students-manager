from database.connection import  SQLiteConnection
from models.curso import Curso
from schemas.curso_schema import CursoSchema

class CursoRepository:
    def __init__(self):
        self.conn , self.cursor = SQLiteConnection.get_connection()

    def list_all(self)  -> list[CursoSchema]:
        sql = """
            SELECT * FROM curso;
        """

        self.cursor.execute(sql)
        all_rows = self.cursor.fetchall()

        cursos = [
            CursoSchema(
                codigo=row[0],
                nome=row[1],
                carga_horaria=row[2],
                ementa=row[3],
            ) for row in all_rows
        ]

        return cursos

    def create(self, curso: Curso):
        sql= """
            INSERT INTO curso(codigo, nome, carga_horaria, ementa) VALUES (?, ?, ?, ?)
        """

        self.cursor.execute(sql, (curso.codigo, curso.nome, curso.carga_horaria, curso.ementa))
        self.conn.commit()
        print("Curso criado com sucesso!")

    def get_by_codigo(self, codigo_curso) -> Curso | None:
        sql = """
            SELECT * FROM curso WHERE codigo = ?;
        """

        self.cursor.execute(sql, (codigo_curso, ))
        row = self.cursor.fetchone()

        if row is None:
            return None

        nome = row['nome']
        carga_horaria = row['carga_horaria']

        return Curso(codigo_curso, nome, carga_horaria)

    def delete(self, codigo_curso):
        sql = """
            DELETE FROM curso WHERE codigo = ?;
        """
        
        self.cursor.execute(sql, (codigo_curso, ))
        self.conn.commit()
        print("Deletado com sucesso!")

    def update(self, curso: Curso):
        sql = """
            UPDATE curso
            SET nome = ?, carga_horaria = ?, ementa = ?
            WHERE codigo = ?;
        """

        self.cursor.execute(sql, (curso.nome, curso.carga_horaria, curso.ementa, curso.codigo))
        self.conn.commit()
        print("Curso atualizado com sucesso!")


    def create_prerequisitos(self, codigo_curso,prerequisito_curso):
        sql= """
            INSERT INTO curso_prerequisito(curso_codigo, prerequisito_codigo) VALUES (?, ?)
        """

        self.cursor.execute(sql, (codigo_curso,prerequisito_curso))
        self.conn.commit()
        print("Prerequisito adicionado com sucesso!")


    def get_prerequisitos(self, codigo_curso):
        sql = """
            SELECT prerequisito_codigo FROM curso_prerequisito WHERE curso_codigo = ?
        """ 

        self.cursor.execute(sql, (codigo_curso, ))
        all_row = self.cursor.fetchall()

        lista_prerequisitos = [row['prerequisito_codigo'] for row in all_row ]
        return lista_prerequisitos