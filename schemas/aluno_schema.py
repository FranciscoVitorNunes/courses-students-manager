from pydantic import BaseModel

class AlunoSchema(BaseModel):
    nome: str
    email: str
    matricula: str
    cr: int
