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
    
    def update(self, id: str, dados: dict):
        campos = []
        valores = []

        if "periodo" in dados:
            campos.append("periodo = ?")
            valores.append(dados["periodo"])

        if "vagas" in dados:
            campos.append("vagas = ?")
            valores.append(dados["vagas"])

        if campos:
            sql = f"""
                UPDATE turma
                SET {", ".join(campos)}
                WHERE id = ?;
            """
            valores.append(id)
            self.cursor.execute(sql, tuple(valores))

        if "horarios" in dados:
            novos_horarios = dados["horarios"]

            sql = "SELECT dia, intervalo FROM horario_turma WHERE turma_id = ?"
            self.cursor.execute(sql, (id,))
            existentes_rows = self.cursor.fetchall()

            existentes = {h["dia"]: h["intervalo"] for h in existentes_rows}

            # Atualizar ou adicionar novos dias
            for dia, intervalo in novos_horarios.items():
                if dia in existentes:
                    if existentes[dia] != intervalo:
                        sql = """
                            UPDATE horario_turma
                            SET intervalo = ?
                            WHERE turma_id = ? AND dia = ?
                        """
                        self.cursor.execute(sql, (intervalo, id, dia))
                else:
                    sql = """
                        INSERT INTO horario_turma (dia, intervalo, turma_id)
                        VALUES (?, ?, ?)
                    """
                    self.cursor.execute(sql, (dia, intervalo, id))

            # Remover dias que sumiram
            dias_novos = set(novos_horarios.keys())
            dias_existentes = set(existentes.keys())

            dias_para_apagar = dias_existentes - dias_novos

            for dia in dias_para_apagar:
                sql = """
                    DELETE FROM horario_turma
                    WHERE turma_id = ? AND dia = ?
                """
                self.cursor.execute(sql, (id, dia))

        self.conn.commit()

        self.cursor.execute("SELECT changes();")
        alterados = self.cursor.fetchone()[0]

        return alterados > 0