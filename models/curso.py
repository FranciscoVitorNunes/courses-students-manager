class Curso:
    """
    Representa um curso acadêmico com informações de código, nome,
    carga horária, ementa e pré-requisitos.
    """

    def __init__(self, codigo: str, nome: str, carga_horaria: int, ementa: str = ""):
        """
        Inicializa um curso.
        
        Args:
            codigo (str): Código único do curso.
            nome (str): Nome do curso.
            carga_horaria (int): Carga horária total.
            ementa (str): Ementa do curso (opcional).
        
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
        self._prerequisitos = []

    @property
    def codigo(self):
        """Retorna o código do curso."""
        return self._codigo

    @property
    def nome(self):
        """Retorna o nome do curso."""
        return self._nome
    
    @nome.setter
    def nome(self, n_nome):
        self._nome = n_nome

    @property
    def carga_horaria(self):
        """Retorna a carga horária do curso."""
        return self._carga_horaria
    
    @carga_horaria.setter
    def carga_horaria(self, n_carga_horaria):
        self._carga_horaria = n_carga_horaria

    @property
    def ementa(self):
        """Retorna a ementa do curso."""
        return self._ementa

    @ementa.setter
    def ementa(self, n_ementa):
        self._ementa = n_ementa

    @property
    def prerequisitos(self):
        """Retorna uma lista dos códigos dos cursos pré-requisitos."""
        return self._prerequisitos.copy()

    def adicionar_prerequisito(self, codigo_curso: str):
        """
        Adiciona um curso como pré-requisito.
        
        Args:
            codigo_curso (str): Código do curso pré-requisito.
        
        Raises:
            ValueError: Se o código for inválido ou redundante.
        """
        if not codigo_curso or not codigo_curso.strip():
            raise ValueError("Código do pré-requisito não pode ser vazio.")
        if codigo_curso == self._codigo:
            raise ValueError("Um curso não pode ser pré-requisito de si próprio.")
        if codigo_curso in self._prerequisitos:
            raise ValueError("Pré-requisito já foi adicionado.")
        self._prerequisitos.append(codigo_curso)

    def validar_prerequisitos(self, cursos_concluidos: list[str]) -> bool:
        """
        Verifica se o aluno concluiu todos os pré-requisitos.
        
        Args:
            cursos_concluidos (list[str]): Lista com códigos dos cursos concluídos pelo aluno.
        
        Returns:
            bool: True se todos os pré-requisitos forem atendidos.
        """
        return all(curso in cursos_concluidos for curso in self._prerequisitos)

    def __str__(self):
        """Representação amigável do curso."""
        return f"{self.codigo} — {self.nome}"

    def __repr__(self):
        """Representação técnica do curso."""
        return f"Curso(codigo='{self.codigo}', nome='{self.nome}')"
