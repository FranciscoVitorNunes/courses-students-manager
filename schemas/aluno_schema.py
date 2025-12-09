from pydantic import BaseModel
from typing import Optional

class AlunoSchema(BaseModel):
    nome: str
    email: str
    matricula: str
    cr: int

class UpdateAlunoSchema(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    cr: Optional[int] = None