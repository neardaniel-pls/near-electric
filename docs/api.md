# Documentação da API

Documentação das principais funções e classes dos módulos do projeto.

## Índice

- [Módulo `utils`](#módulo-utils)
- [Módulo `data_loader`](#módulo-data_loader)
- [Módulo `data_processor`](#módulo-data_processor)
- [Módulo `analyzer`](#módulo-analyzer)
- [Módulo `visualizer`](#módulo-visualizer)
- [Módulo `tariff_calculator`](#módulo-tariff_calculator)

---

## Módulo `utils`

Funções utilitárias compartilhadas.

### `setup_logging(log_file='analise.log', log_level='INFO', log_format=None)`

Configura logging profissional para o projeto.

**Parâmetros:**
- `log_file` (str): Caminho para o ficheiro de log.
- `log_level` (str): Nível de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
- `log_format` (str, opcional): Formato personalizado das mensagens.

**Retorna:**
- `logging.Logger`: Logger configurado.

**Exemplo:**
```python
from src.utils import setup_logging

logger = setup_logging(log_level="DEBUG")
logger.info("Mensagem informativa")
```

### `carregar_config(caminho='config/config.yaml')`

Carrega configuração de um ficheiro YAML.

**Parâmetros:**
- `caminho` (str): Caminho para o ficheiro de configuração.

**Retorna:**
- `dict`: Dicionário com a configuração.

**Exemplo:**
```python
from src.utils import carregar_config

config = carregar_config()
tarifa = config['tarifa']['normal']
```

### `validar_diretorio(caminho, criar=True)`

Valida e opcionalmente cria um diretório.

**Parâmetros:**
- `caminho` (str): Caminho do diretório.
- `criar` (bool): Se True, cria o diretório se não existir.

**Retorna:**
- `Path`: Path do diretório validado.

**Exemplo:**
```python
from src.utils import validar_diretorio

data_dir = validar_diretorio("data")
print(data_dir)  # PosixPath('data')
```

---

## Módulo `data_loader`

Módulo para carregamento de dados de consumo.

### Classe `CarregadorDados`

Classe para carregar e gerenciar dados de consumo.

#### `__init__(data_dir='data')`

Inicializa o carregador de dados.

**Parâmetros:**
- `data_dir` (str): Diretório onde estão os ficheiros CSV.

**Exemplo:**
```python
from src.data_loader import CarregadorDados

carregador = CarregadorDados('data')
```

#### `listar_csvs()`

Lista todos os ficheiros CSV no diretório de dados.

**Retorna:**
- `List[str]`: Lista ordenada de caminhos para ficheiros CSV.

**Exemplo:**
```python
csv_files = carregador.listar_csvs()
print(f"Encontrados {len(csv_files)} ficheiros")
```

#### `carregar_csv(caminho)`

Carrega um ficheiro CSV e retorna DataFrame processado.

**Parâmetros:**
- `caminho` (str): Caminho para o ficheiro CSV.

**Retorna:**
- `Tuple[pd.DataFrame, str]`: Tupla com (DataFrame processado, nome do ficheiro).

**Exemplo:**
```python
df, nome = carregador.carregar_csv('data/consumo_janeiro_2026.csv')
print(f"Carregado: {nome} com {len(df)} registros")
```

#### `carregar_todos()`

Carrega todos os ficheiros CSV e combina em um DataFrame.

**Retorna:**
- `pd.DataFrame`: DataFrame combinado com todos os dados.

**Exemplo:**
```python
df = carregador.carregar_todos()
print(f"Total de registros: {len(df)}")
```

#### `filtrar_estado(df, estado='Real')`

Filtra DataFrame por estado (Real ou Estimado).

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame a filtrar.
- `estado` (str): Estado a filtrar ('Real' ou 'Estimado').

**Retorna:**
- `pd.DataFrame`: DataFrame filtrado.

**Exemplo:**
```python
df_real = carregador.filtrar_estado(df, estado='Real')
```

### Função `carregar_dados(data_dir='data')`

Função conveniente para carregar todos os dados.

**Parâmetros:**
- `data_dir` (str): Diretório onde estão os ficheiros CSV.

**Retorna:**
- `Tuple[pd.DataFrame, CarregadorDados]`: Tupla com (DataFrame combinado, instância do CarregadorDados).

**Exemplo:**
```python
from src.data_loader import carregar_dados

df, carregador = carregar_dados()
print(f"Carregados {len(df)} registros")
```

---

## Módulo `data_processor`

Módulo para processamento e validação de dados.

### Classe `ValidadorDados`

Classe para validar qualidade dos dados.

#### `__init__(df)`

Inicializa o validador.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame a validar.

#### `validar()`

Executa todas as validações e retorna relatório.

**Retorna:**
- `dict`: Dicionário com relatório de validação.

**Exemplo:**
```python
from src.data_processor import ValidadorDados

validador = ValidadorDados(df)
relatorio = validador.validar()
print(f"Problemas: {len(relatorio['valores_anomalos'])}")
```

### Classe `ProcessadorDados`

Classe para processamento de dados.

#### `__init__(df)`

Inicializa o processador.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame a processar.

#### `limpar_dados(estrategia='remover')`

Limpa os dados removendo ou preenchendo valores inválidos.

**Parâmetros:**
- `estrategia` (str): Estratégia de limpeza ('remover', 'media', 'zero').

**Retorna:**
- `pd.DataFrame`: DataFrame limpo.

**Exemplo:**
```python
processador = ProcessadorDados(df)
df_limpo = processador.limpar_dados(estrategia='media')
```

#### `adicionar_colunas_calculadas(tarifa=0.25)`

Adiciona colunas calculadas (kWh, custo).

**Parâmetros:**
- `tarifa` (float): Tarifa em €/kWh.

**Retorna:**
- `pd.DataFrame`: DataFrame com colunas adicionais.

**Exemplo:**
```python
df = processador.adicionar_colunas_calculadas(tarifa=0.25)
print(f"Custo total: €{df['Custo_EUR'].sum():.2f}")
```

#### `agregar_por_periodo(periodo='mes', colunas=None)`

Agrega dados por período (dia, semana, mês, ano).

**Parâmetros:**
- `periodo` (str): Período de agregação ('dia', 'semana', 'mes', 'ano').
- `colunas` (List[str], opcional): Colunas a agregar.

**Retorna:**
- `pd.DataFrame`: DataFrame agregado.

**Exemplo:**
```python
df_mensal = processador.agregar_por_periodo(periodo='mes')
print(df_mensal.head())
```

### Função `validar_dados(df)`

Função conveniente para validar dados.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame a validar.

**Retorna:**
- `dict`: Dicionário com relatório de validação.

**Exemplo:**
```python
from src.data_processor import validar_dados

relatorio = validar_dados(df)
print(f"Problemas: {relatorio['total_problemas']}")
```

### Função `limpar_dados(df, estrategia='remover')`

Função conveniente para limpar dados.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame a limpar.
- `estrategia` (str): Estratégia de limpeza.

**Retorna:**
- `pd.DataFrame`: DataFrame limpo.

**Exemplo:**
```python
from src.data_processor import limpar_dados

df_limpo = limpar_dados(df, estrategia='media')
```

---

## Módulo `analyzer`

Módulo para análises estatísticas de consumo.

### Classe `AnalisadorConsumo`

Classe para análise de consumo de eletricidade.

#### `__init__(df)`

Inicializa o analisador.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame com dados de consumo.

#### `calcular_estatisticas_gerais()`

Calcula estatísticas descritivas gerais.

**Retorna:**
- `dict`: Dicionário com estatísticas.

**Exemplo:**
```python
from src.analyzer import AnalisadorConsumo

analisador = AnalisadorConsumo(df)
estatisticas = analisador.calcular_estatisticas_gerais()
print(f"Total: {estatisticas['total']:.2f} kW")
```

#### `analisar_por_periodo(coluna_periodo='NomeMes')`

Analisa consumo por período (mês, dia da semana, hora).

**Parâmetros:**
- `coluna_periodo` (str): Coluna para agrupamento.

**Retorna:**
- `pd.DataFrame`: DataFrame com análise por período.

**Exemplo:**
```python
consumo_por_mes = analisador.analisar_por_periodo('NomeMes')
print(consumo_por_mes.head())
```

#### `identificar_picos(top_n=20)`

Identifica os momentos de maior consumo.

**Parâmetros:**
- `top_n` (int): Número de picos a identificar.

**Retorna:**
- `pd.DataFrame`: DataFrame com os top N picos.

**Exemplo:**
```python
picos = analisador.identificar_picos(top_n=10)
print(picos)
```

#### `analisar_eficiencia(area_m2=None)`

Analisa eficiência do consumo.

**Parâmetros:**
- `area_m2` (float, opcional): Área da habitação em m².

**Retorna:**
- `dict`: Dicionário com métricas de eficiência.

**Exemplo:**
```python
eficiencia = analisador.analisar_eficiencia(area_m2=100)
print(f"Classificação: {eficiencia['classificacao']}")
```

### Função `calcular_estatisticas(df)`

Função conveniente para calcular estatísticas.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame com dados de consumo.

**Retorna:**
- `dict`: Dicionário com estatísticas.

**Exemplo:**
```python
from src.analyzer import calcular_estatisticas

estatisticas = calcular_estatisticas(df)
print(f"Total: {estatisticas['total']:.2f} kW")
```

### Função `identificar_picos(df, top_n=20)`

Função conveniente para identificar picos.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame com dados de consumo.
- `top_n` (int): Número de picos a identificar.

**Retorna:**
- `pd.DataFrame`: DataFrame com os picos.

**Exemplo:**
```python
from src.analyzer import identificar_picos

picos = identificar_picos(df, top_n=10)
print(picos.head())
```

---

## Módulo `visualizer`

Módulo para visualização de dados de consumo.

### Classe `VisualizadorConsumo`

Classe para visualização de consumo de eletricidade.

#### `__init__(df, figsize=(12, 6))`

Inicializa o visualizador.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame com dados de consumo.
- `figsize` (tuple): Tamanho padrão das figuras (largura, altura).

#### `plotar_consumo_temporal(salvar=False, caminho=None)`

Plota consumo ao longo do tempo.

**Parâmetros:**
- `salvar` (bool): Se True, salva a figura.
- `caminho` (str, opcional): Caminho para salvar a figura.

**Retorna:**
- `plt.Figure`: Figure do matplotlib.

**Exemplo:**
```python
from src.visualizer import VisualizadorConsumo
import matplotlib.pyplot as plt

visualizador = VisualizadorConsumo(df)
fig = visualizador.plotar_consumo_temporal()
plt.show()
```

#### `plotar_consumo_por_periodo(coluna_periodo='NomeMes', tipo_grafico='bar', salvar=False, caminho=None)`

Plota consumo por período.

**Parâmetros:**
- `coluna_periodo` (str): Coluna para agrupamento.
- `tipo_grafico` (str): Tipo de gráfico ('bar', 'line').
- `salvar` (bool): Se True, salva a figura.
- `caminho` (str, opcional): Caminho para salvar a figura.

**Retorna:**
- `plt.Figure`: Figure do matplotlib.

**Exemplo:**
```python
fig = visualizador.plotar_consumo_por_periodo('NomeMes')
plt.show()
```

#### `criar_multiplos_graficos(salvar=False, caminho=None)`

Cria uma figura com múltiplos gráficos.

**Parâmetros:**
- `salvar` (bool): Se True, salva a figura.
- `caminho` (str, opcional): Caminho para salvar a figura.

**Retorna:**
- `plt.Figure`: Figure do matplotlib.

**Exemplo:**
```python
fig = visualizador.criar_multiplos_graficos()
plt.show()
```

### Função `plotar_consumo_temporal(df, salvar=False)`

Função conveniente para plotar consumo temporal.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame com dados de consumo.
- `salvar` (bool): Se True, salva a figura.

**Retorna:**
- `plt.Figure`: Figure do matplotlib.

**Exemplo:**
```python
from src.visualizer import plotar_consumo_temporal

fig = plotar_consumo_temporal(df)
plt.show()
```

---

## Módulo `tariff_calculator`

Módulo para cálculo de custos com diferentes tarifas.

### Classe `TarifaSimples`

Tarifa simples (único preço).

#### `__init__(preco_kwh, nome='Simples')`

Inicializa tarifa simples.

**Parâmetros:**
- `preco_kwh` (float): Preço por kWh em €.
- `nome` (str): Nome da tarifa.

**Exemplo:**
```python
from src.tariff_calculator import TarifaSimples

tarifa = TarifaSimples(0.25)
```

#### `calcular_custo(df)`

Calcula custo para cada registro.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame com colunas 'DataHora' e 'Consumo_kWh'.

**Retorna:**
- `pd.DataFrame`: DataFrame com coluna 'Custo_EUR' adicionada.

**Exemplo:**
```python
df_custo = tarifa.calcular_custo(df)
print(f"Custo total: €{df_custo['Custo_EUR'].sum():.2f}")
```

### Classe `TarifaBiHoraria`

Tarifa bi-horária (vazio e cheio).

#### `__init__(preco_vazio, preco_cheio, horas_vazio=None, nome='Bi-horária')`

Inicializa tarifa bi-horária.

**Parâmetros:**
- `preco_vazio` (float): Preço por kWh em horário de vazio.
- `preco_cheio` (float): Preço por kWh em horário de cheio.
- `horas_vazio` (List[Tuple[int, int]], opcional): Lista de tuplas (inicio, fim) para horário de vazio.
- `nome` (str): Nome da tarifa.

**Exemplo:**
```python
from src.tariff_calculator import TarifaBiHoraria

tarifa = TarifaBiHoraria(0.104, 0.2584)
```

### Classe `TarifaTriHoraria`

Tarifa tri-horária (vazio, ponta e cheio).

#### `__init__(preco_vazio, preco_ponta, preco_cheio, horas_vazio=None, horas_ponta=None, nome='Tri-horária')`

Inicializa tarifa tri-horária.

**Parâmetros:**
- `preco_vazio` (float): Preço por kWh em horário de vazio.
- `preco_ponta` (float): Preço por kWh em horário de ponta.
- `preco_cheio` (float): Preço por kWh em horário de cheio.
- `horas_vazio` (List[Tuple[int, int]], opcional): Lista de tuplas (inicio, fim) para horário de vazio.
- `horas_ponta` (List[Tuple[int, int]], opcional): Lista de tuplas (inicio, fim) para horário de ponta.
- `nome` (str): Nome da tarifa.

**Exemplo:**
```python
from src.tariff_calculator import TarifaTriHoraria

tarifa = TarifaTriHoraria(0.104, 0.312, 0.2584)
```

### Função `comparar_tarifas(df, tarifas)`

Compara custos entre diferentes tarifas.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame com colunas 'DataHora', 'HoraNum', 'Consumo_kWh'.
- `tarifas` (List[Tarifa]): Lista de objetos Tarifa.

**Retorna:**
- `pd.DataFrame`: DataFrame com comparação de custos.

**Exemplo:**
```python
from src.tariff_calculator import (
    TarifaSimples, TarifaBiHoraria, TarifaTriHoraria,
    comparar_tarifas
)

tarifas = [
    TarifaSimples(0.25),
    TarifaBiHoraria(0.104, 0.2584),
    TarifaTriHoraria(0.104, 0.312, 0.2584)
]
df_comparacao = comparar_tarifas(df, tarifas)
print(df_comparacao)
```

### Função `recomendar_tarifa(df, tarifas)`

Recomenda a tarifa mais económica.

**Parâmetros:**
- `df` (pd.DataFrame): DataFrame com colunas 'DataHora', 'HoraNum', 'Consumo_kWh'.
- `tarifas` (List[Tarifa]): Lista de objetos Tarifa.

**Retorna:**
- `Tuple[Tarifa, Dict]`: Tupla com (tarifa recomendada, resumo de custos).

**Exemplo:**
```python
from src.tariff_calculator import (
    TarifaSimples, TarifaBiHoraria, TarifaTriHoraria,
    recomendar_tarifa
)

tarifas = [
    TarifaSimples(0.25),
    TarifaBiHoraria(0.104, 0.2584)
]
tarifa, resumo = recomendar_tarifa(df, tarifas)
print(f"Recomendado: {tarifa.nome}")
```

---

## Exemplos de Uso

### Exemplo Completo de Análise

```python
from src.data_loader import carregar_dados
from src.data_processor import limpar_dados
from src.analyzer import AnalisadorConsumo
from src.visualizer import VisualizadorConsumo
from src.tariff_calculator import (
    TarifaSimples, TarifaBiHoraria,
    comparar_tarifas, recomendar_tarifa
)

# 1. Carregar dados
df, carregador = carregar_dados()
print(f"Carregados {len(df)} registros")

# 2. Filtrar dados reais
df_real = carregador.filtrar_estado(df, estado='Real')

# 3. Limpar dados
df_limpo = limpar_dados(df_real, estrategia='remover')

# 4. Analisar
analisador = AnalisadorConsumo(df_limpo)
estatisticas = analisador.calcular_estatisticas_gerais()
picos = analisador.identificar_picos(top_n=10)

# 5. Comparar tarifas
tarifas = [
    TarifaSimples(0.25),
    TarifaBiHoraria(0.104, 0.2584)
]
df_comparacao = comparar_tarifas(df_limpo, tarifas)
tarifa_recomendada, resumo = recomendar_tarifa(df_limpo, tarifas)

# 6. Visualizar
visualizador = VisualizadorConsumo(df_limpo)
fig = visualizador.criar_multiplos_graficos()
plt.show()

# 7. Mostrar resultados
print(f"\nTarifa recomendada: {tarifa_recomendada.nome}")
print(f"Custo: €{resumo['custo_total']:.2f}")
```

---

Para mais informações, consulte o [`README.md`](../README.md) e o documento [`VALIDACAO_NOTEBOOK.md`](../VALIDACAO_NOTEBOOK.md).
