"""A busca vetorial indexa VÁRIAS colunas, não uma só.

O que dá sentido a um termo do vocabulário quase nunca cabe numa coluna. Indexando
apenas o nome do antimicrobiano, a consulta "antibiótico betalactâmico usado contra
estafilococo" não achava a Oxacilina — o nome sozinho não diz a classe. Medido no
BioByte v5: Oxacilina nem aparecia entre os três primeiros.
"""
import sys, os, re
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fonte = open(raiz + "/backend/agents/langnetagents.py", encoding="utf-8").read()

falhas = []
# o molde emitido tem de ler a lista de colunas, consultar todas e juntar antes de embedar
checks = [
    (r'text_cols = \[c\.strip\(\) for c in os\.getenv\("VECTOR_TEXT_COL"',
     "não lê VECTOR_TEXT_COL como lista"),
    (r'_cols = ", "\.join\(f"`\{c\}`" for c in dict\.fromkeys\(\[id_col\] \+ text_cols\)\)',
     "a consulta não traz todas as colunas pedidas"),
    (r'texto = " — "\.join\(str\(r\.get\(c\)\) for c in text_cols',
     "não junta as colunas antes de embedar"),
]
for padrao, queixa in checks:
    if not re.search(padrao, fonte):
        falhas.append(queixa)

# e o molde não pode ter voltado a embedar uma coluna só
if re.search(r'rv = _embed\(str\(r\.get\(text_col\) or ""\)\)', fonte):
    falhas.append("ainda embeda uma coluna só")

print(f"casos: 4 | passaram: {4 - len(falhas)} | falharam: {len(falhas)}")
for m in falhas: print("  X", m)
sys.exit(1 if falhas else 0)
