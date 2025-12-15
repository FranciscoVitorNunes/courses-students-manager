# services/turma_service.py
from typing import List, Optional, Dict, Any
from models.turma import Turma
from models.curso import Curso
from repositories.turma_repository import TurmaRepository
from repositories.curso_repository import CursoRepository
from schemas.turma_schema import TurmaSchema, UpdateTurmaSchema
from services.curso_service import CursoService


class TurmaService:
    def __init__(self):
        self.repository = TurmaRepository()
        self.curso_repository = CursoRepository()
        self.curso_service = CursoService()
    
    def criar_turma(self, turma_data: TurmaSchema) -> Turma:
        """
        Cria uma nova turma.
        
        Args:
            turma_data: Dados da turma a ser criada.
            
        Returns:
            Objeto Turma criado.
            
        Raises:
            ValueError: Se o ID já existir, curso não existir ou dados forem inválidos.
        """
        # Verificar se turma já existe
        turma_existente = self.repository.get_by_id(turma_data.id)
        if turma_existente:
            raise ValueError(f"Turma com ID {turma_data.id} já existe.")
        
        # Buscar curso
        curso = self.curso_service.buscar_curso(turma_data.curso, incluir_prerequisitos=False)
        if not curso:
            raise ValueError(f"Curso {turma_data.curso} não encontrado.")
        
        # Criar objeto Turma
        turma = Turma(
            id=turma_data.id,
            periodo=turma_data.periodo,
            horarios=turma_data.horarios,
            vagas=turma_data.vagas,
            curso=curso,
            local=getattr(turma_data, 'local', None)
        )
        
        # Salvar no banco via repository
        self.repository.create(turma)
        
        return turma
    
    def buscar_turma(self, turma_id: str, incluir_detalhes: bool = True) -> Optional[Turma]:
        """
        Busca uma turma pelo ID.
        
        Args:
            turma_id: ID da turma.
            incluir_detalhes: Se True, inclui detalhes completos do curso.
            
        Returns:
            Objeto Turma se encontrado, None caso contrário.
        """
        # Buscar turma no banco
        turma_dict = self.repository.get_by_id(turma_id)
        if not turma_dict:
            return None
        
        # Buscar curso
        curso_codigo = turma_dict.get('curso_codigo')
        if not curso_codigo:
            return None
        
        curso = self.curso_service.buscar_curso(curso_codigo, incluir_prerequisitos=False)
        if not curso:
            return None
        
        # Criar objeto Turma
        turma = Turma(
            id=turma_dict['id'],
            periodo=turma_dict['periodo'],
            horarios=turma_dict['horarios'],
            vagas=turma_dict['vagas'],
            curso=curso,
            local=turma_dict.get('local')
        )
        
        # Atualizar status baseado nas matrículas (se houver)
        if 'matriculas' in turma_dict:
            for matricula in turma_dict['matriculas']:
                turma.adicionar_matricula(matricula)
        
        return turma
    
    def listar_turmas(self, periodo: Optional[str] = None, 
                     curso_codigo: Optional[str] = None,
                     status: Optional[str] = None) -> List[Turma]:
        """
        Lista turmas com filtros opcionais.
        
        Args:
            periodo: Filtrar por período (ex: "2025.1").
            curso_codigo: Filtrar por código do curso.
            status: Filtrar por status ("aberta", "fechada", "esgotada").
            
        Returns:
            Lista de objetos Turma.
        """
        # Buscar todas as turmas do banco
        turmas_dict = self.repository.list_all()
        
        turmas = []
        for turma_dict in turmas_dict:
            # Aplicar filtros
            if periodo and turma_dict['periodo'] != periodo:
                continue
            
            if curso_codigo and turma_dict['curso_codigo'] != curso_codigo:
                continue
            
            # Buscar curso
            curso_codigo_atual = turma_dict.get('curso_codigo')
            if not curso_codigo_atual:
                continue
            
            curso = self.curso_service.buscar_curso(curso_codigo_atual, incluir_prerequisitos=False)
            if not curso:
                continue
            
            # Criar objeto Turma
            turma = Turma(
                id=turma_dict['id'],
                periodo=turma_dict['periodo'],
                horarios=turma_dict['horarios'],
                vagas=turma_dict['vagas'],
                curso=curso,
                local=turma_dict.get('local')
            )
            
            # Aplicar filtro de status (após criar o objeto para calcular vagas)
            if status:
                if status == "aberta" and not turma.esta_aberta_para_matricula():
                    continue
                elif status == "esgotada" and turma.status != turma.STATUS_ESGOTADA:
                    continue
                elif status == "fechada" and turma.status != turma.STATUS_FECHADA:
                    continue
            
            turmas.append(turma)
        
        return turmas
    
    def atualizar_turma(self, turma_id: str, dados_atualizacao: UpdateTurmaSchema) -> Optional[Turma]:
        """
        Atualiza parcialmente uma turma.
        
        Args:
            turma_id: ID da turma a atualizar.
            dados_atualizacao: Dados a serem atualizados.
            
        Returns:
            Turma atualizada se encontrada, None caso contrário.
        """
        # Converter para dicionário excluindo valores None
        dados_dict = dados_atualizacao.model_dump(exclude_none=True)
        
        # Atualizar no repository
        atualizado = self.repository.update(turma_id, dados_dict)
        if not atualizado:
            return None
        
        # Buscar turma atualizada
        return self.buscar_turma(turma_id)
    
    def deletar_turma(self, turma_id: str) -> bool:
        """
        Deleta uma turma.
        
        Args:
            turma_id: ID da turma a deletar.
            
        Returns:
            True se deletada, False se não encontrada.
        """
        try:
            # Verificar se há matrículas na turma
            turma = self.buscar_turma(turma_id)
            if turma and len(turma) > 0:
                raise ValueError(
                    f"Não é possível deletar a turma {turma_id}. "
                    f"Há {len(turma)} matrículas registradas."
                )
            
            deletado = self.repository.delete(turma_id)
            return deletado
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Erro ao deletar turma: {str(e)}")
    
    def abrir_turma(self, turma_id: str) -> bool:
        """
        Abre uma turma para matrículas.
        
        Args:
            turma_id: ID da turma.
            
        Returns:
            True se aberta, False se não encontrada.
        """
        turma = self.buscar_turma(turma_id)
        if not turma:
            return False
        
        turma.abrir()
        
        # Atualizar no banco se necessário
        # (Neste caso, o status é calculado dinamicamente, mas podemos persistir se necessário)
        return True
    
    def fechar_turma(self, turma_id: str) -> bool:
        """
        Fecha uma turma para matrículas.
        
        Args:
            turma_id: ID da turma.
            
        Returns:
            True se fechada, False se não encontrada.
        """
        turma = self.buscar_turma(turma_id)
        if not turma:
            return False
        
        turma.fechar()
        return True
    
    def verificar_choque_horario(self, turma_id: str, horarios: Dict[str, str]) -> bool:
        """
        Verifica se há choque de horário com uma turma.
        
        Args:
            turma_id: ID da turma.
            horarios: Horários para verificar choque.
            
        Returns:
            True se houver choque, False caso contrário.
        """
        turma = self.buscar_turma(turma_id)
        if not turma:
            raise ValueError(f"Turma {turma_id} não encontrada.")
        
        return turma.verificar_choque(horarios)
    
    def verificar_disponibilidade_vagas(self, turma_id: str) -> Dict[str, Any]:
        """
        Verifica disponibilidade de vagas em uma turma.
        
        Args:
            turma_id: ID da turma.
            
        Returns:
            Dicionário com informações de vagas.
        """
        turma = self.buscar_turma(turma_id)
        if not turma:
            raise ValueError(f"Turma {turma_id} não encontrada.")
        
        return {
            'turma_id': turma_id,
            'vagas_total': turma.vagas,
            'vagas_ocupadas': turma.vagas_ocupadas(),
            'vagas_disponiveis': turma.vagas_disponiveis(),
            'esta_aberta': turma.esta_aberta_para_matricula(),
            'status': turma.status
        }
    
    def buscar_turmas_por_curso(self, curso_codigo: str, periodo: Optional[str] = None) -> List[Turma]:
        """
        Busca turmas de um curso específico.
        
        Args:
            curso_codigo: Código do curso.
            periodo: Período específico (opcional).
            
        Returns:
            Lista de turmas do curso.
        """
        return self.listar_turmas(periodo=periodo, curso_codigo=curso_codigo)
    
    def buscar_turmas_abertas(self, periodo: Optional[str] = None) -> List[Turma]:
        """
        Busca turmas abertas para matrícula.
        
        Args:
            periodo: Período específico (opcional).
            
        Returns:
            Lista de turmas abertas.
        """
        turmas = self.listar_turmas(periodo=periodo)
        return [turma for turma in turmas if turma.esta_aberta_para_matricula()]
    
    def get_estatisticas_periodo(self, periodo: str) -> Dict[str, Any]:
        """
        Obtém estatísticas das turmas de um período.
        
        Args:
            periodo: Período letivo.
            
        Returns:
            Dicionário com estatísticas.
        """
        turmas = self.listar_turmas(periodo=periodo)
        
        total_turmas = len(turmas)
        turmas_abertas = sum(1 for t in turmas if t.status == Turma.STATUS_ABERTA)
        turmas_fechadas = sum(1 for t in turmas if t.status == Turma.STATUS_FECHADA)
        turmas_esgotadas = sum(1 for t in turmas if t.status == Turma.STATUS_ESGOTADA)
        
        total_vagas = sum(t.vagas for t in turmas)
        vagas_ocupadas = sum(t.vagas_ocupadas() for t in turmas)
        vagas_disponiveis = sum(t.vagas_disponiveis() for t in turmas)
        
        taxa_ocupacao = round((vagas_ocupadas / total_vagas) * 100, 2) if total_vagas > 0 else 0.0
        
        return {
            'periodo': periodo,
            'total_turmas': total_turmas,
            'turmas_abertas': turmas_abertas,
            'turmas_fechadas': turmas_fechadas,
            'turmas_esgotadas': turmas_esgotadas,
            'total_vagas': total_vagas,
            'vagas_ocupadas': vagas_ocupadas,
            'vagas_disponiveis': vagas_disponiveis,
            'taxa_ocupacao': taxa_ocupacao
        }