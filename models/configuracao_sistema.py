class ConfiguracaoSistema:
    """
    Armazena os parâmetros institucionais que regem as regras acadêmicas.
    Essa configuração deve ser utilizada por serviços como RegraAprovacao,
    matrícula e geração de relatórios.
    """

    def __init__(self, nota_minima: float = 6.0, frequencia_minima: float = 75.0,
                 limite_trancamentos: int = 1, max_turmas_por_aluno: int = 6,
                 top_n_alunos: int = 3):
        """
        Inicializa os parâmetros de configuração do sistema.

        Args:
            nota_minima (float): Nota mínima para aprovação.
            frequencia_minima (float): Frequência mínima em porcentagem.
            limite_trancamentos (int): Quantidade máxima de trancamentos permitidos por aluno.
            max_turmas_por_aluno (int): Máximo de matrículas simultâneas por período.
            top_n_alunos (int): Quantidade de alunos exibidos no ranking.

        Raises:
            ValueError: Se algum parâmetro estiver fora dos limites esperados.
        """
        if not 0 <= nota_minima <= 10:
            raise ValueError("A nota mínima deve estar entre 0 e 10.")
        if not 0 <= frequencia_minima <= 100:
            raise ValueError("A frequência mínima deve estar entre 0 e 100.")
        if limite_trancamentos < 0:
            raise ValueError("O limite de trancamentos não pode ser negativo.")
        if max_turmas_por_aluno <= 0:
            raise ValueError("O máximo de turmas por aluno deve ser maior que zero.")
        if top_n_alunos <= 0:
            raise ValueError("O valor de top N alunos deve ser maior que zero.")

        self._nota_minima = nota_minima
        self._frequencia_minima = frequencia_minima
        self._limite_trancamentos = limite_trancamentos
        self._max_turmas_por_aluno = max_turmas_por_aluno
        self._top_n_alunos = top_n_alunos

    @property
    def nota_minima(self):
        """Retorna a nota mínima para aprovação."""
        return self._nota_minima

    @property
    def frequencia_minima(self):
        """Retorna a frequência mínima para aprovação."""
        return self._frequencia_minima

    @property
    def limite_trancamentos(self):
        """Retorna o limite de trancamentos permitidos por aluno."""
        return self._limite_trancamentos

    @property
    def max_turmas_por_aluno(self):
        """Retorna o número máximo de turmas simultâneas por aluno por período."""
        return self._max_turmas_por_aluno

    @property
    def top_n_alunos(self):
        """Retorna o número N de alunos que devem aparecer no ranking."""
        return self._top_n_alunos

    def alterar_parametros(self, **kwargs):
        """
        Altera um ou mais parâmetros do sistema. Apenas parâmetros reconhecidos
        serão modificados, e todos passam pelas mesmas validações do construtor.

        """
        for chave, valor in kwargs.items():
            if chave == "nota_minima":
                if not 0 <= valor <= 10:
                    raise ValueError("A nota mínima deve estar entre 0 e 10.")
                self._nota_minima = valor
            elif chave == "frequencia_minima":
                if not 0 <= valor <= 100:
                    raise ValueError("A frequência mínima deve estar entre 0 e 100.")
                self._frequencia_minima = valor
            elif chave == "limite_trancamentos":
                if valor < 0:
                    raise ValueError("O limite de trancamentos não pode ser negativo.")
                self._limite_trancamentos = valor
            elif chave == "max_turmas_por_aluno":
                if valor <= 0:
                    raise ValueError("O máximo de turmas por aluno deve ser maior que zero.")
                self._max_turmas_por_aluno = valor
            elif chave == "top_n_alunos":
                if valor <= 0:
                    raise ValueError("O valor de top N alunos deve ser maior que zero.")
                self._top_n_alunos = valor

    def __str__(self):
        return (
            f"Configuração: nota_min={self.nota_minima}, freq_min={self.frequencia_minima}, "
            f"limite_tranc={self.limite_trancamentos}, max_turmas={self.max_turmas_por_aluno}, "
            f"top_n={self.top_n_alunos}"
        )

    def __repr__(self):
        return (
            f"ConfiguracaoSistema(nota_minima={self.nota_minima}, frequencia_minima={self.frequencia_minima}, "
            f"limite_trancamentos={self.limite_trancamentos}, max_turmas_por_aluno={self.max_turmas_por_aluno}, "
            f"top_n_alunos={self.top_n_alunos})"
        )
