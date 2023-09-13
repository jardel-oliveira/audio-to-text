import os

import ffmpeg
import speech_recognition as sr
from pydub import AudioSegment


def audio_para_wav(arquivo_entrada):
    """Converte um arquivo de áudio em .mp3, .opus ou .ogg para .wav.

    Args:
        arquivo_entrada (str): O caminho do arquivo de áudio de entrada.

    Returns:
        str: O caminho do arquivo .wav convertido.
    """
    formato = os.path.splitext(arquivo_entrada)[1]
    if formato in (".mp3", ".opus", ".ogg"):
        arquivo_wav = arquivo_entrada.replace(formato, ".wav")
        audio = AudioSegment.from_file(arquivo_entrada)
        audio.export(arquivo_wav, format="wav")
        return arquivo_wav
    else:
        raise ValueError("Formato de arquivo não suportado.")


def dividir_audio(arquivo_entrada, duracao_limite=60):
    """Divide um arquivo de áudio em partes de 1 minuto.

    Args:
        arquivo_entrada (str): O caminho do arquivo de áudio de entrada.
        duracao_limite (int): Duração máxima de cada parte em segundos.

    Returns:
        list: Lista de caminhos dos arquivos de áudio divididos.
    """
    partes = []
    audio = AudioSegment.from_file(arquivo_entrada)
    duracao_total = len(audio) / 1000  # Duração total em segundos

    inicio = 0
    numero_parte = 1
    while inicio < duracao_total:
        fim = min(inicio + duracao_limite, duracao_total)
        parte = audio[inicio * 1000 : fim * 1000]
        arquivo_parte = f"parte_{numero_parte}.wav"
        parte.export(arquivo_parte, format="wav")
        partes.append(arquivo_parte)
        inicio += duracao_limite
        numero_parte += 1

    return partes


def audio_para_texto(arquivo):
    recognizer = sr.Recognizer()

    with sr.AudioFile(arquivo) as source:
        audio = recognizer.record(source)

    try:
        transcript = recognizer.recognize_google(audio, language="pt-BR")
        return transcript
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Falha ao fazer a requisição ao serviço de reconhecimento de fala: {e}")
        return ""


def transcrever_partes(partes):
    texto_completo = ""

    for parte_wav in partes:
        parte_texto = audio_para_texto(parte_wav)

        if parte_texto:
            texto_completo += parte_texto + " "

    return texto_completo


if __name__ == "__main__":
    arquivo_entrada = (
        "/content/seu_audio.mp3"  # Substitua pelo caminho do seu arquivo de áudio
    )
    duracao_limite = 60  # Duração limite de cada parte em segundos

    try:
        arquivo_wav = audio_para_wav(arquivo_entrada)
        partes_wav = dividir_audio(arquivo_wav, duracao_limite)
        print("Áudio dividido e convertido para .wav:")
        for parte in partes_wav:
            print(parte)

        texto_transcrito = transcrever_partes(partes_wav)

        if texto_transcrito:
            with open("texto_convertido.txt", "a") as file:
                file.write(texto_transcrito)

            print("Texto transcrito salvo em texto_convertido.txt")
        else:
            print("Não foi possível transcrever o áudio.")

    except Exception as e:
        print(f"Erro: {e}")
