"""O leitor de saída do modelo aceita JSON ENVOLVIDO em texto.

O `_coerce_json` escrito pelo modelo só lia quando a resposta COMEÇAVA com chave.
Mas o modelo costuma explicar antes ou envolver em bloco de código — e aí a resposta
inteira era descartada como "saída não parseável", com justificativa vazia. Medido no
BioByte v5: a tradução do resultado do laboratório falhava de forma intermitente.
"""
import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
from agents.langnetagents import _reforcar_leitura_de_json as reforcar

# o leitor FRACO que o modelo escreve em algumas rodadas: só lê o que COMEÇA com chave
ADAPTERS_FRACO = '''import json
def _coerce_json(result):
    if result is None:
        return None
    if isinstance(result, str):
        texto = result.strip()
        if texto.startswith("{") or texto.startswith("["):
            try:
                return json.loads(texto)
            except Exception:
                return result
    return result


# e noutras rodadas ele escreve com OUTRO nome — o conserto tem de pegar os dois
def _coerce_result(result):
    return _coerce_json(result)
'''

saida = reforcar(ADAPTERS_FRACO)
ns = {}
exec(compile(saida, "adapters.py", "exec"), ns)
ler = ns["_coerce_json"]
ler2 = ns["_coerce_result"]  # o outro nome que o modelo usa

CASOS = [
    ('{"aproveitavel": true, "n": 4}', {"aproveitavel": True, "n": 4}, "JSON puro"),
    ('Segue o resultado:\n{"aproveitavel": true, "n": 4}', {"aproveitavel": True, "n": 4},
     "JSON depois de uma frase"),
    ('```json\n{"aproveitavel": true, "n": 4}\n```', {"aproveitavel": True, "n": 4},
     "JSON em bloco de codigo"),
    ('Analisei o caso.\n```json\n{"n": 1}\n```\nEspero ter ajudado.', {"n": 1},
     "JSON em bloco, com texto antes e depois"),
    ('[{"a": 1}]', [{"a": 1}], "lista"),
]
falhas = []
for entrada, esperado, nome in CASOS:
    r = ler(entrada)
    if r != esperado:
        falhas.append(f"{nome}: leu {str(r)[:70]}, esperado {esperado}")

# e uma resposta SEM json nenhum não pode virar dicionário inventado
# o conserto tem de valer para QUALQUER nome de leitor que o modelo tenha usado
if ler2('Segue:\n{"n": 9}') != {"n": 9}:
    falhas.append("o leitor com outro nome nao foi reforcado")

r = ler("Não consegui obter o dado.")
if not isinstance(r, str):
    falhas.append("texto sem JSON virou estrutura — não pode inventar")

print(f"casos: {len(CASOS)+2} | passaram: {len(CASOS)+2-len(falhas)} | falharam: {len(falhas)}")
for m in falhas: print("  X", m)
sys.exit(1 if falhas else 0)
