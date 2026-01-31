#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para análise sazonal de consumo de eletricidade.

Este módulo fornece funcionalidades para analisar padrões sazonais,
comparar períodos equivalentes entre anos, e identificar tendências
sazonais no consumo de eletricidade.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from scipy import stats

logger = logging.getLogger(__name__)


class AnalisadorSazonal:
    """Classe para análise sazonal de consumo de eletricidade."""

    def __init__(self, df: pd.DataFrame):
        """Inicializa o analisador sazonal.
        
        Args:
            df: DataFrame com dados de consumo de eletricidade.
                  Deve conter colunas: 'Data', 'Consumo registado (kW)', etc.
        """
        self.df = df.copy()
        self._validar_colunas()
        logger.info(f"AnalisadorSazonal inicializado com {len(df)} registros")

    def _validar_colunas(self):
        """Valida se as colunas necessárias existem."""
        colunas_necessarias = ['Data', 'Consumo registado (kW)']
        for coluna in colunas_necessarias:
            if coluna not in self.df.columns:
                raise ValueError(f"Coluna necessária não encontrada: {coluna}")

    def comparar_meses_entre_anos(self, mes: int) -> pd.DataFrame:
        """Compara o mesmo mês entre diferentes anos.
        
        Args:
            mes: Número do mês (1-12).
            
        Returns:
            DataFrame com comparação do mês entre anos.
        """
        logger.info(f"Comparando mês {mes} entre anos")
        
        # Filtrar dados do mês especificado
        df_mes = self.df[self.df['Mes'] == mes].copy()
        
        if len(df_mes) == 0:
            logger.warning(f"Nenhum dado encontrado para o mês {mes}")
            return pd.DataFrame()
        
        # Agrupar por ano
        comparacao = df_mes.groupby('Ano')['Consumo registado (kW)'].agg([
            ('Total (kW)', 'sum'),
            ('Média (kW)', 'mean'),
            ('Máximo (kW)', 'max'),
            ('Mínimo (kW)', 'min'),
            ('Registros', 'count')
        ]).round(4)
        
        logger.info(f"Comparação concluída: {len(comparacao)} anos analisados")
        return comparacao

    def comparar_estacoes(self) -> pd.DataFrame:
        """Compara consumo entre as quatro estações do ano.
        
        Returns:
            DataFrame com comparação por estação.
        """
        logger.info("Comparando consumo por estação")
        
        # Definir estações
        def obter_estacao(mes):
            if mes in [12, 1, 2]:
                return 'Inverno'
            elif mes in [3, 4, 5]:
                return 'Primavera'
            elif mes in [6, 7, 8]:
                return 'Verão'
            else:
                return 'Outono'
        
        self.df['Estacao'] = self.df['Mes'].apply(obter_estacao)
        
        # Agrupar por estação
        comparacao = self.df.groupby('Estacao')['Consumo registado (kW)'].agg([
            ('Total (kW)', 'sum'),
            ('Média (kW)', 'mean'),
            ('Máximo (kW)', 'max'),
            ('Mínimo (kW)', 'min'),
            ('Registros', 'count')
        ]).round(4)
        
        # Ordenar por estação (Inverno, Primavera, Verão, Outono)
        ordem_estacoes = ['Inverno', 'Primavera', 'Verão', 'Outono']
        comparacao = comparacao.reindex(ordem_estacoes)
        
        logger.info("Comparação por estação concluída")
        return comparacao

    def analisar_padrao_semanal(self) -> pd.DataFrame:
        """Analisa padrões de consumo por dia da semana.
        
        Returns:
            DataFrame com análise por dia da semana.
        """
        logger.info("Analisando padrão semanal")
        
        # Agrupar por dia da semana
        padrao = self.df.groupby(['DiaSemana', 'NomeDiaSemana'])['Consumo registado (kW)'].agg([
            ('Total (kW)', 'sum'),
            ('Média (kW)', 'mean'),
            ('Máximo (kW)', 'max'),
            ('Mínimo (kW)', 'min'),
            ('Registros', 'count')
        ]).round(4)
        
        logger.info("Análise de padrão semanal concluída")
        return padrao

    def analisar_padrao_horario(self, dia_semana: Optional[int] = None) -> pd.DataFrame:
        """Analisa padrões de consumo por hora do dia.
        
        Args:
            dia_semana: Opcional. Se fornecido, analisa apenas esse dia da semana (0=Segunda, 6=Domingo).
            
        Returns:
            DataFrame com análise por hora.
        """
        logger.info(f"Analisando padrão horario{' para dia da semana ' + str(dia_semana) if dia_semana is not None else ''}")
        
        # Filtrar por dia da semana se especificado
        df_filtrado = self.df[self.df['DiaSemana'] == dia_semana] if dia_semana is not None else self.df
        
        # Agrupar por hora
        padrao = df_filtrado.groupby('HoraNum')['Consumo registado (kW)'].agg([
            ('Total (kW)', 'sum'),
            ('Média (kW)', 'mean'),
            ('Máximo (kW)', 'max'),
            ('Mínimo (kW)', 'min'),
            ('Registros', 'count')
        ]).round(4)
        
        logger.info("Análise de padrão horário concluída")
        return padrao

    def comparar_uteis_vs_fds(self) -> Dict:
        """Compara consumo entre dias úteis e fim de semana.
        
        Returns:
            Dicionário com estatísticas comparativas.
        """
        logger.info("Comparando dias úteis vs fim de semana")
        
        # Classificar dias
        df_uteis = self.df[self.df['DiaSemana'] < 5]
        df_fds = self.df[self.df['DiaSemana'] >= 5]
        
        resultado = {
            'uteis': {
                'total_kw': df_uteis['Consumo registado (kW)'].sum(),
                'media_kw': df_uteis['Consumo registado (kW)'].mean(),
                'maximo_kw': df_uteis['Consumo registado (kW)'].max(),
                'registros': len(df_uteis)
            },
            'fds': {
                'total_kw': df_fds['Consumo registado (kW)'].sum(),
                'media_kw': df_fds['Consumo registado (kW)'].mean(),
                'maximo_kw': df_fds['Consumo registado (kW)'].max(),
                'registros': len(df_fds)
            },
            'diferenca_percentual': (
                (df_uteis['Consumo registado (kW)'].mean() - df_fds['Consumo registado (kW)'].mean()) /
                df_fds['Consumo registado (kW)'].mean() * 100
            ) if df_fds['Consumo registado (kW)'].mean() > 0 else 0
        }
        
        logger.info(f"Comparação concluída: {resultado['diferenca_percentual']:.2f}% de diferença")
        return resultado

    def analisar_variacao_mensal(self, ano: Optional[int] = None) -> pd.DataFrame:
        """Analisa variação de consumo ao longo dos meses.
        
        Args:
            ano: Opcional. Se fornecido, analisa apenas esse ano.
            
        Returns:
            DataFrame com variação mensal.
        """
        logger.info(f"Analisando variação mensal{' para ano ' + str(ano) if ano is not None else ''}")
        
        # Filtrar por ano se especificado
        df_filtrado = self.df[self.df['Ano'] == ano] if ano is not None else self.df
        
        # Agrupar por mês
        variacao = df_filtrado.groupby(['Ano', 'Mes', 'NomeMes'])['Consumo registado (kW)'].agg([
            ('Total (kW)', 'sum'),
            ('Média (kW)', 'mean'),
            ('Máximo (kW)', 'max'),
            ('Mínimo (kW)', 'min'),
            ('Registros', 'count')
        ]).round(4)
        
        # Calcular variação percentual mês a mês
        variacao['Variacao (%)'] = variacao['Total (kW)'].pct_change() * 100
        
        logger.info("Análise de variação mensal concluída")
        return variacao

    def identificar_padroes_feriados(self, feriados: List[datetime]) -> pd.DataFrame:
        """Analisa consumo em feriados vs dias normais.
        
        Args:
            feriados: Lista de datas de feriados.
            
        Returns:
            DataFrame com comparação feriados vs dias normais.
        """
        logger.info(f"Analisando {len(feriados)} feriados")
        
        # Marcar feriados
        self.df['Feriado'] = self.df['Data'].dt.date.isin([f.date() for f in feriados])
        
        # Separar dados
        df_feriados = self.df[self.df['Feriado']]
        df_normais = self.df[~self.df['Feriado']]
        
        # Criar comparação
        comparacao = pd.DataFrame({
            'Feriados': {
                'Total (kW)': df_feriados['Consumo registado (kW)'].sum(),
                'Média (kW)': df_feriados['Consumo registado (kW)'].mean(),
                'Registros': len(df_feriados)
            },
            'Normais': {
                'Total (kW)': df_normais['Consumo registado (kW)'].sum(),
                'Média (kW)': df_normais['Consumo registado (kW)'].mean(),
                'Registros': len(df_normais)
            }
        }).T
        
        logger.info("Análise de feriados concluída")
        return comparacao

    def calcular_indice_sazonal(self) -> pd.DataFrame:
        """Calcula índices sazonais para cada mês.
        
        O índice sazonal mostra como cada mês se compara à média anual.
        Valores > 100 indicam consumo acima da média.
        
        Returns:
            DataFrame com índices sazonais.
        """
        logger.info("Calculando índices sazonais")
        
        # Calcular média mensal
        media_mensal = self.df.groupby('Mes')['Consumo registado (kW)'].mean()
        
        # Calcular média global
        media_global = self.df['Consumo registado (kW)'].mean()
        
        # Calcular índice sazonal
        indice_sazonal = (media_mensal / media_global * 100).round(2)
        
        # Criar DataFrame apenas com meses que têm dados
        meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        # Criar dicionário apenas para meses com dados
        dados = {
            'Mês': [],
            'Índice Sazonal': [],
            'Consumo Médio (kW)': []
        }
        
        for mes in range(1, 13):
            if mes in media_mensal.index:
                dados['Mês'].append(meses_nomes[mes - 1])
                dados['Índice Sazonal'].append(indice_sazonal[mes])
                dados['Consumo Médio (kW)'].append(media_mensal[mes])
        
        df_indice = pd.DataFrame(dados)
        
        logger.info("Índices sazonais calculados")
        return df_indice

    def detectar_mudancas_sazonais(self, janela: int = 30) -> pd.DataFrame:
        """Detecta mudanças significativas no padrão sazonal.
        
        Usa teste estatístico para detectar mudanças na média móvel.
        
        Args:
            janela: Tamanho da janela para média móvel.
            
        Returns:
            DataFrame com datas de mudanças detectadas.
        """
        logger.info(f"Detectando mudanças sazonais com janela de {janela} dias")
        
        # Calcular média móvel
        df_ordenado = self.df.sort_values('Data').copy()
        df_ordenado['MediaMovel'] = df_ordenado['Consumo registado (kW)'].rolling(
            window=janela, min_periods=1
        ).mean()
        
        # Calcular diferenças
        df_ordenado['Diferenca'] = df_ordenado['MediaMovel'].diff()
        
        # Detectar mudanças significativas (mais de 2 desvios padrão)
        desvio_padrao = df_ordenado['Diferenca'].std()
        mudancas = df_ordenado[abs(df_ordenado['Diferenca']) > 2 * desvio_padrao].copy()
        
        if len(mudancas) > 0:
            logger.info(f"Detectadas {len(mudancas)} mudanças sazonais")
        else:
            logger.info("Nenhuma mudança sazonal significativa detectada")
        
        return mudancas[['Data', 'MediaMovel', 'Diferenca']]

    def gerar_resumo_sazonal(self) -> Dict:
        """Gera um resumo completo da análise sazonal.
        
        Returns:
            Dicionário com resumo da análise sazonal.
        """
        logger.info("Gerando resumo sazonal")
        
        resumo = {
            'periodo': {
                'inicio': self.df['Data'].min(),
                'fim': self.df['Data'].max(),
                'anos': self.df['Ano'].nunique(),
                'meses': self.df['Mes'].nunique()
            },
            'estacoes': self.comparar_estacoes().to_dict('index'),
            'uteis_vs_fds': self.comparar_uteis_vs_fds(),
            'indice_sazonal': self.calcular_indice_sazonal().to_dict('records'),
            'estatisticas': {
                'total_kw': self.df['Consumo registado (kW)'].sum(),
                'media_kw': self.df['Consumo registado (kW)'].mean(),
                'maximo_kw': self.df['Consumo registado (kW)'].max(),
                'minimo_kw': self.df['Consumo registado (kW)'].min()
            }
        }
        
        logger.info("Resumo sazonal gerado")
        return resumo
