# schemas/aluno_schema.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from schemas.historico_schema import HistoricoSchema


class AlunoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class AlunoCreate(AlunoBase):
    matricula: str = Field(..., min_length=1, max_length=20)
    
    @validator('matricula')
    def validar_matricula(cls, v):
        if not v.strip():
            raise ValueError("Matrícula não pode ser vazia")
        return v.strip()


class AlunoSchema(AlunoCreate):
    cr: Optional[float] = Field(0.0, ge=0.0, le=10.0)
    historico: Optional[List[Dict[str, Any]]] = []
    
    class Config:
        from_attributes = True


class UpdateAlunoSchema(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    cr: Optional[float] = Field(None, ge=0.0, le=10.0)
    
    class Config:
        from_attributes = True


class AlunoComHistoricoSchema(AlunoSchema):
    historico: List[HistoricoSchema] = []
    
    class Config:
        from_attributes = True