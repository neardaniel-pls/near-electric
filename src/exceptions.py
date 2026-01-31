"""Exceções personalizadas para o projeto de análise de consumo de eletricidade."""


class AnalysisError(Exception):
    """Exceção base para erros de análise de consumo."""
    pass


class DataLoadError(AnalysisError):
    """Exceção para erros de carregamento de dados."""
    pass


class InvalidDataFormatError(DataLoadError):
    """Exceção para formato de dados inválido."""
    pass


class DataValidationError(AnalysisError):
    """Exceção para erros de validação de dados."""
    pass


class DataProcessingError(AnalysisError):
    """Exceção para erros de processamento de dados."""
    pass


class ConfigurationError(AnalysisError):
    """Exceção para erros de configuração."""
    pass


class VisualizationError(AnalysisError):
    """Exceção para erros de visualização."""
    pass


class TariffError(AnalysisError):
    """Exceção para erros relacionados a tarifas."""
    pass


class ForecastError(AnalysisError):
    """Exceção para erros de previsão."""
    pass


class AlertError(AnalysisError):
    """Exceção para erros no sistema de alertas."""
    pass


class PowerAnalysisError(AnalysisError):
    """Exceção para erros na análise de potência."""
    pass
