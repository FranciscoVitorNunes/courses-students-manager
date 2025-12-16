
from typing import List, Optional, Dict, Any
from models.curso import Curso
from repositories.curso_repository import CursoRepository
from schemas.curso_schema import CursoSchema, UpdateCursoSchema
from schemas.prerequisito_schema import PrerequisitoCreateSchema


class CursoService:
    def __init__(self):
        self.repository = CursoRepository()
    
    def criar_curso(self, curso_data: CursoSchema) -> Curso:
        """
        Cria um novo curso.
        
        Args:
            curso_data: Dados do curso a ser criado.
            
        Returns:
            Objeto Curso criado.
            
        Raises:
            ValueError: Se o código já existir ou dados forem inválidos.
        """
        # Verificar se curso já existe
        curso_existente = self.repository.get_by_codigo(curso_data.codigo)
        if curso_existente:
            raise ValueError(f"Curso com código {curso_data.codigo} já existe.")
        
        # Criar objeto Curso
        curso = Curso(
            codigo=curso_data.codigo,
            nome=curso_data.nome,
            carga_horaria=curso_data.carga_horaria,
            ementa=curso_data.ementa if hasattr(curso_data, 'ementa') and curso_data.ementa else ""
        )
        
        # Salvar no banco via repository
        self.repository.create(curso_data)
        
        return curso
    
    def buscar_curso(self, codigo: str, incluir_prerequisitos: bool = False) -> Optional[Curso]:
        """
        Busca um curso pelo código.
        
        Args:
            codigo: Código do curso.
            incluir_prerequisitos: Se True, inclui lista de pré-requisitos.
            
        Returns:
            Objeto Curso se encontrado, None caso contrário.
        """
        # Buscar curso no banco
        curso_data = self.repository.get_by_codigo(codigo)
        if not curso_data:
            return None
        
        # Buscar pré-requisitos se solicitado
        prerequisitos = []
        if incluir_prerequisitos:
            prerequisitos = self.repository.get_prerequisitos(codigo)
        
        # Criar objeto Curso
        curso = Curso(
            codigo=curso_data.codigo,
            nome=curso_data.nome,
            carga_horaria=curso_data.carga_horaria,
            ementa=curso_data.ementa if hasattr(curso_data, 'ementa') else "",
            prerequisitos=prerequisitos
        )
        
        return curso
    
    def listar_cursos(self, incluir_prerequisitos: bool = False) -> List[Curso]:
        """
        Lista todos os cursos.
        
        Args:
            incluir_prerequisitos: Se True, inclui pré-requisitos para cada curso.
            
        Returns:
            Lista de objetos Curso.
        """
        cursos_data = self.repository.list_all()
        
        cursos = []
        for curso_data in cursos_data:
            prerequisitos = []
            if incluir_prerequisitos:
                prerequisitos = self.repository.get_prerequisitos(curso_data.codigo)
            
            curso = Curso(
                codigo=curso_data.codigo,
                nome=curso_data.nome,
                carga_horaria=curso_data.carga_horaria,
                ementa=curso_data.ementa if hasattr(curso_data, 'ementa') else "",
                prerequisitos=prerequisitos
            )
            cursos.append(curso)
        
        return cursos
    
    def atualizar_curso(self, codigo: str, dados_atualizacao: UpdateCursoSchema) -> Optional[Curso]:
        """
        Atualiza parcialmente um curso.
        
        Args:
            codigo: Código do curso a atualizar.
            dados_atualizacao: Dados a serem atualizados.
            
        Returns:
            Curso atualizado se encontrado, None caso contrário.
        """
        # Converter para dicionário excluindo valores None
        dados_dict = dados_atualizacao.model_dump(exclude_none=True)
        
        # Atualizar no repository
        atualizado = self.repository.update(codigo, dados_dict)
        if not atualizado:
            return None
        
        # Buscar curso atualizado
        return self.buscar_curso(codigo, incluir_prerequisitos=True)
    
    def deletar_curso(self, codigo: str) -> bool:
        """
        Deleta um curso.
        
        Args:
            codigo: Código do curso a deletar.
            
        Returns:
            True se deletado, False se não encontrado.
        """
        try:
            # Verificar se há pré-requisitos dependentes
            cursos_dependentes = self.repository.get_cursos_que_tem_como_prerequisito(codigo)
            if cursos_dependentes:
                raise ValueError(
                    f"Não é possível deletar o curso {codigo}. "
                    f"Ele é pré-requisito dos cursos: {', '.join(cursos_dependentes)}"
                )
            
            self.repository.delete(codigo)
            return True
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Erro ao deletar curso: {str(e)}")
    
    def adicionar_prerequisito(self, curso_codigo: str, prerequisito_codigo: str) -> bool:
        """
        Adiciona um pré-requisito a um curso.
        
        Args:
            curso_codigo: Código do curso.
            prerequisito_codigo: Código do curso pré-requisito.
            
        Returns:
            True se adicionado com sucesso.
            
        Raises:
            ValueError: Se algum dos cursos não existir ou se houver ciclo.
        """
        # Verificar se cursos existem
        curso = self.buscar_curso(curso_codigo)
        if not curso:
            raise ValueError(f"Curso {curso_codigo} não encontrado.")
        
        prerequisito = self.buscar_curso(prerequisito_codigo)
        if not prerequisito:
            raise ValueError(f"Pré-requisito {prerequisito_codigo} não encontrado.")
        
        # Verificar se não é o mesmo curso
        if curso_codigo == prerequisito_codigo:
            raise ValueError("Um curso não pode ser pré-requisito de si próprio.")
        
        # Verificar se já é pré-requisito
        if prerequisito_codigo in curso.prerequisitos:
            raise ValueError(f"O curso {prerequisito_codigo} já é pré-requisito de {curso_codigo}.")
        
        # Verificar se há ciclo (curso sendo pré-requisito do seu pré-requisito)
        if self._verificar_ciclo_prerequisitos(curso_codigo, prerequisito_codigo):
            raise ValueError(
                f"Não é possível adicionar {prerequisito_codigo} como pré-requisito de {curso_codigo}. "
                f"Isso criaria um ciclo de dependência."
            )
        
        # Adicionar ao objeto curso
        curso.adicionar_prerequisito(prerequisito_codigo)
        
        # Salvar no banco
        self.repository.create_prerequisitos(curso_codigo, prerequisito_codigo)
        
        return True
    
    def _verificar_ciclo_prerequisitos(self, curso_codigo: str, novo_prerequisito: str) -> bool:
        """
        Verifica se adicionar um novo pré-requisito criaria um ciclo.
        
        Args:
            curso_codigo: Código do curso que receberá o pré-requisito.
            novo_prerequisito: Código do novo pré-requisito.
        
        Returns:
            True se houver ciclo, False caso contrário.
        """

        curso_prerequisito = self.obter_prerequisitos(novo_prerequisito)
        print(curso_prerequisito)

        if curso_codigo in curso_prerequisito:
            print("ffalse")
            return True
        else:
            print("true")
            return False
    
    def remover_prerequisito(self, curso_codigo: str, prerequisito_codigo: str) -> bool:
        """
        Remove um pré-requisito de um curso.
        
        Args:
            curso_codigo: Código do curso.
            prerequisito_codigo: Código do pré-requisito a remover.
            
        Returns:
            True se removido, False se não encontrado.
        """
        # Verificar se o curso existe
        curso = self.buscar_curso(curso_codigo, incluir_prerequisitos=True)
        if not curso:
            raise ValueError(f"Curso {curso_codigo} não encontrado.")
        
        # Remover do objeto curso
        removido = curso.remover_prerequisito(prerequisito_codigo)
        if not removido:
            raise ValueError(f"O curso {prerequisito_codigo} não é pré-requisito de {curso_codigo}.")
        
        # Remover do banco
        return self.repository.remover_prerequisito(curso_codigo, prerequisito_codigo)
    
    def obter_prerequisitos(self, curso_codigo: str) -> List[str]:
        """
        Obtém a lista de pré-requisitos de um curso.
        
        Args:
            curso_codigo: Código do curso.
            
        Returns:
            Lista de códigos de pré-requisitos.
        """
        return self.repository.get_prerequisitos(curso_codigo)
    
    def obter_cursos_com_prerequisito(self, prerequisito_codigo: str) -> List[str]:
        """
        Obtém lista de cursos que têm um determinado curso como pré-requisito.
        
        Args:
            prerequisito_codigo: Código do curso pré-requisito.
            
        Returns:
            Lista de códigos de cursos que dependem deste.
        """
        return self.repository.get_cursos_que_tem_como_prerequisito(prerequisito_codigo)
    
    def validar_matricula_aluno(self, aluno_matricula: str, curso_codigo: str, 
                                aluno_service) -> Dict[str, Any]:
        """
        Valida se um aluno pode se matricular em um curso.
        
        Args:
            aluno_matricula: Matrícula do aluno.
            curso_codigo: Código do curso.
            aluno_service: Serviço de aluno para verificar histórico.
            
        Returns:
            Dicionário com resultado da validação.
        """
        resultado = {
            'pode_matricular': False,
            'mensagem': '',
            'prerequisitos_faltantes': [],
            'curso_encontrado': False
        }
        
        # Verificar se curso existe
        curso = self.buscar_curso(curso_codigo, incluir_prerequisitos=True)
        if not curso:
            resultado['mensagem'] = f"Curso {curso_codigo} não encontrado."
            return resultado
        
        resultado['curso_encontrado'] = True
        
        # Verificar se aluno existe
        aluno = aluno_service.buscar_aluno(aluno_matricula)
        if not aluno:
            resultado['mensagem'] = f"Aluno {aluno_matricula} não encontrado."
            return resultado
        
        # Verificar pré-requisitos
        prerequisitos_faltantes = curso.get_prerequisitos_faltantes(
            aluno.get_cursos_aprovados()
        )
        
        if prerequisitos_faltantes:
            resultado['prerequisitos_faltantes'] = prerequisitos_faltantes
            resultado['mensagem'] = (
                f"Aluno não cumpriu os seguintes pré-requisitos: "
                f"{', '.join(prerequisitos_faltantes)}"
            )
        else:
            resultado['pode_matricular'] = True
            resultado['mensagem'] = "Aluno pode se matricular no curso."
        
        return resultado
    
    def buscar_cursos_por_nome(self, nome: str) -> List[Curso]:
        """
        Busca cursos pelo nome (busca parcial).
        
        Args:
            nome: Parte do nome do curso.
            
        Returns:
            Lista de cursos encontrados.
        """
        cursos = self.listar_cursos(incluir_prerequisitos=True)
        nome_lower = nome.lower()
        
        return [curso for curso in cursos if nome_lower in curso.nome.lower()]