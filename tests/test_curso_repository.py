import pytest
from repositories.curso_repository import CursoRepository
from models.curso import Curso

@pytest.fixture
def repo():
    # Cria um repositório novo para cada teste
    return CursoRepository()

@pytest.fixture
def curso_exemplo():
    return Curso("POO001", "Programação Orientada a Objeto", 64, "ementa tests...")

def test_salvar_e_buscar_curso(repo, curso_exemplo):
    repo.salvar_curso(curso_exemplo)
    curso = repo.buscar_curso_por_codigo("POO001")
    assert curso is not None
    assert curso.codigo == "POO001"


#def test_listar_listar(repo):
#    cursos = repo.listar()
#    assert isinstance(cursos, list)
#    assert any(a.codigo == "POO001" for a in cursos)

def test_atualizar_curso(repo, curso_exemplo):
    curso_exemplo.nome = "POO abreviação"
    curso_exemplo.carga_horaria = 45
    repo.atualizar_curso(curso_exemplo)
    curso = repo.buscar_curso_por_codigo("POO001")
    assert curso.nome == "POO abreviação"

def test_deletar_curso(repo):
    repo.deletar_curso("POO001")
    curso = repo.buscar_curso_por_codigo("POO001")
    assert curso is None
