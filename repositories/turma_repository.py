# repositories/turma_repository.py
from database.connection import SQLiteConnection
from models.turma import Turma
from typing import Optional, List, Dict, Any


class TurmaRepository:
    def __init__(self):
        self.conn, self.cursor = SQLiteConnection.get_connection()
    
    def create(self, turma: Turma) -> bool:
        """
        Cria uma nova turma no banco de dados.
        
        Args:
            turma: Objeto Turma a ser criado.
            
        Returns:
            True se criada com sucesso.
            
        Raises:
            ValueError: Se ocorrer erro ao salvar.
        """
        sql_turma = """
            INSERT INTO turma(id, periodo, vagas, curso_codigo, local) 
            VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(sql_turma, (
                turma.id, 
                turma.periodo, 
                turma.vagas, 
                turma.curso.codigo,
                turma.local
            ))
            
            sql_horario = """
                INSERT INTO horario_turma(turma_id, dia, intervalo) 
                VALUES (?, ?, ?)
            """
            
            dados_horarios = []
            for dia, intervalo in turma.horarios.items():
                dados_horarios.append((turma.id, dia, intervalo))

            if dados_horarios:
                self.cursor.executemany(sql_horario, dados_horarios)

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao criar turma: {str(e)}")
    
    def get_by_id(self, turma_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma turma pelo ID.
        
        Args:
            turma_id: ID da turma.
            
        Returns:
            Dicionário com dados da turma, ou None se não encontrada.
        """
        sql_turma = """
            SELECT id, periodo, vagas, curso_codigo, local 
            FROM turma 
            WHERE id = ?
        """
        
        self.cursor.execute(sql_turma, (turma_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None
        
        # Buscar horários
        sql_horarios = """
            SELECT dia, intervalo 
            FROM horario_turma 
            WHERE turma_id = ?
            ORDER BY dia
        """
        self.cursor.execute(sql_horarios, (turma_id,))
        horarios_rows = self.cursor.fetchall()

        horarios_dict = {}
        for h in horarios_rows:
            horarios_dict[h['dia']] = h['intervalo']
        
        # Buscar matrículas (se necessário)
        # Poderíamos adicionar isso posteriormente
        
        return {
            "id": row["id"],
            "periodo": row["periodo"],
            "vagas": row["vagas"],
            "curso_codigo": row["curso_codigo"],
            "local": row["local"],
            "horarios": horarios_dict
        }
    
    def list_all(self) -> List[Dict[str, Any]]:
        """
        Lista todas as turmas.
        
        Returns:
            Lista de dicionários com dados das turmas.
        """
        sql_turmas = """
            SELECT id, periodo, vagas, curso_codigo, local 
            FROM turma 
            ORDER BY periodo DESC, id
        """
        
        self.cursor.execute(sql_turmas)
        turmas_rows = self.cursor.fetchall()

        if not turmas_rows:
            return []

        # Buscar todos os horários de uma vez
        turma_ids = [row['id'] for row in turmas_rows]
        placeholders = ','.join(['?' for _ in turma_ids])
        
        sql_horarios = f"""
            SELECT turma_id, dia, intervalo 
            FROM horario_turma 
            WHERE turma_id IN ({placeholders})
            ORDER BY turma_id, dia
        """
        self.cursor.execute(sql_horarios, turma_ids)
        horarios_rows = self.cursor.fetchall()
        
        # Organizar horários por turma
        horarios_por_turma = {}
        for h_row in horarios_rows:
            turma_id = h_row['turma_id']
            if turma_id not in horarios_por_turma:
                horarios_por_turma[turma_id] = {}
            horarios_por_turma[turma_id][h_row['dia']] = h_row['intervalo']
        
        # Construir resultado
        turmas_completas = []
        for row in turmas_rows:
            turma_id = row['id']
            
            turma_dict = {
                "id": turma_id,
                "periodo": row["periodo"],
                "vagas": row["vagas"],
                "curso_codigo": row["curso_codigo"],
                "local": row["local"],
                "horarios": horarios_por_turma.get(turma_id, {})
            }
            turmas_completas.append(turma_dict)
        
        return turmas_completas
    
    def delete(self, turma_id: str) -> bool:
        """
        Deleta uma turma pelo ID.
        
        Args:
            turma_id: ID da turma.
            
        Returns:
            True se deletada, False caso contrário.
        """
        try:
            # Primeiro deletar horários
            sql_horarios = "DELETE FROM horario_turma WHERE turma_id = ?"
            self.cursor.execute(sql_horarios, (turma_id,))

            # Depois deletar a turma
            sql_turma = "DELETE FROM turma WHERE id = ?"
            self.cursor.execute(sql_turma, (turma_id,))
            
            self.conn.commit()
            
            # Verificar se alguma linha foi afetada
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao deletar turma: {str(e)}")
    
    def update(self, turma_id: str, dados: Dict[str, Any]) -> bool:
        """
        Atualiza parcialmente uma turma.
        
        Args:
            turma_id: ID da turma.
            dados: Dicionário com campos a atualizar.
            
        Returns:
            True se atualizada, False caso contrário.
        """
        if not dados:
            return False
        
        try:
            alterado = False
            
            # Atualizar dados básicos da turma
            campos_turma = []
            valores_turma = []
            
            campos_validos_turma = ['periodo', 'vagas', 'local']
            for campo, valor in dados.items():
                if campo in campos_validos_turma:
                    campos_turma.append(f"{campo} = ?")
                    valores_turma.append(valor)
            
            if campos_turma:
                sql_turma = f"""
                    UPDATE turma
                    SET {", ".join(campos_turma)}
                    WHERE id = ?
                """
                valores_turma.append(turma_id)
                self.cursor.execute(sql_turma, tuple(valores_turma))
                alterado = True
            
            # Atualizar horários se fornecidos
            if "horarios" in dados:
                novos_horarios = dados["horarios"]
                
                # Buscar horários existentes
                sql_existentes = """
                    SELECT dia, intervalo 
                    FROM horario_turma 
                    WHERE turma_id = ?
                """
                self.cursor.execute(sql_existentes, (turma_id,))
                existentes_rows = self.cursor.fetchall()
                existentes = {h["dia"]: h["intervalo"] for h in existentes_rows}
                
                # Atualizar ou adicionar novos horários
                for dia, intervalo in novos_horarios.items():
                    if dia in existentes:
                        if existentes[dia] != intervalo:
                            sql_atualizar = """
                                UPDATE horario_turma
                                SET intervalo = ?
                                WHERE turma_id = ? AND dia = ?
                            """
                            self.cursor.execute(sql_atualizar, (intervalo, turma_id, dia))
                            alterado = True
                    else:
                        sql_inserir = """
                            INSERT INTO horario_turma (dia, intervalo, turma_id)
                            VALUES (?, ?, ?)
                        """
                        self.cursor.execute(sql_inserir, (dia, intervalo, turma_id))
                        alterado = True
                
                # Remover horários que não estão mais na lista
                dias_novos = set(novos_horarios.keys())
                dias_existentes = set(existentes.keys())
                dias_para_remover = dias_existentes - dias_novos
                
                for dia in dias_para_remover:
                    sql_remover = """
                        DELETE FROM horario_turma
                        WHERE turma_id = ? AND dia = ?
                    """
                    self.cursor.execute(sql_remover, (turma_id, dia))
                    alterado = True
            
            self.conn.commit()
            
            if alterado:
                self.cursor.execute("SELECT changes();")
                alterados = self.cursor.fetchone()[0]
                return alterados > 0
            
            return False
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar turma: {str(e)}")
    
    def buscar_por_periodo(self, periodo: str) -> List[Dict[str, Any]]:
        """
        Busca turmas por período.
        
        Args:
            periodo: Período letivo.
            
        Returns:
            Lista de turmas do período.
        """
        sql = """
            SELECT id, periodo, vagas, curso_codigo, local 
            FROM turma 
            WHERE periodo = ?
            ORDER BY id
        """
        
        self.cursor.execute(sql, (periodo,))
        rows = self.cursor.fetchall()
        
        if not rows:
            return []
        
        # Buscar horários para essas turmas
        turma_ids = [row['id'] for row in rows]
        return self._adicionar_horarios_as_turmas(rows, turma_ids)
    
    def buscar_por_curso(self, curso_codigo: str) -> List[Dict[str, Any]]:
        """
        Busca turmas por curso.
        
        Args:
            curso_codigo: Código do curso.
            
        Returns:
            Lista de turmas do curso.
        """
        sql = """
            SELECT id, periodo, vagas, curso_codigo, local 
            FROM turma 
            WHERE curso_codigo = ?
            ORDER BY periodo DESC, id
        """
        
        self.cursor.execute(sql, (curso_codigo,))
        rows = self.cursor.fetchall()
        
        if not rows:
            return []
        
        # Buscar horários para essas turmas
        turma_ids = [row['id'] for row in rows]
        return self._adicionar_horarios_as_turmas(rows, turma_ids)
    
    def _adicionar_horarios_as_turmas(self, turmas_rows: List, turma_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Adiciona horários às turmas.
        
        Args:
            turmas_rows: Lista de linhas de turmas.
            turma_ids: Lista de IDs das turmas.
            
        Returns:
            Lista de turmas com horários.
        """
        if not turma_ids:
            return []
        
        placeholders = ','.join(['?' for _ in turma_ids])
        sql_horarios = f"""
            SELECT turma_id, dia, intervalo 
            FROM horario_turma 
            WHERE turma_id IN ({placeholders})
            ORDER BY turma_id, dia
        """
        self.cursor.execute(sql_horarios, turma_ids)
        horarios_rows = self.cursor.fetchall()
        
        # Organizar horários por turma
        horarios_por_turma = {}
        for h_row in horarios_rows:
            turma_id = h_row['turma_id']
            if turma_id not in horarios_por_turma:
                horarios_por_turma[turma_id] = {}
            horarios_por_turma[turma_id][h_row['dia']] = h_row['intervalo']
        
        # Construir resultado
        turmas_completas = []
        for row in turmas_rows:
            turma_id = row['id']
            turma_dict = {
                "id": turma_id,
                "periodo": row["periodo"],
                "vagas": row["vagas"],
                "curso_codigo": row["curso_codigo"],
                "local": row["local"],
                "horarios": horarios_por_turma.get(turma_id, {})
            }
            turmas_completas.append(turma_dict)
        
        return turmas_completas