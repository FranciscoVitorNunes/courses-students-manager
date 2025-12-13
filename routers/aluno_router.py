# routers/aluno_router.py
from fastapi import HTTPException, APIRouter
from services.aluno_service import AlunoService
from schemas.aluno_schema import AlunoSchema, UpdateAlunoSchema
from schemas.historico_schema import HistoricoCreateSchema, HistoricoUpdateSchema

router = APIRouter(prefix="/alunos", tags=["Alunos"])
service = AlunoService()

@router.get("/")
def listar_alunos(ordenar_por_cr: bool = False):
    """
    Lista todos os alunos.
    
    Parâmetros:
    - ordenar_por_cr: Se True, ordena por CR decrescente.
    """
    try:
        alunos = service.listar_alunos(ordenar_por_cr=ordenar_por_cr)
        return [aluno.to_dict() for aluno in alunos]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao listar alunos: {str(e)}"
        )

@router.post("/")
def criar_aluno(aluno: AlunoSchema):
    """
    Cria um novo aluno.
    """
    try:
        novo_aluno = service.criar_aluno(aluno)
        return {
            "message": "Aluno criado com sucesso!",
            "aluno": novo_aluno.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao criar aluno: {str(e)}"
        )

@router.get("/{matricula}")
def buscar_aluno_por_matricula(matricula: str):
    """
    Busca um aluno pela matrícula.
    """
    aluno = service.buscar_aluno(matricula)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    return aluno.to_dict()

@router.delete("/{matricula}")
def deletar_aluno(matricula: str):
    """
    Deleta um aluno.
    """
    deletado = service.deletar_aluno(matricula)
    if not deletado:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    return {"message": "Aluno deletado com sucesso!"}

@router.patch("/{matricula}")
def atualizar_aluno(matricula: str, aluno: UpdateAlunoSchema):
    """
    Atualiza parcialmente um aluno.
    """
    try:
        aluno_atualizado = service.atualizar_aluno(matricula, aluno)
        if not aluno_atualizado:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        return {
            "message": "Aluno atualizado com sucesso!",
            "aluno": aluno_atualizado.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao atualizar aluno: {str(e)}"
        )

@router.get("/{matricula}/cr")
def obter_cr_aluno(matricula: str):
    """
    Obtém o CR de um aluno.
    """
    aluno = service.buscar_aluno(matricula)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    return {"matricula": matricula, "cr": aluno.cr}

@router.get("/{matricula}/verificar-pre-requisitos/")
def verificar_pre_requisitos_aluno(matricula: str, cursos: str):
    """
    Verifica se aluno cumpriu pré-requisitos para uma lista de cursos.
    
    Parâmetros:
    - cursos: Lista de códigos de cursos separados por vírgula.
    """
    try:
        codigos_cursos = [codigo.strip() for codigo in cursos.split(",") if codigo.strip()]
        resultados = service.verificar_pre_requisitos(matricula, codigos_cursos)
        return {
            "matricula": matricula,
            "pre_requisitos": resultados
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao verificar pré-requisitos: {str(e)}"
        )

@router.get("/ranking/top/{n}")
def obter_top_alunos(n: int = 10):
    """
    Retorna os top N alunos por CR.
    """
    try:
        if n <= 0:
            raise HTTPException(status_code=400, detail="N deve ser maior que 0")
        
        top_alunos = service.obter_top_alunos(n)
        return {
            "top_n": n,
            "alunos": [aluno.to_dict() for aluno in top_alunos]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter top alunos: {str(e)}"
        )
    

@router.get("/{matricula}/historico")
def obter_historico_aluno(matricula: str):
    """
    Obtém o histórico completo de um aluno.
    """
    try:
        historico = service.obter_historico_aluno(matricula)
        return {
            "matricula": matricula,
            "historico": historico
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter histórico: {str(e)}"
        )

@router.post("/{matricula}/historico")
def adicionar_ao_historico(matricula: str, historico: HistoricoCreateSchema):
    """
    Adiciona um registro ao histórico do aluno.
    """
    try:
        registro = service.adicionar_ao_historico(matricula, historico.model_dump())
        return {
            "message": "Registro adicionado ao histórico com sucesso!",
            "registro": registro
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao adicionar ao histórico: {str(e)}"
        )

@router.put("/historico/{registro_id}")
def atualizar_registro_historico(registro_id: int, historico: HistoricoUpdateSchema):
    """
    Atualiza um registro do histórico.
    """
    try:
        atualizado = service.atualizar_registro_historico(
            registro_id, 
            historico.model_dump(exclude_none=True)
        )
        
        if not atualizado:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        
        return {"message": "Registro atualizado com sucesso!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao atualizar registro: {str(e)}"
        )

@router.delete("/historico/{registro_id}")
def remover_registro_historico(registro_id: int):
    """
    Remove um registro do histórico.
    """
    try:
        removido = service.remover_do_historico(registro_id)
        
        if not removido:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        
        return {"message": "Registro removido com sucesso!"}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao remover registro: {str(e)}"
        )

@router.get("/{matricula}/estatisticas")
def obter_estatisticas_aluno(matricula: str):
    """
    Obtém estatísticas do aluno.
    """
    try:
        estatisticas = service.get_estatisticas_aluno(matricula)
        if not estatisticas:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        return {
            "matricula": matricula,
            "estatisticas": estatisticas
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

@router.post("/{matricula}/recalcular-cr")
def recalcular_cr_aluno(matricula: str):
    """
    Recalcula e atualiza o CR do aluno.
    """
    try:
        atualizado = service.atualizar_cr_aluno(matricula)
        if not atualizado:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        aluno = service.buscar_aluno(matricula)
        return {
            "message": "CR recalculado com sucesso!",
            "matricula": matricula,
            "cr": aluno.cr if aluno else 0.0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao recalcular CR: {str(e)}"
        )