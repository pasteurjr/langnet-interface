"""Quem executa cada passo do caso de uso — leitura, conferência e anotação da coluna "Executado por".

POR QUE EXISTE (padrão de interação com agentes v1.0, aprovado em 03/10/2026):
cada passo dos fluxos principal, alternativos e de exceção diz QUEM produz a resposta do sistema:

  pronto         molde determinístico do gerador (login, cadastro, relatório, auditoria)
  código gerado  regra própria do caso de uso, escrita UMA vez pelo modelo como código comum
  agente         tarefa de IA no framework (interpretar, classificar, decidir, recomendar, redigir)

Sem essa coluna, as etapas seguintes adivinhavam: a Interface inventava 103 nomes de tarefa que
não existiam, a Geração de Código deixava 20 telas com "Ação não vinculada" e as mensagens de
exceção viravam campos de exibição. A coluna é a fonte única: Agentes & Tarefas só cria tarefa
para passo `agente`; a Geração de Código faz molde para `pronto`, rota para `código gerado` e
chamada ao framework para `agente`.

O modelo NÃO reescreve os fluxos: na anotação ele só responde, em JSON, o executor de cada passo
(pelo id do passo); quem insere a coluna no texto é este programa. Por isso nenhuma linha do
fluxo pode ser alterada pelo modelo, e a conferência é feita por programa.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Tuple

from prompts.generate_ui_spec import _UC_BLOCK_RE

VALORES = ("pronto", "código gerado", "agente")
COLUNA = "Executado por"

# nomes das três seções de fluxo dentro do caso de uso
_SECOES = (
    ("principal", r'#+\s*Fluxo Principal'),
    ("alternativo", r'#+\s*Fluxos?\s+Alternativos?'),
    ("excecao", r'#+\s*Fluxos?\s+de\s+Exce[çc][ãa]o'),
)


def normalizar_executor(valor: str) -> Optional[str]:
    """'Código gerado', '`codigo-gerado`', 'AGENTE' → valor canônico; outro texto → None."""
    v = re.sub(r'[`*_]', '', str(valor or '')).strip().lower()
    v = v.replace('-', ' ').replace('codigo', 'código')
    v = re.sub(r'\s+', ' ', v)
    return v if v in VALORES else None


# ── tabelas markdown ─────────────────────────────────────────────────────────

def _celulas(linha: str) -> List[str]:
    s = linha.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [c.strip() for c in s.split('|')]


def _eh_separador(linha: str) -> bool:
    return bool(re.match(r'^\s*\|?\s*:?-{2,}', linha)) and set(linha.replace('|', '').strip()) <= set('-: ')


def _secao(corpo: str, cabecalho_re: str) -> Optional[Tuple[int, int]]:
    """Span (início, fim) do texto de uma sub-seção, do fim do título até o próximo título."""
    m = re.search(cabecalho_re + r'[^\n]*\n', corpo, re.I)
    if not m:
        return None
    resto = corpo[m.end():]
    f = re.search(r'\n#+\s', resto)
    return m.end(), m.end() + (f.start() if f else len(resto))


def _tabela(texto: str) -> Tuple[Optional[List[str]], List[Tuple[int, List[str]]]]:
    """Primeira tabela do texto: (cabeçalho, [(índice da linha no texto, células)])."""
    linhas = texto.split('\n')
    cab, corpo, i = None, [], 0
    while i < len(linhas):
        if linhas[i].strip().startswith('|') and i + 1 < len(linhas) and _eh_separador(linhas[i + 1]):
            cab = _celulas(linhas[i])
            j = i + 2
            while j < len(linhas) and linhas[j].strip().startswith('|'):
                corpo.append((j, _celulas(linhas[j])))
                j += 1
            break
        i += 1
    return cab, corpo


def _col(cab: List[str], *nomes: str) -> Optional[int]:
    for k, c in enumerate(cab):
        cl = re.sub(r'[*`]', '', c).strip().lower()
        if any(n in cl for n in nomes):
            return k
    return None


# ── mensagens: texto que o usuário LÊ, não elemento da tela ─────────────────

_ASPAS_RE = re.compile(r'\*\*\s*["“]([^"”]{2,300})["”]\s*\*\*|["“]([^"”]{2,300})["”]')
_GATILHO_MSG = re.compile(r'(mensagem|aviso|alerta|informa|notifica|texto|exibe:|avisa)', re.I)


def extrair_mensagens(resposta: str) -> List[str]:
    """Mensagens que o sistema mostra ao usuário, citadas entre aspas na Resposta do Sistema.

    Separa a MENSAGEM ("Não há antibiograma disponível para avaliar multirresistência.") do NOME
    de um elemento ("Multirresistente", "Ver antibiograma completo"): é mensagem o texto citado
    logo depois de "mensagem/aviso/alerta…", ou uma frase que termina em pontuação. Esta
    distinção é o que impede a mensagem de exceção de virar um campo de exibição na Interface.
    """
    msgs = []
    for m in _ASPAS_RE.finditer(resposta or ''):
        t = (m.group(1) or m.group(2) or '').strip()
        antes = (resposta or '')[max(0, m.start() - 50):m.start()]
        frase = t.endswith(('.', '!', '?', '…')) and len(t.split()) >= 3
        if _GATILHO_MSG.search(antes) or frase:
            if t not in msgs:
                msgs.append(t)
    return msgs


# ── leitura ──────────────────────────────────────────────────────────────────

def _natureza(corpo: str) -> str:
    m = re.search(r'\|\s*\**Natureza\**\s*\|\s*([^|\n]+)', corpo, re.I)
    v = (m.group(1) if m else '').lower()
    return 'agêntica' if 'agêntic' in v or 'agentic' in v else ('convencional' if 'convencional' in v else '')


def passos_do_uc(corpo: str) -> List[Dict]:
    """Os passos dos três fluxos de um caso de uso, cada um com o seu executor (ou None)."""
    passos = []
    for fluxo, cab_re in _SECOES:
        span = _secao(corpo, cab_re)
        if not span:
            continue
        cab, linhas = _tabela(corpo[span[0]:span[1]])
        if not cab:
            continue
        i_id = 0
        i_resp = _col(cab, 'resposta')
        i_acao = _col(cab, 'ação do ator', 'acao do ator')
        i_cond = _col(cab, 'condição', 'condicao', 'erro', 'problema')
        i_exec = _col(cab, 'executado por')
        for _, cel in linhas:
            def c(i):
                return cel[i] if i is not None and i < len(cel) else ''
            resposta = c(i_resp)
            passos.append({
                'fluxo': fluxo,
                'id': re.sub(r'[*`]', '', c(i_id)).strip(),
                'condicao': c(i_cond) if fluxo != 'principal' else '',
                'acao': c(i_acao),
                'resposta': resposta,
                'executado_por': normalizar_executor(c(i_exec)) if i_exec is not None else None,
                'tem_coluna': i_exec is not None,
                'mensagens': extrair_mensagens(resposta),
            })
    return passos


def blocos(doc: str) -> List[Dict]:
    """Casos de uso do documento: id, nome, natureza, corpo e span — sem repetir id."""
    vistos, out = set(), []
    for m in _UC_BLOCK_RE.finditer(doc or ''):
        uc = m.group(1).strip()
        if uc in vistos:
            continue
        vistos.add(uc)
        out.append({'uc': uc, 'nome': m.group(2).strip().strip('*').strip(), 'corpo': m.group(3),
                    'inicio_corpo': m.start(3), 'fim_corpo': m.end(3),
                    'natureza': _natureza(m.group(3))})
    return out


def extrair_execucao(doc: str) -> List[Dict]:
    """Para cada caso de uso: natureza e os passos com quem os executa."""
    return [{'uc': b['uc'], 'nome': b['nome'], 'natureza': b['natureza'],
             'passos': passos_do_uc(b['corpo'])} for b in blocos(doc)]


# ── conferência (programa, não modelo) ──────────────────────────────────────

def conferir_uc(uc: Dict) -> List[str]:
    """Problemas de UM caso de uso já anotado. Lista vazia = aprovado."""
    p = []
    passos = uc['passos']
    if not passos:
        return [f"{uc['uc']}: nenhum fluxo encontrado"]
    for s in passos:
        if not s['tem_coluna']:
            p.append(f"{uc['uc']} {s['fluxo']} {s['id']}: falta a coluna \"{COLUNA}\"")
        elif s['resposta'].strip() and not s['executado_por']:
            p.append(f"{uc['uc']} {s['fluxo']} {s['id']}: executor ausente ou fora de {VALORES}")
    principais = [s for s in passos if s['fluxo'] == 'principal']
    if uc['natureza'] == 'convencional' and any(s['executado_por'] == 'agente' for s in passos):
        p.append(f"{uc['uc']}: caso de uso convencional com passo 'agente'")
    if uc['natureza'] == 'agêntica' and not any(s['executado_por'] == 'agente' for s in principais):
        p.append(f"{uc['uc']}: caso de uso agêntico sem nenhum passo 'agente' no fluxo principal")
    return p


def conferir_execucao(doc: str) -> Dict:
    ucs = extrair_execucao(doc)
    problemas, por_valor, msgs = [], {v: 0 for v in VALORES}, 0
    for uc in ucs:
        problemas += conferir_uc(uc)
        for s in uc['passos']:
            if s['executado_por']:
                por_valor[s['executado_por']] += 1
            if s['fluxo'] == 'excecao':
                msgs += len(s['mensagens'])
    return {'casos_de_uso': len(ucs), 'problemas': problemas, 'por_valor': por_valor,
            'mensagens_de_excecao': msgs, 'aprovado': not problemas and bool(ucs)}


# ── anotação: o modelo diz o executor, o programa escreve a coluna ──────────

REGRA_EXECUTOR = """Para CADA passo, diga quem produz a "Resposta do Sistema":

- "pronto": o que todo sistema tem e o gerador já sabe fazer por molde — login e sessão; cadastrar,
  alterar, listar, filtrar, abrir e apagar registro; gravar em trilha de auditoria; relatório ou
  painel que só mostra o que está no banco; exibir mensagem de erro de validação de formulário;
  navegar entre telas.
- "código gerado": regra própria DESTE caso de uso que um programa comum resolve lendo o banco e
  seguindo uma regra escrita — cálculo, conferência, filtro com condição de negócio, importação de
  serviço externo, montagem e envio de notificação, decidir qual mensagem mostrar a partir de dado.
- "agente": só quando é preciso INTERPRETAR, CLASSIFICAR, DECIDIR, RECOMENDAR, ESTIMAR ou REDIGIR a
  partir de informação que não cabe numa regra fechada — a decisão do agente do caso de uso.

Teste: "um programa comum, sem modelo de linguagem, resolveria isso lendo o banco e seguindo uma
regra escrita?" Sim → "pronto" ou "código gerado". Não → "agente".
Caso de uso CONVENCIONAL nunca tem "agente". Caso de uso AGÊNTICO tem "agente" no(s) passo(s) do
fluxo principal em que a decisão do agente acontece — e só neles; mostrar o resultado na tela,
gravar e avisar continua sendo "pronto" ou "código gerado". Nos fluxos de exceção, a resposta é
quase sempre a tela mostrando uma mensagem: "pronto" (erro de formulário/acesso) ou "código gerado"
(condição de negócio); "agente" só se o próprio agente redige a resposta."""


def montar_pedido(uc: Dict, corpo: str, decisao: str = '') -> str:
    linhas = []
    for s in uc['passos']:
        txt = s['acao'] or s['condicao']
        linhas.append(f"- [{s['fluxo']} {s['id']}] {('condição: ' + s['condicao'] + ' | ') if s['condicao'] and s['acao'] else ''}"
                      f"ator: {txt} | sistema: {s['resposta']}")
    return f"""Caso de uso {uc['uc']} — {uc['nome']}
Natureza: {uc['natureza'] or 'não declarada'}
Decisão do agente: {decisao or 'não se aplica'}

Passos:
{chr(10).join(linhas)}

{REGRA_EXECUTOR}

Responda SÓ com um objeto JSON, sem comentário, com uma chave por passo no formato "fluxo id"
exatamente como entre colchetes acima, e o valor "pronto", "código gerado" ou "agente".
Exemplo: {{"principal 1": "pronto", "principal 2": "agente", "excecao E1": "código gerado"}}"""


def _decisao(corpo: str) -> str:
    m = re.search(r'\|\s*\**Decisão do Agente\**\s*\|\s*([^|\n]+)', corpo, re.I)
    return (m.group(1).strip() if m else '')


def ler_resposta(texto: str, uc: Dict) -> Tuple[Dict[str, str], List[str]]:
    """JSON do modelo → {chave: valor canônico} + problemas (chave faltando, valor inválido)."""
    t = (texto or '').strip()
    t = re.sub(r'^```(?:json)?|```$', '', t, flags=re.M).strip()
    m = re.search(r'\{.*\}', t, re.S)
    try:
        bruto = json.loads(m.group(0)) if m else {}
    except Exception:
        bruto = {}
    out, prob = {}, []
    if not bruto:
        return {}, ['resposta do modelo não é um objeto JSON']
    norm = {re.sub(r'\s+', ' ', str(k)).strip().lower(): v for k, v in bruto.items()}
    for s in uc['passos']:
        chave = f"{s['fluxo']} {s['id']}"
        v = norm.get(chave.lower())
        if v is None:
            if s['resposta'].strip():
                prob.append(f'faltou o passo "{chave}"')
            continue
        nv = normalizar_executor(v)
        if not nv:
            prob.append(f'valor inválido para "{chave}": {v!r}')
            continue
        out[chave] = nv
    return out, prob


def escrever_coluna(corpo: str, executores: Dict[str, str]) -> str:
    """Insere (ou atualiza) a coluna "Executado por" nas três tabelas do corpo do caso de uso.

    Só mexe na última coluna: nenhuma célula existente é alterada.
    """
    novo = corpo
    for fluxo, cab_re in _SECOES:
        span = _secao(novo, cab_re)
        if not span:
            continue
        texto = novo[span[0]:span[1]]
        cab, linhas_tab = _tabela(texto)
        if not cab:
            continue
        linhas = texto.split('\n')
        i_cab = linhas_tab[0][0] - 2 if linhas_tab else None
        if i_cab is None:
            # tabela sem linhas: só acrescenta a coluna ao cabeçalho
            for k, l in enumerate(linhas):
                if l.strip().startswith('|') and k + 1 < len(linhas) and _eh_separador(linhas[k + 1]):
                    i_cab = k
                    break
        i_exec = _col(cab, 'executado por')
        if i_exec is None:
            linhas[i_cab] = linhas[i_cab].rstrip().rstrip('|').rstrip() + f' | {COLUNA} |'
            linhas[i_cab + 1] = linhas[i_cab + 1].rstrip().rstrip('|').rstrip() + ' |---|'
        for j, cel in linhas_tab:
            pid = re.sub(r'[*`]', '', cel[0]).strip()
            v = executores.get(f'{fluxo} {pid}') or '—'
            if i_exec is None:
                linhas[j] = linhas[j].rstrip().rstrip('|').rstrip() + f' | {v} |'
            else:
                cel2 = list(cel)
                while len(cel2) <= i_exec:
                    cel2.append('')
                cel2[i_exec] = v
                linhas[j] = '| ' + ' | '.join(cel2) + ' |'
        novo = novo[:span[0]] + '\n'.join(linhas) + novo[span[1]:]
    return novo


def anotar_uc(doc: str, uc_id: str, responder) -> Dict:
    """Anota UM caso de uso. `responder(pedido, observacao)` chama o modelo e devolve o texto.

    Até duas tentativas; a segunda leva os problemas da primeira. Devolve
    {'doc': novo_doc, 'mudou': bool, 'problemas': [...], 'executores': {...}}.
    """
    b = next((x for x in blocos(doc) if x['uc'] == uc_id), None)
    if not b:
        return {'doc': doc, 'mudou': False, 'problemas': [f'{uc_id} não encontrado'], 'executores': {}}
    uc = {'uc': b['uc'], 'nome': b['nome'], 'natureza': b['natureza'], 'passos': passos_do_uc(b['corpo'])}
    if not uc['passos']:
        return {'doc': doc, 'mudou': False, 'problemas': [f'{uc_id}: sem fluxos'], 'executores': {}}
    pedido = montar_pedido(uc, b['corpo'], _decisao(b['corpo']))
    observacao, problemas, executores = '', [], {}
    for _ in range(2):
        executores, problemas = ler_resposta(responder(pedido, observacao), uc)
        if not problemas:
            corpo_novo = escrever_coluna(b['corpo'], executores)
            uc2 = {**uc, 'passos': passos_do_uc(corpo_novo)}
            problemas = conferir_uc(uc2)
            # nenhuma célula original pode ter mudado
            if not problemas:
                antes = [(s['fluxo'], s['id'], s['acao'], s['resposta']) for s in uc['passos']]
                depois = [(s['fluxo'], s['id'], s['acao'], s['resposta']) for s in uc2['passos']]
                if antes != depois:
                    problemas = ['o texto dos fluxos mudou ao escrever a coluna']
            if not problemas:
                doc_novo = doc[:b['inicio_corpo']] + corpo_novo + doc[b['fim_corpo']:]
                return {'doc': doc_novo, 'mudou': doc_novo != doc, 'problemas': [], 'executores': executores}
        observacao = 'Sua resposta anterior foi recusada por estes motivos: ' + '; '.join(problemas)
    return {'doc': doc, 'mudou': False, 'problemas': problemas, 'executores': executores}
