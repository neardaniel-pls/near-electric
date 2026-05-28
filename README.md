# Near Electric

Um sistema para analisar o consumo de eletricidade no mercado português. Ajuda a entender como gastas energia, prever custos e escolher a melhor tarifa.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)

Desenvolvido por **NearDaniel**

---

## 🚀 Começar Rápido

### Passo 1: Criar ambiente virtual

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

### Passo 2: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 3: Executar

**Opção 1 - Dashboard (recomendado):**
```bash
streamlit run dashboard.py
```
Abre em http://localhost:8501

**Opção 2 - Análise completa:**
```bash
python scripts/run_analysis.py
```

**Opção 3 - Notebook Jupyter:**
```bash
jupyter notebook
```
Depois abra `analise_consumo_eletricidade.ipynb`

---

## 📁 Estrutura do Projeto

```
near-electric/
├── src/           # Código principal do sistema
├── config/        # Configurações (tarifas, etc.)
├── data/          # Coloca aqui os ficheiros CSV
├── processed/     # Dados processados
├── scripts/       # Scripts para executar análises
├── tests/         # Testes
├── dashboard.py   # Dashboard interativo
└── requirements.txt
```

---

## 📊 O que faz o sistema

### 📥 Carregar dados
- Lê automaticamente todos os ficheiros CSV da pasta `data/`
- Valida os dados e detecta problemas
- Combina múltiplos meses numa análise única

### 📈 Análise de consumo
- Calcula estatísticas (média, máximo, mínimo)
- Mostra padrões de consumo por hora, dia e mês
- Identifica picos e anomalias
- Compara períodos diferentes (ex: este mês vs mês passado)

### 🔮 Previsão
- Preve o consumo para os próximos dias
- Usa vários métodos e mostra o mais preciso
- Mostra intervalos de confiança (mínimo e máximo esperado)

### ⚠️ Alertas
- Avisa quando o consumo é muito alto
- Detecta aumentos anormais
- Podes personalizar os limites de alerta

### 💰 Tarifas
- Calcula o custo com diferentes tarifas (simples, bi-horária, tri-horária)
- Compara tarifas automaticamente
- Recomenda a mais económica para o teu perfil

### 🔌 Potência contratada
- Analisa se a tua potência contratada é adequada
- Recomenda a potência ideal
- Calcula a poupança potencial

### 📊 Visualizações
- Gráficos de consumo ao longo do tempo
- Heatmaps (mapas de calor) por hora e dia
- Comparação entre meses e anos
- Painel de indicadores principais (KPIs)

---

## 📝 Como adicionar dados

Basta colocar ficheiros CSV na pasta `data/` com este formato:

```csv
Data,Hora,Consumo registado (kW),Estado
2026/02/01,00:15,0.5,Real
2026/02/01,00:30,0.6,Real
...
```

O sistema detecta automaticamente todos os ficheiros e combina os dados.

---

## ⚙️ Configuração

### Tarifa padrão

Edita [`config/config.yaml`](config/config.yaml) para mudar a tarifa:

```yaml
tarifas:
  padrao: "bi_horaria"  # opções: simples, bi_horaria, tri_horaria
```

### Filtrar dados

```yaml
processamento:
  filtrar_estado: "Real"  # "Real", "Estimado", ou null para ambos
```

### Nível de logs

```yaml
logging:
  nivel: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## 🎯 Exemplos de uso

### Usar como módulo Python

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
```

### Comparar tarifas

```python
from src.tariff_calculator import recomendar_tarifa, TarifaBiHoraria

tarifas = [TarifaBiHoraria(0.104, 0.2584)]
tarifa_recomendada, resumo = recomendar_tarifa(df, tarifas)
```

### Análise sazonal

```python
from src.seasonal_analyzer import AnalisadorSazonal

analisador = AnalisadorSazonal(df)
comparacao = analisador.comparar_meses_entre_anos(mes=1)
```

### Previsão de consumo

```python
from src.forecaster import PrevisorConsumo

previsor = PrevisorConsumo(df)
df_previsao = previsor.prever_ensemble(dias_futuros=7)
```

### Sistema de alertas

```python
from src.alerts import GestorAlertas, NivelAlerta

gestor = GestorAlertas(df)
gestor.adicionar_regra_consumo_diario(limite_kw=50.0, nivel=NivelAlerta.WARNING)
alertas = gestor.verificar_todas_regras()
```

### Análise de potência

```python
from src.power_analyzer import AnalisadorPotencia

analisador = AnalisadorPotencia(df)
potencia_recomendada, descricao, detalhes = analisador.recomendar_potencia()
```

---

## 🧪 Testes

```bash
pytest tests/ -v
```

Com cobertura de código:

```bash
pytest tests/ --cov=src --cov-report=html
```

---

## 📚 Documentação

### [Hub de Documentação](docs/README.md)
Documentação completa com guias e referências

### [Quick Start](docs/QUICK_START.md)
Começa em 5 minutos

### [Guias](docs/guides/)
Guias detalhados para cada funcionalidade:
- [Guia do Dashboard](docs/guides/dashboard-guide.md)
- [Guia de Análise](docs/guides/analysis-guide.md)
- [Guia de Configuração](docs/guides/configuration-guide.md)

### [FAQ](docs/FAQ.md)
Perguntas frequentes e resolução de problemas

### [API Reference](docs/api.md)
Documentação completa da API

### [Changelog](CHANGELOG.md)
Histórico de alterações

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT - ver o ficheiro [LICENSE](LICENSE) para detalhes.

---

## 👤 Autor

**NearDaniel** - Sistema desenvolvido para análise pessoal de consumo de eletricidade.

## Support

- 🐛 [Reportar Bug](https://github.com/neardaniel-pls/near-electric/issues/new?template=bug_report.md)
- 💡 [Sugerir Funcionalidade](https://github.com/neardaniel-pls/near-electric/issues/new?template=feature_request.md)

---

## Related Projects

- **[near-investing](https://github.com/neardaniel-pls/near-investing)**: Portfolio analysis and optimization tool
- **[near-fire-calculator](https://github.com/neardaniel-pls/near-fire-calculator)**: FIRE calculator for the Portuguese market
- **[fedora-user-scripts](https://github.com/neardaniel-pls/fedora-user-scripts)**: Utility scripts for Fedora Linux

---

**Near Electric** - Analisa, prevê e otimiza o teu consumo de eletricidade.
