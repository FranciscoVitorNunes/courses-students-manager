from fastapi import HTTPException
from fastapi import APIRouter
from repositories.matricula_repository import MatriculaRepository
from schemas.matricula_schema import MatriculaSchema, CreateMatriculaSchema, UpdateMatriculaSchema

router = APIRouter(prefix="/matriculas", tags=["Matriculas"])
service = MatriculaRepository()

@router.get("/", response_model=list[MatriculaSchema])
def listar_todas():
    return service.get_all()

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

@router.delete("/{id}")
def deletar(id: int):
    sucesso = service.delete(id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    return {"message": "Matrícula deletada"}

@router.patch("/{id}")
def atualizar_situacao(id: int, m: UpdateMatriculaSchema):
    dados = m.model_dump(exclude_none=True)
    atualizado = service.update(id, dados)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada ou nada para atualizar")
    return {"message": "Situação da matrícula atualizada"}