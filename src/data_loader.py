"""Módulo para carregamento de dados de consumo de eletricidade."""

import glob
import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Any
import pandas as pd
import logging

from .utils import validar_diretorio
from .exceptions import DataLoadError, InvalidDataFormatError


logger = logging.getLogger(__name__)


class CarregadorDados:
    """Classe para carregar e gerenciar dados de consumo de eletricidade."""
    
    COLUNAS_ESPERADAS = ['Data', 'Hora', 'Consumo registado (kW)', 'Estado']
    
    def __init__(self, data_dir: str = "data"):
        """Inicializa o carregador de dados.
        
        Args:
            data_dir: Diretório onde estão os ficheiros CSV.
        """
        self.data_dir = validar_diretorio(data_dir)
        self.dfs = []
        self.nomes_arquivos = []
        self.df_completo = None
        
    def listar_csvs(self) -> List[str]:
        """Lista todos os ficheiros CSV no diretório de dados.
        
        Returns:
            Lista ordenada de caminhos para ficheiros CSV.
        """
        padrao = os.path.join(self.data_dir, '*.csv')
        csv_files = sorted(glob.glob(padrao))
        
        logger.info(f"Ficheiros CSV encontrados em '{self.data_dir}/': {len(csv_files)}")
        for i, file in enumerate(csv_files, 1):
            logger.debug(f"  {i}. {os.path.basename(file)}")
        
        return csv_files
    
    def carregar_csv(self, caminho: str) -> Tuple[pd.DataFrame, str]:
        """Carrega um ficheiro CSV e retorna DataFrame processado.
        
        Args:
            caminho: Caminho para o ficheiro CSV.
            
        Returns:
            Tupla com (DataFrame processado, nome do ficheiro).
            
        Raises:
            DataLoadError: Se houver erro ao carregar o ficheiro.
            InvalidDataFormatError: Se o ficheiro não tiver as colunas esperadas.
        """
        if not Path(caminho).exists():
            raise DataLoadError(f"Ficheiro não encontrado: {caminho}")
        
        nome_ficheiro = os.path.basename(caminho)
        logger.debug(f"Carregando: {nome_ficheiro}")
        
        try:
            # Carregar o ficheiro
            df = pd.read_csv(caminho, encoding='utf-8-sig')
        except Exception as e:
            logger.error(f"Erro ao ler ficheiro {caminho}: {e}")
            raise DataLoadError(f"Erro ao ler ficheiro {caminho}: {e}") from e
        
        # Validar colunas
        self._validar_estrutura(df, caminho)
        
        # Adicionar coluna com o nome do ficheiro/mês
        df['Arquivo'] = nome_ficheiro
        
        # Converter colunas de data e hora para datetime
        try:
            df['Data'] = pd.to_datetime(df['Data'], format='%Y/%m/%d')
            df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M').dt.time
        except Exception as e:
            logger.error(f"Erro ao converter datas em {caminho}: {e}")
            raise ValueError(f"Formato de data/hora inválido em {caminho}")
        
        # Criar coluna datetime combinada
        df['DataHora'] = df.apply(
            lambda row: datetime.combine(row['Data'], row['Hora']), 
            axis=1
        )
        
        # Criar colunas adicionais para análise
        df['Dia'] = df['Data'].dt.day
        df['Mes'] = df['Data'].dt.month
        df['Ano'] = df['Data'].dt.year
        df['DiaSemana'] = df['Data'].dt.dayofweek
        df['NomeDiaSemana'] = df['Data'].dt.day_name()
        df['NomeMes'] = df['Data'].dt.month_name()
        df['HoraNum'] = df['DataHora'].dt.hour
        
        # Converter consumo para numérico
        df['Consumo registado (kW)'] = pd.to_numeric(
            df['Consumo registado (kW)'], 
            errors='coerce'
        )
        
        logger.info(f"✓ Carregado: {nome_ficheiro} ({len(df)} registros)")
        
        return df, nome_ficheiro
    
    def carregar_todos(self) -> pd.DataFrame:
        """Carrega todos os ficheiros CSV e combina em um DataFrame.
        
        Returns:
            DataFrame combinado com todos os dados.
        """
        csv_files = self.listar_csvs()
        
        if not csv_files:
            logger.warning("Nenhum ficheiro CSV encontrado.")
            return pd.DataFrame()
        
        self.dfs = []
        self.nomes_arquivos = []
        
        for arquivo in csv_files:
            try:
                df, nome = self.carregar_csv(arquivo)
                self.dfs.append(df)
                self.nomes_arquivos.append(nome)
            except Exception as e:
                logger.error(f"Falha ao carregar {arquivo}: {e}")
                continue
        
        if not self.dfs:
            logger.error("Nenhum ficheiro foi carregado com sucesso.")
            return pd.DataFrame()
        
        # Combinar todos os DataFrames
        self.df_completo = pd.concat(self.dfs, ignore_index=True)
        
        logger.info(f"Total de registros combinados: {len(self.df_completo)}")
        
        return self.df_completo
    
    def filtrar_estado(self, df: pd.DataFrame, estado: str = 'Real') -> pd.DataFrame:
        """Filtra DataFrame por estado (Real ou Estimado).
        
        Args:
            df: DataFrame a filtrar.
            estado: Estado a filtrar ('Real' ou 'Estimado').
            
        Returns:
            DataFrame filtrado.
        """
        if 'Estado' not in df.columns:
            logger.warning("Coluna 'Estado' não encontrada no DataFrame.")
            return df.copy()
        
        df_filtrado = df[df['Estado'] == estado].copy()
        
        logger.info(
            f"Registros {estado}: {len(df_filtrado)} "
            f"({len(df_filtrado)/len(df)*100:.1f}% do total)"
        )
        
        return df_filtrado
    
    def _validar_estrutura(self, df: pd.DataFrame, caminho: str) -> None:
        """Valida se o DataFrame tem a estrutura esperada.
        
        Args:
            df: DataFrame a validar.
            caminho: Caminho do ficheiro (para logging).
            
        Raises:
            InvalidDataFormatError: Se o DataFrame não tiver as colunas esperadas.
        """
        colunas_faltantes = set(self.COLUNAS_ESPERADAS) - set(df.columns)
        
        if colunas_faltantes:
            raise InvalidDataFormatError(
                f"Ficheiro {caminho} não tem as colunas esperadas. "
                f"Faltam: {colunas_faltantes}"
            )
        
        logger.debug(f"Estrutura validada para {caminho}")
    
    def obter_info_dataset(self, df: pd.DataFrame) -> dict:
        """Obtém informações sobre o dataset.
        
        Args:
            df: DataFrame a analisar.
            
        Returns:
            Dicionário com informações do dataset.
        """
        info = {
            'total_registros': len(df),
            'periodo': {
                'inicio': df['Data'].min().strftime('%Y-%m-%d') if len(df) > 0 else None,
                'fim': df['Data'].max().strftime('%Y-%m-%d') if len(df) > 0 else None,
            },
            'meses': df['NomeMes'].unique().tolist() if 'NomeMes' in df.columns else [],
            'anos': df['Ano'].unique().tolist() if 'Ano' in df.columns else [],
            'estados': df['Estado'].value_counts().to_dict() if 'Estado' in df.columns else {},
        }
        
        return info


def carregar_dados(data_dir: str = "data") -> Tuple[pd.DataFrame, CarregadorDados]:
    """Função conveniente para carregar todos os dados.
    
    Args:
        data_dir: Diretório onde estão os ficheiros CSV.
        
    Returns:
        Tupla com (DataFrame combinado, instância do CarregadorDados).
        
    Example:
        >>> df, carregador = carregar_dados()
        >>> print(f"Carregados {len(df)} registros")
    """
    carregador = CarregadorDados(data_dir)
    df = carregador.carregar_todos()
    return df, carregador
