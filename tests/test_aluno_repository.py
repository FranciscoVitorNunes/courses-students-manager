import pytest
from repositories.aluno_repository import AlunoRepository
from models.aluno import Aluno

@pytest.fixture
def repo():
    # Cria um repositório novo para cada teste
    return AlunoRepository()

@pytest.fixture
def aluno_exemplo():
    return Aluno(matricula="20230001", nome="João da Silva", email="joao@email.com")

def test_salvar_e_buscar_aluno(repo, aluno_exemplo):
    repo.salvar(aluno_exemplo)
    aluno = repo.buscar_por_matricula("20230001")
    assert aluno is not None
    assert aluno.matricula == "20230001"
    assert aluno.nome == "João da Silva"
    assert aluno.email == "joao@email.com"

def test_listar_alunos(repo):
    alunos = repo.listar()
    assert isinstance(alunos, list)
    assert any(a.matricula == "20230001" for a in alunos)

def test_atualizar_aluno(repo, aluno_exemplo):
    aluno_exemplo.nome = "João Atualizado"
    aluno_exemplo.email = "novo@email.com"
    repo.atualizar(aluno_exemplo)
    aluno = repo.buscar_por_matricula("20230001")
    assert aluno.nome == "João Atualizado"
    assert aluno.email == "novo@email.com"

def test_deletar_aluno(repo):
    repo.deletar("20230001")
    aluno = repo.buscar_por_matricula("20230001")
    assert aluno is None
