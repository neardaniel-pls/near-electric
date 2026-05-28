# Quick Start

Começa a usar o Near Electric em 5 minutos.

## Pré-requisitos

- Python 3.11+
- pip

## Setup (2 minutos)

### Passo 1: Clonar o projeto
```bash
git clone https://github.com/neardaniel-pls/near-electric.git
cd near-electric
```

### Passo 2: Criar ambiente virtual
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Passo 3: Executar o dashboard
```bash
streamlit run dashboard.py
```

Abre http://localhost:8501 no browser.

## Primeira Análise (2 minutos)

### Passo 1: Adicionar dados
Coloca ficheiros CSV na pasta `data/` com o formato:
```csv
Data,Hora,Consumo registado (kW),Estado
2026/02/01,00:15,0.5,Real
2026/02/01,00:30,0.6,Real
```

### Passo 2: Explorar o Dashboard
O dashboard tem 7 tabs:
1. **Visão Geral** — Estatísticas e gráficos de consumo
2. **Análise Sazonal** — Padrões por estação, dia da semana, hora
3. **Previsão** — Previsão de consumo futuro
4. **Alertas** — Alertas de consumo elevado
5. **Tarifas** — Comparação de tarifas (simples, bi-horária, tri-horária)
6. **Potência** — Análise de potência contratada
7. **Dados** — Visualização dos dados brutos

## Configuração (Opcional)

Edita `config/config.yaml` para:
- Mudar a tarifa padrão
- Ajustar limites de alertas
- Configurar a potência contratada

## Análise via Código

```python
from src.data_loader import carregar_dados
from src.analyzer import AnalisadorConsumo

df, carregador = carregar_dados()
analisador = AnalisadorConsumo(df)
estatisticas = analisador.calcular_estatisticas_gerais()
```

## Próximos Passos

1. **Guia do Dashboard**: [dashboard-guide.md](guides/dashboard-guide.md)
2. **Guia de Análise**: [analysis-guide.md](guides/analysis-guide.md)
3. **Configuração**: [configuration-guide.md](guides/configuration-guide.md)

## Precisas de ajuda?

- **FAQ**: [FAQ.md](FAQ.md)
- **API**: [api.md](api.md)
- **Issues**: [Reportar Bug](https://github.com/neardaniel-pls/near-electric/issues/new?template=bug_report.md)

---

**Última Atualização**: 2026-05-25
