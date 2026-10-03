"""Ficha da tela — quem executa cada ação, onde fica cada agente, quais mensagens a tela mostra.

Padrão de interação com agentes v1.0 (03/10/2026). A Especificação diz, em cada passo, quem
executa (`pronto` · `código gerado` · `agente`) — ver `langnetexecucao`. Esta etapa liga a TELA
a esses passos:

- cada ação (botão) aponta para o CASO DE USO e o PASSO, nunca para um nome de tarefa inventado
  (medido no BioByte v5: 103 ações apontavam para nomes que não existiam em lugar nenhum);
- o executor da ação é copiado da Especificação pelo PROGRAMA — o modelo só escolhe o passo;
- cada passo `agente` vira um BLOCO de agente na tela, numa de três formas (decisão · auxílio de
  campo · ação da tela), na posição do passo;
- as mensagens dos fluxos alternativos e de exceção ficam como MENSAGENS (aparecem quando o caso
  acontece), não como campos de exibição;
- nenhum dado sensível (senha, hash, token, segredo) aparece em tela.

E o protótipo passa a DENUNCIAR: ao clicar, cada botão diz quem o executa; botão sem executor
aparece marcado. O defeito que antes só aparecia no aplicativo aparece na aprovação da etapa.
"""
from __future__ import annotations

import html as _html
import json
import re
from typing import Dict, List, Optional, Tuple

from agents.langnetexecucao import passos_do_uc, extrair_mensagens

FORMAS_AGENTE = ("decisao", "campo", "tela")
NAVEGACAO = "navegação"

# dado que nunca aparece em tela (pode existir como campo de ENTRADA de senha no login/troca)
SENSIVEL_RE = re.compile(r'(senha|password|passwd|hash|token|segredo|secret|api[_ ]?key|chave[_ ]?api|credencia)', re.I)


def chave_passo(passo: Dict) -> str:
    return f"{passo['fluxo']} {passo['id']}"


def passos_para_prompt(uc_raw: str) -> str:
    """Lista dos passos do caso de uso, com o executor, para o modelo escolher o passo de cada ação."""
    linhas = []
    for p in passos_do_uc(uc_raw or ""):
        ex = p["executado_por"] or "não declarado"
        txt = (p["acao"] or p["condicao"] or "").strip()
        linhas.append(f"- [{chave_passo(p)}] ({ex}) ator: {txt[:220]} | sistema: {p['resposta'][:260]}")
    return "\n".join(linhas) or "(o caso de uso não tem fluxos legíveis)"


# ── pós-processamento (programa) ─────────────────────────────────────────────

def _norm(s: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[*`"“”]', '', str(s or ''))).strip().lower()


def _mensagens_do_uc(passos: List[Dict]) -> List[Dict]:
    out = []
    for p in passos:
        if p["fluxo"] == "principal":
            continue
        for m in p["mensagens"]:
            out.append({"passo": chave_passo(p), "quando": (p["condicao"] or p["acao"])[:200],
                        "texto": m, "executado_por": p["executado_por"]})
    return out


def aplicar_ficha(screen: Dict, uc_raw: str, uc_id: str) -> Dict:
    """Completa a tela com a ficha tirada da Especificação. Muda `screen` no lugar e devolve um
    relatório do que foi feito. Nada aqui é decidido pelo modelo."""
    passos = passos_do_uc(uc_raw or "")
    por_chave = {chave_passo(p): p for p in passos}
    rel = {"acoes": 0, "sem_executor": [], "agentes_sem_bloco": [], "sensiveis_removidos": [],
           "mensagens_que_eram_campo": []}

    # 1. ações → caso de uso + passo; executor copiado do passo
    acoes = []
    for i, a in enumerate(screen.get("actions") or []):
        a = dict(a)
        a.setdefault("id", f"acao-{i + 1}")
        if a.get("navegar_para") or a.get("kind") == "navigate":
            a["executado_por"] = NAVEGACAO
            a.pop("passo", None)
        else:
            a["uc"] = a.get("uc") or uc_id
            chave = _norm(a.get("passo"))
            p = por_chave.get(next((k for k in por_chave if _norm(k) == chave), ""))
            if p and p["executado_por"]:
                a["passo"] = chave_passo(p)
                a["executado_por"] = p["executado_por"]
                a["resposta"] = p["resposta"][:400]
            else:
                a["executado_por"] = None
                rel["sem_executor"].append(a.get("label") or a["id"])
        # campos antigos que levavam o nome inventado
        a.pop("target", None)
        a.pop("kind", None)
        acoes.append(a)
    screen["actions"] = acoes
    rel["acoes"] = len(acoes)

    # 2. blocos de agente: um por passo `agente`, com forma válida
    blocos = {(_norm(b.get("passo"))): b for b in (screen.get("agentes") or []) if b.get("passo")}
    novos = []
    # Um bloco por passo `agente` do FLUXO PRINCIPAL. O passo `agente` de um fluxo alternativo
    # é outro desfecho da MESMA decisão (ex.: "conclui pela ausência de multirresistência"): vira
    # variante do bloco principal, não um segundo bloco na tela.
    principais = [p for p in passos if p["executado_por"] == "agente" and p["fluxo"] == "principal"]
    variantes = [chave_passo(p) for p in passos if p["executado_por"] == "agente" and p["fluxo"] != "principal"]
    if not principais:
        principais = [p for p in passos if p["executado_por"] == "agente"][:1]
        variantes = [v for v in variantes if principais and v != chave_passo(principais[0])]
    for p in principais:
        k = chave_passo(p)
        b = dict(blocos.get(_norm(k)) or {})
        if not b:
            rel["agentes_sem_bloco"].append(k)
        b["passo"] = k
        b["uc"] = uc_id
        if b.get("forma") not in FORMAS_AGENTE:
            b["forma"] = "decisao"
        b.setdefault("rotulo", (p["acao"] or "Agente")[:80])
        b["resposta"] = p["resposta"][:400]
        if p is principais[0] and variantes:
            b["variantes"] = variantes
        if not any(a.get("passo") == k for a in acoes):
            # o passo agente precisa de quem o dispare (salvo se o próprio sistema o aciona)
            b.setdefault("disparo", "automatico" if re.search(r'\bo sistema\b|\bao concluir\b|automaticamente', p["acao"], re.I) else "botao")
        novos.append(b)
    screen["agentes"] = novos

    # 3. mensagens: vêm da Especificação; componente de exibição que só repete a mensagem sai
    msgs = _mensagens_do_uc(passos)
    textos = {_norm(m["texto"]) for m in msgs}
    comps = []
    for c in screen.get("components") or []:
        if _repete_mensagem(c, textos):
            rel["mensagens_que_eram_campo"].append(c.get("label") or c.get("field"))
            continue
        comps.append(c)
    screen["components"] = comps
    screen["mensagens"] = msgs

    # 4. dado sensível nunca em tela (campo de ENTRADA de senha é permitido: type password)
    comps = []
    for c in screen.get("components") or []:
        alvo = f"{c.get('field') or ''} {c.get('bindTo') or ''} {c.get('label') or ''}"
        if SENSIVEL_RE.search(alvo) and c.get("type") not in ("password",):
            if c.get("type") in ("text",) and re.search(r'senha|password', alvo, re.I) and not re.search(r'hash', alvo, re.I):
                c = dict(c, type="password")
            else:
                rel["sensiveis_removidos"].append(c.get("label") or c.get("field"))
                continue
        if c.get("type") == "table":
            cols = (c.get("props") or {}).get("columns")
            if isinstance(cols, list):
                limpas = [x for x in cols if not SENSIVEL_RE.search(json.dumps(x, ensure_ascii=False))]
                if len(limpas) != len(cols):
                    rel["sensiveis_removidos"].append(f"{c.get('field')}: coluna sensível")
                    c = dict(c, props=dict(c.get("props") or {}, columns=limpas))
        comps.append(c)
    screen["components"] = comps
    html_ = screen.get("mockup_html") or ""
    if html_:
        screen["mockup_html"], cortes = remover_colunas_sensiveis(html_)
        if cortes:
            rel["sensiveis_removidos"] += [f"coluna \"{x}\" do desenho" for x in cortes]

    screen["ficha"] = rel
    return rel


def _repete_mensagem(c: Dict, textos: set) -> bool:
    """O componente é só a mensagem de um fluxo posta como campo? Só conta quando o RÓTULO (ou o
    valor de exemplo) É a mensagem — frase de 4+ palavras quase igual a ela. Rótulo curto como
    "Nome" ou "E-mail" é campo de verdade, mesmo que a palavra apareça dentro de uma mensagem
    (erro medido em 03/10/2026: os campos Nome e E-mail da tela de Usuários foram retirados)."""
    if c.get("type") not in ("readonly", "text", "textarea", "alert", "message"):
        return False
    props = c.get("props") or {}
    for cand in (c.get("label"), props.get("text"), props.get("value"), props.get("exemplo")):
        r = _norm(cand)
        if len(r.split()) < 4:
            continue
        for t in textos:
            if r == t or (r in t and len(r) >= 0.7 * len(t)) or (t in r and len(t) >= 0.7 * len(r)):
                return True
    return False


def remover_colunas_sensiveis(doc: str) -> Tuple[str, List[str]]:
    """Tira do desenho as colunas de tabela cujo cabeçalho é dado sensível (ex.: SENHA HASH)."""
    cortes = []

    def tabela(m):
        t = m.group(0)
        ths = re.findall(r'<th\b[^>]*>(.*?)</th>', t, re.S | re.I)
        ruins = [i for i, h in enumerate(ths) if SENSIVEL_RE.search(re.sub(r'<[^>]+>', '', h))]
        if not ruins:
            return t
        cortes.extend(re.sub(r'<[^>]+>', '', ths[i]).strip() for i in ruins)

        def linha(mm):
            r = mm.group(0)
            cel = list(re.finditer(r'<t([hd])\b[^>]*>.*?</t\1>', r, re.S | re.I))
            for i in sorted(ruins, reverse=True):
                if i < len(cel):
                    r = r[:cel[i].start()] + r[cel[i].end():]
            return r
        return re.sub(r'<tr\b.*?</tr>', linha, t, flags=re.S | re.I)

    return re.sub(r'<table\b.*?</table>', tabela, doc, flags=re.S | re.I), cortes


# ── conferência (programa) ───────────────────────────────────────────────────

def conferir_tela(screen: Dict) -> List[str]:
    """Problemas da tela segundo o padrão. Lista vazia = aprovada."""
    p = []
    sid = screen.get("id") or "?"
    html_ = screen.get("mockup_html") or ""
    for a in screen.get("actions") or []:
        if not a.get("executado_por"):
            p.append(f"{sid}: ação \"{a.get('label')}\" sem executor")
        if html_ and f'data-acao="{a.get("id")}"' not in html_:
            p.append(f"{sid}: ação \"{a.get('label')}\" não está marcada no desenho (data-acao)")
    for b in screen.get("agentes") or []:
        if html_ and f'data-agente="{b["passo"]}"' not in html_:
            p.append(f"{sid}: bloco do agente ({b['passo']}) não está no desenho (data-agente)")
    for c in screen.get("components") or []:
        alvo = f"{c.get('field') or ''} {c.get('bindTo') or ''}"
        if SENSIVEL_RE.search(alvo) and c.get("type") != "password":
            p.append(f"{sid}: campo sensível em tela: {c.get('field')}")
    ths = [re.sub(r'<[^>]+>', '', h) for h in re.findall(r'<th\b[^>]*>(.*?)</th>', html_, re.S | re.I)]
    if any(SENSIVEL_RE.search(h) for h in ths):
        p.append(f"{sid}: coluna sensível no desenho")
    if re.search(r'Exemplo [ABC]\b', html_):
        p.append(f"{sid}: desenho com dado genérico (\"Exemplo A/B/C\")")
    # botão desenhado sem ligação a passo nenhum: no aplicativo ele não faria nada
    sem_marca = [re.sub(r'<[^>]+>', '', b).strip()[:40] for b in
                 re.findall(r'<button\b(?![^>]*data-acao)[^>]*>(.*?)</button>', _sem_menu(html_), re.S | re.I)]
    if sem_marca:
        p.append(f"{sid}: botão(ões) sem ligação a passo: " + ", ".join(f'"{x}"' for x in sem_marca[:6]))
    for erro in _scripts_com_erro(html_):
        p.append(f"{sid}: script do desenho com erro ({erro}) — o gráfico/mapa não aparece")
    return p


def _sem_menu(doc: str) -> str:
    return re.sub(r'<(aside|nav)\b.*?</\1>', '', doc or '', flags=re.S | re.I)


def _scripts_com_erro(doc: str) -> List[str]:
    """Scripts embutidos no desenho que nem compilam (medido no BioByte: o gráfico de risco tinha
    um parêntese a mais e não aparecia). Usa o node, se houver; sem node, não acusa."""
    import shutil, subprocess, tempfile, os
    node = shutil.which("node")
    if not node:
        return []
    erros = []
    for m in re.finditer(r'<script\b(?![^>]*\bsrc=)([^>]*)>(.*?)</script>', doc or '', re.S | re.I):
        if 'application/json' in m.group(1) or not m.group(2).strip():
            continue
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
            f.write(m.group(2))
        try:
            r = subprocess.run([node, '--check', f.name], capture_output=True, text=True, timeout=20)
            if r.returncode != 0:
                ult = [l for l in (r.stderr or '').splitlines() if 'Error' in l]
                erros.append(ult[0].strip()[:120] if ult else 'erro de sintaxe')
        except Exception:
            pass
        finally:
            os.unlink(f.name)
    return erros


# ── protótipo executável: o script que denuncia ──────────────────────────────

PROTOTIPO_JS = r"""
(function(){
  var F = JSON.parse(document.getElementById('ficha-da-tela').textContent || '{}');
  var A = {}; (F.actions||[]).forEach(function(a){ A[a.id]=a; });
  var COR = {'agente':'#7c3aed','código gerado':'#0369a1','pronto':'#047857','navegação':'#475569'};
  var css = document.createElement('style');
  css.textContent = '.lnx-tag{position:absolute;top:-9px;right:-6px;font:600 9px/1 Inter,sans-serif;padding:3px 5px;border-radius:6px;color:#fff;pointer-events:none;white-space:nowrap;z-index:5}'
   +'.lnx-sem{outline:2px dashed #dc2626!important;outline-offset:2px}'
   +'#lnx-painel{position:fixed;right:16px;bottom:16px;width:360px;max-height:70vh;overflow:auto;background:#fff;border:1px solid #cbd5e1;border-radius:14px;box-shadow:0 10px 30px rgba(15,23,42,.18);font:13px/1.45 Inter,sans-serif;color:#1e293b;z-index:50;display:none}'
   +'#lnx-painel h4{margin:0;padding:12px 14px;border-bottom:1px solid #e2e8f0;font-size:13px;display:flex;justify-content:space-between}'
   +'#lnx-painel .c{padding:12px 14px}#lnx-painel button{font:inherit;font-size:12px;border:1px solid #cbd5e1;border-radius:8px;padding:4px 8px;background:#fff;margin:4px 4px 0 0;cursor:pointer}'
   +'#lnx-barra{position:fixed;top:0;left:0;right:0;background:#0f172a;color:#e2e8f0;font:12px Inter,sans-serif;padding:6px 14px;display:flex;gap:14px;align-items:center;z-index:60}'
   +'#lnx-barra b{color:#fff}#lnx-barra .x{color:#fca5a5}#lnx-barra a{color:#c4b5fd;cursor:pointer}'
   +'body{padding-top:30px!important}[data-mensagem]{display:none}[data-mensagem].lnx-on{display:block}'
   +'.lnx-est{border:2px solid #7c3aed!important;border-radius:12px;position:relative}'
   +'.lnx-est::before{content:attr(data-estado);position:absolute;top:-10px;left:12px;background:#7c3aed;color:#fff;font:600 10px Inter,sans-serif;padding:2px 7px;border-radius:6px}';
  document.head.appendChild(css);
  var painel = document.createElement('div'); painel.id='lnx-painel'; document.body.appendChild(painel);
  function abrir(t, corpo){ painel.innerHTML='<h4><span>'+t+'</span><a style="cursor:pointer" onclick="this.closest(\'#lnx-painel\').style.display=\'none\'">✕</a></h4><div class="c">'+corpo+'</div>'; painel.style.display='block'; }
  function esc(s){ return String(s||'').replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }

  // 1. marca cada ação com quem a executa; botão sem ficha = sem executor
  var sem = 0, total = 0;
  document.querySelectorAll('main button, main a.btn, main [role=button], main [data-acao], [data-acao]').forEach(function(el){
    if (el.closest('#lnx-painel') || el.closest('#lnx-barra') || el.closest('aside') || el.closest('nav')) return;
    total++;
    var a = A[el.getAttribute('data-acao')];
    var ex = a ? a.executado_por : null;
    if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
    var tag = document.createElement('span'); tag.className='lnx-tag';
    if (ex) { tag.textContent = (ex==='agente'?'✦ ':'')+ex; tag.style.background = COR[ex]||'#475569'; }
    else { tag.textContent='sem executor'; tag.style.background='#dc2626'; el.classList.add('lnx-sem'); sem++; }
    el.appendChild(tag);
    el.addEventListener('click', function(ev){
      ev.preventDefault(); ev.stopPropagation();
      if (!a || !ex) { abrir('Sem executor', 'Este botão não está ligado a nenhum passo do caso de uso. No aplicativo ele não faria nada.<br><br>Peça na conversa da etapa para ligá-lo a um passo, ou para retirá-lo.'); return; }
      if (ex === 'navegação') { abrir('Navegação', 'Abre: '+esc(a.navegar_para||'—')); return; }
      var cab = '<div style="color:'+(COR[ex])+';font-weight:600">'+(ex==='agente'?'✦ ':'')+esc(ex)+'</div><div style="color:#64748b;font-size:12px;margin:2px 0 8px">'+esc(a.uc)+' · passo '+esc(a.passo)+'</div><div>'+esc(a.resposta)+'</div>';
      if (ex === 'agente') { simular(a.passo, cab); return; }
      abrir(esc(a.label), cab);
    }, true);
  });

  // 2. agente: os cinco estados, no próprio bloco da tela
  var ESTADOS = ['aguardando entrada','executando','concluído','recusado','erro'];
  function bloco(passo){ return document.querySelector('[data-agente="'+passo+'"]'); }
  function estado(passo, e){
    var b = bloco(passo); if (!b) return;
    b.classList.add('lnx-est'); b.setAttribute('data-estado', '✦ '+e);
  }
  function simular(passo, cab){
    var ag = (F.agentes||[]).find(function(x){return x.passo===passo;}) || {};
    var bts = ESTADOS.map(function(e){ return '<button data-e="'+e+'">'+e+'</button>'; }).join('');
    abrir('✦ '+esc(ag.rotulo||'Agente'), cab+'<div style="margin-top:10px;font-size:12px;color:#475569">Forma: <b>'+esc(ag.forma||'—')+'</b> · veja cada estado na tela:</div>'+bts);
    painel.querySelectorAll('button[data-e]').forEach(function(b){ b.onclick=function(){ estado(passo, b.getAttribute('data-e')); mostrarMsg(b.getAttribute('data-e')); }; });
    estado(passo, 'executando'); setTimeout(function(){ estado(passo,'concluído'); }, 1400);
  }
  function mostrarMsg(e){
    document.querySelectorAll('[data-mensagem]').forEach(function(m){ m.classList.remove('lnx-on'); });
    if (e==='recusado' || e==='erro'){ var m = document.querySelector('[data-mensagem]'); if (m) m.classList.add('lnx-on'); }
  }

  // 3. situações dos fluxos alternativos e de exceção: a mensagem aparece quando o caso acontece
  function situacoes(){
    var ms = F.mensagens||[];
    if (!ms.length) { abrir('Situações', 'O caso de uso não declara mensagens.'); return; }
    abrir('Situações do caso de uso', ms.map(function(m,i){ return '<div style="margin-bottom:10px"><div style="font-size:11px;color:#64748b">'+esc(m.passo)+' · '+esc(m.quando)+'</div><button data-i="'+i+'">mostrar</button> <span>“'+esc(m.texto)+'”</span></div>'; }).join(''));
    painel.querySelectorAll('button[data-i]').forEach(function(b){ b.onclick=function(){
      var m = ms[+b.getAttribute('data-i')];
      document.querySelectorAll('[data-mensagem]').forEach(function(x){ x.classList.toggle('lnx-on', x.getAttribute('data-mensagem')===m.passo); });
      var alvo = document.querySelector('[data-mensagem="'+m.passo+'"]');
      if (!alvo) { var t=document.createElement('div'); t.setAttribute('data-mensagem', m.passo); t.className='lnx-on'; t.style.cssText='margin:12px 32px;padding:10px 14px;border-radius:10px;background:#fef2f2;border:1px solid #fecaca;color:#991b1b'; t.textContent=m.texto; (document.querySelector('main')||document.body).prepend(t); }
    }; });
  }

  // 4. assistente único (Modo B): fixo, conhece as ações de agente do sistema
  function assistente(){
    var G = window.LNX_AGENTES || [];
    abrir('✦ Assistente', '<div style="color:#475569;margin-bottom:8px">O assistente aciona os mesmos agentes das telas, em conversa. Pergunta só o que falta e mostra cada resultado.</div>'
      + (G.length ? G.map(function(g){ return '<div style="padding:6px 0;border-top:1px solid #f1f5f9"><b>'+esc(g.rotulo)+'</b><div style="font-size:11px;color:#64748b">'+esc(g.uc)+' · '+esc(g.tela)+'</div></div>'; }).join('') : '<i>Nenhum agente no sistema.</i>'));
  }

  var barra = document.createElement('div'); barra.id='lnx-barra';
  barra.innerHTML = '<span>Protótipo · <b>'+esc(F.name||'')+'</b> · '+esc((F.uc||[]).join(', '))+'</span><span><b>'+total+'</b> ações'+(sem?' · <span class="x">'+sem+' sem executor</span>':'')+'</span><a id="lnx-sit">Situações ('+(F.mensagens||[]).length+')</a><a id="lnx-ass" style="margin-left:auto">✦ Assistente</a>';
  document.body.appendChild(barra);
  document.getElementById('lnx-sit').onclick = situacoes;
  document.getElementById('lnx-ass').onclick = assistente;
  window.LNX_RESUMO = {acoes: total, sem_executor: sem};

  // 5. ligação com a etapa (quadro embutido): a tela aberta e o componente apontado vão para a
  //    conversa, para o agente saber de que tela e de que elemento se fala.
  var pai = window.parent !== window ? window.parent : null;
  function avisar(tipo, dados){ if (pai) pai.postMessage(Object.assign({origem:'prototipo-langnet', tipo:tipo, tela:F.name||F.id}, dados||{}), '*'); }
  avisar('tela', {});
  var apontando = false;
  window.addEventListener('message', function(ev){ var m = ev.data||{}; if (m.origem==='etapa-langnet' && m.tipo==='apontar'){ apontando = !!m.ligado; document.body.style.cursor = apontando?'crosshair':''; } });
  document.addEventListener('click', function(ev){
    if (!apontando) return;
    ev.preventDefault(); ev.stopPropagation();
    var el = ev.target.closest('[data-campo],[data-acao],[data-agente],[data-mensagem],label,button,th,h2,h3') || ev.target;
    var campo = el.getAttribute('data-campo') || '';
    var rot = (el.getAttribute('data-acao') && A[el.getAttribute('data-acao')]) ? A[el.getAttribute('data-acao')].label : (el.textContent||'').trim().slice(0,80);
    avisar('componente', {rotulo: rot, campo: campo});
    apontando = false; document.body.style.cursor='';
  }, true);
})();
"""


def ficha_publica(screen: Dict) -> Dict:
    return {"id": screen.get("id"), "name": screen.get("name"), "uc": screen.get("uc") or [],
            "actions": screen.get("actions") or [], "agentes": screen.get("agentes") or [],
            "mensagens": screen.get("mensagens") or []}


def injetar_prototipo(doc: str, screen: Dict, agentes_do_sistema: List[Dict]) -> str:
    """Põe a ficha e o script do protótipo executável no desenho da tela."""
    ficha = json.dumps(ficha_publica(screen), ensure_ascii=False).replace("</", "<\\/")
    glob = json.dumps(agentes_do_sistema, ensure_ascii=False).replace("</", "<\\/")
    bloco = (f'<script type="application/json" id="ficha-da-tela">{ficha}</script>'
             f'<script>window.LNX_AGENTES={glob};</script><script>{PROTOTIPO_JS}</script>')
    if re.search(r'</body>', doc, re.I):
        return re.sub(r'</body>', lambda m: bloco + m.group(0), doc, count=1, flags=re.I)
    return doc + bloco


def agentes_do_sistema(screens: List[Dict]) -> List[Dict]:
    out = []
    for s in screens:
        for b in s.get("agentes") or []:
            out.append({"rotulo": b.get("rotulo"), "uc": b.get("uc"), "passo": b.get("passo"),
                        "tela": s.get("name"), "tela_id": s.get("id")})
    return out
