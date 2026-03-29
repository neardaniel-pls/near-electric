"""Módulo para visualização de dados de consumo de eletricidade."""

from typing import Optional, List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging


logger = logging.getLogger(__name__)

_ESTILO_PADRAO = 'seaborn-v0_8-darkgrid'
_PALETA_PADRAO = 'husl'
_estilo_configurado = False


def _configurar_estilo():
    global _estilo_configurado
    if not _estilo_configurado:
        plt.style.use(_ESTILO_PADRAO)
        sns.set_palette(_PALETA_PADRAO)
        _estilo_configurado = True


class VisualizadorConsumo:
    """Classe para visualização de consumo de eletricidade."""
    
    def __init__(self, df: pd.DataFrame, figsize: tuple = (12, 6)):
        _configurar_estilo()
        self.df = df.copy()
        self.figsize = figsize
    
    def plotar_consumo_temporal(
        self, 
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota consumo ao longo do tempo.
        
        Args:
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if 'DataHora' not in self.df.columns or 'Consumo registado (kW)' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        fig, ax = plt.subplots(figsize=(20, 8))
        ax.plot(
            self.df['DataHora'], 
            self.df['Consumo registado (kW)'], 
            linewidth=0.3, 
            alpha=0.6
        )
        ax.set_title('Consumo de Eletricidade ao Longo do Tempo', fontsize=14, fontweight='bold')
        ax.set_xlabel('Data e Hora', fontsize=12)
        ax.set_ylabel('Consumo (kW)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_consumo_por_periodo(
        self,
        coluna_periodo: str = 'NomeMes',
        tipo_grafico: str = 'bar',
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota consumo por período (mês, dia da semana, hora).
        
        Args:
            coluna_periodo: Coluna para agrupamento.
            tipo_grafico: Tipo de gráfico ('bar', 'line').
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if coluna_periodo not in self.df.columns or 'Consumo registado (kW)' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        # Agrupar dados
        df_periodo = self.df.groupby(coluna_periodo)['Consumo registado (kW)'].sum()
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if tipo_grafico == 'bar':
            df_periodo.plot(kind='bar', ax=ax, color='steelblue')
        else:
            df_periodo.plot(kind='line', ax=ax, marker='o', linewidth=2)
        
        ax.set_title(f'Consumo Total por {coluna_periodo}', fontsize=14, fontweight='bold')
        ax.set_xlabel(coluna_periodo, fontsize=12)
        ax.set_ylabel('Consumo Total (kW)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_boxplot_por_periodo(
        self,
        coluna_periodo: str = 'NomeDiaSemana',
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota boxplot de consumo por período.
        
        Args:
            coluna_periodo: Coluna para agrupamento.
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if coluna_periodo not in self.df.columns or 'Consumo registado (kW)' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(
            x=coluna_periodo, 
            y='Consumo registado (kW)', 
            data=self.df, 
            ax=ax
        )
        ax.set_title(f'Distribuição do Consumo por {coluna_periodo}', fontsize=14, fontweight='bold')
        ax.set_xlabel(coluna_periodo, fontsize=12)
        ax.set_ylabel('Consumo (kW)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_consumo_medio_hora(
        self,
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota consumo médio por hora do dia.
        
        Args:
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if 'HoraNum' not in self.df.columns or 'Consumo registado (kW)' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        consumo_hora = self.df.groupby('HoraNum')['Consumo registado (kW)'].mean()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        consumo_hora.plot(kind='bar', color='coral', ax=ax)
        ax.set_title('Consumo Médio por Hora do Dia', fontsize=14, fontweight='bold')
        ax.set_xlabel('Hora do Dia', fontsize=12)
        ax.set_ylabel('Consumo Médio (kW)', fontsize=12)
        ax.tick_params(axis='x', rotation=0)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_comparacao_periodos(
        self,
        coluna_arquivo: str = 'Arquivo',
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota comparação de consumo médio por hora entre períodos.
        
        Args:
            coluna_arquivo: Coluna que identifica o período/arquivo.
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if coluna_arquivo not in self.df.columns or 'HoraNum' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        if 'Consumo registado (kW)' not in self.df.columns:
            return None
        
        periodos = self.df[coluna_arquivo].unique()
        
        if len(periodos) < 2:
            logger.warning("É necessário pelo menos 2 períodos para comparação")
            return None
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for periodo in periodos:
            df_periodo = self.df[self.df[coluna_arquivo] == periodo]
            consumo_hora = df_periodo.groupby('HoraNum')['Consumo registado (kW)'].mean()
            ax.plot(consumo_hora.index, consumo_hora.values, label=periodo, linewidth=2)
        
        ax.set_title('Comparação de Consumo Médio por Hora', fontsize=14, fontweight='bold')
        ax.set_xlabel('Hora do Dia', fontsize=12)
        ax.set_ylabel('Consumo Médio (kW)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_custo_por_periodo(
        self,
        coluna_periodo: str = 'Arquivo',
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota custo por período.
        
        Args:
            coluna_periodo: Coluna para agrupamento.
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if coluna_periodo not in self.df.columns or 'Custo_EUR' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        custo_periodo = self.df.groupby(coluna_periodo)['Custo_EUR'].sum()
        media_custo = custo_periodo.mean()
        
        fig, ax = plt.subplots(figsize=self.figsize)
        custo_periodo.plot(kind='bar', color='green', ax=ax)
        ax.set_title('Custo por Período', fontsize=14, fontweight='bold')
        ax.set_xlabel(coluna_periodo, fontsize=12)
        ax.set_ylabel('Custo (€)', fontsize=12)
        ax.tick_params(axis='x', rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(
            y=media_custo, 
            color='red', 
            linestyle='--', 
            label=f'Média: €{media_custo:.2f}'
        )
        ax.legend()
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_tendencia(
        self,
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota tendência de consumo por mês.
        
        Args:
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if 'Ano' not in self.df.columns or 'Mes' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        if 'Consumo registado (kW)' not in self.df.columns:
            return None
        
        consumo_mes = self.df.groupby(['Ano', 'Mes'])['Consumo registado (kW)'].sum()
        
        if len(consumo_mes) < 2:
            logger.warning("É necessário pelo menos 2 meses para análise de tendência")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(
            range(len(consumo_mes)), 
            consumo_mes.values, 
            marker='o', 
            linewidth=2, 
            markersize=8
        )
        ax.set_title('Tendência de Consumo por Mês', fontsize=14, fontweight='bold')
        ax.set_xlabel('Mês (cronológico)', fontsize=12)
        ax.set_ylabel('Consumo Total (kW)', fontsize=12)
        ax.set_xticks(
            range(len(consumo_mes)),
            [f"{row['Mes']}/{row['Ano']}" for _, row in consumo_mes.reset_index().iterrows()],
            rotation=45,
            ha='right'
        )
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def criar_multiplos_graficos(
        self,
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Cria uma figura com múltiplos gráficos.
        
        Args:
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Gráfico 1: Consumo médio por hora
        if 'HoraNum' in self.df.columns and 'Consumo registado (kW)' in self.df.columns:
            consumo_hora = self.df.groupby('HoraNum')['Consumo registado (kW)'].mean()
            consumo_hora.plot(kind='bar', ax=axes[0], color='coral')
            axes[0].set_title('Consumo Médio por Hora')
            axes[0].set_xlabel('Hora')
            axes[0].set_ylabel('kW')
            axes[0].tick_params(axis='x', rotation=0)
        
        # Gráfico 2: Consumo por dia da semana
        if 'NomeDiaSemana' in self.df.columns and 'Consumo registado (kW)' in self.df.columns:
            consumo_dia = self.df.groupby('NomeDiaSemana')['Consumo registado (kW)'].sum()
            consumo_dia.plot(kind='bar', ax=axes[1], color='steelblue')
            axes[1].set_title('Consumo por Dia da Semana')
            axes[1].set_xlabel('Dia')
            axes[1].set_ylabel('kW')
            axes[1].tick_params(axis='x', rotation=45)
        
        # Gráfico 3: Boxplot por dia da semana
        if 'NomeDiaSemana' in self.df.columns and 'Consumo registado (kW)' in self.df.columns:
            sns.boxplot(
                x='NomeDiaSemana', 
                y='Consumo registado (kW)', 
                data=self.df, 
                ax=axes[2]
            )
            axes[2].set_title('Distribuição por Dia da Semana')
            axes[2].set_xlabel('Dia')
            axes[2].set_ylabel('kW')
            axes[2].tick_params(axis='x', rotation=45)
        
        # Gráfico 4: Custo por período (se disponível)
        if 'Custo_EUR' in self.df.columns and 'Arquivo' in self.df.columns:
            custo_periodo = self.df.groupby('Arquivo')['Custo_EUR'].sum()
            custo_periodo.plot(kind='bar', ax=axes[3], color='green')
            axes[3].set_title('Custo por Período')
            axes[3].set_xlabel('Período')
            axes[3].set_ylabel('€')
            axes[3].tick_params(axis='x', rotation=45)
        elif 'NomeMes' in self.df.columns and 'Consumo registado (kW)' in self.df.columns:
            consumo_mes = self.df.groupby('NomeMes')['Consumo registado (kW)'].sum()
            consumo_mes.plot(kind='bar', ax=axes[3], color='mediumseagreen')
            axes[3].set_title('Consumo por Mês')
            axes[3].set_xlabel('Mês')
            axes[3].set_ylabel('kW')
            axes[3].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráficos salvos em: {caminho}")
        
        return fig
    
    def plotar_heatmap_hora_dia(
        self,
        salvar: bool = False,
        caminho: Optional[str] = None,
        cmap: str = 'YlOrRd'
    ) -> plt.Figure:
        """Plota heatmap de consumo por hora e dia da semana.
        
        Args:
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            cmap: Colormap para o heatmap.
            
        Returns:
            Figure do matplotlib.
        """
        if 'HoraNum' not in self.df.columns or 'NomeDiaSemana' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        if 'Consumo registado (kW)' not in self.df.columns:
            return None
        
        # Criar pivot table
        heatmap_data = self.df.pivot_table(
            values='Consumo registado (kW)',
            index='NomeDiaSemana',
            columns='HoraNum',
            aggfunc='mean'
        )
        
        # Ordenar dias da semana
        ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 
                      'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        heatmap_data = heatmap_data.reindex(ordem_dias)
        
        fig, ax = plt.subplots(figsize=(16, 8))
        sns.heatmap(
            heatmap_data,
            cmap=cmap,
            annot=False,
            cbar_kws={'label': 'Consumo Médio (kW)'},
            ax=ax
        )
        ax.set_title('Heatmap de Consumo por Hora e Dia da Semana', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Hora do Dia', fontsize=12)
        ax.set_ylabel('Dia da Semana', fontsize=12)
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_heatmap_hora_mes(
        self,
        salvar: bool = False,
        caminho: Optional[str] = None,
        cmap: str = 'YlOrRd'
    ) -> plt.Figure:
        """Plota heatmap de consumo por hora e mês.
        
        Args:
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            cmap: Colormap para o heatmap.
            
        Returns:
            Figure do matplotlib.
        """
        if 'HoraNum' not in self.df.columns or 'NomeMes' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        if 'Consumo registado (kW)' not in self.df.columns:
            return None
        
        # Criar pivot table
        heatmap_data = self.df.pivot_table(
            values='Consumo registado (kW)',
            index='NomeMes',
            columns='HoraNum',
            aggfunc='mean'
        )
        
        # Ordenar meses
        ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        heatmap_data = heatmap_data.reindex(ordem_meses)
        
        fig, ax = plt.subplots(figsize=(16, 10))
        sns.heatmap(
            heatmap_data,
            cmap=cmap,
            annot=False,
            cbar_kws={'label': 'Consumo Médio (kW)'},
            ax=ax
        )
        ax.set_title('Heatmap de Consumo por Hora e Mês', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Hora do Dia', fontsize=12)
        ax.set_ylabel('Mês', fontsize=12)
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_distribuicao_consumo(
        self,
        bins: int = 50,
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota histograma e KDE da distribuição de consumo.
        
        Args:
            bins: Número de bins para o histograma.
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if 'Consumo registado (kW)' not in self.df.columns:
            logger.error("Coluna necessária não encontrada")
            return None
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histograma
        axes[0].hist(
            self.df['Consumo registado (kW)'], 
            bins=bins, 
            color='steelblue',
            alpha=0.7,
            edgecolor='black'
        )
        axes[0].set_title('Histograma de Consumo', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Consumo (kW)', fontsize=12)
        axes[0].set_ylabel('Frequência', fontsize=12)
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # KDE
        sns.kdeplot(
            data=self.df['Consumo registado (kW)'],
            ax=axes[1],
            color='coral',
            fill=True,
            alpha=0.5
        )
        axes[1].set_title('Distribuição de Consumo (KDE)', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Consumo (kW)', fontsize=12)
        axes[1].set_ylabel('Densidade', fontsize=12)
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_comparacao_anual(
        self,
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota comparação de consumo entre anos (year-over-year).
        
        Args:
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if 'Ano' not in self.df.columns or 'Mes' not in self.df.columns:
            logger.error("Colunas necessárias não encontradas")
            return None
        
        if 'Consumo registado (kW)' not in self.df.columns:
            return None
        
        # Agrupar por ano e mês
        df_agrupado = self.df.groupby(['Ano', 'Mes'])['Consumo registado (kW)'].sum().reset_index()
        
        # Verificar se há múltiplos anos
        anos = df_agrupado['Ano'].unique()
        if len(anos) < 2:
            logger.warning("É necessário pelo menos 2 anos para comparação anual")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for ano in anos:
            df_ano = df_agrupado[df_agrupado['Ano'] == ano]
            ax.plot(
                df_ano['Mes'],
                df_ano['Consumo registado (kW)'],
                marker='o',
                linewidth=2,
                label=f'{ano}'
            )
        
        ax.set_title('Comparação de Consumo Anual (Year-over-Year)', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Mês', fontsize=12)
        ax.set_ylabel('Consumo Total (kW)', fontsize=12)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                           'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig
    
    def plotar_kpis(
        self,
        salvar: bool = False,
        caminho: Optional[str] = None
    ) -> plt.Figure:
        """Plota painel de KPIs (Key Performance Indicators).
        
        Args:
            salvar: Se True, salva a figura.
            caminho: Caminho para salvar a figura.
            
        Returns:
            Figure do matplotlib.
        """
        if 'Consumo registado (kW)' not in self.df.columns:
            logger.error("Coluna necessária não encontrada")
            return None
        
        # Calcular KPIs
        total_kw = self.df['Consumo registado (kW)'].sum()
        media_kw = self.df['Consumo registado (kW)'].mean()
        maximo_kw = self.df['Consumo registado (kW)'].max()
        minimo_kw = self.df['Consumo registado (kW)'].min()
        
        # Calcular custo se disponível
        custo_total = self.df['Custo_EUR'].sum() if 'Custo_EUR' in self.df.columns else None
        
        # Criar figura com subplots para KPIs
        fig, axes = plt.subplots(2, 3, figsize=(15, 8))
        axes = axes.flatten()
        
        # KPI 1: Consumo Total
        axes[0].text(0.5, 0.5, f'{total_kw:.2f} kW', 
                     ha='center', va='center', fontsize=24, fontweight='bold',
                     color='steelblue')
        axes[0].set_title('Consumo Total', fontsize=12, fontweight='bold')
        axes[0].axis('off')
        
        # KPI 2: Consumo Médio
        axes[1].text(0.5, 0.5, f'{media_kw:.4f} kW', 
                     ha='center', va='center', fontsize=24, fontweight='bold',
                     color='coral')
        axes[1].set_title('Consumo Médio', fontsize=12, fontweight='bold')
        axes[1].axis('off')
        
        # KPI 3: Consumo Máximo
        axes[2].text(0.5, 0.5, f'{maximo_kw:.2f} kW', 
                     ha='center', va='center', fontsize=24, fontweight='bold',
                     color='red')
        axes[2].set_title('Consumo Máximo', fontsize=12, fontweight='bold')
        axes[2].axis('off')
        
        # KPI 4: Consumo Mínimo
        axes[3].text(0.5, 0.5, f'{minimo_kw:.4f} kW', 
                     ha='center', va='center', fontsize=24, fontweight='bold',
                     color='green')
        axes[3].set_title('Consumo Mínimo', fontsize=12, fontweight='bold')
        axes[3].axis('off')
        
        # KPI 5: Número de Registros
        axes[4].text(0.5, 0.5, f'{len(self.df):,}', 
                     ha='center', va='center', fontsize=24, fontweight='bold',
                     color='purple')
        axes[4].set_title('Registros', fontsize=12, fontweight='bold')
        axes[4].axis('off')
        
        # KPI 6: Custo Total (se disponível)
        if custo_total is not None:
            axes[5].text(0.5, 0.5, f'€{custo_total:.2f}', 
                         ha='center', va='center', fontsize=24, fontweight='bold',
                         color='orange')
            axes[5].set_title('Custo Total', fontsize=12, fontweight='bold')
        else:
            axes[5].text(0.5, 0.5, 'N/A', 
                         ha='center', va='center', fontsize=24, fontweight='bold',
                         color='gray')
            axes[5].set_title('Custo Total', fontsize=12, fontweight='bold')
        axes[5].axis('off')
        
        plt.suptitle('Key Performance Indicators (KPIs)', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        if salvar and caminho:
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {caminho}")
        
        return fig

