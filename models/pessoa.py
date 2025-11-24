class Pessoa:
    """Representa uma pessoa com nome e email."""

    def __init__(self, nome: str, email: str):
        if not nome or not nome.strip():
            raise ValueError("Nome não pode ser vazio.")
        if not email or '@' not in email:
            raise ValueError("Email inválido.")
        
        self._nome = nome.strip()
        self._email = email.strip()

    @property
    def nome(self):
        return self._nome
    
    @nome.setter
    def nome(self, valor):
        if not valor or not valor.strip():
            raise ValueError("Nome não pode ser vazio.")
        self._nome = valor.strip()

    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, valor):
        if not valor or '@' not in valor:
            raise ValueError("Email inválido.")
        self._email = valor.strip()

    def __str__(self):
        return f"{self.nome} ({self.email})"

    def __repr__(self):
        return f"Pessoa(nome='{self.nome}', email='{self.email}')"