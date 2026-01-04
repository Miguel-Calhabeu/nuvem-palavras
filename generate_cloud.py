import numpy as np
from PIL import Image
from wordcloud import WordCloud
import argparse
import sys
import os

def create_cloud(text_file, mask_file, color_code, font_path, max_words=400, min_font_size=10, max_font_size=None, min_word_length=0, prefer_horizontal=0.9):
    # 1. Carregar e Processar a Máscara
    try:
        # Carregar imagem
        img_raw = Image.open(mask_file)
        
        # ... (rest of image processing logic remains same, just inside try block)

        # Converter para RGB se for RGBA (lidar com transparência assumindo fundo branco)
        if img_raw.mode == 'RGBA':
            background = Image.new("RGB", img_raw.size, (255, 255, 255))
            background.paste(img_raw, mask=img_raw.split()[3])
            img_raw = background

        # Converter para escala de cinza
        mask_image = np.array(img_raw.convert("L"))

        # Binarizar a máscara para garantir que apenas 0 e 255 existam
        # 255 é a área ignorada (fundo), 0 é a área desenhável (forma)
        mask_image = np.where(mask_image > 128, 255, 0)

    except FileNotFoundError:
        print(f"Erro: Arquivo de máscara '{mask_file}' não encontrado.")
        raise
    except Exception as e:
        print(f"Erro ao processar a máscara: {e}")
        raise

    # 2. Ler o arquivo de texto
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            base_text = f.read()
            # Repetir texto para garantir preenchimento, se curto
            text_data = base_text * 500
    except FileNotFoundError:
        print(f"Erro: Arquivo de texto '{text_file}' não encontrado.")
        raise

    # 3. Configurar o Gerador
    # Verifica se a fonte existe, senão avisa (mas WordCloud pode tentar default se None, 
    # porém o user passou path explícito, melhor falhar ou avisar)
    if not os.path.exists(font_path):
         print(f"Aviso: Fonte '{font_path}' não encontrada. O sistema tentará usar a padrão ou falhará.")

    wc = WordCloud(
        background_color="white",
        mask=mask_image,               # A forma do objeto
        contour_width=0,               # Sem contorno extra
        contour_color='black',
        max_words=max_words,           # Parametro customizavel
        min_font_size=min_font_size,   # Parametro customizavel
        max_font_size=max_font_size,   # Parametro customizavel
        min_word_length=min_word_length, # Parametro customizavel
        stopwords=[],                  # Lista de stopwords se necessário
        repeat=True,                   # Repetir palavras para preencher
        collocations=False,            # Palavras soltas
        prefer_horizontal=prefer_horizontal, # Parametro customizavel
        font_path=font_path,           # Caminho da fonte
        color_func=lambda *args, **kwargs: color_code # Força a cor passada
    )
    # 4. Geração
    print("Gerando nuvem de palavras...")
    wc.generate(text_data)

    return wc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador de Nuvem de Palavras CLI")
    parser.add_argument("text_file", help="Caminho para o arquivo de texto (.txt)")
    parser.add_argument("mask_file", help="Caminho para a imagem de máscara (.png)")
    parser.add_argument("color_code", help="Código de cor HSL (ex: 'hsl(0, 0%, 0%)')")
    parser.add_argument("font_path", help="Caminho para o arquivo de fonte (.ttf)")

    args = parser.parse_args()

    try:
        wc = create_cloud(args.text_file, args.mask_file, args.color_code, args.font_path)
        # 5. Exportação
        output_file = "resultado.png"
        wc.to_file(output_file)
        print(f"Nuvem de palavras salva em '{output_file}'")
    except Exception as e:
        print(f"Falha na execução: {e}")
        sys.exit(1)
