# Guia do Dashboard

O dashboard interativo é a forma mais fácil de analisar o teu consumo de eletricidade.

## Aceder ao Dashboard

```bash
source venv/bin/activate
streamlit run dashboard.py
```

Abre http://localhost:8501 no browser.

## Tabs

### Visão Geral
Visão geral do consumo com estatísticas, gráficos temporais e KPIs:
- Consumo total, médio, máximo e mínimo
- Gráfico de consumo ao longo do tempo
- Distribuição de consumo
- Comparação entre períodos

### Análise Sazonal
Padrões de consumo por período:
- Consumo por estação (Inverno, Primavera, Verão, Outono)
- Padrões por dia da semana
- Padrões horários
- Dias úteis vs fim de semana
- Heatmaps de consumo por hora e dia

### Previsão
Previsão de consumo futuro:
- Seleciona o número de dias a prever
- Gráfico com previsão e intervalos de confiança
- Comparação de métodos de previsão
- Estatísticas da previsão

### Alertas
Sistema de alertas de consumo:
- Alertas de consumo diário elevado
- Alertas de consumo horário elevado
- Detecção de anomalias
- Configuração de limites personalizados
- Filtragem por severidade (INFO, WARNING, CRITICAL)

### Tarifas
Comparação e otimização de tarifas:
- Cálculo automático com tarifas simples, bi-horária e tri-horária
- Comparação lado a lado
- Recomendação da tarifa mais económica
- Custo mensal estimado por tarifa
- Poupança potencial ao mudar de tarifa

### Potência
Análise de potência contratada:
- Seleção da potência atual
- Estatísticas de pico de consumo
- Comparação entre todas as potências disponíveis
- Recomendação de potência ideal
- Economia potencial anual

### Dados
Visualização dos dados brutos:
- Tabela com todos os dados carregados
- Filtros por data e estado
- Exportação em CSV e Excel

## Filtros

Na barra lateral:
- **Período**: Filtrar por intervalo de datas
- **Estado**: Filtrar por "Real" ou "Estimado"

## Exportação

Em várias tabs, podes exportar dados em CSV ou Excel usando os botões de download.

## Dicas

- Começa pela **Visão Geral** para ter uma ideia do consumo total
- Usa **Tarifas** para verificar se estás na tarifa mais económica
- Verifica **Potência** para garantir que não pagas demais na potência contratada
- **Previsão** ajuda a planear o consumo dos próximos dias

---

[Voltar à Documentação](../README.md) | [Seguinte: Guia de Análise](analysis-guide.md)
