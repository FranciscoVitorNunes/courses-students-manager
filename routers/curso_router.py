# routers/curso_router.py
from fastapi import HTTPException, APIRouter, Depends, Query
from services.curso_service import CursoService
from services.aluno_service import AlunoService
from schemas.curso_schema import CursoSchema, UpdateCursoSchema, CursoComPrerequisitosSchema
from schemas.prerequisito_schema import PrerequisitoCreateSchema, PrerequisitoResponseSchema

router = APIRouter(prefix="/cursos", tags=["Cursos"])

# Dependências
def get_curso_service():
    return CursoService()

def get_aluno_service():
    return AlunoService()

@router.get("/")
def listar_cursos(
    incluir_prerequisitos: bool = Query(False, description="Incluir pré-requisitos na resposta"),
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Lista todos os cursos.
    
    Parâmetros:
    - incluir_prerequisitos: Se True, inclui lista de pré-requisitos para cada curso.
    """
    try:
        cursos = curso_service.listar_cursos(incluir_prerequisitos=incluir_prerequisitos)
        
        if incluir_prerequisitos:
            return [curso.to_dict() for curso in cursos]
        else:
            return [curso.to_dict_resumo() for curso in cursos]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao listar cursos: {str(e)}"
        )

@router.post("/")
def criar_curso(
    curso: CursoSchema,
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Cria um novo curso.
    """
    try:
        novo_curso = curso_service.criar_curso(curso)
        return {
            "message": "Curso criado com sucesso!",
            "curso": novo_curso.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao criar curso: {str(e)}"
        )

@router.get("/{codigo}")
def buscar_curso_por_codigo(
    codigo: str,
    incluir_prerequisitos: bool = Query(True, description="Incluir pré-requisitos na resposta"),
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Busca um curso pelo código.
    
    Parâmetros:
    - incluir_prerequisitos: Se True, inclui lista de pré-requisitos.
    """
    curso_obj = curso_service.buscar_curso(codigo, incluir_prerequisitos=incluir_prerequisitos)
    if not curso_obj:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    
    if incluir_prerequisitos:
        return curso_obj.to_dict()
    else:
        return curso_obj.to_dict_resumo()

@router.delete("/{codigo}")
def deletar_curso(
    codigo: str,
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Deleta um curso.
    """
    try:
        deletado = curso_service.deletar_curso(codigo)
        if not deletado:
            raise HTTPException(status_code=404, detail="Curso não encontrado")
        
        return {"message": "Curso deletado com sucesso!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao deletar curso: {str(e)}"
        )

@router.patch("/{codigo}")
def atualizar_curso(
    codigo: str,
    curso: UpdateCursoSchema,
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Atualiza parcialmente um curso.
    """
    try:
        curso_atualizado = curso_service.atualizar_curso(codigo, curso)
        if not curso_atualizado:
            raise HTTPException(status_code=404, detail="Curso não encontrado")
        
        return {
            "message": "Curso atualizado com sucesso!",
            "curso": curso_atualizado.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao atualizar curso: {str(e)}"
        )

@router.get("/buscar/")
def buscar_cursos_por_nome(
    nome: str = Query(..., description="Nome ou parte do nome do curso"),
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Busca cursos pelo nome (busca parcial).
    """
    try:
        cursos = curso_service.buscar_cursos_por_nome(nome)
        return [curso.to_dict_resumo() for curso in cursos]
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao buscar cursos: {str(e)}"
        )

@router.post("/prerequisitos/", status_code=201)
def adicionar_prerequisito(
    prerequisito: PrerequisitoCreateSchema,
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Adiciona um pré-requisito a um curso.
    """
    try:
        adicionado = curso_service.adicionar_prerequisito(
            prerequisito.curso_codigo,
            prerequisito.prerequisito_codigo
        )
        
        if not adicionado:
            raise HTTPException(status_code=400, detail="Não foi possível adicionar o pré-requisito")
        
        return {
            "message": "Pré-requisito adicionado com sucesso!",
            "curso_codigo": prerequisito.curso_codigo,
            "prerequisito_codigo": prerequisito.prerequisito_codigo
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao adicionar pré-requisito: {str(e)}"
        )

@router.get("/prerequisitos/{codigo}")
def obter_prerequisitos_curso(
    codigo: str,
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Obtém a lista de pré-requisitos de um curso.
    """
    try:
        prerequisitos = curso_service.obter_prerequisitos(codigo)
        
        curso = curso_service.buscar_curso(codigo)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso não encontrado")
        
        return PrerequisitoResponseSchema(
            curso_codigo=codigo,
            prerequisitos=prerequisitos
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter pré-requisitos: {str(e)}"
        )

@router.delete("/prerequisitos/{curso_codigo}/{prerequisito_codigo}")
def remover_prerequisito(
    curso_codigo: str,
    prerequisito_codigo: str,
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Remove um pré-requisito de um curso.
    """
    try:
        removido = curso_service.remover_prerequisito(curso_codigo, prerequisito_codigo)
        if not removido:
            raise HTTPException(status_code=404, detail="Pré-requisito não encontrado")
        
        return {"message": "Pré-requisito removido com sucesso!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao remover pré-requisito: {str(e)}"
        )

@router.get("/{curso_codigo}/dependentes/")
def obter_cursos_dependentes(
    curso_codigo: str,
    curso_service: CursoService = Depends(get_curso_service)
):
    """
    Obtém lista de cursos que têm este curso como pré-requisito.
    """
    try:
        dependentes = curso_service.obter_cursos_com_prerequisito(curso_codigo)
        
        curso = curso_service.buscar_curso(curso_codigo)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso não encontrado")
        
        return {
            "curso_codigo": curso_codigo,
            "cursos_dependentes": dependentes
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter cursos dependentes: {str(e)}"
        )

@router.get("/{curso_codigo}/validar-matricula/{aluno_matricula}")
def validar_matricula_aluno(
    curso_codigo: str,
    aluno_matricula: str,
    curso_service: CursoService = Depends(get_curso_service),
    aluno_service: AlunoService = Depends(get_aluno_service)
):
    """
    Valida se um aluno pode se matricular em um curso.
    """
    try:
        resultado = curso_service.validar_matricula_aluno(
            aluno_matricula, 
            curso_codigo, 
            aluno_service
        )
        
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao validar matrícula: {str(e)}"
        )