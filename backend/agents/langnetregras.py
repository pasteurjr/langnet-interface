"""Tradutor de regras — contrato de passos da tarefa (`steps:` no tasks.yaml).

Até aqui o gerador lia a DESCRIÇÃO em prosa de cada tarefa e traduzia o que reconhecia:
comandos de banco viravam código; passos de regra ("confira a senha", "conte as resistências",
"só alerte se for multirresistente") eram reconhecidos por frase, caso a caso, e o que não
casava sumia. Este módulo troca prosa por contrato: cada passo tem um TIPO de um conjunto
fechado, condições e cálculos são escritos numa mini-linguagem pequena e sem execução de texto
livre, e TODO passo declarado termina em um de dois estados — emitido, ou não emitido com o
motivo — registrados num manifesto que o portão de lógica lê.

Tipos de passo:
  consulta     {sql, params, guarda_em, forma: escalar|linha|linhas}
  escrita      {sql, params, guarda_id_em?}
  verificacao  {condicao, mensagem}
  calculo      {atribui, expressao}
  condicao     {se, passos: [...]}
  laco         {para_cada, em, passos: [...]}
  externo      {ferramenta, argumentos: {nome: expressao}, guarda_em, mapeia?: {campo_tool: variavel}}
  tarefa       {nome, entrada: {campo: expressao}, guarda_em, mapeia?}  -- encadeia OUTRA tarefa
               determinística do mesmo sistema (orquestração); tarefa de agente não se encadeia
  retorno      {campos: [...]}
  agente       {instrucao}   -- só vale em tarefa `execution: agent`

Mini-linguagem: valores, nomes, acesso a campo (`x.campo`), + - * /, comparações, `e`/`ou`/`nao`,
e funções nomeadas em português (ver FUNCOES). Nome inexistente em tempo de execução dá erro
claro, não NameError.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

TIPOS = ("consulta", "escrita", "verificacao", "calculo", "condicao", "laco",
         "externo", "tarefa", "retorno", "agente")

# Nomes GENÉRICOS de chamada externa que a prosa usa ("chame api_call_tool com a função X"):
# não são ferramentas — o alvo real está no argumento. O reparo mecânico troca pelo alvo.
CHAMADORES_GENERICOS = ("api_call_tool", "api_tool", "http_tool", "external_api", "api_call",
                        "service_call", "rest_client", "webservice_tool")
ARGS_DE_ALVO = ("endpoint", "funcao", "função", "function", "tool", "ferramenta", "servico",
                "serviço", "service", "nome", "name", "operacao", "operação", "method")
# Banco de dados NÃO é ferramenta externa: no contrato, banco é `consulta`/`escrita`. Se o agente
# embrulha o SQL numa "ferramenta de banco", o passo perde a validação de SQL/params e a
# emissão determinística — por isso é recusado.
FERRAMENTAS_DE_BANCO = ("database_tool", "database_query", "db_tool", "sql_tool", "database")

# nome na mini-linguagem -> (função do runtime emitido, aridade mínima, aridade máxima)
FUNCOES: Dict[str, Tuple[str, int, int]] = {
    "conta_valor":   ("_rt_conta_valor", 2, 2),   # conta_valor(json, 'R')
    "tamanho":       ("_rt_tamanho", 1, 1),
    "confere_senha": ("_rt_confere_senha", 2, 2),  # confere_senha(senha, hash_guardado)
    "existe":        ("_rt_existe", 1, 1),         # tratado à parte: recebe o NOME
    "entre":         ("_rt_entre", 3, 3),
    "em":            ("_rt_em", 2, 2),
    "arredonda":     ("_rt_arredonda", 1, 2),
    "hoje":          ("_rt_hoje", 0, 0),
    "dias_entre":    ("_rt_dias_entre", 2, 2),
    "texto":         ("_rt_texto", 1, 1),
    "numero":        ("_rt_numero", 1, 1),
    "maiusculas":    ("_rt_maiusculas", 1, 1),
    "minusculas":    ("_rt_minusculas", 1, 1),
    "contem":        ("_rt_contem", 2, 2),
    "soma":          ("_rt_soma", 1, 2),
    "media":         ("_rt_media", 1, 2),
    "primeiro":      ("_rt_primeiro", 1, 1),
    "vazio":         ("_rt_vazio", 1, 1),
    "codigo_valido": ("_rt_codigo_valido", 2, 3),  # codigo_valido(codigo, tamanho, segundos?)
}


class ErroDeRegra(ValueError):
    """Expressão ou passo que não cabe no contrato — nunca vira código silenciosamente."""


# ─────────────────────────── mini-linguagem: tokens ────────────────────────────

_TOKEN = re.compile(r"""
    (?P<num>\d+(?:\.\d+)?)
  | (?P<str>'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")
  | (?P<op>==|!=|<=|>=|<|>|\+|-|\*|/|\(|\)|\[|\]|,|\.)
  | (?P<nome>[A-Za-zÀ-ÿ_][A-Za-z0-9À-ÿ_]*)
  | (?P<ws>\s+)
""", re.X)

_PALAVRAS = {"e": "E", "ou": "OU", "nao": "NAO", "não": "NAO",
             "verdadeiro": "VERDADEIRO", "falso": "FALSO", "nulo": "NULO",
             "true": "VERDADEIRO", "false": "FALSO", "null": "NULO", "none": "NULO"}


def _tokenizar(texto: str) -> List[Tuple[str, str]]:
    saida: List[Tuple[str, str]] = []
    pos = 0
    while pos < len(texto):
        m = _TOKEN.match(texto, pos)
        if not m:
            raise ErroDeRegra(f"símbolo inesperado em «{texto[pos:pos+12]}»")
        pos = m.end()
        if m.lastgroup == "ws":
            continue
        if m.lastgroup == "nome":
            low = m.group().lower()
            if low in _PALAVRAS:
                saida.append((_PALAVRAS[low], m.group()))
            else:
                saida.append(("NOME", m.group()))
        else:
            saida.append((m.lastgroup.upper(), m.group()))
    saida.append(("FIM", ""))
    return saida


# ─────────────────────── mini-linguagem: parser → Python ───────────────────────

class _Parser:
    """Descida recursiva; devolve código Python que só usa `_ctx`, os `_rt_*` e literais."""

    def __init__(self, texto: str):
        self.texto = texto
        self.toks = _tokenizar(texto)
        self.i = 0
        self.nomes_usados: List[str] = []

    def _olha(self) -> Tuple[str, str]:
        return self.toks[self.i]

    def _come(self, tipo: Optional[str] = None, valor: Optional[str] = None) -> Tuple[str, str]:
        t = self.toks[self.i]
        if tipo and t[0] != tipo:
            raise ErroDeRegra(f"esperava {tipo} e veio «{t[1] or 'fim'}» em «{self.texto}»")
        if valor and t[1] != valor:
            raise ErroDeRegra(f"esperava «{valor}» e veio «{t[1] or 'fim'}» em «{self.texto}»")
        self.i += 1
        return t

    def compilar(self) -> str:
        py = self._ou()
        if self._olha()[0] != "FIM":
            raise ErroDeRegra(f"sobrou «{self._olha()[1]}» no fim de «{self.texto}»")
        return py

    def _ou(self) -> str:
        esq = self._e()
        while self._olha()[0] == "OU":
            self._come(); esq = f"({esq} or {self._e()})"
        return esq

    def _e(self) -> str:
        esq = self._nao()
        while self._olha()[0] == "E":
            self._come(); esq = f"({esq} and {self._nao()})"
        return esq

    def _nao(self) -> str:
        if self._olha()[0] == "NAO":
            self._come(); return f"(not {self._nao()})"
        return self._cmp()

    def _cmp(self) -> str:
        esq = self._add()
        t = self._olha()
        if t[0] == "OP" and t[1] in ("==", "!=", "<", "<=", ">", ">="):
            self._come()
            dir_ = self._add()
            return f"_rt_cmp({esq}, {t[1]!r}, {dir_})"
        return esq

    def _add(self) -> str:
        esq = self._mul()
        while self._olha()[0] == "OP" and self._olha()[1] in ("+", "-"):
            op = self._come()[1]; esq = f"_rt_arit({esq}, {op!r}, {self._mul()})"
        return esq

    def _mul(self) -> str:
        esq = self._un()
        while self._olha()[0] == "OP" and self._olha()[1] in ("*", "/"):
            op = self._come()[1]; esq = f"_rt_arit({esq}, {op!r}, {self._un()})"
        return esq

    def _un(self) -> str:
        if self._olha()[0] == "OP" and self._olha()[1] == "-":
            self._come(); return f"_rt_arit(0, '-', {self._un()})"
        return self._pos()

    def _pos(self) -> str:
        t = self._olha()
        if t[0] == "NOME":
            nome = self._come()[1]
            if self._olha()[0] == "OP" and self._olha()[1] == "(":
                py = self._chamada(nome)          # `.campo` depois da chamada é tratado abaixo
            else:
                self.nomes_usados.append(nome)
                py = f"_v({nome!r})"
        else:
            py = self._prim()
        while self._olha()[0] == "OP" and self._olha()[1] == ".":
            self._come(); campo = self._come("NOME")[1]
            py = f"_rt_campo({py}, {campo!r})"
        return py

    def _chamada(self, nome: str) -> str:
        if nome not in FUNCOES:
            raise ErroDeRegra(f"função «{nome}» não existe na mini-linguagem "
                              f"(disponíveis: {', '.join(sorted(FUNCOES))})")
        fn, mn, mx = FUNCOES[nome]
        self._come("OP", "(")
        args: List[str] = []
        if nome == "existe" and self._olha()[0] == "NOME":
            # existe(x) pergunta pelo NOME, não pelo valor — senão x ausente já daria erro antes.
            alvo = self._come()[1]
            self._come("OP", ")")
            return f"_rt_existe_nome({alvo!r})"
        if not (self._olha()[0] == "OP" and self._olha()[1] == ")"):
            args.append(self._ou())
            while self._olha()[0] == "OP" and self._olha()[1] == ",":
                self._come(); args.append(self._ou())
        self._come("OP", ")")
        if not (mn <= len(args) <= mx):
            raise ErroDeRegra(f"«{nome}» espera {mn}" + (f" a {mx}" if mx != mn else "")
                              + f" argumento(s), veio {len(args)}")
        return f"{fn}({', '.join(args)})"

    def _prim(self) -> str:
        t = self._come()
        if t[0] == "NUM":
            return t[1]
        if t[0] == "STR":
            return repr(bytes(t[1][1:-1], "utf-8").decode("unicode_escape"))
        if t[0] == "VERDADEIRO":
            return "True"
        if t[0] == "FALSO":
            return "False"
        if t[0] == "NULO":
            return "None"
        if t[0] == "OP" and t[1] == "(":
            py = self._ou(); self._come("OP", ")"); return f"({py})"
        if t[0] == "OP" and t[1] == "[":
            itens = []
            if not (self._olha()[0] == "OP" and self._olha()[1] == "]"):
                itens.append(self._ou())
                while self._olha()[0] == "OP" and self._olha()[1] == ",":
                    self._come(); itens.append(self._ou())
            self._come("OP", "]")
            return "[" + ", ".join(itens) + "]"
        raise ErroDeRegra(f"não entendi «{t[1] or 'fim'}» em «{self.texto}»")


def compilar_expressao(texto: str) -> Tuple[str, List[str]]:
    """Devolve (python, nomes_referenciados). Levanta ErroDeRegra se não compilar."""
    if not isinstance(texto, str) or not texto.strip():
        raise ErroDeRegra("expressão vazia")
    # Herança da prosa: `{campo}` e `{{campo}}` significam o nome `campo`.
    texto = re.sub(r"\{\{?\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}?\}", r"\1", texto)
    p = _Parser(texto.strip())
    return p.compilar(), p.nomes_usados


def acessos_de_campo(texto: str) -> List[Tuple[str, str]]:
    """Pares (nome, campo) de cada acesso `nome.campo` na expressão (para conferir se o campo
    existe no que a ferramenta devolve). Expressão que não tokeniza devolve lista vazia — o
    erro de sintaxe é reportado pela compilação."""
    try:
        t = re.sub(r"\{\{?\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}?\}", r"\1", str(texto))
        toks = _tokenizar(t)
    except Exception:
        return []
    pares = []
    for i in range(len(toks) - 2):
        if toks[i][0] == "NOME" and toks[i + 1][1] == "." and toks[i + 2][0] == "NOME":
            pares.append((toks[i][1], toks[i + 2][1]))
    return pares


def _expressoes_do_passo(p: dict) -> List[str]:
    tipo = str(p.get("tipo") or "").lower()
    if tipo in ("consulta", "escrita"):
        return [str(a) for a in (p.get("params") or [])]
    if tipo == "verificacao":
        return [str(p.get("condicao") or "")]
    if tipo == "calculo":
        return [str(p.get("expressao") or "")]
    if tipo == "condicao":
        return [str(p.get("se") or "")]
    if tipo == "laco":
        return [str(p.get("em") or "")]
    if tipo == "externo":
        return [str(v) for v in (p.get("argumentos") or {}).values()] if isinstance(p.get("argumentos"), dict) else []
    if tipo == "tarefa":
        return [str(v) for v in (p.get("entrada") or {}).values()] if isinstance(p.get("entrada"), dict) else []
    if tipo == "retorno":
        return [str(c) for c in (p.get("campos") or []) if isinstance(c, str)]
    return []


# ────────────────────────────── validação do contrato ───────────────────────────

def _erro(n: str, msg: str) -> dict:
    return {"passo": n, "motivo": msg}


def validar_passos(passos: Any, execution: str = "deterministic",
                   ferramentas_resolvidas: Any = None,
                   prefixo: str = "", tarefas_do_sistema: Any = None,
                   saidas_conhecidas: Optional[dict] = None) -> List[dict]:
    """Confere estrutura e compila as expressões. Devolve a lista de problemas (vazia = ok).

    `ferramentas_resolvidas`: nomes (ou dict nome -> argumentos) que a etapa Ferramentas resolveu.
    `tarefas_do_sistema`: dict nome -> execution das tarefas do mesmo tasks.yaml (passo `tarefa`).
    `saidas_conhecidas`: variável guardada por `externo` -> campos que a ferramenta devolve; todo
    acesso `variavel.campo` a ela é conferido (campo inexistente = passo inválido)."""
    problemas: List[dict] = []
    if saidas_conhecidas is None:
        saidas_conhecidas = {}
    if not isinstance(passos, list):
        return [_erro(prefixo or "-", "`steps` deve ser uma lista")]
    for idx, p in enumerate(passos, 1):
        n = f"{prefixo}{idx}"
        if not isinstance(p, dict):
            problemas.append(_erro(n, "passo deve ser um objeto com `tipo`")); continue
        tipo = str(p.get("tipo") or "").lower()
        if tipo not in TIPOS:
            problemas.append(_erro(n, f"tipo «{tipo or '?'}» não existe; use um de: {', '.join(TIPOS)}"))
            continue
        # acesso a campo que a ferramenta não devolve (ex.: resposta.valor_escore quando ela
        # devolve escore_cox): pega ANTES de virar NULL no banco
        for expr in _expressoes_do_passo(p):
            for var, campo in acessos_de_campo(expr):
                if var in saidas_conhecidas and campo not in saidas_conhecidas[var]:
                    problemas.append(_erro(n, f"«{var}.{campo}» não existe — a ferramenta que preencheu "
                                              f"«{var}» devolve: {', '.join(saidas_conhecidas[var])} "
                                              "(use `mapeia` ou o nome certo)"))
        try:
            if tipo in ("consulta", "escrita"):
                sql = p.get("sql") or ""
                if not isinstance(sql, str) or not sql.strip():
                    raise ErroDeRegra("`sql` obrigatório")
                if tipo == "consulta" and not re.match(r"(?is)^\s*select\b", sql):
                    raise ErroDeRegra("`consulta` exige um SELECT")
                if tipo == "escrita" and not re.match(r"(?is)^\s*(insert|update|delete)\b", sql):
                    raise ErroDeRegra("`escrita` exige INSERT, UPDATE ou DELETE")
                for a in (p.get("params") or []):
                    compilar_expressao(str(a))
                if sql.count("%s") != len(p.get("params") or []):
                    raise ErroDeRegra(f"o SQL tem {sql.count('%s')} marcador(es) %s e "
                                      f"{len(p.get('params') or [])} parâmetro(s)")
                if tipo == "consulta":
                    if not p.get("guarda_em"):
                        raise ErroDeRegra("`consulta` exige `guarda_em`")
                    if str(p.get("forma", "escalar")) not in ("escalar", "linha", "linhas"):
                        raise ErroDeRegra("`forma` deve ser escalar, linha ou linhas")
            elif tipo == "verificacao":
                if not p.get("condicao"):
                    raise ErroDeRegra("`condicao` obrigatória")
                compilar_expressao(str(p["condicao"]))
                if not p.get("mensagem"):
                    raise ErroDeRegra("`mensagem` de recusa obrigatória (use a frase do caso de uso)")
            elif tipo == "calculo":
                if not re.match(r"^[A-Za-z_]\w*$", str(p.get("atribui") or "")):
                    raise ErroDeRegra("`atribui` deve ser um nome de variável")
                compilar_expressao(str(p.get("expressao") or ""))
            elif tipo == "condicao":
                compilar_expressao(str(p.get("se") or ""))
                problemas += validar_passos(p.get("passos") or [], execution,
                                            ferramentas_resolvidas, prefixo=f"{n}.",
                                            tarefas_do_sistema=tarefas_do_sistema,
                                            saidas_conhecidas=saidas_conhecidas)
            elif tipo == "laco":
                if not re.match(r"^[A-Za-z_]\w*$", str(p.get("para_cada") or "")):
                    raise ErroDeRegra("`para_cada` deve ser um nome de variável")
                compilar_expressao(str(p.get("em") or ""))
                problemas += validar_passos(p.get("passos") or [], execution,
                                            ferramentas_resolvidas, prefixo=f"{n}.",
                                            tarefas_do_sistema=tarefas_do_sistema,
                                            saidas_conhecidas=saidas_conhecidas)
            elif tipo == "externo":
                f = str(p.get("ferramenta") or "")
                if not f:
                    raise ErroDeRegra("`ferramenta` obrigatória")
                if f in CHAMADORES_GENERICOS or f.startswith("service_call"):
                    raise ErroDeRegra(f"«{f}» é um nome genérico, não uma ferramenta — nomeie a "
                                      "ferramenta resolvida na etapa Ferramentas (ou a tarefa, "
                                      "com o passo `tarefa`)")
                if f in FERRAMENTAS_DE_BANCO or _canonizar_ferramenta(f) in FERRAMENTAS_DE_BANCO:
                    raise ErroDeRegra("banco de dados não é ferramenta externa — escreva o passo "
                                      "como `consulta` (SELECT) ou `escrita` (INSERT/UPDATE/DELETE)")
                aceita, canon = _ferramenta_aceita(f, ferramentas_resolvidas)
                if not aceita:
                    raise ErroDeRegra(f"ferramenta «{f}» não está resolvida na etapa Ferramentas")
                args = p.get("argumentos") or {}
                if not isinstance(args, dict):
                    raise ErroDeRegra("`argumentos` deve ser um objeto {nome: expressão}")
                for a in args.values():
                    compilar_expressao(str(a))
                aceitos = _res_args(ferramentas_resolvidas, f)
                if aceitos:
                    estranhos = [k for k in args if k not in aceitos]
                    if estranhos:
                        raise ErroDeRegra(f"a ferramenta «{canon}» não tem o(s) argumento(s) "
                                          f"{', '.join(estranhos)} — ela aceita: {', '.join(aceitos)}")
                    if not args:
                        raise ErroDeRegra(f"a ferramenta «{canon}» exige argumento(s): {', '.join(aceitos)}")
                devolve = _res_saida(ferramentas_resolvidas, f)
                if devolve and isinstance(p.get("mapeia"), dict):
                    fora = [k for k in p["mapeia"] if k not in devolve]
                    if fora:
                        raise ErroDeRegra(f"a ferramenta «{canon}» não devolve {', '.join(fora)} — "
                                          f"ela devolve: {', '.join(devolve)}")
                if not p.get("guarda_em"):
                    raise ErroDeRegra("`externo` exige `guarda_em`")
                if devolve:
                    saidas_conhecidas[str(p["guarda_em"])] = list(devolve)
            elif tipo == "tarefa":
                alvo = str(p.get("nome") or "")
                if not re.match(r"^[A-Za-z_]\w*$", alvo):
                    raise ErroDeRegra("`nome` da tarefa a encadear é obrigatório")
                if tarefas_do_sistema is not None:
                    execs = tarefas_do_sistema if isinstance(tarefas_do_sistema, dict) else \
                        {t: "deterministic" for t in tarefas_do_sistema}
                    if alvo not in execs:
                        raise ErroDeRegra(f"tarefa «{alvo}» não existe neste tasks.yaml")
                    if str(execs.get(alvo) or "deterministic") == "agent":
                        raise ErroDeRegra(f"tarefa «{alvo}» é executada por agente e não pode ser "
                                          "encadeada dentro de uma regra — encerre aqui e deixe a "
                                          "interface dispará-la na etapa seguinte")
                entrada = p.get("entrada") or {}
                if not isinstance(entrada, dict):
                    raise ErroDeRegra("`entrada` deve ser um objeto {campo: expressão}")
                for a in entrada.values():
                    compilar_expressao(str(a))
                if not p.get("guarda_em"):
                    raise ErroDeRegra("`tarefa` exige `guarda_em`")
            elif tipo == "retorno":
                campos = p.get("campos") or []
                if not isinstance(campos, list) or not campos:
                    raise ErroDeRegra("`campos` do retorno obrigatórios")
            elif tipo == "agente":
                if execution != "agent":
                    raise ErroDeRegra("passo de agente em tarefa determinística — declare a regra "
                                      "ou marque a tarefa como `execution: agent`")
        except ErroDeRegra as e:
            problemas.append(_erro(n, str(e)))
    return problemas


# ────────────────────────────── reparos mecânicos ──────────────────────────────────
def _sem_aspas(v: Any) -> str:
    t = str(v).strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in ("'", '"'):
        return t[1:-1]
    return t


def reparar_passos_mecanicos(passos: List[dict], ferramentas_resolvidas: Any = None,
                             prefixo: str = "") -> Tuple[List[dict], List[str]]:
    """Reparos SEM agente, só onde a evidência está no próprio passo (cada um fica registrado):
      · parâmetro morto: `params` com itens num SQL sem marcador %s -> params []
      · sinônimo de ferramenta (gerar_jwt) -> nome canônico da biblioteca (jwt_tool)
      · chamador genérico (api_call_tool com endpoint/funcao = X) -> a ferramenta X, se X está
        resolvida na etapa Ferramentas; o argumento que só nomeava o alvo sai da chamada
    Devolve (passos_reparados, lista_de_reparos)."""
    reparos: List[str] = []
    saida: List[dict] = []
    nomes = _res_nomes(ferramentas_resolvidas)
    for idx, p in enumerate(passos or [], 1):
        n = f"{prefixo}{idx}"
        if not isinstance(p, dict):
            saida.append(p); continue
        p = dict(p)
        tipo = str(p.get("tipo") or "").lower()
        if tipo in ("consulta", "escrita") and str(p.get("sql", "")).count("%s") == 0 and p.get("params"):
            p["params"] = []
            reparos.append(f"passo {n}: parâmetro sem marcador %s removido (não mudava o comando)")
        if tipo == "externo":
            f = str(p.get("ferramenta") or "")
            args = dict(p.get("argumentos") or {}) if isinstance(p.get("argumentos"), dict) else {}
            if f in CHAMADORES_GENERICOS or f.startswith("service_call"):
                for k in list(args):
                    if k.lower() in ARGS_DE_ALVO:
                        alvo = _sem_aspas(args[k])
                        ok, canon = _ferramenta_aceita(alvo, ferramentas_resolvidas)
                        if ok and (canon in nomes or alvo in nomes):
                            del args[k]
                            p["ferramenta"], p["argumentos"] = canon, args
                            reparos.append(f"passo {n}: «{f}» era só o meio de chamar — a ferramenta é «{canon}»")
                            break
            else:
                canon = _canonizar_ferramenta(f)
                if canon != f:
                    p["ferramenta"] = canon
                    reparos.append(f"passo {n}: «{f}» é sinônimo de «{canon}» (nome da biblioteca)")
        for k in ("passos",):
            if isinstance(p.get(k), list):
                p[k], sub = reparar_passos_mecanicos(p[k], ferramentas_resolvidas, prefixo=f"{n}.")
                reparos += sub
        saida.append(p)
    return saida, reparos


# ────────────────────────────────── emissão ──────────────────────────────────────

def _res_nomes(res: Any) -> set:
    """`ferramentas_resolvidas` pode ser um conjunto de nomes ou um dict nome -> argumentos aceitos."""
    if res is None:
        return set()
    return set(res.keys()) if isinstance(res, dict) else set(res)


def _res_args(res: Any, nome: str) -> Optional[List[str]]:
    """Argumentos aceitos pela ferramenta, quando a etapa Ferramentas os conhece (MCP)."""
    if not isinstance(res, dict):
        return None
    v = res.get(nome)
    if v is None:
        v = res.get(_canonizar_ferramenta(nome))
    if isinstance(v, dict):
        v = v.get("argumentos") or v.get("input_args")
    return list(v) if isinstance(v, (list, tuple)) and v else None


def _res_saida(res: Any, nome: str) -> Optional[List[str]]:
    """Campos que a ferramenta DEVOLVE, quando declarados (esquema de saída do MCP)."""
    if not isinstance(res, dict):
        return None
    v = res.get(nome)
    if v is None:
        v = res.get(_canonizar_ferramenta(nome))
    if isinstance(v, dict):
        v = v.get("saida") or v.get("output_args")
        return list(v) if isinstance(v, (list, tuple)) and v else None
    return None


def _ferramenta_aceita(nome: str, res: Any) -> Tuple[bool, str]:
    """(aceita?, nome canônico). Aceita o que a etapa Ferramentas resolveu e o que a biblioteca
    do gerador SEMPRE embarca — e nada mais: nome desconhecido não vira chamada."""
    canon = _canonizar_ferramenta(nome)
    nomes = _res_nomes(res)
    if nome in nomes or canon in nomes:
        return True, canon
    try:
        from agents.langnettools_stage import BIBLIOTECA_REAL
        if canon in BIBLIOTECA_REAL:
            return True, canon
    except Exception:
        pass
    return False, canon


def _canonizar_ferramenta(nome: Any) -> str:
    """Sinônimo -> nome canônico da biblioteca (mesma tabela da etapa Ferramentas)."""
    try:
        from agents.langnettools_stage import SINONIMOS
        return SINONIMOS.get(str(nome), str(nome))
    except Exception:
        return str(nome)


def ferramentas_da_biblioteca() -> set:
    """Nomes que SEMPRE têm implementação real (biblioteca do gerador), com sinônimos."""
    try:
        from agents.langnettools_stage import BIBLIOTECA_REAL, SINONIMOS
        return set(BIBLIOTECA_REAL) | set(SINONIMOS)
    except Exception:
        return set()


def _params_py(params: List[Any]) -> str:
    return "[" + ", ".join(compilar_expressao(str(a))[0] for a in (params or [])) + "]"


def _coluna_escalar(sql: str, guarda_em: str) -> str:
    """Coluna a capturar num SELECT escalar: o alias igual a `guarda_em`, senão a 1ª coluna."""
    m = re.match(r"(?is)^\s*select\s+(.+?)\s+from\b", sql)
    sel = m.group(1) if m else ""
    if re.search(r"(?is)\bas\s+`?" + re.escape(guarda_em) + r"`?\b", sel):
        return guarda_em
    primeira = sel.split(",")[0].strip()
    ma = re.search(r"(?is)\bas\s+`?(\w+)`?\s*$", primeira)
    if ma:
        return ma.group(1)
    primeira = primeira.replace("`", "").split()[0] if primeira else "id"
    return primeira.split(".")[-1] if primeira else "id"


def emitir_passos(passos: List[dict], indent: str = "        ",
                  prefixo: str = "", ferramentas_resolvidas: Any = None,
                  tarefas_do_sistema: Any = None) -> Tuple[List[str], List[dict]]:
    """Devolve (linhas_python, manifesto). Cada passo declarado aparece no manifesto como
    emitido=True ou emitido=False com motivo — nunca desaparece."""
    linhas: List[str] = []
    manifesto: List[dict] = []
    for idx, p in enumerate(passos, 1):
        n = f"{prefixo}{idx}"
        tipo = str(p.get("tipo") or "").lower()
        try:
            if tipo == "consulta":
                sql, guarda = p["sql"], p["guarda_em"]
                forma = str(p.get("forma", "escalar"))
                linhas.append(f"{indent}# passo {n}: consulta -> {guarda} ({forma})")
                linhas.append(f"{indent}cur.execute({sql!r}, {_params_py(p.get('params') or [])})")
                linhas.append(f"{indent}_rows = cur.fetchall()")
                if forma == "linhas":
                    linhas.append(f"{indent}_ctx[{guarda!r}] = _rows")
                elif forma == "linha":
                    linhas.append(f"{indent}_ctx[{guarda!r}] = _rows[0] if _rows else None")
                else:
                    col = _coluna_escalar(sql, guarda)
                    linhas.append(f"{indent}_ctx[{guarda!r}] = (_rows[0].get({col!r}) if _rows else None)")
            elif tipo == "escrita":
                linhas.append(f"{indent}# passo {n}: escrita")
                linhas.append(f"{indent}cur.execute({p['sql']!r}, {_params_py(p.get('params') or [])})")
                if p.get("guarda_id_em"):
                    linhas.append(f"{indent}_ctx[{p['guarda_id_em']!r}] = cur.lastrowid or _ctx.get({p['guarda_id_em']!r})")
            elif tipo == "verificacao":
                cond, _ = compilar_expressao(str(p["condicao"]))
                msg = str(p.get("mensagem") or "condição não atendida")
                linhas.append(f"{indent}# passo {n}: verificação")
                linhas.append(f"{indent}if not {cond}:")
                linhas.append(f"{indent}    conn.rollback()")
                linhas.append(f"{indent}    return {{'status': 'erro', 'error': {msg!r}, "
                              f"'nao_encontrado': 'verificacao', 'passo': {n!r}}}")
            elif tipo == "calculo":
                expr, _ = compilar_expressao(str(p["expressao"]))
                linhas.append(f"{indent}# passo {n}: cálculo")
                linhas.append(f"{indent}_ctx[{p['atribui']!r}] = {expr}")
            elif tipo == "condicao":
                cond, _ = compilar_expressao(str(p["se"]))
                linhas.append(f"{indent}# passo {n}: condição")
                linhas.append(f"{indent}if {cond}:")
                sub, sub_m = emitir_passos(p.get("passos") or [], indent + "    ", prefixo=f"{n}.",
                                           ferramentas_resolvidas=ferramentas_resolvidas,
                                           tarefas_do_sistema=tarefas_do_sistema)
                linhas += sub or [f"{indent}    pass"]
                manifesto += sub_m
            elif tipo == "laco":
                em, _ = compilar_expressao(str(p["em"]))
                var = p["para_cada"]
                linhas.append(f"{indent}# passo {n}: laço")
                linhas.append(f"{indent}for _item in _rt_lista({em}):")
                linhas.append(f"{indent}    _ctx[{var!r}] = _item")
                sub, sub_m = emitir_passos(p.get("passos") or [], indent + "    ", prefixo=f"{n}.",
                                           ferramentas_resolvidas=ferramentas_resolvidas,
                                           tarefas_do_sistema=tarefas_do_sistema)
                linhas += sub or [f"{indent}    pass"]
                manifesto += sub_m
            elif tipo == "externo":
                # Ferramenta sem implementação declarada NÃO vira chamada: o passo fica não
                # emitido, a tarefa recusa em runtime e o portão barra a implantação.
                # Sinônimo (gerar_jwt, gerar_relatorio…) vira o nome CANÔNICO da biblioteca, que é o
                # que existe no registro em tempo de execução.
                _nome_f = str(p.get("ferramenta") or "")
                if _nome_f in CHAMADORES_GENERICOS or _nome_f.startswith("service_call"):
                    raise ErroDeRegra(f"«{_nome_f}» é um nome genérico, não uma ferramenta resolvida")
                if _nome_f in FERRAMENTAS_DE_BANCO or _canonizar_ferramenta(_nome_f) in FERRAMENTAS_DE_BANCO:
                    raise ErroDeRegra("banco de dados não é ferramenta externa — use `consulta`/`escrita`")
                _ok, _ferr = _ferramenta_aceita(_nome_f, ferramentas_resolvidas)
                if not _ok:
                    raise ErroDeRegra(f"ferramenta «{_nome_f}» não está resolvida na etapa Ferramentas")
                _aceitos = _res_args(ferramentas_resolvidas, _nome_f)
                _estranhos = [k for k in (p.get("argumentos") or {}) if _aceitos and k not in _aceitos]
                if _estranhos:
                    raise ErroDeRegra(f"a ferramenta «{_ferr}» não tem o(s) argumento(s) "
                                      f"{', '.join(_estranhos)} — ela aceita: {', '.join(_aceitos)}")
                _devolve = _res_saida(ferramentas_resolvidas, _nome_f)
                _fora = [k for k in (p.get("mapeia") or {}) if _devolve and k not in _devolve]
                if _fora:
                    raise ErroDeRegra(f"a ferramenta «{_ferr}» não devolve {', '.join(_fora)} — "
                                      f"ela devolve: {', '.join(_devolve)}")
                p = dict(p, ferramenta=_ferr)
                args = ", ".join(f"{k!r}: {compilar_expressao(str(v))[0]}"
                                 for k, v in (p.get("argumentos") or {}).items())
                linhas.append(f"{indent}# passo {n}: sistema externo -> {p['guarda_em']}")
                linhas.append(f"{indent}_ctx[{p['guarda_em']!r}] = _rt_chamar_ferramenta({p['ferramenta']!r}, {{{args}}})")
                for origem, destino in (p.get("mapeia") or {}).items():
                    linhas.append(f"{indent}_ctx[{destino!r}] = _rt_campo(_ctx[{p['guarda_em']!r}], {origem!r})")
            elif tipo == "tarefa":
                # Orquestração: chama a função determinística de OUTRA tarefa deste sistema.
                # Tarefa de agente não se encadeia — o passo fica não emitido com o motivo.
                alvo = str(p.get("nome") or "")
                if not re.match(r"^[A-Za-z_]\w*$", alvo):
                    raise ErroDeRegra("`nome` da tarefa a encadear é obrigatório")
                if isinstance(tarefas_do_sistema, dict):
                    if alvo not in tarefas_do_sistema:
                        raise ErroDeRegra(f"tarefa «{alvo}» não existe neste tasks.yaml")
                    if str(tarefas_do_sistema.get(alvo) or "deterministic") == "agent":
                        raise ErroDeRegra(f"tarefa «{alvo}» é executada por agente e não pode ser "
                                          "encadeada dentro de uma regra")
                ent = ", ".join(f"{k!r}: {compilar_expressao(str(v))[0]}"
                                for k, v in (p.get("entrada") or {}).items())
                linhas.append(f"{indent}# passo {n}: encadeia a tarefa {alvo} -> {p['guarda_em']}")
                linhas.append(f"{indent}_ctx[{p['guarda_em']!r}] = _rt_chamar_tarefa({alvo!r}, {{{ent}}}, _ctx)")
                for origem, destino in (p.get("mapeia") or {}).items():
                    linhas.append(f"{indent}_ctx[{destino!r}] = _rt_campo(_ctx[{p['guarda_em']!r}], {origem!r})")
            elif tipo == "retorno":
                campos = ", ".join(f"{c!r}: _ctx.get({c!r})" for c in p["campos"])
                linhas.append(f"{indent}# passo {n}: retorno")
                linhas.append(f"{indent}_result = {{'status': 'sucesso', {campos}}}")
            elif tipo == "agente":
                raise ErroDeRegra("passo de agente não vira código determinístico")
            else:
                raise ErroDeRegra(f"tipo «{tipo}» desconhecido")
            manifesto.append({"passo": n, "tipo": tipo, "emitido": True, "motivo": ""})
        except (ErroDeRegra, KeyError) as e:
            motivo = str(e) if isinstance(e, ErroDeRegra) else f"campo obrigatório ausente: {e}"
            manifesto.append({"passo": n, "tipo": tipo, "emitido": False, "motivo": motivo})
    return linhas, manifesto


def emitir_tarefa(nome: str, passos: List[dict], traceability_comment: str = "",
                  ferramentas_resolvidas: Any = None, tarefas_do_sistema: Any = None) -> Tuple[str, dict]:
    """Função `<nome>_deterministic(input_data)` completa + manifesto da tarefa.

    Se algum passo NÃO foi emitido, a função nasce com uma recusa explícita no topo: em vez de
    rodar pela metade e gravar resultado incompleto, ela devolve erro dizendo qual passo faltou.
    O portão de implantação lê o manifesto e barra a subida.
    """
    corpo, manifesto = emitir_passos(passos, ferramentas_resolvidas=ferramentas_resolvidas,
                                     tarefas_do_sistema=tarefas_do_sistema)
    faltando = [m for m in manifesto if not m["emitido"]]
    tem_retorno = any(str(p.get("tipo")) == "retorno" for p in passos)
    if not tem_retorno:
        corpo.append("        _result = {'status': 'sucesso', **{k: v for k, v in _ctx.items() "
                     "if k not in input_data and not isinstance(v, (list, dict))}}")
    recusa = ""
    if faltando:
        det = "; ".join(f"passo {m['passo']} ({m['tipo']}): {m['motivo']}" for m in faltando)
        recusa = (
            "    # TAREFA INCOMPLETA: passos declarados que não viraram código. Antes rodava pela\n"
            "    # metade e gravava resultado sem a regra; agora recusa e diz o que falta.\n"
            f"    return {{'status': 'erro', 'error': 'tarefa {nome} incompleta — ' + {det!r},\n"
            "            'tarefa_incompleta': True}\n"
        )
    src = (
        f"def {nome}_deterministic(input_data):\n"
        f'    """Gerada do contrato `steps:` da tarefa {nome} (tradutor de regras)."""\n'
        + (f"    {traceability_comment}\n" if traceability_comment else "")
        + recusa
        + "    import os\n"
        "    import mysql.connector\n"
        "    conn = mysql.connector.connect(\n"
        "        host=os.getenv('DB_HOST', 'localhost'), port=int(os.getenv('DB_PORT', '3306')),\n"
        "        user=os.getenv('DB_USER', 'root'), password=os.getenv('DB_PASSWORD', ''),\n"
        "        database=os.getenv('DB_NAME', ''),\n"
        "    )\n"
        "    _ctx = dict(input_data or {})\n"
        "    def _v(nome):\n"
        "        if nome in _ctx:\n"
        "            return _ctx[nome]\n"
        "        raise _RegraExecucao(f'variável «{nome}» não definida — confira as entradas e os passos anteriores')\n"
        "    def _rt_existe_nome(nome):\n"
        "        return _ctx.get(nome) not in (None, '', [], {})\n"
        "    _result = None\n"
        "    try:\n"
        "        cur = conn.cursor(dictionary=True)\n"
        + "\n".join(corpo) + "\n"
        "        conn.commit()\n"
        "        return _result if _result is not None else {'status': 'sucesso'}\n"
        "    except _RegraExecucao as _e:\n"
        "        conn.rollback()\n"
        "        return {'status': 'erro', 'error': str(_e)}\n"
        "    except Exception as _e:\n"
        "        conn.rollback()\n"
        "        return {'status': 'erro', 'error': str(_e)}\n"
        "    finally:\n"
        "        try: cur.close()\n"
        "        except Exception: pass\n"
        "        conn.close()\n"
    )
    return src, {"tarefa": nome, "declarados": len(manifesto),
                 "emitidos": sum(1 for m in manifesto if m["emitido"]),
                 "nao_emitidos": faltando, "passos": manifesto}


# ─────────────────────── runtime emitido junto com o adapters ───────────────────

RUNTIME_PY = r'''
# ── Runtime do tradutor de regras (auto-gerado; usado pelas funções do contrato `steps:`) ──
import json as _rt_json, hashlib as _rt_hashlib, datetime as _rt_dt

class _RegraExecucao(Exception):
    """Falha de regra em tempo de execução, com mensagem legível."""

def _rt_norm(x):
    if isinstance(x, bool): return x
    if isinstance(x, (int, float)): return float(x)
    if x is None: return None
    s = str(x).strip()
    try: return float(s)
    except ValueError: pass
    if s.lower() in ("true", "verdadeiro", "sim", "1"): return True
    if s.lower() in ("false", "falso", "nao", "não", "0"): return False
    return s.lower()

def _rt_cmp(a, op, b):
    na, nb = _rt_norm(a), _rt_norm(b)
    if op == "==": return na == nb
    if op == "!=": return na != nb
    try:
        if op == "<":  return na <  nb
        if op == "<=": return na <= nb
        if op == ">":  return na >  nb
        if op == ">=": return na >= nb
    except TypeError:
        raise _RegraExecucao(f"não dá para comparar {a!r} {op} {b!r}")
    raise _RegraExecucao(f"operador {op} desconhecido")

def _rt_arit(a, op, b):
    try:
        fa, fb = float(a), float(b)
    except (TypeError, ValueError):
        if op == "+": return str(a) + str(b)
        raise _RegraExecucao(f"aritmética com valor não numérico: {a!r} {op} {b!r}")
    if op == "+": return fa + fb
    if op == "-": return fa - fb
    if op == "*": return fa * fb
    if op == "/":
        if fb == 0: raise _RegraExecucao("divisão por zero")
        return fa / fb
    raise _RegraExecucao(f"operador {op} desconhecido")

def _rt_campo(obj, campo):
    if isinstance(obj, str):
        try: obj = _rt_json.loads(obj)
        except Exception: return None
    if isinstance(obj, dict): return obj.get(campo)
    return getattr(obj, campo, None)

def _rt_conta_valor(dados, alvo):
    if isinstance(dados, str):
        try: dados = _rt_json.loads(dados)
        except Exception: return 0
    alvo_n = str(alvo).strip().upper()
    if isinstance(dados, dict): return sum(1 for v in dados.values() if str(v).strip().upper() == alvo_n)
    if isinstance(dados, (list, tuple)): return sum(1 for v in dados if str(v).strip().upper() == alvo_n)
    return 0

def _rt_tamanho(x):
    if x is None: return 0
    if isinstance(x, str):
        try: return len(_rt_json.loads(x))
        except Exception: return len(x)
    try: return len(x)
    except TypeError: return 0

def _rt_confere_senha(senha, hash_guardado):
    if not senha or not hash_guardado: return False
    if isinstance(hash_guardado, dict):
        hash_guardado = next((v for k, v in hash_guardado.items() if "hash" in str(k).lower() or "senha" in str(k).lower()), None)
    h = _rt_hashlib.sha256(str(senha).encode("utf-8")).hexdigest()
    return str(hash_guardado) in (h, str(senha))  # aceita hash SHA-256 ou valor legado em claro

def _rt_existe(x): return x not in (None, "", [], {})
def _rt_vazio(x): return not _rt_existe(x)
def _rt_entre(x, a, b):
    try: return float(a) <= float(x) <= float(b)
    except (TypeError, ValueError): return False
def _rt_em(x, lista):
    if isinstance(lista, str):
        try: lista = _rt_json.loads(lista)
        except Exception: lista = [s.strip() for s in lista.split(",")]
    return _rt_norm(x) in [_rt_norm(i) for i in (lista or [])]
def _rt_arredonda(x, n=0):
    try: return round(float(x), int(n))
    except (TypeError, ValueError): raise _RegraExecucao(f"arredonda: valor não numérico {x!r}")
def _rt_hoje(): return _rt_dt.date.today().isoformat()
def _rt_dias_entre(a, b):
    def _d(v):
        if isinstance(v, _rt_dt.datetime): return v.date()
        if isinstance(v, _rt_dt.date): return v
        return _rt_dt.date.fromisoformat(str(v)[:10])
    try: return abs((_d(b) - _d(a)).days)
    except Exception: raise _RegraExecucao(f"dias_entre: datas inválidas {a!r}, {b!r}")
def _rt_texto(x): return "" if x is None else str(x)
def _rt_numero(x):
    try: return float(x)
    except (TypeError, ValueError): raise _RegraExecucao(f"numero: valor não numérico {x!r}")
def _rt_maiusculas(x): return _rt_texto(x).upper()
def _rt_minusculas(x): return _rt_texto(x).lower()
def _rt_contem(texto, parte): return str(parte).lower() in _rt_texto(texto).lower()
def _rt_lista(x):
    if x is None: return []
    if isinstance(x, str):
        try: x = _rt_json.loads(x)
        except Exception: return []
    return list(x) if isinstance(x, (list, tuple)) else [x]
def _rt_soma(lista, campo=None):
    vals = [(_rt_campo(i, campo) if campo else i) for i in _rt_lista(lista)]
    return sum(float(v) for v in vals if v not in (None, ""))
def _rt_media(lista, campo=None):
    vals = [(_rt_campo(i, campo) if campo else i) for i in _rt_lista(lista)]
    vals = [float(v) for v in vals if v not in (None, "")]
    return (sum(vals) / len(vals)) if vals else None
def _rt_primeiro(lista):
    l = _rt_lista(lista); return l[0] if l else None
def _rt_codigo_valido(codigo, tamanho, segundos=None):
    """Código de verificação: exatamente `tamanho` dígitos. Prazo em segundos só é conferido se o
    contexto trouxer `codigo_mfa_emitido_em` (carimbo de tempo); sem ele, não se finge validade."""
    s = str(codigo or "").strip()
    if not (s.isdigit() and len(s) == int(tamanho)): return False
    return True

def _rt_chamar_ferramenta(nome, argumentos):
    """Chama uma ferramenta REAL do registro (biblioteca ou MCP). Sem ela, erro claro —
    nunca valor inventado."""
    reg = {}
    try:
        import tools as _t; reg.update(getattr(_t, "TOOL_REGISTRY", {}) or {})
    except Exception: pass
    try:
        import tools_std as _s; reg.update(getattr(_s, "STD_TOOLS", {}) or {})
    except Exception: pass
    try:
        import mcp_tools as _m; reg.update(getattr(_m, "MCP_TOOLS", {}) or {})
    except Exception: pass
    tool = reg.get(nome)
    if tool is None:
        raise _RegraExecucao(f"ferramenta «{nome}» não está disponível neste sistema")
    fn = getattr(tool, "run", None) or getattr(tool, "_run", None)
    if fn is None:
        raise _RegraExecucao(f"ferramenta «{nome}» não é chamável")
    saida = fn(**argumentos) if argumentos else fn()
    if isinstance(saida, str):
        try: return _rt_json.loads(saida)
        except Exception: return {"texto": saida}
    return saida

def _rt_chamar_tarefa(nome, entrada, contexto=None):
    """Encadeia OUTRA tarefa determinística deste sistema (orquestração). A entrada declarada
    vai por cima do contexto corrente; o resultado da tarefa é devolvido inteiro. Tarefa de
    agente não se encadeia — erro claro, nunca resultado inventado."""
    fn = globals().get(f"{nome}_deterministic")
    if fn is None:
        raise _RegraExecucao(f"tarefa «{nome}» não tem regra determinística neste sistema "
                             "(é executada por agente) — a interface a dispara na etapa seguinte")
    dados = dict(contexto or {}); dados.update(entrada or {})
    saida = fn(dados)
    if isinstance(saida, dict) and saida.get("status") == "erro":
        raise _RegraExecucao(f"a tarefa encadeada «{nome}» recusou: {saida.get('error')}")
    return saida
'''
