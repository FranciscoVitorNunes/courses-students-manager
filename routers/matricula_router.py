from typing import Optional
from fastapi import HTTPException, APIRouter, Depends, Query, Body
from services.matricula_service import MatriculaService
from schemas.matricula_schema import (
    MatriculaSchema, 
    MatriculaCreateSchema, 
    UpdateMatriculaSchema,
    MatriculaComDetalhesSchema,
    ValidacaoMatriculaSchema,
    ValidacaoMatriculaResponse,
    LancamentoNotaFrequenciaSchema
)

router = APIRouter(prefix="/matriculas", tags=["Matrículas"])


def get_matricula_service():
    return MatriculaService()

@router.get("/", response_model=list[MatriculaComDetalhesSchema])
def listar_matriculas(
    turma_id: Optional[str] = Query(None, description="Filtrar por ID da turma"),
    aluno_matricula: Optional[str] = Query(None, description="Filtrar por matrícula do aluno"),
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Lista todas as matrículas com filtros opcionais.
    """
    try:
        matriculas = matricula_service.listar_matriculas(
            turma_id=turma_id,
            aluno_matricula=aluno_matricula
        )
        return [matricula.to_dict() for matricula in matriculas]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao listar matrículas: {str(e)}"
        )

@router.get("/{matricula_id}", response_model=MatriculaComDetalhesSchema)
def buscar_matricula(
    matricula_id: int,
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Busca uma matrícula pelo ID.
    """
    matricula = matricula_service.buscar_matricula(matricula_id)
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    
    return matricula.to_dict()

@router.post("/", response_model=MatriculaComDetalhesSchema, status_code=201)
def criar_matricula(
    matricula: MatriculaCreateSchema,
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Cria uma nova matrícula com todas as validações.
    """
    try:
        resultado = matricula_service.criar_matricula(matricula)
        return resultado["matricula"]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao criar matrícula: {str(e)}"
        )

@router.delete("/{matricula_id}")
def deletar_matricula(
    matricula_id: int,
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Deleta uma matrícula.
    """
    try:
        deletada = matricula_service.deletar_matricula(matricula_id)
        if not deletada:
            raise HTTPException(status_code=404, detail="Matrícula não encontrada")
        
        return {"message": "Matrícula deletada com sucesso!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao deletar matrícula: {str(e)}"
        )

@router.patch("/{matricula_id}")
def atualizar_matricula(
    matricula_id: int,
    matricula: UpdateMatriculaSchema,
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Atualiza uma matrícula.
    """
    try:
        matricula_atualizada = matricula_service.atualizar_matricula(matricula_id, matricula)
        if not matricula_atualizada:
            raise HTTPException(status_code=404, detail="Matrícula não encontrada")
        
        return {
            "message": "Matrícula atualizada com sucesso!",
            "matricula": matricula_atualizada.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao atualizar matrícula: {str(e)}"
        )

@router.post("/validar")
def validar_matricula(
    validacao: ValidacaoMatriculaSchema = Body(...),
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Valida se um aluno pode se matricular em uma turma.
    Retorna informações detalhadas sobre a validação.
    """
    try:
        resultado = matricula_service.validar_matricula(
            validacao.aluno_matricula,
            validacao.turma_id
        )
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao validar matrícula: {str(e)}"
        )

@router.post("/{matricula_id}/lancar-avaliacao")
def lancar_nota_frequencia(
    matricula_id: int,
    lancamento: LancamentoNotaFrequenciaSchema = Body(...),
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Lança nota e frequência para uma matrícula.
    """
    try:
        resultado = matricula_service.lancar_nota_frequencia(
            matricula_id,
            lancamento.nota,
            lancamento.frequencia
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao lançar nota/frequência: {str(e)}"
        )

@router.post("/{matricula_id}/trancar")
def trancar_matricula(
    matricula_id: int,
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Tranca uma matrícula.
    """
    try:
        resultado = matricula_service.trancar_matricula(matricula_id)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao trancar matrícula: {str(e)}"
        )

@router.get("/turma/{turma_id}/estatisticas")
def estatisticas_turma(
    turma_id: str,
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Obtém estatísticas de uma turma.
    Inclui taxa de aprovação, distribuição de notas, alunos em risco, etc.
    """
    try:
        estatisticas = matricula_service.obter_estatisticas_turma(turma_id)
        return estatisticas
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter estatísticas da turma: {str(e)}"
        )

@router.get("/relatorio/geral")
def relatorio_geral_matriculas(
    periodo: Optional[str] = Query(None, description="Período específico"),
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Gera relatório geral de matrículas.
    """
    try:
        relatorio = matricula_service.gerar_relatorio_matriculas(periodo)
        return relatorio
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao gerar relatório: {str(e)}"
        )

@router.get("/aluno/{aluno_matricula}/turmas")
def listar_turmas_do_aluno(
    aluno_matricula: str,
    matricula_service: MatriculaService = Depends(get_matricula_service)
):
    """
    Lista todas as turmas de um aluno.
    """
    try:
        matriculas = matricula_service.listar_matriculas(aluno_matricula=aluno_matricula)
        return [matricula.to_dict_resumo() for matricula in matriculas]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao listar turmas do aluno: {str(e)}"
        )