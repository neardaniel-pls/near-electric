"""Módulo para análises estatísticas de consumo de eletricidade."""

from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from scipy import stats
import logging

from .utils import formatar_numero, calcular_percentual


logger = logging.getLogger(__name__)


class AnalisadorConsumo:
    """Classe para análise de consumo de eletricidade."""
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o analisador.
        
        Args:
            df: DataFrame com dados de consumo.
        """
        self.df = df.copy()
        self.resultados = {}
    
    def calcular_estatisticas_gerais(self) -> Dict:
        """Calcula estatísticas descritivas gerais.
        
        Returns:
            Dicionário com estatísticas.
        """
        if 'Consumo registado (kW)' not in self.df.columns:
            logger.warning("Coluna de consumo não encontrada")
            return {}
        
        consumo = self.df['Consumo registado (kW)'].dropna()
        
        estatisticas = {
            'total': consumo.sum(),
            'media': consumo.mean(),
            'mediana': consumo.median(),
            'desvio_padrao': consumo.std(),
            'minimo': consumo.min(),
            'maximo': consumo.max(),
            'percentil_25': consumo.quantile(0.25),
            'percentil_75': consumo.quantile(0.75),
            'registros': len(consumo)
        }
        
        self.resultados['estatisticas_gerais'] = estatisticas
        
        logger.info(
            f"Estatísticas gerais: Total={estatisticas['total']:.2f} kW, "
            f"Média={estatisticas['media']:.4f} kW"
        )
        
        return estatisticas
    
    def analisar_por_periodo(self, coluna_periodo: str = 'NomeMes') -> pd.DataFrame:
        """Analisa consumo por período (mês, dia da semana, hora).
        
        Args:
            coluna_periodo: Coluna para agrupamento ('NomeMes', 'NomeDiaSemana', 'HoraNum').
            
        Returns:
            DataFrame com análise por período.
        """
        if coluna_periodo not in self.df.columns:
            logger.warning(f"Coluna {coluna_periodo} não encontrada")
            return pd.DataFrame()
        
        if 'Consumo registado (kW)' not in self.df.columns:
            return pd.DataFrame()
        
        # Agrupar e calcular estatísticas
        df_periodo = self.df.groupby(coluna_periodo)['Consumo registado (kW)'].agg([
            'sum', 'mean', 'max', 'min', 'count'
        ]).round(4)
        
        df_periodo.columns = ['Total (kW)', 'Média (kW)', 'Máximo (kW)', 'Mínimo (kW)', 'Registros']
        
        # Ordenar por total
        df_periodo = df_periodo.sort_values('Total (kW)', ascending=False)
        
        logger.info(f"Análise por {coluna_periodo}: {len(df_periodo)} períodos")
        
        return df_periodo
    
    def identificar_picos(self, top_n: int = 20) -> pd.DataFrame:
        """Identifica os momentos de maior consumo.
        
        Args:
            top_n: Número de picos a identificar.
            
        Returns:
            DataFrame com os top N picos.
        """
        if 'Consumo registado (kW)' not in self.df.columns:
            return pd.DataFrame()
        
        colunas_relevantes = ['DataHora', 'Consumo registado (kW)']
        if 'Estado' in self.df.columns:
            colunas_relevantes.append('Estado')
        if 'Arquivo' in self.df.columns:
            colunas_relevantes.append('Arquivo')
        
        colunas_disponiveis = [c for c in colunas_relevantes if c in self.df.columns]
        
        picos = self.df.nlargest(top_n, 'Consumo registado (kW)')[colunas_disponiveis].copy()
        
        logger.info(f"Top {top_n} picos identificados")
        
        return picos
    
    def analisar_padroes_temporais(self) -> Dict:
        """Analisa padrões temporais de consumo.
        
        Returns:
            Dicionário com padrões identificados.
        """
        padroes = {}
        
        # Horas de pico
        if 'HoraNum' in self.df.columns and 'Consumo registado (kW)' in self.df.columns:
            media_consumo = self.df['Consumo registado (kW)'].mean()
            horas_acima_media = self.df[
                self.df['Consumo registado (kW)'] > media_consumo
            ]['HoraNum'].value_counts().head(10)
            
            padroes['horas_pico'] = {
                'media_consumo': media_consumo,
                'horas_mais_frequentes': horas_acima_media.to_dict()
            }
        
        # Dias de maior consumo
        if 'NomeDiaSemana' in self.df.columns and 'Consumo registado (kW)' in self.df.columns:
            consumo_por_dia = self.df.groupby('NomeDiaSemana')['Consumo registado (kW)'].sum()
            dia_max = consumo_por_dia.idxmax()
            dia_min = consumo_por_dia.idxmin()
            
            padroes['dias_semana'] = {
                'maior_consumo': dia_max,
                'menor_consumo': dia_min,
                'diferenca': consumo_por_dia.max() - consumo_por_dia.min()
            }
        
        # Meses de maior consumo
        if 'NomeMes' in self.df.columns and 'Ano' in self.df.columns and 'Consumo registado (kW)' in self.df.columns:
            consumo_por_mes = self.df.groupby(['Ano', 'NomeMes'])['Consumo registado (kW)'].sum()
            idx_max = consumo_por_mes.idxmax()
            idx_min = consumo_por_mes.idxmin()
            
            padroes['meses'] = {
                'maior_consumo': {'ano': idx_max[0], 'mes': idx_max[1]},
                'menor_consumo': {'ano': idx_min[0], 'mes': idx_min[1]}
            }
        
        logger.info("Padrões temporais analisados")
        
        return padroes
    
    def comparar_periodos(
        self, 
        periodo1: Tuple[int, int],
        periodo2: Tuple[int, int],
        tipo: str = 'mes'
    ) -> Dict:
        """Compara consumo entre dois períodos.
        
        Args:
            periodo1: Tupla (ano, mes) ou (ano, mes, dia) do primeiro período.
            periodo2: Tupla (ano, mes) ou (ano, mes, dia) do segundo período.
            tipo: Tipo de período ('mes', 'dia').
            
        Returns:
            Dicionário com comparação.
        """
        if 'Consumo registado (kW)' not in self.df.columns:
            return {}
        
        # Filtrar períodos
        if tipo == 'mes':
            df1 = self.df[(self.df['Ano'] == periodo1[0]) & (self.df['Mes'] == periodo1[1])]
            df2 = self.df[(self.df['Ano'] == periodo2[0]) & (self.df['Mes'] == periodo2[1])]
            label1 = f"{periodo1[1]}/{periodo1[0]}"
            label2 = f"{periodo2[1]}/{periodo2[0]}"
        else:
            logger.error(f"Tipo de período não suportado: {tipo}")
            return {}
        
        if len(df1) == 0 or len(df2) == 0:
            logger.warning("Um ou ambos os períodos não têm dados")
            return {}
        
        # Calcular estatísticas
        total1 = df1['Consumo registado (kW)'].sum()
        total2 = df2['Consumo registado (kW)'].sum()
        media1 = df1['Consumo registado (kW)'].mean()
        media2 = df2['Consumo registado (kW)'].mean()
        
        # Teste estatístico
        _, pvalor = stats.ttest_ind(
            df1['Consumo registado (kW)'].dropna(),
            df2['Consumo registado (kW)'].dropna()
        )
        
        comparacao = {
            'periodo1': {'label': label1, 'total': total1, 'media': media1},
            'periodo2': {'label': label2, 'total': total2, 'media': media2},
            'diferenca_total': total2 - total1,
            'diferenca_percentual': calcular_percentual(total2 - total1, total1),
            'pvalor': pvalor,
            'significativo': pvalor < 0.05
        }
        
        logger.info(f"Comparação entre {label1} e {label2} concluída")
        
        return comparacao
    
    def analisar_eficiencia(self, area_m2: Optional[float] = None) -> Dict:
        """Analisa eficiência do consumo.
        
        Args:
            area_m2: Área da habitação em m² (opcional).
            
        Returns:
            Dicionário com métricas de eficiência.
        """
        if 'Consumo_kWh' not in self.df.columns:
            logger.warning("Coluna 'Consumo_kWh' não encontrada")
            return {}
        
        consumo_total_kwh = self.df['Consumo_kWh'].sum()
        
        # Estimar número de dias no dataset
        if 'Data' in self.df.columns:
            dias = (self.df['Data'].max() - self.df['Data'].min()).days + 1
        else:
            dias = 30  # Valor padrão
        
        # Consumo mensal estimado
        consumo_mensal = (consumo_total_kwh / dias) * 30
        
        # Benchmarks (valores aproximados para Portugal)
        benchmarks = {
            'residencial_medio': 150,  # kWh/mês
            'residencial_eficiente': 100,  # kWh/mês
            'residencial_ineficiente': 250  # kWh/mês
        }
        
        eficiencia = {
            'consumo_total_kwh': consumo_total_kwh,
            'consumo_mensal_estimado': consumo_mensal,
            'dias_analisados': dias,
            'benchmark_medio': benchmarks['residencial_medio'],
            'vs_benchmark_medio': calcular_percentual(
                consumo_mensal - benchmarks['residencial_medio'],
                benchmarks['residencial_medio']
            ),
            'classificacao': self._classificar_eficiencia(consumo_mensal, benchmarks)
        }
        
        # Calcular por m² se área fornecida
        if area_m2 and area_m2 > 0:
            consumo_mensal_m2 = consumo_mensal / area_m2
            eficiencia['consumo_mensal_m2'] = consumo_mensal_m2
            eficiencia['area_m2'] = area_m2
        
        logger.info(f"Análise de eficiência: {eficiencia['classificacao']}")
        
        return eficiencia
    
    def _classificar_eficiencia(self, consumo_mensal: float, benchmarks: Dict) -> str:
        """Classifica a eficiência do consumo.
        
        Args:
            consumo_mensal: Consumo mensal em kWh.
            benchmarks: Dicionário com benchmarks.
            
        Returns:
            Classificação ('Eficiente', 'Normal', 'Ineficiente').
        """
        if consumo_mensal <= benchmarks['residencial_eficiente']:
            return 'Eficiente'
        elif consumo_mensal <= benchmarks['residencial_medio']:
            return 'Normal'
        else:
            return 'Ineficiente'
    
    def gerar_relatorio(self) -> Dict:
        """Gera relatório completo da análise.
        
        Returns:
            Dicionário com relatório completo.
        """
        relatorio = {
            'estatisticas_gerais': self.calcular_estatisticas_gerais(),
            'padroes_temporais': self.analisar_padroes_temporais(),
            'picos': self.identificar_picos(10).to_dict('records') if len(self.identificar_picos(10)) > 0 else [],
            'eficiencia': self.analisar_eficiencia()
        }
        
        logger.info("Relatório completo gerado")
        
        return relatorio


def calcular_estatisticas(df: pd.DataFrame) -> Dict:
    """Função conveniente para calcular estatísticas.
    
    Args:
        df: DataFrame com dados de consumo.
        
    Returns:
        Dicionário com estatísticas.
        
    Example:
        >>> estatisticas = calcular_estatisticas(df)
        >>> print(f"Total: {estatisticas['total']:.2f} kW")
    """
    analisador = AnalisadorConsumo(df)
    return analisador.calcular_estatisticas_gerais()


def identificar_picos(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Função conveniente para identificar picos.
    
    Args:
        df: DataFrame com dados de consumo.
        top_n: Número de picos a identificar.
        
    Returns:
        DataFrame com os picos.
        
    Example:
        >>> picos = identificar_picos(df, top_n=10)
        >>> print(picos.head())
    """
    analisador = AnalisadorConsumo(df)
    return analisador.identificar_picos(top_n)
