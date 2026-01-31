"""Testes para o módulo data_loader."""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

# Adicionar diretório src ao path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import CarregadorDados


@pytest.fixture
def dados_teste():
    """Cria dados de teste."""
    data = {
        'Data': ['2026/01/01', '2026/01/01', '2026/01/01'],
        'Hora': ['00:15', '00:30', '00:45'],
        'Consumo registado (kW)': [0.5, 0.6, 0.7],
        'Estado': ['Real', 'Real', 'Real']
    }
    return pd.DataFrame(data)


@pytest.fixture
def csv_teste(dados_teste):
    """Cria um ficheiro CSV temporário para teste."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        dados_teste.to_csv(f.name, index=False)
        yield f.name
    # Limpar
    os.unlink(f.name)


def test_carregador_inicializacao():
    """Testa inicialização do CarregadorDados."""
    carregador = CarregadorDados('data')
    assert carregador.data_dir == Path('data')
    assert carregador.dfs == []
    assert carregador.nomes_arquivos == []


def test_carregar_csv(csv_teste):
    """Testa carregamento de um ficheiro CSV."""
    carregador = CarregadorDados()
    df, nome = carregador.carregar_csv(csv_teste)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert 'Consumo registado (kW)' in df.columns
    assert 'DataHora' in df.columns
    assert 'HoraNum' in df.columns
    assert df['Consumo registado (kW)'].min() >= 0


def test_filtrar_estado(dados_teste):
    """Testa filtragem por estado."""
    dados_teste['Estado'] = ['Real', 'Real', 'Estimado']
    
    carregador = CarregadorDados()
    df_real = carregador.filtrar_estado(dados_teste, estado='Real')
    
    assert len(df_real) == 2
    assert all(df_real['Estado'] == 'Real')


def test_validar_estrutura(dados_teste):
    """Testa validação de estrutura do DataFrame."""
    carregador = CarregadorDados()
    
    # Deve passar
    try:
        carregador._validar_estrutura(dados_teste, 'teste.csv')
    except ValueError:
        pytest.fail("Validação falhou para estrutura correta")
    
    # Deve falhar
    dados_incompletos = dados_teste.drop('Estado', axis=1)
    with pytest.raises(ValueError):
        carregador._validar_estrutura(dados_incompletos, 'teste.csv')


def test_obter_info_dataset(dados_teste):
    """Testa obtenção de informações do dataset."""
    carregador = CarregadorDados()
    info = carregador.obter_info_dataset(dados_teste)
    
    assert 'total_registros' in info
    assert info['total_registros'] == 3
    assert 'periodo' in info
    assert 'meses' in info
    assert 'anos' in info


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
