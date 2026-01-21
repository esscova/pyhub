#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT PARA EXTRAIR METADADOS DE VÍDEOS DO YOUTUBE

AUTHOR: WELLINGTON M SANTOS
CONTACT: wsantos08@hotmail.com
DESCRIPTION: Extrator robusto de metadados com type safety e tratamento de erros
DEPENDENCIES: yt-dlp, typing, datetime, dataclasses, logging
"""

# --- Imports ---
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError
import logging
from datetime import datetime
from typing import Optional, List, Any, Dict
from dataclasses import dataclass

#   --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Data Models ---

@dataclass
class YouTubeMetadata:
    """
    Contêiner de metadados de vídeo do YouTube usando dataclass para tipagem forte.
    """
    success: bool
    error: Optional[str] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    channel_url: Optional[str] = None
    channel_follower_count: Optional[int] = None
    video_original_url: Optional[str] = None
    video_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    upload_date: Optional[datetime] = None
    duration: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    language: Optional[str] = None
    uploader: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte o dataclass para um dicionário, formatando datetime para string ISO."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result

# --- Lógica Principal ---

def get_video_data(url: str) -> YouTubeMetadata:
    """
    Obtém informações detalhadas do vídeo usando yt-dlp.
    Retorna um dataclass YouTubeMetadata com os dados ou o erro.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=False)

        if not data:
            logging.warning("Nenhum dado foi retornado pelo yt-dlp. O vídeo pode ser privado ou inexistente.")
            return YouTubeMetadata(success=False, error="Nenhum dado encontrado para a URL fornecida.")

        # parsing data de upload
        upload_date_str = data.get('upload_date')
        upload_date_obj = datetime.strptime(upload_date_str, "%Y%m%d") if upload_date_str else None

        logging.info(f"Dados brutos extraídos com sucesso para o vídeo ID: {data.get('id')}")

        return YouTubeMetadata(
            success=True,
            channel=data.get('channel'),
            channel_id=data.get('channel_id'),
            channel_url=data.get('channel_url'),
            channel_follower_count=data.get('channel_follower_count'),
            video_original_url=data.get('webpage_url'), 
            video_id=data.get('id'),
            thumbnail_url=data.get("thumbnail"),
            upload_date=upload_date_obj,
            duration=data.get('duration_string'),
            title=data.get('title'),
            description=data.get('description'),
            view_count=data.get('view_count'),
            like_count=data.get('like_count'),
            comment_count=data.get('comment_count'),
            categories=data.get('categories'),
            tags=data.get('tags'),
            language=data.get('language'),
            uploader=data.get('uploader')
        )

    except DownloadError as e:
        logging.error(f"Erro de download ou URL inválida: {e}")
        return YouTubeMetadata(success=False, error=f"Erro de download: URL inválida ou vídeo não acessível.")
    
    except ExtractorError as e:
        logging.error(f"Erro do extrator de dados: {e}")
        return YouTubeMetadata(success=False, error=f"Erro de extração: não foi possível processar as informações do vídeo.")

    except Exception as e:
        logging.critical(f"Ocorreu um erro inesperado: {e}", exc_info=True)
        return YouTubeMetadata(success=False, error=f"Erro inesperado no servidor.")

def display_metadata(metadata: YouTubeMetadata):
    """
    Exibe os metadados de forma organizada usando o módulo logging.
    """
    if not metadata.success:
        logging.error("A extração de metadados falhou. Verifique os logs de erro acima.")
        return

    logging.info("--- METADADOS DO VÍDEO EXTRAÍDOS COM SUCESSO ---")
    metadata_dict = metadata.to_dict()    
    metadata_dict.pop('success', None)
    
    for key, value in metadata_dict.items():
        formatted_key = key.replace('_', ' ').title()
        logging.info(f"{formatted_key}: {value}")
    logging.info("---" * 10)

# --- Interface de Linha de Comando (CLI) ---

if __name__ == "__main__":
    logging.info("Script iniciado. Aguardando a URL do usuário.")
    video_url = input("Digite a URL do vídeo do YouTube: ")
    
    if not video_url.strip():
        logging.error("Nenhuma URL foi fornecida. Abortando.")
    else:
        logging.info(f"Iniciando extração para a URL: {video_url}")
        
        video_metadata = get_video_data(video_url)
        display_metadata(video_metadata)
        
        logging.info("Processo finalizado.")
        