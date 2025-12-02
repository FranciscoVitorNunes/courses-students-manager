from models.matricula import Matricula
from models.turma import Turma

class MatriculaService:
    def __init__(self, aluno_repo, curso_repo, turma_repo, matricula_repo):
        self.aluno_repo = aluno_repo
        self.curso_repo = curso_repo
        self.turma_repo = turma_repo
        self.matricula_repo = matricula_repo

    class ValidacaoError(Exception):
        """Exceção customizada para erros de negócio no serviço."""
        pass

    def matricular(self, aluno_matricula: str, turma_id: str):
        aluno = self.aluno_repo.buscar_por_matricula(aluno_matricula)
        dados = self.turma_repo.buscar_por_id(turma_id)
        curso = self.curso_repo.buscar_curso_por_codigo(dados['curso_codigo'])

        turma = Turma(
            id=dados["id"],
            periodo=dados["periodo"],
            horarios=dados["horarios"],
            vagas=dados["vagas"],
            curso=curso
        )


        self._check_entidades_existem(aluno,turma)
        self._check_aluno_ja_matriculado(aluno, turma)
        self._check_turma_cheia(turma)
        self._check_atende_prerequisitos(aluno, turma)
        self._check_choque_de_horario(aluno,turma)

        matricula = Matricula(aluno,turma)
        self.matricula_repo.salvar(matricula)
        return matricula
    
    def _check_entidades_existem(self, aluno, turma):
        if aluno is None:
            raise self.ValidacaoError("Aluno não encontrado.")
        if turma is None:
            raise self.ValidacaoError("Turma não encontrada.")
        
    def _check_aluno_ja_matriculado(self, aluno, turma):
        if self.matricula_repo.buscar_por_aluno_e_turma(aluno.matricula, turma.id):
            raise self.ValidacaoError("Aluno já está matriculado nessa turma.")
        
    def _check_turma_cheia(self, turma):
        vagas_ocupadas = self.matricula_repo.contar_matriculas_por_turma(turma.id)
        
        if vagas_ocupadas >= turma.vagas:
            raise self.ValidacaoError(f"Turma {turma.id} não possui vagas disponíveis.")

    def _check_atende_prerequisitos(self, aluno, turma):
        curso = self.curso_repo.buscar_curso_por_codigo(turma.curso.codigo)
        prerequisitos = self.curso_repo.buscar_prerequisitos(curso.codigo) 

        historico = aluno.get_historico()  # lista de dicts com 'disciplina' e 'situacao'
        cursos_aprovadas = {h['codigo_curso'] for h in historico if h['situacao'] == 'APROVADO'}

        for prereq in prerequisitos:
            if prereq not in cursos_aprovadas:
                raise self.ValidacaoError(f"Pré-requisito não atendido: {prereq}")
        
    def _check_choque_de_horario(self, aluno, turma):
        id_das_turmas = self.matricula_repo.listar_turmas_por_aluno(aluno.matricula)
        turmas_aluno = [self.turma_repo.buscar_por_id(id) for id in id_das_turmas]
        for t in turmas_aluno:
            if t.verificar_choque(turma.horarios):
                raise self.ValidacaoError(f"Choque de horário com a turma: {t.id}")