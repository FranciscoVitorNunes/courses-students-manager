# models/aluno.py
from models.pessoa import Pessoa
from typing import List, Dict, Any, Optional


class Aluno(Pessoa):
    """Representa um aluno e operações relativas ao seu histórico e CR."""

    def __init__(self, matricula: str, nome: str, email: str, cr: float = 0.0):
        """
        Inicializa um objeto aluno.
        
        Args:
            matricula (str): Matrícula única do aluno.
            nome (str): Nome do aluno.
            email (str): Email do aluno.
            cr (float): Coeficiente de Rendimento (opcional, padrão 0.0)
        
        Raises:
            ValueError: Se a matrícula for vazia ou inválida.
        """
        super().__init__(nome, email)
        
        if not matricula or not matricula.strip():
            raise ValueError("Matrícula não pode ser vazia.")
        
        self._matricula = matricula.strip()
        self._historico: List[Dict[str, Any]] = []
        self._cr = float(cr)

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

    def calcular_cr(self) -> float:
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
        soma_ponderada = 0.0
        
        for registro in self._historico:
            # Considera apenas disciplinas concluídas (não "CURSANDO")
            if registro.get('situacao') in ['APROVADO', 'REPROVADO_POR_NOTA']:
                nota = float(registro.get('nota', 0))
                carga = int(registro.get('carga_horaria', 0))
                
                if carga > 0:
                    soma_ponderada += nota * carga
                    total_carga += carga
        
        self._cr = round(soma_ponderada / total_carga, 2) if total_carga > 0 else 0.0
        return self._cr

    def adicionar_ao_historico(self, codigo_curso: str, nota: float, frequencia: float, 
                               carga_horaria: int, situacao: str) -> None:
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
        if situacao not in ['APROVADO', 'REPROVADO_POR_NOTA', 
                           'REPROVADO_POR_FREQUENCIA', 'CURSANDO']:
            raise ValueError("Situação inválida.")
        
        registro = {
            'codigo_curso': codigo_curso,
            'nota': float(nota),
            'frequencia': float(frequencia),
            'carga_horaria': int(carga_horaria),
            'situacao': situacao
        }
        self._historico.append(registro)
        self.calcular_cr()

    def carregar_historico(self, historico: List[Dict[str, Any]]) -> None:
        """
        Carrega o histórico completo do aluno (útil para reconstrução do banco).
        
        Args:
            historico: Lista de registros históricos.
        """
        self._historico = []
        for registro in historico:
            self.adicionar_ao_historico(
                codigo_curso=registro['codigo_curso'],
                nota=registro['nota'],
                frequencia=registro['frequencia'],
                carga_horaria=registro['carga_horaria'],
                situacao=registro['situacao']
            )
        self.calcular_cr()

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

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o aluno para um dicionário.
        
        Returns:
            Dict com os dados do aluno.
        """
        return {
            'matricula': self.matricula,
            'nome': self.nome,
            'email': self.email,
            'cr': self.cr,
            'historico': self.historico
        }

    def __lt__(self, outro: 'Aluno') -> bool:
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

    def __str__(self):
        return f"Aluno({self.matricula}) - {self.nome} - CR: {self.cr}"

    def __repr__(self):
        return f"Aluno(matricula='{self.matricula}', nome='{self.nome}', email='{self.email}', cr={self.cr})"