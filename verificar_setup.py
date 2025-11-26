#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificação rápida do ambiente e configurações.
Execute antes de iniciar o processamento.
"""

import os
import sys

def verificar_variaveis_ambiente():
    """Verifica variáveis de ambiente necessárias"""
    print("="*60)
    print("VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE")
    print("="*60)
    
    variaveis = {
        "MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT"),
        "MINIO_ACCESS_KEY": os.getenv("MINIO_ACCESS_KEY"),
        "MINIO_SECRET_KEY": os.getenv("MINIO_SECRET_KEY"),
        "MINIO_BUCKET": os.getenv("MINIO_BUCKET", "enderecos")
    }
    
    todas_ok = True
    for var, valor in variaveis.items():
        if valor:
            if "SECRET" in var:
                print(f"✓ {var}: {'*' * len(valor)}")
            else:
                print(f"✓ {var}: {valor}")
        else:
            print(f"✗ {var}: NÃO CONFIGURADO")
            todas_ok = False
    
    return todas_ok

def verificar_arquivos_csv():
    """Verifica se os arquivos CSV existem"""
    print("\n" + "="*60)
    print("VERIFICAÇÃO DE ARQUIVOS CSV")
    print("="*60)
    
    path_base = "./dados-exemplo/bronze"
    arquivos = [
        "enderecos_livres.csv",
        "enderecos_com_erros.csv",
        "dne.csv",
        "cnefe.csv",
        "osm.csv",
        "dados_geograficos.csv",
        "variacoes_enderecos.csv"
    ]
    
    todas_ok = True
    for arquivo in arquivos:
        caminho = os.path.join(path_base, arquivo)
        if os.path.exists(caminho):
            tamanho = os.path.getsize(caminho)
            print(f"✓ {arquivo} ({tamanho:,} bytes)")
        else:
            print(f"✗ {arquivo}: NÃO ENCONTRADO")
            todas_ok = False
    
    return todas_ok

def verificar_notebooks():
    """Verifica se os notebooks existem"""
    print("\n" + "="*60)
    print("VERIFICAÇÃO DE NOTEBOOKS")
    print("="*60)
    
    notebooks = [
        "00_configuracao_inicial.ipynb",
        "00_carregar_dados_exemplo.ipynb",
        "01_tratamento_inicial_ner.ipynb",
        "02_normalizacao_camada_prata.ipynb",
        "03_camada_ouro_deduplicacao.ipynb",
        "04_clusterizacao.ipynb",
        "05_motor_correspondencia.ipynb",
        "06_validacao_geografica.ipynb",
        "07_analise_resultados.ipynb"
    ]
    
    todas_ok = True
    for notebook in notebooks:
        if os.path.exists(notebook):
            print(f"✓ {notebook}")
        else:
            print(f"✗ {notebook}: NÃO ENCONTRADO")
            todas_ok = False
    
    return todas_ok

def verificar_python():
    """Verifica versão do Python"""
    print("\n" + "="*60)
    print("VERIFICAÇÃO DO PYTHON")
    print("="*60)
    
    versao = sys.version_info
    print(f"Python {versao.major}.{versao.minor}.{versao.micro}")
    
    if versao.major >= 3 and versao.minor >= 7:
        print("✓ Versão compatível")
        return True
    else:
        print("✗ Versão incompatível (requer Python 3.7+)")
        return False

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("VERIFICAÇÃO DE SETUP - MOTOR DE CORRESPONDÊNCIA")
    print("="*60)
    print()
    
    resultados = {
        "Variáveis de Ambiente": verificar_variaveis_ambiente(),
        "Arquivos CSV": verificar_arquivos_csv(),
        "Notebooks": verificar_notebooks(),
        "Python": verificar_python()
    }
    
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    
    todas_ok = True
    for item, status in resultados.items():
        simbolo = "✓" if status else "✗"
        print(f"{simbolo} {item}")
        if not status:
            todas_ok = False
    
    print("="*60)
    
    if todas_ok:
        print("\n✓ Tudo pronto! Você pode iniciar o processamento.")
        print("\nPróximos passos:")
        print("  1. Abra o Jupyter Notebook")
        print("  2. Execute: 00_configuracao_inicial.ipynb")
        print("  3. Execute: 00_carregar_dados_exemplo.ipynb")
        print("  4. Siga o GUIA_PASSO_A_PASSO.md")
        return 0
    else:
        print("\n✗ Alguns itens precisam ser corrigidos antes de continuar.")
        print("\nConsulte o GUIA_PASSO_A_PASSO.md para mais detalhes.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
