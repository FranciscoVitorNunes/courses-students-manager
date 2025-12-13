# repositories/curso_repository.py
from database.connection import SQLiteConnection
from models.curso import Curso
from schemas.curso_schema import CursoSchema
from typing import Optional, List, Dict, Any


class CursoRepository:
    def __init__(self):
        self.conn, self.cursor = SQLiteConnection.get_connection()
    
    def create(self, curso: CursoSchema) -> bool:
        """
        Cria um novo curso no banco de dados.
        
        Args:
            curso: Dados do curso.
            
        Returns:
            True se criado com sucesso.
            
        Raises:
            ValueError: Se ocorrer erro ao salvar.
        """
        sql = """
            INSERT INTO curso(codigo, nome, carga_horaria, ementa) 
            VALUES (?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(sql, (
                curso.codigo, 
                curso.nome, 
                curso.carga_horaria, 
                curso.ementa if hasattr(curso, 'ementa') and curso.ementa else ""
            ))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao criar curso: {str(e)}")
    
    def get_by_codigo(self, codigo_curso: str) -> Optional[CursoSchema]:
        """
        Busca um curso pelo código.
        
        Args:
            codigo_curso: Código do curso.
            
        Returns:
            CursoSchema se encontrado, None caso contrário.
        """
        sql = """
            SELECT codigo, nome, carga_horaria, ementa 
            FROM curso 
            WHERE codigo = ?;
        """
        
        self.cursor.execute(sql, (codigo_curso,))
        row = self.cursor.fetchone()
        
        if row is None:
            return None
        
        return CursoSchema(
            codigo=row['codigo'],
            nome=row['nome'],
            carga_horaria=row['carga_horaria'],
            ementa=row['ementa'] if row['ementa'] else ""
        )
    
    def list_all(self) -> List[CursoSchema]:
        """
        Lista todos os cursos.
        
        Returns:
            Lista de CursoSchema.
        """
        sql = """
            SELECT codigo, nome, carga_horaria, ementa FROM curso 
            ORDER BY nome;
        """
        
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        
        return [
            CursoSchema(
                codigo=row['codigo'],
                nome=row['nome'],
                carga_horaria=row['carga_horaria'],
                ementa=row['ementa'] if row['ementa'] else ""
            ) for row in rows
        ]
    
    def delete(self, codigo_curso: str) -> bool:
        """
        Deleta um curso pelo código.
        
        Args:
            codigo_curso: Código do curso.
            
        Returns:
            True se deletado, False caso contrário.
        """
        sql = """
            DELETE FROM curso WHERE codigo = ?;
        """
        
        try:
            # Primeiro, deletar pré-requisitos associados
            sql_delete_prereqs = """
                DELETE FROM curso_prerequisito 
                WHERE curso_codigo = ? OR prerequisito_codigo = ?
            """
            self.cursor.execute(sql_delete_prereqs, (codigo_curso, codigo_curso))
            
            # Agora deletar o curso
            self.cursor.execute(sql, (codigo_curso,))
            self.conn.commit()
            
            # Verificar se alguma linha foi afetada
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao deletar curso: {str(e)}")
    
    def update(self, codigo: str, dados: dict) -> bool:
        """
        Atualiza parcialmente um curso.
        
        Args:
            codigo: Código do curso.
            dados: Dicionário com campos a atualizar.
            
        Returns:
            True se atualizado, False caso contrário.
        """
        if not dados:
            return False
        
        campos = []
        valores = []
        
        for campo, valor in dados.items():
            if campo in ['nome', 'carga_horaria', 'ementa']:
                campos.append(f"{campo} = ?")
                valores.append(valor)
        
        if not campos:
            return False
        
        sql = f"""
            UPDATE curso
            SET {", ".join(campos)}
            WHERE codigo = ?;
        """
        valores.append(codigo)
        
        try:
            self.cursor.execute(sql, tuple(valores))
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar curso: {str(e)}")
    
    def create_prerequisitos(self, codigo_curso: str, prerequisito_curso: str) -> bool:
        """
        Adiciona um pré-requisito a um curso.
        
        Args:
            codigo_curso: Código do curso.
            prerequisito_curso: Código do curso pré-requisito.
            
        Returns:
            True se adicionado com sucesso.
            
        Raises:
            ValueError: Se ocorrer erro ao salvar.
        """
        sql = """
            INSERT INTO curso_prerequisito(curso_codigo, prerequisito_codigo) 
            VALUES (?, ?)
        """
        
        try:
            self.cursor.execute(sql, (codigo_curso, prerequisito_curso))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao adicionar pré-requisito: {str(e)}")
    
    def get_prerequisitos(self, codigo_curso: str) -> List[str]:
        """
        Obtém a lista de pré-requisitos de um curso.
        
        Args:
            codigo_curso: Código do curso.
            
        Returns:
            Lista de códigos de pré-requisitos.
        """
        sql = """
            SELECT prerequisito_codigo 
            FROM curso_prerequisito 
            WHERE curso_codigo = ?
            ORDER BY prerequisito_codigo
        """
        
        self.cursor.execute(sql, (codigo_curso,))
        rows = self.cursor.fetchall()
        
        return [row['prerequisito_codigo'] for row in rows]
    
    def remover_prerequisito(self, codigo_curso: str, prerequisito_curso: str) -> bool:
        """
        Remove um pré-requisito de um curso.
        
        Args:
            codigo_curso: Código do curso.
            prerequisito_curso: Código do pré-requisito a remover.
            
        Returns:
            True se removido, False caso contrário.
        """
        sql = """
            DELETE FROM curso_prerequisito 
            WHERE curso_codigo = ? AND prerequisito_codigo = ?
        """
        
        try:
            self.cursor.execute(sql, (codigo_curso, prerequisito_curso))
            self.conn.commit()
            
            self.cursor.execute("SELECT changes();")
            alterados = self.cursor.fetchone()[0]
            
            return alterados > 0
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao remover pré-requisito: {str(e)}")
    
    def get_cursos_que_tem_como_prerequisito(self, prerequisito_codigo: str) -> List[str]:
        """
        Obtém lista de cursos que têm um determinado curso como pré-requisito.
        
        Args:
            prerequisito_codigo: Código do curso pré-requisito.
            
        Returns:
            Lista de códigos de cursos que dependem deste.
        """
        sql = """
            SELECT curso_codigo 
            FROM curso_prerequisito 
            WHERE prerequisito_codigo = ?
        """
        
        self.cursor.execute(sql, (prerequisito_codigo,))
        rows = self.cursor.fetchall()
        
        return [row['curso_codigo'] for row in rows]
    
    def verificar_ciclo_prerequisitos(self, curso_codigo: str, prerequisito_codigo: str) -> bool:
        """
        Verifica se adicionar um pré-requisito criaria um ciclo.
        
        Args:
            curso_codigo: Código do curso que receberá o pré-requisito.
            prerequisito_codigo: Código do novo pré-requisito.
            
        Returns:
            True se houver ciclo, False caso contrário.
        """
        visitados = set()
        
        def dfs(codigo_atual: str) -> bool:
            """Busca em profundidade para detectar ciclos."""
            if codigo_atual == curso_codigo:
                return True
            
            if codigo_atual in visitados:
                return False
            
            visitados.add(codigo_atual)
            
            # Obter cursos que têm o curso atual como pré-requisito
            dependentes = self.get_cursos_que_tem_como_prerequisito(codigo_atual)
            
            for dependente in dependentes:
                if dfs(dependente):
                    return True
            
            return False
        
        # Começar a busca a partir do novo pré-requisito
        return dfs(prerequisito_codigo)
    
    def buscar_por_nome(self, nome: str) -> List[CursoSchema]:
        """
        Busca cursos pelo nome (busca parcial).
        
        Args:
            nome: Parte do nome do curso.
            
        Returns:
            Lista de cursos encontrados.
        """
        sql = """
            SELECT codigo, nome, carga_horaria, ementa 
            FROM curso 
            WHERE LOWER(nome) LIKE ? 
            ORDER BY nome
        """
        
        self.cursor.execute(sql, (f"%{nome.lower()}%",))
        rows = self.cursor.fetchall()
        
        return [
            CursoSchema(
                codigo=row['codigo'],
                nome=row['nome'],
                carga_horaria=row['carga_horaria'],
                ementa=row['ementa'] if row['ementa'] else ""
            ) for row in rows
        ]