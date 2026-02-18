#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Raspa os posts recentes do TabNews via RSS.
AUTHOR: WELLINGTON M SANTOS
CONTACT: wsantos08@hotmail.com
USO: python tabnews_scraper.py [--output posts.json]
DESCRIPTION: Ferramenta CLI para extrair feed tabnews e persistir em formato JSON.
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from typing import List
from urllib.request import urlopen, Request
from urllib.error import URLError
import xml.etree.ElementTree as ET

# --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Constantes ---
RSS_URL = 'https://www.tabnews.com.br/recentes/rss'
RSS_NAMESPACE = 'http://purl.org/rss/1.0/modules/content/'


# --- Helpers ---

class _HTMLStripper(HTMLParser):
    """Remove tags HTML e retorna texto puro."""
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str):
        self._parts.append(data)

    def get_text(self) -> str:
        return '\n'.join(
            line for line in
            (' '.join(self._parts).splitlines())
            if line.strip()
        )


def _strip_html(html: str) -> str:
    stripper = _HTMLStripper()
    stripper.feed(html)
    return stripper.get_text()


def _extract_author(url: str) -> str:
    """Extrai o autor a partir da URL do post (ex: tabnews.com.br/autor/slug)."""
    try:
        return url.rstrip('/').split('/')[-2]
    except IndexError:
        return 'desconhecido'


# --- Model ---

@dataclass
class Post:
    """Representa um post extraído do TabNews."""
    url: str
    autor: str
    titulo: str
    conteudo: str


# --- Lógica Principal ---

def fetch_rss() -> bytes:
    """Faz o download do feed RSS."""
    req = Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.read()
    except URLError as e:
        logging.error(f"Falha ao baixar o RSS: {e}")
        sys.exit(1)


def parse_posts(rss_data: bytes) -> List[Post]:
    """Parseia o XML do RSS e retorna a lista de posts."""
    root = ET.fromstring(rss_data)
    channel = root.find('channel')
    if channel is None:
        logging.error("Feed RSS inválido: elemento <channel> não encontrado.")
        sys.exit(1)

    posts: List[Post] = []
    for item in channel.findall('item'):
        url   = (item.findtext('link') or '').strip()
        titulo = (item.findtext('title') or 'N/A').strip()
        autor  = _extract_author(url)

        # content:encoded (post completo); fallback para description (resumo)
        conteudo_html = (
            item.findtext(f'{{{RSS_NAMESPACE}}}encoded')
            or item.findtext('description')
            or ''
        )
        conteudo = _strip_html(conteudo_html) if conteudo_html else 'N/A'

        posts.append(Post(url=url, autor=autor, titulo=titulo, conteudo=conteudo))

    return posts


def save_to_json(posts: List[Post], filename: str):
    """Salva a lista de posts em um arquivo JSON."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([asdict(p) for p in posts], f, ensure_ascii=False, indent=2)
        logging.info(f"Dados salvos em '{filename}'.")
    except IOError as e:
        logging.error(f"Erro ao salvar '{filename}': {e}")


# --- CLI ---

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Raspa os posts recentes do TabNews via RSS.',
        epilog='Exemplo: python tabnews_scraper.py --output posts.json'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Arquivo .json para salvar os resultados. Se omitido, imprime resumo no terminal.'
    )
    args = parser.parse_args()

    logging.info("Buscando feed RSS do TabNews...")
    rss_data = fetch_rss()
    posts = parse_posts(rss_data)

    if not posts:
        logging.warning("Nenhum post encontrado no feed.")
        sys.exit(0)

    logging.info(f"{len(posts)} posts obtidos com sucesso.")

    if args.output:
        save_to_json(posts, args.output)
    else:
        print("\n--- POSTS RECENTES ---")
        for post in posts:
            print(f"Título : {post.titulo}")
            print(f"  Autor : {post.autor}")
            print(f"  URL   : {post.url}")
            print("-" * 40)
