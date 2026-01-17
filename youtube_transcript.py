"""
Script para extrair transcrições de vídeos do YouTube

Dependências:
  - youtube_transcript_api

"""

# DEPENDENCIAS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# FUNÇÃO COLETAR ID DO VIDEO
def get_video_id(url:str) -> str|None:
  """
  Obtém o ID do vídeo a partir de uma URL do YouTube.
  """
  if 'youtu.be' in url:
    return url.split('/')[-1].split('?')[0]
  elif 'v=' in url:
    return url.split('v=')[1]
  else:
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
