#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AUTOR: WELLINGTON M SANTOS
CONTATO: wsantos08@hotmail.com
DESCRICAO: Calcula retornos nominais e acumulados de ações via Yahoo Finance.
DEPENDENCIAS: pandas, yfinance
USO: python stock_returns.py PETR4.SA --start 2025-01-01 --end 2026-01-01
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

# --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Constantes ---
DEFAULT_PERIOD_DAYS = 365


# --- Helpers ---

def _parse_date(date_str: str) -> datetime:
    """Converte string YYYY-MM-DD para datetime."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        logging.error(f"Data inválida '{date_str}'. Use formato YYYY-MM-DD.")
        sys.exit(1)


def _validate_ticker(ticker: str) -> str:
    """Adiciona sufixo .SA se necessário para ações BR."""
    ticker = ticker.upper().strip()
    if not ticker:
        logging.error("Ticker vazio.")
        sys.exit(1)
    # .SA se parecer código brasileiro sem sufixo
    if len(ticker) <= 6 and ticker[-2:] not in ['.SA', '.US']:
        ticker += '.SA'
    return ticker


# --- Lógica Principal ---

def fetch_stock_data(ticker: str, start: datetime, end: datetime) -> pd.DataFrame:
    """Baixa dados históricos do Yahoo Finance."""
    logging.info(f"Buscando dados de {ticker} ({start.date()} a {end.date()})...")
    try:
        dados = yf.download(
            ticker,
            start=start.strftime('%Y-%m-%d'),
            end=end.strftime('%Y-%m-%d'),
            auto_adjust=False,
            progress=False
        )
        if dados.empty:
            logging.error(f"Nenhum dado encontrado para '{ticker}'. Verifique o símbolo.")
            sys.exit(1)
        return dados
    except Exception as e:
        logging.error(f"Erro ao buscar dados: {e}")
        sys.exit(1)


def calculate_returns(dados: pd.DataFrame) -> dict:
    """Calcula retornos nominal e acumulado."""
    precos = dados['Adj Close']
    
    preco_inicial = precos.iloc[0]
    preco_final = precos.iloc[-1]
    if isinstance(preco_inicial, pd.Series):
        preco_inicial = float(preco_inicial.iloc[0])
    else:
        preco_inicial = float(preco_inicial)
    if isinstance(preco_final, pd.Series):
        preco_final = float(preco_final.iloc[0])
    else:
        preco_final = float(preco_final)
    
    data_inicial = precos.index[0].date()
    data_final = precos.index[-1].date()
    
    retorno_nominal = (preco_final / preco_inicial) - 1
    retorno_diario = precos.pct_change()
    retorno_acumulado = (1 + retorno_diario).cumprod() - 1
    
    return {
        'preco_inicial': preco_inicial,
        'preco_final': preco_final,
        'data_inicial': data_inicial,
        'data_final': data_final,
        'retorno_nominal': retorno_nominal,
        'retorno_acumulado': retorno_acumulado
    }


def display_results(ticker: str, results: dict, tail_days: int = 5):
    """Imprime resultados formatados no terminal."""
    print(f"\n{'='*60}")
    print(f"Análise de Retorno: {ticker}")
    print(f"{'='*60}")
    print(f"Preço Inicial ({results['data_inicial']}): R$ {results['preco_inicial']:.2f}")
    print(f"Preço Final   ({results['data_final']}): R$ {results['preco_final']:.2f}")
    print(f"Retorno Nominal Total: {results['retorno_nominal']:.2%}")
    print(f"\nRetorno Acumulado (últimos {tail_days} dias):")
    print("-" * 60)
    
    tail = results['retorno_acumulado'].tail(tail_days)
    for idx in tail.index:
        date = idx.date() if hasattr(idx, 'date') else idx
        value = tail.loc[idx]

        if isinstance(value, pd.Series):
            value = float(value.iloc[0])
        print(f"{date}: {value:.2%}")
    
    print(f"{'='*60}\n")


def save_to_csv(dados: pd.DataFrame, ticker: str, output: str):
    """Salva dados completos em CSV."""
    try:
        # add coluna de retorno acumulado
        dados_export = dados.copy()
        retorno_diario = dados_export['Adj Close'].pct_change()
        dados_export['Retorno Acumulado'] = (1 + retorno_diario).cumprod() - 1
        
        dados_export.to_csv(output)
        logging.info(f"Dados salvos em '{output}'.")
    except IOError as e:
        logging.error(f"Erro ao salvar CSV: {e}")


# --- CLI ---

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Calcula retornos de ações via Yahoo Finance.',
        epilog='Exemplo: python stock_returns.py PETR4 --start 2025-01-01 --end 2026-01-01'
    )
    
    parser.add_argument(
        'ticker',
        type=str,
        help='Código da ação (ex: PETR4, VALE3). Sufixo .SA é adicionado automaticamente.'
    )
    parser.add_argument(
        '--start',
        type=str,
        help='Data inicial no formato YYYY-MM-DD. Padrão: 365 dias atrás.'
    )
    parser.add_argument(
        '--end',
        type=str,
        help='Data final no formato YYYY-MM-DD. Padrão: hoje.'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Arquivo CSV para salvar dados históricos completos.'
    )
    parser.add_argument(
        '--tail',
        type=int,
        default=5,
        help='Número de dias a exibir no retorno acumulado. Padrão: 5.'
    )
    
    args = parser.parse_args()
    
    # datas
    end = _parse_date(args.end) if args.end else datetime.now()
    start = _parse_date(args.start) if args.start else end - timedelta(days=DEFAULT_PERIOD_DAYS)
    
    if start >= end:
        logging.error("Data inicial deve ser anterior à data final.")
        sys.exit(1)
    
    # ticker
    ticker = _validate_ticker(args.ticker)
    
    # análise
    dados = fetch_stock_data(ticker, start, end)
    results = calculate_returns(dados)
    display_results(ticker, results, args.tail)
    
    # CSV 
    if args.output:
        save_to_csv(dados, ticker, args.output)
