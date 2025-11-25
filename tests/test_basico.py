from models.aluno import Aluno
from models.curso import Curso
from models.matricula import Matricula
from models.turma import Turma

def test_criacao_aluno():
    aluno = Aluno("001", "Jayr Alencar", "jayr@prof.ufca.edu.br")
    assert aluno.matricula == "001"
    assert aluno.nome == "Jayr Alencar"
    assert aluno.email == "jayr@prof.ufca.edu.br"
    assert aluno.cr == 0.0

def test_criacao_curso_e_prerequistos():
    curso2 = Curso("INP001", " Introdução a Programação", 64, "portugol, estrutura de repetição...etc")
    curso = Curso("POO006", "Programação orientada a objetos", 64, "classes, objetos... etc")
    curso.adicionar_prerequisito("INP001")
    assert "INP001" in curso.prerequisitos
    # assert curso.adicionar_prerequisito("POO006") -> teste erro

def test_criacao_turma():
    curso = Curso("POO006", "Programação orientada a objetos", 64, "classes, objetos... etc")
    turma = Turma("TU1", "2026.1", { "TER":"18-22" }, 50, curso)

    assert turma.id == "TU1"
    assert turma.periodo == "2026.1"
    assert turma.vagas == 50
    assert turma.curso == curso

def test_criar_matricula_e_adicionar_avaliacao():
    curso = Curso("POO006", "Programação Orientada a Objetos", 64, "classes, objetos... etc")
    turma = Turma("TU1", "2026.1", {"TER":"18-22"}, 50, curso)
    aluno = Aluno("2025001", "Jayr Alencar", "jayr@prof.ufca.edu.br")
    matricula = Matricula(aluno, turma)

    matricula.lancar_avaliacao(9.5, 78)

    assert matricula.frequencia == 78
    assert matricula.nota == 9.5
    assert matricula.ativa is False