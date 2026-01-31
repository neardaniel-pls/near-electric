"""Wrapper para importar módulos do diretório src."""

# Importar todos os módulos principais para facilitar o uso
from src.utils import setup_logging, carregar_config, validar_diretorio
from src.data_loader import CarregadorDados, carregar_dados
from src.data_processor import ValidadorDados, ProcessadorDados, validar_dados, limpar_dados
from src.analyzer import AnalisadorConsumo, calcular_estatisticas, identificar_picos
from src.visualizer import VisualizadorConsumo, plotar_consumo_temporal
from src.tariff_calculator import (
    TarifaSimples, TarifaBiHoraria, TarifaTriHoraria,
    comparar_tarifas, recomendar_tarifa
)
from src.seasonal_analyzer import AnalisadorSazonal
from src.forecaster import PrevisorConsumo
from src.alerts import GestorAlertas, TipoAlerta, NivelAlerta, configurar_alertas_padrao

__all__ = [
    # utils
    'setup_logging',
    'carregar_config',
    'validar_diretorio',
    # data_loader
    'CarregadorDados',
    'carregar_dados',
    # data_processor
    'ValidadorDados',
    'ProcessadorDados',
    'validar_dados',
    'limpar_dados',
    # analyzer
    'AnalisadorConsumo',
    'calcular_estatisticas',
    'identificar_picos',
    # visualizer
    'VisualizadorConsumo',
    'plotar_consumo_temporal',
    # tariff_calculator
    'TarifaSimples',
    'TarifaBiHoraria',
    'TarifaTriHoraria',
    'comparar_tarifas',
    'recomendar_tarifa',
    # seasonal_analyzer
    'AnalisadorSazonal',
    # forecaster
    'PrevisorConsumo',
    # alerts
    'GestorAlertas',
    'TipoAlerta',
    'NivelAlerta',
    'configurar_alertas_padrao',
]
