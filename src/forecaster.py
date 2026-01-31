#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para previsão de consumo de eletricidade.

Este módulo fornece funcionalidades para prever consumo futuro
usando técnicas de séries temporais e modelos estatísticos.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PrevisorConsumo:
    """Classe para previsão de consumo de eletricidade."""
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o previsor de consumo.
        
        Args:
            df: DataFrame com dados históricos de consumo.
                  Deve conter colunas: 'DataHora', 'Consumo registado (kW)', etc.
        """
        self.df = df.copy()
        self._validar_colunas()
        logger.info(f"PrevisorConsumo inicializado com {len(df)} registros")
    
    def _validar_colunas(self):
        """Valida se as colunas necessárias existem."""
        colunas_necessarias = ['DataHora', 'Consumo registado (kW)']
        for coluna in colunas_necessarias:
            if coluna not in self.df.columns:
                raise ValueError(f"Coluna necessária não encontrada: {coluna}")
    
    def prever_media_movel(
        self,
        dias_futuros: int = 7,
        janela: int = 7
    ) -> pd.DataFrame:
        """Prevê consumo usando média móvel simples.
        
        Args:
            dias_futuros: Número de dias para prever.
            janela: Tamanho da janela para média móvel.
            
        Returns:
            DataFrame com previsões.
        """
        logger.info(f"Previsão por média móvel: {dias_futuros} dias, janela={janela}")
        
        # Ordenar por data
        df_ordenado = self.df.sort_values('DataHora').copy()
        
        # Calcular média móvel
        df_ordenado['MediaMovel'] = df_ordenado['Consumo registado (kW)'].rolling(
            window=janela, min_periods=1
        ).mean()
        
        # Obter última média móvel
        ultima_media = df_ordenado['MediaMovel'].iloc[-1]
        
        # Criar datas futuras
        ultima_data = df_ordenado['DataHora'].iloc[-1]
        datas_futuras = [ultima_data + timedelta(hours=i) for i in range(1, dias_futuros * 24 + 1)]
        
        # Criar DataFrame de previsão
        df_previsao = pd.DataFrame({
            'DataHora': datas_futuras,
            'Consumo_Previsto (kW)': ultima_media,
            'Metodo': 'MediaMovel'
        })
        
        logger.info(f"Previsão gerada: {len(df_previsao)} pontos")
        return df_previsao
    
    def prever_por_padrao_semanal(
        self,
        dias_futuros: int = 7
    ) -> pd.DataFrame:
        """Prevê consumo baseando-se no padrão semanal histórico.
        
        Args:
            dias_futuros: Número de dias para prever.
            
        Returns:
            DataFrame com previsões.
        """
        logger.info(f"Previsão por padrão semanal: {dias_futuros} dias")
        
        # Calcular padrão semanal (média por hora e dia da semana)
        padrao = self.df.groupby(['DiaSemana', 'HoraNum'])['Consumo registado (kW)'].mean()
        
        # Obter última data
        ultima_data = self.df['DataHora'].iloc[-1]
        
        # Gerar datas futuras
        datas_futuras = []
        consumos_previstos = []
        
        for i in range(1, dias_futuros * 24 + 1):
            data_futura = ultima_data + timedelta(hours=i)
            dia_semana = data_futura.weekday()
            hora = data_futura.hour
            
            # Obter consumo previsto do padrão
            if (dia_semana, hora) in padrao.index:
                consumo = padrao[(dia_semana, hora)]
            else:
                # Se não houver dados para essa combinação, usar média geral
                consumo = self.df['Consumo registado (kW)'].mean()
            
            datas_futuras.append(data_futura)
            consumos_previstos.append(consumo)
        
        df_previsao = pd.DataFrame({
            'DataHora': datas_futuras,
            'Consumo_Previsto (kW)': consumos_previstos,
            'Metodo': 'PadraoSemanal'
        })
        
        logger.info(f"Previsão gerada: {len(df_previsao)} pontos")
        return df_previsao
    
    def prever_por_padrao_diario(
        self,
        dias_futuros: int = 7
    ) -> pd.DataFrame:
        """Prevê consumo baseando-se no padrão diário médio.
        
        Args:
            dias_futuros: Número de dias para prever.
            
        Returns:
            DataFrame com previsões.
        """
        logger.info(f"Previsão por padrão diário: {dias_futuros} dias")
        
        # Calcular padrão diário (média por hora)
        padrao = self.df.groupby('HoraNum')['Consumo registado (kW)'].mean()
        
        # Obter última data
        ultima_data = self.df['DataHora'].iloc[-1]
        
        # Gerar datas futuras
        datas_futuras = []
        consumos_previstos = []
        
        for i in range(1, dias_futuros * 24 + 1):
            data_futura = ultima_data + timedelta(hours=i)
            hora = data_futura.hour
            
            # Obter consumo previsto do padrão
            if hora in padrao.index:
                consumo = padrao[hora]
            else:
                # Se não houver dados para essa hora, usar média geral
                consumo = self.df['Consumo registado (kW)'].mean()
            
            datas_futuras.append(data_futura)
            consumos_previstos.append(consumo)
        
        df_previsao = pd.DataFrame({
            'DataHora': datas_futuras,
            'Consumo_Previsto (kW)': consumos_previstos,
            'Metodo': 'PadraoDiario'
        })
        
        logger.info(f"Previsão gerada: {len(df_previsao)} pontos")
        return df_previsao
    
    def prever_por_tendencia(
        self,
        dias_futuros: int = 7,
        janela: int = 30
    ) -> pd.DataFrame:
        """Prevê consumo usando tendência linear.
        
        Args:
            dias_futuros: Número de dias para prever.
            janela: Número de dias para calcular tendência.
            
        Returns:
            DataFrame com previsões.
        """
        logger.info(f"Previsão por tendência: {dias_futuros} dias, janela={janela}")
        
        # Ordenar por data
        df_ordenado = self.df.sort_values('DataHora').copy()
        
        # Filtrar últimos dias para calcular tendência
        data_limite = df_ordenado['DataHora'].iloc[-1] - timedelta(days=janela)
        df_tendencia = df_ordenado[df_ordenado['DataHora'] >= data_limite]
        
        # Calcular tendência linear
        x = np.arange(len(df_tendencia))
        y = df_tendencia['Consumo registado (kW)'].values
        
        # Regressão linear simples
        coeficiente = np.polyfit(x, y, 1)
        tendencia = np.poly1d(coeficiente)
        
        # Prever valores futuros
        datas_futuras = []
        consumos_previstos = []
        
        for i in range(1, dias_futuros * 24 + 1):
            data_futura = df_ordenado['DataHora'].iloc[-1] + timedelta(hours=i)
            x_futuro = len(df_tendencia) + i
            consumo = tendencia(x_futuro)
            
            # Garantir que o consumo não seja negativo
            consumo = max(consumo, 0)
            
            datas_futuras.append(data_futura)
            consumos_previstos.append(consumo)
        
        df_previsao = pd.DataFrame({
            'DataHora': datas_futuras,
            'Consumo_Previsto (kW)': consumos_previstos,
            'Metodo': 'Tendencia'
        })
        
        logger.info(f"Previsão gerada: {len(df_previsao)} pontos")
        return df_previsao
    
    def prever_ensemble(
        self,
        dias_futuros: int = 7,
        pesos: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """Prevê usando ensemble de múltiplos métodos.
        
        Args:
            dias_futuros: Número de dias para prever.
            pesos: Dicionário com pesos para cada método.
                    Se None, usa pesos iguais.
            
        Returns:
            DataFrame com previsões ensemble.
        """
        logger.info(f"Previsão ensemble: {dias_futuros} dias")
        
        # Gerar previsões com diferentes métodos
        df_media_movel = self.prever_media_movel(dias_futuros)
        df_padrao_semanal = self.prever_por_padrao_semanal(dias_futuros)
        df_padrao_diario = self.prever_por_padrao_diario(dias_futuros)
        
        # Definir pesos padrão se não fornecidos
        if pesos is None:
            pesos = {
                'MediaMovel': 0.2,
                'PadraoSemanal': 0.5,
                'PadraoDiario': 0.3
            }
        
        # Criar DataFrame combinado
        df_ensemble = pd.DataFrame({
            'DataHora': df_media_movel['DataHora']
        })
        
        # Adicionar previsões de cada método
        df_ensemble['MediaMovel'] = df_media_movel['Consumo_Previsto (kW)']
        df_ensemble['PadraoSemanal'] = df_padrao_semanal['Consumo_Previsto (kW)']
        df_ensemble['PadraoDiario'] = df_padrao_diario['Consumo_Previsto (kW)']
        
        # Calcular média ponderada
        df_ensemble['Consumo_Previsto (kW)'] = (
            df_ensemble['MediaMovel'] * pesos['MediaMovel'] +
            df_ensemble['PadraoSemanal'] * pesos['PadraoSemanal'] +
            df_ensemble['PadraoDiario'] * pesos['PadraoDiario']
        )
        
        df_ensemble['Metodo'] = 'Ensemble'
        
        logger.info(f"Previsão ensemble gerada: {len(df_ensemble)} pontos")
        return df_ensemble
    
    def calcular_intervalo_confianca(
        self,
        df_previsao: pd.DataFrame,
        nivel_confianca: float = 0.95
    ) -> pd.DataFrame:
        """Calcula intervalo de confiança para a previsão.
        
        Args:
            df_previsao: DataFrame com previsões.
            nivel_confianca: Nível de confiança (0-1).
            
        Returns:
            DataFrame com intervalos de confiança.
        """
        logger.info(f"Calculando intervalo de confiança: {nivel_confianca*100}%")
        
        # Calcular desvio padrão histórico
        desvio_padrao = self.df['Consumo registado (kW)'].std()
        
        # Calcular valor z para o nível de confiança
        from scipy import stats
        z_score = stats.norm.ppf((1 + nivel_confianca) / 2)
        
        # Calcular margem de erro
        margem_erro = z_score * desvio_padrao
        
        # Adicionar intervalos de confiança
        df_resultado = df_previsao.copy()
        df_resultado['Limite_Inferior (kW)'] = (
            df_resultado['Consumo_Previsto (kW)'] - margem_erro
        ).clip(lower=0)
        df_resultado['Limite_Superior (kW)'] = (
            df_resultado['Consumo_Previsto (kW)'] + margem_erro
        )
        
        logger.info(f"Intervalos de confiança calculados")
        return df_resultado
    
    def comparar_previsoes(
        self,
        dias_teste: int = 7
    ) -> Dict:
        """Compara diferentes métodos de previsão com dados reais.
        
        Args:
            dias_teste: Número de dias para teste.
            
        Returns:
            Dicionário com métricas de comparação.
        """
        logger.info(f"Comparando métodos de previsão: {dias_teste} dias de teste")
        
        # Separar dados de treino e teste
        df_ordenado = self.df.sort_values('DataHora')
        data_corte = df_ordenado['DataHora'].iloc[-1] - timedelta(days=dias_teste)
        
        df_treino = df_ordenado[df_ordenado['DataHora'] < data_corte]
        df_teste = df_ordenado[df_ordenado['DataHora'] >= data_corte]
        
        # Criar previsor com dados de treino
        previsor_treino = PrevisorConsumo(df_treino)
        
        # Gerar previsões
        df_previsao = previsor_treino.prever_ensemble(dias_futuros=dias_teste)
        
        # Alinhar previsões com dados reais
        df_comparacao = df_teste[['DataHora', 'Consumo registado (kW)']].copy()
        df_comparacao = df_comparacao.merge(
            df_previsao[['DataHora', 'Consumo_Previsto (kW)']],
            on='DataHora',
            how='inner'
        )
        
        # Calcular métricas
        erros = df_comparacao['Consumo registado (kW)'] - df_comparacao['Consumo_Previsto (kW)']
        
        mae = np.mean(np.abs(erros))  # Mean Absolute Error
        mae_percentual = mae / df_teste['Consumo registado (kW)'].mean() * 100
        rmse = np.sqrt(np.mean(erros**2))  # Root Mean Square Error
        
        resultado = {
            'mae': mae,
            'mae_percentual': mae_percentual,
            'rmse': rmse,
            'pontos_testados': len(df_comparacao),
            'media_real': df_teste['Consumo registado (kW)'].mean(),
            'media_prevista': df_previsao['Consumo_Previsto (kW)'].mean()
        }
        
        logger.info(f"Comparação concluída: MAE={mae:.4f} kW ({mae_percentual:.2f}%)")
        return resultado
    
    def gerar_resumo_previsao(
        self,
        dias_futuros: int = 7
    ) -> Dict:
        """Gera um resumo da previsão de consumo.
        
        Args:
            dias_futuros: Número de dias para prever.
            
        Returns:
            Dicionário com resumo da previsão.
        """
        logger.info(f"Gerando resumo de previsão: {dias_futuros} dias")
        
        # Gerar previsão ensemble
        df_previsao = self.prever_ensemble(dias_futuros)
        
        # Calcular intervalo de confiança
        df_previsao = self.calcular_intervalo_confianca(df_previsao)
        
        # Agrupar por dia
        df_previsao['Data'] = df_previsao['DataHora'].dt.date
        resumo_diario = df_previsao.groupby('Data').agg({
            'Consumo_Previsto (kW)': 'sum',
            'Limite_Inferior (kW)': 'sum',
            'Limite_Superior (kW)': 'sum'
        }).round(2)
        
        # Calcular totais
        total_previsto = df_previsao['Consumo_Previsto (kW)'].sum()
        total_inferior = df_previsao['Limite_Inferior (kW)'].sum()
        total_superior = df_previsao['Limite_Superior (kW)'].sum()
        
        # Comparar com histórico
        media_historica = self.df['Consumo registado (kW)'].mean()
        media_prevista = df_previsao['Consumo_Previsto (kW)'].mean()
        variacao_percentual = (media_prevista - media_historica) / media_historica * 100
        
        resultado = {
            'periodo_previsao': {
                'inicio': df_previsao['DataHora'].min(),
                'fim': df_previsao['DataHora'].max(),
                'dias': dias_futuros
            },
            'totais': {
                'previsto_kw': total_previsto,
                'limite_inferior_kw': total_inferior,
                'limite_superior_kw': total_superior
            },
            'medias': {
                'historica_kw': media_historica,
                'prevista_kw': media_prevista,
                'variacao_percentual': variacao_percentual
            },
            'resumo_diario': resumo_diario.to_dict('index')
        }
        
        logger.info("Resumo de previsão gerado")
        return resultado
