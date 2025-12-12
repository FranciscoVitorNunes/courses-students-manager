# repositories/aluno_repository.py
from database.connection import SQLiteConnection
from schemas.aluno_schema import AlunoSchema
from typing import Optional, List


class AlunoRepository:
    def __init__(self):
        self.conn, self.cursor = SQLiteConnection.get_connection()
    
    def salvar(self, aluno: AlunoSchema) -> bool:
        """
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
        
        return AlunoSchema(
            matricula=row['matricula'],
            nome=row['nome'],
            email=row['email'],
            cr=row['cr']
        )
    
    def listar(self) -> List[AlunoSchema]:
        """
        Returns:
            Lista de AlunoSchema.
        """
        sql = """
            SELECT matricula, nome, email, cr FROM aluno;
        """
        
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        
        return [
            AlunoSchema(
                matricula=row['matricula'],
                nome=row['nome'],
                email=row['email'],
                cr=row['cr']
            ) for row in rows
        ]
    
    def deletar(self, matricula: str) -> bool:
        """
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