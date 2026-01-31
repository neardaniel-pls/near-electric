
## 1. O Que Pode Ser Melhorado

### 1.2 Arquitetura e Design

#### 1.2.1 Separação de Responsabilidades
**Problema:** [`dashboard.py`](dashboard.py:1-750) é muito grande (750 linhas) e mistura lógica de UI com lógica de negócio.

**Recomendação:** Separar em módulos menores:
- `dashboard/ui_components.py` - Componentes reutilizáveis da UI
- `dashboard/handlers.py` - Handlers de eventos
- `dashboard/state.py` - Gerenciamento de estado da aplicação

#### 1.2.2 Injeção de Dependências
**Problema:** Classes como [`AnalisadorPotencia`](src/power_analyzer.py:89-125) carregam configuração diretamente de ficheiros.

**Recomendação:** Usar injeção de dependências para facilitar testes e flexibilidade.

```python
# Atual
class AnalisadorPotencia:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # Carrega config diretamente...

# Melhor
class AnalisadorPotencia:
    def __init__(self, df: pd.DataFrame, config: Config = None):
        self.df = df.copy()
        self.config = config or load_default_config()
```

#### 1.2.3 Padrão Singleton para Logging
**Problema:** [`src/utils.py`](src/utils.py:10-56) reconfigura logging toda vez que `setup_logging()` é chamado.

**Recomendação:** Implementar um padrão singleton ou lazy initialization para logging.

### 1.3 Performance

#### 1.3.1 Uso de Iteração em DataFrame
**Problema:** [`src/alerts.py`](src/alerts.py:233-243) usa `iterrows()` que é lento.

**Recomendação:** Usar operações vetorizadas do pandas.

```python
# Atual (lento)
for _, row in self.df.iterrows():
    if row['Consumo registado (kW)'] > regra['limite_kw']:
        # ...

# Melhor (vetorizado)
excessos = self.df[self.df['Consumo registado (kW)'] > regra['limite_kw']]
for _, row in excessos.iterrows():
    # ...
```

#### 1.3.2 Cache de Resultados
**Problema:** Cálculos repetidos são executados múltiplas vezes sem cache.

**Recomendação:** Implementar cache com `functools.lru_cache` para funções puras.

### 1.4 Configuração

#### 1.4.1 Validação de Configuração
**Problema:** [`config/config.yaml`](config/config.yaml) não tem validação de esquema.

**Recomendação:** Usar `pydantic` ou `marshmallow` para validar configuração.

```python
from pydantic import BaseModel, Field, validator

class Config(BaseModel):
    caminhos: Dict[str, str]
    logging: LoggingConfig
    processamento: ProcessamentoConfig
    
    @validator('logging')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v['nivel'] not in valid_levels:
            raise ValueError(f"Nível de log inválido: {v['nivel']}")
        return v
```

#### 1.4.2 Configuração de Ambiente
**Problema:** Não há suporte para variáveis de ambiente.

**Recomendação:** Adicionar suporte para `.env` usando `python-dotenv`.

### 1.6 Documentação

#### 1.6.1 Docstrings Incompletas
**Problema:** Alguns métodos não têm docstrings detalhadas.

**Recomendação:** Seguir o padrão Google Style ou NumPy Style para docstrings.

#### 1.6.2 Documentação de API
**Problema:** [`docs/api.md`](docs/api.md:1-707) não está sincronizada com o código atual (falta documentação de módulos novos).

**Recomendação:** Atualizar documentação para incluir:
- `src/seasonal_analyzer.py`
- `src/forecaster.py`
- `src/alerts.py`
- `src/power_analyzer.py`

---
