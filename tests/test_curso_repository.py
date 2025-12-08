import pytest
from repositories.curso_repository import CursoRepository
from models.curso import Curso

repo = CursoRepository()

def test_salvar_curso():
    curso = Curso("BD001", "Banco de Dados", 80)
    repo.salvar_curso(curso)

    encontrado = repo.buscar_curso_por_codigo("BD001")
    assert encontrado is not None
    assert encontrado.nome == "Banco de Dados"

def test_atualizar_curso():
    curso = Curso("BD001", "Banco de Dados Avançado", 100)
    curso.ementa = "Nova ementa"

    repo.atualizar_curso(curso)
    atualizado = repo.buscar_curso_por_codigo("BD001")

    assert atualizado.nome == "Banco de Dados Avançado"

def test_deletar_curso():
    repo.deletar_curso("BD001")
    encontrado = repo.buscar_curso_por_codigo("BD001")

    assert encontrado is None

def test_adicionar_prerequisito():
    curso_bd = Curso("BD001", "Banco de Dados", 80)
    curso_algo = Curso("ALGO001", "Algoritmos", 60)

    repo.salvar_curso(curso_bd)
    repo.salvar_curso(curso_algo)

    repo.adiconar_prerequisitos("BD001", "ALGO001")

    prereqs = repo.buscar_prerequisitos("BD001")

    assert "ALGO001" in prereqs
