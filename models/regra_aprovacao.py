class RegraAprovacao:
    """
    Aplica regras acadêmicas de aprovação e reprovação com base nos
    parâmetros definidos pela ConfiguracaoSistema.
    """

    def __init__(self, configuracao_sistema):
        """
        Inicializa o processador de regras acadêmicas.

        Args:
            configuracao_sistema (ConfiguracaoSistema): Objeto contendo
                os parâmetros institucionais de avaliação.
        """
        self._config = configuracao_sistema

    @property
    def configuracao(self):
        """Retorna a configuração de sistema utilizada."""
        return self._config

    def avaliar(self, nota: float, frequencia: float) -> str:
        """
        Determina a situação de um aluno em uma disciplina com base nos
        parâmetros institucionais.

        Args:
            nota (float): Nota obtida pelo aluno (0 a 10).
            frequencia (float): Frequência em porcentagem (0 a 100).

        Returns:
            str: Situação acadêmica
                 ("APROVADO", "REPROVADO_POR_NOTA"
                  ou "REPROVADO_POR_FREQUENCIA").

        Raises:
            ValueError: Se nota ou frequência estiverem fora dos limites.
        """
        if not 0 <= nota <= 10:
            raise ValueError("Nota deve estar entre 0 e 10.")
        if not 0 <= frequencia <= 100:
            raise ValueError("Frequência deve estar entre 0 e 100.")

        if frequencia < self._config.frequencia_minima:
            return "REPROVADO_POR_FREQUENCIA"
        if nota < self._config.nota_minima:
            return "REPROVADO_POR_NOTA"
        return "APROVADO"

    def aluno_aprovado(self, aluno) -> bool:
        """
        Verifica se um aluno está aprovado no contexto geral,
        considerando o CR e regras institucionais.

        Critério padrão:
            - CR >= nota mínima do sistema (critério institucional)
            - Caso a instituição altere o cálculo, esse método pode ser ajustado.

        Args:
            aluno (Aluno): Instância de aluno.

        Returns:
            bool: True se aprovado de acordo com a regra institucional.
        """
        return aluno.cr >= self._config.nota_minima

    def aluno_em_risco(self, aluno) -> bool:
        """
        Verifica se o aluno está em situação de risco acadêmico.

        Um aluno está em risco se o CR for menor que a nota mínima ou
        se tiver muitas reprovações no histórico.

        Args:
            aluno (Aluno): Instância de aluno.

        Returns:
            bool: True se o aluno estiver em situação de risco.
        """
        if aluno.cr < self._config.nota_minima:
            return True

        total_reprovacoes = sum(
            1 for registro in aluno.historico
            if registro.get("situacao") in [
                "REPROVADO_POR_NOTA",
                "REPROVADO_POR_FREQUENCIA"
            ]
        )
        return total_reprovacoes >= 2

    def melhor_entre(self, alunos: list):
        """
        Retorna o melhor aluno da lista com base na lógica institucional
        de desempenho.

        Args:
            alunos (list[Aluno]): Lista de alunos.

        Returns:
            Aluno: Melhor aluno entre os fornecidos.
        """
        if not alunos:
            return None
        return max(alunos, key=lambda a: a.cr)
