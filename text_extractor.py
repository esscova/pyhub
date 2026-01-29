#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT PARA EXTRAIR TEXTO DE IMAGENS (OCR)

DEPENDENCIES: easyocr
AUTHOR: WELLINGTON M SANTOS
CONTACT: wsantos08@hotmail.com
VERSION: 1.0.0
DESCRIPTION: Ferramenta de CLI para extrair texto de imagens (locais ou URLs),
             com suporte a múltiplos idiomas e exportação do resultado.
"""

# --- Imports ---
import torch
import easyocr
import argparse
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

# --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Data Model ---
@dataclass
class TextBlock:
    """Dataclass para representar um bloco de texto extraído."""
    coordinates: Optional[List[List[int]]] = None
    text: Optional[str] = None
    confidence: Optional[float] = None

# --- Lógica Principal ---

def extrair_texto(filepath: str, language: str) -> List[TextBlock]:
    """
    Extrai texto de uma imagem ou URL usando o EasyOCR.
    Retorna uma lista de objetos TextBlock.
    """
    try:
        if torch.cuda.is_available():
            device = "GPU (CUDA)"
        else:
            device = "CPU"
        logging.info(f"Dispositivo de processamento detectado: {device}")
        
        if not filepath:
            logging.warning('Nenhum arquivo de imagem ou URL fornecido.')
            return []

        logging.info(f"Iniciando leitor com idioma(s): '{language}'")
        reader = easyocr.Reader([language])

        logging.info(f"Lendo texto de: {filepath}")
        result_raw = reader.readtext(filepath)
        
        logging.info(f"Leitura concluída. {len(result_raw)} blocos de texto encontrados.")
        
        extracted_blocks = []
        for coords, text, prob in result_raw:
            block = TextBlock(coordinates=coords, text=text, confidence=prob)
            extracted_blocks.append(block)
            
        return extracted_blocks
  
    except Exception as e:
        logging.error(f"Erro ao ler a imagem: {e}")
        return []

def imprimir_texto(blocos_de_texto: List[TextBlock]):
    """
    Imprime os detalhes de cada bloco de texto extraído no console.
    """
    if not blocos_de_texto:
        logging.warning('Nenhum texto para imprimir.')
        return

    logging.info('--- BLOCOS DE TEXTO DETECTADOS ---')
    for block in blocos_de_texto:
        print(f"Texto: {block.text}")
        print(f"  -> Confiança: {(block.confidence * 100):.2f}%")
        print("-" * 20)
    logging.info('--- FIM DA LISTA DE BLOCOS ---')  

def unificar_texto(blocos_de_texto: List[TextBlock]) -> str:
    """
    Une o texto de todos os blocos em uma única string contínua.
    """
    if not blocos_de_texto:
        logging.warning('Nenhum texto para unificar.')
        return ''
    
    logging.info('Unificando todos os blocos de texto...')
    texto_unificado = " ".join([block.text for block in blocos_de_texto if block.text])
    logging.info('Texto unificado com sucesso.')
    return texto_unificado

def salvar_texto_em_arquivo(texto: str, filename: str):
    """
    Salva o texto unificado em um arquivo de texto (.txt).
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(texto)
        logging.info(f"Texto unificado salvo com sucesso em '{filename}'.")
    except Exception as e:
        logging.error(f"Erro ao salvar o arquivo '{filename}': {e}")

# --- Interface CLI ---

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extrai texto de imagens (locais ou URLs) usando OCR.',
        epilog='Exemplo: python text_extractor.py image.jpg --language en --output resultado.txt'
    )

    # Argumento obrigatório: caminho da imagem
    parser.add_argument('filepath', type=str, help='Caminho para o arquivo de imagem ou URL.')
    
    # Argumentos opcionais
    parser.add_argument('--language', type=str, default='pt', help='Idioma(s) do texto a ser reconhecido (ex: "pt", "en", "pt,en"). Padrão: "pt".')
    parser.add_argument('--output', type=str, help='Nome do arquivo .txt para salvar o texto unificado. Se não fornecido, exibe no console.')

    args = parser.parse_args()

    # --- Fluxo Principal ---
    blocos_extraidos = extrair_texto(args.filepath, args.language)

    if blocos_extraidos:
        imprimir_texto(blocos_extraidos)
        texto_final = unificar_texto(blocos_extraidos)
        
        if args.output:
            salvar_texto_em_arquivo(texto_final, args.output)
        else:
            logging.info('\n--- TEXTO UNIFICADO ---')
            print(texto_final)
            logging.info('------------------------\n')
    
    logging.info("Processo finalizado.")
