# repositories/aluno_repository.py
from database.connection import SQLiteConnection
from schemas.aluno_schema import AlunoSchema
from typing import Optional, List, Dict, Any


class AlunoRepository:
    def __init__(self):
        self.conn, self.cursor = SQLiteConnection.get_connection()
    
    def salvar(self, aluno: AlunoSchema) -> bool:
        """
        Salva um novo aluno no banco de dados.
        
        Args:
            aluno: Dados do aluno.
            
        Returns:
            True se salvo com sucesso.
        """
        sql = """
            INSERT INTO aluno(matricula, nome, email, cr) 
            VALUES (?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(sql, (
                aluno.matricula, 
                aluno.nome, 
                aluno.email, 
                aluno.cr or 0.0
            ))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao salvar aluno: {str(e)}")
    
    def buscar_por_matricula(self, matricula: str) -> Optional[AlunoSchema]:
        """
        Busca um aluno pela matrícula.
        
        Args:
            matricula: Matrícula do aluno.
            
        Returns:
            AlunoSchema se encontrado, None caso contrário.
        """
        sql = """
            SELECT matricula, nome, email, cr FROM aluno 
            WHERE matricula = ?;
        """
        
        self.cursor.execute(sql, (matricula,))
        row = self.cursor.fetchone()
        
        if row is None:
            return None
        
        # Buscar histórico do aluno
        historico = self.buscar_historico_aluno(matricula)
        
        return AlunoSchema(
            matricula=row['matricula'],
            nome=row['nome'],
            email=row['email'],
            cr=row['cr'],
            historico=historico
        )
    
    def listar(self) -> List[AlunoSchema]:
        """
        Lista todos os alunos.
        
        Returns:
            Lista de AlunoSchema.
        """
        sql = """
            SELECT matricula, nome, email, cr FROM aluno;
        """
        
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        
        alunos = []
        for row in rows:
            # Buscar histórico para cada aluno
            historico = self.buscar_historico_aluno(row['matricula'])
            
            alunos.append(AlunoSchema(
                matricula=row['matricula'],
                nome=row['nome'],
                email=row['email'],
                cr=row['cr'],
                historico=historico
            ))
        
        return alunos
    
    def deletar(self, matricula: str) -> bool:
        """
        Deleta um aluno pelo matrícula.
        
        Args:
            matricula: Matrícula do aluno.
            
        Returns:
            True se deletado, False caso contrário.
        """
        sql = """
            DELETE FROM aluno WHERE matricula = ?;
        """
        
        try:
            self.cursor.execute(sql, (matricula,))
            self.conn.commit()
            
            # Verificar se alguma linha foi afetada
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao deletar aluno: {str(e)}")
    
    def atualizar(self, matricula: str, dados: dict) -> bool:
        """
        Atualiza parcialmente um aluno.
        
        Args:
            matricula: Matrícula do aluno.
            dados: Dicionário com campos a atualizar.
            
        Returns:
            True se atualizado, False caso contrário.
        """
        if not dados:
            return False
        
        campos = []
        valores = []
        
        for campo, valor in dados.items():
            if campo in ['nome', 'email', 'cr']:
                campos.append(f"{campo} = ?")
                valores.append(valor)
        
        if not campos:
            return False
        
        sql = f"""
            UPDATE aluno
            SET {", ".join(campos)}
            WHERE matricula = ?;
        """
        valores.append(matricula)
        
        try:
            self.cursor.execute(sql, tuple(valores))
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar aluno: {str(e)}")
    
    def existe_matricula(self, matricula: str) -> bool:
        """
        Verifica se uma matrícula já existe.
        
        Args:
            matricula: Matrícula a verificar.
            
        Returns:
            True se existe, False caso contrário.
        """
        sql = """
            SELECT 1 FROM aluno WHERE matricula = ? LIMIT 1;
        """
        
        self.cursor.execute(sql, (matricula,))
        return self.cursor.fetchone() is not None
    
    # ========== MÉTODOS PARA HISTÓRICO ==========
    
    def adicionar_historico(self, aluno_matricula: str, registro: Dict[str, Any]) -> int:
        """
        Adiciona um registro ao histórico do aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            registro: Dicionário com dados do registro.
            
        Returns:
            ID do registro inserido.
        """
        sql = """
            INSERT INTO historico_aluno 
            (aluno_matricula, codigo_curso, nota, frequencia, carga_horaria, situacao, semestre)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(sql, (
                aluno_matricula,
                registro['codigo_curso'],
                registro['nota'],
                registro['frequencia'],
                registro['carga_horaria'],
                registro['situacao'],
                registro.get('semestre')
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao adicionar histórico: {str(e)}")
    
    def buscar_historico_aluno(self, aluno_matricula: str) -> List[Dict[str, Any]]:
        """
        Busca o histórico completo de um aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            
        Returns:
            Lista de registros históricos.
        """
        sql = """
            SELECT 
                id, codigo_curso, nota, frequencia, carga_horaria, 
                situacao, semestre, data_registro
            FROM historico_aluno 
            WHERE aluno_matricula = ?
            ORDER BY data_registro DESC, semestre DESC
        """
        
        self.cursor.execute(sql, (aluno_matricula,))
        rows = self.cursor.fetchall()
        
        historico = []
        for row in rows:
            historico.append({
                'id': row['id'],
                'codigo_curso': row['codigo_curso'],
                'nota': row['nota'],
                'frequencia': row['frequencia'],
                'carga_horaria': row['carga_horaria'],
                'situacao': row['situacao'],
                'semestre': row['semestre'],
                'data_registro': row['data_registro']
            })
        
        return historico
    
    def buscar_registro_historico(self, registro_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca um registro específico do histórico.
        
        Args:
            registro_id: ID do registro.
            
        Returns:
            Dicionário com dados do registro, ou None se não encontrado.
        """
        sql = """
            SELECT * FROM historico_aluno WHERE id = ?
        """
        
        self.cursor.execute(sql, (registro_id,))
        row = self.cursor.fetchone()
        
        if row is None:
            return None
        
        return dict(row)
    
    def atualizar_historico(self, registro_id: int, dados: Dict[str, Any]) -> bool:
        """
        Atualiza um registro do histórico.
        
        Args:
            registro_id: ID do registro.
            dados: Dicionário com campos a atualizar.
            
        Returns:
            True se atualizado, False caso contrário.
        """
        if not dados:
            return False
        
        campos = []
        valores = []
        
        campos_validos = ['nota', 'frequencia', 'situacao', 'semestre']
        
        for campo, valor in dados.items():
            if campo in campos_validos:
                campos.append(f"{campo} = ?")
                valores.append(valor)
        
        if not campos:
            return False
        
        sql = f"""
            UPDATE historico_aluno
            SET {", ".join(campos)}, data_registro = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        valores.append(registro_id)
        
        try:
            self.cursor.execute(sql, tuple(valores))
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar histórico: {str(e)}")
    
    def remover_historico(self, registro_id: int) -> bool:
        """
        Remove um registro do histórico.
        
        Args:
            registro_id: ID do registro.
            
        Returns:
            True se removido, False caso contrário.
        """
        sql = """
            DELETE FROM historico_aluno WHERE id = ?
        """
        
        try:
            self.cursor.execute(sql, (registro_id,))
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao remover histórico: {str(e)}")
    
    def remover_historico_por_curso(self, aluno_matricula: str, codigo_curso: str) -> bool:
        """
        Remove um curso específico do histórico do aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            codigo_curso: Código do curso.
            
        Returns:
            True se removido, False caso contrário.
        """
        sql = """
            DELETE FROM historico_aluno 
            WHERE aluno_matricula = ? AND codigo_curso = ?
        """
        
        try:
            self.cursor.execute(sql, (aluno_matricula, codigo_curso))
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao remover curso do histórico: {str(e)}")
    
    def verificar_curso_aprovado(self, aluno_matricula: str, codigo_curso: str) -> bool:
        """
        Verifica se o aluno foi aprovado em um curso específico.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            codigo_curso: Código do curso.
            
        Returns:
            True se aprovado, False caso contrário.
        """
        sql = """
            SELECT 1 FROM historico_aluno 
            WHERE aluno_matricula = ? 
            AND codigo_curso = ? 
            AND situacao = 'APROVADO'
            LIMIT 1
        """
        
        self.cursor.execute(sql, (aluno_matricula, codigo_curso))
        return self.cursor.fetchone() is not None
    
    def get_cursos_aprovados(self, aluno_matricula: str) -> List[str]:
        """
        Retorna lista de cursos aprovados pelo aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            
        Returns:
            Lista de códigos de cursos aprovados.
        """
        sql = """
            SELECT codigo_curso FROM historico_aluno 
            WHERE aluno_matricula = ? AND situacao = 'APROVADO'
        """
        
        self.cursor.execute(sql, (aluno_matricula,))
        rows = self.cursor.fetchall()
        
        return [row['codigo_curso'] for row in rows]
    
    def calcular_cr_aluno(self, aluno_matricula: str) -> float:
        """
        Calcula o CR do aluno diretamente do banco de dados.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            
        Returns:
            Valor do CR.
        """
        sql = """
            SELECT 
                SUM(nota * carga_horaria) as soma_ponderada,
                SUM(carga_horaria) as total_carga
            FROM historico_aluno 
            WHERE aluno_matricula = ? 
            AND situacao IN ('APROVADO', 'REPROVADO_POR_NOTA')
        """
        
        self.cursor.execute(sql, (aluno_matricula,))
        row = self.cursor.fetchone()
        
        if row and row['total_carga'] and row['total_carga'] > 0:
            cr = row['soma_ponderada'] / row['total_carga']
            return round(cr, 2)
        
        return 0.0
    
    def atualizar_cr_aluno(self, aluno_matricula: str) -> bool:
        """
        Atualiza o CR do aluno na tabela aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            
        Returns:
            True se atualizado, False caso contrário.
        """
        cr = self.calcular_cr_aluno(aluno_matricula)
        
        sql = """
            UPDATE aluno SET cr = ? WHERE matricula = ?
        """
        
        try:
            self.cursor.execute(sql, (cr, aluno_matricula))
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar CR do aluno: {str(e)}")