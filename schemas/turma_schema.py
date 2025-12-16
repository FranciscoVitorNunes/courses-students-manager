from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List
from datetime import time


class TurmaBase(BaseModel):
    periodo: str = Field(..., min_length=6, max_length=7, description="Período letivo (ex: 2025.1)")
    vagas: int = Field(..., gt=0, description="Quantidade máxima de vagas")
    curso: str = Field(..., description="Código do curso")
    horarios: Dict[str, str] = Field(..., description="Horários no formato {dia: 'HH:MM-HH:MM'}")
    local: Optional[str] = Field(None, max_length=100, description="Local da turma")
    status: bool = Field(description="Define se a turma está aberta(true) ou fechada(false)")
    
    @validator('periodo')
    def validar_periodo(cls, v):
        if not v or '.' not in v:
            raise ValueError("Período deve estar no formato YYYY.S (ex: 2025.1)")
        
        try:
            ano, semestre = v.split('.')
            if len(ano) != 4 or not ano.isdigit():
                raise ValueError("Ano deve ter 4 dígitos")
            if semestre not in ['1', '2']:
                raise ValueError("Semestre deve ser 1 ou 2")
        except ValueError:
            raise ValueError("Período inválido. Use formato YYYY.S (ex: 2025.1)")
        
        return v
    
    @validator('horarios')
    def validar_horarios(cls, v):
        if not v:
            raise ValueError("A turma deve ter pelo menos um horário")
        
        dias_validos = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
        
        for dia, intervalo in v.items():
            dia_lower = dia.lower()
            if dia_lower not in dias_validos:
                raise ValueError(f"Dia inválido: {dia}. Use: {', '.join(dias_validos)}")
            
            # Validar formato do intervalo
            try:
                inicio_str, fim_str = intervalo.split('-')
                inicio = time.fromisoformat(inicio_str)
                fim = time.fromisoformat(fim_str)
                
                if inicio >= fim:
                    raise ValueError(f"Horário de início deve ser anterior ao fim no dia {dia}")
                
                if inicio.hour < 6 or fim.hour > 22:
                    raise ValueError(f"Horários devem estar entre 06:00 e 22:00 no dia {dia}")
            
            except ValueError as e:
                raise ValueError(f"Intervalo inválido para {dia}: '{intervalo}'. Erro: {str(e)}")
        
        return v


class TurmaCreate(TurmaBase):
    id: str = Field(..., min_length=1, max_length=20, description="ID único da turma")


class TurmaSchema(TurmaCreate):
    class Config:
        from_attributes = True


class UpdateTurmaSchema(BaseModel):
    periodo: Optional[str] = Field(None, min_length=6, max_length=7)
    vagas: Optional[int] = Field(None, gt=0)
    horarios: Optional[Dict[str, str]] = Field(None)
    local: Optional[str] = Field(None, max_length=100)
    status: Optional[bool] = Field(None)

    @validator('periodo')
    def validar_periodo(cls, v):
        if v is None:
            return v
        return TurmaBase.validar_periodo.__func__(cls, v)
    
    @validator('vagas')
    def validar_vagas(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Vagas deve ser maior que zero")
        return v
    
    @validator('horarios')
    def validar_horarios(cls, v):
        if v is None:
            return v
        return TurmaBase.validar_horarios.__func__(cls, v)
    
    class Config:
        from_attributes = True


class TurmaResponseSchema(TurmaSchema):
    status: str
    vagas_ocupadas: int
    vagas_disponiveis: int
    curso_nome: Optional[str] = None
    
    class Config:
        from_attributes = True


class TurmaResumoSchema(BaseModel):
    id: str
    periodo: str
    vagas: int
    vagas_disponiveis: int
    status: str
    curso_codigo: str
    curso_nome: str
    local: Optional[str]
    
    class Config:
        from_attributes = True