from fastapi import HTTPException
from fastapi import APIRouter
from repositories.matricula_repository import MatriculaRepository
from schemas.matricula_schema import MatriculaSchema, CreateMatriculaSchema

router = APIRouter(prefix="/matriculas", tags=["Matriculas"])
service = MatriculaRepository()

@router.get("/{id}", response_model=MatriculaSchema)
def buscar(id: int):
    matricula = service.get_by_id(id)
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    return matricula

@router.post("/", response_model=MatriculaSchema)
def criar(m: CreateMatriculaSchema):
    dados = m.model_dump()
    id = service.create(dados)
    return service.get_by_id(id)