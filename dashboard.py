#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard interativo para análise de consumo de eletricidade.

Este dashboard usa Streamlit para criar uma interface interativa
para visualização e análise de dados de consumo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from src.utils import setup_logging, carregar_config, validar_diretorio
from src.data_loader import CarregadorDados
from src.data_processor import ProcessadorDados
from src.analyzer import AnalisadorConsumo
from src.visualizer import VisualizadorConsumo
from src.seasonal_analyzer import AnalisadorSazonal
from src.forecaster import PrevisorConsumo
from src.alerts import GestorAlertas
from src.power_analyzer import AnalisadorPotencia
from src.tariff_calculator import TarifaSimples, TarifaBiHoraria, TarifaTriHoraria, comparar_tarifas, recomendar_tarifa

try:
    config = carregar_config('config/config.yaml')
    POTENCIA_ATUAL_PADRAO = config.get('potencia', {}).get('atual', 10.35)
except Exception:
    POTENCIA_ATUAL_PADRAO = 10.35

st.set_page_config(
    page_title="Near Electric - Dashboard de Consumo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

st.title("⚡ Near Electric - Dashboard de Consumo de Eletricidade")
st.markdown("---")


def carregar_dados(data_dir, config_file):
    logger = setup_logging(log_level="INFO")
    config = carregar_config(config_file)
    carregador = CarregadorDados(data_dir)
    df_completo = carregador.carregar_todos()

    if len(df_completo) == 0:
        return None, None, False

    df_real = carregador.filtrar_estado(df_completo, estado='Real')
    processador = ProcessadorDados(df_real)
    df_processado = processador.limpar_dados(estrategia='remover')
    tarifa = config.get('tarifas', {}).get('parametros', {}).get('simples', {}).get('preco', 0.25)
    df_processado = processador.adicionar_colunas_calculadas(tarifa=tarifa)

    return df_processado, config, True


def _carregar_dados_com_erro(data_dir, config_file):
    with st.spinner("Carregando dados..."):
        try:
            df_loaded, config_loaded, sucesso = carregar_dados(data_dir, config_file)
            if sucesso:
                st.session_state['df'] = df_loaded
                st.session_state['config'] = config_loaded
                st.session_state['carregado'] = True
                st.success(f"Dados carregados com sucesso! {len(df_loaded)} registros.")
            else:
                st.error("Nenhum dado foi carregado. Verifique se há ficheiros CSV no diretório.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")


# Sidebar
st.sidebar.header("⚙️ Configurações")
data_dir = st.sidebar.text_input("Diretório de Dados", value="data")
config_file = st.sidebar.text_input("Ficheiro de Configuração", value="config/config.yaml")

if st.sidebar.button("🔄 Carregar Dados"):
    _carregar_dados_com_erro(data_dir, config_file)

if 'carregado' not in st.session_state:
    with st.spinner("Carregando dados..."):
        try:
            df_loaded, config_loaded, sucesso = carregar_dados(data_dir, config_file)
            if sucesso:
                st.session_state['df'] = df_loaded
                st.session_state['config'] = config_loaded
                st.session_state['carregado'] = True
        except Exception:
            pass

if 'carregado' not in st.session_state or not st.session_state['carregado']:
    st.info("👈 Coloque ficheiros CSV na pasta `data/` e use o botão acima para carregar.")
    st.stop()

df = st.session_state['df']
config = st.session_state['config']

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

if 'Data' in df.columns:
    data_min = df['Data'].min().date()
    data_max = df['Data'].max().date()

    data_inicio = st.sidebar.date_input("Data Início", value=data_min, min_value=data_min, max_value=data_max)
    data_fim = st.sidebar.date_input("Data Fim", value=data_max, min_value=data_min, max_value=data_max)

    if data_inicio > data_fim:
        st.sidebar.warning("Data início posterior à data fim. A trocar...")
        data_inicio, data_fim = data_fim, data_inicio

    df_filtrado = df[
        (df['Data'] >= pd.Timestamp(data_inicio)) &
        (df['Data'] < pd.Timestamp(data_fim) + pd.Timedelta(days=1))
    ].copy()
else:
    df_filtrado = df.copy()

if 'Estado' in df.columns:
    estados = df['Estado'].unique()
    estado_selecionado = st.sidebar.multiselect("Estado", estados, default=['Real'])
    if estado_selecionado:
        df_filtrado = df_filtrado[df_filtrado['Estado'].isin(estado_selecionado)]

# Sidebar - Estatísticas
st.sidebar.header("📊 Estatísticas")
st.sidebar.metric("Registros", f"{len(df_filtrado):,}")
st.sidebar.metric("Consumo Total", f"{df_filtrado['Consumo registado (kW)'].sum():.2f} kW")
st.sidebar.metric("Consumo Médio", f"{df_filtrado['Consumo registado (kW)'].mean():.4f} kW")
if 'Custo_EUR' in df_filtrado.columns:
    custo_total_filtrado = df_filtrado['Custo_EUR'].sum()
    st.sidebar.metric("Custo Estimado", f"€{custo_total_filtrado:.2f}")

# Tabs - reordered for UX (most actionable first)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Visão Geral",
    "💰 Tarifas",
    "⚡ Potência",
    "⚠️ Alertas",
    "📅 Análise Sazonal",
    "🔮 Previsão",
    "📋 Dados"
])

# Tab 1: Visão Geral
with tab1:
    st.header("Visão Geral do Consumo")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Consumo Total",
            f"{df_filtrado['Consumo registado (kW)'].sum():.2f} kW",
            delta=f"{df_filtrado['Consumo registado (kW)'].sum() / df['Consumo registado (kW)'].sum() * 100:.1f}% do total",
            delta_color="off"
        )

    with col2:
        st.metric("Consumo Médio", f"{df_filtrado['Consumo registado (kW)'].mean():.4f} kW")

    with col3:
        st.metric("Consumo Máximo", f"{df_filtrado['Consumo registado (kW)'].max():.2f} kW")

    with col4:
        st.metric("Consumo Mínimo", f"{df_filtrado['Consumo registado (kW)'].min():.4f} kW")

    if 'Consumo_kWh' in df_filtrado.columns:
        st.markdown("")
        col5, col6 = st.columns(2)
        with col5:
            st.metric("Energia Total", f"{df_filtrado['Consumo_kWh'].sum():.2f} kWh")
        with col6:
            if 'Custo_EUR' in df_filtrado.columns:
                st.metric("Custo Estimado", f"€{df_filtrado['Custo_EUR'].sum():.2f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Consumo ao Longo do Tempo")
        if 'DataHora' in df_filtrado.columns:
            visualizador = VisualizadorConsumo(df_filtrado)
            fig = visualizador.plotar_consumo_temporal()
            if fig:
                st.pyplot(fig)
                plt.close(fig)

    with col2:
        st.subheader("Consumo por Dia da Semana")
        if 'NomeDiaSemana' in df_filtrado.columns:
            visualizador = VisualizadorConsumo(df_filtrado)
            fig = visualizador.plotar_consumo_por_periodo('NomeDiaSemana')
            if fig:
                st.pyplot(fig)
                plt.close(fig)

    st.markdown("---")

    st.subheader("Distribuição de Consumo")
    visualizador = VisualizadorConsumo(df_filtrado)
    fig = visualizador.plotar_distribuicao_consumo()
    if fig:
        st.pyplot(fig)
        plt.close(fig)

# Tab 2: Tarifas
with tab2:
    st.header("Comparação de Tarifas")

    col1, col2, col3 = st.columns(3)

    with col1:
        preco_simples = st.number_input("Preço Simples (€/kWh)", value=0.25, min_value=0.0, format="%.4f", key="simples")

    with col2:
        preco_vazio = st.number_input("Preço Vazio (€/kWh)", value=0.104, min_value=0.0, format="%.4f", key="vazio")
        preco_cheio = st.number_input("Preço Cheio (€/kWh)", value=0.2584, min_value=0.0, format="%.4f", key="cheio")

    with col3:
        preco_ponta = st.number_input("Preço Ponta (€/kWh)", value=0.312, min_value=0.0, format="%.4f", key="ponta")

    tarifas = [
        TarifaSimples(preco_simples, "Simples"),
        TarifaBiHoraria(preco_vazio, preco_cheio, nome="Bi-horária"),
        TarifaTriHoraria(preco_vazio, preco_ponta, preco_cheio, nome="Tri-horária")
    ]

    df_comparacao = comparar_tarifas(df_filtrado, tarifas)

    st.subheader("Comparação de Custos")
    st.dataframe(df_comparacao)

    fig, ax = plt.subplots(figsize=(10, 6))
    df_comparacao.plot(kind='bar', x='tarifa', y='custo_total', ax=ax, color=['#3498db', '#2ecc71', '#f39c12'])
    ax.set_title('Comparação de Custos por Tarifa', fontweight='bold')
    ax.set_ylabel('Custo (€)')
    ax.set_xlabel('Tarifa')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")
    tarifa_recomendada, resumo_recomendacao = recomendar_tarifa(df_filtrado, tarifas)
    st.subheader("Recomendação")
    st.success(f"A tarifa mais económica é: **{tarifa_recomendada.nome}**")
    st.info(f"Custo: €{resumo_recomendacao['custo_total']:.2f}")

# Tab 3: Potência
with tab3:
    st.header("Análise de Potência Contratada")

    st.subheader("Configurar Potência Atual")

    potencias_disponiveis = sorted(AnalisadorPotencia.POTENCIAS.keys())

    col1, col2 = st.columns(2)

    with col1:
        potencia_atual = st.selectbox(
            "Potência Contratada Atual (kVA)",
            potencias_disponiveis,
            index=potencias_disponiveis.index(POTENCIA_ATUAL_PADRAO) if POTENCIA_ATUAL_PADRAO in potencias_disponiveis else 0,
            format_func=lambda x: f"{x} kVA - {AnalisadorPotencia.POTENCIAS[x]}",
            key="potencia_select"
        )

    with col2:
        margem_seguranca = st.selectbox(
            "Margem de Segurança para Recomendação",
            ["Conservadora (50%)", "Moderada (30%)", "Otimista (15%)"],
            index=1,
            key="margem_select"
        )
        tipo_tarifa = st.selectbox(
            "Tipo de Tarifa para Cálculo de Custo",
            ["Simples", "Bi-horária", "Tri-horária"],
            index=0,
            key="tipo_tarifa_select"
        )

    margem_map = {
        "Conservadora (50%)": AnalisadorPotencia.MARGEM_SEGURANCA_CONSERVADORA,
        "Moderada (30%)": AnalisadorPotencia.MARGEM_SEGURANCA_MODERADA,
        "Otimista (15%)": AnalisadorPotencia.MARGEM_SEGURANCA_OTIMISTA
    }

    tipo_tarifa_map = {
        "Simples": "simples",
        "Bi-horária": "bi_horaria",
        "Tri-horária": "tri_horaria"
    }
    tipo_tarifa_key = tipo_tarifa_map.get(tipo_tarifa, "simples")

    with st.spinner("A analisar potência..."):
        analisador_potencia = AnalisadorPotencia(df_filtrado)
        estatisticas = analisador_potencia.calcular_estatisticas_potencia()
        custo_consumo_anual = analisador_potencia.calcular_custo_consumo_anual(tipo_tarifa_key)
        analise = analisador_potencia.analisar_eficiencia_potencia(potencia_atual)
        potencia_recomendada, descricao, detalhes = analisador_potencia.recomendar_potencia(
            margem_seguranca=margem_map[margem_seguranca]
        )

    st.subheader("Estatísticas de Consumo")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Pico Máximo", f"{estatisticas['pico_maximo']:.4f} kW")
    with col2:
        st.metric("Pico Médio", f"{estatisticas['pico_medio']:.4f} kW")
    with col3:
        st.metric("Pico Percentil 95", f"{estatisticas['pico_percentil_95']:.4f} kW")
    with col4:
        st.metric("Pico Percentil 99", f"{estatisticas['pico_percentil_99']:.4f} kW")

    st.markdown(f"**Custo Anual de Consumo ({tipo_tarifa}):** €{custo_consumo_anual:.2f}")

    st.markdown("---")
    st.subheader("Análise da Potência Atual")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Utilização Média", f"{analise['utilizacao_media']:.2f}%")
    with col2:
        st.metric("Utilização do Pico", f"{analise['utilizacao_pico']:.2f}%")
    with col3:
        st.metric("Utilização P99", f"{analise['utilizacao_p99']:.2f}%")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Classificação:** {analise['classificacao']}")
    with col2:
        st.info(f"**Recomendação:** {analise['recomendacao']}")

    st.markdown("---")
    st.subheader("Recomendação de Potência")

    col1, col2 = st.columns(2)

    with col1:
        st.success(f"**Potência Recomendada:** {potencia_recomendada} kVA")
        st.info(f"**Descrição:** {descricao}")

    with col2:
        st.info(f"**Margem de Segurança:** {detalhes['margem_seguranca']*100:.0f}%")
        st.info(f"**Potência Necessária:** {detalhes['potencia_necessaria']:.4f} kW")

    if potencia_atual != potencia_recomendada:
        st.markdown("---")
        st.subheader("Economia Potencial")

        custo_atual = analisador_potencia.obter_custo_potencia(potencia_atual) * 12
        custo_recomendado = analisador_potencia.obter_custo_potencia(potencia_recomendada) * 12
        economia_anual = max(0, custo_atual - custo_recomendado)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Economia Anual", f"€{economia_anual:.2f}")
        with col2:
            st.metric("Economia Mensal", f"€{economia_anual/12:.2f}")
        with col3:
            st.metric("Economia Diária", f"€{economia_anual/365:.2f}")

        if economia_anual > 0:
            st.success(f"Ao mudar para {potencia_recomendada} kVA, pode poupar **€{economia_anual:.2f} por ano**!")
        else:
            st.warning(f"A potência atual ({potencia_atual} kVA) já é adequada para o seu consumo.")

    st.markdown("---")
    st.subheader("Comparação de Todas as Potências")

    df_comparacao_potencias = analisador_potencia.comparar_potencias(potencia_atual)
    st.dataframe(df_comparacao_potencias)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(df_comparacao_potencias))
    width = 0.35
    ax.bar(x, df_comparacao_potencias['Potência (kVA)'], width, label='Potência Contratada', alpha=0.7)
    ax.axhline(y=estatisticas['pico_maximo'], color='red', linestyle='--', label='Pico Máximo', linewidth=2)
    ax.axhline(y=estatisticas['pico_percentil_99'], color='orange', linestyle='--', label='Pico P99', linewidth=2)
    ax.set_xlabel('Potência Contratada')
    ax.set_ylabel('Potência (kW)')
    ax.set_title('Comparação de Potências vs Consumo Real', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(df_comparacao_potencias['Potência (kVA)'], rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 6))
    utilizacoes = []
    for potencia in df_comparacao_potencias['Potência (kVA)']:
        utilizacoes.append(estatisticas['pico_maximo'] / potencia * 100)

    colors = ['green' if u < 70 else 'orange' if u < 90 else 'red' for u in utilizacoes]
    ax.bar(df_comparacao_potencias['Potência (kVA)'].astype(str), utilizacoes, color=colors)
    ax.axhline(y=100, color='red', linestyle='--', label='Limite (100%)')
    ax.axhline(y=85, color='orange', linestyle='--', label='Próximo do limite (85%)')
    ax.axhline(y=70, color='green', linestyle='--', label='Adequado (70%)')
    ax.set_xlabel('Potência Contratada (kVA)')
    ax.set_ylabel('Utilização do Pico (%)')
    ax.set_title('Utilização da Potência por Opção', fontweight='bold')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Tab 4: Alertas
with tab4:
    st.header("Alertas de Consumo")

    OPCOES_SENSIBILIDADE = {"Calma": 0.5, "Normal": 1.0, "Sensível": 2.0}
    SENSIBILIDADE_NOTAS = {
        "Calma": "Apenas alertas para desvios muito grandes (>50% acima da média). Ideal se não quer muitos alertas.",
        "Normal": "Alertas para desvios moderados (~50% acima da média). Bom equilíbrio.",
        "Sensível": "Alertas mesmo para desvios pequenos (~25% acima da média). Útil se quer detetar tudo.",
    }
    sensibilidade = st.selectbox(
        "Sensibilidade",
        options=list(OPCOES_SENSIBILIDADE.keys()),
        index=1,
        key="sensibilidade",
    )
    st.caption(SENSIBILIDADE_NOTAS[sensibilidade])
    nivel_sens = OPCOES_SENSIBILIDADE[sensibilidade]

    with st.spinner("A analisar padrões..."):
        gestor = GestorAlertas(df_filtrado)
        resumo = gestor.analisar_resumo(sensibilidade=nivel_sens)

    geral = resumo.get('resumo_geral', {})
    n_alertas = geral.get('total_alertas', 0)
    n_categorias = geral.get('n_categorias', 0)

    if n_alertas == 0:
        st.success("Nenhum alerta encontrado — o consumo parece estar dentro dos padrões normais.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            cor = "🟡" if n_alertas <= 10 else "🔴"
            st.metric("Alertas", f"{cor} {n_alertas} em {n_categorias} categorias")
        with col2:
            st.metric("Registos Analisados", f"{geral['registos_analisados']:,}")

        ICONES = {
            'consumo_diario': '📅',
            'anomalias': '🔍',
            'tendencia': '📈',
            'custo': '💰',
        }
        NOMES = {
            'consumo_diario': 'Dias com Consumo Elevado',
            'anomalias': 'Anomalias (pontos fora do normal)',
            'tendencia': 'Tendência de Aumento',
            'custo': 'Custos Elevados',
        }

        for cat in ['consumo_diario', 'anomalias', 'tendencia', 'custo']:
            dados = resumo.get(cat)
            if not dados:
                continue

            icone = ICONES[cat]
            nome = NOMES[cat]
            niv = dados['nivel']
            cor_borda = "🔴" if niv == 'critical' else "🟡"
            container = st.container(border=True)

            header_cols = container.columns([1, 6, 1])
            with header_cols[0]:
                st.write(f"## {icone}")
            with header_cols[1]:
                st.markdown(f"**{nome}**")
            with header_cols[2]:
                st.write(f"**{cor_borda} {dados['total']}**")

            detail_cols = container.columns(4)

            if cat == 'consumo_diario':
                with detail_cols[0]:
                    st.metric("Dias afetados", dados['dias_afetados'])
                with detail_cols[1]:
                    st.metric("Pior dia", f"{dados['pior_dia']:.1f} kW")
                with detail_cols[2]:
                    st.metric("Média diária", f"{dados['media_diaria']:.1f} kW")
                with detail_cols[3]:
                    st.metric("Nível", niv.upper())

            elif cat == 'anomalias':
                with detail_cols[0]:
                    st.metric("Registos anómalos", dados['total'])
                with detail_cols[1]:
                    st.metric("Z-score máx", f"{dados['pico_z']:.1f}")
                with detail_cols[2]:
                    st.metric("Limite Z", f"{dados['z_threshold']:.1f}")
                with detail_cols[3]:
                    st.metric("Nível", niv.upper())

            elif cat == 'tendencia':
                m = dados['maior_de']
                p = dados['maior_para']
                with detail_cols[0]:
                    st.metric("Meses com aumento", dados['total'])
                with detail_cols[1]:
                    st.metric("Maior aumento", f"+{dados['maior_aumento']:.0f}%")
                with detail_cols[2]:
                    st.metric("De", f"{m[1]}/{m[0]}")
                with detail_cols[3]:
                    st.metric("Para", f"{p[1]}/{p[0]}")

            elif cat == 'custo':
                with detail_cols[0]:
                    st.metric("Meses acima da média", dados['total'])
                with detail_cols[1]:
                    st.metric("Custo médio/mês", f"€{dados['custo_medio_mensal']:.2f}")
                with detail_cols[2]:
                    st.metric("Pior mês", f"€{dados['pior_mes']:.2f}")
                with detail_cols[3]:
                    st.metric("Dias analisados", dados['dias_analisados'])

            container.info(f"**O que fazer:** {dados['dica']}")

# Tab 5: Análise Sazonal
with tab5:
    st.header("Análise Sazonal")

    analisador_sazonal = AnalisadorSazonal(df_filtrado)

    st.subheader("Consumo por Estação")
    comparacao_estacoes = analisador_sazonal.comparar_estacoes()
    st.dataframe(comparacao_estacoes)

    fig, ax = plt.subplots(figsize=(10, 6))
    CORES_ESTACOES = {'Primavera': '#2ecc71', 'Verão': '#f39c12', 'Outono': '#e74c3c', 'Inverno': '#3498db'}
    cores = [CORES_ESTACOES.get(est, '#95a5a6') for est in comparacao_estacoes.index]
    comparacao_estacoes['Total (kW)'].plot(kind='bar', color=cores, ax=ax)
    ax.set_title('Consumo Total por Estação', fontweight='bold')
    ax.set_ylabel('Consumo (kW)')
    ax.set_xlabel('Estação')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")

    st.subheader("Padrão Semanal")
    padrao_semanal = analisador_sazonal.analisar_padrao_semanal()
    st.dataframe(padrao_semanal)

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

    st.subheader("Heatmap de Consumo")
    visualizador = VisualizadorConsumo(df_filtrado)
    fig = visualizador.plotar_heatmap_hora_dia()
    if fig:
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("---")
    st.subheader("Índice Sazonal")
    indice_sazonal = analisador_sazonal.calcular_indice_sazonal()
    st.dataframe(indice_sazonal)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#27ae60' if x < 100 else '#f39c12' if x < 120 else '#e74c3c' for x in indice_sazonal['Índice Sazonal']]
    ax.bar(range(len(indice_sazonal)), indice_sazonal['Índice Sazonal'], color=colors)
    ax.set_xticks(range(len(indice_sazonal)))
    ax.set_xticklabels([m[:3] for m in indice_sazonal['Mês']], rotation=45, fontsize=10)
    ax.axhline(y=100, color='blue', linestyle='--', label='Média')
    ax.set_title('Índice Sazonal por Mês', fontweight='bold')
    ax.set_ylabel('Índice')
    ax.set_xlabel('Mês')
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Tab 6: Previsão
with tab6:
    st.header("Previsão de Consumo")

    col1, col2 = st.columns(2)

    with col1:
        dias_previsao = st.slider("Dias para Previsão", min_value=1, max_value=30, value=7)

    with col2:
        metodo_previsao = st.selectbox(
            "Método de Previsão",
            ["Ensemble", "Média Móvel", "Padrão Semanal", "Padrão Diário", "Tendência"],
            key="metodo_previsao"
        )

    previsor = PrevisorConsumo(df_filtrado)

    metodos = {
        "Ensemble": previsor.prever_ensemble,
        "Média Móvel": previsor.prever_media_movel,
        "Padrão Semanal": previsor.prever_por_padrao_semanal,
        "Padrão Diário": previsor.prever_por_padrao_diario,
        "Tendência": previsor.prever_por_tendencia,
    }

    with st.spinner("A gerar previsão..."):
        df_previsao = metodos[metodo_previsao](dias_futuros=dias_previsao)
        df_previsao = previsor.calcular_intervalo_confianca(df_previsao)

    st.subheader(f"Previsão para os próximos {dias_previsao} dias")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Previsto", f"{df_previsao['Consumo_Previsto (kW)'].sum():.2f} kW")
    with col2:
        st.metric("Mínimo Previsto", f"{df_previsao['Consumo_Previsto (kW)'].min():.4f} kW")
    with col3:
        st.metric("Máximo Previsto", f"{df_previsao['Consumo_Previsto (kW)'].max():.2f} kW")

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(
        df_filtrado['DataHora'],
        df_filtrado['Consumo registado (kW)'],
        label='Histórico',
        alpha=0.5,
        linewidth=0.5
    )

    ax.plot(
        df_previsao['DataHora'],
        df_previsao['Consumo_Previsto (kW)'],
        label='Previsão',
        color='red',
        linewidth=2
    )

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

    st.markdown("---")
    st.subheader("Detalhes da Previsão")
    df_previsao_display = df_previsao.copy()
    df_previsao_display['Data'] = df_previsao_display['DataHora'].dt.strftime('%Y-%m-%d %H:%M').astype(str)
    st.dataframe(df_previsao_display[['Data', 'Consumo_Previsto (kW)', 'Limite_Inferior (kW)', 'Limite_Superior (kW)']])

# Tab 7: Dados
with tab7:
    st.header("Dados de Consumo")

    st.subheader("Dados Filtrados")
    st.dataframe(df_filtrado)

    st.markdown("---")
    st.subheader("Estatísticas Descritivas")
    st.dataframe(df_filtrado.describe())

    st.markdown("---")
    st.subheader("Exportar Dados")

    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f'dados_consumo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

# Footer
st.markdown("---")
st.markdown("💡 **Dica:** Use os filtros na barra lateral para analisar períodos específicos.")
st.markdown("⚡ **Near Electric** - Desenvolvido por NearDaniel")
st.markdown("📧 GitHub: [neardaniel-pls](https://github.com/neardaniel-pls)")
