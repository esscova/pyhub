#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT PARA DETECÇÃO DE OUTLIERS EM ARQUIVOS CSV

DEPENDENCIES: pandas, logging, argparse, typing
AUTHOR: WELLINGTON M SANTOS
CONTACT: wsantos08@hotmail.com
DESCRIPTION: Ferramenta de CLI para detecção de outliers com o método IQR, 
             com suporte a diferentes formatos de arquivo e exportação de resultados.
"""

# --- Imports ---
import pandas as pd
import logging
import argparse
from typing import Optional

# --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )

def carregar_dados(filepath: str, sep: str = ',', encoding: str = 'utf-8') -> Optional[pd.DataFrame]:
    """
    Carrega dados de um arquivo CSV com tratamento de erros específico.
    """
    logging.info(f"Tentando carregar dados do arquivo: {filepath}")
    try:
        dados = pd.read_csv(filepath, sep=sep, encoding=encoding)
        logging.info(f"Dados carregados com sucesso. Shape: {dados.shape}")
        return dados
    except FileNotFoundError:
        logging.error(f"Erro: Arquivo não encontrado em '{filepath}'")
        return None
    except pd.errors.EmptyDataError:
        logging.error(f"Erro: O arquivo '{filepath}' está vazio.")
        return None
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado ao carregar o arquivo: {e}")
        return None

def detectar_outliers(df: pd.DataFrame, multiplier: float = 1.5) -> pd.DataFrame:
    """
    Detecta outliers em colunas numéricas usando o método IQR.
    O multiplicador pode ser ajustado (ex: 1.5 para outliers, 3.0 para outliers extremos).
    """
    resultados = []
    logging.info(f"Iniciando detecção de outliers com multiplicador IQR = {multiplier}...")
    
    colunas_numericas = df.select_dtypes(include='number').columns
    if colunas_numericas.empty: # numbers?
        logging.warning("Nenhuma coluna numérica encontrada no DataFrame.")
        return pd.DataFrame() 

    for col in colunas_numericas:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        limite_inferior = q1 - multiplier * iqr
        limite_superior = q3 + multiplier * iqr

        outliers = df[(df[col] < limite_inferior) | (df[col] > limite_superior)]
        qtd_outliers = len(outliers)
        
        if qtd_outliers > 0:
            perc_outliers = (qtd_outliers / len(df)) * 100
            resultados.append({
                "Coluna": col,
                "Qtd Outliers": qtd_outliers,
                "% Outliers": round(perc_outliers, 2),
                "Limite Inferior": round(limite_inferior, 2),
                "Limite Superior": round(limite_superior, 2),
                "Indices": list(outliers.index)
            })
            
    logging.info("Detecção de outliers concluída.")
    return pd.DataFrame(resultados)

def salvar_resultados(df_resultados: pd.DataFrame, output_path: str):
    """Salva o DataFrame de resultados em um arquivo CSV."""
    try:
        df_resultados.to_csv(output_path, index=False)
        logging.info(f"Resultados salvos com sucesso em '{output_path}'")
    except Exception as e:
        logging.error(f"Erro ao salvar os resultados: {e}")

# --- Interface de Linha de Comando (CLI) ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Detecta outliers em um arquivo CSV usando o método IQR.",
        epilog="Exemplo: python detect_outliers.py dados.csv --output resultados.csv --sep ';'"
    )
    
    # Argumento posicional (obrigatório)
    parser.add_argument("filepath", help="Caminho para o arquivo de dados (CSV).")
    
    # Argumentos opcionais com valores padrão
    parser.add_argument("--sep", default=",", help="Separador de colunas do arquivo CSV. Padrão: ','.")
    parser.add_argument("--encoding", default="utf-8", help="Codificação do arquivo. Padrão: 'utf-8'.")
    parser.add_argument("--multiplier", type=float, default=1.5, help="Multiplicador do IQR (ex: 1.5 ou 3.0). Padrão: 1.5.")
    parser.add_argument("--output", help="Caminho para salvar o arquivo de resultados (CSV). Se não for fornecido, exibe no console.")

    args = parser.parse_args()
    df = carregar_dados(args.filepath, sep=args.sep, encoding=args.encoding)

    if df is not None:
        resultados_df = detectar_outliers(df, multiplier=args.multiplier)

        if not resultados_df.empty:
            if args.output:
                salvar_resultados(resultados_df, args.output)
            else:
                logging.info("--- RESULTADOS DA DETECÇÃO DE OUTLIERS ---")
                print(resultados_df.to_string())
                logging.info("-----------------------------------------")
        else:
            logging.info("Nenhum outlier foi encontrado nas colunas numéricas.")
    
    logging.info("Processo finalizado.")
