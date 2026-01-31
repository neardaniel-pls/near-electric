# Análise de Consumo de Eletricidade

Este projeto permite analisar dados de consumo de eletricidade de múltiplos meses a partir de ficheiros CSV.

## 📁 Estrutura do Projeto

```
analise-eletricidade/
├── venv/                                      # Ambiente virtual Python
├── data/                                      # Ficheiros CSV originais (um por mês)
│   └── consumo_janeiro_2026.csv             # Dados brutos de consumo
├── processed/                                  # Dados processados e exportados
│   ├── dados_combinados_processados.csv       # Todos os dados combinados
│   ├── resumo_por_arquivo.csv                # Resumo por ficheiro/mês
│   ├── resumo_por_mes.csv                    # Resumo por mês
│   └── consumo_janeiro_2026_processado.csv # Dados individuais processados
├── analise_consumo_eletricidade.ipynb       # Notebook Jupyter para análise
├── requirements.txt                            # Dependências Python
├── README.md                                   # Este ficheiro
└── .gitignore                                  # Ficheiros ignorados no Git
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

### 3. Iniciar o Jupyter Notebook

```bash
jupyter notebook
```

Isto abrirá o Jupyter no seu navegador. Abra o ficheiro [`analise_consumo_eletricidade.ipynb`](analise_consumo_eletricidade.ipynb) para começar a análise.

## 📊 Funcionalidades do Notebook

O notebook [`analise_consumo_eletricidade.ipynb`](analise_consumo_eletricidade.ipynb) inclui:

### 1. **Carregamento Automático de Múltiplos Ficheiros**
- Detecção automática de todos os ficheiros CSV na pasta `data/`
- Combinação de dados de múltiplos meses
- Processamento unificado de todos os ficheiros

### 2. **Pré-processamento**
- Conversão de tipos de dados
- Criação de colunas adicionais (dia, mês, ano, hora, dia da semana)
- Filtragem de dados reais vs estimados

### 3. **Análise Exploratória**
- Estatísticas básicas de consumo (todos os meses)
- Consumo por ficheiro/mês
- Consumo por mês
- Consumo por dia da semana
- Consumo por hora do dia

### 4. **Visualizações**
- Gráfico de consumo ao longo do tempo (todos os meses)
- Gráfico de consumo total por ficheiro/mês
- Gráfico de consumo por mês
- Gráfico de consumo por dia da semana
- Gráfico de consumo médio por hora
- Boxplot do consumo por dia da semana
- Comparação de consumo médio por hora entre meses
- Tendência de consumo ao longo dos meses
- Gráfico de custo por ficheiro/mês

### 5. **Análise Avançada**
- Identificação de picos de consumo
- Cálculo de custo estimado (tarifa configurável)
- Análise de padrões de consumo
- Horas de pico
- Comparação entre meses

### 6. **Exportação de Dados**
- Exportação de dados combinados para CSV
- Exportação de resumos por ficheiro/mês
- Exportação de dados individuais processados

### 7. **Resumo da Análise**
- Relatório final com todas as métricas importantes
- Comparação entre meses
- Identificação de meses com maior/menor consumo

## 📝 Como Adicionar Novos Meses

### Passo 1: Colocar o novo ficheiro CSV na pasta `data/`

Basta colocar o novo ficheiro CSV na pasta `data/`. O nome do ficheiro pode ser qualquer coisa, mas recomenda-se seguir o padrão:
- `consumo_janeiro_2026.csv`
- `consumo_fevereiro_2026.csv`
- `consumo_marco_2026.csv`
- etc.

### Passo 2: Executar o notebook

O notebook detectará automaticamente todos os ficheiros CSV na pasta `data/` e carregará os dados. Não é necessário alterar o código!

### Exemplo:

```bash
# Suponha que tem dados de janeiro e fevereiro
data/
├── consumo_janeiro_2026.csv
├── consumo_fevereiro_2026.csv
└── consumo_marco_2026.csv

# Execute o notebook e ele carregará todos os 3 ficheiros automaticamente
```

## 📋 Formato do CSV

Cada ficheiro CSV deve ter as seguintes colunas:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| Data | Data no formato YYYY/MM/DD | 2026/01/01 |
| Hora | Hora no formato HH:MM | 00:15 |
| Consumo registado (kW) | Consumo em kilowatts | 0.5 |
| Estado | Estado da medição (Real/Estimado) | Real |

## 🛠️ Dependências

- **pandas** (>=2.0.0) - Manipulação de dados
- **numpy** (>=1.24.0) - Operações numéricas
- **matplotlib** (>=3.7.0) - Visualização de dados
- **seaborn** (>=0.12.0) - Visualização avançada
- **jupyter** (>=1.0.0) - Ambiente de notebook

## 💡 Personalização

### Alterar a Tarifa de Eletricidade

No notebook, pode alterar a tarifa usada para calcular o custo:

```python
tarifa = 0.25  # € por kWh (altere este valor)
```

### Alterar as Pastas de Dados

Se quiser usar nomes diferentes para as pastas, altere estas variáveis no notebook:

```python
DATA_DIR = 'data'          # Pasta com ficheiros CSV originais
PROCESSED_DIR = 'processed'  # Pasta para dados processados
```

## 📈 Exemplos de Análise

### Perguntas que pode responder com este notebook:

1. **Qual foi o consumo total de todos os meses?**
   - O notebook calcula automaticamente o consumo total em kW

2. **Qual mês teve maior consumo?**
   - Consulte o gráfico "Consumo Total por Arquivo/Mês" ou o resumo final

3. **Como o consumo varia entre meses?**
   - Analise o gráfico "Tendência de Consumo por Mês"

4. **Qual é o padrão de consumo ao longo do dia?**
   - Consulte o gráfico "Consumo Médio por Hora do Dia"

5. **Como o consumo varia entre dias da semana?**
   - Analise o gráfico "Consumo por Dia da Semana"

6. **Qual foi o custo estimado de todos os meses?**
   - O notebook calcula o custo com base na tarifa configurada

7. **Quando ocorreram os picos de consumo?**
   - Consulte a secção "Identificar picos de consumo"

8. **Como o consumo se compara entre diferentes meses?**
   - Analise o gráfico "Comparação de Consumo Médio por Hora - Todos os Meses"

## 🔍 Dicas de Uso

1. **Execute as células em ordem** - O notebook está organizado sequencialmente
2. **Adicione novos ficheiros CSV à pasta `data/`** - O notebook detectará automaticamente
3. **Personalize as visualizações** - Pode alterar cores, tamanhos e estilos
4. **Adicione as suas próprias análises** - O notebook é um ponto de partida
5. **Guarde os resultados** - O notebook exporta dados processados automaticamente para a pasta `processed/`

## 📂 Organização dos Dados Processados

Após executar o notebook, os seguintes ficheiros serão criados na pasta `processed/`:

- `dados_combinados_processados.csv` - Todos os dados de todos os meses combinados
- `resumo_por_arquivo.csv` - Resumo do consumo por ficheiro/mês
- `resumo_por_mes.csv` - Resumo do consumo por mês
- `consumo_NOME_MES_processado.csv` - Dados individuais processados para cada ficheiro

## 🐛 Resolução de Problemas

### O ambiente virtual não funciona?
```bash
# Remova o venv existente e crie um novo
rm -rf venv  # Linux/Mac
# ou
rmdir /s venv  # Windows

python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### Erro ao importar bibliotecas?
```bash
# Certifique-se de que o ambiente virtual está ativado
# Reinstale as dependências
pip install -r requirements.txt --upgrade
```

### O Jupyter não abre?
```bash
# Tente instalar o jupyterlab como alternativa
pip install jupyterlab
jupyter lab
```

### O notebook não encontra os ficheiros CSV?
```bash
# Verifique se os ficheiros estão na pasta correta
ls data/  # Deve mostrar os ficheiros CSV

# Verifique o formato dos ficheiros
head data/consumo_janeiro_2026.csv  # Deve mostrar as colunas corretas
```

## 📚 Recursos Adicionais

- [Documentação do Pandas](https://pandas.pydata.org/docs/)
- [Documentação do Matplotlib](https://matplotlib.org/stable/contents.html)
- [Documentação do Seaborn](https://seaborn.pydata.org/)
- [Documentação do Jupyter](https://jupyter.org/documentation)

## 📄 Licença

Este projeto é para uso pessoal e educacional.

## 👤 Autor

Desenvolvido para análise pessoal de consumo de eletricidade.

---

**Nota:** Este notebook foi criado para analisar ficheiros CSV de consumo de eletricidade. Basta colocar novos ficheiros CSV na pasta `data/` e o notebook detectará automaticamente todos os meses disponíveis para análise.
