# Contribuir

1. Faz fork do repo em https://github.com/neardaniel-pls/near-electric
2. Cria uma branch: `git checkout -b feature/nova-funcionalidade`
3. Faz as tuas alterações
4. Faz push e abre um pull request

## Estilo de Código

- Seguir PEP 8
- Usar type hints nas funções
- Adicionar docstrings em português
- Manter o código em `src/` e o dashboard em `dashboard.py`
- Usar `config/config.yaml` para configurações

## Testes

- Testar com `pytest tests/ -v`
- Verificar que o dashboard carrega: `streamlit run dashboard.py`

## Mensagens de Commit

Usar commits convencionais: `feat`, `fix`, `docs`, `refactor`, `chore`
