from pydantic import BaseModel

class TurmaSchema(BaseModel):
    id: str
    periodo: str
    vagas: int
    curso: str
    horarios: dict

class UpdateTurmaSchema(BaseModel):
    pass