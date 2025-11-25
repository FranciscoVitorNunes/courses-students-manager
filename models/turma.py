from models.oferta import Oferta


class Turma(Oferta):
    """
    Representa uma turma ofertada para um curso em um determinado período letivo.
    Possui vínculo com um curso, controla o status (aberta/fechada) e registra matrículas.
    """

    STATUS_ABERTA = "aberta"
    STATUS_FECHADA = "fechada"

    def __init__(self, id: str, periodo: str, horarios: dict, vagas: int, curso):
        """
        Inicializa uma turma vinculada a um curso.

        Args:
            id (str): Identificador único da turma.
            periodo (str): Período letivo da turma.
            horarios (dict): Horários da turma no formato {dia: "inicio-fim"}.
            vagas (int): Quantidade máxima de vagas.
            curso (Curso): Curso ao qual a turma pertence.

        Raises:
            ValueError: Se o curso não for fornecido.
        """
        super().__init__(id, periodo, horarios, vagas)
        if curso is None:
            raise ValueError("A turma deve estar vinculada a um curso.")
        self._curso = curso
        self._status = self.STATUS_ABERTA
        self._matriculas = []

    @property
    def curso(self):
        """Retorna o curso ao qual a turma pertence."""
        return self._curso

    @property
    def status(self):
        """Retorna o status da turma (aberta ou fechada)."""
        return self._status

    @property
    def matriculas(self):
        """Retorna uma lista das matrículas registradas na turma."""
        return self._matriculas.copy()

    def abrir(self):
        """Altera o status da turma para aberta."""
        self._status = self.STATUS_ABERTA

    def fechar(self):
        """Altera o status da turma para fechada."""
        self._status = self.STATUS_FECHADA

    def adicionar_matricula(self, matricula):
        """
        Adiciona uma matrícula à turma

        Args:
            matricula (Matricula): Matrícula a ser associada à turma.
        """
        self._matriculas.append(matricula)

    def vagas_ocupadas(self) -> int:
        """
        Retorna o número de vagas ocupadas considerando apenas matrículas ativas.

        Returns:
            int: Quantidade de matrículas ativas na turma.
        """
        return sum(1 for m in self._matriculas if m.ativa)

    def vagas_disponiveis(self) -> int:
        """
        Retorna o número de vagas ainda disponíveis na turma.

        Returns:
            int: Número de vagas restantes.
        """
        return self.vagas - self.vagas_ocupadas()

    def __len__(self):
        """Retorna a quantidade de matrículas ativas, permitindo len(turma)."""
        return self.vagas_ocupadas()

    def __str__(self):
        """Representação amigável da turma."""
        return f"Turma {self.id} — {self.curso.nome} — {self.periodo} ({self.status})"

    def __repr__(self):
        """Representação técnica da turma."""
        return f"Turma(id='{self.id}', curso='{self.curso.codigo}', periodo='{self.periodo}', status='{self.status}')"
