from typing import Optional
from datetime import datetime
from config.settings import Settings


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
    SITUACAO_DESISTENTE = "DESISTENTE"
    
    _settings = Settings()

    def __init__(self, aluno, turma, id: Optional[int] = None, 
                 nota: Optional[float] = None, frequencia: Optional[float] = None,
                 situacao: str = "CURSANDO", data_matricula: Optional[str] = None):
        """
        Inicializa uma matrícula vinculando um aluno a uma turma.

        Args:
            aluno (Aluno): Aluno que está se matriculando.
            turma (Turma): Turma na qual o aluno está sendo matriculado.
            id (int): ID da matrícula no banco (opcional).
            nota (float): Nota já lançada (opcional).
            frequencia (float): Frequência já lançada (opcional).
            situacao (str): Situação inicial da matrícula.
            data_matricula (str): Data da matrícula (opcional).

        Raises:
            ValueError: Se aluno ou turma forem inválidos.
        """
        if aluno is None or turma is None:
            raise ValueError("Aluno e Turma são obrigatórios.")
        
        self._id = id
        self._aluno = aluno
        self._turma = turma
        self._nota = nota
        self._frequencia = frequencia
        self._situacao = situacao.upper()
        self._data_matricula = data_matricula or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._data_conclusao = None
        self._ativa = self._situacao == self.SITUACAO_CURSANDO
    
    @classmethod
    def from_dict(cls, data: dict, aluno, turma) -> 'Matricula':
        """
        Cria uma matrícula a partir de um dicionário.

        Args:
            data: Dicionário com dados da matrícula.
            aluno: Objeto Aluno.
            turma: Objeto Turma.

        Returns:
            Instância de Matricula.
        """
        return cls(
            aluno=aluno,
            turma=turma,
            id=data.get('id'),
            nota=data.get('nota'),
            frequencia=data.get('frequencia'),
            situacao=data.get('situacao', 'CURSANDO'),
            data_matricula=data.get('data_matricula')
        )

    @property
    def id(self) -> Optional[int]:
        """Retorna o ID da matrícula."""
        return self._id

    @property
    def aluno(self):
        """Retorna o aluno associado à matrícula."""
        return self._aluno

    @property
    def turma(self):
        """Retorna a turma vinculada à matrícula."""
        return self._turma

    @property
    def nota(self) -> Optional[float]:
        """Retorna a nota lançada na matrícula."""
        return self._nota
    
    @nota.setter
    def nota(self, valor: float):
        """Define a nota da matrícula."""
        if not 0 <= valor <= 10:
            raise ValueError("Nota deve estar entre 0 e 10.")
        self._nota = valor
        self._atualizar_situacao()

    @property
    def frequencia(self) -> Optional[float]:
        """Retorna a frequência do aluno."""
        return self._frequencia
    
    @frequencia.setter
    def frequencia(self, valor: float):
        """Define a frequência da matrícula."""
        if not 0 <= valor <= 100:
            raise ValueError("Frequência deve estar entre 0 e 100.")
        self._frequencia = valor
        self._atualizar_situacao()

    @property
    def situacao(self) -> str:
        """Retorna a situação acadêmica atual da matrícula."""
        return self._situacao

    @property
    def ativa(self) -> bool:
        """Indica se a matrícula ainda está ativa."""
        return self._ativa

    @property
    def data_matricula(self) -> str:
        """Retorna a data da matrícula."""
        return self._data_matricula

    @property
    def data_conclusao(self) -> Optional[str]:
        """Retorna a data de conclusão da matrícula."""
        return self._data_conclusao

    def lancar_avaliacao(self, nota: float, frequencia: float) -> None:
        """
        Registra nota e frequência do aluno e atualiza automaticamente sua situação.

        Args:
            nota (float): Nota obtida na disciplina (0 a 10).
            frequencia (float): Frequência do aluno em porcentagem (0 a 100).

        Raises:
            ValueError: Se nota ou frequência estiver fora dos limites.
        """
        self.nota = nota
        self.frequencia = frequencia

    def _atualizar_situacao(self) -> None:
        """
        Define automaticamente a situação acadêmica com base na avaliação.
        Usa as configurações do sistema.
        """
        if self._nota is None or self._frequencia is None:
            self._situacao = self.SITUACAO_CURSANDO
            self._ativa = True
            return

        # Verificar se foi reprovado por frequência
        if self._frequencia < self._settings.frequencia_minima:
            self._situacao = self.SITUACAO_REPROVADO_FREQUENCIA
        # Verificar se foi reprovado por nota
        elif self._nota < self._settings.nota_minima_aprovacao:
            self._situacao = self.SITUACAO_REPROVADO_NOTA
        # Caso contrário, aprovado
        else:
            self._situacao = self.SITUACAO_APROVADO
        
        self._ativa = False
        self._data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._registrar_no_historico_do_aluno()

    def _registrar_no_historico_do_aluno(self) -> None:
        """
        Adiciona os dados finais da matrícula ao histórico acadêmico do aluno.
        """
        if self._frequencia is None or self._nota is None:
            return
        
        self._aluno.adicionar_ao_historico(
            codigo_curso=self._turma.curso.codigo,
            nota=self._nota,
            frequencia=self._frequencia,
            carga_horaria=self._turma.curso.carga_horaria,
            situacao=self._situacao,
            semestre=self._turma.periodo
        )

    def trancar(self) -> None:
        """
        Tranca a matrícula.
        Só pode trancar até a data limite configurada.

        Raises:
            ValueError: Se não puder trancar por data ou situação.
        """
        if not self._ativa:
            raise ValueError("Não é possível trancar uma matrícula já finalizada.")
        
        if not self._settings.pode_trancar():
            raise ValueError("Data limite para trancamento já passou.")
        
        self._situacao = self.SITUACAO_TRANCADA
        self._ativa = False
        self._data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def desistir(self) -> None:
        """
        Marca a matrícula como desistente.
        """
        self._situacao = self.SITUACAO_DESISTENTE
        self._ativa = False
        self._data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_info_avaliacao(self) -> dict:
        """
        Retorna informações sobre a avaliação do aluno.

        Returns:
            Dict com informações da avaliação.
        """
        return {
            'nota': self._nota,
            'frequencia': self._frequencia,
            'nota_minima': self._settings.nota_minima_aprovacao,
            'frequencia_minima': self._settings.frequencia_minima,
            'situacao_atual': self._situacao,
            'aprovado': self._situacao == self.SITUACAO_APROVADO
        }

    def to_dict(self) -> dict:
        """
        Converte a matrícula para dicionário.

        Returns:
            Dict com dados da matrícula.
        """
        return {
            'id': self._id,
            'aluno_matricula': self._aluno.matricula,
            'aluno_nome': self._aluno.nome,
            'turma_id': self._turma.id,
            'turma_periodo': self._turma.periodo,
            'curso_codigo': self._turma.curso.codigo,
            'curso_nome': self._turma.curso.nome,
            'nota': self._nota,
            'frequencia': self._frequencia,
            'situacao': self._situacao,
            'ativa': self._ativa,
            'data_matricula': self._data_matricula,
            'data_conclusao': self._data_conclusao,
            'info_avaliacao': self.get_info_avaliacao() if self._nota is not None else None
        }

    def to_dict_resumo(self) -> dict:
        """
        Retorna um resumo da matrícula.

        Returns:
            Dict resumido da matrícula.
        """
        return {
            'id': self._id,
            'aluno_matricula': self._aluno.matricula,
            'turma_id': self._turma.id,
            'curso_codigo': self._turma.curso.codigo,
            'situacao': self._situacao,
            'nota': self._nota,
            'ativa': self._ativa
        }

    def __eq__(self, other) -> bool:
        """Matrículas são consideradas iguais se aluno e turma forem iguais."""
        if not isinstance(other, Matricula):
            return NotImplemented
        return self.aluno == other.aluno and self.turma == other.turma

    def __hash__(self) -> int:
        """Permite uso da matrícula em conjuntos ou como chave de dicionário."""
        return hash((self.aluno.matricula, self.turma.id))

    def __str__(self) -> str:
        """Representação amigável da matrícula."""
        nota_str = f"Nota: {self._nota}" if self._nota is not None else "Nota: --"
        freq_str = f"Freq: {self._frequencia}%" if self._frequencia is not None else "Freq: --"
        return f"Matrícula {self._id}: {self._aluno.nome} em {self._turma.curso.nome} - {self._situacao} ({nota_str}, {freq_str})"

    def __repr__(self) -> str:
        """Representação técnica da matrícula para debug."""
        return f"Matricula(id={self._id}, aluno={self._aluno.matricula}, turma={self._turma.id}, situacao={self._situacao})"