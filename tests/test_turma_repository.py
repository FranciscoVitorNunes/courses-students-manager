from repositories.turma_repository import TurmaRepository
from repositories.curso_repository import CursoRepository
from models.curso import Curso
from models.turma import Turma

repo_turma = TurmaRepository()
repo_curso = CursoRepository()

def test_buscar_turma_com_horarios():
    curso = Curso('ENG001', 'Engenharia de Software', 80)
    repo_curso.salvar_curso(curso)

    turma = Turma(
        id="T123",
        periodo="2025.1",
        vagas=30,
        horarios={"SEG": "08-10"},
        curso=curso
    )
    
    repo_turma.salvar(turma)

    resultado = repo_turma.buscar_por_id("T123")

    assert resultado is not None
    assert resultado["horarios"]["SEG"] == "08-10"
