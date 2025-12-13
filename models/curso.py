# models/curso.py
from typing import List, Optional, Dict, Any


class Curso:
    """
    Representa um curso acadêmico com informações de código, nome,
    carga horária, ementa e pré-requisitos.
    """

    def __init__(self, codigo: str, nome: str, carga_horaria: int, 
                 ementa: str = "", prerequisitos: Optional[List[str]] = None):
        """
        Inicializa um curso.
        
        Args:
            codigo (str): Código único do curso.
            nome (str): Nome do curso.
            carga_horaria (int): Carga horária total.
            ementa (str): Ementa do curso (opcional).
            prerequisitos (List[str]): Lista de códigos de pré-requisitos (opcional).
        
        Raises:
            ValueError: Se os valores fornecidos forem inválidos.
        """
        if not codigo or not codigo.strip():
            raise ValueError("Código do curso não pode ser vazio.")
        if not nome or not nome.strip():
            raise ValueError("Nome do curso não pode ser vazio.")
        if not isinstance(carga_horaria, int) or carga_horaria <= 0:
            raise ValueError("Carga horária deve ser um inteiro maior que zero.")
        
        self._codigo = codigo.strip()
        self._nome = nome.strip()
        self._carga_horaria = carga_horaria
        self._ementa = ementa.strip()
        self._prerequisitos = prerequisitos if prerequisitos is not None else []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Curso':
        """
        Cria um curso a partir de um dicionário.
        
        Args:
            data: Dicionário com dados do curso.
        
        Returns:
            Instância de Curso.
        """
        return cls(
            codigo=data['codigo'],
            nome=data['nome'],
            carga_horaria=data['carga_horaria'],
            ementa=data.get('ementa', ''),
            prerequisitos=data.get('prerequisitos', [])
        )

    @property
    def codigo(self) -> str:
        """Retorna o código do curso (somente leitura)."""
        return self._codigo

    @property
    def nome(self) -> str:
        """Retorna o nome do curso."""
        return self._nome
    
    @nome.setter
    def nome(self, valor: str):
        """Define o nome do curso."""
        if not valor or not valor.strip():
            raise ValueError("Nome do curso não pode ser vazio.")
        self._nome = valor.strip()

    @property
    def carga_horaria(self) -> int:
        """Retorna a carga horária do curso."""
        return self._carga_horaria
    
    @carga_horaria.setter
    def carga_horaria(self, valor: int):
        """Define a carga horária do curso."""
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("Carga horária deve ser um inteiro maior que zero.")
        self._carga_horaria = valor

    @property
    def ementa(self) -> str:
        """Retorna a ementa do curso."""
        return self._ementa

    @ementa.setter
    def ementa(self, valor: str):
        """Define a ementa do curso."""
        self._ementa = valor.strip()

    @property
    def prerequisitos(self) -> List[str]:
        """Retorna uma cópia da lista de códigos dos cursos pré-requisitos."""
        return self._prerequisitos.copy()

    def adicionar_prerequisito(self, codigo_curso: str) -> bool:
        """
        Adiciona um curso como pré-requisito.
        
        Args:
            codigo_curso (str): Código do curso pré-requisito.
        
        Returns:
            bool: True se adicionado com sucesso.
        
        Raises:
            ValueError: Se o código for inválido ou redundante.
        """
        if not codigo_curso or not codigo_curso.strip():
            raise ValueError("Código do pré-requisito não pode ser vazio.")
        
        codigo_curso = codigo_curso.strip()
        
        if codigo_curso == self._codigo:
            raise ValueError("Um curso não pode ser pré-requisito de si próprio.")
        
        if codigo_curso in self._prerequisitos:
            raise ValueError("Pré-requisito já foi adicionado.")
        
        self._prerequisitos.append(codigo_curso)
        return True

    def remover_prerequisito(self, codigo_curso: str) -> bool:
        """
        Remove um curso dos pré-requisitos.
        
        Args:
            codigo_curso (str): Código do curso pré-requisito.
        
        Returns:
            bool: True se removido, False se não encontrado.
        """
        if codigo_curso in self._prerequisitos:
            self._prerequisitos.remove(codigo_curso)
            return True
        return False

    def carregar_prerequisitos(self, prerequisitos: List[str]) -> None:
        """
        Carrega uma lista completa de pré-requisitos.
        
        Args:
            prerequisitos: Lista de códigos de pré-requisitos.
        """
        self._prerequisitos = []
        for codigo in prerequisitos:
            self.adicionar_prerequisito(codigo)

    def validar_prerequisitos(self, cursos_concluidos: List[str]) -> bool:
        """
        Verifica se o aluno concluiu todos os pré-requisitos.
        
        Args:
            cursos_concluidos (list[str]): Lista com códigos dos cursos concluídos pelo aluno.
        
        Returns:
            bool: True se todos os pré-requisitos forem atendidos.
        """
        return all(curso in cursos_concluidos for curso in self._prerequisitos)

    def get_prerequisitos_faltantes(self, cursos_concluidos: List[str]) -> List[str]:
        """
        Retorna lista de pré-requisitos que ainda não foram concluídos.
        
        Args:
            cursos_concluidos: Lista de códigos de cursos concluídos.
        
        Returns:
            Lista de códigos de pré-requisitos faltantes.
        """
        return [curso for curso in self._prerequisitos if curso not in cursos_concluidos]

    def verificar_ciclo_prerequisitos(self, todos_cursos: Dict[str, 'Curso']) -> bool:
        """
        Verifica se há ciclos nos pré-requisitos.
        
        Args:
            todos_cursos: Dicionário com todos os cursos do sistema (código -> Curso).
        
        Returns:
            bool: True se há ciclo, False caso contrário.
        """
        visitados = set()
        
        def dfs(curso_codigo: str) -> bool:
            """Busca em profundidade para detectar ciclos."""
            if curso_codigo in visitados:
                return True  # Ciclo detectado
            
            visitados.add(curso_codigo)
            curso = todos_cursos.get(curso_codigo)
            
            if curso:
                for prereq in curso.prerequisitos:
                    if dfs(prereq):
                        return True
            
            visitados.remove(curso_codigo)
            return False
        
        return dfs(self._codigo)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o curso para um dicionário.
        
        Returns:
            Dicionário com os dados do curso.
        """
        return {
            'codigo': self.codigo,
            'nome': self.nome,
            'carga_horaria': self.carga_horaria,
            'ementa': self.ementa,
            'prerequisitos': self.prerequisitos
        }

    def to_dict_resumo(self) -> Dict[str, Any]:
        """
        Retorna um resumo do curso (sem pré-requisitos detalhados).
        
        Returns:
            Dicionário resumido do curso.
        """
        return {
            'codigo': self.codigo,
            'nome': self.nome,
            'carga_horaria': self.carga_horaria,
            'total_prerequisitos': len(self._prerequisitos)
        }

    def __eq__(self, outro: object) -> bool:
        """
        Compara dois cursos por código.
        
        Args:
            outro: Outro objeto para comparação.
        
        Returns:
            bool: True se os códigos são iguais.
        """
        if not isinstance(outro, Curso):
            return NotImplemented
        return self.codigo == outro.codigo

    def __str__(self) -> str:
        """Representação amigável do curso."""
        prereq_str = f", {len(self._prerequisitos)} pré-requisitos" if self._prerequisitos else ""
        return f"{self.codigo} — {self.nome} ({self.carga_horaria}h{prereq_str})"

    def __repr__(self) -> str:
        """Representação técnica do curso."""
        return f"Curso(codigo='{self.codigo}', nome='{self.nome}', carga_horaria={self.carga_horaria})"