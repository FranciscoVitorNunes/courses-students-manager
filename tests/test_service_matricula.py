import pytest
from repositories.aluno_repository import AlunoRepository
from repositories.curso_repository import CursoRepository
from repositories.maticula_repository import MatriculaRepository
from repositories.turma_repository import TurmaRepository
from services.matricula_service import MatriculaService

from models.curso import Curso
from models.turma import Turma
from models.aluno import Aluno

repo_aluno = AlunoRepository()
repo_turma = TurmaRepository()
repo_mat = MatriculaRepository()
repo_curso = CursoRepository()

def test_matricular_integracao(): 
    # Criar e salvar entidades (acessa o banco)
    curso = Curso('POO001', 'Programação Orientada a Objetos', 64)
    repo_curso.salvar_curso(curso) 

    turma = Turma(id="TU1", periodo="2026.1", horarios={ "TER":"18-22" }, vagas=50, curso=curso)
    repo_turma.salvar(turma)

    aluno = Aluno(matricula='2025001', nome='Vitor', email='vitor@gmail.com')
    repo_aluno.salvar(aluno)

    # Injetar na ordem CORRETA
    service = MatriculaService(repo_aluno, repo_curso, repo_turma, repo_mat)

    # Executar a operação principal
    matricula = service.matricular("2025001", "TU1")

    # Assert: verificar se a matrícula foi salva e tem os dados corretos
    # Idealmente, você buscaria a matrícula pelo repo_mat e verificaria
    assert matricula is not None
    assert matricula.aluno.matricula == '2025001'
    
