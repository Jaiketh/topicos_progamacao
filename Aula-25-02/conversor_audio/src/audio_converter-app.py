from pydub import AudioSegment
import os

def convert_opus_to_mp3(input_file, output_file):
    try:
        # Carrega o arquivo OPUS
        audio = AudioSegment.from_file(input_file, format="opus")
        
        # Exporta o arquivo no formato MP3
        audio.export(output_file, format="mp3")
        print(f"Arquivo convertido com sucesso: {output_file}")
    except Exception as e:
        print(f"Erro ao converter o arquivo: {e}")

def main():
    print("Conversor de Áudio - OPUS para MP3")
    input_path = input("Digite o caminho do arquivo OPUS: ").strip()
    output_path = input("Digite o caminho para salvar o arquivo MP3: ").strip()

    if not os.path.exists(input_path):
        print("O arquivo de entrada não existe.")
        return

    convert_opus_to_mp3(input_path, output_path)

if __name__ == "__main__":
    main()