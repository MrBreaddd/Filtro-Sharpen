from PIL import Image, ImageFilter # Image abre, salva e manipula imagens. ImageFilter aplica filtros
import threading                   # threading permite a utilização de múltiplas threads

# Kernel de sharpening 3x3. O valor central (5) dá peso ao pixel atual enquanto que os (-1) subtraem os vizinhos
sharpen_kernel = [
     0, -1,  0,
    -1,  5, -1,
     0, -1,  0
]

def filtro_em_area(imagem, coord, kernel, lock): #Função por de fato processar o filtro, utiliza o lock para impedir que 
    x_in, y_in, x_fin, y_fin = coord             #múltiplas threads façam alterações simultâneas para evitar corrupção da
    with lock:                                   #imagem que está na memória
        recorte = imagem.crop((x_in, y_in, x_fin, y_fin))
        filtrada = recorte.filter(ImageFilter.Kernel((3, 3), kernel, scale=None, offset=0))
        imagem.paste(filtrada, (x_in, y_in))

def dividir_imagem(imagem, num_threads): #Função responsável pela divisão da imagem em faixas de acordo com a quantidade de threads
    largura, altura = imagem.size #Coleta do tamanho da imagem original
    largura_por_thread = largura // num_threads #Determinação da quantidade de áreas
    regioes = []
    for i in range(num_threads): #Produz o conjunto de regiões que são retornadas
        x_in = i * largura_por_thread
        x_fin = (i + 1) * largura_por_thread if i != num_threads - 1 else largura
        regioes.append((x_in, 0, x_fin, altura))
    return regioes

def filtro_threads(imagem_caminho, num_threads, kernel, nome_saida): #Função responsável por toda a organização do programa, desde a aplicação do filtro até o salvamento da iteração
    try: #Parametrização inicial e coleta de imagem
        imagem = Image.open(imagem_caminho).convert("RGB")
        regioes = dividir_imagem(imagem, num_threads)
        threads = []
        lock = threading.Lock()

        for coord in regioes: #Cria uma thread por faixa de imagem
            thread = threading.Thread(target=filtro_em_area, args=(imagem, coord, kernel, lock))
            threads.append(thread)
            thread.start()

        for thread in threads: #Garante que todas as thread tenham sido executadas antes de prosseguir
            thread.join()

        imagem.save(nome_saida) #Salva cada iteração
        print(f"Imagem com sharpening salva como {nome_saida}")

        #Erros de execução ou falha em encontrar imagem
    except FileNotFoundError:
        print(f"Erro: A imagem '{imagem_caminho}' não foi encontrada.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__": #Bloco principal do programa, primeira parte a ser executada e onde as prédifinições são definidas
    imagem_caminho = "imagem.jpg"
    num_threads = 4
    iteracoes = 5

    imagem_atual = imagem_caminho

    for i in range(1, iteracoes + 1): #Bloco responsável por executar o filtro por todas as iterações, utilizando a imagem mais recente
        nome_base, extensao = imagem_caminho.rsplit('.', 1)
        nome_saida = f"{nome_base}_sharpened_{i}.{extensao}"

        filtro_threads(imagem_atual, num_threads, sharpen_kernel, nome_saida)

        imagem_atual = nome_saida