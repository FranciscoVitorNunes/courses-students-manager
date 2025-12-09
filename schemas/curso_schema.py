from pydantic import BaseModel

class CursoSchema(BaseModel):
    codigo: str
    nome: str
    carga_horaria: int
    ementa: str