class Matricula:
    """
    Representa a matrícula de um aluno em uma turma.
    Gerencia informações de nota, frequência, situação acadêmica,
    além do estado de matrícula (ativa, concluída ou trancada).
    """

    SITUACAO_CURSANDO = "CURSANDO"
    SITUACAO_APROVADO = "APROVADO"
    SITUACAO_REPROVADO_NOTA = "REPROVADO_POR_NOTA"
    SITUACAO_REPROVADO_FREQUENCIA = "REPROVADO_POR_FREQUENCIA"
    SITUACAO_TRANCADA = "TRANCADA"

    def __init__(self, aluno, turma):
        """
        Inicializa uma matrícula vinculando um aluno a uma turma.
        Ao ser criada, a matrícula já é registrada dentro da turma.

        Args:
            aluno (Aluno): Aluno que está se matriculando.
            turma (Turma): Turma na qual o aluno está sendo matriculado.

        Raises:
            ValueError: Se aluno ou turma forem inválidos.
        """
        if aluno is None or turma is None:
            raise ValueError("Aluno e Turma são obrigatórios.")
        self._aluno = aluno
        self._turma = turma
        self._nota = None
        self._frequencia = None
        self._situacao = self.SITUACAO_CURSANDO
        self._ativa = True
        turma.adicionar_matricula(self)

    @property
    def aluno(self):
        """Retorna o aluno associado à matrícula."""
        return self._aluno

    @property
    def turma(self):
        """Retorna a turma vinculada à matrícula."""
        return self._turma

    @property
    def nota(self):
        """Retorna a nota lançada na matrícula (None caso ainda indisponível)."""
        return self._nota

    @property
    def frequencia(self):
        """Retorna a frequência do aluno (None caso ainda não informada)."""
        return self._frequencia

    @property
    def situacao(self):
        """Retorna a situação acadêmica atual da matrícula."""
        return self._situacao

    @property
    def ativa(self):
        """Indica se a matrícula ainda está ativa (não concluída e não trancada)."""
        return self._ativa

    def lancar_avaliacao(self, nota: float, frequencia: float):
        """
        Registra nota e frequência do aluno e atualiza automaticamente sua situação.

        Args:
            nota (float): Nota obtida na disciplina (0 a 10).
            frequencia (float): Frequência do aluno em porcentagem (0 a 100).

        Raises:
            ValueError: Se nota ou frequência estiver fora dos limites.
        """
        if not 0 <= nota <= 10:
            raise ValueError("Nota deve estar entre 0 e 10.")
        if not 0 <= frequencia <= 100:
            raise ValueError("Frequência deve estar entre 0 e 100.")
        self._nota = nota
        self._frequencia = frequencia
        self._atualizar_situacao()

    def _atualizar_situacao(self):
        """
        Define automaticamente a situação acadêmica com base na avaliação.
        Após a conclusão, a matrícula deixa de estar ativa e registra o
        resultado no histórico do aluno.
        """
        if self._nota is None or self._frequencia is None:
            self._situacao = self.SITUACAO_CURSANDO
            return

        if self._frequencia < 75:
            self._situacao = self.SITUACAO_REPROVADO_FREQUENCIA
        elif self._nota < 6:
            self._situacao = self.SITUACAO_REPROVADO_NOTA
        else:
            self._situacao = self.SITUACAO_APROVADO

        self._ativa = False
        self._registrar_no_historico_do_aluno()

    def _registrar_no_historico_do_aluno(self):
        """
        Adiciona os dados finais da matrícula ao histórico acadêmico do aluno.
        Executado somente quando há conclusão (aprovação ou reprovação).
        """
        if self._frequencia is None or self._nota is None:
            return
        self._aluno.adicionar_historico(
            codigo_curso=self._turma.curso.codigo,
            nota=self._nota,
            frequencia=self._frequencia,
            carga_horaria=self._turma.curso.carga_horaria,
            situacao=self._situacao
        )

    def trancar(self):
        """
        Tranca a matrícula.
        Uma matrícula trancada nunca pode ser concluída posteriormente.

        Raises:
            ValueError: Se a matrícula já estiver concluída.
        """
        if not self._ativa:
            raise ValueError("Não é possível trancar uma matrícula já finalizada.")
        self._situacao = self.SITUACAO_TRANCADA
        self._ativa = False

    def __eq__(self, other):
        """Matrículas são consideradas iguais se aluno e turma forem iguais."""
        if not isinstance(other, Matricula):
            return NotImplemented
        return self.aluno == other.aluno and self.turma == other.turma

    def __hash__(self):
        """Permite uso da matrícula em conjuntos ou como chave de dicionário."""
        return hash((self.aluno, self.turma))

    def __str__(self):
        """Representação amigável da matrícula."""
        return f"Matrícula de {self.aluno.nome} em {self.turma.curso.nome} — Situação: {self.situacao}"

    def __repr__(self):
        """Representação técnica da matrícula para debug."""
        return f"Matricula(aluno={self.aluno.matricula}, turma={self.turma.id}, situacao={self.situacao})"
