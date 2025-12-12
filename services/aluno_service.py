# services/aluno_service.py
from typing import List, Optional, Dict, Any
from models.aluno import Aluno
from repositories.aluno_repository import AlunoRepository
from schemas.aluno_schema import AlunoSchema, UpdateAlunoSchema


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
        aluno_existente = self.repository.buscar_por_matricula(aluno_data.matricula)
        if aluno_existente:
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
            cr=aluno_data.cr
        )
        
        # Carregar histórico se existir no banco
        # Nota: Você precisará ajustar o repository para buscar histórico também
        # Por enquanto, vamos assumir que o histórico é carregado separadamente
        
        return aluno
    
    def listar_alunos(self, ordenar_por_cr: bool = False) -> List[Aluno]:
        """
        Lista todos os alunos.
        
        Args:
            ordenar_por_cr: Se True, ordena por CR decrescente.
            
        Returns:
            Lista de objetos Aluno.
        """
        alunos_data = self.repository.listar()
        
        # Converter schemas para objetos Aluno
        alunos = []
        for aluno_data in alunos_data:
            aluno = Aluno(
                matricula=aluno_data.matricula,
                nome=aluno_data.nome,
                email=aluno_data.email,
                cr=aluno_data.cr
            )
            alunos.append(aluno)
        
        # Ordenar se solicitado
        if ordenar_por_cr:
            alunos.sort()
        
        return alunos
    
    def atualizar_aluno(self, matricula: str, dados_atualizacao: UpdateAlunoSchema) -> Optional[Aluno]:
        """
        Atualiza parcialmente um aluno.
        
        Args:
            matricula: Matrícula do aluno a atualizar.
            dados_atualizacao: Dados a serem atualizados.
            
        Returns:
            Aluno atualizado se encontrado, None caso contrário.
        """
        # Converter para dicionário excluindo valores None
        dados_dict = dados_atualizacao.model_dump(exclude_none=True)
        
        # Atualizar no repository
        atualizado = self.repository.atualizar(matricula, dados_dict)
        if not atualizado:
            return None
        
        # Buscar aluno atualizado
        return self.buscar_aluno(matricula)
    
    def deletar_aluno(self, matricula: str) -> bool:
        """
        Deleta um aluno.
        
        Args:
            matricula: Matrícula do aluno a deletar.
            
        Returns:
            True se deletado, False se não encontrado.
        """
        try:
            self.repository.deletar(matricula)
            return True
        except Exception:
            return False
    
    def calcular_cr_aluno(self, matricula: str) -> Optional[float]:
        """
        Calcula o CR de um aluno específico.
        
        Args:
            matricula: Matrícula do aluno.
            
        Returns:
            Valor do CR se aluno encontrado, None caso contrário.
        """
        aluno = self.buscar_aluno(matricula)
        if not aluno:
            return None
        
        # Se o aluno tiver histórico carregado, recalcular
        # Caso contrário, retornar CR atual do banco
        return aluno.cr
    
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
            resultados[codigo] = aluno.curso_aprovado(codigo)
        
        return resultados
    
    def obter_top_alunos(self, n: int = 10) -> List[Aluno]:
        """
        Retorna os top N alunos por CR.
        
        Args:
            n: Quantidade de alunos a retornar.
            
        Returns:
            Lista dos N melhores alunos por CR.
        """
        alunos = self.listar_alunos(ordenar_por_cr=True)
        return alunos[:n]