# schemas/historico_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class HistoricoBase(BaseModel):
    codigo_curso: str = Field(..., min_length=1, max_length=20, description="Código do curso")
    nota: float = Field(..., ge=0.0, le=10.0, description="Nota obtida (0-10)")
    frequencia: float = Field(..., ge=0.0, le=100.0, description="Frequência (0-100%)")
    carga_horaria: int = Field(..., gt=0, description="Carga horária do curso")
    situacao: str = Field(..., description="Situação do aluno no curso")
    semestre: Optional[str] = Field(None, description="Semestre (ex: 2025.1)")
    
    @validator('situacao')
    def validar_situacao(cls, v):
        situacoes_validas = ['APROVADO', 'REPROVADO_POR_NOTA', 
                            'REPROVADO_POR_FREQUENCIA', 'CURSANDO', 
                            'TRANCADO', 'DESISTENTE']
        if v.upper() not in situacoes_validas:
            raise ValueError(f"Situação deve ser uma das: {', '.join(situacoes_validas)}")
        return v.upper()


class HistoricoCreateSchema(HistoricoBase):
    pass


class HistoricoSchema(HistoricoBase):
    id: int
    aluno_matricula: str
    data_registro: datetime
    
    class Config:
        from_attributes = True


class HistoricoUpdateSchema(BaseModel):
    nota: Optional[float] = Field(None, ge=0.0, le=10.0)
    frequencia: Optional[float] = Field(None, ge=0.0, le=100.0)
    situacao: Optional[str] = Field(None)
    semestre: Optional[str] = Field(None)
    
    @validator('situacao')
    def validar_situacao(cls, v):
        if v is None:
            return v
        situacoes_validas = ['APROVADO', 'REPROVADO_POR_NOTA', 
                            'REPROVADO_POR_FREQUENCIA', 'CURSANDO', 
                            'TRANCADO', 'DESISTENTE']
        if v.upper() not in situacoes_validas:
            raise ValueError(f"Situação deve ser uma das: {', '.join(situacoes_validas)}")
        return v.upper()