from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class MatriculaBase(BaseModel):
    aluno_matricula: str = Field(..., description="Matrícula do aluno")
    turma_id: str = Field(..., description="ID da turma")
    
    @validator('aluno_matricula')
    def validar_matricula(cls, v):
        if not v or not v.strip():
            raise ValueError("Matrícula não pode ser vazia")
        return v.strip()
    
    @validator('turma_id')
    def validar_turma_id(cls, v):
        if not v or not v.strip():
            raise ValueError("ID da turma não pode ser vazio")
        return v.strip()


class MatriculaCreateSchema(MatriculaBase):
    situacao: Optional[str] = Field("CURSANDO", description="Situação inicial da matrícula")
    
    @validator('situacao')
    def validar_situacao(cls, v):
        situacoes_validas = ['CURSANDO', 'APROVADO', 'REPROVADO_POR_NOTA', 
                            'REPROVADO_POR_FREQUENCIA', 'TRANCADA', 'DESISTENTE']
        if v.upper() not in situacoes_validas:
            raise ValueError(f"Situação deve ser uma das: {', '.join(situacoes_validas)}")
        return v.upper()


class UpdateMatriculaSchema(BaseModel):
    situacao: Optional[str] = Field(None, description="Nova situação da matrícula")
    nota: Optional[float] = Field(None, ge=0.0, le=10.0, description="Nota do aluno (0-10)")
    frequencia: Optional[float] = Field(None, ge=0.0, le=100.0, description="Frequência do aluno (0-100%)")
    
    @validator('situacao')
    def validar_situacao(cls, v):
        if v is None:
            return v
        situacoes_validas = ['CURSANDO', 'APROVADO', 'REPROVADO_POR_NOTA', 
                            'REPROVADO_POR_FREQUENCIA', 'TRANCADA', 'DESISTENTE']
        if v.upper() not in situacoes_validas:
            raise ValueError(f"Situação deve ser uma das: {', '.join(situacoes_validas)}")
        return v.upper()


class MatriculaSchema(MatriculaBase):
    id: int
    situacao: str
    data_matricula: Optional[datetime] = None
    nota: Optional[float] = None
    frequencia: Optional[float] = None
    
    class Config:
        from_attributes = True


class MatriculaComDetalhesSchema(MatriculaSchema):
    aluno_nome: Optional[str] = None
    turma_periodo: Optional[str] = None
    curso_codigo: Optional[str] = None
    curso_nome: Optional[str] = None
    
    class Config:
        from_attributes = True


class ValidacaoMatriculaSchema(BaseModel):
    aluno_matricula: str
    turma_id: str


class ValidacaoMatriculaResponse(BaseModel):
    valida: bool
    mensagem: str
    erros: list[str] = []
    prerequisitos_faltantes: Optional[list[str]] = None


class LancamentoNotaFrequenciaSchema(BaseModel):
    nota: float = Field(..., ge=0.0, le=10.0)
    frequencia: float = Field(..., ge=0.0, le=100.0)