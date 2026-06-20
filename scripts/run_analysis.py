#!/usr/bin/env python3
"""Script principal para executar análise de consumo de eletricidade."""

import sys
from pathlib import Path
import argparse
import logging
import matplotlib.pyplot as plt

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import setup_logging, carregar_config, validar_diretorio
from src.data_loader import CarregadorDados, carregar_dados
from src.data_processor import ValidadorDados, ProcessadorDados
from src.analyzer import AnalisadorConsumo
from src.visualizer import VisualizadorConsumo
from src.tariff_calculator import (
    TarifaSimples, TarifaBiHoraria, TarifaTriHoraria,
    comparar_tarifas, recomendar_tarifa
)


def main():
    """Função principal para executar a análise."""
    # Parse argumentos da linha de comando
    parser = argparse.ArgumentParser(
        description='Análise de consumo de eletricidade'
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
        default='processed',
        help='Diretório para guardar os dados processados'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Nível de logging'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Não mostrar gráficos'
    )
    parser.add_argument(
        '--save-plots',
        action='store_true',
        help='Salvar gráficos em ficheiros'
    )
    args = parser.parse_args()
    
    # Configurar logging
    logger = setup_logging(log_level=args.log_level)
    logger.info("="*70)
    logger.info("INÍCIO DA ANÁLISE DE CONSUMO DE ELETRICIDADE")
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
            logger.error("Nenhum dado foi carregado. Verifique se há ficheiros CSV em data/")
            return 1
        
        # Filtrar dados reais
        logger.info("Filtrando dados reais...")
        df_real = carregador.filtrar_estado(df_completo, estado='Real')
        
        # Validar qualidade dos dados
        logger.info("Validando qualidade dos dados...")
        validador = ValidadorDados(df_real)
        relatorio_validacao = validador.validar()
        
        if relatorio_validacao['estatisticas']:
            logger.info(
                f"Estatísticas: {relatorio_validacao['estatisticas']['registros_validos']} "
                f"registros válidos de {relatorio_validacao['estatisticas']['total_registros']}"
            )
        
        # Processar dados
        logger.info("Processando dados...")
        processador = ProcessadorDados(df_real)
        df_processado = processador.limpar_dados(estrategia='remover')
        
        # Adicionar colunas calculadas
        tarifa_padrao = config.get('tarifas', {}).get('parametros', {}).get('simples', {}).get('preco', 0.25)
        df_processado = processador.adicionar_colunas_calculadas(tarifa=tarifa_padrao)
        
        # Análise estatística
        logger.info("Executando análise estatística...")
        analisador = AnalisadorConsumo(df_processado)
        estatisticas = analisador.calcular_estatisticas_gerais()
        
        logger.info(
            f"Consumo total: {estatisticas['total']:.2f} kW, "
            f"Média: {estatisticas['media']:.4f} kW"
        )
        
        # Análise por período
        logger.info("Analisando por período...")
        consumo_por_mes = analisador.analisar_por_periodo('NomeMes')
        consumo_por_dia = analisador.analisar_por_periodo('NomeDiaSemana')
        
        # Identificar picos
        logger.info("Identificando picos de consumo...")
        picos = analisador.identificar_picos(top_n=10)
        
        # Análise de eficiência
        logger.info("Analisando eficiência...")
        area = config.get('analise', {}).get('area_habitacao')
        eficiencia = analisador.analisar_eficiencia(area_m2=area)
        logger.info(f"Classificação de eficiência: {eficiencia.get('classificacao', 'N/A')}")
        
        # Comparar tarifas
        logger.info("Comparando tarifas...")
        tarifas = [
            TarifaSimples(0.25, "Simples"),
            TarifaBiHoraria(0.104, 0.2584, nome="Bi-horária"),
            TarifaTriHoraria(0.104, 0.312, 0.2584, nome="Tri-horária")
        ]
        
        df_comparacao = comparar_tarifas(df_processado, tarifas)
        logger.info("Comparação de tarifas:")
        for _, row in df_comparacao.iterrows():
            logger.info(f"  {row['tarifa']}: €{row['custo_total']:.2f}")
        
        # Recomendar tarifa
        tarifa_recomendada, resumo_recomendacao = recomendar_tarifa(df_processado, tarifas)
        logger.info(f"Tarifa recomendada: {tarifa_recomendada.nome}")
        
        # Visualizações
        if not args.no_plot:
            logger.info("Gerando visualizações...")
            visualizador = VisualizadorConsumo(df_processado)
            
            # Criar múltiplos gráficos
            fig = visualizador.criar_multiplos_graficos(
                salvar=args.save_plots,
                caminho=str(output_dir / 'graficos_completos.png') if args.save_plots else None
            )
            
            if not args.save_plots:
                plt.show()
        
        # Exportar dados processados
        logger.info("Exportando dados processados...")
        caminho_saida = output_dir / 'dados_processados.csv'
        df_processado.to_csv(caminho_saida, index=False, encoding='utf-8-sig')
        logger.info(f"Dados exportados para: {caminho_saida}")
        
        # Exportar resumos
        logger.info("Exportando resumos...")
        caminho_resumo = output_dir / 'resumo_consumo.csv'
        consumo_por_mes.to_csv(caminho_resumo, encoding='utf-8-sig')
        logger.info(f"Resumo exportado para: {caminho_resumo}")
        
        # Exportar comparação de tarifas
        caminho_tarifas = output_dir / 'comparacao_tarifas.csv'
        df_comparacao.to_csv(caminho_tarifas, index=False, encoding='utf-8-sig')
        logger.info(f"Comparação de tarifas exportada para: {caminho_tarifas}")
        
        # Relatório final
        logger.info("="*70)
        logger.info("RELATÓRIO FINAL")
        logger.info("="*70)
        logger.info(f"Período: {df_processado['Data'].min()} a {df_processado['Data'].max()}")
        logger.info(f"Consumo total: {estatisticas['total']:.2f} kW")
        logger.info(f"Consumo médio: {estatisticas['media']:.4f} kW")
        
        if 'Custo_EUR' in df_processado.columns:
            custo_total = df_processado['Custo_EUR'].sum()
            logger.info(f"Custo total estimado: €{custo_total:.2f}")
        
        logger.info(f"Tarifa recomendada: {tarifa_recomendada.nome} (€{resumo_recomendacao['custo_total']:.2f})")
        logger.info(f"Classificação de eficiência: {eficiencia.get('classificacao', 'N/A')}")
        logger.info("="*70)
        logger.info("ANÁLISE CONCLUÍDA COM SUCESSO")
        logger.info("="*70)
        
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
