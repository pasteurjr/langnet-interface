# -*- coding: utf-8 -*-
"""Figuras da V11 (matplotlib). Gera PNGs em diagrams_v11/. Não altera nada da V10."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle, Polygon
from PIL import Image
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "diagrams_v11"
OUT.mkdir(exist_ok=True)
plt.rcParams["font.family"] = "Liberation Sans"

FS = 1.0   # escala de fonte por figura (a figura encolhe no slide)
INK = "#161e33"; MUTED = "#5a667e"; LINE = "#c9d1e0"
C = {"indigo": ("#4f46e5", "#ecebfd"), "sky": ("#0283c9", "#e3f3fc"), "violet": ("#7c3aed", "#f2eafe"),
     "teal": ("#0d9488", "#e1f5f3"), "emerald": ("#059669", "#e2f6ee"), "amber": ("#d97706", "#fcf1df"),
     "rose": ("#e11d48", "#fce6ec"), "slate": ("#334166", "#eaedf4"), "gray": ("#8a94a8", "#f1f3f7")}


def fig(w, h):
    f = plt.figure(figsize=(w, h), dpi=200)
    ax = f.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    return f, ax


def box(ax, x, y, w, h, txt, cor="indigo", size=13, bold=True, fill=None, tc=None, lw=2, r=0.12, ls="-", italic=False):
    c1, c3 = C[cor]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=%g" % r,
                                fc=fill or c3, ec=c1, lw=lw, ls=ls))
    if txt:
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=size * FS,
                fontweight="bold" if bold else "normal", color=tc or c1, style="italic" if italic else "normal",
                linespacing=1.15)


def seta(ax, x1, y1, x2, y2, cor=INK, lw=2, ls="-", rad=0.0, head=14):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=head, color=cor,
                                 lw=lw, ls=ls, connectionstyle="arc3,rad=%g" % rad, shrinkA=0, shrinkB=0))


def txt(ax, x, y, s, size=12, cor=INK, bold=False, ha="center", va="center", italic=False):
    ax.text(x, y, s, fontsize=size * FS, color=cor, fontweight="bold" if bold else "normal", ha=ha, va=va,
            style="italic" if italic else "normal", linespacing=1.15)


def salva(f, nome):
    f.savefig(OUT / nome, dpi=200, facecolor="white")
    plt.close(f)
    print("ok", nome)


# ───────────────────────── MLP ─────────────────────────
def mlp():
    f, ax = fig(10.7, 5.6)
    camadas = [(4, "sky"), (6, "violet"), (6, "violet"), (2, "emerald")]
    xs = [1.4, 3.9, 6.4, 8.8]
    pos = []
    for (n, cor), x in zip(camadas, xs):
        ys = np.linspace(4.4 - (6 - n) * 0.33, 1.0 + (6 - n) * 0.33, n) if n > 1 else [2.7]
        pos.append([(x, y) for y in ys])
    for a, b in zip(pos[:-1], pos[1:]):
        for (x1, y1) in a:
            for (x2, y2) in b:
                ax.plot([x1, x2], [y1, y2], color="#b9c2d6", lw=0.9, zorder=1)
    for (n, cor), pts in zip(camadas, pos):
        for (x, y) in pts:
            ax.add_patch(Circle((x, y), 0.25, fc=C[cor][1], ec=C[cor][0], lw=2.2, zorder=3))
    for i, (x, y) in enumerate(pos[0]):
        txt(ax, x - 0.55, y, "x%d" % (i + 1), 13, MUTED, italic=True)
    for (x, y), rot in zip(pos[3], ["classe A", "classe B"]):
        txt(ax, x + 0.4, y, rot, 13, C["emerald"][0], True, ha="left")
    txt(ax, 1.4, 5.15, "Camada de entrada", 14, C["sky"][0], True)
    txt(ax, 5.15, 5.15, "Camadas intermediárias (ocultas)", 14, C["violet"][0], True)
    txt(ax, 8.8, 5.15, "Camada de saída", 14, C["emerald"][0], True)
    ax.plot([3.4, 6.9], [4.9, 4.9], color=C["violet"][0], lw=1.5)
    txt(ax, 5.15, 0.35, "cada linha é uma conexão com peso próprio  ·  o sinal flui da esquerda para a direita", 12, MUTED, italic=True)
    salva(f, "mlp.png")


# ───────────────────────── CNN: caminho da imagem ─────────────────────────
def cnn():
    src = Image.open(OUT / "cnn_camadas.png")
    W, H = src.size
    # os três painéis do recorte (NG, 2019)
    p1 = src.crop((27, 14, 612, 408)); p2 = src.crop((986, 14, 1618, 408)); p3 = src.crop((1992, 14, 2659, 408))
    rosto = p3.crop((0, 0, p3.size[0] // 6, p3.size[1] // 4 + 4))
    f, ax = fig(14, 4.6)
    def poe(im, x, y, w):
        h = w * im.size[1] / im.size[0]
        ax.imshow(np.asarray(im), extent=(x, x + w, y, y + h), zorder=2)
        return h
    y0 = 1.25
    # 1 imagem
    h = poe(rosto.resize((rosto.size[0] * 3, rosto.size[1] * 3)), 0.35, y0 + 0.1, 1.55)
    txt(ax, 1.12, 3.95, "Imagem", 15, C["teal"][0], True)
    txt(ax, 1.12, 0.7, "pixels de entrada", 11.5, MUTED, italic=True)
    # 2 convoluções
    h = poe(p1, 2.55, y0, 2.7)
    txt(ax, 3.9, 3.95, "Convoluções", 15, C["teal"][0], True)
    txt(ax, 3.9, 0.7, "filtros acham bordas e orientações", 11.5, MUTED, italic=True)
    # 3 características
    poe(p2, 5.95, y0, 2.8)
    txt(ax, 7.35, 3.95, "Características", 15, C["teal"][0], True)
    txt(ax, 7.35, 0.7, "combinam bordas em partes: olho, nariz", 11.5, MUTED, italic=True)
    # 4 camadas posteriores
    poe(p3, 9.45, y0, 2.75)
    txt(ax, 10.82, 3.95, "Camadas posteriores", 15, C["teal"][0], True)
    txt(ax, 10.82, 0.7, "combinam partes em objetos inteiros", 11.5, MUTED, italic=True)
    # 5 resultado
    box(ax, 12.65, 1.75, 1.2, 1.3, "Resultado\n\nrosto\n0,97", "emerald", 12.5)
    for x1, x2 in [(1.95, 2.45), (5.3, 5.85), (8.8, 9.35), (12.25, 12.6)]:
        seta(ax, x1, 2.4, x2, 2.4, C["teal"][0], 2.5, head=18)
    txt(ax, 13.8, 0.25, "painéis de filtros: Ng, 2019", 9, MUTED, ha="right", italic=True)
    salva(f, "cnn_caminho.png")


# ───────────────────────── Transfer Learning ─────────────────────────
def transfer():
    f, ax = fig(12, 6.4)
    # coluna esquerda: rede pré-treinada original
    txt(ax, 2.6, 6.0, "Rede pré-treinada", 16, C["slate"][0], True)
    txt(ax, 2.6, 5.62, "milhões de imagens gerais (ImageNet)", 11.5, MUTED, italic=True)
    esq = [("Classificador original\n1000 classes gerais", "gray"),
           ("Bloco convolucional 5 · objetos", "sky"), ("Bloco convolucional 4 · partes", "sky"),
           ("Bloco convolucional 3 · formas", "sky"), ("Bloco convolucional 2 · texturas", "sky"),
           ("Bloco convolucional 1 · bordas", "sky")]
    y = 4.75
    for i, (t, cor) in enumerate(esq):
        box(ax, 0.6, y, 4.0, 0.62, t, cor, 12, ls="--" if i == 0 else "-", tc=(C["rose"][0] if i == 0 else None))
        y -= 0.78
    txt(ax, 4.72, 5.06, "descartado", 11, C["rose"][0], True, ha="left")
    txt(ax, 2.6, 0.35, "imagem de entrada", 12, MUTED, italic=True)
    seta(ax, 2.6, 0.55, 2.6, 0.8, MUTED, 1.5)
    # seta de reaproveitamento
    seta(ax, 4.8, 2.55, 6.55, 2.55, C["amber"][0], 3.5, head=24)
    txt(ax, 5.65, 3.05, "reaproveita o\nconhecimento", 13, C["amber"][0], True)
    # coluna direita: nova rede
    txt(ax, 8.55, 6.0, "Nova rede para o seu problema", 16, C["emerald"][0], True)
    txt(ax, 8.55, 5.62, "algumas centenas de imagens do domínio", 11.5, MUTED, italic=True)
    novas = [("Densa softmax · as SUAS classes", "emerald"), ("Dropout", "emerald"),
             ("Densa (ReLU)", "emerald"), ("Pooling global", "emerald")]
    y = 4.95
    for t, cor in novas:
        box(ax, 6.7, y, 3.7, 0.5, t, cor, 12)
        y -= 0.6
    congel = ["Bloco convolucional 5", "Bloco convolucional 4", "Bloco convolucional 3",
              "Bloco convolucional 2", "Bloco convolucional 1"]
    y = 2.42
    for t in congel:
        box(ax, 6.7, y, 3.7, 0.4, t + "  · congelado", "sky", 11, fill="#dbe9f5")
        y -= 0.48
    ax.plot([10.6, 10.6], [0.5, 2.82], color=C["sky"][0], lw=3)
    txt(ax, 10.75, 1.66, "congeladas\n(pesos não\nmudam)", 12, C["sky"][0], True, ha="left")
    ax.plot([10.6, 10.6], [3.15, 5.45], color=C["emerald"][0], lw=3)
    txt(ax, 10.75, 4.3, "adaptadas\n(treinadas\ncom os seus\ndados)", 12, C["emerald"][0], True, ha="left")
    salva(f, "transfer.png")


# ───────────────────────── Transformer ─────────────────────────
def transformer():
    f, ax = fig(15, 8.4)
    # codificador
    ax.add_patch(FancyBboxPatch((0.6, 2.2), 3.6, 3.25, boxstyle="round,pad=0,rounding_size=0.2",
                                fc="#f6f8fc", ec=C["sky"][0], lw=2, ls="--"))
    ax.text(0.3, 3.8, "CODIFICADOR", fontsize=15 * FS, color=C["sky"][0], fontweight="bold", rotation=90, ha="center", va="center")
    txt(ax, 4.5, 3.3, "N×", 16, C["sky"][0], True)
    box(ax, 0.9, 2.45, 3.0, 0.62, "Atenção multi-cabeça", "sky", 12.5, fill="#cfe8f7")
    box(ax, 0.9, 3.25, 3.0, 0.45, "Soma e normalização", "gray", 11, bold=False)
    box(ax, 0.9, 3.88, 3.0, 0.62, "Rede feed-forward", "sky", 12.5)
    box(ax, 0.9, 4.68, 3.0, 0.45, "Soma e normalização", "gray", 11, bold=False)
    box(ax, 0.9, 1.25, 3.0, 0.6, "Embeddings +\nposição", "slate", 11.5)
    txt(ax, 2.4, 0.55, "Entrada\n“o paciente tem febre”", 12, MUTED)
    seta(ax, 2.4, 0.85, 2.4, 1.23, MUTED, 1.6)
    for a, b in [(1.86, 2.43), (3.07, 3.23), (3.7, 3.86), (4.5, 4.66)]:
        seta(ax, 2.4, a, 2.4, b, INK, 1.6, head=11)
    # decodificador
    ax.add_patch(FancyBboxPatch((5.5, 2.2), 3.6, 4.35, boxstyle="round,pad=0,rounding_size=0.2",
                                fc="#f6f8fc", ec=C["violet"][0], lw=2, ls="--"))
    ax.text(9.45, 4.4, "DECODIFICADOR", fontsize=15 * FS, color=C["violet"][0], fontweight="bold", rotation=90, ha="center", va="center")
    txt(ax, 5.25, 2.75, "N×", 16, C["violet"][0], True)
    box(ax, 5.8, 2.4, 3.0, 0.6, "Atenção mascarada\n(só olha para trás)", "violet", 11.5, fill="#e4d6fb")
    box(ax, 5.8, 3.12, 3.0, 0.38, "Soma e normalização", "gray", 10.5, bold=False)
    box(ax, 5.8, 3.62, 3.0, 0.62, "Atenção cruzada\n(consulta o codificador)", "violet", 11.5, fill="#e4d6fb")
    box(ax, 5.8, 4.36, 3.0, 0.38, "Soma e normalização", "gray", 10.5, bold=False)
    box(ax, 5.8, 4.86, 3.0, 0.62, "Rede feed-forward", "violet", 12.5)
    box(ax, 5.8, 5.6, 3.0, 0.38, "Soma e normalização", "gray", 10.5, bold=False)
    box(ax, 5.8, 1.25, 3.0, 0.6, "Embeddings +\nposição", "slate", 11.5)
    txt(ax, 7.3, 0.55, "Saída já gerada\n(deslocada um passo)", 12, MUTED)
    seta(ax, 7.3, 0.85, 7.3, 1.23, MUTED, 1.6)
    for a, b in [(1.86, 2.38), (3.01, 3.1), (3.51, 3.6), (4.25, 4.34), (4.75, 4.84), (5.49, 5.58)]:
        seta(ax, 7.3, a, 7.3, b, INK, 1.6, head=11)
    # saída
    box(ax, 5.8, 7.2, 3.0, 0.45, "Linear → Softmax", "emerald", 12)
    seta(ax, 7.3, 5.99, 7.3, 7.18, INK, 1.6, head=11)
    txt(ax, 7.3, 8.05, "probabilidade do próximo token", 12.5, C["emerald"][0], True)
    seta(ax, 7.3, 7.66, 7.3, 7.85, INK, 1.6, head=11)
    # ligação codificador -> atenção cruzada
    seta(ax, 3.9, 4.95, 5.78, 3.95, C["sky"][0], 2.6, rad=-0.25, head=18)
    txt(ax, 4.75, 5.55, "chaves e valores\ndo codificador", 11, C["sky"][0], True)
    # matriz de atenção
    toks = ["o", "paciente", "tem", "febre", "alta"]
    rng = np.random.default_rng(7)
    M = np.array([[.70, .15, .05, .05, .05],
                  [.20, .55, .10, .10, .05],
                  [.05, .45, .30, .15, .05],
                  [.05, .40, .10, .35, .10],
                  [.03, .12, .05, .60, .20]])
    x0, y0, s = 10.9, 1.55, 0.72
    for i in range(5):
        for j in range(5):
            v = M[i, j]
            cor = plt.cm.Purples(0.08 + 0.9 * v)
            ax.add_patch(Rectangle((x0 + j * s, y0 + (4 - i) * s), s, s, fc=cor, ec="white", lw=1.5))
        txt(ax, x0 - 0.12, y0 + (4 - i) * s + s / 2, toks[i], 12, INK, ha="right")
        ax.text(x0 + i * s + s / 2, y0 + 5 * s + 0.1, toks[i], fontsize=12 * FS, color=INK, rotation=40, ha="left", va="bottom")
    txt(ax, x0 + 2.5 * s, 6.85, "Matriz de atenção", 15, C["violet"][0], True)
    txt(ax, x0 + 2.5 * s, 1.1, "linha = token que pergunta (consulta)\ncoluna = token consultado (chave)\ncor forte = mais atenção", 11, MUTED)
    txt(ax, x0 + 2.5 * s, 0.4, "“febre” olha para “paciente”", 11, C["violet"][0], italic=True)
    seta(ax, 8.85, 3.93, 9.95, 3.3, C["violet"][0], 1.5, ls="--", head=12)
    salva(f, "transformer.png")


# ───────────────────────── padrões de composição ─────────────────────────
def padroes():
    f, ax = fig(15, 4.8)
    cor = "amber"; c1 = C[cor][0]
    # Encadeamento
    txt(ax, 2.4, 4.4, "Encadeamento", 17, c1, True)
    for i, t in enumerate(["Passo 1", "Passo 2", "Passo 3"]):
        box(ax, 0.3 + i * 1.5, 2.3, 1.15, 0.8, t, cor, 12)
        if i < 2:
            seta(ax, 1.47 + i * 1.5, 2.7, 1.78 + i * 1.5, 2.7, INK, 2)
    txt(ax, 2.4, 1.3, "a saída de um é a\nentrada do próximo", 12.5, MUTED, italic=True)
    ax.plot([5.05, 5.05], [0.5, 4.5], color=LINE, lw=1.5)
    # Roteamento
    txt(ax, 7.5, 4.4, "Roteamento", 17, c1, True)
    box(ax, 5.35, 2.3, 1.0, 0.8, "Pedido", "slate", 12)
    ax.add_patch(Polygon([[6.75, 2.7], [7.35, 3.25], [7.95, 2.7], [7.35, 2.15]], fc=C[cor][1], ec=c1, lw=2))
    txt(ax, 7.35, 2.7, "classifica", 10.5, c1, True)
    seta(ax, 6.37, 2.7, 6.73, 2.7, INK, 2)
    for k, (t, y) in enumerate([("Especialista A", 3.55), ("Especialista B", 2.45), ("Especialista C", 1.35)]):
        destaque = k == 1
        box(ax, 8.4, y, 1.9, 0.62, t, "emerald" if destaque else "gray", 11.5, lw=2.6 if destaque else 1.5)
        seta(ax, 7.95, 2.7, 8.38, y + 0.31, C["emerald"][0] if destaque else "#b9c2d6", 2.4 if destaque else 1.4)
    txt(ax, 7.5, 0.75, "um classificador escolhe\nquem atende", 12.5, MUTED, italic=True)
    ax.plot([10.55, 10.55], [0.5, 4.5], color=LINE, lw=1.5)
    # Paralelismo
    txt(ax, 12.8, 4.4, "Paralelismo", 17, c1, True)
    box(ax, 10.8, 2.3, 0.95, 0.8, "Tarefa", "slate", 12)
    for t, y in [("Parte 1", 3.55), ("Parte 2", 2.45), ("Parte 3", 1.35)]:
        box(ax, 12.15, y, 1.15, 0.62, t, cor, 11.5)
        seta(ax, 11.77, 2.7, 12.13, y + 0.31, INK, 1.6)
        seta(ax, 13.32, y + 0.31, 13.73, 2.7, INK, 1.6)
    box(ax, 13.75, 2.25, 1.1, 0.9, "Agrega\nou vota", "emerald", 11.5)
    txt(ax, 12.8, 0.75, "partes independentes ao\nmesmo tempo, juntadas no fim", 12.5, MUTED, italic=True)
    salva(f, "padroes.png")


# ───────────────────────── tipos de RAG ─────────────────────────
def rag():
    f, ax = fig(15, 6.2)
    c = "rose"
    txt(ax, 0.4, 5.75, "PREPARAÇÃO  (uma vez, e a cada documento novo)", 13.5, C["slate"][0], True, ha="left")
    etapas1 = [("Documentos", "slate", "PDF, normas,\nprontuários"),
               ("Fatiamento", c, "chunking: por tamanho,\npor seção, por sentido"),
               ("Embeddings", c, "cada pedaço vira\num vetor de sentido"),
               ("Indexação vetorial", c, "FAISS · Qdrant · pgvector\nChroma · Milvus"),
               ("Metadados", c, "fonte, data, tipo,\nsetor, versão")]
    for i, (t, cor, d) in enumerate(etapas1):
        x = 0.4 + i * 2.95
        box(ax, x, 4.35, 2.45, 0.8, t, cor, 13.5)
        txt(ax, x + 1.225, 3.75, d, 11, MUTED)
        if i < 4:
            seta(ax, x + 2.47, 4.75, x + 2.93, 4.75, INK, 2)
    txt(ax, 0.4, 2.95, "CONSULTA  (a cada pergunta)", 13.5, C["slate"][0], True, ha="left")
    etapas2 = [("Pergunta", "slate", ""),
               ("Busca semântica\nou híbrida", c, "vetor + palavra-chave"),
               ("Filtros por\nmetadados", c, "só o setor, só a\nversão vigente"),
               ("Reranking", c, "reordena pelos\nmais relevantes"),
               ("Contexto\n→ LLM", "emerald", "resposta com a\nfonte citada")]
    for i, (t, cor, d) in enumerate(etapas2):
        x = 0.4 + i * 2.95
        box(ax, x, 1.45, 2.45, 0.95, t, cor, 13)
        if d:
            txt(ax, x + 1.225, 0.9, d, 11, MUTED)
        if i < 4:
            seta(ax, x + 2.47, 1.92, x + 2.93, 1.92, INK, 2)
    # índice alimenta a busca
    seta(ax, 9.85, 3.4, 4.6, 2.43, C[c][0], 2, ls="--", head=14)
    txt(ax, 7.9, 2.72, "o índice é consultado", 11, C[c][0], True, italic=True)
    salva(f, "rag_tipos.png")


# ───────────────────────── LangGraph ─────────────────────────
def langgraph():
    f, ax = fig(7.2, 5.6)
    c = "indigo"
    box(ax, 0.3, 4.75, 6.6, 0.6, "Estado compartilhado:  caso · risco · decisão", "slate", 12.5)
    def no(x, y, t, cor=c, w=1.9):
        box(ax, x, y, w, 0.6, t, cor, 12.5)
    ax.add_patch(Circle((1.2, 4.0), 0.22, fc=INK)); txt(ax, 1.62, 4.0, "START", 11, MUTED, True, ha="left")
    no(0.25, 2.9, "classificar")
    seta(ax, 1.2, 3.77, 1.2, 3.52, INK, 1.8)
    ax.add_patch(Polygon([[3.1, 3.2], [3.7, 3.65], [4.3, 3.2], [3.7, 2.75]], fc=C["amber"][1], ec=C["amber"][0], lw=2))
    txt(ax, 3.7, 3.2, "risco?", 11, C["amber"][0], True)
    seta(ax, 2.17, 3.2, 3.08, 3.2, INK, 1.8)
    no(4.9, 3.6, "alertar", "rose", 1.7)
    no(4.9, 2.2, "registrar", "emerald", 1.7)
    seta(ax, 4.2, 3.4, 4.88, 3.85, C["rose"][0], 1.8); txt(ax, 4.45, 3.85, "alto", 11, C["rose"][0], True)
    seta(ax, 4.2, 3.0, 4.88, 2.5, C["emerald"][0], 1.8); txt(ax, 4.4, 2.5, "baixo", 11, C["emerald"][0], True)
    ax.add_patch(Circle((5.75, 1.05), 0.24, fc="white", ec=INK, lw=2)); ax.add_patch(Circle((5.75, 1.05), 0.14, fc=INK))
    txt(ax, 6.1, 1.05, "END", 11, MUTED, True, ha="left")
    seta(ax, 5.75, 2.18, 5.75, 1.3, INK, 1.8)
    seta(ax, 6.62, 3.9, 6.05, 1.2, INK, 1.8, rad=-0.35)
    txt(ax, 2.0, 1.6, "nó = função\naresta = transição\nlosango = aresta condicional", 11, MUTED, ha="center", italic=True)
    salva(f, "langgraph.png")


# ───────────────────────── AutoGen: dois agentes ─────────────────────────
def autogen():
    f, ax = fig(7.2, 5.6)
    box(ax, 0.2, 4.4, 2.4, 0.85, "Redator\n(AssistantAgent)", "violet", 12)
    box(ax, 4.6, 4.4, 2.4, 0.85, "Revisor\n(AssistantAgent)", "teal", 12)
    ax.plot([1.4, 1.4], [0.3, 4.38], color=C["violet"][0], lw=1.5, ls=":")
    ax.plot([5.8, 5.8], [0.3, 4.38], color=C["teal"][0], lw=1.5, ls=":")
    msgs = [(1, "1  mensagem: rascunho do resumo", "violet"),
            (0, "2  resposta: falta citar a fonte", "teal"),
            (1, "3  nova versão, com a fonte", "violet"),
            (0, "4  aprovado — TERMINATE", "emerald")]
    y = 3.75
    for dirr, t, cor in msgs:
        if dirr:
            seta(ax, 1.45, y, 5.75, y, C[cor][0], 2.2)
        else:
            seta(ax, 5.75, y, 1.45, y, C[cor][0], 2.2)
        ax.text(3.6, y + 0.14, t, fontsize=11.5 * FS, color=C[cor][0], ha="center", va="bottom", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=C[cor][0], lw=1))
        y -= 0.9
    salva(f, "autogen.png")


# ───────────────────────── Protocolos com OKF ─────────────────────────
def protocolos():
    f, ax = fig(14, 6.6)
    box(ax, 5.6, 2.75, 2.8, 1.1, "AGENTE", "rose", 22, fill=C["rose"][0], tc="white")
    # vertical: MCP
    box(ax, 4.9, 5.2, 4.2, 1.05, "Ferramentas · bancos · APIs\n(servidores MCP)", "sky", 13.5)
    ax.add_patch(FancyArrowPatch((7.0, 3.87), (7.0, 5.18), arrowstyle="<|-|>", mutation_scale=18, color=C["sky"][0], lw=3))
    txt(ax, 7.2, 4.5, "MCP — Model Context Protocol\neixo vertical: agente ↔ ferramentas", 12, C["sky"][0], True, ha="left")
    # horizontal: A2A à esquerda
    box(ax, 0.4, 2.8, 2.6, 1.0, "outro agente", "violet", 14)
    ax.add_patch(FancyArrowPatch((3.02, 3.3), (5.58, 3.3), arrowstyle="<|-|>", mutation_scale=18, color=C["violet"][0], lw=3))
    txt(ax, 4.3, 3.62, "A2A", 14, C["violet"][0], True)
    txt(ax, 4.3, 2.85, "agente ↔ agente", 11, C["violet"][0])
    # horizontal: OKF à direita
    ax.add_patch(FancyArrowPatch((8.42, 3.3), (10.9, 3.3), arrowstyle="<|-|>", mutation_scale=18, color=C["amber"][0], lw=3))
    txt(ax, 9.66, 3.62, "OKF", 14, C["amber"][0], True)
    txt(ax, 9.66, 2.85, "conhecimento aberto", 11, C["amber"][0])
    # documento OKF
    ax.add_patch(Polygon([[10.95, 2.5], [10.95, 4.1], [12.3, 4.1], [12.65, 3.75], [12.65, 2.5]], fc=C["amber"][1], ec=C["amber"][0], lw=2))
    txt(ax, 11.8, 3.3, "base de\nconhecimento\nOKF", 12, C["amber"][0], True)
    # humano lê também
    ax.add_patch(Circle((13.3, 3.75), 0.2, fc=C["slate"][1], ec=C["slate"][0], lw=2))
    ax.add_patch(FancyBboxPatch((13.02, 2.85), 0.56, 0.7, boxstyle="round,pad=0,rounding_size=0.2", fc=C["slate"][1], ec=C["slate"][0], lw=2))
    seta(ax, 12.97, 3.3, 12.7, 3.3, C["slate"][0], 1.6, head=10)
    txt(ax, 13.3, 2.5, "pessoas\ntambém leem", 10.5, C["slate"][0], True)
    # eixo horizontal marcado
    ax.plot([0.4, 13.6], [1.75, 1.75], color=LINE, lw=2)
    txt(ax, 7.0, 1.4, "eixo horizontal: agente ↔ agente (A2A)  ·  agentes e pessoas ↔ conhecimento compartilhado (OKF)", 12.5, INK, True)
    txt(ax, 7.0, 0.8, "OKF — Open Knowledge Format: formato aberto de troca de conhecimento, legível por agentes e por humanos", 11.5, MUTED, italic=True)
    salva(f, "protocolos_okf.png")


# ───────────────────────── Vibe Coding × SDD ─────────────────────────
def vibe_sdd():
    f, ax = fig(15, 5.4)
    # vibe
    ax.add_patch(FancyBboxPatch((0.25, 0.3), 6.2, 4.8, boxstyle="round,pad=0,rounding_size=0.2", fc="#fff7ed", ec=C["amber"][0], lw=2))
    txt(ax, 3.35, 4.7, "Vibe Coding", 20, C["amber"][0], True)
    box(ax, 0.6, 3.0, 1.5, 0.8, "pedido", "gray", 13)
    box(ax, 2.6, 3.0, 1.5, 0.8, "IA gera", "amber", 13)
    box(ax, 4.6, 3.0, 1.5, 0.8, "código", "gray", 13)
    seta(ax, 2.12, 3.4, 2.58, 3.4, INK, 2); seta(ax, 4.12, 3.4, 4.58, 3.4, INK, 2)
    seta(ax, 5.35, 2.98, 1.35, 2.98, C["amber"][0], 2, rad=-0.45)
    txt(ax, 3.35, 1.95, "“não ficou bom, tenta de novo”", 12.5, C["amber"][0], italic=True)
    txt(ax, 3.35, 1.0, "sem especificação  ·  sem rastreabilidade\nsem validação  ·  sem processo definido", 12.5, C["rose"][0], True)
    # SDD
    ax.add_patch(FancyBboxPatch((6.85, 0.3), 7.9, 4.8, boxstyle="round,pad=0,rounding_size=0.2", fc="#ecfdf5", ec=C["emerald"][0], lw=2))
    txt(ax, 10.8, 4.7, "SDD — Specification-Driven Development", 20, C["emerald"][0], True)
    et = ["Requisitos", "Especifi-\ncação", "Artefatos", "Desenvol-\nvimento", "Validação"]
    for i, t in enumerate(et):
        x = 7.1 + i * 1.53
        box(ax, x, 3.0, 1.3, 0.85, t, "emerald", 12)
        if i < 4:
            seta(ax, x + 1.32, 3.42, x + 1.51, 3.42, INK, 2, head=11)
    ax.add_patch(FancyArrowPatch((7.1 + 4 * 1.53 + 0.65, 2.98), (7.75, 2.98), arrowstyle="-|>", mutation_scale=14,
                                 color=C["emerald"][0], lw=2, ls="--", connectionstyle="arc3,rad=-0.28"))
    txt(ax, 10.8, 1.95, "rastreabilidade: da validação de volta ao requisito", 12, C["emerald"][0], italic=True)
    txt(ax, 10.8, 0.95, "cada artefato aponta para a sua origem\na IA acelera cada etapa, e cada etapa é conferida", 12.5, C["emerald"][0], True)
    salva(f, "vibe_sdd.png")


# ───────────────────────── rastreabilidade ─────────────────────────
def rastreio():
    f, ax = fig(15, 4.6)
    nos = [("Requisito", "o que o sistema\ndeve fazer"), ("Caso de uso", "como o usuário\nrealiza"),
           ("Modelo de dados\ne tela", "onde o dado mora\ne onde aparece"), ("Tarefa", "quem executa\ne com que regra"),
           ("Caso de teste", "como se confere\no comportamento"), ("Código", "o que\nimplementa")]
    for i, (t, d) in enumerate(nos):
        x = 0.3 + i * 2.48
        box(ax, x, 2.3, 2.0, 1.0, t, "indigo", 13.5)
        txt(ax, x + 1.0, 1.65, d, 11.5, MUTED)
        if i < 5:
            seta(ax, x + 2.02, 2.95, x + 2.46, 2.95, INK, 2.2)
            ax.add_patch(FancyArrowPatch((x + 2.46, 2.55), (x + 2.02, 2.55), arrowstyle="-|>", mutation_scale=11,
                                         color=C["amber"][0], lw=1.6, ls="--"))
    txt(ax, 7.5, 4.05, "derivação: cada artefato nasce do anterior", 13, INK, True)
    seta(ax, 5.0, 3.72, 10.0, 3.72, INK, 1.4, head=10)
    txt(ax, 7.5, 0.55, "rastreio: cada artefato guarda a referência de onde veio — dá para ir do código ao requisito, e voltar", 13, C["amber"][0], True)
    salva(f, "rastreabilidade.png")


# ───────────────────────── requisitos ─────────────────────────
def requisitos():
    f, ax = fig(15, 5.6)
    c = "violet"
    ax.add_patch(Polygon([[0.3, 1.7], [0.3, 3.9], [1.95, 3.9], [2.4, 3.45], [2.4, 1.7]], fc=C["slate"][1], ec=C["slate"][0], lw=2))
    txt(ax, 1.35, 2.8, "Documento\nde entrada", 13, C["slate"][0], True)
    # extração
    box(ax, 3.2, 3.55, 3.4, 1.25, "EXTRAÇÃO\no que está escrito", c, 13.5)
    box(ax, 3.2, 1.0, 3.4, 1.25, "INFERÊNCIA\no que é necessário\ne não foi escrito", c, 13, fill="#e4d6fb")
    seta(ax, 2.42, 3.2, 3.18, 4.1, INK, 2); seta(ax, 2.42, 2.4, 3.18, 1.65, INK, 2)
    # web
    box(ax, 3.35, 0.05, 3.1, 0.62, "pesquisa web complementa", "sky", 11.5)
    seta(ax, 4.9, 0.69, 4.9, 0.98, C["sky"][0], 1.8)
    # tipos
    tipos = [("Requisitos funcionais", "o que o sistema faz"), ("Requisitos não funcionais", "desempenho, segurança, disponibilidade"),
             ("Regras de negócio", "políticas e critérios do domínio")]
    for i, (t, d) in enumerate(tipos):
        y = 3.95 - i * 1.3
        box(ax, 7.7, y, 3.6, 0.95, t + "\n", c, 13)
        txt(ax, 9.5, y + 0.27, d, 11, MUTED)
        seta(ax, 6.62, 4.17, 7.68, y + 0.47, "#8b7fd0", 1.6)
        seta(ax, 6.62, 1.62, 7.68, y + 0.47, "#9b8fd6", 1.5, ls="--")
    # documento de requisitos
    box(ax, 12.1, 1.5, 2.6, 2.8, "Documento de\nrequisitos\n\ncada item com\na sua procedência", "emerald", 13)
    seta(ax, 11.32, 2.9, 12.08, 2.9, INK, 2.2)
    txt(ax, 8.3, 5.25, "extraídos (linha contínua)  e  inferidos (linha tracejada)", 12, MUTED, italic=True)
    salva(f, "requisitos.png")


# ───────────────────────── fábrica × máquina ─────────────────────────
def fabrica():
    f, ax = fig(15, 4.2)
    ax.add_patch(FancyBboxPatch((0.25, 0.3), 9.6, 3.6, boxstyle="round,pad=0,rounding_size=0.2", fc="#f5f0ff", ec=C["violet"][0], lw=2.2))
    txt(ax, 5.05, 3.5, "LangNet — a fábrica: um processo SDD automatizado", 15, C["violet"][0], True)
    et = ["Docu-\nmentos", "Especifi-\ncação", "Dados e\ninterface", "Agentes e\ntarefas", "Rede de\nPetri", "Testes", "Código"]
    for i, t in enumerate(et):
        x = 0.5 + i * 1.33
        box(ax, x, 1.75, 1.15, 1.0, t, "violet", 11)
        if i < 6:
            seta(ax, x + 1.16, 2.25, x + 1.32, 2.25, INK, 1.6, head=10)
    txt(ax, 5.05, 0.95, "cada etapa: origem → geração → revisão → aprovação, com versão", 12, MUTED, italic=True)
    seta(ax, 9.9, 2.25, 10.85, 2.25, C["amber"][0], 4, head=26)
    ax.add_patch(FancyBboxPatch((10.9, 0.3), 3.85, 3.6, boxstyle="round,pad=0,rounding_size=0.2", fc="#ecfdf5", ec=C["emerald"][0], lw=2.2))
    txt(ax, 12.82, 3.5, "A aplicação gerada", 15, C["emerald"][0], True)
    for i, t in enumerate(["telas e backend", "banco de dados", "agentes e ferramentas", "executor da rede"]):
        box(ax, 11.25, 2.65 - i * 0.6, 3.15, 0.48, t, "emerald", 11.5)
    salva(f, "fabrica_maquina.png")


# ───────────────────────── Petri ─────────────────────────
def petri():
    f, ax = fig(15, 6.0)
    def lugar(x, y, n, tok=False, ativo=False):
        ax.add_patch(Circle((x, y), 0.36, fc="#add8e6" if not ativo else "#fde68a", ec=INK, lw=1.8, zorder=3))
        if tok:
            ax.add_patch(Circle((x, y), 0.11, fc=C["rose"][0], zorder=4))
        txt(ax, x, y - 0.62, n, 11, INK)
    def trans(x, y, n):
        ax.add_patch(Rectangle((x - 0.06, y - 0.42), 0.12, 0.84, fc=INK, zorder=3))
        txt(ax, x, y + (0.62 if n != "sincronizar" else -0.66), n, 10.5, MUTED, italic=True)
    def arco(x1, y1, x2, y2, rad=0):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13, color=INK, lw=1.6,
                                     connectionstyle="arc3,rad=%g" % rad, zorder=2))
    def agente(x, y, w, h, nome, cor):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.25", fc=C[cor][1], ec=C[cor][0], lw=2.4, zorder=1))
        txt(ax, x + w / 2, y + h - 0.25, nome, 12.5, C[cor][0], True)
    agente(0.25, 1.9, 2.55, 2.55, "Início", "slate")
    agente(3.2, 3.35, 4.3, 2.35, "Agente de Tradução", "sky")
    agente(3.2, 0.3, 4.3, 2.35, "Agente de Classificação", "violet")
    agente(10.0, 1.9, 2.6, 2.55, "Agente de Alerta", "rose")
    lugar(0.9, 3.0, "caso recebido", tok=True, ativo=True)
    trans(2.2, 3.0, "iniciar")
    lugar(4.0, 4.4, "antibiograma\npronto")
    trans(5.35, 4.4, "traduzir")
    lugar(6.75, 4.4, "vocabulário\ntraduzido")
    lugar(4.0, 1.4, "dados do\ncaso prontos")
    trans(5.35, 1.4, "classificar")
    lugar(6.75, 1.4, "caso\nclassificado")
    trans(8.6, 3.0, "sincronizar")
    lugar(10.6, 3.0, "pronto p/\nalerta")
    trans(11.85, 3.0, "redigir")
    lugar(13.6, 3.0, "alerta\nregistrado")
    arco(1.27, 3.0, 2.13, 3.0)
    arco(2.27, 3.15, 3.63, 4.35, -0.15); arco(2.27, 2.85, 3.63, 1.45, 0.15)
    arco(4.37, 4.4, 5.28, 4.4); arco(5.42, 4.4, 6.38, 4.4)
    arco(4.37, 1.4, 5.28, 1.4); arco(5.42, 1.4, 6.38, 1.4)
    arco(7.12, 4.35, 8.53, 3.15, -0.15); arco(7.12, 1.45, 8.53, 2.85, 0.15)
    arco(8.67, 3.0, 10.23, 3.0); arco(10.97, 3.0, 11.78, 3.0); arco(11.92, 3.0, 13.23, 3.0)
    txt(ax, 9.4, 5.25, "ponto de sincronização:\nsó dispara quando os dois\nramos terminaram", 11.5, C["amber"][0], True)
    txt(ax, 1.45, 5.15, "divide em dois\nramos paralelos", 11.5, C["amber"][0], True)
    ax.add_patch(Circle((12.2, 5.75), 0.11, fc=C["rose"][0])); txt(ax, 12.4, 5.75, "token = estado atual", 11.5, INK, ha="left")
    ax.add_patch(Circle((12.2, 5.3), 0.2, fc="#add8e6", ec=INK)); txt(ax, 12.5, 5.3, "lugar", 11.5, INK, ha="left")
    ax.add_patch(Rectangle((12.15, 4.7), 0.1, 0.32, fc=INK)); txt(ax, 12.5, 4.86, "transição = tarefa", 11.5, INK, ha="left")
    salva(f, "petri.png")


# ───────────────────────── causa-efeito ─────────────────────────
def causa_efeito():
    f, ax = fig(7.6, 5.2)
    causas = [("c1", "antibiograma disponível", 4.3), ("c4", "lista de antimicrobianos", 3.25),
              ("c6", "agente interpreta sem falha", 2.2), ("c7", "3 ou mais classes resistentes", 1.15)]
    for cod, d, y in causas:
        box(ax, 0.15, y - 0.3, 3.0, 0.6, "", "sky")
        txt(ax, 0.3, y, cod, 12, C["sky"][0], True, ha="left")
        txt(ax, 0.75, y, d, 10.5, INK, ha="left")
    ax.add_patch(Circle((4.35, 2.75), 0.3, fc="white", ec=C["indigo"][0], lw=2)); txt(ax, 4.35, 2.75, "E", 13, C["indigo"][0], True)
    for _, _, y in causas:
        ax.plot([3.15, 4.07], [y, 2.75], color=C["indigo"][0], lw=1.6)
    box(ax, 5.3, 3.1, 2.2, 0.9, "e3  Multirresis-\ntente = Sim", "emerald", 11.5)
    box(ax, 5.3, 1.2, 2.2, 0.9, "e4  Multirresis-\ntente = Não", "rose", 11.5)
    seta(ax, 4.65, 2.8, 5.28, 3.5, INK, 1.8)
    ax.plot([3.15, 4.3], [1.15, 1.15], color=INK, lw=1.6)
    ax.add_patch(Circle((4.6, 1.15), 0.3, fc="white", ec=C["rose"][0], lw=2)); txt(ax, 4.6, 1.15, "não", 11, C["rose"][0], True)
    seta(ax, 4.9, 1.2, 5.28, 1.55, INK, 1.8)
    txt(ax, 1.65, 4.95, "CAUSAS (o que chega)", 12, C["sky"][0], True)
    txt(ax, 6.4, 4.95, "EFEITOS (o que o\nsistema responde)", 12, C["emerald"][0], True)
    txt(ax, 3.8, 0.3, "UC-011 · Identificar multirresistência no antibiograma", 10.5, MUTED, italic=True)
    salva(f, "causa_efeito.png")


if __name__ == "__main__":
    escala = {mlp: 1.25, cnn: 1.15, transfer: 1.1, transformer: 1.35, padroes: 1.2, rag: 1.15, langgraph: 1.15,
              autogen: 1.1, protocolos: 1.25, vibe_sdd: 1.2, rastreio: 1.2, requisitos: 1.2, fabrica: 1.15,
              petri: 1.25, causa_efeito: 1.2}
    for fn, k in escala.items():
        FS = k
        fn()
