# -*- coding: utf-8 -*-
"""Figuras novas da V14 (busca vetorial e LangChain). Usa os mesmos auxiliares da V11."""
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch
import diagramas_v11 as G
from diagramas_v11 import fig, box, seta, txt, C, INK, MUTED
from pathlib import Path

OUT = Path(__file__).resolve().parent / "diagrams_v14"


def salva(f, nome):
    f.savefig(OUT / nome, dpi=200, facecolor="white")
    print("ok", nome)


def busca_vetorial():
    f, ax = fig(15, 6.2)
    # ── esquerda: busca convencional ──
    ax.add_patch(FancyBboxPatch((0.25, 0.3), 6.4, 5.6, boxstyle="round,pad=0,rounding_size=0.2", fc="#f6f7fa", ec=C["slate"][0], lw=2))
    txt(ax, 3.45, 5.5, "Busca convencional  ·  por palavra", 16, C["slate"][0], True)
    box(ax, 0.6, 4.45, 5.7, 0.6, "pergunta: “bacteremia por cateter”", "slate", 13, bold=False)
    txt(ax, 3.45, 4.05, "procura as mesmas palavras no índice", 11.5, MUTED, italic=True)
    docs = [("acha", "“bacteremia confirmada em hemocultura”", "emerald"),
            ("NÃO acha", "“infecção de corrente sanguínea por cateter”", "rose"),
            ("não acha", "“fratura de fêmur em idoso”", "gray")]
    y = 3.35
    for tag, t, cor in docs:
        box(ax, 0.6, y - 0.28, 5.7, 0.56, "", cor, 11.5)
        txt(ax, 0.8, y, tag, 11.5, C[cor][0], True, ha="left")
        txt(ax, 2.05, y, t, 11, INK, ha="left")
        y -= 0.72
    txt(ax, 3.45, 0.75, "perde o documento certo, porque ele\nusa outras palavras para a mesma coisa", 12.5, C["rose"][0], True)
    # ── direita: busca vetorial ──
    ax.add_patch(FancyBboxPatch((6.95, 0.3), 7.8, 5.6, boxstyle="round,pad=0,rounding_size=0.2", fc="#fdf2f5", ec=C["rose"][0], lw=2))
    txt(ax, 10.85, 5.5, "Busca vetorial (RAG)  ·  por sentido", 16, C["rose"][0], True)
    box(ax, 7.25, 4.45, 3.4, 0.6, "texto → embedding", "rose", 13)
    txt(ax, 12.7, 4.75, "[0,12  −0,83  0,40  …]\n1.536 números", 12, INK, ha="center")
    seta(ax, 10.7, 4.75, 11.3, 4.75, INK, 1.8)
    # espaço vetorial (2D, ilustrativo)
    cx, cy = 9.1, 2.3
    ax.add_patch(FancyBboxPatch((7.25, 0.55), 4.6, 3.55, boxstyle="round,pad=0,rounding_size=0.1", fc="white", ec="#d6dbe6", lw=1.5))
    txt(ax, 9.55, 3.9, "espaço de significado", 11, MUTED, italic=True)
    perto = [(8.45, 2.95, "bacteremia", 0.3), (9.8, 2.75, "ICS por cateter", 0.3), (9.0, 2.0, "infecção de\ncorrente sanguínea", -0.36)]
    longe = [(11.1, 3.35, "fratura"), (11.2, 1.0, "dieta"), (7.7, 0.95, "vacina")]
    ax.add_patch(Circle((cx, cy + 0.05), 1.05, fc="none", ec=C["rose"][0], lw=1.8, ls="--"))
    for x, y, t, dy in perto:
        ax.add_patch(Circle((x, y), 0.09, fc=C["emerald"][0]))
        txt(ax, x, y + dy, t, 10.5, C["emerald"][0], True)
    for x, y, t in longe:
        ax.add_patch(Circle((x, y), 0.08, fc="#9aa3b5"))
        txt(ax, x, y - 0.25, t, 10.5, MUTED)
    ax.add_patch(Circle((cx, cy + 0.2), 0.13, fc=C["rose"][0]))
    txt(ax, cx, cy - 0.12, "pergunta", 10.5, C["rose"][0], True)
    txt(ax, 13.3, 2.55, "busca os\nvizinhos mais\npróximos\n(similaridade\nde cosseno)", 12, INK, True)
    txt(ax, 10.85, 0.0 + 0.35, "", 1)
    salva(f, "busca_vetorial.png")


def langchain():
    f, ax = fig(7.4, 5.4)
    c = "sky"
    txt(ax, 3.7, 5.05, "uma cadeia: peças prontas ligadas por  |", 13, INK, True)
    box(ax, 0.25, 3.35, 2.0, 0.85, "Prompt\n(modelo de texto)", c, 12)
    box(ax, 2.7, 3.35, 2.0, 0.85, "Modelo\n(LLM)", c, 12)
    box(ax, 5.15, 3.35, 2.0, 0.85, "Parser\n(saída)", c, 12)
    seta(ax, 2.27, 3.78, 2.68, 3.78, INK, 2); seta(ax, 4.72, 3.78, 5.13, 3.78, INK, 2)
    txt(ax, 2.47, 4.3, "|", 18, C["amber"][0], True); txt(ax, 4.92, 4.3, "|", 18, C["amber"][0], True)
    box(ax, 0.25, 1.35, 2.0, 0.85, "Recuperador\n(índice vetorial)", "rose", 12)
    box(ax, 2.7, 1.35, 2.0, 0.85, "Ferramenta\n(@tool)", "amber", 12)
    box(ax, 5.15, 1.35, 2.0, 0.85, "Memória\n(histórico)", "violet", 12)
    for x in (1.25, 3.7, 6.15):
        seta(ax, x, 2.22, x if x != 6.15 else 6.15, 3.33, MUTED, 1.4, ls="--")
    txt(ax, 3.7, 0.55, "as peças de baixo entram na cadeia quando preciso", 11.5, MUTED, italic=True)
    salva(f, "langchain.png")


if __name__ == "__main__":
    G.FS = 1.3
    busca_vetorial()
    G.FS = 1.15
    langchain()
