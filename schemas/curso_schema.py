from pydantic import BaseModel
from typing  import Optional

class CursoSchema(BaseModel):
    codigo: str
    nome: str
    carga_horaria: int
    ementa: str

class UpdateCursoSchema(BaseModel):
    nome: Optional[str] = None
    carga_horaria: Optional[int] = None
    ementa: Optional[str] = None