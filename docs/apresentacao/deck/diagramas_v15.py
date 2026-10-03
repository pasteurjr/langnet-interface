# -*- coding: utf-8 -*-
"""Figuras da V15, montadas com as imagens da apresentação-base (algoritmos inteligentes3.pptx)."""
import os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import diagramas_v11 as G
from diagramas_v11 import txt, seta, C, INK, MUTED

SRC = Path(os.environ.get("ALG_SRC", "."))
OUT = Path(__file__).resolve().parent / "diagrams_v15"
OUT.mkdir(exist_ok=True)


def im(n):
    return np.asarray(Image.open(SRC / n).convert("RGB"))


def painel(ax, a, x, y, w):
    h = w * a.shape[0] / a.shape[1]
    ax.imshow(a, extent=(x, x + w, y, y + h), zorder=2, interpolation="lanczos")
    return h


def salva(f, nome):
    f.savefig(OUT / nome, dpi=220, facecolor="white"); plt.close(f); print("ok", nome)


def cnn_arquitetura():
    G.FS = 1.25
    f, ax = G.fig(15, 4.6)
    y0 = 0.75
    h = painel(ax, im("c126_0.png"), 0.2, y0, 4.6)
    txt(ax, 2.5, 4.3, "Camadas convolucionais", 15, C["teal"][0], True)
    txt(ax, 2.5, 0.35, "cada neurônio olha só um pedaço da camada de baixo", 11, MUTED, italic=True)
    seta(ax, 4.9, 2.2, 5.5, 2.2, C["teal"][0], 2.5, head=18)
    painel(ax, im("p_pool.png"), 5.6, 1.55, 3.1)
    txt(ax, 7.15, 4.3, "Pooling", 15, C["teal"][0], True)
    txt(ax, 7.15, 0.95, "reduz a matriz\n(máximo de cada bloco)", 11, MUTED, italic=True)
    seta(ax, 8.85, 2.2, 9.4, 2.2, C["teal"][0], 2.5, head=18)
    painel(ax, im("p_flat.png"), 9.5, 1.35, 2.2)
    txt(ax, 10.6, 4.3, "Flatten", 15, C["teal"][0], True)
    txt(ax, 10.6, 0.95, "matriz vira vetor", 11, MUTED, italic=True)
    seta(ax, 11.8, 2.2, 12.3, 2.2, C["teal"][0], 2.5, head=18)
    painel(ax, im("p_dense.png"), 12.4, 1.35, 2.3)
    txt(ax, 13.55, 4.3, "Camada densa", 15, C["teal"][0], True)
    txt(ax, 13.55, 0.95, "liga tudo a tudo e\ndecide (softmax)", 11, MUTED, italic=True)
    txt(ax, 14.9, 0.1, "figuras: Géron, 2019", 9, MUTED, ha="right", italic=True)
    salva(f, "cnn_arquitetura.png")


def lado_a_lado(nomes, titulos, saida, larg=6.0, alt=None):
    G.FS = 1.2
    ims = [im(n) for n in nomes]
    n = len(ims)
    w = larg
    hs = [w * a.shape[0] / a.shape[1] for a in ims]
    H = max(hs) + 0.8
    f, ax = G.fig(w * n + 0.4 * (n + 1), H)
    x = 0.4
    for a, t, h in zip(ims, titulos, hs):
        painel(ax, a, x, 0.1 + (max(hs) - h) / 2, w)
        if t:
            txt(ax, x + w / 2, max(hs) + 0.45, t, 16, C["violet"][0], True)
        x += w + 0.4
    salva(f, saida)


def simples(nome, saida, titulo=None):
    lado_a_lado([nome], [titulo], saida)


if __name__ == "__main__":
    cnn_arquitetura()
    simples("s044_0.png", "knn.png", "K = 3: os três vizinhos votam")
    simples("s047_0.png", "reg_linear.png", "a reta que melhor passa pelos pontos")
    lado_a_lado(["s055_1.png", "s056_0.png"], ["o limite de decisão", "a sigmoide: de 0 a 1"], "reg_logistica.png")
    lado_a_lado(["s061_0.png"], ["uma pergunta divide o plano em dois"], "arvore.png", larg=8.0)
    lado_a_lado(["s066_0.png", "s066_1.png"], [None, None], "floresta_tmp.png", larg=8.0)
    simples("s067_0.png", "svm.png", "levada a 3D, a separação vira um plano")
    simples("s154_0.png", "kmeans.png", "sorteia centros, agrupa, recalcula, repete")


def lora():
    """LoRA: W congelada + B·A treinadas"""
    from matplotlib.patches import Rectangle
    G.FS = 1.25
    f, ax = G.fig(9, 5.2)
    ax.add_patch(Rectangle((0.4, 0.9), 3.0, 3.0, fc="#dbe9f5", ec=C["sky"][0], lw=2.5))
    txt(ax, 1.9, 2.55, "W", 34, C["sky"][0], True)
    txt(ax, 1.9, 1.75, "pesos originais\ncongelados", 12, C["sky"][0], True)
    txt(ax, 1.9, 4.25, "d × d  (ex.: 4096 × 4096 = 16,8 milhões)", 11, MUTED)
    txt(ax, 3.9, 2.4, "+", 34, INK, True)
    ax.add_patch(Rectangle((4.4, 0.9), 0.45, 3.0, fc=C["emerald"][1], ec=C["emerald"][0], lw=2.5))
    txt(ax, 4.625, 2.4, "B", 22, C["emerald"][0], True)
    txt(ax, 4.625, 0.55, "d × r", 11, MUTED)
    txt(ax, 5.2, 2.4, "×", 26, INK, True)
    ax.add_patch(Rectangle((5.55, 3.45), 3.0, 0.45, fc=C["emerald"][1], ec=C["emerald"][0], lw=2.5))
    txt(ax, 7.05, 3.675, "A", 22, C["emerald"][0], True)
    txt(ax, 7.05, 4.25, "r × d", 11, MUTED)
    txt(ax, 7.05, 2.35, "só B e A são treinadas\nposto r = 16:\n131 mil pesos (< 1%)", 13, C["emerald"][0], True)
    txt(ax, 4.5, 0.12, "W' = W + B·A  —  depois do treino, B·A se soma a W", 12, INK, True)
    salva(f, "lora.png")
