"""Backend do aplicativo gerado — os passos `pronto` (moldes) e a casa dos passos `código gerado`.

Padrão de interação com agentes v1.0: `pronto` e `código gerado` rodam em ROTAS DA API do
backend do aplicativo; só o passo `agente` vai ao servidor de agentes (framework). Antes
(BioByte v5) o backend só servia a estrutura da rede para um console Admin/Petri, e todo
cadastro passava pelo servidor de agentes — com falha calada, sem login e devolvendo senha_hash.

Moldes deste arquivo (determinísticos, iguais em todo aplicativo):
- login com token (POST /api/auth/login, GET /api/auth/eu); toda rota /api exige o token;
- cadastro genérico por tabela do modelo de dados (listar com busca, abrir, criar, alterar,
  apagar), com o erro do banco traduzido em palavras e NUNCA devolvido como sucesso;
- opções de vínculo e de lista fechada (GET /api/opcoes/{tabela}/{coluna}) — campo de vínculo
  vira lista com rótulo legível, nunca caixa de texto de id;
- relatório por agrupamento (GET /api/relatorio/{tabela}?agrupar=coluna);
- trilha de auditoria em toda gravação, quando o modelo tem a tabela;
- dado sensível (senha, hash, sal, token, segredo) nunca sai do servidor;
- as regras `código gerado` de cada caso de uso entram por `regras.py` (escrito pelo modelo).
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

SENSIVEL = r"(senha|password|passwd|hash|_sal$|^sal$|salt|token|segredo|secret|api_?key|chave_api|credencia)"


def _enums(schema_sql: str) -> Dict[str, Dict[str, List[str]]]:
    out: Dict[str, Dict[str, List[str]]] = {}
    for mt in re.finditer(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\((.*?)(?=CREATE\s+TABLE|\Z)", schema_sql or "", re.S | re.I):
        for mc in re.finditer(r"`?(\w+)`?\s+ENUM\s*\(([^)]*)\)", mt.group(2), re.I):
            out.setdefault(mt.group(1), {})[mc.group(1)] = re.findall(r"'([^']*)'", mc.group(2))
    return out


def meta_do_modelo(schema_sql: str) -> Dict:
    from agents.langnetcoherence import schema_columns, schema_fks
    cols = schema_columns(schema_sql or "") or {}
    fks = schema_fks(schema_sql or "") or {}
    login = next((t for t, cs in cols.items()
                  if "email" in cs and any(re.search(r"senha|password", c) for c in cs)), None)
    auditoria = next((t for t, cs in cols.items() if "auditoria" in t and "acao" in cs), None)
    return {"tabelas": cols, "fks": fks, "enums": _enums(schema_sql), "login": login,
            "auditoria": auditoria, "sensivel": SENSIVEL}


def emitir_backend_main(schema_sql: str, project_name: str, com_regras: bool = True,
                        origens: Optional[Dict[str, Dict[str, str]]] = None) -> str:
    """`origens`: {tarefa: {campo: "banco tabela.coluna" | "tela x" | "tarefa y" | "contexto"}},
    lidas do documento de Agentes e Tarefas — o programa busca o que vem do banco."""
    m = meta_do_modelo(schema_sql)
    m["origens"] = origens or {}
    meta = json.dumps(m, ensure_ascii=False, indent=1)
    return _MOLDE.replace("__META__", meta).replace("__PROJETO__", project_name or "Aplicativo") \
                 .replace("__COM_REGRAS__", "True" if com_regras else "False")


_MOLDE = r'''"""__PROJETO__ — API do aplicativo (gerado pelo LangNet).

Passos `pronto` (moldes) e `código gerado` (regras.py) do padrão de interação. O que é decisão de
agente roda no servidor de agentes; esta API nunca o reimplementa.
"""
import os, re, json, uuid, hashlib, secrets, datetime, logging
from typing import Any, Dict, Optional
import jwt
import mysql.connector
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

log = logging.getLogger("api")
META = json.loads(r"""__META__""")
SENSIVEL = re.compile(META["sensivel"], re.I)
SEGREDO = os.getenv("APP_SECRET") or secrets.token_hex(32)
HORAS_TOKEN = int(os.getenv("APP_TOKEN_HORAS", "12"))

app = FastAPI(title="__PROJETO__ — API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def conexao():
    return mysql.connector.connect(host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", "3306")),
                                   user=os.getenv("DB_USER", "root"), password=os.getenv("DB_PASSWORD", ""),
                                   database=os.getenv("DB_NAME", ""), autocommit=False)


def erro_em_palavras(e: Exception) -> str:
    t = str(e)
    log.error("banco recusou: %s", t)  # o detalhe técnico fica no registro; a tela recebe palavras
    col = re.search(r"(?:column|Field|FOREIGN KEY \(`?)\s*'?`?(\w+)", t)
    campo = (col.group(1).replace("_", " ") if col else "um campo")
    if "1452" in t or "foreign key" in t.lower():
        return f"Não foi possível salvar: {campo} aponta para um registro que não existe."
    if "1062" in t or "Duplicate" in t:
        return "Não foi possível salvar: já existe um registro com esse valor."
    if "1048" in t or "1364" in t or "cannot be null" in t or "doesn't have a default" in t:
        return f"Não foi possível salvar: {campo} não foi preenchido."
    if "1406" in t or "too long" in t:
        return f"Não foi possível salvar: o texto de {campo} é maior que o permitido."
    if "1265" in t or "1366" in t or "Data truncated" in t or "Incorrect" in t:
        return f"Não foi possível salvar: o valor informado não é aceito para {campo}."
    if "1451" in t:
        return "Não foi possível apagar: outros registros dependem deste."
    return "Não foi possível concluir a operação no banco de dados."


def limpo(linha: Dict[str, Any]) -> Dict[str, Any]:
    """Nada sensível sai do servidor."""
    out = {}
    for k, v in (linha or {}).items():
        if SENSIVEL.search(k):
            continue
        if isinstance(v, (datetime.date, datetime.datetime)):
            v = v.isoformat()
        elif isinstance(v, (bytes, bytearray)):
            v = None
        elif v.__class__.__name__ == "Decimal":
            v = float(v)
        out[k] = v
    return out


def tabela_valida(t: str) -> list:
    cols = META["tabelas"].get(t)
    if not cols:
        raise HTTPException(404, {"erro": f"Cadastro '{t}' não existe."})
    return cols


# ── login com token ────────────────────────────────────────────────────────────
def _confere_senha(senha: str, guardado: str, sal: str = "") -> bool:
    if not guardado:
        return False
    if guardado.startswith("$2"):
        try:
            import bcrypt
            return bcrypt.checkpw(senha.encode(), guardado.encode())
        except Exception:
            return False
    for cand in (sal + senha, senha + sal, senha):
        if hashlib.sha256(cand.encode()).hexdigest() == guardado:
            return True
    return False


def _guardar_senha(dados: Dict[str, Any], cols: list) -> None:
    """Campo `senha` vindo da tela vira hash no servidor (com sal, se o modelo tem a coluna)."""
    senha = dados.pop("senha", None)
    if not senha:
        return
    col_hash = next((c for c in cols if re.search(r"senha.*hash|password.*hash|^senha$|^password$", c)), None)
    col_sal = next((c for c in cols if re.search(r"(senha_)?sal$|salt", c)), None)
    if not col_hash:
        return
    if col_sal:
        sal = secrets.token_hex(8)
        dados[col_sal] = sal
        dados[col_hash] = hashlib.sha256((sal + senha).encode()).hexdigest()
    else:
        import bcrypt
        dados[col_hash] = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


@app.post("/api/auth/login")
def login(corpo: Dict[str, Any]):
    t = META.get("login")
    if not t:
        raise HTTPException(501, {"erro": "Este sistema não tem cadastro de usuários."})
    cols = META["tabelas"][t]
    email = str(corpo.get("email") or "").strip().lower()
    senha = str(corpo.get("senha") or corpo.get("password") or "")
    if not email or not senha:
        raise HTTPException(400, {"erro": "Informe e-mail e senha."})
    c = conexao(); cur = c.cursor(dictionary=True)
    try:
        cur.execute(f"SELECT * FROM `{t}` WHERE LOWER(email)=%s LIMIT 1", (email,))
        u = cur.fetchone()
    finally:
        cur.close(); c.close()
    col_hash = next((x for x in cols if re.search(r"senha.*hash|password.*hash|^senha$|^password$", x)), None)
    col_sal = next((x for x in cols if re.search(r"(senha_)?sal$|salt", x)), None)
    if not u or not _confere_senha(senha, str(u.get(col_hash) or ""), str(u.get(col_sal) or "")):
        raise HTTPException(401, {"erro": "E-mail ou senha inválidos."})
    if "ativo" in u and not u.get("ativo"):
        raise HTTPException(403, {"erro": "Usuário desativado. Procure o administrador."})
    tok = jwt.encode({"sub": str(u.get("id")), "email": u.get("email"), "papel": u.get("papel"),
                      "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=HORAS_TOKEN)}, SEGREDO, "HS256")
    _auditar(str(u.get("id")), "login", t, str(u.get("id")))
    return {"token": tok, "usuario": limpo(u)}


def usuario(request: Request) -> Dict[str, Any]:
    h = request.headers.get("authorization") or ""
    if not h.lower().startswith("bearer "):
        raise HTTPException(401, {"erro": "Sessão expirada. Entre novamente."})
    try:
        return jwt.decode(h[7:], SEGREDO, algorithms=["HS256"])
    except Exception:
        raise HTTPException(401, {"erro": "Sessão expirada. Entre novamente."})


@app.get("/api/auth/eu")
def eu(u=Depends(usuario)):
    return u


# ── auditoria ──────────────────────────────────────────────────────────────────
def _auditar(usuario_id: str, acao: str, tabela: str, registro: str, antes=None, depois=None):
    t = META.get("auditoria")
    if not t:
        return
    cols = META["tabelas"][t]
    linha = {"id": str(uuid.uuid4()), "acao": acao[:60], "usuario_id": usuario_id}
    for c, v in (("tabela_afetada", tabela), ("registro_afetado", registro), ("entidade", tabela),
                 ("registro_id", registro), ("dados_antes", json.dumps(antes, default=str) if antes else None),
                 ("dados_depois", json.dumps(depois, default=str) if depois else None)):
        if c in cols:
            linha[c] = v
    linha = {k: v for k, v in linha.items() if k in cols}
    try:
        c = conexao(); cur = c.cursor()
        cur.execute(f"INSERT INTO `{t}` ({', '.join('`'+k+'`' for k in linha)}) VALUES ({', '.join(['%s']*len(linha))})",
                    tuple(linha.values()))
        c.commit(); cur.close(); c.close()
    except Exception as e:  # a auditoria não derruba a operação, mas a falha aparece no registro
        log.error("auditoria falhou em %s/%s: %s", tabela, acao, e)


# ── cadastro genérico ──────────────────────────────────────────────────────────
@app.get("/api/dados/{tabela}")
def listar(tabela: str, request: Request, q: str = "", limite: int = 200, u=Depends(usuario)):
    cols = tabela_valida(tabela)
    filtros = {k: v for k, v in request.query_params.items() if k in cols and not SENSIVEL.search(k)}
    onde, vals = [], []
    for k, v in filtros.items():
        onde.append(f"`{k}`=%s"); vals.append(v)
    if q:
        texto = [c for c in cols if not SENSIVEL.search(c) and not c.endswith("id")]
        if texto:
            onde.append("(" + " OR ".join(f"CAST(`{c}` AS CHAR) LIKE %s" for c in texto) + ")")
            vals += [f"%{q}%"] * len(texto)
    ordem = "created_at DESC" if "created_at" in cols else "1"
    c = conexao(); cur = c.cursor(dictionary=True)
    try:
        cur.execute(f"SELECT * FROM `{tabela}`" + (" WHERE " + " AND ".join(onde) if onde else "")
                    + f" ORDER BY {ordem} LIMIT %s", tuple(vals) + (max(1, min(limite, 1000)),))
        linhas = [limpo(r) for r in cur.fetchall()]
        cur.execute(f"SELECT COUNT(*) n FROM `{tabela}`" + (" WHERE " + " AND ".join(onde) if onde else ""), tuple(vals))
        total = cur.fetchone()["n"]
    except mysql.connector.Error as e:
        raise HTTPException(422, {"erro": erro_em_palavras(e)})
    finally:
        cur.close(); c.close()
    return {"rows": linhas, "total": total}


@app.get("/api/dados/{tabela}/{rid}")
def abrir(tabela: str, rid: str, u=Depends(usuario)):
    tabela_valida(tabela)
    c = conexao(); cur = c.cursor(dictionary=True)
    try:
        cur.execute(f"SELECT * FROM `{tabela}` WHERE id=%s", (rid,))
        r = cur.fetchone()
    finally:
        cur.close(); c.close()
    if not r:
        raise HTTPException(404, {"erro": "Registro não encontrado."})
    return limpo(r)


def _gravar(tabela: str, dados: Dict[str, Any], rid: Optional[str], u: Dict[str, Any]):
    cols = tabela_valida(tabela)
    dados = dict(dados or {})
    _guardar_senha(dados, cols)
    dados = {k: (None if v == "" else v) for k, v in dados.items() if k in cols and k not in ("created_at", "updated_at")}
    c = conexao(); cur = c.cursor(dictionary=True)
    try:
        antes = None
        if rid:
            cur.execute(f"SELECT * FROM `{tabela}` WHERE id=%s", (rid,))
            antes = cur.fetchone()
            if not antes:
                raise HTTPException(404, {"erro": "Registro não encontrado."})
            dados.pop("id", None)
            if dados:
                cur.execute(f"UPDATE `{tabela}` SET " + ", ".join(f"`{k}`=%s" for k in dados) + " WHERE id=%s",
                            tuple(dados.values()) + (rid,))
        else:
            if "id" in cols and not dados.get("id"):
                dados["id"] = str(uuid.uuid4())
            cur.execute(f"INSERT INTO `{tabela}` ({', '.join('`'+k+'`' for k in dados)}) VALUES ({', '.join(['%s']*len(dados))})",
                        tuple(dados.values()))
            rid = dados.get("id") or str(cur.lastrowid)
        c.commit()
        cur.execute(f"SELECT * FROM `{tabela}` WHERE id=%s", (rid,))
        depois = cur.fetchone()
    except mysql.connector.Error as e:
        c.rollback()
        raise HTTPException(422, {"erro": erro_em_palavras(e)})
    finally:
        cur.close(); c.close()
    _auditar(u.get("sub"), "alterar" if antes else "criar", tabela, str(rid), limpo(antes) if antes else None, limpo(depois))
    return limpo(depois)


@app.post("/api/dados/{tabela}")
def criar(tabela: str, corpo: Dict[str, Any], u=Depends(usuario)):
    return _gravar(tabela, corpo, None, u)


@app.put("/api/dados/{tabela}/{rid}")
def alterar(tabela: str, rid: str, corpo: Dict[str, Any], u=Depends(usuario)):
    return _gravar(tabela, corpo, rid, u)


@app.delete("/api/dados/{tabela}/{rid}")
def apagar(tabela: str, rid: str, u=Depends(usuario)):
    tabela_valida(tabela)
    c = conexao(); cur = c.cursor()
    try:
        cur.execute(f"DELETE FROM `{tabela}` WHERE id=%s", (rid,))
        n = cur.rowcount
        c.commit()
    except mysql.connector.Error as e:
        c.rollback()
        raise HTTPException(422, {"erro": erro_em_palavras(e)})
    finally:
        cur.close(); c.close()
    if not n:
        raise HTTPException(404, {"erro": "Registro não encontrado."})
    _auditar(u.get("sub"), "apagar", tabela, rid)
    return {"apagado": rid}


# ── opções de vínculo e de lista fechada ───────────────────────────────────────
def _rotulo(cols: list) -> str:
    for c in ("nome", "titulo", "descricao", "email", "codigo", "numero_prontuario"):
        if c in cols:
            return c
    return next((c for c in cols if not c.endswith("id") and not SENSIVEL.search(c)), "id")


@app.get("/api/opcoes/{tabela}/{coluna}")
def opcoes(tabela: str, coluna: str, u=Depends(usuario)):
    tabela_valida(tabela)
    fixas = (META["enums"].get(tabela) or {}).get(coluna)
    if fixas:
        return [{"valor": v, "rotulo": v} for v in fixas]
    alvo = (META["fks"].get(tabela) or {}).get(coluna)
    if not alvo:
        raise HTTPException(404, {"erro": f"{coluna} não é vínculo nem lista fechada."})
    cols = META["tabelas"][alvo]
    rot = _rotulo(cols)
    c = conexao(); cur = c.cursor(dictionary=True)
    try:
        cur.execute(f"SELECT id, `{rot}` AS rotulo FROM `{alvo}` ORDER BY `{rot}` LIMIT 500")
        return [{"valor": r["id"], "rotulo": str(r["rotulo"])} for r in cur.fetchall()]
    finally:
        cur.close(); c.close()


# ── relatório ──────────────────────────────────────────────────────────────────
@app.get("/api/relatorio/{tabela}")
def relatorio(tabela: str, agrupar: str, u=Depends(usuario)):
    cols = tabela_valida(tabela)
    if agrupar not in cols or SENSIVEL.search(agrupar):
        raise HTTPException(400, {"erro": f"Não é possível agrupar por {agrupar}."})
    c = conexao(); cur = c.cursor(dictionary=True)
    try:
        cur.execute(f"SELECT `{agrupar}` AS chave, COUNT(*) AS total FROM `{tabela}` GROUP BY `{agrupar}` ORDER BY total DESC")
        return [{"chave": (r["chave"].isoformat() if hasattr(r["chave"], "isoformat") else r["chave"]), "total": r["total"]}
                for r in cur.fetchall()]
    finally:
        cur.close(); c.close()


# ── entradas do agente que vêm do banco: o PROGRAMA busca, o agente julga ──────
def _tabela_do_contexto() -> Dict[str, str]:
    """caso_id → casos_clinicos, a partir das chaves estrangeiras do modelo."""
    m = {}
    for _t, fk in META["fks"].items():
        for col, ref in fk.items():
            m.setdefault(col, ref)
    return m


@app.post("/api/agente/entradas/{tarefa}")
def entradas_do_agente(tarefa: str, corpo: Dict[str, Any], u=Depends(usuario)):
    origens = (META.get("origens") or {}).get(tarefa) or {}
    ctx = {k: v for k, v in (corpo or {}).items() if v not in (None, "")}
    ref = _tabela_do_contexto()
    out: Dict[str, Any] = {}
    faltam = []
    c = conexao(); cur = c.cursor(dictionary=True)
    try:
        for campo, origem in origens.items():
            if campo in ctx:
                continue
            o = str(origem or "").split(None, 1)
            if not o or o[0].lower() != "banco" or len(o) < 2:
                continue
            mt = re.match(r"(\w+)(?:\.(\w+))?", o[1].strip())
            if not mt or mt.group(1) not in META["tabelas"]:
                faltam.append(campo); continue
            tab, col = mt.group(1), mt.group(2)
            cols = META["tabelas"][tab]
            onde, vals = [], []
            for k, v in ctx.items():
                if k in cols:
                    onde.append(f"`{k}`=%s"); vals.append(v)
                elif ref.get(k) == tab and "id" in cols:
                    onde.append("`id`=%s"); vals.append(v)
            sql = f"SELECT * FROM `{tab}`" + (" WHERE " + " AND ".join(onde) if onde else "") + " LIMIT 200"
            cur.execute(sql, tuple(vals))
            linhas = [limpo(r) for r in cur.fetchall()]
            if col:
                if col not in cols:
                    faltam.append(campo); continue
                if not linhas:
                    faltam.append(campo); continue
                out[campo] = linhas[0].get(col)
            else:
                out[campo] = linhas
    finally:
        cur.close(); c.close()
    if faltam:
        out["_entradas_sem_valor"] = faltam  # o agente recebe a lista e recusa em vez de inventar
    return out


@app.exception_handler(HTTPException)
async def _erro(request, exc):
    d = exc.detail if isinstance(exc.detail, dict) else {"erro": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content=d)


@app.get("/api/saude")
def saude():
    return {"ok": True, "servico": "__PROJETO__"}


# ── regras `código gerado` de cada caso de uso ────────────────────────────────
if __COM_REGRAS__ and os.path.exists(os.path.join(os.path.dirname(__file__), "regras.py")):
    import regras  # noqa: E402
    regras.instalar(app, conexao=conexao, usuario=usuario, limpo=limpo, erro_em_palavras=erro_em_palavras,
                    auditar=_auditar, meta=META)


if __name__ == "__main__":
    import uvicorn
    # o motor de implantação do LangNet passa a porta em PORT
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT") or os.getenv("API_PORT") or "8000"))
'''
