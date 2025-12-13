# schemas/curso_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from schemas.prerequisito_schema import PrerequisitoResponseSchema


class CursoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    carga_horaria: int = Field(..., gt=0)
    ementa: Optional[str] = Field("", max_length=1000)
    
    @validator('carga_horaria')
    def validar_carga_horaria(cls, v):
        if v <= 0:
            raise ValueError("Carga horária deve ser maior que zero")
        return v


class CursoCreate(CursoBase):
    codigo: str = Field(..., min_length=1, max_length=20)
    
    @validator('codigo')
    def validar_codigo(cls, v):
        if not v.strip():
            raise ValueError("Código não pode ser vazio")
        return v.strip().upper()


class CursoSchema(CursoCreate):
    class Config:
        from_attributes = True


class UpdateCursoSchema(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    carga_horaria: Optional[int] = Field(None, gt=0)
    ementa: Optional[str] = Field(None, max_length=1000)
    
    @validator('carga_horaria')
    def validar_carga_horaria(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Carga horária deve ser maior que zero")
        return v
    
    class Config:
        from_attributes = True


class CursoComPrerequisitosSchema(CursoSchema):
    prerequisitos: List[str] = []
    
    class Config:
        from_attributes = True


class CursoResumoSchema(BaseModel):
    codigo: str
    nome: str
    carga_horaria: int
    total_prerequisitos: int
    
    class Config:
        from_attributes = True