from fastapi import HTTPException
from fastapi import APIRouter
from repositories.nota_repository import NotaRepository
from schemas.nota_frequencia_schema import NotaSchema, CreateNotaSchema

router = APIRouter(prefix="/notas", tags=["Notas"])
service = NotaRepository()

@router.get("/matricula/{matricula_id}", response_model=list[NotaSchema])
def listar_notas(matricula_id: int):
    return service.get_by_matricula(matricula_id)