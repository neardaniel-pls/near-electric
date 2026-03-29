"""Módulo para processamento e validação de dados de consumo."""

from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from scipy import stats
import logging

from .utils import calcular_percentual


logger = logging.getLogger(__name__)


class ValidadorDados:
    """Classe para validar qualidade dos dados."""
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o validador.
        
        Args:
            df: DataFrame a validar.
        """
        self.df = df.copy()
        self.relatorio = {
            'registros_faltantes': [],
            'valores_anomalos': [],
            'inconsistencias_temporais': [],
            'estatisticas': {}
        }
    
    def validar(self) -> Dict:
        """Executa todas as validações e retorna relatório.
        
        Returns:
            Dicionário com relatório de validação.
        """
        logger.info("Iniciando validação de dados...")
        
        self._verificar_valores_negativos()
        self._verificar_valores_nulos()
        self._verificar_continuidade_temporal()
        self._detectar_outliers()
        self._calcular_estatisticas()
        
        total_problemas = (
            len(self.relatorio['registros_faltantes']) +
            len(self.relatorio['valores_anomalos']) +
            len(self.relatorio['inconsistencias_temporais'])
        )
        
        logger.info(f"Validação concluída. Problemas encontrados: {total_problemas}")
        
        return self.relatorio
    
    def _verificar_valores_negativos(self) -> None:
        """Verifica se há valores de consumo negativos."""
        if 'Consumo registado (kW)' not in self.df.columns:
            return
        
        negativos = self.df[self.df['Consumo registado (kW)'] < 0]
        
        if len(negativos) > 0:
            logger.warning(f"Encontrados {len(negativos)} valores negativos de consumo")
            self.relatorio['valores_anomalos'].append({
                'tipo': 'valores_negativos',
                'quantidade': len(negativos),
                'exemplos': negativos.head(5).to_dict('records')
            })
    
    def _verificar_valores_nulos(self) -> None:
        """Verifica se há valores nulos."""
        nulos_por_coluna = self.df.isnull().sum()
        
        colunas_com_nulos = nulos_por_coluna[nulos_por_coluna > 0]
        
        if len(colunas_com_nulos) > 0:
            logger.warning(f"Encontrados valores nulos em {len(colunas_com_nulos)} colunas")
            self.relatorio['valores_anomalos'].append({
                'tipo': 'valores_nulos',
                'colunas': colunas_com_nulos.to_dict()
            })
    
    def _verificar_continuidade_temporal(self) -> None:
        """Verifica se há lacunas na série temporal."""
        if 'DataHora' not in self.df.columns:
            return
        
        df_ordenado = self.df.sort_values('DataHora')
        diferenca = df_ordenado['DataHora'].diff()
        
        # Intervalo esperado: 15 minutos
        intervalo_esperado = pd.Timedelta(minutes=15)
        
        # Encontrar lacunas maiores que 15 minutos
        lacunas = diferenca[diferenca > intervalo_esperado]
        
        if len(lacunas) > 0:
            logger.warning(f"Encontradas {len(lacunas)} lacunas temporais")
            self.relatorio['inconsistencias_temporais'].append({
                'tipo': 'lacunas_temporais',
                'quantidade': len(lacunas),
                'maxima': lacunas.max(),
                'exemplos': lacunas.head(5).tolist()
            })
    
    def _detectar_outliers(self) -> None:
        """Detecta outliers usando Z-score."""
        if 'Consumo registado (kW)' not in self.df.columns:
            return
        
        consumo = self.df['Consumo registado (kW)'].dropna()
        
        if len(consumo) == 0:
            return
        
        # Calcular Z-score
        z_scores = np.abs(stats.zscore(consumo))
        
        # Outliers: Z-score > 3
        outliers = consumo[z_scores > 3]
        
        if len(outliers) > 0:
            logger.warning(f"Encontrados {len(outliers)} outliers (Z-score > 3)")
            self.relatorio['valores_anomalos'].append({
                'tipo': 'outliers',
                'quantidade': len(outliers),
                'percentual': calcular_percentual(len(outliers), len(consumo)),
                'maximo': outliers.max(),
                'minimo': outliers.min()
            })
    
    def _calcular_estatisticas(self) -> None:
        """Calcula estatísticas básicas dos dados."""
        if 'Consumo registado (kW)' not in self.df.columns:
            return
        
        consumo = self.df['Consumo registado (kW)'].dropna()
        
        if len(consumo) == 0:
            return
        
        self.relatorio['estatisticas'] = {
            'total_registros': len(self.df),
            'registros_validos': len(consumo),
            'media': consumo.mean(),
            'mediana': consumo.median(),
            'desvio_padrao': consumo.std(),
            'minimo': consumo.min(),
            'maximo': consumo.max(),
            'percentil_25': consumo.quantile(0.25),
            'percentil_75': consumo.quantile(0.75)
        }


class ProcessadorDados:
    """Classe para processamento de dados."""
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o processador.
        
        Args:
            df: DataFrame a processar.
        """
        self.df_original = df.copy()
        self.df_processado = df.copy()
    
    def limpar_dados(self, estrategia: str = 'remover') -> pd.DataFrame:
        """Limpa os dados removendo ou preenchendo valores inválidos.
        
        Args:
            estrategia: Estratégia de limpeza ('remover', 'media', 'zero').
            
        Returns:
            DataFrame limpo.
        """
        logger.info(f"Limpeza de dados com estratégia: {estrategia}")
        
        if 'Consumo registado (kW)' not in self.df_processado.columns:
            return self.df_processado
        
        # Remover valores negativos
        self.df_processado = self.df_processado[
            self.df_processado['Consumo registado (kW)'] >= 0
        ]
        
        # Tratar valores nulos
        if estrategia == 'remover':
            self.df_processado = self.df_processado.dropna(
                subset=['Consumo registado (kW)']
            )
        elif estrategia == 'media':
            media = self.df_processado['Consumo registado (kW)'].mean()
            self.df_processado = self.df_processado.copy()
            self.df_processado['Consumo registado (kW)'] = self.df_processado['Consumo registado (kW)'].fillna(media)
        elif estrategia == 'zero':
            self.df_processado = self.df_processado.copy()
            self.df_processado['Consumo registado (kW)'] = self.df_processado['Consumo registado (kW)'].fillna(0)
        
        logger.info(
            f"Limpeza concluída. "
            f"Registros originais: {len(self.df_original)}, "
            f"Registros após limpeza: {len(self.df_processado)}"
        )
        
        return self.df_processado
    
    def adicionar_colunas_calculadas(self, tarifa: float = 0.25) -> pd.DataFrame:
        """Adiciona colunas calculadas (kWh, custo).
        
        Args:
            tarifa: Tarifa em €/kWh.
            
        Returns:
            DataFrame com colunas adicionais.
        """
        if 'Consumo registado (kW)' not in self.df_processado.columns:
            logger.warning("Coluna de consumo não encontrada")
            return self.df_processado
        
        # Converter kW para kWh (cada registro é de 15 minutos = 0.25 horas)
        self.df_processado['Consumo_kWh'] = (
            self.df_processado['Consumo registado (kW)'] * 0.25
        )
        
        # Calcular custo
        self.df_processado['Custo_EUR'] = (
            self.df_processado['Consumo_kWh'] * tarifa
        )
        
        logger.info(
            f"Colunas calculadas adicionadas. "
            f"Custo total: €{self.df_processado['Custo_EUR'].sum():.2f}"
        )
        
        return self.df_processado
    
    def agregar_por_periodo(
        self, 
        periodo: str = 'mes',
        colunas: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Agrega dados por período (dia, semana, mês, ano).
        
        Args:
            periodo: Período de agregação ('dia', 'semana', 'mes', 'ano').
            colunas: Colunas a agregar (default: ['Consumo_kWh', 'Custo_EUR']).
            
        Returns:
            DataFrame agregado.
        """
        if colunas is None:
            colunas = ['Consumo_kWh', 'Custo_EUR']
        
        # Filtrar apenas colunas que existem
        colunas_validas = [c for c in colunas if c in self.df_processado.columns]
        
        if not colunas_validas:
            logger.warning("Nenhuma coluna válida para agregação")
            return pd.DataFrame()
        
        # Definir agrupamento
        if periodo == 'dia':
            groupby = [self.df_processado['Data'].dt.date]
        elif periodo == 'semana':
            iso = self.df_processado['Data'].dt.isocalendar()
            groupby = [iso.year, iso.week]
        elif periodo == 'mes':
            groupby = [self.df_processado['Ano'], self.df_processado['Mes']]
        elif periodo == 'ano':
            groupby = [self.df_processado['Ano']]
        else:
            logger.error(f"Período inválido: {periodo}")
            return pd.DataFrame()
        
        # Agregar
        df_agregado = self.df_processado.groupby(groupby)[colunas_validas].agg(['sum', 'mean', 'max', 'min'])
        
        logger.info(f"Agregação por {periodo} concluída: {len(df_agregado)} grupos")
        
        return df_agregado
    
    def obter_resumo(self) -> Dict:
        """Obtém resumo dos dados processados.
        
        Returns:
            Dicionário com resumo dos dados.
        """
        resumo = {
            'registros': len(self.df_processado),
            'periodo': {
                'inicio': self.df_processado['Data'].min() if len(self.df_processado) > 0 else None,
                'fim': self.df_processado['Data'].max() if len(self.df_processado) > 0 else None,
            },
        }
        
        if 'Consumo_kWh' in self.df_processado.columns:
            resumo['consumo'] = {
                'total_kWh': self.df_processado['Consumo_kWh'].sum(),
                'media_kWh': self.df_processado['Consumo_kWh'].mean(),
                'max_kWh': self.df_processado['Consumo_kWh'].max(),
            }
        
        if 'Custo_EUR' in self.df_processado.columns:
            resumo['custo'] = {
                'total_EUR': self.df_processado['Custo_EUR'].sum(),
                'media_EUR': self.df_processado['Custo_EUR'].mean(),
            }
        
        return resumo

