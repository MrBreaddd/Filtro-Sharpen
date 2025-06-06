from PIL import Image, ImageFilter
import threading

# Kernel de sharpening 3x3
sharpen_kernel = [
     0, -1,  0,
    -1,  5, -1,
     0, -1,  0
]

def filtro_em_area(imagem, coord, kernel, lock):
    x_in, y_in, x_fin, y_fin = coord
    with lock:
        recorte = imagem.crop((x_in, y_in, x_fin, y_fin))
        filtrada = recorte.filter(ImageFilter.Kernel((3, 3), kernel, scale=None, offset=0))
        imagem.paste(filtrada, (x_in, y_in))

def dividir_imagem(imagem, num_threads):
    largura, altura = imagem.size
    largura_por_thread = largura // num_threads
    regioes = []
    for i in range(num_threads):
        x_in = i * largura_por_thread
        x_fin = (i + 1) * largura_por_thread if i != num_threads - 1 else largura
        regioes.append((x_in, 0, x_fin, altura))
    return regioes

def filtro_threads(imagem_caminho, num_threads, kernel, nome_saida):
    try:
        imagem = Image.open(imagem_caminho).convert("RGB")
        regioes = dividir_imagem(imagem, num_threads)
        threads = []
        lock = threading.Lock()

        for coord in regioes:
            thread = threading.Thread(target=filtro_em_area, args=(imagem, coord, kernel, lock))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        imagem.save(nome_saida)
        print(f"Imagem com sharpening salva como {nome_saida}")

    except FileNotFoundError:
        print(f"Erro: A imagem '{imagem_caminho}' não foi encontrada.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    imagem_caminho = "imagem.jpg"
    num_threads = 4
    iteracoes = 5

    imagem_atual = imagem_caminho

    for i in range(1, iteracoes + 1):
        nome_base, extensao = imagem_caminho.rsplit('.', 1)
        nome_saida = f"{nome_base}_sharpened_{i}.{extensao}"

        filtro_threads(imagem_atual, num_threads, sharpen_kernel, nome_saida)

        imagem_atual = nome_saida