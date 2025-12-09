from fastapi import HTTPException
from fastapi import APIRouter
from repositories.aluno_repository import AlunoRepository
from schemas.aluno_schema import AlunoSchema, UpdateAlunoSchema

router = APIRouter(prefix="/alunos", tags=["Alunos"])
service = AlunoRepository()

@router.get("/")
def listar():
    return service.listar()

@router.post("/")
def criar(aluno: AlunoSchema):
    try:
        service.salvar(aluno)
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao criar aluno")


@router.get("/{matricula}")
def buscar_por_matricula(matricula: str):
    aluno = service.buscar_por_matricula(matricula)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno

@router.delete("/{matricula}")
def deletar(matricula: str):
        service.deletar(matricula)

@router.patch("/{matricula}")
def atualizar(matricula: str, aluno: UpdateAlunoSchema):
    dados = aluno.model_dump(exclude_none=True)

    atualizado = service.atualizar(matricula, dados)

    if not atualizado:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado ou nada para atualizar"
        )

    return {"message": "Aluno atualizado parcialmente"}