# schemas/prerequisito_schema.py
from pydantic import BaseModel, Field


class PrerequisitoBase(BaseModel):
    curso_codigo: str = Field(..., description="Código do curso")
    prerequisito_codigo: str = Field(..., description="Código do curso pré-requisito")


class PrerequisitoCreateSchema(PrerequisitoBase):
    pass


class PrerequisitoSchema(PrerequisitoBase):
    id: int
    
    class Config:
        from_attributes = True


class PrerequisitoResponseSchema(BaseModel):
    curso_codigo: str
    prerequisitos: list[str]
    
    class Config:
        from_attributes = True