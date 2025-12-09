from pydantic import BaseModel
from typing import Dict

class TurmaSchema(BaseModel):
    id: str
    periodo: str
    vagas: int
    curso: str
    horarios: Dict[str, str]

class UpdateTurmaSchema(BaseModel):
    pass