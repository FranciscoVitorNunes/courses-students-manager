from fastapi import HTTPException
from fastapi import APIRouter
from repositories.nota_repository import NotaRepository
from schemas.nota_frequencia_schema import NotaSchema, CreateNotaSchema

router = APIRouter(prefix="/notas", tags=["Notas"])
service = NotaRepository()

@router.get("/matricula/{matricula_id}", response_model=list[NotaSchema])
def listar_notas(matricula_id: int):
    return service.get_by_matricula(matricula_id)

@router.post("/", response_model=NotaSchema)
def criar_nota(n: CreateNotaSchema):
    id = service.create(n.model_dump())
    return service.get_by_matricula(n.matricula_id)[-1]

@router.delete("/{id}")
def deletar_nota(id: int):
    sucesso = service.delete(id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Nota não encontrada")
    return {"message": "Nota deletada"}