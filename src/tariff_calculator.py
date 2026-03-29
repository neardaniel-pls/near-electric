"""Módulo para cálculo de custos com diferentes tarifas de eletricidade."""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import logging


logger = logging.getLogger(__name__)


class Tarifa(ABC):
    """Classe abstrata base para tarifas de eletricidade."""
    
    def __init__(self, nome: str, descricao: str = ""):
        """Inicializa a tarifa.
        
        Args:
            nome: Nome da tarifa.
            descricao: Descrição da tarifa.
        """
        self.nome = nome
        self.descricao = descricao
    
    @abstractmethod
    def calcular_custo(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula custo para cada registro.
        
        Args:
            df: DataFrame com colunas 'DataHora' e 'Consumo_kWh'.
            
        Returns:
            DataFrame com coluna 'Custo_EUR' adicionada.
        """
        pass
    
    @abstractmethod
    def obter_resumo(self, df: pd.DataFrame) -> Dict:
        """Obtém resumo dos custos.
        
        Args:
            df: DataFrame com coluna 'Custo_EUR'.
            
        Returns:
            Dicionário com resumo dos custos.
        """
        pass


class TarifaSimples(Tarifa):
    """Tarifa simples (único preço)."""
    
    def __init__(self, preco_kwh: float, nome: str = "Simples"):
        """Inicializa tarifa simples.
        
        Args:
            preco_kwh: Preço por kWh em €.
            nome: Nome da tarifa.
        """
        super().__init__(nome, f"Tarifa simples: €{preco_kwh}/kWh")
        self.preco_kwh = preco_kwh
    
    def calcular_custo(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula custo aplicando preço único."""
        if 'Consumo_kWh' not in df.columns:
            logger.error("Coluna 'Consumo_kWh' não encontrada")
            return df
        
        df = df.copy()
        df['Custo_EUR'] = df['Consumo_kWh'] * self.preco_kwh
        
        logger.info(f"Custo calculado com tarifa {self.nome}: €{df['Custo_EUR'].sum():.2f}")
        
        return df
    
    def obter_resumo(self, df: pd.DataFrame) -> Dict:
        """Obtém resumo dos custos."""
        if 'Custo_EUR' not in df.columns:
            return {}
        
        return {
            'tarifa': self.nome,
            'custo_total': df['Custo_EUR'].sum(),
            'custo_medio': df['Custo_EUR'].mean(),
            'custo_max': df['Custo_EUR'].max(),
            'preco_kwh': self.preco_kwh
        }


class TarifaBiHoraria(Tarifa):
    """Tarifa bi-horária (vazio e cheio)."""
    
    def __init__(
        self, 
        preco_vazio: float, 
        preco_cheio: float,
        horas_vazio: List[Tuple[int, int]] = None,
        nome: str = "Bi-horária"
    ):
        """Inicializa tarifa bi-horária.
        
        Args:
            preco_vazio: Preço por kWh em horário de vazio.
            preco_cheio: Preço por kWh em horário de cheio.
            horas_vazio: Lista de tuplas (inicio, fim) para horário de vazio.
                         Default: [(0, 7), (22, 24)] (00h-07h e 22h-24h).
            nome: Nome da tarifa.
        """
        super().__init__(
            nome, 
            f"Tarifa bi-horária: Vazio €{preco_vazio}/kWh, Cheio €{preco_cheio}/kWh"
        )
        self.preco_vazio = preco_vazio
        self.preco_cheio = preco_cheio
        self.horas_vazio = horas_vazio or [(0, 7), (22, 24)]
    
    def _eh_horario_vazio(self, hora: int) -> bool:
        """Verifica se uma hora está no horário de vazio.
        
        Args:
            hora: Hora do dia (0-23).
            
        Returns:
            True se for horário de vazio, False caso contrário.
        """
        for inicio, fim in self.horas_vazio:
            if inicio <= hora < fim:
                return True
        return False
    
    def calcular_custo(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula custo aplicando tarifa bi-horária."""
        if 'Consumo_kWh' not in df.columns:
            logger.error("Coluna 'Consumo_kWh' não encontrada")
            return df
        
        df = df.copy()
        
        df['Preco_kWh'] = np.select(
            [
                df['HoraNum'].between(0, 6, inclusive='both'),
                df['HoraNum'].between(22, 23, inclusive='both'),
            ],
            [self.preco_vazio, self.preco_vazio],
            default=self.preco_cheio
        )
        df['Horario'] = np.where(df['Preco_kWh'] == self.preco_vazio, 'vazio', 'cheio')
        
        # Calcular custo
        df['Custo_EUR'] = df['Consumo_kWh'] * df['Preco_kWh']
        
        # Estatísticas
        custo_vazio = df[df['Horario'] == 'vazio']['Custo_EUR'].sum()
        custo_cheio = df[df['Horario'] == 'cheio']['Custo_EUR'].sum()
        
        logger.info(
            f"Custo calculado com tarifa {self.nome}: "
            f"Total €{df['Custo_EUR'].sum():.2f} "
            f"(Vazio: €{custo_vazio:.2f}, Cheio: €{custo_cheio:.2f})"
        )
        
        return df
    
    def obter_resumo(self, df: pd.DataFrame) -> Dict:
        """Obtém resumo dos custos."""
        if 'Custo_EUR' not in df.columns or 'Horario' not in df.columns:
            return {}
        
        custo_vazio = df[df['Horario'] == 'vazio']['Custo_EUR'].sum()
        custo_cheio = df[df['Horario'] == 'cheio']['Custo_EUR'].sum()
        consumo_vazio = df[df['Horario'] == 'vazio']['Consumo_kWh'].sum()
        consumo_cheio = df[df['Horario'] == 'cheio']['Consumo_kWh'].sum()
        
        return {
            'tarifa': self.nome,
            'custo_total': df['Custo_EUR'].sum(),
            'custo_vazio': custo_vazio,
            'custo_cheio': custo_cheio,
            'consumo_vazio_kwh': consumo_vazio,
            'consumo_cheio_kwh': consumo_cheio,
            'percentual_vazio': (custo_vazio / df['Custo_EUR'].sum()) * 100,
            'percentual_cheio': (custo_cheio / df['Custo_EUR'].sum()) * 100,
            'preco_vazio': self.preco_vazio,
            'preco_cheio': self.preco_cheio
        }


class TarifaTriHoraria(Tarifa):
    """Tarifa tri-horária (vazio, ponta e cheio)."""
    
    def __init__(
        self,
        preco_vazio: float,
        preco_ponta: float,
        preco_cheio: float,
        horas_vazio: List[Tuple[int, int]] = None,
        horas_ponta: List[Tuple[int, int]] = None,
        nome: str = "Tri-horária"
    ):
        """Inicializa tarifa tri-horária.
        
        Args:
            preco_vazio: Preço por kWh em horário de vazio.
            preco_ponta: Preço por kWh em horário de ponta.
            preco_cheio: Preço por kWh em horário de cheio.
            horas_vazio: Lista de tuplas (inicio, fim) para horário de vazio.
                         Default: [(0, 7), (22, 24)].
            horas_ponta: Lista de tuplas (inicio, fim) para horário de ponta.
                         Default: [(18, 21)].
            nome: Nome da tarifa.
        """
        super().__init__(
            nome,
            f"Tarifa tri-horária: Vazio €{preco_vazio}/kWh, "
            f"Ponta €{preco_ponta}/kWh, Cheio €{preco_cheio}/kWh"
        )
        self.preco_vazio = preco_vazio
        self.preco_ponta = preco_ponta
        self.preco_cheio = preco_cheio
        self.horas_vazio = horas_vazio or [(0, 7), (22, 24)]
        self.horas_ponta = horas_ponta or [(18, 21)]
    
    def _determinar_periodo(self, hora: int) -> str:
        """Determina o período (vazio, ponta ou cheio).
        
        Args:
            hora: Hora do dia (0-23).
            
        Returns:
            Período ('vazio', 'ponta' ou 'cheio').
        """
        # Verificar se é horário de vazio
        for inicio, fim in self.horas_vazio:
            if inicio <= hora < fim:
                return 'vazio'
        
        # Verificar se é horário de ponta
        for inicio, fim in self.horas_ponta:
            if inicio <= hora < fim:
                return 'ponta'
        
        # Caso contrário, é horário de cheio
        return 'cheio'
    
    def calcular_custo(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula custo aplicando tarifa tri-horária."""
        if 'Consumo_kWh' not in df.columns:
            logger.error("Coluna 'Consumo_kWh' não encontrada")
            return df
        
        df = df.copy()
        
        # Determinar período
        df['Periodo'] = df['HoraNum'].apply(self._determinar_periodo)
        
        # Aplicar preços
        precos = {
            'vazio': self.preco_vazio,
            'ponta': self.preco_ponta,
            'cheio': self.preco_cheio
        }
        df['Preco_kWh'] = df['Periodo'].map(precos)
        
        # Calcular custo
        df['Custo_EUR'] = df['Consumo_kWh'] * df['Preco_kWh']
        
        # Estatísticas
        custo_vazio = df[df['Periodo'] == 'vazio']['Custo_EUR'].sum()
        custo_ponta = df[df['Periodo'] == 'ponta']['Custo_EUR'].sum()
        custo_cheio = df[df['Periodo'] == 'cheio']['Custo_EUR'].sum()
        
        logger.info(
            f"Custo calculado com tarifa {self.nome}: "
            f"Total €{df['Custo_EUR'].sum():.2f} "
            f"(Vazio: €{custo_vazio:.2f}, Ponta: €{custo_ponta:.2f}, Cheio: €{custo_cheio:.2f})"
        )
        
        return df
    
    def obter_resumo(self, df: pd.DataFrame) -> Dict:
        """Obtém resumo dos custos."""
        if 'Custo_EUR' not in df.columns or 'Periodo' not in df.columns:
            return {}
        
        resumo = {
            'tarifa': self.nome,
            'custo_total': df['Custo_EUR'].sum(),
            'preco_vazio': self.preco_vazio,
            'preco_ponta': self.preco_ponta,
            'preco_cheio': self.preco_cheio
        }
        
        for periodo in ['vazio', 'ponta', 'cheio']:
            df_periodo = df[df['Periodo'] == periodo]
            resumo[f'custo_{periodo}'] = df_periodo['Custo_EUR'].sum()
            resumo[f'consumo_{periodo}_kwh'] = df_periodo['Consumo_kWh'].sum()
            resumo[f'percentual_{periodo}'] = (
                df_periodo['Custo_EUR'].sum() / df['Custo_EUR'].sum() * 100
            )
        
        return resumo


def comparar_tarifas(
    df: pd.DataFrame, 
    tarifas: List[Tarifa]
) -> pd.DataFrame:
    """Compara custos entre diferentes tarifas.
    
    Args:
        df: DataFrame com colunas 'DataHora', 'HoraNum', 'Consumo_kWh'.
        tarifas: Lista de objetos Tarifa.
        
    Returns:
        DataFrame com comparação de custos.
        
    Example:
        >>> tarifas = [
        ...     TarifaSimples(0.25),
        ...     TarifaBiHoraria(0.104, 0.2584)
        ... ]
        >>> comparacao = comparar_tarifas(df, tarifas)
    """
    resultados = []
    
    for tarifa in tarifas:
        df_custo = tarifa.calcular_custo(df)
        resumo = tarifa.obter_resumo(df_custo)
        resultados.append(resumo)
    
    df_comparacao = pd.DataFrame(resultados)
    
    # Ordenar por custo total
    df_comparacao = df_comparacao.sort_values('custo_total').reset_index(drop=True)
    
    logger.info("Comparação de tarifas concluída")
    
    return df_comparacao


def recomendar_tarifa(
    df: pd.DataFrame, 
    tarifas: List[Tarifa]
) -> Tuple[Tarifa, Dict]:
    """Recomenda a tarifa mais económica.
    
    Args:
        df: DataFrame com colunas 'DataHora', 'HoraNum', 'Consumo_kWh'.
        tarifas: Lista de objetos Tarifa.
        
    Returns:
        Tupla com (tarifa recomendada, resumo de custos).
        
    Example:
        >>> tarifas = [
        ...     TarifaSimples(0.25),
        ...     TarifaBiHoraria(0.104, 0.2584)
        ... ]
        >>> tarifa, resumo = recomendar_tarifa(df, tarifas)
        >>> print(f"Recomendado: {tarifa.nome}")
    """
    df_comparacao = comparar_tarifas(df, tarifas)
    
    # Encontrar tarifa mais económica
    idx_melhor = df_comparacao['custo_total'].idxmin()
    melhor_nome = df_comparacao.loc[idx_melhor, 'tarifa']
    melhor_tarifa = next(t for t in tarifas if t.nome == melhor_nome)
    melhor_resumo = df_comparacao.loc[idx_melhor].to_dict()
    
    # Calcular economia em relação à mais cara
    idx_pior = df_comparacao['custo_total'].idxmax()
    pior_custo = df_comparacao.loc[idx_pior, 'custo_total']
    pior_nome = df_comparacao.loc[idx_pior, 'tarifa']
    economia = pior_custo - melhor_resumo['custo_total']
    
    logger.info(
        f"Tarifa recomendada: {melhor_tarifa.nome} "
        f"(economia de €{economia:.2f} vs {pior_nome})"
    )
    
    return melhor_tarifa, melhor_resumo
