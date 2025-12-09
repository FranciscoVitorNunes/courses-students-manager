from fastapi import HTTPException
from fastapi import APIRouter
from repositories.curso_repository import CursoRepository
from schemas.curso_schema import CursoSchema

router = APIRouter(prefix="/cursos", tags=["Cursos"])
service = CursoRepository()

@router.get("/")
def listar():
    return service.list_all()

@router.post("/")
def criar(curso: CursoSchema):
    try:
        service.create(curso)
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao criar curso")


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
def atualizar(matricula: str, aluno: CursoSchema):
    dados = aluno.model_dump(exclude_none=True)

    atualizado = service.atualizar(matricula, dados)

    if not atualizado:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado ou nada para atualizar"
        )

    return {"message": "Aluno atualizado parcialmente"}