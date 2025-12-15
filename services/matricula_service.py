# services/matricula_service.py
from typing import List, Optional, Dict, Any, Tuple
from models.matricula import Matricula
from models.aluno import Aluno
from models.turma import Turma
from repositories.matricula_repository import MatriculaRepository
from repositories.aluno_repository import AlunoRepository
from repositories.turma_repository import TurmaRepository
from repositories.curso_repository import CursoRepository
from schemas.matricula_schema import MatriculaCreateSchema, UpdateMatriculaSchema
from config.settings import Settings
from services.aluno_service import AlunoService
from services.turma_service import TurmaService
from services.curso_service import CursoService
from datetime import datetime


class MatriculaService:
    """
    Serviço para gerenciamento de matrículas.
    Inclui validações de pré-requisitos, choque de horário, vagas, etc.
    """
    
    def __init__(
            self,
            aluno_service: Optional[AlunoService] = None,
            turma_service: Optional[TurmaService] = None,
            curso_service: Optional[CursoService] = None
            ):
        self.repository = MatriculaRepository()
        self.aluno_repo = AlunoRepository()
        self.turma_repo = TurmaRepository()
        self.curso_repo = CursoRepository()
        self.aluno_service = aluno_service or AlunoService()
        self.turma_service = turma_service or TurmaService()
        self.curso_service = curso_service or CursoService()
        self.settings = Settings()
    
    def criar_matricula(self, matricula_data: MatriculaCreateSchema) -> Dict[str, Any]:
        """
        Cria uma nova matrícula com todas as validações.
        
        Args:
            matricula_data: Dados da matrícula a ser criada.
            
        Returns:
            Dict com resultado da matrícula.
            
        Raises:
            ValueError: Se alguma validação falhar.
        """
        aluno_matricula = matricula_data.aluno_matricula
        turma_id = matricula_data.turma_id
        
        print(f"🔍 MATRICULA_SERVICE.criar_matricula: aluno={aluno_matricula}, turma={turma_id}")
        print(f"🔍 MATRICULA_SERVICE: Tipo de turma_id: {type(turma_id)}, Valor: '{turma_id}'")
        
        # 1. Verificar se aluno existe
        aluno = self.aluno_service.buscar_aluno(aluno_matricula)
        if not aluno:
            print(f"❌ MATRICULA_SERVICE: Aluno {aluno_matricula} não encontrado")
            raise ValueError(f"Aluno {aluno_matricula} não encontrado.")
        
        # 2. Verificar se turma existe
        print(f"🔍 MATRICULA_SERVICE: Buscando turma com turma_service.buscar_turma('{turma_id}')")
        turma = self.turma_service.buscar_turma(turma_id)
        
        if not turma:
            print(f"❌ MATRICULA_SERVICE: Turma {turma_id} não encontrada pelo turma_service")
            # Verificar se existe direto no repository
            from repositories.turma_repository import TurmaRepository
            turma_repo = TurmaRepository()
            turma_dict = turma_repo.get_by_id(turma_id)
            print(f"🔍 MATRICULA_SERVICE: Verificação direta no repository: {turma_dict}")
            raise ValueError(f"Turma {turma_id} não encontrada.")
        
        print(f"✅ MATRICULA_SERVICE: Turma encontrada: {turma.id}")
        
        # 3. Verificar se já está matriculado
        if self.repository.existe_matricula(aluno_matricula, turma_id):
            raise ValueError(f"Aluno já está matriculado na turma {turma_id}.")
        
        # 4. Validar matrícula (pré-requisitos, choque de horário, vagas, etc.)
        validacao = self.validar_matricula(aluno_matricula, turma_id)
        if not validacao['valida']:
            raise ValueError(f"Matrícula não permitida: {validacao['mensagem']}")
        
        # 5. Verificar limite de turmas por aluno (se configurado)
        if self.settings.max_turmas_por_aluno > 0:
            matriculas_ativas = self.repository.count_matriculas_por_aluno(aluno_matricula, turma.periodo)
            if matriculas_ativas >= self.settings.max_turmas_por_aluno:
                raise ValueError(
                    f"Aluno já atingiu o limite de {self.settings.max_turmas_por_aluno} "
                    f"turmas no período {turma.periodo}."
                )
        
        # 6. Criar matrícula no banco
        dados_matricula = {
            "aluno_matricula": aluno_matricula,
            "turma_id": turma_id,
            "situacao": Matricula.SITUACAO_CURSANDO
        }
        
        matricula_id = self.repository.create(dados_matricula)
        
        # 7. Criar objeto Matricula
        matricula_obj = Matricula(
            id=matricula_id,
            aluno=aluno,
            turma=turma,
            situacao=Matricula.SITUACAO_CURSANDO
        )
        
        return {
            "message": "Matrícula criada com sucesso!",
            "matricula": matricula_obj.to_dict(),
            "valida": True
        }
    
    def validar_matricula(self, aluno_matricula: str, turma_id: str) -> Dict[str, Any]:
        """
        Valida se um aluno pode se matricular em uma turma.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            turma_id: ID da turma.
            
        Returns:
            Dict com resultado da validação.
        """
        resultado = {
            "valida": False,
            "mensagem": "",
            "erros": []
        }
        
        # 1. Verificar se aluno existe
        aluno = self.aluno_service.buscar_aluno(aluno_matricula)
        if not aluno:
            resultado["erros"].append("Aluno não encontrado")
            resultado["mensagem"] = "Aluno não encontrado"
            return resultado
        
        # 2. Verificar se turma existe e está aberta
        turma = self.turma_service.buscar_turma(turma_id)
        if not turma:
            resultado["erros"].append("Turma não encontrada")
            resultado["mensagem"] = "Turma não encontrada"
            return resultado
        
        if not turma.esta_aberta_para_matricula():
            resultado["erros"].append("Turma não está aberta para matrícula")
            resultado["mensagem"] = f"Turma não está aberta para matrícula (status: {turma.status})"
            return resultado
        
        # 3. Verificar vagas disponíveis
        vagas_disponiveis = turma.vagas_disponiveis()
        if vagas_disponiveis <= 0:
            resultado["erros"].append("Turma sem vagas disponíveis")
            resultado["mensagem"] = "Turma sem vagas disponíveis"
            return resultado
        
        # 4. Verificar pré-requisitos do curso
        curso = turma.curso
        cursos_aprovados = aluno.get_cursos_aprovados()
        prerequisitos_faltantes = curso.get_prerequisitos_faltantes(cursos_aprovados)
        
        if prerequisitos_faltantes:
            resultado["erros"].append(f"Pré-requisitos não atendidos: {', '.join(prerequisitos_faltantes)}")
            resultado["mensagem"] = f"Pré-requisitos não atendidos: {', '.join(prerequisitos_faltantes)}"
            resultado["prerequisitos_faltantes"] = prerequisitos_faltantes
            return resultado
        
        # 5. Verificar choque de horário
        # Obter horários das turmas atuais do aluno no mesmo período
        horarios_aluno = self.repository.get_horarios_do_aluno(aluno_matricula, turma.periodo)
        
        for dia, intervalos in horarios_aluno.items():
            for intervalo in intervalos:
                # Verificar se há choque com algum horário da nova turma
                if dia in turma.horarios:
                    # Implementar lógica de detecção de choque
                    if self._verificar_choque_horario(intervalo, turma.horarios[dia]):
                        resultado["erros"].append(f"Choque de horário no dia {dia}")
                        resultado["mensagem"] = f"Choque de horário detectado no dia {dia}"
                        return resultado
        
        # 6. Verificar se já está matriculado no mesmo curso no período
        matriculas_aluno = self.repository.listar_matriculas_por_aluno(aluno_matricula)
        for matricula in matriculas_aluno:
            if (matricula['turma_periodo'] == turma.periodo and 
                matricula['curso_codigo'] == curso.codigo):
                resultado["erros"].append(f"Já matriculado no curso {curso.codigo} no período {turma.periodo}")
                resultado["mensagem"] = f"Já matriculado no curso {curso.codigo} no período {turma.periodo}"
                return resultado
        
        resultado["valida"] = True
        resultado["mensagem"] = "Matrícula válida"
        return resultado
    
    def _verificar_choque_horario(self, intervalo1: str, intervalo2: str) -> bool:
        """
        Verifica se há choque entre dois intervalos de horário.
        
        Args:
            intervalo1: Intervalo no formato "HH:MM-HH:MM".
            intervalo2: Intervalo no formato "HH:MM-HH:MM".
            
        Returns:
            True se houver choque, False caso contrário.
        """
        def parse_intervalo(intervalo: str) -> Tuple[datetime.time, datetime.time]:
            inicio_str, fim_str = intervalo.split('-')
            inicio = datetime.strptime(inicio_str, "%H:%M").time()
            fim = datetime.strptime(fim_str, "%H:%M").time()
            return inicio, fim
        
        inicio1, fim1 = parse_intervalo(intervalo1)
        inicio2, fim2 = parse_intervalo(intervalo2)
        
        # Choque ocorre quando os intervalos se sobrepõem
        return not (fim1 <= inicio2 or fim2 <= inicio1)
    
    def buscar_matricula(self, matricula_id: int) -> Optional[Matricula]:
        """
        Busca uma matrícula pelo ID.
        
        Args:
            matricula_id: ID da matrícula.
            
        Returns:
            Objeto Matricula se encontrado, None caso contrário.
        """
        matricula_data = self.repository.get_by_id(matricula_id)
        if not matricula_data:
            return None
        
        aluno = self.aluno_service.buscar_aluno(matricula_data['aluno_matricula'])
        turma = self.turma_service.buscar_turma(matricula_data['turma_id'])
        
        if not aluno or not turma:
            return None
        
        return Matricula(
            id=matricula_data['id'],
            aluno=aluno,
            turma=turma,
            nota=matricula_data.get('nota'),
            frequencia=matricula_data.get('frequencia'),
            situacao=matricula_data['situacao'],
            data_matricula=matricula_data['data_matricula']
        )
    
    def listar_matriculas(self, turma_id: Optional[str] = None, 
                         aluno_matricula: Optional[str] = None) -> List[Matricula]:
        """
        Lista matrículas com filtros opcionais.
        
        Args:
            turma_id: Filtrar por turma.
            aluno_matricula: Filtrar por aluno.
            
        Returns:
            Lista de objetos Matricula.
        """
        if turma_id:
            matriculas_data = self.repository.listar_matriculas_por_turma(turma_id)
        elif aluno_matricula:
            matriculas_data = self.repository.listar_matriculas_por_aluno(aluno_matricula)
        else:
            matriculas_data = self.repository.get_all()
        
        matriculas = []
        for matricula_data in matriculas_data:
            aluno = self.aluno_service.buscar_aluno(matricula_data['aluno_matricula'])
            turma = self.turma_service.buscar_turma(matricula_data['turma_id'])
            
            if aluno and turma:
                matricula = Matricula(
                    id=matricula_data['id'],
                    aluno=aluno,
                    turma=turma,
                    nota=matricula_data.get('nota'),
                    frequencia=matricula_data.get('frequencia'),
                    situacao=matricula_data['situacao'],
                    data_matricula=matricula_data.get('data_matricula')
                )
                matriculas.append(matricula)
        
        return matriculas
    
    def atualizar_matricula(self, matricula_id: int, 
                           dados_atualizacao: UpdateMatriculaSchema) -> Optional[Matricula]:
        """
        Atualiza uma matrícula.
        
        Args:
            matricula_id: ID da matrícula.
            dados_atualizacao: Dados a atualizar.
            
        Returns:
            Matricula atualizada se encontrada, None caso contrário.
        """
        dados_dict = dados_atualizacao.model_dump(exclude_none=True)
        
        atualizado = self.repository.update(matricula_id, dados_dict)
        if not atualizado:
            return None
        
        return self.buscar_matricula(matricula_id)
    
    def deletar_matricula(self, matricula_id: int) -> bool:
        """
        Deleta uma matrícula.
        
        Args:
            matricula_id: ID da matrícula.
            
        Returns:
            True se deletada, False se não encontrada.
        """
        try:
            return self.repository.delete(matricula_id)
        except Exception as e:
            raise ValueError(f"Erro ao deletar matrícula: {str(e)}")
    
    def lancar_nota_frequencia(self, matricula_id: int, nota: float, frequencia: float) -> Dict[str, Any]:
        """
        Lança nota e frequência para uma matrícula.
        
        Args:
            matricula_id: ID da matrícula.
            nota: Nota do aluno (0-10).
            frequencia: Frequência do aluno (0-100).
            
        Returns:
            Dict com resultado da operação.
        """
        # Validar nota e frequência
        if not 0 <= nota <= 10:
            raise ValueError("Nota deve estar entre 0 e 10.")
        if not 0 <= frequencia <= 100:
            raise ValueError("Frequência deve estar entre 0 e 100.")
        
        # Buscar matrícula
        matricula = self.buscar_matricula(matricula_id)
        if not matricula:
            raise ValueError(f"Matrícula {matricula_id} não encontrada.")
        
        # Verificar se matrícula está ativa
        if not matricula.ativa:
            raise ValueError("Não é possível lançar avaliação para matrícula não ativa.")
        
        # Atualizar no banco
        atualizado = self.repository.atualizar_nota_frequencia(matricula_id, nota, frequencia)
        if not atualizado:
            raise ValueError("Erro ao lançar nota/frequência.")
        
        # Atualizar objeto
        matricula.nota = nota
        matricula.frequencia = frequencia
        
        return {
            "message": "Nota e frequência lançadas com sucesso!",
            "matricula": matricula.to_dict()
        }
    
    def trancar_matricula(self, matricula_id: int) -> Dict[str, Any]:
        """
        Tranca uma matrícula.
        
        Args:
            matricula_id: ID da matrícula.
            
        Returns:
            Dict com resultado da operação.
        """
        matricula = self.buscar_matricula(matricula_id)
        if not matricula:
            raise ValueError(f"Matrícula {matricula_id} não encontrada.")
        
        # Verificar se pode trancar
        if not self.settings.pode_trancar():
            raise ValueError("Data limite para trancamento já passou.")
        
        if not matricula.ativa:
            raise ValueError("Não é possível trancar uma matrícula já finalizada.")
        
        # Trancar no banco
        dados = {"situacao": Matricula.SITUACAO_TRANCADA}
        atualizado = self.repository.update(matricula_id, dados)
        if not atualizado:
            raise ValueError("Erro ao trancar matrícula.")
        
        # Atualizar objeto
        matricula.trancar()
        
        return {
            "message": "Matrícula trancada com sucesso!",
            "matricula": matricula.to_dict()
        }
    
    def obter_estatisticas_turma(self, turma_id: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de uma turma.
        
        Args:
            turma_id: ID da turma.
            
        Returns:
            Dict com estatísticas da turma.
        """
        turma = self.turma_service.buscar_turma(turma_id)
        if not turma:
            raise ValueError(f"Turma {turma_id} não encontrada.")
        
        matriculas = self.listar_matriculas(turma_id=turma_id)
        
        # Estatísticas básicas
        total_matriculas = len(matriculas)
        matriculas_ativas = sum(1 for m in matriculas if m.ativa)
        matriculas_concluidas = total_matriculas - matriculas_ativas
        
        # Distribuição de notas
        notas = [m.nota for m in matriculas if m.nota is not None]
        frequencias = [m.frequencia for m in matriculas if m.frequencia is not None]
        
        # Situações
        situacoes = {}
        for matricula in matriculas:
            situacao = matricula.situacao
            situacoes[situacao] = situacoes.get(situacao, 0) + 1
        
        # Taxa de aprovação
        aprovados = situacoes.get(Matricula.SITUACAO_APROVADO, 0)
        total_concluido = sum(count for situacao, count in situacoes.items() 
                             if situacao != Matricula.SITUACAO_CURSANDO)
        
        taxa_aprovacao = round((aprovados / total_concluido * 100), 2) if total_concluido > 0 else 0.0
        
        # Cálculos de notas
        media_notas = round(sum(notas) / len(notas), 2) if notas else None
        media_frequencias = round(sum(frequencias) / len(frequencias), 2) if frequencias else None
        
        return {
            'turma_id': turma_id,
            'turma_periodo': turma.periodo,
            'curso_codigo': turma.curso.codigo,
            'curso_nome': turma.curso.nome,
            'total_matriculas': total_matriculas,
            'matriculas_ativas': matriculas_ativas,
            'matriculas_concluidas': matriculas_concluidas,
            'situacoes': situacoes,
            'taxa_aprovacao': taxa_aprovacao,
            'media_notas': media_notas,
            'media_frequencias': media_frequencias,
            'alunos_em_risco': self._identificar_alunos_em_risco(matriculas)
        }
    
    def _identificar_alunos_em_risco(self, matriculas: List[Matricula]) -> List[Dict[str, Any]]:
        """
        Identifica alunos em risco (nota parcial < corte ou frequência < mínimo).
        
        Args:
            matriculas: Lista de matrículas.
            
        Returns:
            Lista de alunos em risco.
        """
        alunos_em_risco = []
        
        for matricula in matriculas:
            if matricula.ativa and matricula.nota is not None and matricula.frequencia is not None:
                nota_minima = self.settings.nota_minima_aprovacao
                frequencia_minima = self.settings.frequencia_minima
                
                if matricula.nota < nota_minima or matricula.frequencia < frequencia_minima:
                    alunos_em_risco.append({
                        'aluno_matricula': matricula.aluno.matricula,
                        'aluno_nome': matricula.aluno.nome,
                        'nota_atual': matricula.nota,
                        'frequencia_atual': matricula.frequencia,
                        'nota_minima': nota_minima,
                        'frequencia_minima': frequencia_minima,
                        'risco_nota': matricula.nota < nota_minima,
                        'risco_frequencia': matricula.frequencia < frequencia_minima
                    })
        
        return alunos_em_risco
    
    def gerar_relatorio_matriculas(self, periodo: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera relatório geral de matrículas.
        
        Args:
            periodo: Período específico (opcional).
            
        Returns:
            Dict com relatório de matrículas.
        """
        # Esta é uma implementação básica
        # Em uma implementação real, buscaria dados mais completos do banco
        
        return {
            'periodo': periodo or 'Todos',
            'total_matriculas': self._contar_matriculas(periodo),
            'matriculas_ativas': self._contar_matriculas_ativas(periodo),
            'taxa_conclusao': self._calcular_taxa_conclusao(periodo),
            'top_cursos': self._obter_top_cursos(periodo)
        }
    
    def _contar_matriculas(self, periodo: Optional[str] = None) -> int:
        """Conta total de matrículas."""
        # Implementação simplificada
        return len(self.listar_matriculas())
    
    def _contar_matriculas_ativas(self, periodo: Optional[str] = None) -> int:
        """Conta matrículas ativas."""
        matriculas = self.listar_matriculas()
        return sum(1 for m in matriculas if m.ativa)
    
    def _calcular_taxa_conclusao(self, periodo: Optional[str] = None) -> float:
        """Calcula taxa de conclusão."""
        matriculas = self.listar_matriculas()
        if not matriculas:
            return 0.0
        
        concluidas = sum(1 for m in matriculas if not m.ativa)
        return round((concluidas / len(matriculas)) * 100, 2)
    
    def _obter_top_cursos(self, periodo: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtém cursos com mais matrículas."""
        # Implementação simplificada
        return [
            {'curso_codigo': 'POO001', 'curso_nome': 'Programação OO', 'total_matriculas': 25},
            {'curso_codigo': 'BD001', 'curso_nome': 'Banco de Dados', 'total_matriculas': 20},
            {'curso_codigo': 'WEB001', 'curso_nome': 'Desenvolvimento Web', 'total_matriculas': 18}
        ]