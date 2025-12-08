from repositories.aluno_repository import AlunoRepository

class AlunoService:
    def __init__(self, aluno):
        self.aluno = aluno
        
    def criar_aluno_service(self):
        # Verificar se matricula já existe
        try:
            AlunoRepository.salvar(self.aluno)
        except:
            return False
        
    def deletar_aluno_service(self, matricula):
        try:
            AlunoRepository.deletar(matricula)
        except:
            return False
        
    def atualizar_aluno_service(self, aluno):
        try:
            AlunoRepository.atualizar(aluno)
        except:
            return False

    def buscar_aluno_service(self, matricula):
        try:
            AlunoRepository.buscar_por_matricula(matricula)
        except:
            return False

