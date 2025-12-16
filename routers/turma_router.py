from fastapi import HTTPException, APIRouter, Depends, Query
from typing import Optional
from services.turma_service import TurmaService
from services.curso_service import CursoService
from schemas.turma_schema import TurmaSchema, UpdateTurmaSchema

router = APIRouter(prefix="/turmas", tags=["Turmas"])

# Dependências
def get_turma_service():
    return TurmaService()

def get_curso_service():
    return CursoService()

@router.get("/")
def listar_turmas(
    periodo: Optional[str] = Query(None, description="Filtrar por período (ex: 2025.1)"),
    curso_codigo: Optional[str] = Query(None, description="Filtrar por código do curso"),
    status: Optional[str] = Query(None, description="Filtrar por status (aberta, fechada, esgotada)"),
    apenas_abertas: bool = Query(False, description="Apenas turmas abertas para matrícula"),
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Lista todas as turmas com filtros opcionais."""
    try:
        if apenas_abertas:
            status = "aberta"
        
        turmas = turma_service.listar_turmas(
            periodo=periodo,
            curso_codigo=curso_codigo,
            status=status
        )
        
        return [turma.to_dict_resumo() for turma in turmas]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao listar turmas: {str(e)}"
        )

@router.get("/curso/{curso_codigo}")
def buscar_turmas_por_curso(
    curso_codigo: str,
    periodo: Optional[str] = Query(None, description="Filtrar por período"),
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Busca turmas de um curso específico."""
    try:
        turmas = turma_service.buscar_turmas_por_curso(curso_codigo, periodo=periodo)
        return [turma.to_dict_resumo() for turma in turmas]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao buscar turmas do curso: {str(e)}"
        )

@router.get("/periodo/{periodo}/estatisticas")
def estatisticas_periodo(
    periodo: str,
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Obtém estatísticas das turmas de um período."""
    try:
        estatisticas = turma_service.get_estatisticas_periodo(periodo)
        return estatisticas
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

@router.get("/{turma_id}/vagas")
def verificar_vagas_turma(
    turma_id: str,
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Verifica disponibilidade de vagas em uma turma."""
    try:
        info_vagas = turma_service.verificar_disponibilidade_vagas(turma_id)
        return info_vagas
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao verificar vagas: {str(e)}"
        )

@router.get("/{turma_id}")
def buscar_turma_por_id(
    turma_id: str,
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Busca uma turma pelo ID."""
    turma = turma_service.buscar_turma(turma_id)
    
    return turma.to_dict()

@router.post("/", status_code=201)
def criar_turma(
    turma: TurmaSchema,
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Cria uma nova turma."""
    try:
        nova_turma = turma_service.criar_turma(turma)
        return {
            "message": "Turma criada com sucesso!",
            "turma": nova_turma.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao criar turma: {str(e)}"
        )

@router.delete("/{turma_id}")
def deletar_turma(
    turma_id: str,
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Deleta uma turma."""
    try:
        deletada = turma_service.deletar_turma(turma_id)
        if not deletada:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        return {"message": "Turma deletada com sucesso!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao deletar turma: {str(e)}"
        )

@router.patch("/{turma_id}")
def atualizar_turma(
    turma_id: str,
    turma: UpdateTurmaSchema,
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Atualiza parcialmente uma turma."""
    try:
        turma_atualizada = turma_service.atualizar_turma(turma_id, turma)
        if not turma_atualizada:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        return {
            "message": "Turma atualizada com sucesso!",
            "turma": turma_atualizada.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao atualizar turma: {str(e)}"
        )

@router.post("/{turma_id}/abrir")
def abrir_turma(
    turma_id: str,
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Abre uma turma para matrículas."""
    try:
        response, msg = turma_service.abrir_turma(turma_id)
        
        turma = turma_service.buscar_turma(turma_id)
        return {
            "message": f"{msg}",
            "turma": turma.to_dict_resumo()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao abrir turma: {str(e)}"
        )

@router.post("/{turma_id}/fechar")
def fechar_turma(
    turma_id: str,
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Fecha uma turma para matrículas."""
    try:
        response, msg = turma_service.fechar_turma(turma_id)
        
        turma = turma_service.buscar_turma(turma_id)
        return {
            "message": f"{msg}",
            "turma": turma.to_dict_resumo()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao fechar turma: {str(e)}"
        )

@router.post("/{turma_id}/verificar-choque")
def verificar_choque_horario(
    turma_id: str,
    horarios: dict,
    turma_service: TurmaService = Depends(get_turma_service)
):
    """Verifica se há choque de horário com uma turma."""
    try:
        tem_choque = turma_service.verificar_choque_horario(turma_id, horarios)
        return {
            "turma_id": turma_id,
            "tem_choque": tem_choque,
            "mensagem": "Há choque de horário" if tem_choque else "Não há choque de horário"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao verificar choque: {str(e)}"
        )