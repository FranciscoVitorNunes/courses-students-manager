from fastapi import FastAPI
from routers import aluno_router
from routers import curso_router
from routers import turma_router
from routers import matricula_router

app = FastAPI(title="Gerenciador de Cursos e Alunos")

@app.get("/")
def teste():
    return "Gerenciador de Cursos e Alunos"

app.include_router(aluno_router.router)
app.include_router(curso_router.router)
app.include_router(turma_router.router)
app.include_router(matricula_router.router)
