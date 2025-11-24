from models.pessoa import Pessoa


class Aluno(Pessoa):
    """Representa um aluno e operações relativas ao seu histórico e CR."""

    def __init__(self, matricula: str, nome: str, email: str):
        """
        Inicializa um objeto aluno.
        
        Args:
            matricula (str): Matrícula única do aluno.
            nome (str): Nome do aluno.
            email (str): Email do aluno.
        
        Raises:
            ValueError: Se a matrícula for vazia ou inválida.
        """
        super().__init__(nome, email)
        
        if not matricula or not matricula.strip():
            raise ValueError("Matrícula não pode ser vazia.")
        
        self._matricula = matricula.strip()
        self._historico = []
        self._cr = 0.0

    @property
    def matricula(self):
        """Retorna a matrícula do aluno (somente leitura)."""
        return self._matricula

    @property
    def historico(self):
        """Retorna uma cópia do histórico para evitar modificação externa."""
        return self._historico.copy()

    @property
    def cr(self):
        """Retorna o CR atual (Coeficiente de Rendimento)."""
        return self._cr

    def calcular_cr(self):
        """
        Calcula e atualiza o Coeficiente de Rendimento (CR) do aluno.
        
        O CR é a média ponderada das notas pela carga horária.
        Considera apenas disciplinas com situação "APROVADO" ou "REPROVADO_POR_NOTA".
        
        Returns:
            float: O coeficiente de rendimento calculado.
        """
        if not self._historico:
            self._cr = 0.0
            return self._cr
        
        total_carga = 0
        soma_ponderada = 0
        
        for registro in self._historico:
            # Considera apenas disciplinas concluídas (não "CURSANDO")
            if registro.get('situacao') in ['APROVADO', 'REPROVADO_POR_NOTA', 'REPROVADO_POR_FREQUENCIA']:
                nota = registro.get('nota', 0)
                carga = registro.get('carga_horaria', 0)
                
                if carga > 0:
                    soma_ponderada += nota * carga
                    total_carga += carga
        
        self._cr = soma_ponderada / total_carga if total_carga > 0 else 0.0
        return self._cr

    def adicionar_historico(self, codigo_curso: str, nota: float, frequencia: float, 
                           carga_horaria: int, situacao: str):
        """
        Adiciona um registro ao histórico acadêmico do aluno.
        
        Args:
            codigo_curso (str): Código único da disciplina.
            nota (float): Nota obtida (0-10).
            frequencia (float): Frequência (0-100%).
            carga_horaria (int): Carga horária da disciplina.
            situacao (str): Situação (APROVADO, REPROVADO_POR_NOTA, etc).
        
        Raises:
            ValueError: Se os valores estiverem fora dos limites permitidos.
        """
        if not 0 <= nota <= 10:
            raise ValueError("Nota deve estar entre 0 e 10.")
        if not 0 <= frequencia <= 100:
            raise ValueError("Frequência deve estar entre 0 e 100.")
        if carga_horaria <= 0:
            raise ValueError("Carga horária deve ser maior que zero.")
        
        registro = {
            'codigo_curso': codigo_curso,
            'nota': nota,
            'frequencia': frequencia,
            'carga_horaria': carga_horaria,
            'situacao': situacao
        }
        self._historico.append(registro)
        self.calcular_cr()

    def get_historico(self):
        """Retorna o histórico completo do aluno."""
        return self.historico

    def get_cr(self):
        """Retorna o CR atual do aluno."""
        return self.cr

    def curso_aprovado(self, codigo_curso: str) -> bool:
        """
        Verifica se o aluno foi aprovado em um curso específico.
        
        Args:
            codigo_curso (str): Código do curso a verificar.
        
        Returns:
            bool: True se o aluno foi aprovado no curso.
        """
        for registro in self._historico:
            if (registro.get('codigo_curso') == codigo_curso and 
                registro.get('situacao') == 'APROVADO'):
                return True
        return False

    def __lt__(self, outro):
        """
        Compara alunos para ordenação.
        Critério primário: CR (decrescente)
        Critério secundário: Nome (alfabética)
        
        Args:
            outro (Aluno): Outro aluno para comparação.
        
        Returns:
            bool: True se este aluno deve vir antes na ordenação.
        """
        if not isinstance(outro, Aluno):
            return NotImplemented
        
        # Ordenação decrescente por CR
        if self.cr != outro.cr:
            return self.cr > outro.cr
        
        # Desempate por nome (ordem alfabética)
        return self.nome < outro.nome

    def __eq__(self, outro):
        """
        Compara igualdade de alunos pela matrícula.
        
        Args:
            outro (Aluno): Outro aluno para comparação.
        
        Returns:
            bool: True se as matrículas são iguais.
        """
        if not isinstance(outro, Aluno):
            return NotImplemented
        return self.matricula == outro.matricula

    def __hash__(self):
        """Permite uso em sets e dicts."""
        return hash(self.matricula)

    def __str__(self):
        """Representação amigável do aluno."""
        return f"Aluno {self.nome} (Matrícula: {self.matricula}, CR: {self.cr:.2f})"

    def __repr__(self):
        """Representação técnica do aluno."""
        return f"Aluno(matricula='{self.matricula}', nome='{self.nome}', cr={self.cr:.2f})"

    def __iter__(self):
        """Permite iteração sobre o histórico."""
        return iter(self._historico)