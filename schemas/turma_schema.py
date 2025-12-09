from pydantic import BaseModel
from typing import Dict
from typing import Optional

class TurmaSchema(BaseModel):
    id: str
    periodo: str
    vagas: int
    curso: str
    horarios: Dict[str, str]

class UpdateTurmaSchema(BaseModel):
    periodo: Optional[str] = None
    vagas: Optional[int] = None
    horarios: Optional[Dict[str, str]] = None