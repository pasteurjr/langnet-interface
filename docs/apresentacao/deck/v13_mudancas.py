# -*- coding: utf-8 -*-
"""V13 — a V12 inteira, sem nenhuma alteração, mais duas lâminas de infraestrutura
logo depois de "Inferência: os parâmetros que importam"."""
import copy


def _acha(S, titulo):
    for i, s in enumerate(S):
        if s.get("titulo") == titulo:
            return i
    raise KeyError(titulo)


def aplicar(v12):
    S = copy.deepcopy(v12)
    i = _acha(S, "Inferência: os parâmetros que importam")
    S[i + 1:i + 1] = [
        {"tipo": "cartoes", "bloco": 4, "chapeu": "Infraestrutura",
         "titulo": "Infraestrutura: a GPU, e onde treinar",
         "destaque": "O que limita treino e inferência é a memória da placa de vídeo, a VRAM.",
         "cartoes": [
             ("O que é uma GPU", "milhares de núcleos simples fazendo, em paralelo, a multiplicação de matrizes de que as redes neurais são feitas."),
             ("As placas no mercado", "de uso pessoal: RTX 3060 (12 GB), 4060, 5060, 5080 (16 GB), 5090 (32 GB). De datacenter: NVIDIA A100 e H100 (80 GB), H200 e B200."),
             ("Onde treinar", "Google Colab, no navegador, com GPU gratuita ou paga; nuvem por hora: AWS, Google Cloud (com GPUs e TPUs) e Azure."),
             ("Regra de bolso", "um modelo de 27 bilhões de parâmetros em 4 bits ocupa uns 16 GB; ajuste fino com LoRA cabe numa placa pessoal; treinar do zero, só em cluster.", "good")],
         "corpo": 15, "fala": ""},
        {"tipo": "maquinas", "bloco": 4, "chapeu": "Infraestrutura",
         "titulo": "A nossa infraestrutura",
         "maquinas": [
             ("Máquina principal", "treino pesado e inferência local",
              ["Intel Core i7 de 12ª geração", "128 GB de memória DDR5",
               "GPUs: RTX 5080 (16 GB) + RTX 5060 + RTX 4060",
               "2 NVMe de 2 TB (4 TB no total)"],
              "serve os modelos abertos para o LangNet, faz ajuste fino com LoRA e treina as redes de imagem."),
             ("Máquina de apoio", "treinos menores e experimentos",
              ["Intel Core de 9ª geração", "96 GB de memória DDR4",
               "GPU: RTX 3060 (12 GB)", "1 NVMe de 2 TB"],
              "roda os notebooks das aulas, modelos pequenos e testes antes de ir para a máquina principal.")],
         "nota": "Por que ter isso em casa: o dado sensível não sai da instituição, e o modelo local faz o trabalho repetitivo sem gastar tokens pagos. O modelo pago fica para o que exige mais.",
         "fala": ""},
    ]
    return S
