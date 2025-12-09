from fastapi import HTTPException
from fastapi import APIRouter
from repositories.matricula_repository import MatriculaRepository
from schemas.matricula_schema import MatriculaSchema, CreateMatriculaSchema, UpdateTurmaSchema
from models.turma import Turma

router = APIRouter(prefix="/turmas", tags=["Turmas"])
service = MatriculaRepository()

@router.get("/{id}", response_model=MatriculaSchema)
def buscar(id: int):
    matricula = service.get_by_id(id)
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    return matricula