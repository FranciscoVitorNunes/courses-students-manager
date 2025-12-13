from fastapi import FastAPI
from routers import aluno_router
from routers import curso_router
from routers import turma_router
from routers import matricula_router
from routers import nota_router
from routers import frequencia_router

app = FastAPI(title="Gerenciador de Cursos e Alunos")

@app.get("/")
def home():
    return {
        "message": "Gerenciador de Cursos e Alunos",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

app.include_router(aluno_router.router)
app.include_router(curso_router.router)
app.include_router(turma_router.router)
app.include_router(matricula_router.router)
app.include_router(nota_router.router)
app.include_router(frequencia_router.router)