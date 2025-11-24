class Relatorio:
    """
    Classe responsável por gerar relatórios acadêmicos com base nos
    dados de alunos, turmas e configuração do sistema.
    """

    def __init__(self, configuracao_sistema, regra_aprovacao):
        """
        Inicializa o serviço de relatórios.

        Args:
            configuracao_sistema (ConfiguracaoSistema): Configurações institucionais.
            regra_aprovacao (RegraAprovacao): Serviço responsável por avaliar desempenho.
        """
        self._config = configuracao_sistema
        self._regra = regra_aprovacao

    def alunos_por_turma(self, turma):
        """
        Retorna os alunos matriculados em uma turma.

        Args:
            turma (Turma): Turma consultada.

        Returns:
            list[Aluno]: Lista de alunos da turma.
        """
        return [matricula.aluno for matricula in turma.matriculas]

    def taxa_aprovacao(self, turma):
        """
        Calcula a taxa de aprovação de uma turma.

        Args:
            turma (Turma): Turma consultada.

        Returns:
            float: Percentual de aprovação (0 a 100).
        """
        concluidas = [
            m for m in turma.matriculas
            if not m.ativa and m.situacao != m.SITUACAO_TRANCADA
        ]
        if not concluidas:
            return 0.0
        aprovados = [
            m for m in concluidas if m.situacao == m.SITUACAO_APROVADO
        ]
        return round((len(aprovados) / len(concluidas)) * 100, 2)

    def distribuicao_notas(self, turma):
        """
        Retorna um dicionário com a distribuição das notas dos alunos.

        Args:
            turma (Turma): Turma consultada.

        Returns:
            dict: Chaves "APROVADO", "REPROVADO_POR_NOTA", "REPROVADO_POR_FREQUENCIA", "TRANCADA".
        """
        resultado = {
            "APROVADO": 0,
            "REPROVADO_POR_NOTA": 0,
            "REPROVADO_POR_FREQUENCIA": 0,
            "TRANCADA": 0
        }
        for m in turma.matriculas:
            if not m.ativa:
                resultado[m.situacao] = resultado.get(m.situacao, 0) + 1
        return resultado

    def alunos_em_risco(self, alunos: list):
        """
        Retorna alunos considerados em risco acadêmico segundo a regra institucional.

        Args:
            alunos (list[Aluno]): Lista de alunos avaliados.

        Returns:
            list[Aluno]: Lista de alunos em risco.
        """
        return [a for a in alunos if self._regra.aluno_em_risco(a)]

    def ranking(self, alunos: list):
        """
        Retorna o ranking de alunos com base no CR, limitado ao top N definido na configuração.

        Args:
            alunos (list[Aluno]): Lista de alunos avaliados.

        Returns:
            list[Aluno]: Ranking dos melhores alunos.
        """
        alunos_ordenados = sorted(alunos, reverse=True)
        return alunos_ordenados[: self._config.top_n_alunos]
