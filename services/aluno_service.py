# services/aluno_service.py
from typing import List, Optional, Dict, Any
from models.aluno import Aluno
from repositories.aluno_repository import AlunoRepository
from schemas.aluno_schema import AlunoSchema, UpdateAlunoSchema
from schemas.historico_schema import HistoricoCreateSchema


class AlunoService:
    def __init__(self):
        self.repository = AlunoRepository()
    
    def criar_aluno(self, aluno_data: AlunoSchema) -> Aluno:
        """
        Cria um novo aluno.
        
        Args:
            aluno_data: Dados do aluno a ser criado.
            
        Returns:
            Objeto Aluno criado.
            
        Raises:
            ValueError: Se a matrícula já existir ou dados forem inválidos.
        """
        # Verificar se aluno já existe
        if self.repository.existe_matricula(aluno_data.matricula):
            raise ValueError(f"Aluno com matrícula {aluno_data.matricula} já existe.")
        
        # Criar objeto Aluno
        aluno = Aluno(
            matricula=aluno_data.matricula,
            nome=aluno_data.nome,
            email=aluno_data.email,
            cr=aluno_data.cr if aluno_data.cr is not None else 0.0
        )
        
        # Salvar no banco via repository
        self.repository.salvar(aluno_data)
        
        # Salvar histórico se fornecido
        if aluno_data.historico:
            for registro in aluno_data.historico:
                self.repository.adicionar_historico(
                    aluno_data.matricula,
                    registro
                )
        
        return aluno
    
    def buscar_aluno(self, matricula: str) -> Optional[Aluno]:
        """
        Busca um aluno pela matrícula.
        
        Args:
            matricula: Matrícula do aluno.
            
        Returns:
            Objeto Aluno se encontrado, None caso contrário.
        """
        aluno_data = self.repository.buscar_por_matricula(matricula)
        if not aluno_data:
            return None
        
        # Converter schema para objeto Aluno
        aluno = Aluno(
            matricula=aluno_data.matricula,
            nome=aluno_data.nome,
            email=aluno_data.email,
            cr=aluno_data.cr,
            historico=aluno_data.historico
        )
        
        return aluno
    
    # ... (outros métodos permanecem iguais até adicionar os novos métodos de histórico)
    
    def adicionar_ao_historico(self, aluno_matricula: str, historico_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adiciona um registro ao histórico do aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            historico_data: Dados do registro histórico.
            
        Returns:
            Registro criado.
            
        Raises:
            ValueError: Se aluno não existir ou dados forem inválidos.
        """
        # Verificar se aluno existe
        if not self.repository.existe_matricula(aluno_matricula):
            raise ValueError(f"Aluno com matrícula {aluno_matricula} não encontrado.")
        
        # Criar objeto Aluno para validação
        aluno = self.buscar_aluno(aluno_matricula)
        if not aluno:
            raise ValueError(f"Aluno com matrícula {aluno_matricula} não encontrado.")
        
        # Adicionar ao objeto Aluno (validação ocorre aqui)
        registro = aluno.adicionar_ao_historico(
            codigo_curso=historico_data['codigo_curso'],
            nota=historico_data['nota'],
            frequencia=historico_data['frequencia'],
            carga_horaria=historico_data['carga_horaria'],
            situacao=historico_data['situacao'],
            semestre=historico_data.get('semestre')
        )
        
        # Persistir no banco
        registro_id = self.repository.adicionar_historico(aluno_matricula, registro)
        registro['id'] = registro_id
        
        # Atualizar CR no banco
        self.repository.atualizar_cr_aluno(aluno_matricula)
        
        return registro
    
    def obter_historico_aluno(self, aluno_matricula: str) -> List[Dict[str, Any]]:
        """
        Obtém o histórico completo de um aluno.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            
        Returns:
            Lista de registros históricos.
            
        Raises:
            ValueError: Se aluno não existir.
        """
        if not self.repository.existe_matricula(aluno_matricula):
            raise ValueError(f"Aluno com matrícula {aluno_matricula} não encontrado.")
        
        return self.repository.buscar_historico_aluno(aluno_matricula)
    
    def atualizar_registro_historico(self, registro_id: int, dados: Dict[str, Any]) -> bool:
        """
        Atualiza um registro do histórico.
        
        Args:
            registro_id: ID do registro.
            dados: Dados a atualizar.
            
        Returns:
            True se atualizado, False caso contrário.
        """
        # Buscar registro atual
        registro = self.repository.buscar_registro_historico(registro_id)
        if not registro:
            return False
        
        # Buscar aluno para validação
        aluno = self.buscar_aluno(registro['aluno_matricula'])
        if not aluno:
            return False
        
        # Atualizar no objeto Aluno (validação ocorre aqui)
        atualizado = aluno.atualizar_historico(registro['codigo_curso'], **dados)
        if not atualizado:
            return False
        
        # Persistir no banco
        atualizado = self.repository.atualizar_historico(registro_id, dados)
        if atualizado:
            # Atualizar CR no banco
            self.repository.atualizar_cr_aluno(registro['aluno_matricula'])
        
        return atualizado
    
    def remover_do_historico(self, registro_id: int) -> bool:
        """
        Remove um registro do histórico.
        
        Args:
            registro_id: ID do registro.
            
        Returns:
            True se removido, False caso contrário.
        """
        # Buscar registro para obter matrícula do aluno
        registro = self.repository.buscar_registro_historico(registro_id)
        if not registro:
            return False
        
        # Remover do banco
        removido = self.repository.remover_historico(registro_id)
        if removido:
            # Atualizar CR do aluno
            self.repository.atualizar_cr_aluno(registro['aluno_matricula'])
        
        return removido
    
    def verificar_pre_requisitos(self, matricula: str, codigos_cursos: List[str]) -> Dict[str, bool]:
        """
        Verifica se aluno cumpriu pré-requisitos para uma lista de cursos.
        
        Args:
            matricula: Matrícula do aluno.
            codigos_cursos: Lista de códigos de cursos para verificar.
            
        Returns:
            Dicionário com código do curso como chave e booleano como valor.
        """
        aluno = self.buscar_aluno(matricula)
        if not aluno:
            raise ValueError(f"Aluno {matricula} não encontrado.")
        
        resultados = {}
        for codigo in codigos_cursos:
            resultados[codigo] = self.repository.verificar_curso_aprovado(matricula, codigo)
        
        return resultados
    
    def calcular_cr_aluno(self, matricula: str) -> Optional[float]:
        """
        Calcula o CR de um aluno específico diretamente do banco.
        
        Args:
            matricula: Matrícula do aluno.
            
        Returns:
            Valor do CR se aluno encontrado, None caso contrário.
        """
        if not self.repository.existe_matricula(matricula):
            return None
        
        return self.repository.calcular_cr_aluno(matricula)
    
    def atualizar_cr_aluno(self, matricula: str) -> bool:
        """
        Atualiza o CR de um aluno no banco de dados.
        
        Args:
            matricula: Matrícula do aluno.
            
        Returns:
            True se atualizado, False caso contrário.
        """
        if not self.repository.existe_matricula(matricula):
            return False
        
        return self.repository.atualizar_cr_aluno(matricula)
    
    def get_estatisticas_aluno(self, matricula: str) -> Optional[Dict[str, Any]]:
        """
        Obtém estatísticas do aluno.
        
        Args:
            matricula: Matrícula do aluno.
            
        Returns:
            Dicionário com estatísticas, ou None se aluno não existir.
        """
        aluno = self.buscar_aluno(matricula)
        if not aluno:
            return None
        
        return aluno.get_estatisticas()