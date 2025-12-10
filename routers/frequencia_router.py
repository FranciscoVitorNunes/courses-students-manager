from fastapi import HTTPException
from fastapi import APIRouter
from repositories.frequencia_repository import FrequenciaRepository
from schemas.nota_frequencia_schema import FrequenciaSchema, CreateFrequenciaSchema

router = APIRouter(prefix="/frequencias", tags=["Frequencias"])
service = FrequenciaRepository()

@router.post("/", response_model=FrequenciaSchema)
def criar_frequencia(f: CreateFrequenciaSchema):
    id = service.create(f.model_dump())
    return service.get_by_matricula(f.matricula_id)[-1]

@router.get("/matricula/{matricula_id}", response_model=list[FrequenciaSchema])
def listar_frequencias(matricula_id: int):
    return service.get_by_matricula(matricula_id)