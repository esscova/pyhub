"""
Script para extrair transcrições de vídeos do YouTube

Dependências:
  - youtube_transcript_api
  - typing

"""

# DEPENDENCIAS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from typing import Optional

# FUNÇÃO COLETAR ID DO VIDEO
def get_video_id(url: str) -> Optional[str]:
    """
    Extrai o ID do vídeo de uma URL do YouTube

    Args:
        url: URL do vídeo do YouTube

    Returns:
        video_id ou None se inválido
    """
    try:
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
        elif "v=" in url:
            video_id = url.split("v=")[1].split("&")[0].split("?")[0]
        else:
            return None

        if len(video_id) == 11: # id tem 11 carcteres?
            return video_id
        return None

    except Exception:
        return None

# FUNÇÃO COLETAR TRANSCRIÇÃO
def get_transcript(video_id:str, languages:list[str]=["pt", "pt-BR", "en", "en-US"]) -> str|None:
  """
  Obtém a transcrição de um vídeo do YouTube.
  """
  try:
    result = YouTubeTranscriptApi().fetch(video_id, languages=languages)
    formatter = TextFormatter()
    transcript = formatter.format_transcript(result)
    # transcript = transcript.replace("\n", " ")

  except Exception as e:
    print(f"Error fetching transcript: {str(e)}")
    transcript = None

  return transcript
  
# FUNÇÃO PARA PERSISTIR TRANSCRIÇÃO
def save_transcript(transcript:str, filename:str = 'transcricao.txt') -> None:
  with open(filename, 'w', encoding='utf-8') as f:
    f.write(transcript)

# MAIN
def main():
  url = input("Digite a URL do vídeo do YouTube: ")
  video_id = get_video_id(url)

  if not video_id:
    print("URL inválida.")
  else:
    transcript = get_transcript(video_id)
    if transcript:
      print(f'\nTranscrição\n{transcript[:100]}\n...')
      save_transcript(transcript)
      print("\n=== Transcrição salva com sucesso! ===")
    else:
      print("Não foi possível obter a transcrição.")

if __name__ == "__main__":
  main()
