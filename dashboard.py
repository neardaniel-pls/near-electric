#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard interativo para análise de consumo de eletricidade.

Este dashboard usa Streamlit para criar uma interface interativa
para visualização e análise de dados de consumo.
"""

import sys
from pathlib import Path

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

from src.utils import setup_logging, carregar_config, validar_diretorio
from src.data_loader import CarregadorDados
from src.data_processor import ProcessadorDados
from src.analyzer import AnalisadorConsumo
from src.visualizer import VisualizadorConsumo
from src.seasonal_analyzer import AnalisadorSazonal
from src.forecaster import PrevisorConsumo
from src.alerts import configurar_alertas_padrao, NivelAlerta

# Configurar página
st.set_page_config(
    page_title="Dashboard de Consumo de Eletricidade",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Título da aplicação
st.title("⚡ Dashboard de Análise de Consumo de Eletricidade")
st.markdown("---")

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações")

# Caminho dos dados
data_dir = st.sidebar.text_input("Diretório de Dados", value="data")
config_file = st.sidebar.text_input("Ficheiro de Configuração", value="config/config.yaml")

# Nível de logging
log_level = st.sidebar.selectbox(
    "Nível de Logging",
    ["DEBUG", "INFO", "WARNING", "ERROR"],
    index=1
)

# Botão para carregar dados
if st.sidebar.button("🔄 Carregar Dados"):
    with st.spinner("Carregando dados..."):
        try:
            # Configurar logging
            logger = setup_logging(log_level=log_level)
            
            # Carregar configuração
            config = carregar_config(config_file)
            
            # Carregar dados
            carregador = CarregadorDados(data_dir)
            df_completo = carregador.carregar_todos()
            
            if len(df_completo) == 0:
                st.error("Nenhum dado foi carregado. Verifique se há ficheiros CSV no diretório.")
            else:
                # Filtrar dados reais
                df_real = carregador.filtrar_estado(df_completo, estado='Real')
                
                # Processar dados
                processador = ProcessadorDados(df_real)
                df_processado = processador.limpar_dados(estrategia='remover')
                tarifa = config.get('tarifas', {}).get('parametros', {}).get('simples', {}).get('preco', 0.25)
                df_processado = processador.adicionar_colunas_calculadas(tarifa=tarifa)
                
                # Guardar no session state
                st.session_state['df'] = df_processado
                st.session_state['config'] = config
                st.session_state['carregado'] = True
                
                st.success(f"Dados carregados com sucesso! {len(df_processado)} registros.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")

# Verificar se dados estão carregados
if 'carregado' not in st.session_state or not st.session_state['carregado']:
    st.info("👈 Use a barra lateral para carregar os dados de consumo.")
    st.stop()

df = st.session_state['df']
config = st.session_state['config']

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Filtro de data
if 'Data' in df.columns:
    data_min = df['Data'].min().date()
    data_max = df['Data'].max().date()
    
    data_inicio = st.sidebar.date_input("Data Início", value=data_min, min_value=data_min, max_value=data_max)
    data_fim = st.sidebar.date_input("Data Fim", value=data_max, min_value=data_min, max_value=data_max)
    
    # Aplicar filtro de data
    df_filtrado = df[
        (df['Data'].dt.date >= data_inicio) &
        (df['Data'].dt.date <= data_fim)
    ].copy()
else:
    df_filtrado = df.copy()

# Filtro de estado
if 'Estado' in df.columns:
    estados = df['Estado'].unique()
    estado_selecionado = st.sidebar.multiselect("Estado", estados, default=['Real'])
    if estado_selecionado:
        df_filtrado = df_filtrado[df_filtrado['Estado'].isin(estado_selecionado)]

# Mostrar estatísticas dos dados filtrados
st.sidebar.header("📊 Estatísticas")
st.sidebar.metric("Registros", len(df_filtrado))
st.sidebar.metric("Consumo Total", f"{df_filtrado['Consumo registado (kW)'].sum():.2f} kW")
st.sidebar.metric("Consumo Médio", f"{df_filtrado['Consumo registado (kW)'].mean():.4f} kW")

# Tabs para diferentes visualizações
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Visão Geral", 
    "📅 Análise Sazonal", 
    "🔮 Previsão", 
    "⚠️ Alertas", 
    "💰 Tarifas",
    "📋 Dados"
])

# Tab 1: Visão Geral
with tab1:
    st.header("Visão Geral do Consumo")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Consumo Total",
            f"{df_filtrado['Consumo registado (kW)'].sum():.2f} kW",
            delta=f"{df_filtrado['Consumo registado (kW)'].sum() / df['Consumo registado (kW)'].sum() * 100:.1f}% do total"
        )
    
    with col2:
        st.metric(
            "Consumo Médio",
            f"{df_filtrado['Consumo registado (kW)'].mean():.4f} kW"
        )
    
    with col3:
        st.metric(
            "Consumo Máximo",
            f"{df_filtrado['Consumo registado (kW)'].max():.2f} kW"
        )
    
    with col4:
        st.metric(
            "Consumo Mínimo",
            f"{df_filtrado['Consumo registado (kW)'].min():.4f} kW"
        )
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Consumo ao Longo do Tempo")
        if 'DataHora' in df_filtrado.columns:
            visualizador = VisualizadorConsumo(df_filtrado)
            fig = visualizador.plotar_consumo_temporal()
            st.pyplot(fig)
            plt.close(fig)
    
    with col2:
        st.subheader("Consumo por Dia da Semana")
        if 'NomeDiaSemana' in df_filtrado.columns:
            visualizador = VisualizadorConsumo(df_filtrado)
            fig = visualizador.plotar_consumo_por_periodo('NomeDiaSemana')
            st.pyplot(fig)
            plt.close(fig)
    
    st.markdown("---")
    
    # Distribuição de consumo
    st.subheader("Distribuição de Consumo")
    visualizador = VisualizadorConsumo(df_filtrado)
    fig = visualizador.plotar_distribuicao_consumo()
    st.pyplot(fig)
    plt.close(fig)

# Tab 2: Análise Sazonal
with tab2:
    st.header("Análise Sazonal")
    
    analisador_sazonal = AnalisadorSazonal(df_filtrado)
    
    # Comparação por estação
    st.subheader("Consumo por Estação")
    comparacao_estacoes = analisador_sazonal.comparar_estacoes()
    st.dataframe(comparacao_estacoes)
    
    # Gráfico de estação
    fig, ax = plt.subplots(figsize=(10, 6))
    comparacao_estacoes['Total (kW)'].plot(kind='bar', color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'], ax=ax)
    ax.set_title('Consumo Total por Estação', fontweight='bold')
    ax.set_ylabel('Consumo (kW)')
    ax.set_xlabel('Estação')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    
    st.markdown("---")
    
    # Padrão semanal
    st.subheader("Padrão Semanal")
    padrao_semanal = analisador_sazonal.analisar_padrao_semanal()
    st.dataframe(padrao_semanal)
    
    # Gráfico de padrão semanal
    fig, ax = plt.subplots(figsize=(10, 6))
    padrao_semanal['Total (kW)'].plot(kind='bar', color='steelblue', ax=ax)
    ax.set_title('Consumo por Dia da Semana', fontweight='bold')
    ax.set_ylabel('Consumo (kW)')
    ax.set_xlabel('Dia da Semana')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    
    st.markdown("---")
    
    # Heatmap
    st.subheader("Heatmap de Consumo")
    visualizador = VisualizadorConsumo(df_filtrado)
    fig = visualizador.plotar_heatmap_hora_dia()
    st.pyplot(fig)
    plt.close(fig)
    
    # Índice sazonal
    st.markdown("---")
    st.subheader("Índice Sazonal")
    indice_sazonal = analisador_sazonal.calcular_indice_sazonal()
    st.dataframe(indice_sazonal)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['green' if x < 100 else 'red' for x in indice_sazonal['Índice Sazonal']]
    ax.bar(indice_sazonal['Mês'], indice_sazonal['Índice Sazonal'], color=colors)
    ax.axhline(y=100, color='blue', linestyle='--', label='Média')
    ax.set_title('Índice Sazonal por Mês', fontweight='bold')
    ax.set_ylabel('Índice')
    ax.set_xlabel('Mês')
    plt.xticks(rotation=45)
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Tab 3: Previsão
with tab3:
    st.header("Previsão de Consumo")
    
    # Configurar previsão
    col1, col2 = st.columns(2)
    
    with col1:
        dias_previsao = st.slider("Dias para Previsão", min_value=1, max_value=30, value=7)
    
    with col2:
        metodo_previsao = st.selectbox(
            "Método de Previsão",
            ["Ensemble", "Média Móvel", "Padrão Semanal", "Padrão Diário", "Tendência"]
        )
    
    # Gerar previsão
    previsor = PrevisorConsumo(df_filtrado)
    
    if metodo_previsao == "Ensemble":
        df_previsao = previsor.prever_ensemble(dias_futuros=dias_previsao)
    elif metodo_previsao == "Média Móvel":
        df_previsao = previsor.prever_media_movel(dias_futuros=dias_previsao)
    elif metodo_previsao == "Padrão Semanal":
        df_previsao = previsor.prever_por_padrao_semanal(dias_futuros=dias_previsao)
    elif metodo_previsao == "Padrão Diário":
        df_previsao = previsor.prever_por_padrao_diario(dias_futuros=dias_previsao)
    else:
        df_previsao = previsor.prever_por_tendencia(dias_futuros=dias_previsao)
    
    # Calcular intervalo de confiança
    df_previsao = previsor.calcular_intervalo_confianca(df_previsao)
    
    # Mostrar previsão
    st.subheader(f"Previsão para os próximos {dias_previsao} dias")
    
    # Resumo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Previsto", f"{df_previsao['Consumo_Previsto (kW)'].sum():.2f} kW")
    with col2:
        st.metric("Mínimo Previsto", f"{df_previsao['Consumo_Previsto (kW)'].min():.4f} kW")
    with col3:
        st.metric("Máximo Previsto", f"{df_previsao['Consumo_Previsto (kW)'].max():.2f} kW")
    
    # Gráfico de previsão
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Dados históricos
    ax.plot(
        df_filtrado['DataHora'],
        df_filtrado['Consumo registado (kW)'],
        label='Histórico',
        alpha=0.5,
        linewidth=0.5
    )
    
    # Previsão
    ax.plot(
        df_previsao['DataHora'],
        df_previsao['Consumo_Previsto (kW)'],
        label='Previsão',
        color='red',
        linewidth=2
    )
    
    # Intervalo de confiança
    ax.fill_between(
        df_previsao['DataHora'],
        df_previsao['Limite_Inferior (kW)'],
        df_previsao['Limite_Superior (kW)'],
        alpha=0.2,
        color='red',
        label='Intervalo de Confiança (95%)'
    )
    
    ax.set_title('Previsão de Consumo', fontweight='bold')
    ax.set_xlabel('Data e Hora')
    ax.set_ylabel('Consumo (kW)')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    
    # Tabela de previsão
    st.markdown("---")
    st.subheader("Detalhes da Previsão")
    df_previsao_display = df_previsao.copy()
    df_previsao_display['Data'] = df_previsao_display['DataHora'].dt.strftime('%Y-%m-%d %H:%M')
    st.dataframe(df_previsao_display[['Data', 'Consumo_Previsto (kW)', 'Limite_Inferior (kW)', 'Limite_Superior (kW)']])

# Tab 4: Alertas
with tab4:
    st.header("Alertas de Consumo")
    
    # Configurar alertas
    st.subheader("Configurar Alertas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        limite_diario = st.number_input("Limite de Consumo Diário (kW)", value=50.0, min_value=0.0)
        limite_horario = st.number_input("Limite de Consumo Horário (kW)", value=2.0, min_value=0.0)
    
    with col2:
        aumento_mensal = st.number_input("Aumento Mensal (%)", value=50.0, min_value=0.0)
        z_score = st.number_input("Z-score para Anomalias", value=3.0, min_value=0.0)
    
    # Configurar gestor de alertas
    from src.alerts import GestorAlertas, TipoAlerta
    gestor = GestorAlertas(df_filtrado)
    gestor.adicionar_regra_consumo_diario(limite_kw=limite_diario)
    gestor.adicionar_regra_consumo_horario(limite_kw=limite_horario)
    gestor.adicionar_regra_aumento_mensal(percentual=aumento_mensal)
    gestor.adicionar_regra_anomalia(z_score=z_score)
    
    # Verificar alertas
    alertas = gestor.verificar_todas_regras()
    
    # Mostrar resumo
    resumo = gestor.obter_resumo()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Alertas", resumo['total'])
    with col2:
        st.metric("Alertas Críticos", resumo['alertas_criticos'])
    with col3:
        st.metric("Alertas de Aviso", resumo['alertas_warning'])
    
    st.markdown("---")
    
    # Filtrar alertas
    filtro_nivel = st.selectbox("Filtrar por Nível", ["Todos", "CRITICAL", "WARNING", "INFO"])
    
    if filtro_nivel == "Todos":
        alertas_filtrados = alertas
    else:
        alertas_filtrados = gestor.filtrar_por_nivel(NivelAlerta(filtro_nivel))
    
    # Mostrar alertas
    if alertas_filtrados:
        st.subheader(f"Alertas Encontrados ({len(alertas_filtrados)})")
        
        for alerta in alertas_filtrados:
            cor = "🔴" if alerta.nivel == NivelAlerta.CRITICAL else "🟡" if alerta.nivel == NivelAlerta.WARNING else "🔵"
            st.markdown(f"{cor} **{alerta.tipo.value}** - {alerta.data_hora.strftime('%Y-%m-%d %H:%M')}")
            st.info(alerta.mensagem)
            st.markdown("---")
    else:
        st.success("✅ Nenhum alerta encontrado!")

# Tab 5: Tarifas
with tab5:
    st.header("Comparação de Tarifas")
    
    from src.tariff_calculator import TarifaSimples, TarifaBiHoraria, TarifaTriHoraria, comparar_tarifas, recomendar_tarifa
    
    # Configurar tarifas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        preco_simples = st.number_input("Preço Simples (€/kWh)", value=0.25, min_value=0.0, format="%.4f")
    
    with col2:
        preco_vazio = st.number_input("Preço Vazio (€/kWh)", value=0.104, min_value=0.0, format="%.4f")
        preco_cheio = st.number_input("Preço Cheio (€/kWh)", value=0.2584, min_value=0.0, format="%.4f")
    
    with col3:
        preco_ponta = st.number_input("Preço Ponta (€/kWh)", value=0.312, min_value=0.0, format="%.4f")
    
    # Criar tarifas
    tarifas = [
        TarifaSimples(preco_simples, "Simples"),
        TarifaBiHoraria(preco_vazio, preco_cheio, nome="Bi-horária"),
        TarifaTriHoraria(preco_vazio, preco_ponta, preco_cheio, nome="Tri-horária")
    ]
    
    # Comparar tarifas
    df_comparacao = comparar_tarifas(df_filtrado, tarifas)
    
    # Mostrar comparação
    st.subheader("Comparação de Custos")
    st.dataframe(df_comparacao)
    
    # Gráfico de comparação
    fig, ax = plt.subplots(figsize=(10, 6))
    df_comparacao.plot(kind='bar', x='tarifa', y='custo_total', ax=ax, color=['#3498db', '#2ecc71', '#f39c12'])
    ax.set_title('Comparação de Custos por Tarifa', fontweight='bold')
    ax.set_ylabel('Custo (€)')
    ax.set_xlabel('Tarifa')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    
    # Recomendação
    st.markdown("---")
    tarifa_recomendada, resumo_recomendacao = recomendar_tarifa(df_filtrado, tarifas)
    st.subheader("💡 Recomendação")
    st.success(f"A tarifa mais económica é: **{tarifa_recomendada.nome}**")
    st.info(f"Custo: €{resumo_recomendacao['custo_total']:.2f}")

# Tab 6: Dados
with tab6:
    st.header("Dados de Consumo")
    
    # Mostrar dados
    st.subheader("Dados Filtrados")
    st.dataframe(df_filtrado)
    
    # Estatísticas
    st.markdown("---")
    st.subheader("Estatísticas Descritivas")
    st.dataframe(df_filtrado.describe())
    
    # Download
    st.markdown("---")
    st.subheader("Exportar Dados")
    
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f'dados_consumo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

# Footer
st.markdown("---")
st.markdown("💡 **Dica:** Use os filtros na barra lateral para analisar períodos específicos.")
st.markdown("⚡ **Dashboard de Análise de Consumo de Eletricidade** - Desenvolvido com Streamlit")
