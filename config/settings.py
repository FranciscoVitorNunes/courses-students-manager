import json
from typing import Dict, Any
from datetime import datetime


class Settings:
    """
    Gerencia as configurações do sistema.
    Configurações são carregadas de um arquivo JSON.
    """
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self, config_file: str = "config/settings.json"):
        """Carrega configurações do arquivo JSON."""
        default_config = {
            "nota_minima_aprovacao": 6.0,
            "frequencia_minima": 75.0,
            "data_limite_trancamento": "2025-12-15",
            "max_turmas_por_aluno": 6,
            "top_n_alunos": 10
        }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            print(f"Arquivo de configuração {config_file} não encontrado. Usando configurações padrão.")
            self._config = default_config
        except json.JSONDecodeError:
            print(f"Erro ao decodificar {config_file}. Usando configurações padrão.")
            self._config = default_config
    
    @property
    def nota_minima_aprovacao(self) -> float:
        """Nota mínima para aprovação."""
        return self._config.get("nota_minima_aprovacao", 6.0)
    
    @property
    def frequencia_minima(self) -> float:
        """Frequência mínima para aprovação (%)."""
        return self._config.get("frequencia_minima", 75.0)
    
    @property
    def data_limite_trancamento(self) -> datetime:
        """Data limite para trancamento de matrículas."""
        data_str = self._config.get("data_limite_trancamento", "2025-12-15")
        return datetime.strptime(data_str, "%Y-%m-%d")
    
    @property
    def max_turmas_por_aluno(self) -> int:
        """Máximo de turmas por aluno (0 para ilimitado)."""
        return self._config.get("max_turmas_por_aluno", 6)
    
    @property
    def top_n_alunos(self) -> int:
        """Quantidade de alunos no ranking Top N."""
        return self._config.get("top_n_alunos", 10)
    
    def pode_trancar(self) -> bool:
        """Verifica se ainda é possível trancar matrículas."""
        return datetime.now() <= self.data_limite_trancamento
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Atualiza configurações."""
        self._config.update(new_config)
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna configurações como dicionário."""
        return {
            "nota_minima_aprovacao": self.nota_minima_aprovacao,
            "frequencia_minima": self.frequencia_minima,
            "data_limite_trancamento": self.data_limite_trancamento.strftime("%Y-%m-%d"),
            "max_turmas_por_aluno": self.max_turmas_por_aluno,
            "top_n_alunos": self.top_n_alunos,
            "pode_trancar": self.pode_trancar()
        }