from pydantic import BaseModel
from typing import Optional

# Nota
class NotaSchema(BaseModel):
    id: int
    matricula_id: int
    avaliacao: str
    nota: float

class CreateNotaSchema(BaseModel):
    matricula_id: int
    avaliacao: str
    nota: float

# Frequência
class FrequenciaSchema(BaseModel):
    id: int
    matricula_id: int
    data: str
    presenca: int

class CreateFrequenciaSchema(BaseModel):
    matricula_id: int
    data: str
    presenca: int