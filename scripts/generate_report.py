#!/usr/bin/env python3
"""Script para geração de relatórios de análise de consumo."""

import sys
from pathlib import Path
import argparse
from datetime import datetime

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import setup_logging, carregar_config, validar_diretorio
from src.data_loader import CarregadorDados
from src.data_processor import ProcessadorDados
from src.analyzer import AnalisadorConsumo
from src.visualizer import VisualizadorConsumo
from src.tariff_calculator import (
    TarifaSimples, TarifaBiHoraria, TarifaTriHoraria,
    comparar_tarifas, recomendar_tarifa
)


def gerar_relatorio_texto(df, analisador, comparacao_tarifas, tarifa_recomendada, eficiencia):
    """Gera relatório em formato texto.
    
    Args:
        df: DataFrame processado.
        analisador: Instância de AnalisadorConsumo.
        comparacao_tarifas: DataFrame com comparação de tarifas.
        tarifa_recomendada: Tarifa recomendada.
        eficiencia: Dicionário com análise de eficiência.
        
    Returns:
        String com relatório formatado.
    """
    linhas = []
    linhas.append("="*70)
    linhas.append("RELATÓRIO DE ANÁLISE DE CONSUMO DE ELETRICIDADE")
    linhas.append("="*70)
    linhas.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    linhas.append("")
    
    # Período analisado
    if 'Data' in df.columns:
        linhas.append("-"*70)
        linhas.append("PERÍODO ANALISADO")
        linhas.append("-"*70)
        linhas.append(f"  Início: {df['Data'].min().strftime('%d/%m/%Y')}")
        linhas.append(f"  Fim: {df['Data'].max().strftime('%d/%m/%Y')}")
        linhas.append(f"  Dias: {(df['Data'].max() - df['Data'].min()).days + 1}")
        linhas.append("")
    
    # Estatísticas gerais
    estatisticas = analisador.calcular_estatisticas_gerais()
    linhas.append("-"*70)
    linhas.append("ESTATÍSTICAS GERAIS")
    linhas.append("-"*70)
    linhas.append(f"  Registros: {estatisticas['registros']}")
    linhas.append(f"  Consumo total: {estatisticas['total']:.2f} kW")
    linhas.append(f"  Consumo médio: {estatisticas['media']:.4f} kW")
    linhas.append(f"  Consumo mediano: {estatisticas['mediana']:.4f} kW")
    linhas.append(f"  Consumo mínimo: {estatisticas['minimo']:.4f} kW")
    linhas.append(f"  Consumo máximo: {estatisticas['maximo']:.2f} kW")
    linhas.append("")
    
    # Custo
    if 'Custo_EUR' in df.columns:
        custo_total = df['Custo_EUR'].sum()
        custo_medio = df['Custo_EUR'].mean()
        linhas.append("-"*70)
        linhas.append("CUSTO ESTIMADO")
        linhas.append("-"*70)
        linhas.append(f"  Custo total: €{custo_total:.2f}")
        linhas.append(f"  Custo médio: €{custo_medio:.4f}")
        linhas.append("")
    
    # Eficiência
    linhas.append("-"*70)
    linhas.append("EFICIÊNCIA")
    linhas.append("-"*70)
    linhas.append(f"  Consumo mensal: {eficiencia.get('consumo_mensal_estimado', 0):.2f} kWh")
    linhas.append(f"  Classificação: {eficiencia.get('classificacao', 'N/A')}")
    if 'vs_benchmark_medio' in eficiencia:
        vs = eficiencia['vs_benchmark_medio']
        status = "acima" if vs > 0 else "abaixo"
        linhas.append(f"  vs benchmark: {abs(vs):.1f}% {status} da média")
    linhas.append("")
    
    # Comparação de tarifas
    linhas.append("-"*70)
    linhas.append("COMPARAÇÃO DE TARIFAS")
    linhas.append("-"*70)
    for _, row in comparacao_tarifas.iterrows():
        linha = f"  {row['tarifa']}: €{row['custo_total']:.2f}"
        if row['tarifa'] == tarifa_recomendada.nome:
            linha += " ✓ RECOMENDADO"
        linhas.append(linha)
    linhas.append("")
    
    # Recomendação
    economia = comparacao_tarifas['custo_total'].max() - comparacao_tarifas['custo_total'].min()
    linhas.append("-"*70)
    linhas.append("RECOMENDAÇÃO")
    linhas.append("-"*70)
    linhas.append(f"  Tarifa: {tarifa_recomendada.nome}")
    linhas.append(f"  Custo: €{comparacao_tarifas['custo_total'].min():.2f}")
    linhas.append(f"  Economia: €{economia:.2f} vs tarifa mais cara")
    linhas.append("")
    
    # Picos de consumo
    picos = analisador.identificar_picos(5)
    linhas.append("-"*70)
    linhas.append("TOP 5 PICOS DE CONSUMO")
    linhas.append("-"*70)
    for i, (_, row) in enumerate(picos.iterrows(), 1):
        data_hora = row['DataHora'].strftime('%d/%m/%Y %H:%M') if 'DataHora' in row else 'N/A'
        consumo = row['Consumo registado (kW)']
        linhas.append(f"  {i}. {data_hora} - {consumo:.2f} kW")
    linhas.append("")
    
    linhas.append("="*70)
    linhas.append("FIM DO RELATÓRIO")
    linhas.append("="*70)
    
    return "\n".join(linhas)


def main():
    """Função principal para geração de relatórios."""
    parser = argparse.ArgumentParser(
        description='Geração de relatórios de análise de consumo'
    )
    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Caminho para o ficheiro de configuração'
    )
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Diretório com os ficheiros CSV de dados'
    )
    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Diretório para guardar os relatórios'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Nível de logging'
    )
    parser.add_argument(
        '--formato',
        default='txt',
        choices=['txt', 'html'],
        help='Formato do relatório'
    )
    args = parser.parse_args()
    
    # Configurar logging
    logger = setup_logging(log_level=args.log_level)
    logger.info("="*70)
    logger.info("GERAÇÃO DE RELATÓRIOS")
    logger.info("="*70)
    
    try:
        # Carregar configuração
        logger.info("Carregando configuração...")
        config = carregar_config(args.config)
        
        # Validar diretórios
        logger.info("Validando diretórios...")
        data_dir = validar_diretorio(args.data_dir, criar=False)
        output_dir = validar_diretorio(args.output_dir, criar=True)
        
        # Carregar dados
        logger.info("Carregando dados...")
        carregador = CarregadorDados(str(data_dir))
        df_completo = carregador.carregar_todos()
        
        if len(df_completo) == 0:
            logger.error("Nenhum dado foi carregado")
            return 1
        
        # Filtrar dados reais
        df_real = carregador.filtrar_estado(df_completo, estado='Real')
        
        # Processar dados
        logger.info("Processando dados...")
        processador = ProcessadorDados(df_real)
        df_processado = processador.limpar_dados(estrategia='remover')
        tarifa = config.get('tarifas', {}).get('parametros', {}).get('simples', {}).get('preco', 0.25)
        df_processado = processador.adicionar_colunas_calculadas(tarifa=tarifa)
        
        # Analisar
        logger.info("Executando análises...")
        analisador = AnalisadorConsumo(df_processado)
        
        # Comparar tarifas
        logger.info("Comparando tarifas...")
        tarifas = [
            TarifaSimples(0.25, "Simples"),
            TarifaBiHoraria(0.104, 0.2584, nome="Bi-horária"),
            TarifaTriHoraria(0.104, 0.312, 0.2584, nome="Tri-horária")
        ]
        df_comparacao = comparar_tarifas(df_processado, tarifas)
        tarifa_recomendada, resumo_recomendacao = recomendar_tarifa(df_processado, tarifas)
        
        # Análise de eficiência
        area = config.get('analise', {}).get('area_habitacao')
        eficiencia = analisador.analisar_eficiencia(area_m2=area)
        
        # Gerar relatório
        logger.info("Gerando relatório...")
        relatorio = gerar_relatorio_texto(
            df_processado,
            analisador,
            df_comparacao,
            tarifa_recomendada,
            eficiencia
        )
        
        # Salvar relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if args.formato == 'html':
            caminho = output_dir / f'relatorio_{timestamp}.html'
            # TODO: Implementar versão HTML
            logger.warning("Versão HTML ainda não implementada")
            caminho = output_dir / f'relatorio_{timestamp}.txt'
        else:
            caminho = output_dir / f'relatorio_{timestamp}.txt'
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        logger.info(f"Relatório salvo em: {caminho}")
        
        # Mostrar relatório
        print("\n" + relatorio)
        
        logger.info("Relatório gerado com sucesso!")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Ficheiro não encontrado: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Erro de valor: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Erro inesperado: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
