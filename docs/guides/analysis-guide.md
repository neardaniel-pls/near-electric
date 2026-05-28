# Guia de Análise

Guia para usar o Near Electric como módulo Python para análises avançadas.

## Carregar Dados

```python
from src.data_loader import carregar_dados

df, carregador = carregar_dados()
print(f"Carregados {len(df)} registos")
```

O sistema lê automaticamente todos os ficheiros CSV da pasta `data/`.

## Análise Estatística

```python
from src.analyzer import AnalisadorConsumo

analisador = AnalisadorConsumo(df)
estatisticas = analisador.calcular_estatisticas_gerais()
picos = analisador.identificar_picos()
```

Métodos disponíveis:
- `calcular_estatisticas_gerais()` — Estatísticas descritivas
- `analise_por_periodo()` — Análise por dia, semana, mês, ano
- `identificar_picos()` — Detetar picos de consumo
- `comparar_periodos()` — Comparar dois períodos

## Análise Sazonal

```python
from src.seasonal_analyzer import AnalisadorSazonal

sazonal = AnalisadorSazonal(df)
comparacao = sazonal.comparar_meses_entre_anos(mes=1)
estacoes = sazonal.analisar_por_estacao()
uteis_fim_semana = sazonal.comparar_uteis_fim_semana()
```

Funcionalidades:
- Comparação de meses entre anos
- Análise por estação do ano
- Padrões por dia da semana
- Comparação dias úteis vs fim de semana
- Índices sazonais

## Comparação de Tarifas

```python
from src.tariff_calculator import TarifaSimples, TarifaBiHoraria, TarifaTriHoraria, recomendar_tarifa

tarifas = [
    TarifaSimples(0.1742),
    TarifaBiHoraria(0.104, 0.2584),
    TarifaTriHoraria(0.0988, 0.3371, 0.1742),
]

melhor, resumo = recomendar_tarifa(df, tarifas)
print(f"Melhor tarifa: {melhor}")
```

Tarifas disponíveis:
- **TarifaSimples(preco)** — Preço único
- **TarifaBiHoraria(vazio, cheio)** — Dois períodos
- **TarifaTriHoraria(vazio, ponta, cheio)** — Três períodos

## Previsão de Consumo

```python
from src.forecaster import PrevisorConsumo

previsor = PrevisorConsumo(df)
previsao = previsor.prever_ensemble(dias_futuros=7)
comparacao = previsor.comparar_metodos()
```

Métodos de previsão:
- Média móvel
- Padrão semanal
- Padrão diário
- Tendência linear
- Ensemble (combinação automática)

## Sistema de Alertas

```python
from src.alerts import GestorAlertas, NivelAlerta

gestor = GestorAlertas(df)
gestor.adicionar_regra_consumo_diario(limite_kw=50.0, nivel=NivelAlerta.WARNING)
alertas = gestor.verificar_todas_regras()

for alerta in alertas:
    print(f"[{alerta.nivel.name}] {alerta.mensagem}")
```

Tipos de alertas:
- Consumo diário acima do limite
- Consumo horário acima do limite
- Aumento mensal significativo
- Anomalias (Z-score)
- Custo elevado

## Análise de Potência

```python
from src.power_analyzer import AnalisadorPotencia

analisador = AnalisadorPotencia(df, potencia_atual=10.35)
potencia, descricao, detalhes = analisador.recomendar_potencia()
```

A análise verifica:
- Se a potência contratada está adequada
- Qual a potência ideal baseada no consumo real
- Economia potencial ao ajustar a potência
- Margens de segurança (conservadora, moderada, otimista)

## Visualizações

```python
from src.visualizer import VisualizadorConsumo

visualizador = VisualizadorConsumo(df)
fig = visualizador.plotar_consumo_temporal()
fig = visualizador.plotar_heatmap_hora_dia()
fig = visualizador.plotar_distribuicao()
```

## Dicas

- Sempre começa com `carregar_dados()` para obter o DataFrame
- Usa `calcular_estatisticas_gerais()` para ter uma visão rápida
- Compara tarifas para otimizar custos
- Verifica a potência contratada para poupar nos custos fixos

---

[Voltar à Documentação](../README.md) | [Anterior: Guia do Dashboard](dashboard-guide.md) | [Seguinte: Guia de Configuração](configuration-guide.md)
