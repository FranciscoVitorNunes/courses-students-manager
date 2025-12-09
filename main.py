from fastapi import FastAPI
from routers import aluno_router
from routers import curso_router

app = FastAPI(title="Gerenciador de Cursos e Alunos")

@app.get("/")
def teste():
    return "Gerenciador de Cursos e Alunos"

app.include_router(aluno_router.router)
app.include_router(curso_router.router)

