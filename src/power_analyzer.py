#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para análise de potência contratada e recomendações.

Este módulo permite analisar o consumo de potência e recomendar
a potência contratada mais adequada com base nos dados de consumo.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

from .utils import setup_logging, carregar_config
from .exceptions import ConfigurationError, PowerAnalysisError

logger = setup_logging()

# Carregar configuração
try:
    config_potencias = carregar_config('config/potencias.yaml')
    config_principal = carregar_config('config/config.yaml')
    POTENCIA_ATUAL_PADRAO = config_principal.get('potencia', {}).get('atual', 10.35)
    
    # Carregar custos de potência
    CUSTOS_POTENCIA = {}
    for potencia, dados in config_potencias.get('potencias', {}).items():
        CUSTOS_POTENCIA[potencia] = dados.get('custo_mensal', 0)
    
    # Carregar preços de consumo por tipo de tarifa
    TARIFAS_CONSUMO = config_potencias.get('tarifas_consumo', {})
    PRECO_SIMPLES = TARIFAS_CONSUMO.get('simples', {}).get('preco_kwh', 0.1424)
    PRECO_BI_VAZIO = TARIFAS_CONSUMO.get('bi_horaria', {}).get('preco_vazio', 0.0987)
    PRECO_BI_CHEIO = TARIFAS_CONSUMO.get('bi_horaria', {}).get('preco_cheio', 0.1633)
    PRECO_TRI_VAZIO = TARIFAS_CONSUMO.get('tri_horaria', {}).get('preco_vazio', 0.0987)
    PRECO_TRI_PONTA = TARIFAS_CONSUMO.get('tri_horaria', {}).get('preco_ponta', 0.1633)
    PRECO_TRI_CHEIO = TARIFAS_CONSUMO.get('tri_horaria', {}).get('preco_cheio', 0.1633)
    
    # Carregar nomes das potências
    NOMES_POTENCIAS = {}
    for potencia, dados in config_potencias.get('potencias', {}).items():
        NOMES_POTENCIAS[potencia] = dados.get('nome', '')
    
except (ConfigurationError, Exception) as e:
    logger.warning(f"Erro ao carregar configuração de potência: {e}. Usando valores padrão.")
    POTENCIA_ATUAL_PADRAO = 10.35
    CUSTOS_POTENCIA = {
        1.15: 2.64,
        2.30: 5.28,
        3.45: 7.92,
        6.90: 15.84,
        10.35: 23.76,
        13.80: 31.68,
        17.25: 39.60,
        20.70: 47.52
    }
    PRECO_SIMPLES = 0.1424
    PRECO_BI_VAZIO = 0.0987
    PRECO_BI_CHEIO = 0.1633
    PRECO_TRI_VAZIO = 0.0987
    PRECO_TRI_PONTA = 0.1633
    PRECO_TRI_CHEIO = 0.1633
    NOMES_POTENCIAS = {
        1.15: "Garagem ou espaços similares de pequenas dimensões",
        2.30: "Apartamento T0 (1 pessoa)",
        3.45: "Apartamento para 1 a 2 pessoas",
        6.90: "Apartamento para 3 a 5 pessoas",
        10.35: "Moradia com mais de 5 pessoas",
        13.80: "Moradia com piscina",
        17.25: "Pequenas empresas",
        20.70: "Médias empresas"
    }


class TipoPotencia(Enum):
    """Enumeração dos tipos de potência contratada disponíveis."""
    
    KVA_1_15 = 1.15
    KVA_2_30 = 2.30
    KVA_3_45 = 3.45
    KVA_6_90 = 6.90
    KVA_10_35 = 10.35
    KVA_13_80 = 13.80
    KVA_17_25 = 17.25
    KVA_20_70 = 20.70


class AnalisadorPotencia:
    """Classe para análise de potência contratada."""
    
    # Definições das potências disponíveis
    POTENCIAS = {
        1.15: "Garagem ou espaços similares de pequenas dimensões",
        2.30: "Apartamento T0 (1 pessoa)",
        3.45: "Apartamento para 1 a 2 pessoas",
        6.90: "Apartamento para 3 a 5 pessoas",
        10.35: "Moradia com mais de 5 pessoas",
        13.80: "Moradia com piscina",
        17.25: "Pequenas empresas",
        20.70: "Médias empresas"
    }
    
    # Margens de segurança recomendadas
    MARGEM_SEGURANCA_CONSERVADORA = 0.50  # 50% acima do pico
    MARGEM_SEGURANCA_MODERADA = 0.30      # 30% acima do pico
    MARGEM_SEGURANCA_OTIMISTA = 0.15      # 15% acima do pico
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o analisador de potência.
        
        Args:
            df: DataFrame com os dados de consumo
        """
        self.df = df.copy()
        self._validar_colunas()
        
    def _validar_colunas(self) -> None:
        """Valida se as colunas necessárias existem.
        
        Raises:
            PowerAnalysisError: Se colunas necessárias não existirem.
        """
        colunas_necessarias = ['Consumo registado (kW)']
        for col in colunas_necessarias:
            if col not in self.df.columns:
                raise PowerAnalysisError(f"Coluna '{col}' não encontrada no DataFrame")
    
    def calcular_estatisticas_potencia(self) -> Dict:
        """
        Calcula estatísticas de potência baseadas no consumo.
        
        Returns:
            Dicionário com estatísticas de potência
        """
        consumo = self.df['Consumo registado (kW)']
        
        estatisticas = {
            'pico_maximo': consumo.max(),
            'pico_medio': consumo.mean(),
            'pico_percentil_95': consumo.quantile(0.95),
            'pico_percentil_99': consumo.quantile(0.99),
            'desvio_padrao': consumo.std(),
            'total_registros': len(consumo)
        }
        
        logger.info(f"Estatísticas de potência calculadas: {estatisticas}")
        return estatisticas
    
    def recomendar_potencia(self, 
                           margem_seguranca: float = MARGEM_SEGURANCA_MODERADA,
                           usar_percentil: float = 0.99) -> Tuple[float, str, Dict]:
        """
        Recomenda a potência contratada mais adequada.
        
        Args:
            margem_seguranca: Margem de segurança (0.0 a 1.0)
            usar_percentil: Percentil a usar como base (0.0 a 1.0)
        
        Returns:
            Tupla com (potencia_recomendada, descricao, detalhes)
        """
        estatisticas = self.calcular_estatisticas_potencia()
        
        # Usar o percentil especificado como base
        pico_base = estatisticas[f'pico_percentil_{int(usar_percentil*100)}']
        
        # Adicionar margem de segurança
        potencia_necessaria = pico_base * (1 + margem_seguranca)
        
        # Encontrar a potência contratada mais próxima (arredondar para cima)
        potencias_disponiveis = sorted(self.POTENCIAS.keys())
        potencia_recomendada = None
        
        for potencia in potencias_disponiveis:
            if potencia >= potencia_necessaria:
                potencia_recomendada = potencia
                break
        
        # Se não encontrou potência suficiente, usar a maior disponível
        if potencia_recomendada is None:
            potencia_recomendada = potencias_disponiveis[-1]
        
        descricao = self.POTENCIAS[potencia_recomendada]
        
        detalhes = {
            'pico_base': pico_base,
            'margem_seguranca': margem_seguranca,
            'potencia_necessaria': potencia_necessaria,
            'potencia_recomendada': potencia_recomendada,
            'estatisticas': estatisticas
        }
        
        logger.info(f"Potência recomendada: {potencia_recomendada} kVA ({descricao})")
        return potencia_recomendada, descricao, detalhes
    
    def comparar_potencias(self, potencia_atual: Optional[float] = None) -> pd.DataFrame:
        """
        Compara todas as potências disponíveis.
        
        Args:
            potencia_atual: Potência contratada atual (opcional)
        
        Returns:
            DataFrame com comparação de potências
        """
        estatisticas = self.calcular_estatisticas_potencia()
        potencias_disponiveis = sorted(self.POTENCIAS.keys())
        
        dados = []
        for potencia in potencias_disponiveis:
            margem_pico = ((potencia - estatisticas['pico_maximo']) / 
                          estatisticas['pico_maximo'] * 100) if estatisticas['pico_maximo'] > 0 else float('inf')
            margem_media = ((potencia - estatisticas['pico_medio']) / 
                           estatisticas['pico_medio'] * 100) if estatisticas['pico_medio'] > 0 else float('inf')
            
            adequada = (
                potencia >= estatisticas['pico_maximo'] * 1.15 and
                potencia >= estatisticas['pico_percentil_99'] * 1.10
            )
            
            dados.append({
                'Potência (kVA)': potencia,
                'Descrição': self.POTENCIAS[potencia],
                'Margem sobre Pico (%)': round(margem_pico, 2),
                'Margem sobre Média (%)': round(margem_media, 2),
                'Adequada': '✅ Sim' if adequada else '❌ Não',
                'Custo Anual Estimado (€)': self._estimar_custo_anual(potencia)
            })
        
        df = pd.DataFrame(dados)
        
        # Marcar potência atual se fornecida
        if potencia_atual is not None:
            df['Atual'] = df['Potência (kVA)'].apply(
                lambda x: '👈 Atual' if x == potencia_atual else ''
            )
        
        return df
    
    def analisar_eficiencia_potencia(self, potencia_atual: float) -> Dict:
        """
        Analisa a eficiência da potência contratada atual.
        
        Args:
            potencia_atual: Potência contratada atual em kVA
        
        Returns:
            Dicionário com análise de eficiência
        """
        estatisticas = self.calcular_estatisticas_potencia()
        
        # Calcular utilização média
        utilizacao_media = (estatisticas['pico_medio'] / potencia_atual * 100)
        
        # Calcular utilização do pico
        utilizacao_pico = (estatisticas['pico_maximo'] / potencia_atual * 100)
        
        # Calcular utilização do percentil 99
        utilizacao_p99 = (estatisticas['pico_percentil_99'] / potencia_atual * 100)
        
        # Determinar classificação
        if utilizacao_p99 < 50:
            classificacao = "⚠️ Sobredimensionada"
            recomendacao = "Considere reduzir a potência contratada"
        elif utilizacao_p99 < 70:
            classificacao = "✅ Adequada (conservadora)"
            recomendacao = "Potência adequada, mas pode ser otimizada"
        elif utilizacao_p99 < 85:
            classificacao = "✅ Adequada (ótima)"
            recomendacao = "Potência bem dimensionada"
        elif utilizacao_p99 < 95:
            classificacao = "⚠️ Próxima do limite"
            recomendacao = "Monitore o consumo, pode precisar aumentar"
        else:
            classificacao = "🔴 Subdimensionada"
            recomendacao = "Recomendado aumentar a potência contratada"
        
        # Calcular economia potencial usando a potência atual fornecida
        potencia_recomendada, _, detalhes = self.recomendar_potencia()
        economia_potencial = self._calcular_economia_potencial(potencia_atual, potencia_recomendada)
        
        analise = {
            'potencia_atual': potencia_atual,
            'utilizacao_media': utilizacao_media,
            'utilizacao_pico': utilizacao_pico,
            'utilizacao_p99': utilizacao_p99,
            'classificacao': classificacao,
            'recomendacao': recomendacao,
            'potencia_recomendada': potencia_recomendada,
            'economia_potencial_anual': economia_potencial,
            'estatisticas': estatisticas
        }
        
        logger.info(f"Análise de eficiência: {classificacao}")
        return analise
    
    def _calcular_economia_potencial(self, potencia_atual: float, potencia_recomendada: float) -> float:
        """
        Calcula a economia potencial anual.
        
        Args:
            potencia_atual: Potência atual em kVA
            potencia_recomendada: Potência recomendada em kVA
        
        Returns:
            Economia potencial anual em €
        """
        # Calcular economia usando os custos do config.yaml
        custo_atual = CUSTOS_POTENCIA.get(potencia_atual, 0) * 12
        custo_recomendado = CUSTOS_POTENCIA.get(potencia_recomendada, 0) * 12
        
        economia = max(0, custo_atual - custo_recomendado)
        
        return economia
    
    def _estimar_custo_anual(self, potencia: float) -> float:
        """
        Estima o custo anual de uma potência contratada.
        
        Args:
            potencia: Potência em kVA
        
        Returns:
            Custo anual estimado em €
        """
        custo_mensal = CUSTOS_POTENCIA.get(potencia, 0)
        return custo_mensal * 12
    
    def calcular_custo_consumo_anual(self, tipo_tarifa: str = 'simples') -> float:
        """
        Calcula o custo anual de consumo baseado no tipo de tarifa.
        
        Args:
            tipo_tarifa: Tipo de tarifa ('simples', 'bi_horaria', 'tri_horaria')
        
        Returns:
            Custo anual de consumo em €
        """
        # Total de consumo em kWh (cada registro é de 15 minutos = 0.25 horas)
        consumo_total_kwh = self.df['Consumo registado (kW)'].sum() * 0.25
        
        if tipo_tarifa == 'simples':
            custo_anual = consumo_total_kwh * PRECO_SIMPLES
        elif tipo_tarifa == 'bi_horaria':
            # Separar consumo em vazio e cheio
            # Horários de vazio: [[0, 7], [22, 24]]
            # Horários de cheio: [[7, 22], [24, 0]]
            
            # Criar coluna de hora
            df_temp = self.df.copy()
            df_temp['Hora'] = df_temp['DataHora'].dt.hour
            
            # Classificar como vazio ou cheio
            def classificar_hora(h):
                # Verificar se está em horário de vazio
                for vazio in [[0, 7], [22, 24]]:
                    if vazio[0] <= h < vazio[1]:
                        return 'vazio'
                return 'cheio'
            
            df_temp['Periodo'] = df_temp['Hora'].apply(classificar_hora)
            
            # Separar consumo
            consumo_vazio = df_temp[df_temp['Periodo'] == 'vazio']['Consumo registado (kW)'].sum() * 0.25
            consumo_cheio = df_temp[df_temp['Periodo'] == 'cheio']['Consumo registado (kW)'].sum() * 0.25
            
            custo_anual = (consumo_vazio * PRECO_BI_VAZIO) + (consumo_cheio * PRECO_BI_CHEIO)
        elif tipo_tarifa == 'tri_horaria':
            # Separar consumo em vazio, ponta e cheio
            # Horários de vazio: [[0, 7], [22, 24]]
            # Horários de ponta: [[18, 21]]
            # Horários de cheio: [[7, 18], [21, 22], [24, 0]]
            
            # Criar coluna de hora
            df_temp = self.df.copy()
            df_temp['Hora'] = df_temp['DataHora'].dt.hour
            
            # Classificar como vazio, ponta ou cheio
            def classificar_hora_tri(h):
                # Verificar se está em horário de vazio
                for vazio in [[0, 7], [22, 24]]:
                    if vazio[0] <= h < vazio[1]:
                        return 'vazio'
                # Verificar se está em horário de ponta
                for ponta in [[18, 21]]:
                    if ponta[0] <= h < ponta[1]:
                        return 'ponta'
                return 'cheio'
            
            df_temp['Periodo'] = df_temp['Hora'].apply(classificar_hora_tri)
            
            # Separar consumo
            consumo_vazio = df_temp[df_temp['Periodo'] == 'vazio']['Consumo registado (kW)'].sum() * 0.25
            consumo_ponta = df_temp[df_temp['Periodo'] == 'ponta']['Consumo registado (kW)'].sum() * 0.25
            consumo_cheio = df_temp[df_temp['Periodo'] == 'cheio']['Consumo registado (kW)'].sum() * 0.25
            
            custo_anual = (consumo_vazio * PRECO_TRI_VAZIO) + (consumo_ponta * PRECO_TRI_PONTA) + (consumo_cheio * PRECO_TRI_CHEIO)
        else:
            custo_anual = consumo_total_kwh * PRECO_SIMPLES
        
        return custo_anual
    
    def obter_custo_potencia(self, potencia: float) -> float:
        """
        Obtém o custo mensal de uma potência contratada.
        
        Args:
            potencia: Potência em kVA
        
        Returns:
            Custo mensal em €
        """
        return CUSTOS_POTENCIA.get(potencia, 0)
    
    def gerar_relatorio_potencia(self, potencia_atual: Optional[float] = None) -> str:
        """
        Gera um relatório detalhado da análise de potência.
        
        Args:
            potencia_atual: Potência contratada atual (opcional)
        
        Returns:
            String com o relatório formatado
        """
        estatisticas = self.calcular_estatisticas_potencia()
        potencia_recomendada, descricao, detalhes = self.recomendar_potencia()
        
        relatorio = "="*70 + "\n"
        relatorio += "RELATÓRIO DE ANÁLISE DE POTÊNCIA CONTRATADA\n"
        relatorio += "="*70 + "\n\n"
        
        relatorio += "📊 ESTATÍSTICAS DE CONSUMO:\n"
        relatorio += "-"*70 + "\n"
        relatorio += f"Pico Máximo: {estatisticas['pico_maximo']:.4f} kW\n"
        relatorio += f"Pico Médio: {estatisticas['pico_medio']:.4f} kW\n"
        relatorio += f"Pico Percentil 95: {estatisticas['pico_percentil_95']:.4f} kW\n"
        relatorio += f"Pico Percentil 99: {estatisticas['pico_percentil_99']:.4f} kW\n"
        relatorio += f"Desvio Padrão: {estatisticas['desvio_padrao']:.4f} kW\n\n"
        
        if potencia_atual:
            analise = self.analisar_eficiencia_potencia(potencia_atual)
            relatorio += "⚡ ANÁLISE DA POTÊNCIA ATUAL:\n"
            relatorio += "-"*70 + "\n"
            relatorio += f"Potência Atual: {potencia_atual} kVA\n"
            relatorio += f"Utilização Média: {analise['utilizacao_media']:.2f}%\n"
            relatorio += f"Utilização do Pico: {analise['utilizacao_pico']:.2f}%\n"
            relatorio += f"Utilização P99: {analise['utilizacao_p99']:.2f}%\n"
            relatorio += f"Classificação: {analise['classificacao']}\n"
            relatorio += f"Recomendação: {analise['recomendacao']}\n\n"
        
        relatorio += "💡 RECOMENDAÇÃO:\n"
        relatorio += "-"*70 + "\n"
        relatorio += f"Potência Recomendada: {potencia_recomendada} kVA\n"
        relatorio += f"Descrição: {descricao}\n"
        relatorio += f"Margem de Segurança: {detalhes['margem_seguranca']*100:.0f}%\n\n"
        
        if potencia_atual and potencia_atual != potencia_recomendada:
            # Calcular economia potencial
            economia_potencial = self._calcular_economia_potencial(potencia_atual, potencia_recomendada)
            relatorio += f"💰 ECONOMIA POTENCIAL ANUAL: €{economia_potencial:.2f}\n\n"
        
        relatorio += "="*70 + "\n"
        
        return relatorio
