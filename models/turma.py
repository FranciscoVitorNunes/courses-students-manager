# models/turma.py
from models.oferta import Oferta
from models.curso import Curso
from typing import List, Dict, Any, Optional


class Turma(Oferta):
    """
    Representa uma turma ofertada para um curso em um determinado período letivo.
    Possui vínculo com um curso, controla o status (aberta/fechada) e registra matrículas.
    """

    def __init__(self, id: str, periodo: str, horarios: Dict[str, str], 
                 vagas: int, curso: Curso, local: Optional[str] = None, status: bool=True):
        """
        Inicializa uma turma vinculada a um curso.

        Args:
            id (str): Identificador único da turma.
            periodo (str): Período letivo da turma.
            horarios (dict): Horários da turma no formato {dia: "HH:MM-HH:MM"}.
            vagas (int): Quantidade máxima de vagas.
            curso (Curso): Curso ao qual a turma pertence.
            local (str): Local onde a turma acontece (opcional).

        Raises:
            ValueError: Se o curso não for fornecido.
        """
        super().__init__(id, periodo, horarios, vagas)
        
        if curso is None:
            raise ValueError("A turma deve estar vinculada a um curso.")
        
        self._curso = curso
        self._local = local.strip() if local else None
        self._status = status
        self._matriculas = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], curso: Curso) -> 'Turma':
        """
        Cria uma turma a partir de um dicionário.

        Args:
            data: Dicionário com dados da turma.
            curso: Objeto Curso associado.

        Returns:
            Instância de Turma.
        """
        return cls(
            id=data['id'],
            periodo=data['periodo'],
            horarios=data['horarios'],
            vagas=data['vagas'],
            curso=curso,
            local=data.get('local')
        )
    @property
    def id(self):
        """Retorna ID da turna"""
        return self._id
    
    @property
    def curso(self) -> Curso:
        """Retorna o curso ao qual a turma pertence."""
        return self._curso

    @property
    def local(self) -> Optional[str]:
        """Retorna o local da turma."""
        return self._local

    @local.setter
    def local(self, valor: str):
        """Define o local da turma."""
        self._local = valor.strip() if valor else None

    @property
    def status(self) -> str:
        """Retorna o status da turma."""
        return self._status

    @property
    def matriculas(self) -> List:
        """Retorna uma cópia das matrículas registradas na turma."""
        return self._matriculas.copy()

    def abrir(self):
        """Altera o status da turma para aberta."""
        self._status = True

    def fechar(self):
        """Altera o status da turma para fechada."""
        self._status = False

    def atualizar_status_vagas(self) -> None:
        """
        Atualiza status automaticamente com base nas vagas.
        Se todas as vagas estiverem ocupadas, status muda para "esgotada".
        """
        if self.vagas_ocupadas() >= self.vagas:
            self._status = False
        else:
            self._status = True

    def adicionar_matricula(self, matricula) -> bool:
        """
        Adiciona uma matrícula à turma.

        Args:
            matricula: Matrícula a ser associada à turma.

        Returns:
            bool: True se adicionada com sucesso.
        """
        if not matricula:
            raise ValueError("Matrícula não pode ser nula.")
        
        self._matriculas.append(matricula)
        self.atualizar_status_vagas()
        return True

    def remover_matricula(self, matricula) -> bool:
        """
        Remove uma matrícula da turma.

        Args:
            matricula: Matrícula a ser removida.

        Returns:
            bool: True se removida, False se não encontrada.
        """
        if matricula in self._matriculas:
            self._matriculas.remove(matricula)
            self.atualizar_status_vagas()
            return True
        return False

    def vagas_ocupadas(self) -> int:
        """
        Retorna o número de vagas ocupadas considerando apenas matrículas ativas.

        Returns:
            int: Quantidade de matrículas ativas na turma.
        """
        # Considerando todas as matrículas como ativas por padrão
        # Em uma implementação real, verificaríamos um campo 'ativa' em cada matrícula
        return len(self._matriculas)

    def vagas_disponiveis(self) -> int:
        """
        Retorna o número de vagas ainda disponíveis na turma.

        Returns:
            int: Número de vagas restantes.
        """
        return max(0, self.vagas - self.vagas_ocupadas())

    def esta_aberta_para_matricula(self) -> bool:
        """
        Verifica se a turma está aberta para novas matrículas.

        Returns:
            bool: True se aberta e com vagas disponíveis.
        """
        return self._status == True 

    def verificar_choque_com_turma(self, outra_turma: 'Turma') -> bool:
        """
        Verifica se há choque de horário com outra turma.

        Args:
            outra_turma: Outra turma para verificação.

        Returns:
            bool: True se houver choque de horário.
        """
        return self.verificar_choque(outra_turma.horarios)

    def get_info_matriculas(self) -> Dict[str, Any]:
        """
        Retorna informações sobre as matrículas da turma.

        Returns:
            Dict com informações das matrículas.
        """
        return {
            'total_matriculas': len(self._matriculas),
            'vagas_ocupadas': self.vagas_ocupadas(),
            'vagas_disponiveis': self.vagas_disponiveis(),
            'taxa_ocupacao': round((self.vagas_ocupadas() / self.vagas) * 100, 2) if self.vagas > 0 else 0.0
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a turma para dicionário.

        Returns:
            Dict com dados da turma.
        """
        return {
            'id': self.id,
            'periodo': self.periodo,
            'vagas': self.vagas,
            'horarios': self.horarios,
            'local': self.local,
            'status': self.status,
            'curso': self.curso.to_dict_resumo(),
            'vagas_ocupadas': self.vagas_ocupadas(),
            'vagas_disponiveis': self.vagas_disponiveis(),
            'info_matriculas': self.get_info_matriculas()
        }

    def to_dict_resumo(self) -> Dict[str, Any]:
        """
        Retorna um resumo da turma.

        Returns:
            Dict resumido da turma.
        """
        return {
            'id': self.id,
            'periodo': self.periodo,
            'vagas': self.vagas,
            'status': self.status,
            'curso_codigo': self.curso.codigo,
            'curso_nome': self.curso.nome,
            'vagas_disponiveis': self.vagas_disponiveis()
        }

    def __len__(self) -> int:
        """Retorna a quantidade de matrículas ativas, permitindo len(turma)."""
        return self.vagas_ocupadas()

    def __eq__(self, outro: object) -> bool:
        """
        Compara duas turmas por ID.

        Args:
            outro: Outro objeto para comparação.

        Returns:
            bool: True se os IDs são iguais.
        """
        if not isinstance(outro, Turma):
            return NotImplemented
        return self.id == outro.id

    def __str__(self) -> str:
        """Representação amigável da turma."""
        status_str = f" ({self.status})" if self.status != True else ""
        local_str = f" - Local: {self.local}" if self.local else ""
        return f"Turma {self.id} - {self.curso.nome} - {self.periodo}{status_str}{local_str}"

    def __repr__(self) -> str:
        """Representação técnica da turma."""
        return f"Turma(id='{self.id}', curso='{self.curso.codigo}', periodo='{self.periodo}', status='{self.status}')"
    
    def __bool__(self) -> bool:
        return bool(self.id) and self.id is not None