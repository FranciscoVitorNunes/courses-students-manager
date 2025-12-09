from pydantic import BaseModel
from typing import Optional

class MatriculaSchema(BaseModel):
    id: int
    aluno_matricula: str
    turma_id: str
    situacao: str

class CreateMatriculaSchema(BaseModel):
    aluno_matricula: str
    turma_id: str
    situacao: Optional[str] = "cursando"

class UpdateMatriculaSchema(BaseModel):
    situacao: Optional[str] = None