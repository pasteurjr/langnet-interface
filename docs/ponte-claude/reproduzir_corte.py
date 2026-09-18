#!/usr/bin/env python3
"""
Reproduz (ou descarta) o corte de respostas longas da Claude Code API.

    python3 reproduzir_corte.py <base_url> <api_key> [linhas]

POR QUE A VERSAO ANTERIOR NAO SERVIA: ela pedia "400 frases de 25 palavras" e o
tamanho da resposta variava com o humor do modelo -- 85 KB de um lado, 38 KB do
outro. E o corte so aparece ACIMA de ~53 KB (medido: 21/32/45/53 KB chegaram
inteiros; 85 KB chegou decepado). Com 38 KB o teste passa mesmo havendo defeito.

Agora o tamanho e DETERMINISTICO: cada linha tem largura fixa, entao
<linhas> x 63 bytes e o tamanho exato esperado. O padrao (1200) da ~76 KB,
bem acima do limiar.

Confere tres coisas:
  1. a PRIMEIRA linha chegou (L000001)
  2. a ULTIMA linha chegou
  3. nenhuma linha do meio faltou
"""
import sys, json, time, re, datetime, httpx

BASE   = (sys.argv[1] if len(sys.argv) > 1 else "https://camerascasas.no-ip.info:4443/v1").rstrip("/")
KEY    = sys.argv[2] if len(sys.argv) > 2 else ""
LINHAS = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
ENCHE  = "=" * 48   # deixa cada linha com largura fixa

PEDIDO = (
    f"Escreva EXATAMENTE {LINHAS} linhas, uma por linha, sem nada antes nem depois.\n"
    f"A linha numero N tem esta forma exata, com o numero em 6 digitos:\n"
    f"L000001 {ENCHE}\n"
    f"L000002 {ENCHE}\n"
    f"...ate L{LINHAS:06d} {ENCHE}\n"
    f"Nao pule numeros, nao comente, nao use cercas de codigo."
)

def conferir(rotulo, texto, finish, seg, arquivo):
    open(arquivo, "w").write(texto)
    achadas = set(int(m) for m in re.findall(r"^L(\d{6})", texto, re.M))
    esperadas = set(range(1, LINHAS + 1))
    faltando = sorted(esperadas - achadas)
    print(f"\n=== {rotulo} ===")
    print(f"  caracteres        : {len(texto):,}   (esperado ~{LINHAS*(len(ENCHE)+9):,})")
    print(f"  finish_reason     : {finish}")
    print(f"  segundos          : {round(seg)}")
    print(f"  linhas recebidas  : {len(achadas):,} de {LINHAS:,}")
    print(f"  L000001 (PRIMEIRA): {'SIM' if 1 in achadas else 'NAO  <<< CORTE NA CABECA'}")
    print(f"  L{LINHAS:06d} (ULTIMA) : {'SIM' if LINHAS in achadas else 'NAO  <<< CORTE NO FIM'}")
    if faltando:
        print(f"  faltando          : {len(faltando)} linhas, da L{faltando[0]:06d} a L{faltando[-1]:06d}")
    print(f"  comeca em         : {texto[:50]!r}")
    print(f"  bruto gravado em  : {arquivo}")
    return 1 in achadas and LINHAS in achadas and not faltando

def sem_fluxo():
    t = time.time()
    r = httpx.Client(verify=False, timeout=3000).post(
        BASE + "/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model": "claude-code", "messages": [{"role": "user", "content": PEDIDO}],
              "max_tokens": 64000})
    d = r.json()
    c = d["choices"][0]
    print(f"  usage             : {d.get('usage')}")
    return conferir("SEM FLUXO", c["message"]["content"] or "", c.get("finish_reason"),
                    time.time() - t, "resposta_sem_fluxo.txt")

def com_fluxo():
    t = time.time(); txt = ""; fin = None
    with httpx.Client(verify=False, timeout=3000).stream(
        "POST", BASE + "/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"model": "claude-code", "messages": [{"role": "user", "content": PEDIDO}],
              "max_tokens": 64000, "stream": True}) as r:
        for linha in r.iter_lines():
            if not linha.startswith("data: "): continue
            d = linha[6:].strip()
            if d == "[DONE]": break
            try: j = json.loads(d)
            except Exception: continue
            e = j["choices"][0]
            txt += (e.get("delta") or {}).get("content", "") or ""
            fin = e.get("finish_reason") or fin
    return conferir("COM FLUXO", txt, fin, time.time() - t, "resposta_com_fluxo.txt")

if __name__ == "__main__":
    print(f"inicio: {datetime.datetime.now().astimezone().isoformat()}  |  base={BASE}  |  linhas={LINHAS}")
    a = sem_fluxo()
    b = com_fluxo()
    print(f"\nfim: {datetime.datetime.now().astimezone().isoformat()}")
    print(f"\nVEREDITO  sem fluxo: {'INTEIRO' if a else 'CORTADO'}   |   com fluxo: {'INTEIRO' if b else 'CORTADO'}")
