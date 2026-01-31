#!/usr/bin/env python3
"""Script para validação de dados de consumo de eletricidade."""

import sys
from pathlib import Path
import argparse

# Adicionar diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import setup_logging, carregar_config, validar_diretorio
from src.data_loader import CarregadorDados
from src.data_processor import ValidadorDados


def main():
    """Função principal para validação de dados."""
    parser = argparse.ArgumentParser(
        description='Validação de dados de consumo de eletricidade'
    )
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Diretório com os ficheiros CSV de dados'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Nível de logging'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Tentar corrigir problemas encontrados'
    )
    args = parser.parse_args()
    
    # Configurar logging
    logger = setup_logging(log_level=args.log_level)
    logger.info("="*70)
    logger.info("VALIDAÇÃO DE DADOS DE CONSUMO DE ELETRICIDADE")
    logger.info("="*70)
    
    try:
        # Validar diretório
        data_dir = validar_diretorio(args.data_dir, criar=False)
        
        # Carregar dados
        logger.info("Carregando dados...")
        carregador = CarregadorDados(str(data_dir))
        df_completo = carregador.carregar_todos()
        
        if len(df_completo) == 0:
            logger.error("Nenhum dado foi carregado")
            return 1
        
        # Filtrar dados reais
        df_real = carregador.filtrar_estado(df_completo, estado='Real')
        
        # Validar qualidade
        logger.info("Validando qualidade dos dados...")
        validador = ValidadorDados(df_real)
        relatorio = validador.validar()
        
        # Mostrar resultados
        logger.info("\n" + "="*70)
        logger.info("RELATÓRIO DE VALIDAÇÃO")
        logger.info("="*70)
        
        # Estatísticas
        if 'estatisticas' in relatorio and relatorio['estatisticas']:
            est = relatorio['estatisticas']
            logger.info(f"\nEstatísticas:")
            logger.info(f"  Registros totais: {est['total_registros']}")
            logger.info(f"  Registros válidos: {est['registros_validos']}")
            logger.info(f"  Média: {est['media']:.4f} kW")
            logger.info(f"  Mediana: {est['mediana']:.4f} kW")
            logger.info(f"  Desvio padrão: {est['desvio_padrao']:.4f} kW")
            logger.info(f"  Mínimo: {est['minimo']:.4f} kW")
            logger.info(f"  Máximo: {est['maximo']:.4f} kW")
        
        # Problemas encontrados
        if 'valores_anomalos' in relatorio and relatorio['valores_anomalos']:
            logger.info(f"\nValores anómalos: {len(relatorio['valores_anomalos'])}")
            for problema in relatorio['valores_anomalos']:
                logger.info(f"\n  Tipo: {problema['tipo']}")
                if problema['tipo'] == 'valores_negativos':
                    logger.info(f"    Quantidade: {problema['quantidade']}")
                elif problema['tipo'] == 'valores_nulos':
                    logger.info(f"    Colunas com nulos: {list(problema['colunas'].keys())}")
                elif problema['tipo'] == 'outliers':
                    logger.info(f"    Quantidade: {problema['quantidade']}")
                    logger.info(f"    Percentual: {problema['percentual']:.2f}%")
                    logger.info(f"    Máximo: {problema['maximo']:.4f} kW")
        
        # Inconsistências temporais
        if 'inconsistencias_temporais' in relatorio and relatorio['inconsistencias_temporais']:
            logger.info(f"\nInconsistências temporais: {len(relatorio['inconsistencias_temporais'])}")
            for problema in relatorio['inconsistencias_temporais']:
                logger.info(f"\n  Tipo: {problema['tipo']}")
                if problema['tipo'] == 'lacunas_temporais':
                    logger.info(f"    Quantidade: {problema['quantidade']}")
                    logger.info(f"    Máxima: {problema['maxima']}")
        
        # Resumo
        total_problemas = (
            len(relatorio.get('valores_anomalos', [])) +
            len(relatorio.get('inconsistencias_temporais', []))
        )
        
        logger.info("\n" + "="*70)
        if total_problemas == 0:
            logger.info("✓ Nenhum problema encontrado nos dados!")
        else:
            logger.warning(f"⚠️  Encontrados {total_problemas} problema(s) nos dados")
            if not args.fix:
                logger.info("\nPara tentar corrigir problemas, execute:")
                logger.info("  python scripts/validate_data.py --fix")
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
