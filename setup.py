#!/usr/bin/env python3
"""Script de setup para o projeto Análise de Consumo de Eletricidade."""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Executa um comando e mostra o resultado."""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}")
    print(f"Comando: {cmd}")
    print("-"*70)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ {description} concluído com sucesso!")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"✗ Erro ao executar {description}")
        print(result.stderr)
        return False
    
    return True


def main():
    """Função principal de setup."""
    print("="*70)
    print("SETUP DO PROJETO - ANÁLISE DE CONSUMO DE ELETRICIDADE")
    print("="*70)
    
    # Verificar Python
    print("\nVerificando versão do Python...")
    python_version = sys.version_info
    print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("✗ Python 3.8 ou superior é necessário")
        return 1
    
    # Criar estrutura de diretórios
    print("\nCriando estrutura de diretórios...")
    dirs_to_create = [
        'data',
        'processed',
        'reports',
        'reports/mensal',
        'reports/anual',
        'cache',
        'logs',
        'tests',
        'scripts',
        'config',
        'docs',
        'src'
    ]
    
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_name}/")
    
    # Criar ficheiros .gitkeep
    print("\nCriando ficheiros .gitkeep...")
    gitkeep_dirs = ['data', 'cache', 'tests', 'scripts', 'config', 'docs']
    for dir_name in gitkeep_dirs:
        gitkeep_file = Path(dir_name) / '.gitkeep'
        if not gitkeep_file.exists():
            gitkeep_file.touch()
            print(f"  ✓ {gitkeep_file}")
    
    # Instalar dependências
    print("\nInstalando dependências...")
    if not run_command(
        "pip install -r requirements.txt",
        "Instalação de dependências"
    ):
        print("\n⚠️  Houve erros na instalação de dependências.")
        print("   Tente instalar manualmente: pip install -r requirements.txt")
        return 1
    
    # Verificar instalação de pacotes principais
    print("\nVerificando pacotes instalados...")
    packages = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'scipy', 'yaml']
    
    for package in packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - não instalado")
            return 1
    
    # Criar ficheiro de configuração local (opcional)
    print("\nCriando ficheiro de configuração local...")
    local_config = Path('config/local.yaml')
    if not local_config.exists():
        local_config.write_text("# Configurações locais (sobrescrevem config.yaml)\n")
        print(f"  ✓ {local_config}")
    
    # Informações finais
    print("\n" + "="*70)
    print("SETUP CONCLUÍDO COM SUCESSO!")
    print("="*70)
    print("\nPróximos passos:")
    print("  1. Coloque os ficheiros CSV de consumo na pasta 'data/'")
    print("  2. Execute a análise:")
    print("     python scripts/run_analysis.py")
    print("  3. Ou use o notebook Jupyter:")
    print("     jupyter notebook")
    print("\nPara mais informações, consulte o README.md")
    print("="*70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
