from fastapi import HTTPException
from fastapi import APIRouter
from repositories.aluno_repository import AlunoRepository
from schemas.aluno_schema import AlunoSchema

router = APIRouter(prefix="/alunos", tags=["Alunos"])
service = AlunoRepository()

@router.get("/")
def listar():
    return service.listar()


@router.get("/{matricula}")
def buscar_por_matricula(matricula: str):
    aluno = service.buscar_por_matricula(matricula)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno