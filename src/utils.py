"""Funções utilitárias para análise de consumo de eletricidade."""

import logging
import sys
from pathlib import Path
from typing import Optional
import yaml


def setup_logging(
    log_file: str = "analise.log",
    log_level: str = "INFO",
    log_format: Optional[str] = None
) -> logging.Logger:
    """Configura logging profissional para o projeto.
    
    Args:
        log_file: Caminho para o ficheiro de log.
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Formato personalizado das mensagens de log.
        
    Returns:
        Logger configurado.
        
    Example:
        >>> logger = setup_logging(log_level="DEBUG")
        >>> logger.info("Mensagem informativa")
    """
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Criar diretório de logs se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar nível de logging
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configurar handlers
    handlers = [
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
    
    # Configurar logging
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers,
        force=True  # Reconfigurar se já existir
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configurado: nível={log_level}, ficheiro={log_file}")
    
    return logger


def carregar_config(caminho: str = "config/config.yaml") -> dict:
    """Carrega configuração de um ficheiro YAML.
    
    Args:
        caminho: Caminho para o ficheiro de configuração.
        
    Returns:
        Dicionário com a configuração.
        
    Raises:
        FileNotFoundError: Se o ficheiro não existir.
        yaml.YAMLError: Se o ficheiro não for válido.
        
    Example:
        >>> config = carregar_config()
        >>> tarifa = config['tarifa']['normal']
    """
    config_path = Path(caminho)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Ficheiro de configuração não encontrado: {caminho}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def validar_diretorio(caminho: str, criar: bool = True) -> Path:
    """Valida e opcionalmente cria um diretório.
    
    Args:
        caminho: Caminho do diretório.
        criar: Se True, cria o diretório se não existir.
        
    Returns:
        Path do diretório validado.
        
    Raises:
        NotADirectoryError: Se o caminho existir e não for um diretório.
        
    Example:
        >>> data_dir = validar_diretorio("data")
        >>> print(data_dir)
        PosixPath('data')
    """
    path = Path(caminho)
    
    if path.exists():
        if not path.is_dir():
            raise NotADirectoryError(f"Caminho não é um diretório: {caminho}")
    else:
        if criar:
            path.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(f"Diretório não existe: {caminho}")
    
    return path


def formatar_numero(valor: float, decimais: int = 2) -> str:
    """Formata um número com separadores de milhares.
    
    Args:
        valor: Valor a formatar.
        decimais: Número de casas decimais.
        
    Returns:
        String formatada.
        
    Example:
        >>> formatar_numero(1234.5678, 2)
        '1,234.57'
    """
    return f"{valor:,.{decimais}f}"


def calcular_percentual(valor: float, total: float) -> float:
    """Calcula percentual de um valor em relação ao total.
    
    Args:
        valor: Valor a calcular.
        total: Total (100%).
        
    Returns:
        Percentual calculado.
        
    Raises:
        ValueError: Se total for zero.
        
    Example:
        >>> calcular_percentual(25, 100)
        25.0
    """
    if total == 0:
        raise ValueError("Total não pode ser zero")
    return (valor / total) * 100


def normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo espaços extras e convertendo para minúsculas.
    
    Args:
        texto: Texto a normalizar.
        
    Returns:
        Texto normalizado.
        
    Example:
        >>> normalizar_texto("  Exemplo de TEXTO  ")
        'exemplo de texto'
    """
    return texto.strip().lower()
