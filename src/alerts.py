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
        self.df = df.copy()
        self.alertas: List[Alerta] = []
        self.regras: List[Dict] = []
        logger.info(f"GestorAlertas inicializado com {len(df)} registros")
    
    def analisar_resumo(self, sensibilidade: float = 1.0) -> Dict:
        """Gera um resumo de alertas com base na sensibilidade.
        
        Args:
            sensibilidade: Fator de sensibilidade (0.5=conservador, 1.0=normal, 2.0=sensível).
        
        Returns:
            Dicionário com resumo estruturado por categoria.
        """
        consumo = self.df['Consumo registado (kW)']
        media = consumo.mean()
        desvio = consumo.std()
        
        consumo_diario = self.df.groupby(self.df['Data'].dt.date)['Consumo registado (kW)'].sum()
        media_diaria = consumo_diario.mean()
        
        resultado = {}
        
        limiar_diario = 1 + 1.0 / sensibilidade
        picos = consumo_diario[consumo_diario > media_diaria * limiar_diario]
        if len(picos) > 0:
            pior = picos.max()
            ratio = pior / media_diaria if media_diaria > 0 else 0
            if ratio > 4:
                dica = (
                    f"O pior dia ({pior:.1f} kW) é {ratio:.0f}x superior à média — "
                    "isto é quase certamente um pico de um aparelho de alto consumo "
                    "(aquecimento central, termoacumulador, ar-condicionado). "
                    "Verifique o separador Visão Geral para identificar a hora exata."
                )
            else:
                dica = (
                    "Verifique aparelhos que ficam ligados em standby "
                    "(TV, routers, carregadores) e confira o isolamento térmico."
                )
            resultado['consumo_diario'] = {
                'total': len(picos),
                'nivel': 'warning' if len(picos) <= len(consumo_diario) * 0.2 else 'critical',
                'pior_dia': pior,
                'media_diaria': media_diaria,
                'dias_afetados': f"{len(picos)}/{len(consumo_diario)}",
                'dica': dica,
            }
        
        z_threshold = 3.0 / sensibilidade
        if desvio > 0:
            z_scores = ((consumo - media) / desvio).abs()
            anomalias_mask = z_scores > z_threshold
            n_anomalias = anomalias_mask.sum()
        else:
            n_anomalias = 0
        
        if n_anomalias > 0:
            resultado['anomalias'] = {
                'total': int(n_anomalias),
                'nivel': 'warning' if n_anomalias <= 10 else 'critical',
                'z_threshold': z_threshold,
                'pico_z': float(z_scores.max()) if desvio > 0 else 0,
                'dica': (
                    f"Foram encontrados {n_anomalias} registos com consumo anormalmente alto. "
                    "Isto pode indicar um aparelho avariado ou um pico de uso (ex: aquecimento elétrico). "
                    "Verifique os momentos de maior consumo no separador Visão Geral."
                ),
            }
        
        if 'Ano' in self.df.columns and 'Mes' in self.df.columns:
            consumo_mensal = self.df.groupby(['Ano', 'Mes'])['Consumo registado (kW)'].sum()
            meses_com_aumento = []
            for i in range(1, len(consumo_mensal)):
                anterior = consumo_mensal.iloc[i - 1]
                atual = consumo_mensal.iloc[i]
                if anterior > 0:
                    pct = (atual - anterior) / anterior * 100
                    if pct > 20 / sensibilidade:
                        meses_com_aumento.append({
                            'de': consumo_mensal.index[i - 1],
                            'para': consumo_mensal.index[i],
                            'aumento_pct': pct,
                        })
            if meses_com_aumento:
                maior = max(meses_com_aumento, key=lambda x: x['aumento_pct'])
                resultado['tendencia'] = {
                    'total': len(meses_com_aumento),
                    'nivel': 'warning',
                    'maior_aumento': maior['aumento_pct'],
                    'maior_de': maior['de'],
                    'maior_para': maior['para'],
                    'dica': (
                        "O consumo tem vindo a aumentar. Possíveis causas: uso de aquecimento/ar-condicionado, "
                        "mais pessoas em casa, ou aparelhos mais antigos. Considere rever a tarifa contratada "
                        "e verificar o isolamento da habitação."
                    ),
                }
        
        if 'Custo_EUR' in self.df.columns:
            custo_total = self.df['Custo_EUR'].sum()
            custo_mensal = self.df.groupby(['Ano', 'Mes'])['Custo_EUR'].sum()
            media_custo = custo_mensal.mean()
            custo_alto = custo_mensal[custo_mensal > media_custo * (1 + 0.3 / sensibilidade)]
            if len(custo_alto) > 0:
                resultado['custo'] = {
                    'total': len(custo_alto),
                    'nivel': 'warning' if len(custo_alto) <= len(custo_mensal) * 0.3 else 'critical',
                    'custo_medio_mensal': media_custo,
                    'pior_mes': float(custo_alto.max()),
                    'dias_analisados': int((self.df['Data'].max() - self.df['Data'].min()).days + 1),
                    'dica': (
                        f"O custo médio mensal é €{media_custo:.2f}. "
                        "Considere passar para tarifa bi-horária ou tri-horária se a maioria "
                        "do consumo for fora do horário de ponta (ver separador Tarifas)."
                    ),
                }
        
        resultado['resumo_geral'] = {
            'total_alertas': sum(v['total'] for v in resultado.values() if isinstance(v, dict) and 'total' in v),
            'n_categorias': len(resultado),
            'registos_analisados': len(self.df),
        }
        
        return resultado
    
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
        
        mask = self.df['Consumo registado (kW)'] > regra['limite_kw']
        excedentes = self.df[mask]
        
        for _, row in excedentes.iterrows():
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
        
        media = self.df['Consumo registado (kW)'].mean()
        desvio = self.df['Consumo registado (kW)'].std()
        
        if desvio == 0:
            return alertas
        
        z_scores = ((self.df['Consumo registado (kW)'] - media) / desvio).abs()
        mask = z_scores > regra['z_score']
        anomalias = self.df[mask]
        z_scores_filtrados = z_scores[mask]
        
        for _, row in anomalias.iterrows():
            z = z_scores_filtrados.loc[row.name]
            alerta = Alerta(
                tipo=regra['tipo'],
                nivel=regra['nivel'],
                mensagem=f"Anomalia detectada: Z-score de {z:.2f}",
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

