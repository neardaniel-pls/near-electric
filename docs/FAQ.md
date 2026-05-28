# Perguntas Frequentes

## Geral

### Onde obtive os dados de consumo?
Podes exportar os dados do teu fornecedor de eletricidade (ex: EDP). O sistema aceita ficheiros CSV com as colunas: `Data`, `Hora`, `Consumo registado (kW)`, `Estado`.

### Funciona com dados de outros países?
O sistema foi desenhado para o mercado português (tarifas EDP, potências em kVA). Podes adaptar as tarifas em `config/tariffs.yaml` para outros mercados.

### Preciso de ter Python instalado?
Sim. O dashboard corre sobre Streamlit, que requer Python 3.11+. Segue o [Quick Start](QUICK_START.md) para instalar.

## Dados

### Que formato deve ter o CSV?
```csv
Data,Hora,Consumo registado (kW),Estado
2026/02/01,00:15,0.5,Real
2026/02/01,00:30,0.6,Real
```

### Posso analisar vários meses?
Sim! Coloca todos os ficheiros CSV na pasta `data/`. O sistema detecta e combina automaticamente.

### O que significa "Estado" no CSV?
- **Real** — Leitura real do contador
- **Estimado** — Valor estimado pelo fornecedor

Por defeito, o sistema filtra apenas valores "Real". Podes alterar em `config/config.yaml`.

## Tarifas

### Quais tarifas estão disponíveis?
- **Simples** — Preço único durante todo o dia
- **Bi-horária** — Preço diferente nas horas de vazio e cheio
- **Tri-horária** — Preço diferente nas horas de vazio, ponta e cheio

### Como comparo tarifas?
No dashboard, vai à tab **Tarifas**. O sistema calcula o custo com cada tarifa e recomenda a mais económica para o teu perfil.

### Os preços das tarifas estão atualizados?
Os preços estão em `config/tariffs.yaml`. Verifica e atualiza com os valores do teu fornecedor.

## Potência Contratada

### O que é a potência contratada?
É a potência máxima que podes usar em simultâneo, definida no teu contrato com o fornecedor. Potências maiores têm custos fixos maiores.

### Como sei se a minha potência está adequada?
Vai à tab **Potência** no dashboard. O sistema analisa o teu consumo real e recomenda a potência ideal.

## Previsão

### Quão precisas são as previsões?
As previsões usam múltiplos métodos (média móvel, padrão semanal, tendência linear) e combinam-os num ensemble. A precisão depende da quantidade e qualidade dos dados.

### Posso prever mais do que 7 dias?
Sim, mas a precisão diminui com o horizonte de previsão. Previsões curtas (3-7 dias) são mais fiáveis.

## Troubleshooting

### Os dados não carregam
- Verifica que o CSV tem as colunas corretas: `Data`, `Hora`, `Consumo registado (kW)`, `Estado`
- Verifica que o ficheiro está na pasta `data/`
- Verifica que o encoding é UTF-8

### O dashboard não abre
```bash
source venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

### Erro "ModuleNotFoundError"
Certifica-te que o ambiente virtual está ativo: `source venv/bin/activate`

## Ainda tens dúvidas?

- **Documentação completa**: [docs/README.md](README.md)
- **Reportar problema**: [Issues](https://github.com/neardaniel-pls/near-electric/issues)

---

**Última Atualização**: 2026-05-25
