from fastapi import HTTPException
from fastapi import APIRouter
from repositories.curso_repository import CursoRepository
from schemas.curso_schema import CursoSchema, UpdateCursoSchema

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


@router.get("/{codigo}")
def buscar_por_codigo(codigo: str):
    curso = service.get_by_codigo(codigo)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    return curso

@router.delete("/{codigo}")
def deletar(codigo: str):
    service.delete(codigo)

@router.patch("/{codigo}")
def atualizar(codigo: str, curso: UpdateCursoSchema):
    dados = curso.model_dump(exclude_none=True)

    atualizado = service.update(codigo, dados)

    if not atualizado:
        raise HTTPException(
            status_code=404,
            detail="Curso não encontrado ou nada para atualizar"
        )

    return {"message": "Curso atualizado parcialmente"}