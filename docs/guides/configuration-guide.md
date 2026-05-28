# Guia de Configuração

Como configurar o Near Electric para o teu perfil de consumo.

## Ficheiros de Configuração

| Ficheiro | Propósito |
|----------|-----------|
| `config/config.yaml` | Configuração principal |
| `config/tariffs.yaml` | Definições de tarifas |
| `config/potencias.yaml` | Potências contratadas disponíveis |
| `config/local.yaml` | Configurações locais (não versionado) |

## config.yaml

```yaml
tarifas:
  padrao: "bi_horaria"  # simples, bi_horaria, tri_horaria

processamento:
  filtrar_estado: "Real"  # "Real", "Estimado", ou null para ambos

logging:
  nivel: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

potencia:
  atual: 10.35  # kVA
```

### Tarifa Padrão

Define qual tarifa usar por defeito nos cálculos:
- `simples` — Tarifa de preço único
- `bi_horaria` — Tarifa com horas de vazio e cheio
- `tri_horaria` — Tarifa com horas de vazio, ponta e cheio

### Filtrar Estado

- `"Real"` — Apenas leituras reais do contador (recomendado)
- `"Estimado"` — Apenas valores estimados pelo fornecedor
- `null` — Todos os valores

### Potência Atual

A potência contratada em kVA. Valores comuns: 3.45, 6.90, 10.35, 13.80, 17.25.

## tariffs.yaml

Contém as definições detalhadas das tarifas com preços por kWh:

```yaml
simples:
  unico: 0.1742

bi_horaria:
  vazio: 0.104
  cheio: 0.2584

tri_horaria:
  vazio: 0.0988
  ponta: 0.3371
  cheio: 0.1742
```

Atualiza estes valores com os preços do teu fornecedor de eletricidade.

## potencias.yaml

Lista de potências contratadas disponíveis com custos:

```yaml
potencias:
  - kva: 1.15
    custo_mensal: 2.85
  - kva: 3.45
    custo_mensal: 8.55
  - kva: 6.90
    custo_mensal: 17.10
  ...
```

## Alertas Personalizados

No dashboard, tab **Alertas**, podes configurar:
- Limite de consumo diário (kW)
- Limite de consumo horário (kW)
- Limiar de aumento mensal (%)
- Sensibilidade de deteção de anomalias

Ou via código:

```python
from src.alerts import GestorAlertas, NivelAlerta

gestor = GestorAlertas(df)
gestor.adicionar_regra_consumo_diario(limite_kw=50.0, nivel=NivelAlerta.WARNING)
```

## Configuração Local

Cria `config/local.yaml` para configurações que não queres versionar (ex: preços específicos do teu contrato). Este ficheiro está no `.gitignore`.

---

[Voltar à Documentação](../README.md) | [Anterior: Guia de Análise](analysis-guide.md)
