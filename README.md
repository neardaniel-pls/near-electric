# ⚡ Near Electric ⚡

Sistema completo para análise de dados de consumo de eletricidade com suporte a múltiplos meses, diferentes tarifas e visualizações avançadas.

Desenvolvido por **NearDaniel**

## 📁 Estrutura do Projeto

```
analise-eletricidade/
├── src/                           # Código fonte
│   ├── __init__.py
│   ├── utils.py                    # Funções utilitárias e logging
│   ├── data_loader.py              # Carregamento de dados
│   ├── data_processor.py           # Processamento e validação
│   ├── analyzer.py                 # Análises estatísticas
│   ├── visualizer.py               # Visualizações
│   ├── tariff_calculator.py        # Cálculo de tarifas
│   ├── seasonal_analyzer.py        # Análise sazonal (NOVO!)
│   ├── forecaster.py              # Previsão de consumo (NOVO!)
│   ├── alerts.py                  # Sistema de alertas (NOVO!)
│   └── power_analyzer.py          # Análise de potência (NOVO!)
├── tests/                         # Testes unitários
│   ├── __init__.py
│   ├── test_data_loader.py
│   └── test_tariff_calculator.py
├── scripts/                       # Scripts utilitários
│   ├── run_analysis.py            # Script principal de análise
│   ├── validate_data.py           # Validação de dados
│   └── generate_report.py        # Geração de relatórios
├── config/                        # Configurações
│   ├── config.yaml                 # Configuração principal
│   └── tariffs.yaml                # Definições de tarifas
├── data/                          # Dados brutos (CSV)
│   └── consumo_*.csv
├── processed/                     # Dados processados
│   └── *.csv
├── reports/                       # Relatórios gerados
│   ├── mensal/
│   └── anual/
├── cache/                         # Cache de cálculos
├── logs/                          # Logs de execução
├── dashboard.py                    # Dashboard interativo (NOVO!)
├── analise_consumo_eletricidade.ipynb  # Notebook Jupyter
├── requirements.txt                # Dependências Python
├── VALIDACAO_NOTEBOOK.md          # Documento de validação
└── README.md                      # Este ficheiro
```

## 🚀 Configuração Rápida

### 1. Criar e Ativar o Ambiente Virtual

**No Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**No Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar as Dependências

```bash
pip install -r requirements.txt
```

### 3. Executar a Análise

**Opção 1: Usar o script principal:**
```bash
python scripts/run_analysis.py
```

**Opção 2: Usar o notebook Jupyter:**
```bash
jupyter notebook
```
Depois abra [`analise_consumo_eletricidade.ipynb`](analise_consumo_eletricidade.ipynb).

**Opção 3: Usar o dashboard interativo (NOVO!):**
```bash
streamlit run dashboard.py
```
O dashboard estará disponível em http://localhost:8501

## 📊 Funcionalidades

### 1. Carregamento Automático de Dados
- Detecção automática de todos os ficheiros CSV na pasta `data/`
- Validação de estrutura dos dados
- Combinação de múltiplos meses
- Processamento unificado de todos os ficheiros

### 2. Validação de Qualidade de Dados
- Detecção de valores negativos
- Identificação de valores nulos
- Verificação de continuidade temporal
- Detecção de outliers usando Z-score

### 3. Análise Estatística
- Estatísticas descritivas (média, mediana, desvio padrão)
- Análise por período (dia, semana, mês, ano)
- Identificação de picos de consumo
- Análise de padrões temporais
- Comparação entre períodos
- Análise de eficiência com benchmarks

### 4. Análise Sazonal (NOVO!)
- Comparação de meses entre anos
- Análise por estação (Inverno, Primavera, Verão, Outono)
- Padrões de consumo por dia da semana
- Padrões horários
- Comparação dias úteis vs fim de semana
- Índices sazonais
- Detecção de mudanças sazonais

### 5. Previsão de Consumo (NOVO!)
- Previsão por média móvel
- Previsão por padrão semanal
- Previsão por padrão diário
- Previsão por tendência linear
- Previsão ensemble (combinação de métodos)
- Intervalos de confiança
- Comparação de métodos de previsão

### 6. Sistema de Alertas (NOVO!)
- Alertas de consumo diário alto
- Alertas de consumo horário alto
- Alertas de aumento mensal
- Detecção de anomalias
- Alertas de custo alto
- Configuração personalizada de limites
- Filtragem por nível de severidade

### 7. Análise de Potência Contratada (NOVO!)
- Recomendação de potência contratada baseada no consumo real
- Análise de eficiência da potência atual
- Comparação entre todas as potências disponíveis (1.15 a 20.70 kVA)
- Cálculo de economia potencial anual
- Margens de segurança configuráveis (conservadora, moderada, otimista)
- Estatísticas de pico (máximo, médio, percentil 95, percentil 99)
- Classificação da potência atual (sobredimensionada, adequada, subdimensionada)
- Relatório detalhado de análise de potência

### 8. Cálculo de Tarifas
- **Tarifa Simples:** Preço único por kWh
- **Tarifa Bi-horária:** Preços diferentes para horário de vazio e cheio
- **Tarifa Tri-horária:** Preços para vazio, ponta e cheio
- Comparação automática entre tarifas
- Recomendação da tarifa mais económica

### 9. Visualizações
- Consumo ao longo do tempo
- Consumo por período (mês, dia da semana, hora)
- Boxplots de distribuição
- Comparação entre períodos
- Tendência de consumo
- Custo por período
- Múltiplos gráficos em uma figura
- **Heatmaps** (NOVO!): Consumo por hora e dia da semana
- **Heatmaps** (NOVO!): Consumo por hora e mês
- **Distribuição** (NOVO!): Histograma e KDE
- **Comparação anual** (NOVO!): Year-over-year
- **KPIs** (NOVO!): Painel de indicadores chave

### 10. Dashboard Interativo (NOVO!)
- Interface web com Streamlit
- Filtros de data e estado
- Visualização em tempo real
- Análise sazonal interativa
- Previsão com diferentes métodos
- Configuração de alertas
- Comparação de tarifas
- Análise de potência contratada (NOVO!)
- Exportação de dados (CSV/Excel)

### 11. Exportação de Dados
- Dados processados em CSV
- Resumos por período
- Comparação de tarifas
- Gráficos em alta resolução
- Exportação em Excel (NOVO!)

## 📝 Como Adicionar Novos Meses

Basta colocar novos ficheiros CSV na pasta `data/` com o formato adequado:

```csv
Data,Hora,Consumo registado (kW),Estado
2026/02/01,00:15,0.5,Real
2026/02/01,00:30,0.6,Real
...
```

O sistema detectará automaticamente todos os ficheiros e carregará os dados.

## ⚙️ Configuração

### Configuração Principal (`config/config.yaml`)

```yaml
caminhos:
  dados: "data"
  processados: "processed"
  relatorios: "reports"

logging:
  nivel: "INFO"
  ficheiro: "logs/analise.log"

processamento:
  estrategia_limpeza: "remover"  # remover, media, zero
  filtrar_estado: "Real"

analise:
  top_picos: 20
  area_habitacao: null  # Em m²

tarifas:
  padrao: "bi_horaria"
```

### Definição de Tarifas (`config/tariffs.yaml`)

O ficheiro [`config/tariffs.yaml`](config/tariffs.yaml) contém as definições detalhadas das tarifas portuguesas:
- Preços por período
- Horários de vazio, ponta e cheio
- Benchmarks de consumo
- Impostos e taxas

## 🎯 Uso Avançado

### Executar com Parâmetros Personalizados

```bash
python scripts/run_analysis.py \
  --config config/config.yaml \
  --data-dir data \
  --output-dir processed \
  --log-level DEBUG \
  --save-plots
```

### Usar como Módulo Python

```python
from src.data_loader import carregar_dados
from src.analyzer import AnalisadorConsumo
from src.visualizer import VisualizadorConsumo

# Carregar dados
df, carregador = carregar_dados()

# Analisar
analisador = AnalisadorConsumo(df)
estatisticas = analisador.calcular_estatisticas_gerais()

# Visualizar
visualizador = VisualizadorConsumo(df)
fig = visualizador.plotar_consumo_temporal()
plt.show()
```

### Comparar Tarifas

```python
from src.tariff_calculator import (
    TarifaSimples, TarifaBiHoraria, TarifaTriHoraria,
    comparar_tarifas, recomendar_tarifa
)

tarifas = [
    TarifaSimples(0.25),
    TarifaBiHoraria(0.104, 0.2584),
    TarifaTriHoraria(0.104, 0.312, 0.2584)
]

df_comparacao = comparar_tarifas(df, tarifas)
tarifa_recomendada, resumo = recomendar_tarifa(df, tarifas)
```

### Análise Sazonal (NOVO!)

```python
from src.seasonal_analyzer import AnalisadorSazonal

# Criar analisador
analisador = AnalisadorSazonal(df)

# Comparar meses entre anos
comparacao_janeiro = analisador.comparar_meses_entre_anos(mes=1)

# Comparar estações
comparacao_estacoes = analisador.comparar_estacoes()

# Calcular índice sazonal
indice = analisador.calcular_indice_sazonal()

# Gerar resumo completo
resumo = analisador.gerar_resumo_sazonal()
```

### Previsão de Consumo (NOVO!)

```python
from src.forecaster import PrevisorConsumo

# Criar previsor
previsor = PrevisorConsumo(df)

# Prever usando ensemble
df_previsao = previsor.prever_ensemble(dias_futuros=7)

# Calcular intervalo de confiança
df_previsao = previsor.calcular_intervalo_confianca(df_previsao)

# Comparar métodos de previsão
metricas = previsor.comparar_previsoes(dias_teste=7)

# Gerar resumo
resumo_previsao = previsor.gerar_resumo_previsao(dias_futuros=7)
```

### Sistema de Alertas (NOVO!)

```python
from src.alerts import GestorAlertas, TipoAlerta, NivelAlerta

# Criar gestor de alertas
gestor = GestorAlertas(df)

# Configurar regras
gestor.adicionar_regra_consumo_diario(limite_kw=50.0, nivel=NivelAlerta.WARNING)
gestor.adicionar_regra_consumo_horario(limite_kw=2.0, nivel=NivelAlerta.CRITICAL)
gestor.adicionar_regra_aumento_mensal(percentual=50)
gestor.adicionar_regra_anomalia(z_score=3.0)

# Verificar alertas
alertas = gestor.verificar_todas_regras()

# Filtrar alertas
alertas_criticos = gestor.filtrar_por_nivel(NivelAlerta.CRITICAL)

# Obter resumo
resumo = gestor.obter_resumo()

# Exportar alertas
df_alertas = gestor.exportar_alertas(formato='dataframe')
```

### Visualizações Avançadas (NOVO!)

```python
from src.visualizer import VisualizadorConsumo

visualizador = VisualizadorConsumo(df)

# Heatmap por hora e dia da semana
fig = visualizador.plotar_heatmap_hora_dia(salvar=True, caminho='heatmap_hora_dia.png')

# Heatmap por hora e mês
fig = visualizador.plotar_heatmap_hora_mes(salvar=True, caminho='heatmap_hora_mes.png')

# Distribuição de consumo
fig = visualizador.plotar_distribuicao_consumo(bins=50)

# Comparação anual (year-over-year)
fig = visualizador.plotar_comparacao_anual()

# Painel de KPIs
fig = visualizador.plotar_kpis()
```

### Análise de Potência Contratada (NOVO!)

```python
from src.power_analyzer import AnalisadorPotencia

# Criar analisador
analisador = AnalisadorPotencia(df)

# Calcular estatísticas de potência
estatisticas = analisador.calcular_estatisticas_potencia()

# Recomendar potência
potencia_recomendada, descricao, detalhes = analisador.recomendar_potencia(
    margem_seguranca=0.30  # 30% de margem
)

# Analisar eficiência da potência atual
analise = analisador.analisar_eficiencia_potencia(potencia_atual=10.35)

# Comparar todas as potências
df_comparacao = analisador.comparar_potencias(potencia_atual=10.35)

# Gerar relatório detalhado
relatorio = analisador.gerar_relatorio_potencia(potencia_atual=10.35)
print(relatorio)
```

## 🧪 Testes

Executar os testes unitários:

```bash
pytest tests/ -v
```

Executar com cobertura:

```bash
pytest tests/ --cov=src --cov-report=html
```

## 📚 Documentação

- [`VALIDACAO_NOTEBOOK.md`](VALIDACAO_NOTEBOOK.md) - Documento detalhado de validação e roadmap
- [`config/config.yaml`](config/config.yaml) - Configuração principal
- [`config/tariffs.yaml`](config/tariffs.yaml) - Definições de tarifas

## 🛠️ Dependências

- **pandas** (>=2.0.0) - Manipulação de dados
- **numpy** (>=1.24.0) - Operações numéricas
- **matplotlib** (>=3.7.0) - Visualização de dados
- **seaborn** (>=0.12.0) - Visualização avançada
- **scipy** (>=1.10.0) - Análise estatística
- **pyyaml** (>=6.0) - Carregamento de configuração
- **jupyter** (>=1.0.0) - Ambiente de notebook
- **streamlit** (>=1.28.0) - Dashboard interativo (NOVO!)
- **openpyxl** (>=3.1.0) - Exportação Excel (NOVO!)

## 💡 Perguntas Frequentes

### Como alterar a tarifa usada?

Edite o ficheiro [`config/config.yaml`](config/config.yaml) e altere a seção `tarifas`:

```yaml
tarifas:
  padrao: "tri_horaria"  # simples, bi_horaria, tri_horaria
```

### Como filtrar apenas dados reais?

A configuração padrão já filtra dados reais. Para alterar:

```yaml
processamento:
  filtrar_estado: "Real"  # "Real", "Estimado", ou null para ambos
```

### Como ajustar o nível de logging?

```yaml
logging:
  nivel: "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 📈 Roadmap

Veja o documento [`VALIDACAO_NOTEBOOK.md`](VALIDACAO_NOTEBOOK.md) para:
- Análise detalhada do que existe
- O que pode ser adicionado
- O que pode ser melhorado
- Prioridades de implementação
- Recomendações de arquitetura

## 📄 Licença

Este projeto é para uso pessoal e educacional.

## 👤 Autor

**NearDaniel** - Desenvolvido para análise pessoal de consumo de eletricidade.

---

**Nota:** Este sistema foi criado para analisar ficheiros CSV de consumo de eletricidade. Basta colocar novos ficheiros CSV na pasta `data/` e o sistema detectará automaticamente todos os meses disponíveis para análise.

**⚡ Near Electric** - Sistema de análise de consumo de eletricidade desenvolvido por NearDaniel
