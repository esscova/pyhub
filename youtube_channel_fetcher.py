#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT PARA COLETAR ÚLTIMOS VÍDEOS DE UM CANAL DO YOUTUBE

DEPENDENCIES: scrapetube
AUTHOR: WELLINGTON M SANTOS
CONTACT: wsantos08@hotmail.com
VERSION: 1.0.0
DESCRIPTION: Ferramenta de CLI para coletar os últimos vídeos de um canal,
             extraindo metadados e permitindo salvar em um arquivo JSON.
"""

# --- IMPORTS ---
import scrapetube
import logging
import argparse
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

# --- logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- DATA MODEL ---
@dataclass
class Video:
    """Dataclass para representar um vídeo do YouTube."""
    video_id: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    description_snippet: Optional[str] = None
    views: Optional[str] = None
    published_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte o dataclass para um dicionário."""
        return {k: v for k, v in self.__dict__.items()}

# --- FUNCOES ---

def coletar_videos_do_canal(canal_url: str, limit: int) -> Optional[List[Dict[str, Any]]]:
    """
    Coleta a lista de vídeos brutos de um canal usando a biblioteca scrapetube.
    """
    try:
        logging.info(f"Iniciando coleta de vídeos do canal: {canal_url} (limite: {limit})")
        videos_generator = scrapetube.get_channel(channel_url=canal_url, limit=limit)
        lista_de_videos = list(videos_generator)
        logging.info(f"Coleta concluída. {len(lista_de_videos)} vídeos encontrados.")
        return lista_de_videos
    except Exception as e:
        logging.error(f"Erro ao coletar vídeos do canal: {e}\nVerifique a URL e sua conexão.")
        return None

def extrair_dados(dados_brutos: List[Dict[str, Any]]) -> List[Video]:
    """
    Transforma a lista de dicionários brutos em uma lista de objetos Video.
    """
    try:
        logging.info("Iniciando extração e estruturação dos dados...")
       
        lista_de_objetos_video = []
        for video_data in dados_brutos:
            video_obj = Video(
                video_id=video_data.get('videoId'),
                url=f"https://www.youtube.com/watch?v={video_data.get('videoId')}",
                title=video_data.get('title', {}).get('runs', [{}])[0].get('text'),
                description_snippet=video_data.get('descriptionSnippet', {}).get('runs', [{}])[0].get('text', 'N/A'),
                views=video_data.get('viewCountText', {}).get('simpleText', 'N/A'),
                published_at=video_data.get('publishedTimeText', {}).get('simpleText', 'N/A'),
            )
            lista_de_objetos_video.append(video_obj)
        
        logging.info(f"Extração concluída. {len(lista_de_objetos_video)} vídeos processados.")
        return lista_de_objetos_video
    except Exception as e:
        logging.error(f"Erro ao extrair dados dos vídeos: {e}")
        return []

def imprimir_dados(videos: List[Video]):
    """
    Imprime os dados dos vídeos de forma legível no console.
    """
    if not videos:
        logging.warning("Nenhum dado para imprimir.")
        return
        
    logging.info("--- VÍDEOS COLETADOS ---")
    for video in videos:
        print(f"\n▪️Título: {video.title}")
        print(f"▪️URL: {video.url}")
        print(f"▪️Visualizações: {video.views} | Publicado em: {video.published_at}")
        print("")
    logging.info("--- FIM DA LISTA ---\n")

def persistir_json(videos: List[Video], filename: str = 'videos.json'):
    """
    Salva a lista de objetos Video em um arquivo JSON.
    """
    if not videos:
        logging.warning("Nenhum dado para salvar.")
        return

    try:
        logging.info(f"Salvando dados em '{filename}'...")
        dados_para_salvar = [video.to_dict() for video in videos]        
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dados_para_salvar, f, ensure_ascii=False, indent=4)
        logging.info(f"Dados salvos com sucesso em '{filename}'.")
    except Exception as e:
        logging.error(f"Erro ao persistir dados no arquivo '{filename}': {e}")

# --- INTERFACE CLI ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Coleta os últimos vídeos de um canal do YouTube.",
        epilog="Exemplo: python coletor_videos.py https://www.youtube.com/c/canalexemplo --limit 5 --output meus_videos.json"
    )
    
    # ARG: URL do canal
    parser.add_argument("channel_url", type=str, help="URL do canal do YouTube (ex: https://www.youtube.com/c/canalexemplo)")
    
    # ARG OPT: limite de vídeos
    parser.add_argument("--limit", type=int, default=10, help="Número máximo de vídeos a serem coletados. Padrão: 10.")
    # ARG OPT: arquivo de saída
    parser.add_argument("--output", type=str, help="Nome do arquivo JSON para salvar os resultados. Se não fornecido, apenas exibe no console.")
    args = parser.parse_args()

    # --- FLOW ---
    dados_brutos = coletar_videos_do_canal(args.channel_url, args.limit)

    if dados_brutos:
        videos_estruturados = extrair_dados(dados_brutos)

        if videos_estruturados:
            if args.output:
                persistir_json(videos_estruturados, args.output)
            else:
                imprimir_dados(videos_estruturados)
    
    logging.info("Processo finalizado.")
