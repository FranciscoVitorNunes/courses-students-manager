# models/aluno.py
from models.pessoa import Pessoa
from typing import List, Dict, Any, Optional
from datetime import datetime


class Aluno(Pessoa):
    """Representa um aluno e operações relativas ao seu histórico e CR."""

    def __init__(self, matricula: str, nome: str, email: str, cr: float = 0.0, 
                 historico: Optional[List[Dict[str, Any]]] = None):
        """
        Inicializa um objeto aluno.
        
        Args:
            matricula (str): Matrícula única do aluno.
            nome (str): Nome do aluno.
            email (str): Email do aluno.
            cr (float): Coeficiente de Rendimento (opcional, padrão 0.0)
            historico: Histórico do aluno (opcional)
        
        Raises:
            ValueError: Se a matrícula for vazia ou inválida.
        """
        super().__init__(nome, email)
        
        if not matricula or not matricula.strip():
            raise ValueError("Matrícula não pode ser vazia.")
        
        self._matricula = matricula.strip()
        self._historico: List[Dict[str, Any]] = historico if historico else []
        self._cr = float(cr)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Aluno':
        """
        Cria um aluno a partir de um dicionário.
        
        Args:
            data: Dicionário com dados do aluno.
        
        Returns:
            Instância de Aluno.
        """
        return cls(
            matricula=data['matricula'],
            nome=data['nome'],
            email=data['email'],
            cr=data.get('cr', 0.0),
            historico=data.get('historico', [])
        )

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
            situacao = registro.get('situacao', '').upper()
            if situacao in ['APROVADO', 'REPROVADO_POR_NOTA']:
                nota = float(registro.get('nota', 0))
                carga = int(registro.get('carga_horaria', 0))
                
                if carga > 0:
                    soma_ponderada += nota * carga
                    total_carga += carga
        
        self._cr = round(soma_ponderada / total_carga, 2) if total_carga > 0 else 0.0
        return self._cr

    def adicionar_ao_historico(self, codigo_curso: str, nota: float, frequencia: float, 
                               carga_horaria: int, situacao: str, semestre: Optional[str] = None) -> None:
        """
        Adiciona um registro ao histórico acadêmico do aluno.
        
        Args:
            codigo_curso (str): Código único da disciplina.
            nota (float): Nota obtida (0-10).
            frequencia (float): Frequência (0-100%).
            carga_horaria (int): Carga horária da disciplina.
            situacao (str): Situação (APROVADO, REPROVADO_POR_NOTA, etc).
            semestre (str): Semestre em que o curso foi cursado (opcional).
        
        Raises:
            ValueError: Se os valores estiverem fora dos limites permitidos.
        """
        # Validações
        if not 0 <= nota <= 10:
            raise ValueError("Nota deve estar entre 0 e 10.")
        if not 0 <= frequencia <= 100:
            raise ValueError("Frequência deve estar entre 0 e 100.")
        if carga_horaria <= 0:
            raise ValueError("Carga horária deve ser maior que zero.")
        
        situacoes_validas = ['APROVADO', 'REPROVADO_POR_NOTA', 
                            'REPROVADO_POR_FREQUENCIA', 'CURSANDO', 
                            'TRANCADO', 'DESISTENTE']
        
        situacao_upper = situacao.upper()
        if situacao_upper not in situacoes_validas:
            raise ValueError(f"Situação inválida. Use: {', '.join(situacoes_validas)}")
        
        # Verificar se curso já está no histórico
        for registro in self._historico:
            if registro.get('codigo_curso') == codigo_curso:
                raise ValueError(f"Curso {codigo_curso} já está no histórico do aluno.")
        
        registro = {
            'codigo_curso': codigo_curso,
            'nota': float(nota),
            'frequencia': float(frequencia),
            'carga_horaria': int(carga_horaria),
            'situacao': situacao_upper,
            'semestre': semestre,
            'data_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self._historico.append(registro)
        self.calcular_cr()
        return registro

    def atualizar_historico(self, codigo_curso: str, **kwargs) -> bool:
        """
        Atualiza um registro existente no histórico.
        
        Args:
            codigo_curso: Código do curso a atualizar.
            **kwargs: Campos a atualizar (nota, frequencia, situacao, etc.)
        
        Returns:
            True se atualizado, False se curso não encontrado.
        """
        for registro in self._historico:
            if registro.get('codigo_curso') == codigo_curso:
                # Atualizar apenas campos válidos
                campos_validos = ['nota', 'frequencia', 'situacao', 'semestre']
                for campo, valor in kwargs.items():
                    if campo in campos_validos:
                        if campo == 'nota' and not (0 <= float(valor) <= 10):
                            raise ValueError("Nota deve estar entre 0 e 10.")
                        elif campo == 'frequencia' and not (0 <= float(valor) <= 100):
                            raise ValueError("Frequência deve estar entre 0 e 100.")
                        
                        registro[campo] = valor
                
                registro['data_registro'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.calcular_cr()
                return True
        
        return False

    def remover_do_historico(self, codigo_curso: str) -> bool:
        """
        Remove um curso do histórico do aluno.
        
        Args:
            codigo_curso: Código do curso a remover.
        
        Returns:
            True se removido, False se não encontrado.
        """
        for i, registro in enumerate(self._historico):
            if registro.get('codigo_curso') == codigo_curso:
                self._historico.pop(i)
                self.calcular_cr()
                return True
        
        return False

    def carregar_historico(self, historico: List[Dict[str, Any]]) -> None:
        """
        Carrega o histórico completo do aluno (útil para reconstrução do banco).
        
        Args:
            historico: Lista de registros históricos.
        """
        self._historico = []
        for registro in historico:
            self._historico.append({
                'codigo_curso': registro['codigo_curso'],
                'nota': float(registro.get('nota', 0)),
                'frequencia': float(registro.get('frequencia', 0)),
                'carga_horaria': int(registro.get('carga_horaria', 0)),
                'situacao': registro.get('situacao', 'CURSANDO').upper(),
                'semestre': registro.get('semestre'),
                'data_registro': registro.get('data_registro', 
                                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            })
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

    def get_cursos_cursados(self) -> List[str]:
        """
        Retorna lista de códigos de cursos que o aluno já cursou.
        
        Returns:
            Lista de códigos de cursos.
        """
        return [registro['codigo_curso'] for registro in self._historico]

    def get_cursos_aprovados(self) -> List[str]:
        """
        Retorna lista de códigos de cursos que o aluno foi aprovado.
        
        Returns:
            Lista de códigos de cursos aprovados.
        """
        return [registro['codigo_curso'] for registro in self._historico 
                if registro.get('situacao') == 'APROVADO']

    def get_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do aluno.
        
        Returns:
            Dicionário com estatísticas.
        """
        total_cursos = len(self._historico)
        cursos_aprovados = sum(1 for r in self._historico if r.get('situacao') == 'APROVADO')
        cursos_reprovados = sum(1 for r in self._historico if r.get('situacao').startswith('REPROVADO'))
        
        # Calcular média geral de notas
        notas = [r['nota'] for r in self._historico if 'nota' in r]
        media_geral = round(sum(notas) / len(notas), 2) if notas else 0.0
        
        return {
            'total_cursos': total_cursos,
            'cursos_aprovados': cursos_aprovados,
            'cursos_reprovados': cursos_reprovados,
            'taxa_aprovacao': round((cursos_aprovados / total_cursos * 100), 2) if total_cursos > 0 else 0.0,
            'media_geral': media_geral,
            'cr': self.cr
        }

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
            'historico': self.historico,
            'estatisticas': self.get_estatisticas()
        }

    def to_dict_resumo(self) -> Dict[str, Any]:
        """
        Retorna um resumo do aluno (sem histórico detalhado).
        
        Returns:
            Dict resumido do aluno.
        """
        return {
            'matricula': self.matricula,
            'nome': self.nome,
            'email': self.email,
            'cr': self.cr,
            'total_cursos': len(self._historico),
            'cursos_aprovados': len(self.get_cursos_aprovados())
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
        return f"Aluno({self.matricula}) - {self.nome} - CR: {self.cr} - Cursos: {len(self.historico)}"

    def __repr__(self):
        return f"Aluno(matricula='{self.matricula}', nome='{self.nome}', email='{self.email}', cr={self.cr})"