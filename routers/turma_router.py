from fastapi import HTTPException
from fastapi import APIRouter
from repositories.turma_repository import TurmaRepository
from repositories.curso_repository import CursoRepository
from schemas.turma_schema import TurmaSchema, UpdateTurmaSchema
from models.turma import Turma
from models.curso import Curso

router = APIRouter(prefix="/turmas", tags=["Turmas"])
service = TurmaRepository()
curso_repo  = CursoRepository()

@router.get("/")
def listar():
    return service.list_all()

@router.post("/")
def criar(turma: TurmaSchema):
    try:
        curso = curso_repo.get_by_codigo(turma.curso)

        turma_model = Turma(
            id=turma.id,
            periodo=turma.periodo,
            horarios=turma.horarios,
            vagas=turma.vagas,
            curso=curso
        )
        service.create(turma_model)

    except Exception as e:
        print("ERRO REAL:", e)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}")
def buscar_por_id(id: str):
    turma = service.get_by_id(id)
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    return TurmaSchema(
        id=turma['id'],
        periodo=turma['periodo'],
        vagas=turma['vagas'],
        curso=turma['curso_codigo'],
        horarios=turma['horarios']
    )

@router.delete("/{id}")
def deletar(id: str):
    service.delete(id)

@router.patch("/{codigo}")
def atualizar(codigo: str, curso: UpdateTurmaSchema):
    dados = curso.model_dump(exclude_none=True)

    atualizado = service.update(codigo, dados)

    if not atualizado:
        raise HTTPException(
            status_code=404,
            detail="Curso não encontrado ou nada para atualizar"
        )

    return {"message": "Curso atualizado parcialmente"}