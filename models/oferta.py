class Oferta:
    """
    Representa uma oferta acadêmica em um período letivo.
    É uma estrutura base que pode ser herdada por outras classes,
    como Turma.
    """

    def __init__(self, id: str, periodo: str, horarios: dict, vagas: int):
        """
        Inicializa uma oferta acadêmica.

        Args:
            id (str): Identificador único da oferta.
            periodo (str): Período letivo (ex.: "2025.1").
            horarios (dict): Horários da oferta no formato {dia: "inicio-fim"}.
            vagas (int): Quantidade máxima de vagas.

        Raises:
            ValueError: Se algum valor for inválido.
        """
        if not id or not id.strip():
            raise ValueError("ID da oferta não pode ser vazio.")
        if not periodo or not periodo.strip():
            raise ValueError("Período não pode ser vazio.")
        if not isinstance(horarios, dict) or not horarios:
            raise ValueError("Horários devem ser um dicionário não vazio.")
        if not isinstance(vagas, int) or vagas <= 0:
            raise ValueError("Vagas devem ser um inteiro maior que zero.")

        for dia, intervalo in horarios.items():
            if not isinstance(dia, str) or not isinstance(intervalo, str):
                raise ValueError("Horários devem estar no formato {dia: 'inicio-fim'}.")
            if "-" not in intervalo:
                raise ValueError("Intervalo de horário inválido (esperado 'inicio-fim').")

        self._id = id.strip()
        self._periodo = periodo.strip()
        self._horarios = horarios
        self._vagas = vagas

    @property
    def id(self):
        """Retorna o identificador único da oferta."""
        return self._id

    @property
    def periodo(self):
        """Retorna o período letivo da oferta."""
        return self._periodo

    @property
    def horarios(self):
        """Retorna os horários da oferta."""
        return self._horarios.copy()

    @property
    def vagas(self):
        """Retorna a quantidade de vagas disponíveis para a oferta."""
        return self._vagas

    def verificar_choque(self, horarios_externos: dict) -> bool:
        """
        Verifica se existe conflito de horários com outra oferta.

        Args:
            horarios_externos (dict): Horários no mesmo formato da oferta atual.

        Returns:
            bool: True se houver choque de horário, False caso contrário.
        """
        for dia, intervalo in self._horarios.items():
            if dia in horarios_externos and horarios_externos[dia] == intervalo:
                return True
        return False

    def __str__(self):
        """Representação amigável da oferta."""
        return f"Oferta {self.id} — Período {self.periodo}"

    def __repr__(self):
        """Representação técnica da oferta."""
        return f"Oferta(id='{self.id}', periodo='{self.periodo}')"
