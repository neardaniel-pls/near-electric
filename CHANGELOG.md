# Changelog

Todas as alterações notáveis deste projeto serão documentadas neste ficheiro.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.2.0] - 2026-01-31

### Adicionado
- **Análise de Potência Contratada**
  - Módulo `src/power_analyzer.py` - Análise de potência contratada
  - Recomendação de potência contratada baseada no consumo real
  - Análise de eficiência da potência atual
  - Comparação entre todas as potências disponíveis (1.15 a 20.70 kVA)
  - Cálculo de economia potencial anual
  - Margens de segurança configuráveis (conservadora, moderada, otimista)
  - Estatísticas de pico (máximo, médio, percentil 95, percentil 99)
  - Classificação da potência atual (sobredimensionada, adequada, subdimensionada)
  - Relatório detalhado de análise de potência

- **Nova Tab no Dashboard**
  - Tab "⚡ Potência" com análise completa de potência contratada
  - Seleção de potência atual
  - Configuração de margem de segurança
  - Visualização de estatísticas de consumo
  - Gráficos de comparação de potências
  - Gráficos de utilização por potência
  - Recomendação de potência com economia potencial

### Melhorado
- **Dashboard**
  - Atualizado para 7 tabs (adicionada tab de Potência)
  - Nova funcionalidade de análise de potência contratada
  - Visualizações adicionais para comparação de potências

- **Documentação**
  - README.md atualizado com nova funcionalidade
  - Exemplos de uso para análise de potência

### Notas
- A análise de potência ajuda a identificar se a potência contratada está adequada
- Potências disponíveis: 1.15, 2.30, 3.45, 6.90, 10.35, 13.80, 17.25, 20.70 kVA
- Custos de potência baseados em valores aproximados da EDP
- A margem de segurança permite ajustar a recomendação conforme preferência

## [1.1.0] - 2026-01-31

### Adicionado
- **Análise Sazonal (Fase 2)**
  - Módulo `src/seasonal_analyzer.py` - Análise de padrões sazonais
  - Comparação de meses entre anos
  - Análise por estação (Inverno, Primavera, Verão, Outono)
  - Padrões de consumo por dia da semana
  - Padrões horários
  - Comparação dias úteis vs fim de semana
  - Índices sazonais
  - Detecção de mudanças sazonais
  - Análise de feriados vs dias normais

- **Previsão de Consumo (Fase 3)**
  - Módulo `src/forecaster.py` - Previsão de consumo futuro
  - Previsão por média móvel
  - Previsão por padrão semanal
  - Previsão por padrão diário
  - Previsão por tendência linear
  - Previsão ensemble (combinação de métodos)
  - Intervalos de confiança
  - Comparação de métodos de previsão
  - Resumo de previsão

- **Sistema de Alertas (Fase 3)**
  - Módulo `src/alerts.py` - Sistema de alertas configuráveis
  - Alertas de consumo diário alto
  - Alertas de consumo horário alto
  - Alertas de aumento mensal
  - Detecção de anomalias usando Z-score
  - Alertas de custo alto
  - Configuração personalizada de limites
  - Filtragem por nível de severidade (INFO, WARNING, CRITICAL)
  - Exportação de alertas

- **Visualizações Avançadas (Fase 2 e 4)**
  - Heatmaps de consumo por hora e dia da semana
  - Heatmaps de consumo por hora e mês
  - Distribuição de consumo (histograma e KDE)
  - Comparação anual (year-over-year)
  - Painel de KPIs (Key Performance Indicators)
  - Novos métodos adicionados ao `VisualizadorConsumo`

- **Dashboard Interativo (Fase 4)**
  - `dashboard.py` - Dashboard web com Streamlit
  - Interface interativa para análise de dados
  - Filtros de data e estado
  - 6 tabs: Visão Geral, Análise Sazonal, Previsão, Alertas, Tarifas, Dados
  - Visualização em tempo real
  - Exportação de dados em CSV e Excel

- **Exportação de Dados**
  - Suporte para exportação em Excel (openpyxl)
  - Download direto do dashboard

### Melhorado
- **Visualizador**
  - Adicionados 5 novos métodos de visualização
  - Suporte a diferentes colormaps para heatmaps
  - Opções de salvamento de figuras

- **Documentação**
  - README.md atualizado com novas funcionalidades
  - Exemplos de uso para análise sazonal, previsão e alertas
  - Estrutura do projeto atualizada

### Alterado
- **Dependências**
  - Adicionadas `streamlit>=1.28.0` para dashboard
  - Adicionadas `openpyxl>=3.1.0` e `xlsxwriter>=3.1.0` para Excel
  - Atualizadas versões mínimas

### Notas
- Esta versão implementa as Fases 2-4 do roadmap definido em VALIDACAO_NOTEBOOK.md
- O dashboard pode ser iniciado com: `streamlit run dashboard.py`
- Para usar as novas funcionalidades, instale as dependências atualizadas

## [1.0.0] - 2026-01-31

### Adicionado
- **Estrutura modular do projeto**
  - Módulo `src/utils.py` - Funções utilitárias e logging profissional
  - Módulo `src/data_loader.py` - Carregamento automático de dados
  - Módulo `src/data_processor.py` - Processamento e validação de dados
  - Módulo `src/analyzer.py` - Análises estatísticas avançadas
  - Módulo `src/visualizer.py` - Visualizações profissionais
  - Módulo `src/tariff_calculator.py` - Cálculo com diferentes tarifas

- **Sistema de configuração**
  - `config/config.yaml` - Configuração principal do projeto
  - `config/tariffs.yaml` - Definições detalhadas de tarifas portuguesas

- **Scripts utilitários**
  - `scripts/run_analysis.py` - Script principal de análise
  - `scripts/validate_data.py` - Validação de qualidade de dados
  - `scripts/generate_report.py` - Geração de relatórios
  - `setup.py` - Script de setup inicial

- **Suporte a tarifas**
  - Tarifa simples (único preço)
  - Tarifa bi-horária (vazio e cheio)
  - Tarifa tri-horária (vazio, ponta e cheio)
  - Comparação automática entre tarifas
  - Recomendação da tarifa mais económica

- **Validação de dados**
  - Detecção de valores negativos
  - Identificação de valores nulos
  - Verificação de continuidade temporal
  - Detecção de outliers usando Z-score

- **Análises estatísticas**
  - Estatísticas descritivas (média, mediana, desvio padrão)
  - Análise por período (dia, semana, mês, ano)
  - Identificação de picos de consumo
  - Análise de padrões temporais
  - Comparação entre períodos
  - Análise de eficiência com benchmarks

- **Visualizações**
  - Consumo ao longo do tempo
  - Consumo por período (mês, dia da semana, hora)
  - Boxplots de distribuição
  - Comparação entre períodos
  - Tendência de consumo
  - Múltiplos gráficos em uma figura

- **Logging profissional**
  - Configuração de níveis de log
  - Saída para ficheiro e console
  - Mensagens detalhadas de progresso

- **Testes unitários**
  - Testes para `data_loader`
  - Testes para `tariff_calculator`
  - Estrutura para expansão de testes

- **Documentação**
  - `VALIDACAO_NOTEBOOK.md` - Documento detalhado de validação
  - `docs/api.md` - Documentação completa da API
  - `README.md` atualizado com nova estrutura
  - `CHANGELOG.md` - Este ficheiro

### Melhorado
- **Modularização**
  - Código separado em módulos reutilizáveis
  - Funções com type hints
  - Docstrings detalhadas
  - Exemplos de uso

- **Tratamento de erros**
  - Try/except em pontos críticos
  - Mensagens de erro claras
  - Logging de exceções

- **Performance**
  - Uso de vetoriação onde possível
  - Cache de resultados (estrutura preparada)
  - Processamento eficiente de grandes datasets

- **Configuração**
  - Ficheiros YAML para configuração
  - Parâmetros centralizados
  - Fácil personalização

### Alterado
- **Estrutura do projeto**
  - Nova organização de diretórios
  - Separação clara entre código, testes e dados
  - Scripts independentes no diretório `scripts/`

- **Dependências**
  - Adicionadas `pyyaml` e `scipy` ao `requirements.txt`
  - Versões mínimas especificadas

### Removido
- Nada

### Segurança
- Nenhuma vulnerabilidade conhecida

### Notas
- Esta versão representa uma refatoração completa do notebook original
- O notebook original `analise_consumo_eletricidade.ipynb` ainda pode ser usado
- Para usar os novos módulos, execute `python setup.py` primeiro
- As dependências devem ser instaladas: `pip install -r requirements.txt`

## [0.1.0] - Data anterior

### Adicionado
- Notebook Jupyter `analise_consumo_eletricidade.ipynb`
- Carregamento automático de ficheiros CSV
- Análise exploratória básica
- 9 visualizações estáticas
- Cálculo de custo com tarifa simples
- Exportação de dados processados

---

## Próximas Versões

### [1.1.0] - Planejado
- Adicionar dashboard interativo com Streamlit
- Implementar previsão de consumo usando séries temporais
- Adicionar alertas automáticos
- Suporte a dados em tempo real
- Exportação de relatórios em PDF
- Integração com APIs de fornecedores de energia

### [1.2.0] - Planejado
- Análise de sazonalidade avançada
- Detecção de anomalias com machine learning
- Otimização de consumo com recomendações
- Comparação com dados de outros utilizadores
- Análise de impacto de clima no consumo
- Dashboard móvel

---

## Convenções de Versão

- **Major (X.0.0):** Alterações significativas, que podem quebrar compatibilidade
- **Minor (X.Y.0):** Novas funcionalidades, compatibilidade mantida
- **Patch (X.Y.Z):** Correções de bugs, pequenas melhorias
