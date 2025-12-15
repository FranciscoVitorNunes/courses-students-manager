from database.connection import SQLiteConnection
from typing import Optional, List, Dict, Any
from datetime import datetime


class MatriculaRepository:
    def __init__(self):
        self.conn, self.cursor = SQLiteConnection.get_connection()
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retorna todas as matrículas.
        
        Returns:
            Lista de dicionários com matrículas.
        """
        sql = """
            SELECT 
                m.id,
                m.aluno_matricula,
                m.turma_id,
                m.situacao,
                m.data_matricula,
                a.nome as aluno_nome,
                t.periodo as turma_periodo,
                t.vagas as turma_vagas,
                c.codigo as curso_codigo,
                c.nome as curso_nome,
                c.carga_horaria as curso_carga
            FROM matricula m
            JOIN aluno a ON m.aluno_matricula = a.matricula
            JOIN turma t ON m.turma_id = t.id
            JOIN curso c ON t.curso_codigo = c.codigo
            ORDER BY m.data_matricula DESC
        """
        
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Busca uma matrícula pelo ID.
        
        Args:
            id: ID da matrícula.
            
        Returns:
            Dicionário com dados da matrícula, ou None se não encontrada.
        """
        sql = """
            SELECT 
                m.id,
                m.aluno_matricula,
                m.turma_id,
                m.situacao,
                m.data_matricula,
                a.nome as aluno_nome,
                t.periodo as turma_periodo,
                t.vagas as turma_vagas,
                c.codigo as curso_codigo,
                c.nome as curso_nome,
                c.carga_horaria as curso_carga
            FROM matricula m
            JOIN aluno a ON m.aluno_matricula = a.matricula
            JOIN turma t ON m.turma_id = t.id
            JOIN curso c ON t.curso_codigo = c.codigo
            WHERE m.id = ?
        """
        
        self.cursor.execute(sql, (id,))
        row = self.cursor.fetchone()
        
        if not row:
            return None
        
        return dict(row)
    
    def create(self, dados: Dict[str, Any]) -> int:
        """
        Cria uma nova matrícula.
        
        Args:
            dados: Dicionário com dados da matrícula.
            
        Returns:
            ID da matrícula criada.
            
        Raises:
            ValueError: Se ocorrer erro ao salvar.
        """
        sql = """
            INSERT INTO matricula (aluno_matricula, turma_id, situacao, data_matricula)
            VALUES (?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(sql, (
                dados["aluno_matricula"],
                dados["turma_id"],
                dados.get("situacao", "CURSANDO"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao criar matrícula: {str(e)}")
    
    def delete(self, id: int) -> bool:
        """
        Deleta uma matrícula pelo ID.
        
        Args:
            id: ID da matrícula.
            
        Returns:
            True se deletada, False caso contrário.
        """
        sql = "DELETE FROM matricula WHERE id = ?"
        
        try:
            self.cursor.execute(sql, (id,))
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao deletar matrícula: {str(e)}")
    
    def update(self, id: int, dados: Dict[str, Any]) -> bool:
        """
        Atualiza uma matrícula.
        
        Args:
            id: ID da matrícula.
            dados: Dicionário com campos a atualizar.
            
        Returns:
            True se atualizada, False caso contrário.
        """
        if not dados:
            return False
        
        campos = []
        valores = []
        
        campos_validos = ['situacao', 'nota', 'frequencia']
        
        for campo, valor in dados.items():
            if campo in campos_validos:
                campos.append(f"{campo} = ?")
                valores.append(valor)
        
        if not campos:
            return False
        
        sql = f"""
            UPDATE matricula
            SET {", ".join(campos)}
            WHERE id = ?
        """
        valores.append(id)
        
        try:
            self.cursor.execute(sql, tuple(valores))
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar matrícula: {str(e)}")
    
    def buscar_por_aluno_e_turma(self, aluno_matricula: str, turma_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca matrícula por aluno e turma.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            turma_id: ID da turma.
            
        Returns:
            Dicionário com matrícula se encontrada, None caso contrário.
        """
        sql = """
            SELECT * FROM matricula 
            WHERE aluno_matricula = ? AND turma_id = ?
            LIMIT 1
        """
        
        self.cursor.execute(sql, (aluno_matricula, turma_id))
        row = self.cursor.fetchone()
        
        return dict(row) if row else None
    
    def existe_matricula(self, aluno_matricula: str, turma_id: str) -> bool:
        """
        Verifica se já existe matrícula para aluno e turma.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            turma_id: ID da turma.
            
        Returns:
            True se existe, False caso contrário.
        """
        return self.buscar_por_aluno_e_turma(aluno_matricula, turma_id) is not None
    
    def count_matriculas_por_turma(self, turma_id: str) -> int:
        """
        Conta matrículas ativas em uma turma.
        
        Args:
            turma_id: ID da turma.
            
        Returns:
            Número de matrículas ativas.
        """
        sql = """
            SELECT COUNT(*) FROM matricula 
            WHERE turma_id = ? AND situacao IN ('CURSANDO', 'APROVADO', 'REPROVADO_POR_NOTA', 'REPROVADO_POR_FREQUENCIA')
        """
        
        self.cursor.execute(sql, (turma_id,))
        return self.cursor.fetchone()[0]
    
    def count_matriculas_por_aluno(self, aluno_matricula: str, periodo: Optional[str] = None) -> int:
        """
        Conta matrículas ativas de um aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            periodo: Período específico (opcional).
            
        Returns:
            Número de matrículas ativas do aluno.
        """
        if periodo:
            sql = """
                SELECT COUNT(*) FROM matricula m
                JOIN turma t ON m.turma_id = t.id
                WHERE m.aluno_matricula = ? 
                AND t.periodo = ?
                AND m.situacao IN ('CURSANDO', 'APROVADO', 'REPROVADO_POR_NOTA', 'REPROVADO_POR_FREQUENCIA')
            """
            self.cursor.execute(sql, (aluno_matricula, periodo))
        else:
            sql = """
                SELECT COUNT(*) FROM matricula 
                WHERE aluno_matricula = ? 
                AND situacao IN ('CURSANDO', 'APROVADO', 'REPROVADO_POR_NOTA', 'REPROVADO_POR_FREQUENCIA')
            """
            self.cursor.execute(sql, (aluno_matricula,))
        
        return self.cursor.fetchone()[0]
    
    def listar_matriculas_por_aluno(self, aluno_matricula: str) -> List[Dict[str, Any]]:
        """
        Lista todas as matrículas de um aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            
        Returns:
            Lista de matrículas do aluno.
        """
        sql = """
            SELECT 
                m.id,
                m.aluno_matricula,
                m.turma_id,
                m.situacao,
                m.data_matricula,
                t.periodo,
                t.vagas,
                c.codigo as curso_codigo,
                c.nome as curso_nome
            FROM matricula m
            JOIN turma t ON m.turma_id = t.id
            JOIN curso c ON t.curso_codigo = c.codigo
            WHERE m.aluno_matricula = ?
            ORDER BY t.periodo DESC, m.data_matricula DESC
        """
        
        self.cursor.execute(sql, (aluno_matricula,))
        rows = self.cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def listar_matriculas_por_turma(self, turma_id: str) -> List[Dict[str, Any]]:
        """
        Lista todas as matrículas de uma turma.
        
        Args:
            turma_id: ID da turma.
            
        Returns:
            Lista de matrículas da turma.
        """
        sql = """
            SELECT 
                m.id,
                m.aluno_matricula,
                m.turma_id,
                m.situacao,
                m.data_matricula,
                a.nome as aluno_nome,
                a.email as aluno_email
            FROM matricula m
            JOIN aluno a ON m.aluno_matricula = a.matricula
            WHERE m.turma_id = ?
            ORDER BY a.nome
        """
        
        self.cursor.execute(sql, (turma_id,))
        rows = self.cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def listar_turmas_por_aluno(self, aluno_matricula: str) -> List[str]:
        """
        Lista IDs das turmas de um aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            
        Returns:
            Lista de IDs das turmas.
        """
        sql = """
            SELECT turma_id FROM matricula 
            WHERE aluno_matricula = ? 
            AND situacao IN ('CURSANDO', 'APROVADO', 'REPROVADO_POR_NOTA', 'REPROVADO_POR_FREQUENCIA')
        """
        
        self.cursor.execute(sql, (aluno_matricula,))
        rows = self.cursor.fetchall()
        
        return [row['turma_id'] for row in rows]
    
    def get_horarios_do_aluno(self, aluno_matricula: str, periodo: str) -> Dict[str, List[str]]:
        """
        Obtém horários de todas as turmas do aluno em um período.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            periodo: Período letivo.
            
        Returns:
            Dicionário com horários por dia.
        """
        sql = """
            SELECT ht.dia, ht.intervalo
            FROM matricula m
            JOIN turma t ON m.turma_id = t.id
            JOIN horario_turma ht ON t.id = ht.turma_id
            WHERE m.aluno_matricula = ? 
            AND t.periodo = ?
            AND m.situacao IN ('CURSANDO', 'APROVADO', 'REPROVADO_POR_NOTA', 'REPROVADO_POR_FREQUENCIA')
        """
        
        self.cursor.execute(sql, (aluno_matricula, periodo))
        rows = self.cursor.fetchall()
        
        horarios = {}
        for row in rows:
            dia = row['dia']
            intervalo = row['intervalo']
            if dia not in horarios:
                horarios[dia] = []
            horarios[dia].append(intervalo)
        
        return horarios
    
    def atualizar_nota_frequencia(self, matricula_id: int, nota: float, frequencia: float) -> bool:
        """
        Atualiza nota e frequência de uma matrícula.
        
        Args:
            matricula_id: ID da matrícula.
            nota: Nota do aluno.
            frequencia: Frequência do aluno.
            
        Returns:
            True se atualizado, False caso contrário.
        """
        # Primeiro, atualizar nota e frequência
        update_sql = """
            UPDATE matricula
            SET nota = ?, frequencia = ?
            WHERE id = ?
        """
        
        try:
            self.cursor.execute(update_sql, (nota, frequencia, matricula_id))
            
            # Atualizar situação baseada nas regras
            from config.settings import Settings
            settings = Settings()
            
            if frequencia < settings.frequencia_minima:
                situacao = 'REPROVADO_POR_FREQUENCIA'
            elif nota < settings.nota_minima_aprovacao:
                situacao = 'REPROVADO_POR_NOTA'
            else:
                situacao = 'APROVADO'
            
            # Atualizar situação
            self.cursor.execute(
                "UPDATE matricula SET situacao = ? WHERE id = ?",
                (situacao, matricula_id)
            )
            
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar nota/frequência: {str(e)}")