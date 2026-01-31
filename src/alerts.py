#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para configuração e envio de alertas de consumo.

Este módulo fornece funcionalidades para configurar alertas
baseados em condições específicas de consumo e notificar
quando essas condições são atingidas.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class TipoAlerta(Enum):
    """Tipos de alertas disponíveis."""
    CONSUMO_DIARIO_ALTO = "Consumo Diário Alto"
    CONSUMO_HOURLY_ALTO = "Consumo Horário Alto"
    AUMENTO_MENSAL = "Aumento Mensal"
    AUMENTO_SEMANAL = "Aumento Semanal"
    ANOMALIA = "Anomalia Detectada"
    CUSTO_ALTO = "Custo Alto"
    PADRAO_INCOMUM = "Padrão Incomum"


class NivelAlerta(Enum):
    """Níveis de severidade dos alertas."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Alerta:
    """Classe representando um alerta."""
    
    def __init__(
        self,
        tipo: TipoAlerta,
        nivel: NivelAlerta,
        mensagem: str,
        data_hora: datetime,
        valor: float,
        referencia: Optional[float] = None
    ):
        """Inicializa um alerta.
        
        Args:
            tipo: Tipo do alerta.
            nivel: Nível de severidade.
            mensagem: Mensagem descritiva.
            data_hora: Data e hora do alerta.
            valor: Valor que disparou o alerta.
            referencia: Valor de referência (opcional).
        """
        self.tipo = tipo
        self.nivel = nivel
        self.mensagem = mensagem
        self.data_hora = data_hora
        self.valor = valor
        self.referencia = referencia
    
    def __str__(self):
        """Representação string do alerta."""
        ref_str = f" (ref: {self.referencia:.2f})" if self.referencia else ""
        return f"[{self.nivel.value}] {self.tipo.value}: {self.mensagem} - Valor: {self.valor:.2f}{ref_str}"
    
    def to_dict(self) -> Dict:
        """Converte o alerta para dicionário."""
        return {
            'tipo': self.tipo.value,
            'nivel': self.nivel.value,
            'mensagem': self.mensagem,
            'data_hora': self.data_hora.isoformat(),
            'valor': self.valor,
            'referencia': self.referencia
        }


class GestorAlertas:
    """Classe para gerenciar alertas de consumo."""
    
    def __init__(self, df: pd.DataFrame):
        """Inicializa o gestor de alertas.
        
        Args:
            df: DataFrame com dados de consumo.
        """
        self.df = df.copy()
        self.alertas: List[Alerta] = []
        self.regras: List[Dict] = []
        logger.info(f"GestorAlertas inicializado com {len(df)} registros")
    
    def adicionar_regra_consumo_diario(
        self,
        limite_kw: float,
        nivel: NivelAlerta = NivelAlerta.WARNING
    ):
        """Adiciona regra para consumo diário alto.
        
        Args:
            limite_kw: Limite de consumo diário em kW.
            nivel: Nível de severidade do alerta.
        """
        regra = {
            'tipo': TipoAlerta.CONSUMO_DIARIO_ALTO,
            'limite_kw': limite_kw,
            'nivel': nivel,
            'funcao': self._verificar_consumo_diario
        }
        self.regras.append(regra)
        logger.info(f"Regra adicionada: Consumo diário > {limite_kw} kW")
    
    def adicionar_regra_consumo_horario(
        self,
        limite_kw: float,
        nivel: NivelAlerta = NivelAlerta.CRITICAL
    ):
        """Adiciona regra para consumo horário alto.
        
        Args:
            limite_kw: Limite de consumo horário em kW.
            nivel: Nível de severidade do alerta.
        """
        regra = {
            'tipo': TipoAlerta.CONSUMO_HOURLY_ALTO,
            'limite_kw': limite_kw,
            'nivel': nivel,
            'funcao': self._verificar_consumo_horario
        }
        self.regras.append(regra)
        logger.info(f"Regra adicionada: Consumo horário > {limite_kw} kW")
    
    def adicionar_regra_aumento_mensal(
        self,
        percentual: float,
        nivel: NivelAlerta = NivelAlerta.WARNING
    ):
        """Adiciona regra para aumento mensal.
        
        Args:
            percentual: Percentual de aumento para alertar.
            nivel: Nível de severidade do alerta.
        """
        regra = {
            'tipo': TipoAlerta.AUMENTO_MENSAL,
            'percentual': percentual,
            'nivel': nivel,
            'funcao': self._verificar_aumento_mensal
        }
        self.regras.append(regra)
        logger.info(f"Regra adicionada: Aumento mensal > {percentual}%")
    
    def adicionar_regra_anomalia(
        self,
        z_score: float = 3.0,
        nivel: NivelAlerta = NivelAlerta.WARNING
    ):
        """Adiciona regra para detecção de anomalias.
        
        Args:
            z_score: Limite de Z-score para anomalias.
            nivel: Nível de severidade do alerta.
        """
        regra = {
            'tipo': TipoAlerta.ANOMALIA,
            'z_score': z_score,
            'nivel': nivel,
            'funcao': self._verificar_anomalias
        }
        self.regras.append(regra)
        logger.info(f"Regra adicionada: Anomalias (Z-score > {z_score})")
    
    def adicionar_regra_custo_alto(
        self,
        limite_eur: float,
        nivel: NivelAlerta = NivelAlerta.WARNING
    ):
        """Adiciona regra para custo alto.
        
        Args:
            limite_eur: Limite de custo em euros.
            nivel: Nível de severidade do alerta.
        """
        regra = {
            'tipo': TipoAlerta.CUSTO_ALTO,
            'limite_eur': limite_eur,
            'nivel': nivel,
            'funcao': self._verificar_custo_alto
        }
        self.regras.append(regra)
        logger.info(f"Regra adicionada: Custo > €{limite_eur}")
    
    def _verificar_consumo_diario(self, regra: Dict) -> List[Alerta]:
        """Verifica consumo diário alto."""
        alertas = []
        
        if 'Data' not in self.df.columns:
            return alertas
        
        # Agrupar por dia
        consumo_diario = self.df.groupby(self.df['Data'].dt.date)['Consumo registado (kW)'].sum()
        
        # Verificar limite
        for data, consumo in consumo_diario.items():
            if consumo > regra['limite_kw']:
                alerta = Alerta(
                    tipo=regra['tipo'],
                    nivel=regra['nivel'],
                    mensagem=f"Consumo diário de {consumo:.2f} kW excede limite de {regra['limite_kw']} kW",
                    data_hora=datetime.combine(data, datetime.min.time()),
                    valor=consumo,
                    referencia=regra['limite_kw']
                )
                alertas.append(alerta)
        
        return alertas
    
    def _verificar_consumo_horario(self, regra: Dict) -> List[Alerta]:
        """Verifica consumo horário alto."""
        alertas = []
        
        if 'DataHora' not in self.df.columns:
            return alertas
        
        # Verificar cada registro
        for _, row in self.df.iterrows():
            if row['Consumo registado (kW)'] > regra['limite_kw']:
                alerta = Alerta(
                    tipo=regra['tipo'],
                    nivel=regra['nivel'],
                    mensagem=f"Consumo horário de {row['Consumo registado (kW)']:.2f} kW excede limite de {regra['limite_kw']} kW",
                    data_hora=row['DataHora'],
                    valor=row['Consumo registado (kW)'],
                    referencia=regra['limite_kw']
                )
                alertas.append(alerta)
        
        return alertas
    
    def _verificar_aumento_mensal(self, regra: Dict) -> List[Alerta]:
        """Verifica aumento mensal."""
        alertas = []
        
        if 'Ano' not in self.df.columns or 'Mes' not in self.df.columns:
            return alertas
        
        # Agrupar por mês
        consumo_mensal = self.df.groupby(['Ano', 'Mes'])['Consumo registado (kW)'].sum()
        
        # Comparar com mês anterior
        for i in range(1, len(consumo_mensal)):
            consumo_atual = consumo_mensal.iloc[i]
            consumo_anterior = consumo_mensal.iloc[i-1]
            
            if consumo_anterior > 0:
                aumento = (consumo_atual - consumo_anterior) / consumo_anterior * 100
                
                if aumento > regra['percentual']:
                    mes_atual = consumo_mensal.index[i]
                    mes_anterior = consumo_mensal.index[i-1]
                    
                    alerta = Alerta(
                        tipo=regra['tipo'],
                        nivel=regra['nivel'],
                        mensagem=f"Aumento de {aumento:.1f}% de {mes_anterior} para {mes_atual}",
                        data_hora=datetime(mes_atual[0], mes_atual[1], 1),
                        valor=aumento,
                        referencia=regra['percentual']
                    )
                    alertas.append(alerta)
        
        return alertas
    
    def _verificar_anomalias(self, regra: Dict) -> List[Alerta]:
        """Verifica anomalias usando Z-score."""
        alertas = []
        
        if 'DataHora' not in self.df.columns:
            return alertas
        
        # Calcular Z-score
        media = self.df['Consumo registado (kW)'].mean()
        desvio = self.df['Consumo registado (kW)'].std()
        
        if desvio == 0:
            return alertas
        
        # Verificar outliers
        for _, row in self.df.iterrows():
            z_score = abs((row['Consumo registado (kW)'] - media) / desvio)
            
            if z_score > regra['z_score']:
                alerta = Alerta(
                    tipo=regra['tipo'],
                    nivel=regra['nivel'],
                    mensagem=f"Anomalia detectada: Z-score de {z_score:.2f}",
                    data_hora=row['DataHora'],
                    valor=row['Consumo registado (kW)'],
                    referencia=media
                )
                alertas.append(alerta)
        
        return alertas
    
    def _verificar_custo_alto(self, regra: Dict) -> List[Alerta]:
        """Verifica custo alto."""
        alertas = []
        
        if 'Custo_EUR' not in self.df.columns:
            return alertas
        
        # Agrupar por mês
        custo_mensal = self.df.groupby(['Ano', 'Mes'])['Custo_EUR'].sum()
        
        # Verificar limite
        for (ano, mes), custo in custo_mensal.items():
            if custo > regra['limite_eur']:
                alerta = Alerta(
                    tipo=regra['tipo'],
                    nivel=regra['nivel'],
                    mensagem=f"Custo mensal de €{custo:.2f} excede limite de €{regra['limite_eur']}",
                    data_hora=datetime(ano, mes, 1),
                    valor=custo,
                    referencia=regra['limite_eur']
                )
                alertas.append(alerta)
        
        return alertas
    
    def verificar_todas_regras(self) -> List[Alerta]:
        """Verifica todas as regras configuradas.
        
        Returns:
            Lista de alertas gerados.
        """
        logger.info(f"Verificando {len(self.regras)} regras de alerta")
        self.alertas = []
        
        for regra in self.regras:
            alertas_regra = regra['funcao'](regra)
            self.alertas.extend(alertas_regra)
        
        logger.info(f"Total de alertas gerados: {len(self.alertas)}")
        return self.alertas
    
    def filtrar_por_nivel(self, nivel: NivelAlerta) -> List[Alerta]:
        """Filtra alertas por nível de severidade.
        
        Args:
            nivel: Nível de severidade.
            
        Returns:
            Lista de alertas filtrados.
        """
        return [a for a in self.alertas if a.nivel == nivel]
    
    def filtrar_por_tipo(self, tipo: TipoAlerta) -> List[Alerta]:
        """Filtra alertas por tipo.
        
        Args:
            tipo: Tipo de alerta.
            
        Returns:
            Lista de alertas filtrados.
        """
        return [a for a in self.alertas if a.tipo == tipo]
    
    def filtrar_por_periodo(
        self,
        inicio: datetime,
        fim: datetime
    ) -> List[Alerta]:
        """Filtra alertas por período.
        
        Args:
            inicio: Data/hora inicial.
            fim: Data/hora final.
            
        Returns:
            Lista de alertas filtrados.
        """
        return [
            a for a in self.alertas
            if inicio <= a.data_hora <= fim
        ]
    
    def obter_resumo(self) -> Dict:
        """Obtém resumo dos alertas.
        
        Returns:
            Dicionário com resumo dos alertas.
        """
        total = len(self.alertas)
        por_nivel = {nivel.value: 0 for nivel in NivelAlerta}
        por_tipo = {tipo.value: 0 for tipo in TipoAlerta}
        
        for alerta in self.alertas:
            por_nivel[alerta.nivel.value] += 1
            por_tipo[alerta.tipo.value] += 1
        
        return {
            'total': total,
            'por_nivel': por_nivel,
            'por_tipo': por_tipo,
            'alertas_criticos': len(self.filtrar_por_nivel(NivelAlerta.CRITICAL)),
            'alertas_warning': len(self.filtrar_por_nivel(NivelAlerta.WARNING)),
            'alertas_info': len(self.filtrar_por_nivel(NivelAlerta.INFO))
        }
    
    def exportar_alertas(self, formato: str = 'dict') -> List[Dict]:
        """Exporta alertas para diferentes formatos.
        
        Args:
            formato: Formato de exportação ('dict', 'dataframe').
            
        Returns:
            Alertas exportados no formato especificado.
        """
        if formato == 'dict':
            return [a.to_dict() for a in self.alertas]
        elif formato == 'dataframe':
            return pd.DataFrame([a.to_dict() for a in self.alertas])
        else:
            raise ValueError(f"Formato não suportado: {formato}")
    
    def limpar_alertas(self):
        """Limpa todos os alertas."""
        self.alertas = []
        logger.info("Alertas limpos")


def configurar_alertas_padrao(df: pd.DataFrame) -> GestorAlertas:
    """Configura alertas padrão para o DataFrame.
    
    Args:
        df: DataFrame com dados de consumo.
        
    Returns:
        GestorAlertas configurado com regras padrão.
    """
    gestor = GestorAlertas(df)
    
    # Configurar regras padrão
    media_diaria = df.groupby(df['Data'].dt.date)['Consumo registado (kW)'].sum().mean()
    media_hora = df['Consumo registado (kW)'].mean()
    desvio = df['Consumo registado (kW)'].std()
    
    # Consumo diário alto (2x média)
    gestor.adicionar_regra_consumo_diario(limite_kw=media_diaria * 2)
    
    # Consumo horário alto (3x média)
    gestor.adicionar_regra_consumo_horario(limite_kw=media_hora * 3)
    
    # Aumento mensal (50%)
    gestor.adicionar_regra_aumento_mensal(percentual=50)
    
    # Anomalias (Z-score > 3)
    gestor.adicionar_regra_anomalia(z_score=3.0)
    
    # Custo alto (se disponível)
    if 'Custo_EUR' in df.columns:
        custo_medio = df.groupby(['Ano', 'Mes'])['Custo_EUR'].sum().mean()
        gestor.adicionar_regra_custo_alto(limite_eur=custo_medio * 1.5)
    
    logger.info("Alertas padrão configurados")
    return gestor
