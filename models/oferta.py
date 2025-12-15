# models/oferta.py
from typing import Dict, List, Tuple, Optional
from datetime import time


class Oferta:
    """
    Classe base para ofertas acadêmicas (Turmas, Workshops, etc.)
    Contém atributos e métodos comuns relacionados a horários e vagas.
    """

    def __init__(self, id: str, periodo: str, horarios: Dict[str, str], vagas: int):
        """
        Inicializa uma oferta acadêmica.

        Args:
            id (str): Identificador único.
            periodo (str): Período letivo (ex: 2025.1).
            horarios (dict): Horários no formato {dia: "HH:MM-HH:MM"}.
            vagas (int): Quantidade máxima de vagas.

        Raises:
            ValueError: Se os parâmetros forem inválidos.
        """
        if not id or not id.strip():
            raise ValueError("ID da oferta não pode ser vazio.")
        if not periodo or not periodo.strip():
            raise ValueError("Período não pode ser vazio.")
        if not isinstance(vagas, int) or vagas <= 0:
            raise ValueError("Vagas deve ser um inteiro positivo.")
        if not horarios:
            raise ValueError("A oferta deve ter pelo menos um horário.")

        self._id = id.strip()
        self._periodo = periodo.strip()
        self._vagas = vagas
        self._horarios = {}
        
        # Validar e normalizar horários
        for dia, intervalo in horarios.items():
            self._adicionar_horario(dia, intervalo)

    @property
    def id(self):
        """Retorna o ID da oferta."""
        return self._id

    @property
    def periodo(self):
        """Retorna o período da oferta."""
        return self._periodo

    @periodo.setter
    def periodo(self, valor: str):
        """Define o período da oferta."""
        if not valor or not valor.strip():
            raise ValueError("Período não pode ser vazio.")
        self._periodo = valor.strip()

    @property
    def vagas(self):
        """Retorna a quantidade de vagas."""
        return self._vagas

    @vagas.setter
    def vagas(self, valor: int):
        """Define a quantidade de vagas."""
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("Vagas deve ser um inteiro positivo.")
        self._vagas = valor

    @property
    def horarios(self):
        """Retorna uma cópia dos horários."""
        return self._horarios.copy()

    def _adicionar_horario(self, dia: str, intervalo: str):
        """
        Adiciona um horário à oferta com validação.

        Args:
            dia (str): Dia da semana (ex: "seg", "ter", "qua").
            intervalo (str): Intervalo no formato "HH:MM-HH:MM".

        Raises:
            ValueError: Se o dia ou intervalo forem inválidos.
        """
        # Validar dia
        dias_validos = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
        dia_lower = dia.lower().strip()
        if dia_lower not in dias_validos:
            raise ValueError(f"Dia inválido: {dia}. Use: {', '.join(dias_validos)}")

        # Validar e parsear intervalo
        try:
            inicio_str, fim_str = intervalo.split("-")
            inicio = time.fromisoformat(inicio_str)
            fim = time.fromisoformat(fim_str)
            
            if inicio >= fim:
                raise ValueError("Horário de início deve ser anterior ao horário de fim.")
            
            if inicio.hour < 6 or fim.hour > 22:
                raise ValueError("Horários devem estar entre 06:00 e 22:00.")
            
            self._horarios[dia_lower] = intervalo
        except ValueError as e:
            raise ValueError(f"Intervalo inválido '{intervalo}': {str(e)}")

    def adicionar_horario(self, dia: str, intervalo: str):
        """
        Adiciona um novo horário à oferta.

        Args:
            dia (str): Dia da semana.
            intervalo (str): Intervalo no formato "HH:MM-HH:MM".
        """
        self._adicionar_horario(dia, intervalo)

    def remover_horario(self, dia: str) -> bool:
        """
        Remove um horário da oferta.

        Args:
            dia (str): Dia da semana a remover.

        Returns:
            bool: True se removido, False se não encontrado.
        """
        if dia.lower() in self._horarios:
            del self._horarios[dia.lower()]
            return True
        return False

    def atualizar_horario(self, dia: str, novo_intervalo: str) -> bool:
        """
        Atualiza um horário existente.

        Args:
            dia (str): Dia da semana.
            novo_intervalo (str): Novo intervalo no formato "HH:MM-HH:MM".

        Returns:
            bool: True se atualizado, False se não encontrado.
        """
        dia_lower = dia.lower()
        if dia_lower not in self._horarios:
            return False
        
        self._adicionar_horario(dia, novo_intervalo)
        return True

    def _parse_intervalo(self, intervalo: str) -> Tuple[time, time]:
        """
        Converte string de intervalo em objetos time.

        Args:
            intervalo (str): Intervalo no formato "HH:MM-HH:MM".

        Returns:
            Tuple[time, time]: Horário de início e fim.
        """
        inicio_str, fim_str = intervalo.split("-")
        return time.fromisoformat(inicio_str), time.fromisoformat(fim_str)

    def verificar_choque(self, horarios_externos: Dict[str, str]) -> bool:
        """
        Verifica se há choque de horário com outros horários.

        Args:
            horarios_externos (dict): Outros horários no formato {dia: "HH:MM-HH:MM"}.

        Returns:
            bool: True se houver choque, False caso contrário.
        """
        for dia, intervalo_externo in horarios_externos.items():
            if dia.lower() in self._horarios:
                # Parsear intervalos
                inicio_atual, fim_atual = self._parse_intervalo(self._horarios[dia.lower()])
                inicio_externo, fim_externo = self._parse_intervalo(intervalo_externo)
                
                # Verificar sobreposição
                if not (fim_atual <= inicio_externo or fim_externo <= inicio_atual):
                    return True
        return False

    def get_horarios_parseados(self) -> Dict[str, Tuple[time, time]]:
        """
        Retorna os horários parseados como objetos time.

        Returns:
            Dict[str, Tuple[time, time]]: Horários parseados.
        """
        return {
            dia: self._parse_intervalo(intervalo)
            for dia, intervalo in self._horarios.items()
        }

    def get_dias_semana(self) -> List[str]:
        """
        Retorna lista de dias da semana com horários.

        Returns:
            List[str]: Dias da semana.
        """
        return list(self._horarios.keys())

    def to_dict(self) -> Dict[str, any]:
        """
        Converte a oferta para dicionário.

        Returns:
            Dict com dados da oferta.
        """
        return {
            'id': self.id,
            'periodo': self.periodo,
            'vagas': self.vagas,
            'horarios': self.horarios
        }

    def __str__(self):
        """Representação amigável da oferta."""
        dias = ", ".join([f"{dia}: {intervalo}" for dia, intervalo in self._horarios.items()])
        return f"{self.id} - {self.periodo} - Vagas: {self.vagas} - Horários: {dias}"

    def __repr__(self):
        """Representação técnica da oferta."""
        return f"Oferta(id='{self.id}', periodo='{self.periodo}', vagas={self.vagas})"