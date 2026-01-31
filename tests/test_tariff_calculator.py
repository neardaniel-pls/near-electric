"""Testes para o módulo tariff_calculator."""

import pytest
import pandas as pd
from datetime import datetime, time

# Adicionar diretório src ao path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tariff_calculator import (
    TarifaSimples, TarifaBiHoraria, TarifaTriHoraria,
    comparar_tarifas, recomendar_tarifa
)


@pytest.fixture
def dados_teste():
    """Cria dados de teste para cálculo de tarifas."""
    data = []
    for dia in range(1, 4):  # 3 dias
        for hora in range(0, 24, 3):  # A cada 3 horas
            data.append({
                'DataHora': datetime(2026, 1, dia, hora, 0),
                'HoraNum': hora,
                'Consumo_kWh': 0.5  # 0.5 kWh por registro
            })
    return pd.DataFrame(data)


def test_tarifa_simples(dados_teste):
    """Testa tarifa simples."""
    tarifa = TarifaSimples(preco_kwh=0.25)
    
    df_custo = tarifa.calcular_custo(dados_teste)
    
    assert 'Custo_EUR' in df_custo.columns
    assert df_custo['Custo_EUR'].sum() == pytest.approx(24 * 0.5 * 0.25)  # 24 registros
    
    resumo = tarifa.obter_resumo(df_custo)
    assert resumo['tarifa'] == 'Simples'
    assert resumo['preco_kwh'] == 0.25


def test_tarifa_bi_horaria(dados_teste):
    """Testa tarifa bi-horária."""
    tarifa = TarifaBiHoraria(preco_vazio=0.104, preco_cheio=0.2584)
    
    df_custo = tarifa.calcular_custo(dados_teste)
    
    assert 'Custo_EUR' in df_custo.columns
    assert 'Horario' in df_custo.columns
    assert set(df_custo['Horario'].unique()) <= {'vazio', 'cheio'}
    
    # Verificar se horário de vazio está correto
    vazio = df_custo[df_custo['Horario'] == 'vazio']
    assert len(vazio) > 0
    
    resumo = tarifa.obter_resumo(df_custo)
    assert resumo['tarifa'] == 'Bi-horária'
    assert resumo['preco_vazio'] == 0.104
    assert resumo['preco_cheio'] == 0.2584


def test_tarifa_tri_horaria(dados_teste):
    """Testa tarifa tri-horária."""
    tarifa = TarifaTriHoraria(
        preco_vazio=0.104,
        preco_ponta=0.312,
        preco_cheio=0.2584
    )
    
    df_custo = tarifa.calcular_custo(dados_teste)
    
    assert 'Custo_EUR' in df_custo.columns
    assert 'Periodo' in df_custo.columns
    assert set(df_custo['Periodo'].unique()) <= {'vazio', 'ponta', 'cheio'}
    
    resumo = tarifa.obter_resumo(df_custo)
    assert resumo['tarifa'] == 'Tri-horária'
    assert resumo['preco_vazio'] == 0.104
    assert resumo['preco_ponta'] == 0.312
    assert resumo['preco_cheio'] == 0.2584


def test_comparar_tarifas(dados_teste):
    """Testa comparação de tarifas."""
    tarifas = [
        TarifaSimples(0.25),
        TarifaBiHoraria(0.104, 0.2584),
        TarifaTriHoraria(0.104, 0.312, 0.2584)
    ]
    
    df_comparacao = comparar_tarifas(dados_teste, tarifas)
    
    assert len(df_comparacao) == 3
    assert 'tarifa' in df_comparacao.columns
    assert 'custo_total' in df_comparacao.columns
    assert df_comparacao['custo_total'].is_monotonic_increasing  # Ordenado por custo


def test_recomendar_tarifa(dados_teste):
    """Testa recomendação de tarifa."""
    tarifas = [
        TarifaSimples(0.25),
        TarifaBiHoraria(0.104, 0.2584),
        TarifaTriHoraria(0.104, 0.312, 0.2584)
    ]
    
    tarifa, resumo = recomendar_tarifa(dados_teste, tarifas)
    
    assert isinstance(tarifa, TarifaBiHoraria)  # Deve ser a mais económica
    assert 'custo_total' in resumo
    assert resumo['custo_total'] > 0


def test_horario_vazio_bi_horaria():
    """Testa determinação de horário de vazio na tarifa bi-horária."""
    tarifa = TarifaBiHoraria(preco_vazio=0.104, preco_cheio=0.2584)
    
    # Horas de vazio: 00h-07h e 22h-24h
    assert tarifa._eh_horario_vazio(0) == True
    assert tarifa._eh_horario_vazio(6) == True
    assert tarifa._eh_horario_vazio(22) == True
    assert tarifa._eh_horario_vazio(23) == True
    
    # Horas de cheio: 07h-22h
    assert tarifa._eh_horario_vazio(7) == False
    assert tarifa._eh_horario_vazio(12) == False
    assert tarifa._eh_horario_vazio(21) == False


def test_periodo_tri_horaria():
    """Testa determinação de período na tarifa tri-horária."""
    tarifa = TarifaTriHoraria(
        preco_vazio=0.104,
        preco_ponta=0.312,
        preco_cheio=0.2584
    )
    
    # Vazio: 00h-07h e 22h-24h
    assert tarifa._determinar_periodo(0) == 'vazio'
    assert tarifa._determinar_periodo(6) == 'vazio'
    assert tarifa._determinar_periodo(22) == 'vazio'
    
    # Ponta: 18h-21h
    assert tarifa._determinar_periodo(18) == 'ponta'
    assert tarifa._determinar_periodo(20) == 'ponta'
    
    # Cheio: restante
    assert tarifa._determinar_periodo(7) == 'cheio'
    assert tarifa._determinar_periodo(12) == 'cheio'
    assert tarifa._determinar_periodo(21) == 'cheio'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
