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
  verificacao  {condicao | recusa_se, mensagem}   -- condicao: o que PRECISA valer; recusa_se: o que recusa
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
FERRAMENTAS_DE_BANCO = ("database_tool", "database_query", "db_tool", "sql_tool", "database",
                        "sql_query_tool", "sql_query", "query_tool", "db_query")


def e_ferramenta_de_banco(nome: str) -> bool:
    """Nome que denota acesso ao BANCO, e não uma ferramenta externa.

    A lista fixa não dava conta: "sql_query_tool" não contém nenhum dos nomes dela e escapava,
    virando pendência falsa ("registre na etapa MCP") para algo que nunca terá servidor externo.
    Agora vale a lista OU a combinação de uma palavra de banco (sql, database, db) com uma
    palavra de ferramenta/consulta.
    """
    alvo = (nome or "").strip().lower()
    if any(b in alvo for b in FERRAMENTAS_DE_BANCO):
        return True
    tem_banco = any(w in alvo for w in ("sql", "database", "db_", "_db"))
    tem_acao = any(w in alvo for w in ("tool", "query", "exec", "select", "insert", "client"))
    return tem_banco and tem_acao
# Ferramentas da biblioteca do gerador: SEMPRE embarcadas no app (tools_std.py), com a assinatura
# real. Entram na lista que o agente vê e na conferência de argumentos/saída mesmo quando a etapa
# Ferramentas não as cita — foi por não vê-las que o agente "fabricou" um token juntando textos.
BIBLIOTECA_ASSINATURAS = {
    "jwt_tool":           {"argumentos": ["sub", "role", "exp_horas"], "saida": ["token_jwt", "expira_em_horas"]},
    "pdf_generator_tool": {"argumentos": ["data", "output_path"], "saida": ["status", "path", "filename"]},
    "csv_exporter_tool":  {"argumentos": ["data", "output_path"], "saida": ["status", "path", "filename", "rows"]},
    "email_sender_tool":  {"argumentos": ["to", "subject", "body", "attachment_path"], "saida": []},
    "token_tool":         {"argumentos": ["usuario_id", "papel", "minutos"],
                           "saida": ["token", "assinatura", "expira_em", "minutos"]},
    "hash_chain_tool":    {"argumentos": ["autor_id", "acao", "registro_afetado", "data_hora",
                                          "marca_anterior"],
                           "saida": ["hash_atual", "marca_anterior"]},
    "password_hash_tool": {"argumentos": ["senha"], "saida": ["senha_hash"]},
    "pseudonimizar_tool": {"argumentos": ["valor", "sal"], "saida": ["pseudonimo", "hash"]},
}


def com_biblioteca(resolvidas: Any) -> dict:
    """Resolvidas da etapa Ferramentas + biblioteca do gerador (nome -> {argumentos, saida})."""
    base = {}
    if isinstance(resolvidas, dict):
        base.update(resolvidas)
    elif resolvidas:
        base.update({n: None for n in resolvidas})
    for n, v in BIBLIOTECA_ASSINATURAS.items():
        if not isinstance(base.get(n), dict):
            base[n] = dict(v)
    return base

# nome na mini-linguagem -> (função do runtime emitido, aridade mínima, aridade máxima)
FUNCOES: Dict[str, Tuple[str, int, int]] = {
    "conta_valor":   ("_rt_conta_valor", 2, 2),   # conta_valor(json, 'R')
    "tamanho":       ("_rt_tamanho", 1, 1),
    "confere_senha": ("_rt_confere_senha", 2, 2),  # confere_senha(senha, hash_guardado)
    "existe":        ("_rt_existe", 1, 1),         # tratado à parte: recebe o NOME
    "opcional":      ("_rt_opcional", 1, 1),       # idem: valor da entrada se veio, senão nulo
    "hash_senha":    ("_rt_hash_senha", 1, 1),     # SHA-256 — o mesmo que confere_senha reconhece
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
    # Conferir texto que veio de fora como JSON é necessidade real (resposta de serviço,
    # arquivo importado). Sem estas duas, o agente inventava `json_valido`/`json_parse` e o
    # contrato da ferramenta era recusado — a necessidade existia, faltava a palavra.
    "json_valido": ("_rt_json_valido", 1, 1),      # json_valido(texto) -> verdadeiro/falso
    "de_json": ("_rt_de_json", 1, 1),              # de_json(texto) -> objeto (recusa se inválido)
    # Ordenar uma lista por um campo é necessidade real ("o bundle de maior redução"): sem a
    # palavra, o contrato escrevia `ordenar(lista, por=campo, ordem=desc)` e `por`/`ordem`/`desc`
    # viravam nomes de valor que ninguém produzia — a tarefa recusava antes de começar.
    "ordenar": ("_rt_ordenar", 1, 3),              # ordenar(lista, por=campo, ordem=desc)
}


class ErroDeRegra(ValueError):
    """Expressão ou passo que não cabe no contrato — nunca vira código silenciosamente."""


# ─────────────────────────── mini-linguagem: tokens ────────────────────────────

_TOKEN = re.compile(r"""
    (?P<num>\d+(?:\.\d+)?)
  | (?P<str>'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")
  | (?P<op>==|!=|<=|>=|<|>|=|\?|:|\+|-|\*|/|\(|\)|\[|\]|,|\.)
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
        self.locais: set = set()          # nomes do "para cada", que não vêm do contexto

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
        py = self._ternario()
        if self._olha()[0] != "FIM":
            raise ErroDeRegra(f"sobrou «{self._olha()[1]}» no fim de «{self.texto}»")
        return py

    def _ternario(self) -> str:
        """«valor_a se CONDIÇÃO senao valor_b» — o jeito natural de escrever a escolha em
        português. Sem isto, `se` e `senao` eram lidos como nomes de valor e a tarefa passava a
        exigir da tela dois campos chamados «se» e «senao»."""
        esq = self._ou()
        t = self._olha()
        if t[0] == "OP" and t[1] == "?":
            self._come()
            entao = self._ternario()
            self._come("OP", ":")
            senao = self._ternario()
            return f"({entao} if {esq} else {senao})"
        if t[0] == "NOME" and t[1].lower() == "se":
            self._come()
            cond = self._ou()
            t2 = self._olha()
            if not (t2[0] == "NOME" and t2[1].lower() in ("senao", "senão")):
                raise ErroDeRegra(f"faltou «senao» na escolha em «{self.texto}»")
            self._come()
            alt = self._ternario()
            return f"({esq} if {cond} else {alt})"
        return esq

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
        # «x em [a, b]» é o jeito natural de perguntar se um valor está numa lista. Só existia
        # como função, `em(x, lista)`, e a frase entre dois valores não era lida.
        if t[0] == "NOME" and t[1].lower() == "em":
            self._come()
            return f"_rt_em({esq}, {self._add()})"
        if t[0] == "OP" and t[1] in ("==", "=", "!=", "<", "<=", ">", ">="):
            self._come()
            dir_ = self._add()
            op = "==" if t[1] == "=" else t[1]   # o contrato costuma escrever «=» para comparar
            return f"_rt_cmp({esq}, {op!r}, {dir_})"
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
            elif nome in self.locais:
                py = f"_it_{nome}"        # item do "para cada": não é valor de entrada
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
        if (nome in ("existe", "opcional") and self._olha()[0] == "NOME"
                and not (self.toks[self.i + 1][0] == "OP" and self.toks[self.i + 1][1] == ".")):
            # existe(x)/opcional(x) perguntam pelo NOME, não pelo valor — senão x ausente já
            # daria erro antes. opcional(x) é o jeito de um filtro que pode vir vazio.
            alvo = self._come()[1]
            self._come("OP", ")")
            return f"_rt_{nome}_nome({alvo!r})"
        if not (self._olha()[0] == "OP" and self._olha()[1] == ")"):
            args.append(self._arg_de_chamada())
            while self._olha()[0] == "OP" and self._olha()[1] == ",":
                self._come(); args.append(self._arg_de_chamada())
        self._come("OP", ")")
        if not (mn <= len(args) <= mx):
            raise ErroDeRegra(f"«{nome}» espera {mn}" + (f" a {mx}" if mx != mn else "")
                              + f" argumento(s), veio {len(args)}")
        return f"{fn}({', '.join(args)})"

    def _var_de_compreensao(self) -> Optional[str]:
        """Olha adiante: a lista aberta é uma compreensão «… para cada X em …»? Devolve X."""
        prof = 0
        j = self.i
        while j < len(self.toks):
            t = self.toks[j]
            if t[0] == "OP" and t[1] in ("(", "["):
                prof += 1
            elif t[0] == "OP" and t[1] in (")", "]"):
                if prof == 0:
                    return None
                prof -= 1
            elif (prof == 0 and t[0] == "NOME" and t[1].lower() == "para"
                  and j + 3 < len(self.toks)
                  and self.toks[j + 1][1].lower() == "cada"
                  and self.toks[j + 2][0] == "NOME"
                  and self.toks[j + 3][1].lower() == "em"):
                return self.toks[j + 2][1]
            j += 1
        return None

    def _arg_de_chamada(self) -> str:
        """Argumento de chamada. Aceita a forma com nome — `ordenar(lista, por=preco, ordem=desc)`
        — em que o que vem depois do `=` é o NOME de um campo, e portanto texto."""
        t, prox = self._olha(), self.toks[self.i + 1] if self.i + 1 < len(self.toks) else ("FIM", "")
        if t[0] == "NOME" and prox[0] == "OP" and prox[1] == "=":
            rotulo = self._come()[1].lower()
            self._come("OP", "=")
            alvo = self._olha()
            if alvo[0] == "NOME" and not (self.toks[self.i + 1][0] == "OP"
                                          and self.toks[self.i + 1][1] in ("(", ".")):
                valor = repr(self._come()[1])
            else:
                valor = self._ternario()
            return f"{rotulo}={valor}"
        return self._ternario()

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
            py = self._ternario(); self._come("OP", ")"); return f"({py})"
        if t[0] == "OP" and t[1] == "[":
            # «[b para cada b em lista se CONDIÇÃO]» — a lista filtrada, escrita em português.
            # Sem isto, `para`, `cada`, `em` e `se` eram lidos como valores que a tela teria de
            # mandar, e o passo não virava código.
            _var = self._var_de_compreensao()
            if _var:
                self.locais.add(_var)
                item = self._ternario()
                self._come("NOME"); self._come("NOME")          # para cada
                self._come("NOME"); self._come("NOME")          # <var> em
                origem = self._ou()
                cond = None
                if self._olha()[0] == "NOME" and self._olha()[1].lower() == "se":
                    self._come(); cond = self._ou()
                self._come("OP", "]")
                self.locais.discard(_var)
                filtro = f" if {cond}" if cond else ""
                return f"[{item} for _it_{_var} in _rt_lista({origem}){filtro}]"
            itens = []
            if not (self._olha()[0] == "OP" and self._olha()[1] == "]"):
                itens.append(self._ternario())
                while self._olha()[0] == "OP" and self._olha()[1] == ",":
                    self._come(); itens.append(self._ternario())
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
        return [str(p.get("condicao") or p.get("recusa_se") or "")]
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
        return [re.split(r"\s+como\s+", str(c))[0] for c in (p.get("campos") or []) if isinstance(c, str)]
    if tipo == "agente":
        # `usa`: os valores que o PROGRAMA entrega ao modelo. São expressões como quaisquer
        # outras — se citarem um nome que nenhum passo produziu, o contrato acusa.
        return [str(v) for v in (p.get("usa") or []) if isinstance(v, (str, int, float))]
    return []



def conferir_chamadas_externas(tarefas: dict, fichas: dict, tipos_das_colunas: dict = None) -> list:
    """Confere cada chamada a servico externo contra a FICHA que o servico declara.

    POR QUE (15/09/2026): a estimativa de reducao de risco chamava o escore de Cox passando o
    VALOR DO ESCORE no lugar da idade e tambem no lugar do APACHE II. A ficha do servico diz, com
    todas as letras, que os dois sao inteiros obrigatorios. Ninguem conferia — o erro so aparecia
    em execucao, embrulhado num "falha no sistema externo".

    Devolve a lista de divergencias: argumento que o servico nao conhece, obrigatorio que ninguem
    passou, e campo lido da resposta que o servico nao devolve.
    """
    achados = []

    def _varrer(nome_tarefa, passos):
        for p in (passos or []):
            if not isinstance(p, dict):
                continue
            if str(p.get("tipo")) == "externo" and p.get("ferramenta") in fichas:
                ficha = fichas[p["ferramenta"]]
                recebe = ficha.get("recebe") or {}
                devolve = ficha.get("devolve") or {}
                passados = set((p.get("argumentos") or {}).keys())
                if recebe:
                    for arg in sorted(passados - set(recebe)):
                        achados.append({
                            "tarefa": nome_tarefa, "ferramenta": p["ferramenta"], "tipo": "argumento_desconhecido",
                            "o_que": f"passa «{arg}», que o serviço não recebe "
                                     f"(ele recebe: {', '.join(recebe) or 'nada'})"})
                    for obrig in sorted(k for k, v in recebe.items() if v.get("obrigatorio")):
                        if obrig not in passados:
                            achados.append({
                                "tarefa": nome_tarefa, "ferramenta": p["ferramenta"], "tipo": "obrigatorio_faltando",
                                "o_que": f"o serviço exige «{obrig}» ({recebe[obrig]['tipo']}) e a chamada não passa"})
                # TIPO do que esta sendo passado. O nome do argumento pode estar certo e o VALOR
                # errado: a estimativa passava `escore_info.valor_escore` (decimal) no campo
                # `idade`, que a ficha declara como INTEIRO. Nome conferia, tipo nao — e so
                # estourava em execucao, embrulhado num "falha no sistema externo".
                colunas = tipos_das_colunas or {}
                for arg, valor in (p.get("argumentos") or {}).items():
                    esperado = (recebe.get(arg) or {}).get("tipo")
                    if not esperado or not isinstance(valor, str):
                        continue
                    campo = valor.split(".")[-1].strip().strip("'\"")
                    tipo_sql = (colunas.get(campo) or "").upper()
                    if not tipo_sql:
                        continue
                    familia = ("integer" if tipo_sql.startswith(("INT", "BIGINT", "SMALLINT", "TINYINT"))
                               else "number" if tipo_sql.startswith(("DECIMAL", "NUMERIC", "FLOAT", "DOUBLE"))
                               else "boolean" if tipo_sql.startswith("BOOL")
                               else "string")
                    if familia != esperado and not (esperado == "number" and familia == "integer"):
                        achados.append({
                            "tarefa": nome_tarefa, "ferramenta": p["ferramenta"], "tipo": "tipo_incompativel",
                            "o_que": f"passa «{valor}» ({familia}) em «{arg}», que o servico declara "
                                     f"como {esperado}"})
                if devolve:
                    for campo in sorted((p.get("mapeia") or {}).keys()):
                        if campo not in devolve:
                            achados.append({
                                "tarefa": nome_tarefa, "ferramenta": p["ferramenta"], "tipo": "resposta_inexistente",
                                "o_que": f"lê «{campo}» da resposta, que o serviço não devolve "
                                         f"(ele devolve: {', '.join(devolve)})"})
            for aninhado in ("passos", "senao", "passos_senao"):
                if p.get(aninhado):
                    _varrer(nome_tarefa, p[aninhado])

    for nome, cfg in (tarefas or {}).items():
        if isinstance(cfg, dict):
            _varrer(nome, cfg.get("steps"))
    return achados

def resolver_nomes_de_linha(passos: List[dict],
                            entradas_declaradas: Optional[List[str]] = None,
                            tarefas_do_sistema: Optional[Any] = None,
                            apelidos: Optional[Dict[str, str]] = None,
                            tabelas: Optional[Dict[str, List[str]]] = None,
                            ferramentas_resolvidas: Any = None,
                            nome_tarefa: str = "",
                            entradas_por_tarefa: Optional[Dict[str, List[str]]] = None,
                            colunas_opcionais: Optional[Dict[str, set]] = None) -> List[str]:
    """Liga nome solto ao campo da LINHA que um passo anterior capturou.

    POR QUE: o contrato consulta `SELECT id, senha_hash, papel, ativo ... guarda_em: usuario` e
    depois usa `usuario_id` e `papel` soltos — que são `usuario.id` e `usuario.papel`. Como
    ninguém os produz com esse nome, a tarefa recusa antes de começar: medido no BioByte em
    23/09/2026, o login devolvia "E-mail ou senha inválidos" com senha CERTA, e o detalhe técnico
    dizia "inputs obrigatórios ausentes: hash_atual, marca_anterior, papel, usuario_id".

    A informação para resolver está no próprio contrato: as colunas da consulta. Aqui o programa
    reescreve `papel` → `usuario.papel` e `usuario_id` → `usuario.id`, e devolve a lista do que
    resolveu. O que não casar continua pendente e é declarado — nada é adivinhado.
    """
    colunas_por_linha: Dict[str, List[str]] = {}
    trocas: List[str] = []

    def _colunas_do_select(sql: str) -> List[str]:
        m = re.search(r"select\s+(.+?)\s+from\s", str(sql or ""), re.I | re.S)
        if not m:
            return []
        cols = []
        for parte in m.group(1).split(","):
            parte = parte.strip()
            if not parte or parte == "*":
                continue
            apelido = re.search(r"\bas\s+([A-Za-z_]\w*)\s*$", parte, re.I)
            nome = apelido.group(1) if apelido else parte.split(".")[-1].strip("` ")
            if re.fullmatch(r"[A-Za-z_]\w*", nome or ""):
                cols.append(nome)
        return cols

    def _mapear(lista):
        for p in lista or []:
            if not isinstance(p, dict):
                continue
            if str(p.get("tipo")) == "consulta" and p.get("guarda_em"):
                colunas_por_linha[str(p["guarda_em"])] = _colunas_do_select(p.get("sql"))
            for campo in ("passos", "senao", "passos_senao"):
                if isinstance(p.get(campo), list):
                    _mapear(p[campo])
    _mapear(passos)

    def _resolver(nome: str, disponiveis: Optional[set] = None) -> Optional[str]:
        """`disponiveis` limita a busca às linhas JÁ capturadas. Sem esse limite, o programa
        resolvia o nome pela linha que o PRÓPRIO passo ainda ia capturar — `usuario_id` virava
        `usuario.id` dentro da consulta que busca o usuário, e a tarefa passava a exigir da tela
        um valor chamado «usuario»."""
        for linha, cols in colunas_por_linha.items():
            if disponiveis is not None and linha not in disponiveis:
                continue
            if nome == f"{linha}_id" and "id" in cols:
                return f"{linha}.id"
            if nome in cols:
                return f"{linha}.{nome}"
        return None

    produzidos: set = set()
    _declaradas_ini = {str(x) for x in (entradas_declaradas or [])}

    def _reescrever(lista):
        for p in lista or []:
            if not isinstance(p, dict):
                continue
            for k in ("guarda_em", "atribui", "guarda_id_em", "para_cada"):
                if p.get(k):
                    produzidos.add(str(p[k]))
            # parâmetros de consulta/escrita
            if isinstance(p.get("params"), list):
                novos = []
                for arg in p["params"]:
                    a = str(arg)
                    if (re.fullmatch(r"[A-Za-z_]\w*", a) and a not in produzidos
                            and a not in _declaradas_ini):
                        alvo = _resolver(a, produzidos)
                        if alvo:
                            trocas.append(f"{a} → {alvo}")
                            novos.append(alvo)
                            continue
                    novos.append(arg)
                p["params"] = novos
            # campos devolvidos
            if str(p.get("tipo")) == "retorno" and isinstance(p.get("campos"), list):
                novos = []
                for c in p["campos"]:
                    a = str(c)
                    if a not in produzidos and a not in _declaradas_ini:
                        alvo = _resolver(a, produzidos)
                        if alvo:
                            # o retorno mantém o NOME curto, mas passa a existir como cálculo
                            trocas.append(f"retorno {a} ← {alvo}")
                            novos.append(a)
                            continue
                    novos.append(c)
                p["campos"] = novos
            for campo in ("passos", "senao", "passos_senao"):
                if isinstance(p.get(campo), list):
                    _reescrever(p[campo])
    _reescrever(passos)

    # ENCADEAMENTO DA AUDITORIA: a gravação em registros_auditoria pede `marca_anterior` (a marca
    # do registro anterior) e `hash_atual` (a marca deste). Nenhum dos dois é entrada de tela e
    # nenhum passo os produzia — a tarefa recusava antes de começar. A ferramenta existe no pacote
    # e devolve exatamente `hash_atual`; aqui o programa costura os dois passos que faltavam.
    def _costurar_auditoria(lista):
        i = 0
        while i < len(lista):
            p = lista[i]
            if isinstance(p, dict):
                for campo in ("passos", "senao", "passos_senao"):
                    if isinstance(p.get(campo), list):
                        _costurar_auditoria(p[campo])
                # A gravação da trilha pede a marca anterior e a marca deste evento. O contrato
                # às vezes as nomeia (marca_anterior, hash_atual) e às vezes deixa o lugar EM
                # BRANCO — e aí a gravação morre com "expressão vazia". Os dois casos são a mesma
                # falta, e aqui os dois são costurados.
                _cols = dict(_colunas_com_marcador(str(p.get("sql") or ""))) \
                    if str(p.get("tipo")) == "escrita" else {}
                _par = list(p.get("params") or [])
                def _falta(col: str) -> bool:
                    idx = _cols.get(col)
                    if idx is None or idx >= len(_par):
                        return False
                    v = str(_par[idx]).strip()
                    return (not v) or (re.fullmatch(r"[A-Za-z_]\w*", v) and v not in produzidos)
                _precisa_marca = ("registros_auditoria" in str(p.get("sql") or "")
                                  and (_falta("hash_atual") or _falta("marca_anterior")))
                usados = {str(x) for x in _par}
                if (str(p.get("tipo")) == "escrita"
                        and "registros_auditoria" in str(p.get("sql") or "")
                        and (({"marca_anterior", "hash_atual"} & usados) or _precisa_marca)
                        and "marca_anterior" not in produzidos):
                    for _c in ("hash_atual", "marca_anterior"):
                        _i = _cols.get(_c)
                        if _i is not None and _i < len(_par) and not str(_par[_i]).strip():
                            _par[_i] = _c
                    _i = _cols.get("data_hora")
                    if _i is not None and _i < len(_par) and not str(_par[_i]).strip():
                        _par[_i] = "hoje()"
                    p["params"] = _par
                    autor = next((str(x) for x in _par
                                  if str(x).endswith(".id") or str(x).endswith("_id")), "usuario.id")
                    antes = [
                        {"tipo": "consulta",
                         "sql": "SELECT hash_atual FROM registros_auditoria ORDER BY created_at DESC LIMIT 1",
                         "params": [], "guarda_em": "marca_anterior", "forma": "escalar"},
                        {"tipo": "externo", "ferramenta": "hash_chain_tool",
                         "argumentos": {"autor_id": autor, "acao": "'registro'",
                                        "registro_afetado": autor, "data_hora": "hoje()",
                                        "marca_anterior": "marca_anterior"},
                         "guarda_em": "hash_atual", "mapeia": {"hash_atual": "hash_atual"}},
                    ]
                    lista[i:i] = antes
                    produzidos.update({"marca_anterior", "hash_atual"})
                    trocas.append("encadeamento da auditoria costurado "
                                  "(marca anterior consultada + marca atual pela ferramenta)")
                    i += len(antes)
            i += 1
    _costurar_auditoria(passos)

    # o retorno precisa que o nome curto EXISTA: acrescenta um cálculo antes do retorno
    for i, p in enumerate(list(passos)):
        if isinstance(p, dict) and str(p.get("tipo")) == "retorno":
            faltam = []
            for c in (p.get("campos") or []):
                a = str(c)
                if a in produzidos:
                    continue
                alvo = _resolver(a)
                if alvo:
                    faltam.append({"tipo": "calculo", "atribui": a, "expressao": alvo})
                    produzidos.add(a)
            if faltam:
                passos[i:i] = faltam
                trocas += [f"{x['atribui']} = {x['expressao']} (acrescentado antes do retorno)"
                           for x in faltam]
            break

    # CHAMAR QUEM NÃO EXISTE: o contrato encadeia "tarefas" que são, na verdade, o CÓDIGO da
    # tarefa no documento de agentes e tarefas (T-AUT-002), o código do agente de auditoria
    # (AG-13) ou um ajudante que ninguém escreveu (auditar_classificacao). Como o passo não vira
    # código, a tarefa inteira recusa em runtime. Medido no BioByte em 23/09/2026: 15 das 22
    # tarefas com contrato recusavam, e a causa mais comum era esta.
    # Aqui o programa faz três coisas, sempre declarando o que fez:
    #   · código do documento  -> nome da tarefa correspondente;
    #   · auditoria            -> os três passos que a auditoria realmente é (marca anterior,
    #                             marca deste evento pela ferramenta, gravação na trilha);
    #   · conferir o usuário   -> a consulta e a recusa que as outras tarefas já fazem à mão.
    _nomes_sys = set(tarefas_do_sistema or [])
    _apelidos = {k.upper(): v for k, v in (apelidos or {}).items()}

    def _auditoria_trio(entrada: dict, guarda: str) -> List[dict]:
        autor = str(entrada.get("autor_id") or entrada.get("usuario_id") or "usuario_id")
        acao = entrada.get("acao")
        alvo = str(entrada.get("registro_afetado")
                   or next((v for k, v in entrada.items()
                            if k.endswith("_id") and k not in ("autor_id", "usuario_id")), autor))
        acao_expr = f"'{acao}'" if acao and re.fullmatch(r"[A-Za-z_]\w*", str(acao)) else (acao or "'registro'")
        return [
            {"tipo": "consulta",
             "sql": "SELECT hash_atual FROM registros_auditoria ORDER BY created_at DESC LIMIT 1",
             "params": [], "guarda_em": "marca_anterior", "forma": "escalar"},
            {"tipo": "externo", "ferramenta": "hash_chain_tool",
             "argumentos": {"autor_id": autor, "acao": acao_expr, "registro_afetado": alvo,
                            "data_hora": "hoje()", "marca_anterior": "marca_anterior"},
             "guarda_em": guarda or "auditoria", "mapeia": {"hash_atual": "hash_atual"}},
            {"tipo": "escrita",
             "sql": ("INSERT INTO registros_auditoria(autor_id, acao, registro_afetado, "
                     "marca_anterior, hash_atual) VALUES(%s,%s,%s,%s,%s)"),
             "params": [autor, acao_expr, alvo, "marca_anterior", "hash_atual"]},
        ]

    def _escolher_servico(passo: dict, tarefa: str, resolvidas: Any) -> Optional[str]:
        """Qual serviço externo a chamada genérica queria? O que mais compartilha palavras com o
        assunto da tarefa e com os valores passados. Sem candidato, nada é escolhido."""
        nomes = [n for n in _res_nomes(resolvidas) if n not in ferramentas_da_biblioteca()]
        if not nomes:
            return None
        def _palavras(t: str) -> set:
            return {w for w in re.split(r"[^a-z0-9]+", str(t).lower()) if len(w) > 3}
        alvo = _palavras(tarefa) | _palavras(" ".join(str(v) for v in (passo.get("argumentos") or {}).values())) \
            | _palavras(str(passo.get("guarda_em") or ""))
        melhor, pontos = None, 0
        for n in nomes:
            p_ = len(_palavras(n) & alvo)
            if p_ > pontos:
                melhor, pontos = n, p_
        return melhor if pontos >= 1 else None

    def _gravacao_de(alvo: str, entrada: dict, guarda: str) -> Optional[List[dict]]:
        """«criar_alerta_multirresistencia» não é tarefa: é a GRAVAÇÃO numa tabela. O nome diz a
        tabela e a entrada diz as colunas — o resto é o INSERT que o contrato descreveu por
        extenso. Sem tabela correspondente, nada é inventado."""
        if not tabelas:
            return None
        assunto = re.sub(r"^(criar|inserir|gravar|registrar|adicionar)_", "", alvo.lower())
        if not assunto:
            return None
        cand = [t for t in tabelas
                if t.lower() in (assunto, assunto + "s", assunto + "es")
                or re.sub(r"(s|es)$", "", t.lower()) == assunto
                or t.lower().replace("_", "") == assunto.replace("_", "")]
        if not cand:
            # "resultado_hemocultura" -> "resultados_hemocultura"
            partes = assunto.split("_")
            alvo_plural = "_".join([partes[0] + "s"] + partes[1:])
            cand = [t for t in tabelas if t.lower() == alvo_plural]
        if not cand:
            return None
        tab = cand[0]
        cols = [c for c in (tabelas.get(tab) or []) if c in entrada]
        if not cols:
            return None
        return [{"tipo": "escrita",
                 "sql": f"INSERT INTO {tab}({', '.join(cols)}) VALUES({', '.join(['%s'] * len(cols))})",
                 "params": [str(entrada[c]) for c in cols],
                 "guarda_id_em": guarda or f"{tab}_id"}]

    def _conferir_usuario(entrada: dict) -> List[dict]:
        quem = str(entrada.get("usuario_id") or "usuario_id")
        return [
            {"tipo": "consulta", "sql": "SELECT id, papel, ativo FROM usuarios WHERE id=%s",
             "params": [quem], "guarda_em": "usuario", "forma": "linha"},
            {"tipo": "verificacao", "recusa_se": "nao existe(usuario) ou usuario.ativo = 0",
             "mensagem": "Usuário inválido ou inativo."},
        ]

    def _ajustar_encadeamentos(lista):
        i = 0
        while i < len(lista):
            p = lista[i]
            if isinstance(p, dict):
                for campo in ("passos", "senao", "passos_senao", "entao", "corpo"):
                    if isinstance(p.get(campo), list):
                        _ajustar_encadeamentos(p[campo])
                if str(p.get("tipo")) == "externo":
                    _f = str(p.get("ferramenta") or "").lower()
                    # "chamar a API" não é ferramenta: o serviço externo tem nome e ficha, e é um
                    # dos que a etapa Ferramentas resolveu (MCP). Aqui o programa escolhe o
                    # serviço pelo assunto da tarefa e dos argumentos, e tira o envelope da
                    # chamada (servico, timeout, endpoint), que não é dado do serviço.
                    if _f in CHAMADORES_GENERICOS or _f.startswith("service_call") or _f == "api_call_tool":
                        _cand = _escolher_servico(p, nome_tarefa, ferramentas_resolvidas)
                        if _cand:
                            _aceita = _res_args(ferramentas_resolvidas, _cand)
                            _envelope = {"servico", "service", "endpoint", "url", "timeout",
                                         "metodo", "method", "tempo_limite"}
                            _args = {k: v for k, v in (p.get("argumentos") or {}).items()
                                     if k not in _envelope}
                            if _aceita:
                                _sobra = [k for k in _args if k not in _aceita]
                                _faltam = [k for k in _aceita if k not in _args]
                                if len(_sobra) == 1 and len(_faltam) == 1:
                                    _args[_faltam[0]] = _args.pop(_sobra[0])
                                    trocas.append(f"o serviço {_cand} recebe «{_faltam[0]}» — "
                                                  f"o contrato chamava de «{_sobra[0]}»")
                                else:
                                    for k in _sobra:
                                        _args.pop(k, None)
                            p["ferramenta"] = _cand
                            p["argumentos"] = _args
                            trocas.append(f"«{p.get('ferramenta')}»: a chamada genérica virou o "
                                          f"serviço externo {_cand}")
                    _ar = p.get("argumentos") if isinstance(p.get("argumentos"), dict) else {}
                    # "ferramenta de auditoria" não é ferramenta: auditoria é gravar na trilha.
                    if "auditoria" in _f or _f.startswith("auditar"):
                        trio = _auditoria_trio(_ar, str(p.get("guarda_em") or "auditoria"))
                        lista[i:i + 1] = trio
                        produzidos.update({"marca_anterior", "hash_atual",
                                           str(p.get("guarda_em") or "auditoria")})
                        trocas.append(f"«{p.get('ferramenta')}» não é uma ferramenta: virou a "
                                      f"gravação na trilha de auditoria")
                        i += len(trio)
                        continue
                    # Pedir o usuário ao "banco como ferramenta" é, na verdade, conferir o usuário.
                    if (_f in FERRAMENTAS_DE_BANCO or _canonizar_ferramenta(_f) in FERRAMENTAS_DE_BANCO) \
                            and set(_ar) <= {"usuario_id", "id"} and _ar:
                        par = _conferir_usuario(_ar)
                        lista[i:i + 1] = par
                        produzidos.add("usuario")
                        trocas.append("a conferência do usuário estava escrita como chamada ao "
                                      "banco — virou consulta e recusa")
                        i += len(par)
                        continue
                    # Resumo de um valor com sal é pseudonimização, não marca de auditoria.
                    if _f == "hash_chain_tool" and ("valor" in _ar or "sal" in _ar):
                        p["ferramenta"] = "pseudonimizar_tool"
                        trocas.append("o resumo de um valor com sal é pseudonimização → "
                                      "pseudonimizar_tool")
                if str(p.get("tipo")) == "tarefa":
                    alvo = str(p.get("nome") or p.get("tarefa") or "").strip()
                    ent = p.get("entrada") if isinstance(p.get("entrada"), dict) else {}
                    if alvo and alvo not in _nomes_sys and alvo.upper() in _apelidos:
                        novo_nome = _apelidos[alvo.upper()]
                        trocas.append(f"o contrato chamava «{alvo}», que é o código no documento — "
                                      f"passa a chamar a tarefa {novo_nome}")
                        p["nome"] = novo_nome
                        alvo = novo_nome
                    # ENCADEAR QUEM PEDE OUTRA COISA: o contrato manda "chamar autenticar_usuario"
                    # passando só o identificador do usuário — e autenticar pede e-mail e senha.
                    # A chamada nunca dá certo, e a tarefa inteira recusa logo no segundo passo.
                    # Quando a intenção é claramente conferir quem está operando, isso vira a
                    # consulta e a recusa que as outras tarefas fazem à mão.
                    if (alvo in _nomes_sys and entradas_por_tarefa
                            and entradas_por_tarefa.get(alvo)):
                        _pede = {str(x) for x in entradas_por_tarefa[alvo]}
                        _tem = {str(k) for k in ent}
                        if _pede - _tem and _tem and _tem <= {"usuario_id", "id", "autor_id"}:
                            par = _conferir_usuario(ent)
                            lista[i:i + 1] = par
                            produzidos.add("usuario")
                            if p.get("guarda_em"):
                                par.append({"tipo": "calculo", "atribui": str(p["guarda_em"]),
                                            "expressao": "usuario"})
                                produzidos.add(str(p["guarda_em"]))
                                lista[i:i + 2] = par
                            trocas.append(f"chamar «{alvo}» com {sorted(_tem)} não daria certo "
                                          f"(ela pede {sorted(_pede)}) — virou a conferência do "
                                          f"usuário")
                            i += len(par)
                            continue
                    if alvo and alvo not in _nomes_sys:
                        baixo = alvo.lower()
                        if baixo.startswith("ag-13") or "auditar" in baixo or "auditoria" in baixo:
                            trio = _auditoria_trio(ent, str(p.get("guarda_em") or "auditoria"))
                            lista[i:i + 1] = trio
                            produzidos.update({"marca_anterior", "hash_atual",
                                               str(p.get("guarda_em") or "auditoria")})
                            trocas.append(f"«{alvo}» não é uma tarefa: virou a trilha de auditoria "
                                          f"de verdade (marca anterior, marca deste evento, gravação)")
                            i += len(trio)
                            continue
                        _grav = (_gravacao_de(alvo, ent, str(p.get("guarda_em") or ""))
                                 if re.match(r"^(criar|inserir|gravar|adicionar)_", baixo) else None)
                        if _grav:
                            lista[i:i + 1] = _grav
                            produzidos.add(str(_grav[0].get("guarda_id_em")))
                            trocas.append(f"«{alvo}» não é uma tarefa: virou a gravação em "
                                          f"{_grav[0]['sql'].split()[2].split('(')[0]}")
                            i += len(_grav)
                            continue
                        if re.match(r"^(validar|conferir)_(usuario|sessao|token)", baixo) or baixo.startswith("t-aut"):
                            par = _conferir_usuario(ent)
                            lista[i:i + 1] = par
                            produzidos.add("usuario")
                            trocas.append(f"«{alvo}» não é uma tarefa: virou a conferência do "
                                          f"usuário (consulta + recusa se inexistente ou inativo)")
                            i += len(par)
                            continue
            i += 1
    _ajustar_encadeamentos(passos)

    # COLUNA QUE ACEITA VAZIO NÃO OBRIGA A TELA: o cadastro de um caso que está ABRINDO não tem
    # data de encerramento, e o modelo de dados diz isso (a coluna aceita vazio). Mesmo assim a
    # tarefa exigia o campo e recusava antes de começar. Aqui o valor passa a ser opcional —
    # continua indo para a gravação, e vai vazio quando a tela não mandar.
    if colunas_opcionais:
        def _opcionalizar(lista):
            for p in lista or []:
                if not isinstance(p, dict):
                    continue
                if str(p.get("tipo")) in ("escrita", "consulta") and isinstance(p.get("params"), list):
                    tab = re.search(r"(?is)\b(?:into|update)\s+`?(\w+)`?", str(p.get("sql") or ""))
                    livres = colunas_opcionais.get(tab.group(1).lower()) if tab else None
                    if livres:
                        cols = dict(_colunas_com_marcador(str(p.get("sql") or "")))
                        novos = list(p["params"])
                        for col, idx in cols.items():
                            if (col in livres and idx < len(novos)
                                    and re.fullmatch(r"[A-Za-z_]\w*", str(novos[idx]))):
                                novos[idx] = f"opcional({novos[idx]})"
                                trocas.append(f"«{col}» aceita vazio no modelo de dados — a tela "
                                              f"não é obrigada a mandar")
                        p["params"] = novos
                for campo in ("passos", "senao", "passos_senao", "entao", "corpo"):
                    if isinstance(p.get(campo), list):
                        _opcionalizar(p[campo])
        _opcionalizar(passos)

    # PASSO DE JULGAMENTO SEM DIZER O QUE DEVOLVE: o contrato escreve a instrução ao modelo
    # ("determine o resultado, com justificativa") e esquece de listar o que ele devolve. Sem essa
    # lista o passo não vira código e a tarefa recusa — e, pior, os nomes que os passos SEGUINTES
    # usavam passavam a ser cobrados da tela. O que ele devolve está justamente aí: são os nomes
    # que os passos seguintes usam e que ninguém produz.
    def _pendentes_depois(lista: List[dict], desde: int, ja: set) -> List[str]:
        falta: List[str] = []
        def _varre(ps):
            for q in ps or []:
                if not isinstance(q, dict):
                    continue
                for expr in _expressoes_do_passo(q):
                    try:
                        _, nomes = compilar_expressao(str(expr))
                    except Exception:
                        continue
                    for n in nomes:
                        if n not in ja and n not in falta:
                            falta.append(n)
                for k in ("guarda_em", "atribui", "guarda_id_em", "para_cada"):
                    if q.get(k):
                        ja.add(str(q[k]))
                for m in (q.get("mapeia") or {}).values():
                    ja.add(str(m))
                for c in ("passos", "senao", "passos_senao", "entao", "corpo"):
                    if isinstance(q.get(c), list):
                        _varre(q[c])
                for campo in (q.get("campos") or []):
                    n = str(campo).split(" como ")[0].strip()
                    if "." not in n and n not in ja and n not in falta:
                        falta.append(n)
        _varre(lista[desde + 1:])
        return falta

    if entradas_declaradas is not None:
        _ja = set(produzidos) | {str(x) for x in entradas_declaradas}
        for _i, _p in enumerate(passos):
            if not isinstance(_p, dict) or str(_p.get("tipo")) != "agente":
                continue
            if _p.get("devolve") or not _p.get("instrucao"):
                continue
            _alvo = [n for n in _pendentes_depois(passos, _i, set(_ja)) if not _resolver(n)][:6]
            if _p.get("guarda_em") and str(_p["guarda_em"]) not in _alvo:
                _alvo.insert(0, str(_p["guarda_em"]))
            if _alvo:
                _p["devolve"] = _alvo
                produzidos.update(_alvo)
                trocas.append("o passo de julgamento não dizia o que devolve — devolve "
                              + ", ".join(_alvo) + " (o que os passos seguintes usam)")

    # RECUSA QUE NÃO DÁ PARA CONFERIR: `recusa_se: "nao valido"` quando nenhum passo produz
    # «valido» e a tela não manda nada com esse nome. A conferência não tem como ser feita — e,
    # do jeito que estava, virava exigência de um campo fantasma na tela. Sai do código e fica
    # declarada, para aparecer no portão.
    if entradas_declaradas is not None:
        _conhecidos = set(produzidos) | {str(x) for x in entradas_declaradas}
        _sobra = []
        for _p in passos:
            if (isinstance(_p, dict) and str(_p.get("tipo")) == "verificacao"
                    and _p.get("recusa_se")):
                try:
                    _, _ns = compilar_expressao(str(_p["recusa_se"]))
                except Exception:
                    _ns = []
                _orfaos = [n for n in _ns if n not in _conhecidos and not _resolver(n)]
                if _ns and len(_orfaos) == len(set(_ns)):
                    trocas.append(f"a recusa «{_p['recusa_se']}» fala de "
                                  f"{', '.join(sorted(set(_orfaos)))}, que ninguém produz e a tela "
                                  f"não manda — a conferência não virou código")
                    continue
            _sobra.append(_p)
        if len(_sobra) != len(passos):
            passos[:] = _sobra

    # TEXTO FIXO SEM ASPAS: o contrato escreve `params: [caso_id, auditoria_encerramento, baixa]`
    # querendo dizer que as duas últimas são PALAVRAS — o tipo e a gravidade do registro. Sem as
    # aspas elas viram nomes de valor que ninguém produz, e a tarefa passa a exigir da tela dois
    # campos que a tela nunca teve. Medido no BioByte em 23/09/2026: 17 das 22 tarefas com
    # contrato exigiam valores assim e recusavam antes de começar.
    # A prova de que é palavra, e não valor: não está no `Input data format` da tarefa, nenhum
    # passo a produz e não é coluna de nenhuma linha consultada. Aí, e só aí, vira texto.
    if entradas_declaradas is not None:
        _declaradas = {str(x) for x in entradas_declaradas}
        _vistos: set = set(produzidos)

        def _e_palavra(a: str) -> bool:
            return (bool(re.fullmatch(r"[A-Za-z_]\w*", a))
                    and a not in _vistos and a not in _declaradas
                    and a not in FUNCOES and a not in _PALAVRAS
                    and not _resolver(a) and a not in colunas_por_linha)

        def _aspas(lista):
            for p in lista or []:
                if not isinstance(p, dict):
                    continue
                if isinstance(p.get("params"), list):
                    novos = []
                    for arg in p["params"]:
                        a = str(arg)
                        if _e_palavra(a):
                            trocas.append(f"{a} é palavra fixa, não valor de tela → '{a}'")
                            novos.append(f"'{a}'")
                        else:
                            novos.append(arg)
                    p["params"] = novos
                for _chave_dict in ("argumentos", "entrada"):
                    if isinstance(p.get(_chave_dict), dict):
                        for k, v in list(p[_chave_dict].items()):
                            a = str(v)
                            if _e_palavra(a):
                                trocas.append(f"{a} é palavra fixa, não valor de tela → '{a}'")
                                p[_chave_dict][k] = f"'{a}'"
                for k in ("guarda_em", "atribui", "guarda_id_em", "para_cada"):
                    if p.get(k):
                        _vistos.add(str(p[k]))
                for m in (p.get("mapeia") or {}).values():
                    _vistos.add(str(m))
                for campo in ("passos", "senao", "passos_senao", "entao", "corpo"):
                    if isinstance(p.get(campo), list):
                        _aspas(p[campo])
        _aspas(passos)

        # DEVOLVER O QUE NÃO EXISTE: campo de retorno que nenhum passo produz, que não é entrada
        # e não é coluna de linha nenhuma. Antes ele obrigava a tela a mandar o próprio resultado.
        _vistos = set(produzidos) | _declaradas
        def _produzidos_todos(lista):
            for p in lista or []:
                if not isinstance(p, dict):
                    continue
                for k in ("guarda_em", "atribui", "guarda_id_em", "para_cada"):
                    if p.get(k):
                        _vistos.add(str(p[k]))
                for m in (p.get("mapeia") or {}).values():
                    _vistos.add(str(m))
                for campo in ("passos", "senao", "passos_senao", "entao", "corpo"):
                    if isinstance(p.get(campo), list):
                        _produzidos_todos(p[campo])
        _produzidos_todos(passos)
        for p in passos:
            if isinstance(p, dict) and str(p.get("tipo")) == "retorno" and isinstance(p.get("campos"), list):
                mantem = []
                for c in p["campos"]:
                    a = str(c).split(" como ")[0].strip()
                    if a in _vistos or "." in a or _resolver(a):
                        mantem.append(c)
                    else:
                        trocas.append(f"o contrato mandava devolver «{a}», que nenhum passo "
                                      f"produz — retirado do retorno")
                p["campos"] = mantem or p["campos"]
    return trocas


def _nomes_perguntados(expr: str) -> List[str]:
    """Nomes que a expressão apenas PERGUNTA se existem — `existe(x)`, `opcional(x)`. Podem faltar
    sem que a tarefa recuse."""
    try:
        toks = _tokenizar(re.sub(r"\{\{?\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}?\}", r"\1", str(expr)))
    except Exception:
        return []
    fora = []
    for i in range(2, len(toks)):
        if (toks[i][0] == "NOME" and toks[i - 1][1] == "("
                and toks[i - 2][1] in ("existe", "opcional")):
            fora.append(toks[i][1])
    return fora


def entradas_do_contrato(passos: List[dict]) -> Tuple[List[str], List[str]]:
    """(entradas_obrigatorias, entradas_opcionais) que o contrato ESPERA receber: todo nome usado
    numa expressão que nenhum passo anterior produziu. Nome só dentro de existe()/opcional() é
    opcional. É o que a tela/contexto tem de fornecer — e o que o servidor confere antes de rodar."""
    obrig: List[str] = []
    opc: List[str] = []
    produzidos: set = set()

    def _varre(lista, dentro_de_ramo: bool = False):
        # Nome usado SO dentro de um ramo condicional (ou de um laco) nao e obrigatorio: o
        # ramo pode nao acontecer. Medido no BioByte em 14/09/2026 — a classificacao NHSN
        # exigia `classificacao_sobrescrita` e `observacao_medico` mesmo quando NAO havia
        # sobrescrita, e a tarefa recusava antes de comecar.
        for p in lista or []:
            if not isinstance(p, dict):
                continue
            for expr in _expressoes_do_passo(p):
                # Quem diz o que é NOME DE VALOR é o próprio leitor da mini-linguagem. A leitura
                # por palavras soltas contava como valor a palavra da escolha («se», «senao») e o
                # rótulo do argumento («por», «ordem», «desc»), e a tarefa passava a exigir da
                # tela campos com esses nomes. Só se a expressão não for legível é que se cai na
                # varredura antiga, para não perder o que ela pegava.
                try:
                    _, _nomes = compilar_expressao(str(expr))
                except Exception:
                    _nomes = None
                if _nomes is not None:
                    for _n in _nomes:
                        if _n in produzidos or _n in ("verdadeiro", "falso", "nulo"):
                            continue
                        (opc if dentro_de_ramo else obrig).append(_n)
                    for _n in _nomes_perguntados(str(expr)):
                        if _n not in produzidos:
                            opc.append(_n)
                    continue
                try:
                    toks = _tokenizar(re.sub(r"\{\{?\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}?\}", r"\1", str(expr)))
                except Exception:
                    continue
                for i, t in enumerate(toks):
                    if t[0] != "NOME":
                        continue
                    if i + 1 < len(toks) and toks[i + 1][1] == "(":
                        continue                       # chamada de função
                    if i > 0 and toks[i - 1][1] == ".":
                        continue                       # campo de um valor
                    if t[1] in produzidos or t[1] in ("verdadeiro", "falso", "nulo"):
                        continue
                    tolerado = (dentro_de_ramo
                                or (i >= 2 and toks[i - 1][1] == "("
                                    and toks[i - 2][1] in ("existe", "opcional")))
                    (opc if tolerado else obrig).append(t[1])
            for k in ("guarda_em", "atribui", "para_cada", "guarda_id_em"):
                if p.get(k):
                    produzidos.add(str(p[k]))
            # o passo de julgamento produz exatamente os nomes que declara em `devolve`
            for _d in (p.get("devolve") or []):
                if isinstance(_d, str) and _d.strip():
                    produzidos.add(_d.strip())
            for _, destino in (p.get("mapeia") or {}).items():
                produzidos.add(str(destino))
            if isinstance(p.get("passos"), list):
                _ramo = dentro_de_ramo or str(p.get("tipo")) in ("condicao", "laco")
                _varre(p["passos"], _ramo)
            for _chave_ramo in ("senao", "passos_senao"):
                if isinstance(p.get(_chave_ramo), list):
                    _varre(p[_chave_ramo], True)
    _varre(passos)
    obrig_u = sorted(set(obrig))
    opc_u = sorted(set(opc) - set(obrig))
    return obrig_u, opc_u


# ────────────────────────────── validação do contrato ───────────────────────────

def _mensagem_legivel(msg: Any) -> str:
    """A recusa é lida por uma pessoa. O contrato às vezes escreve um código no lugar da frase
    («usuario_invalido»); aqui ele vira uma frase, para a tela não mostrar jargão."""
    t = str(msg or "").strip()
    if not t:
        return "condição não atendida"
    if " " in t or any(c in t for c in ".!?"):
        return t
    palavras = [w for w in re.split(r"[_\-]+", t) if w]
    if not palavras:
        return t
    frase = " ".join(palavras)
    return frase[:1].upper() + frase[1:] + "."


def _erro(n: str, msg: str) -> dict:
    return {"passo": n, "motivo": msg}


def validar_passos(passos: Any, execution: str = "deterministic",
                   ferramentas_resolvidas: Any = None,
                   prefixo: str = "", tarefas_do_sistema: Any = None,
                   saidas_conhecidas: Optional[dict] = None,
                   entradas_disponiveis: Optional[set] = None) -> List[dict]:
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
    if not prefixo:
        # Identificador que um passo lê de `SELECT id FROM <tabela>` e o `retorno` devolve com outro
        # nome (micro_id) não chega às telas seguintes, que esperam <tabela>_id (microbiologia_id).
        _ids_de_tabela: Dict[str, str] = {}
        def _mapear_ids(lista):
            for q in lista or []:
                if not isinstance(q, dict):
                    continue
                if q.get("tipo") == "consulta" and str(q.get("forma", "escalar")) == "escalar" and q.get("guarda_em"):
                    mt = re.match(r"(?is)^\s*select\s+`?(\w+\.)?id`?\s+from\s+`?(\w+)`?", str(q.get("sql") or ""))
                    if mt:
                        _ids_de_tabela[str(q["guarda_em"])] = mt.group(2).lower()
                if isinstance(q.get("passos"), list):
                    _mapear_ids(q["passos"])
        _mapear_ids(passos)
        for idx_r, q in enumerate(passos, 1):
            if isinstance(q, dict) and q.get("tipo") == "retorno":
                for c in (q.get("campos") or []):
                    c_s = str(c).strip()
                    if c_s in _ids_de_tabela:
                        tab = _ids_de_tabela[c_s]; sing = tab[:-1] if tab.endswith("s") else tab
                        if c_s not in (f"{tab}_id", f"{sing}_id"):
                            problemas.append(_erro(str(idx_r), f"«{c_s}» é o id lido de «{tab}»: devolva-o como "
                                                              f"«{c_s} como {sing}_id» para as telas seguintes herdarem"))
    if not prefixo and entradas_disponiveis is not None:
        # Entrada que ninguém fornece (a tela não tem o campo, o contexto não carrega, nenhum
        # passo produz): em runtime seria "variável não definida" na mão do operador.
        obrig, _opc = entradas_do_contrato(passos)
        fora = [e for e in obrig if e not in entradas_disponiveis]
        if fora:
            problemas.append(_erro("-", f"entrada(s) que nenhuma tela/contexto fornece: {', '.join(fora)} — "
                                        f"ou é um destes nomes: {', '.join(sorted(entradas_disponiveis))}; ou o valor "
                                        "tem de ser PRODUZIDO por um passo antes de ser lido (ex.: `calculo` "
                                        f"que atribui {fora[0]} = 'CRIAR' dentro do ramo em que isso vale)"))
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
            for m_ct in re.finditer(r"contem\(\s*([A-Za-z_]\w*)\s*,\s*'([^']+)'\s*\)", str(expr)):
                var_ct, campo_ct = m_ct.group(1), m_ct.group(2)
                if var_ct in saidas_conhecidas and campo_ct in saidas_conhecidas[var_ct]:
                    problemas.append(_erro(n, f"contem({var_ct}, '{campo_ct}') confere se o TEXTO contém a palavra — "
                                              f"a chave «{campo_ct}» sempre está na resposta, mesmo vazia; para saber se "
                                              f"veio preenchida use «{var_ct}.{campo_ct} != nulo»"))
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
                if "?" in re.sub(r"'[^']*'", "", sql):
                    raise ErroDeRegra("o SQL usa `?` como marcador — o marcador é %s")
                if tipo == "consulta":
                    _filtros = [str(a) for a in (p.get("params") or [])
                                if re.match(r"^(data_|dt_|filtro|periodo|busca|tipo_|status_)\w*$", str(a).strip())]
                    if _filtros:
                        raise ErroDeRegra(f"filtro de consulta lido como obrigatório: {', '.join(_filtros)} — "
                                          f"use opcional({_filtros[0]}) nos params e no SQL "
                                          "\"(%s IS NULL OR coluna >= %s)\" para o filtro poder ficar vazio")
                # Senha em claro: coluna *_hash recebendo a senha sem hash_senha(...)
                _params = [str(a) for a in (p.get("params") or [])]
                for _col, _idx in _colunas_com_marcador(sql):
                    if re.search(r"senha_hash|password_hash|hash_senha", _col.lower()) and _idx < len(_params) \
                            and not re.search(r"hash_senha\(", _params[_idx]) \
                            and re.search(r"senha|password", _params[_idx].lower()):
                        raise ErroDeRegra(f"a coluna «{_col}» receberia a senha em claro — grave "
                                          f"hash_senha({_params[_idx]})")
                if tipo == "consulta":
                    if not p.get("guarda_em"):
                        raise ErroDeRegra("`consulta` exige `guarda_em`")
                    if str(p.get("forma", "escalar")) not in ("escalar", "linha", "linhas"):
                        raise ErroDeRegra("`forma` deve ser escalar, linha ou linhas")
            elif tipo == "verificacao":
                if bool(p.get("condicao")) == bool(p.get("recusa_se")):
                    raise ErroDeRegra("`verificacao` tem OU `condicao` (o que precisa valer para seguir) "
                                      "OU `recusa_se` (o que, valendo, recusa) — exatamente um dos dois")
                compilar_expressao(str(p.get("condicao") or p.get("recusa_se")))
                if not p.get("mensagem"):
                    raise ErroDeRegra("`mensagem` de recusa obrigatória (use a frase do caso de uso)")
                # Polaridade: `condicao` é o que PRECISA ser verdade para seguir. Condição que descreve
                # o PROBLEMA ("nao existe(x)", "x == nulo ou y == nulo", "vazio(l)") com mensagem de
                # falta/erro recusa justamente quando está tudo certo — é `recusa_se`.
                if p.get("condicao"):
                    cond_l = str(p["condicao"]).strip().lower()
                    msg_l = str(p["mensagem"]).lower()
                    descreve_problema = bool(re.match(r"^(nao|não)\s+existe\(", cond_l) or cond_l.startswith("vazio(")
                                             or re.search(r"==\s*nulo", cond_l))
                    msg_de_falta = bool(re.search(r"n[aã]o[_ ](encontrad|exist|localizad)|inexist|nao_encontrad|"
                                                  r"missing|falt|ausent|obrigat|inv[aá]lid|vazi", msg_l))
                    if descreve_problema and msg_de_falta:
                        raise ErroDeRegra("verificação invertida: `condicao` é o que precisa ser VERDADE para "
                                          "continuar; se a expressão descreve o PROBLEMA, use `recusa_se` no "
                                          "lugar de `condicao`")
            elif tipo == "calculo":
                if not re.match(r"^[A-Za-z_]\w*$", str(p.get("atribui") or "")):
                    raise ErroDeRegra("`atribui` deve ser um nome de variável")
                compilar_expressao(str(p.get("expressao") or ""))
                # Resultado clínico/numérico NÃO pode ser constante ("ex.: -35" da especificação
                # virando cálculo): ou se calcula de dados, ou é julgamento → passo `agente`.
                _expr_l = str(p.get("expressao") or "").strip()
                if re.match(r"^-?\d+(\.\d+)?$", _expr_l) or re.match(r"^'\[.*\]'$", _expr_l):
                    if re.search(r"reducao|redução|risco|escore|score|estimativa|intervalo|probabilidade|"
                                 r"percent|taxa|media|média|valor_", str(p["atribui"]).lower()):
                        raise ErroDeRegra(f"«{p['atribui']}» = {_expr_l} é valor FIXO — resultado não pode ser "
                                          "constante: calcule a partir dos dados ou, se é julgamento, use passo "
                                          "`agente` (a tarefa deve ser `execution: agent`)")
                # Segredo não se fabrica com texto: token/JWT/OTP vem de ferramenta real.
                if re.search(r"token|jwt|segredo|secret|otp|api_key", str(p["atribui"]).lower()) and \
                        re.search(r"\+|texto\(|maiusculas\(|minusculas\(|'", str(p.get("expressao") or "")):
                    raise ErroDeRegra(f"«{p['atribui']}» não pode ser montado com texto — token/segredo vem "
                                      "de ferramenta real (jwt_tool: sub, role, exp_horas → token_jwt)")
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
                for c in campos:
                    if not re.match(r"^[A-Za-z_]\w*(\.[A-Za-z_]\w*)?(\s+como\s+[A-Za-z_]\w*)?$", str(c)):
                        raise ErroDeRegra(f"campo de retorno «{c}» deve ser `nome`, `nome.campo` ou "
                                          "`nome.campo como apelido`")
                    if re.match(r"^[A-Za-z_]\w*\.id$", str(c).strip()):
                        _base = str(c).split(".")[0]
                        raise ErroDeRegra(f"«{c}» devolvido sem nome de contexto — escreva "
                                          f"«{c} como {_base}_id» para as telas seguintes herdarem")
            elif tipo == "agente":
                # REGRA 3 (programa busca -> modelo julga -> programa grava): o passo de julgamento
                # deixou de ser "o resto que o modelo se vira" e passou a ser um passo com contrato
                # como qualquer outro. Ele declara O QUE ENTREGA ao modelo (`usa`) e O QUE ESPERA
                # DE VOLTA (`devolve`). Sem `devolve`, o programa não teria o que gravar e a
                # resposta do modelo se perderia — por isso é obrigatório.
                if execution != "agent":
                    raise ErroDeRegra("passo de agente em tarefa determinística — declare a regra "
                                      "ou marque a tarefa como `execution: agent`")
                instr = str(p.get("instrucao") or p.get("instrução") or "").strip()
                if instr.startswith("[NÃO VALIDADO"):
                    # marcador posto pela etapa de estruturação: repete o motivo REAL em vez de
                    # cobrar `devolve` de um passo que nunca foi um julgamento de verdade
                    _mot = instr[1:instr.find("]")] if "]" in instr else "passo não validado"
                    raise ErroDeRegra(_mot)
                if not instr:
                    raise ErroDeRegra("`instrucao` obrigatória — diga ao modelo, em uma frase, "
                                      "qual julgamento ele deve fazer")
                if len(instr) < 12:
                    raise ErroDeRegra(f"`instrucao` «{instr}» é curta demais para ser um julgamento")
                devolve = p.get("devolve") or []
                if not isinstance(devolve, list) or not devolve:
                    raise ErroDeRegra("`devolve` obrigatório — liste os nomes dos valores que o "
                                      "modelo deve responder (ex.: [bundle_nome, justificativa]); "
                                      "sem isso o programa não tem o que gravar")
                for d in devolve:
                    if not re.match(r"^[A-Za-z_]\w*$", str(d).strip()):
                        raise ErroDeRegra(f"«{d}» não serve como nome de valor devolvido — "
                                          "use uma palavra só, sem espaço nem ponto")
                usa = p.get("usa") or []
                if not isinstance(usa, list):
                    raise ErroDeRegra("`usa` deve ser uma lista dos valores entregues ao modelo")
                for u in usa:
                    compilar_expressao(str(u))
                # Ferramenta em passo de julgamento: NÃO. Acionar sistema externo é passo `externo`,
                # executado pelo programa. Se dependesse do modelo pedir, funcionaria num provedor
                # e falharia em silêncio noutro.
                if p.get("ferramenta"):
                    raise ErroDeRegra(f"passo de julgamento não aciona a ferramenta «{p['ferramenta']}» — "
                                      "ponha um passo `externo` ANTES dele e entregue o resultado "
                                      "pelo `usa`; quem aciona sistema externo é o programa")
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
    # `retorno`/expressões que leem `resultado.X` onde X é o NOME DE VARIÁVEL dado por `mapeia`
    # (path -> arquivo_gerado lido como resultado.arquivo_gerado): a evidência está no próprio
    # contrato — passa a ler a variável mapeada.
    mapeados: Dict[str, Dict[str, str]] = {}
    def _colher(lista):
        for q in lista or []:
            if isinstance(q, dict):
                if q.get("tipo") in ("externo", "tarefa") and q.get("guarda_em") and isinstance(q.get("mapeia"), dict):
                    mapeados.setdefault(str(q["guarda_em"]), {}).update({str(a): str(b) for a, b in q["mapeia"].items()})
                if isinstance(q.get("passos"), list):
                    _colher(q["passos"])
    _colher(saida)
    if mapeados:
        def _troca(expr: str, n: str) -> str:
            def _sub(m):
                var, campo = m.group(1), m.group(2)
                mp = mapeados.get(var) or {}
                if campo in mp.values():                 # lê pelo nome da variável mapeada
                    reparos.append(f"passo {n}: «{var}.{campo}» é a variável «{campo}» (mapeada de «{var}»)")
                    return campo
                if campo in mp:                          # lê o campo da ferramenta já mapeado
                    reparos.append(f"passo {n}: «{var}.{campo}» já está mapeado para «{mp[campo]}»")
                    return mp[campo]
                return m.group(0)
            return re.sub(r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\b", _sub, expr)
        for idx, p in enumerate(saida, 1):
            if isinstance(p, dict) and p.get("tipo") == "retorno":
                p["campos"] = [_troca(str(c), f"{prefixo}{idx}") if isinstance(c, str) else c for c in (p.get("campos") or [])]
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


def _colunas_com_marcador(sql: str) -> List[Tuple[str, int]]:
    """(coluna, índice do %s que a alimenta) em INSERT ... (cols) VALUES (...) e UPDATE ... SET col=%s."""
    saida: List[Tuple[str, int]] = []
    m = re.search(r"(?is)insert\s+into\s+`?\w+`?\s*\(([^)]*)\)\s*values\s*\((.*)\)", sql)
    if m:
        cols = [c.strip().strip("`") for c in m.group(1).split(",")]
        vals = [v.strip() for v in _split_nivel0(m.group(2))]
        k = 0
        for col, val in zip(cols, vals):
            if val == "%s":
                saida.append((col, k))
            k += val.count("%s")
        return saida
    m = re.search(r"(?is)update\s+`?\w+`?\s+set\s+(.*?)(\s+where\b|$)", sql)
    if m:
        k = 0
        for par in _split_nivel0(m.group(1)):
            mm = re.match(r"\s*`?(\w+)`?\s*=\s*(.*)$", par, re.S)
            if mm:
                if mm.group(2).strip() == "%s":
                    saida.append((mm.group(1), k))
                k += mm.group(2).count("%s")
    return saida


def _split_nivel0(texto: str) -> List[str]:
    partes, nivel, atual = [], 0, ""
    for ch in texto:
        if ch == "(":
            nivel += 1
        elif ch == ")":
            nivel -= 1
        if ch == "," and nivel == 0:
            partes.append(atual); atual = ""
        else:
            atual += ch
    if atual.strip():
        partes.append(atual)
    return partes


def _params_py(params: List[Any]) -> str:
    # cada parâmetro passa por _rt_sql: objeto/lista vira JSON (coluna JSON), booleano vira 0/1
    return "[" + ", ".join(f"_rt_sql({compilar_expressao(str(a))[0]})" for a in (params or [])) + "]"


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


def _TAREFA_ATUAL() -> str:
    """Nome da tarefa sendo traduzida (só para a mensagem de erro em runtime)."""
    try:
        import agents.langnetagents as _la
        return str(getattr(_la, "_TASK_EM_TRADUCAO", "") or "")
    except Exception:
        return ""


def emitir_passos(passos: List[dict], indent: str = "        ",
                  prefixo: str = "", ferramentas_resolvidas: Any = None,
                  tarefas_do_sistema: Any = None,
                  com_transacao: bool = True) -> Tuple[List[str], List[dict]]:
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
                # Coluna que o passo nao tem valor para preencher: NAO escrever vazio explicito.
                # O banco recusa vazio em coluna obrigatoria mesmo quando ela TEM valor padrao (o
                # padrao so vale quando a coluna e omitida). Medido em 14/09/2026: o servico externo
                # de Cox nao devolve intervalo de confianca, a tarefa escrevia vazio e a gravacao
                # inteira falhava com "Column 'intervalo_confianca' cannot be null".
                # O numero do passo pode ser "7.2" — e isso NAO e nome de variavel valido em
                # Python. Troca o que nao for letra ou digito por sublinhado.
                _n_var = re.sub(r"[^0-9A-Za-z]", "_", str(n))
                linhas.append(f"{indent}_sql_{_n_var}, _par_{_n_var} = _sem_colunas_vazias("
                              f"{p['sql']!r}, {_params_py(p.get('params') or [])})")
                linhas.append(f"{indent}cur.execute(_sql_{_n_var}, _par_{_n_var})")
                if p.get("guarda_id_em"):
                    linhas.append(f"{indent}_ctx[{p['guarda_id_em']!r}] = cur.lastrowid or _ctx.get({p['guarda_id_em']!r})")
            elif tipo == "verificacao":
                if p.get("recusa_se"):
                    cond, _ = compilar_expressao(str(p["recusa_se"]))
                    teste = f"if {cond}:"
                else:
                    cond, _ = compilar_expressao(str(p["condicao"]))
                    teste = f"if not {cond}:"
                msg = _mensagem_legivel(p.get("mensagem"))
                linhas.append(f"{indent}# passo {n}: verificação")
                linhas.append(f"{indent}{teste}")
                if com_transacao:
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
                                           tarefas_do_sistema=tarefas_do_sistema,
                                           com_transacao=com_transacao)
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
                                           tarefas_do_sistema=tarefas_do_sistema,
                                           com_transacao=com_transacao)
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
                # `resposta.escore_cox` devolve a chave `escore_cox` com o valor do campo — antes
                # a chave saía com o ponto e o valor era None (a tela não achava o campo)
                partes_ret = []
                for c in p["campos"]:
                    c = str(c)
                    apelido = None
                    if re.search(r"\s+como\s+", c):
                        c, apelido = re.split(r"\s+como\s+", c, maxsplit=1)
                    if "." in c:
                        expr_c, _ = compilar_expressao(c)
                        partes_ret.append(f"{(apelido or c.split('.')[-1])!r}: {expr_c}")
                    else:
                        partes_ret.append(f"{(apelido or c.strip())!r}: _ctx.get({c.strip()!r})")
                campos = ", ".join(partes_ret)
                linhas.append(f"{indent}# passo {n}: retorno")
                linhas.append(f"{indent}_result = {{'status': 'sucesso', {campos}}}")
            elif tipo == "agente":
                # REGRA 3: o julgamento é UM PASSO da receita, não a receita inteira. O programa
                # entrega os valores de `usa` já apurados, pede exatamente os nomes de `devolve`,
                # e grava a resposta no contexto para os passos seguintes usarem. O modelo não
                # consulta banco, não aciona ferramenta e não decide o que fazer depois.
                instr = str(p.get("instrucao") or p.get("instrução") or "")
                devolve = [str(d).strip() for d in (p.get("devolve") or [])]
                usa = [str(u) for u in (p.get("usa") or [])]
                if not instr.strip() or not devolve:
                    raise ErroDeRegra("passo de julgamento sem `instrucao` ou sem `devolve`")
                partes_usa = []
                for u in usa:
                    expr_u, _ = compilar_expressao(u)
                    rotulo = u.strip()
                    partes_usa.append(f"{rotulo!r}: {expr_u}")
                dados = "{" + ", ".join(partes_usa) + "}"
                linhas.append(f"{indent}# passo {n}: julgamento do modelo -> {', '.join(devolve)}")
                linhas.append(f"{indent}_ctx.update(_rt_consultar_modelo({instr!r}, {dados}, "
                              f"{devolve!r}, {_TAREFA_ATUAL()!r}, {n!r}))")
            else:
                raise ErroDeRegra(f"tipo «{tipo}» desconhecido")
            manifesto.append({"passo": n, "tipo": tipo, "emitido": True, "motivo": ""})
        except (ErroDeRegra, KeyError) as e:
            motivo = str(e) if isinstance(e, ErroDeRegra) else f"campo obrigatório ausente: {e}"
            manifesto.append({"passo": n, "tipo": tipo, "emitido": False, "motivo": motivo})
    return linhas, manifesto


# ────────────────── ferramenta "por regra" (etapa Ferramentas) ──────────────────
# A etapa Ferramentas deixa o usuário dizer que uma capacidade é uma REGRA INTERNA (nem serviço
# externo, nem biblioteca). Até aqui a regra ficava só como frase: o módulo gerado nascia com uma
# recusa e a capacidade seguia pendente para sempre. Agora a regra é declarada no MESMO contrato de
# passos das tarefas — e vira código pelo mesmo tradutor.
#
# Regra é CÁLCULO PURO: recebe os valores que a tarefa já apurou e devolve o resultado. Não lê o
# banco, não aciona sistema externo e não consulta modelo — para isso a TAREFA tem os passos dela.
TIPOS_DE_REGRA = ("calculo", "condicao", "laco", "verificacao", "retorno")

_MOTIVO_FORA_DA_REGRA = {
    "consulta": "ferramenta por regra não lê o banco — ponha um passo `consulta` na TAREFA e "
                "entregue o valor pela entrada da ferramenta",
    "escrita": "ferramenta por regra não grava — quem grava é a TAREFA, depois de receber o resultado",
    "externo": "ferramenta por regra não aciona sistema externo — isso é origem `externa` (etapa MCP)",
    "tarefa": "ferramenta por regra não encadeia tarefa",
    "agente": "ferramenta por regra não consulta o modelo — julgamento é passo `agente` da TAREFA",
}


def _normalizar_tipo_pelo_formato(passos: Any) -> int:
    """Corrige o NOME do passo quando o formato dele já diz o que ele é.

    POR QUE: o passo que guarda o resultado de uma expressão num nome chama-se `calculo` e tem
    dois campos, `atribui` e `expressao`. O modelo às vezes escreve `tipo: atribui` — usando o
    nome do campo como nome do passo — e o contrato inteiro é recusado por causa do rótulo,
    embora o passo esteja completo e correto. Medido no BioByte em 21/09/2026: o leitor de JSON,
    usado por quatro tarefas, ficou pendente por isto e por nada mais.

    A correção é conservadora: só troca o nome quando os campos são EXATAMENTE os do passo certo.
    Passo faltando campo continua sendo recusado — o rótulo não vira desculpa.
    """
    trocados = 0
    if not isinstance(passos, list):
        return 0
    for p in passos:
        if not isinstance(p, dict):
            continue
        tipo = str(p.get("tipo") or "").lower()
        if tipo in ("atribui", "atribuicao", "atribuição", "define", "definicao"):
            if p.get("atribui") and p.get("expressao"):
                p["tipo"] = "calculo"
                trocados += 1
        # passos de dentro de condição e de laço contam igual: o defeito de rótulo aparece lá
        # com a mesma frequência, e recusar o contrato inteiro por causa deles é o mesmo erro.
        for campo in ("passos", "entao", "senao", "corpo", "then", "else"):
            filho = p.get(campo)
            if isinstance(filho, list):
                trocados += _normalizar_tipo_pelo_formato(filho)
    return trocados


def validar_regra(passos: Any, entrada: Any = None) -> List[dict]:
    """Confere o contrato de uma ferramenta por regra. Devolve a lista de problemas (vazia = ok)."""
    problemas: List[dict] = []
    _normalizar_tipo_pelo_formato(passos)
    if not isinstance(passos, list) or not passos:
        return [_erro("-", "a regra precisa de `passos` — descreva o cálculo em passos, "
                           "como no contrato das tarefas")]
    for idx, p in enumerate(passos, 1):
        tipo = str((p or {}).get("tipo") or "").lower() if isinstance(p, dict) else ""
        if tipo in _MOTIVO_FORA_DA_REGRA:
            problemas.append(_erro(str(idx), _MOTIVO_FORA_DA_REGRA[tipo]))
        elif tipo not in TIPOS_DE_REGRA:
            problemas.append(_erro(str(idx), f"tipo «{tipo or '?'}» não vale numa regra; "
                                             f"use um de: {', '.join(TIPOS_DE_REGRA)}"))
    if not any(isinstance(p, dict) and str(p.get("tipo")) == "retorno" for p in passos):
        problemas.append(_erro("-", "falta o passo `retorno` dizendo quais valores a ferramenta devolve"))
    problemas += validar_passos(passos, execution="deterministic")
    # entradas que ninguém fornece: a ferramenta declara os parâmetros que recebe
    if entrada is not None:
        disp = {str(e).strip() for e in (entrada or []) if str(e).strip()}
        obrig, _opc = entradas_do_contrato(passos)
        fora = [e for e in obrig if e not in disp]
        if fora:
            problemas.append(_erro("-", f"a regra lê {', '.join(fora)}, que não está na `entrada` da "
                                        f"ferramenta ({', '.join(sorted(disp)) or 'vazia'}) nem é "
                                        "produzido por passo anterior"))
    # remove duplicatas mantendo a ordem
    vistos, unicos = set(), []
    for pr in problemas:
        ch = (pr["passo"], pr["motivo"])
        if ch not in vistos:
            vistos.add(ch); unicos.append(pr)
    return unicos


def emitir_regra(nome: str, entrada: Any, passos: List[dict], descricao: str = "",
                 regra_prosa: str = "") -> Tuple[str, dict]:
    """Função Python da ferramenta por regra + manifesto. Passo que não vira código faz a
    ferramenta RECUSAR na chamada, dizendo qual passo faltou — nunca devolve valor inventado."""
    params = [str(e).strip() for e in (entrada or []) if str(e).strip().isidentifier()]
    corpo, manifesto = emitir_passos(passos, indent="        ", com_transacao=False)
    faltando = [m for m in manifesto if not m["emitido"]]
    assinatura = ", ".join(f"{e}=None" for e in params) if params else "**entradas"
    semente = ("{" + ", ".join(f"{e!r}: {e}" for e in params) + "}") if params else "dict(entradas)"
    recusa = ""
    if faltando:
        det = "; ".join(f"passo {m['passo']} ({m['tipo']}): {m['motivo']}" for m in faltando)
        recusa = (f"    raise _RegraExecucao('ferramenta {nome} incompleta — ' + {det!r})\n")
    doc = [f'    """{descricao or nome}', ""]
    if regra_prosa:
        doc += ["    REGRA (declarada na etapa Ferramentas, aprovada pelo usuário):",
                f"    {regra_prosa}", ""]
    doc += ['    Gerada do contrato de passos da própria ferramenta (tradutor de regras)."""']
    src = (
        f"def {nome}({assinatura}) -> Dict[str, Any]:\n"
        + "\n".join(doc) + "\n"
        + recusa
        + f"    _ctx = {semente}\n"
        "    def _v(_n):\n"
        "        if _n in _ctx:\n"
        "            return _ctx[_n]\n"
        "        raise _RegraExecucao(f'valor «{_n}» não informado à ferramenta')\n"
        "    def _rt_existe_nome(_n):\n"
        "        return _ctx.get(_n) not in (None, '', [], {})\n"
        "    def _rt_opcional_nome(_n):\n"
        "        _x = _ctx.get(_n)\n"
        "        return None if _x in ('', [], {}) else _x\n"
        "    _result = None\n"
        "    try:\n"
        + "\n".join(corpo) + "\n"
        "        return _result if _result is not None else {'status': 'sucesso'}\n"
        "    except _RegraExecucao as _e:\n"
        "        return {'status': 'erro', 'error': str(_e)}\n"
    )
    _obrig, _opc = entradas_do_contrato(passos)
    return src, {"ferramenta": nome, "declarados": len(manifesto),
                 "emitidos": sum(1 for m in manifesto if m["emitido"]),
                 "nao_emitidos": faltando, "entradas": _obrig, "passos": manifesto}


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
        "    def _rt_opcional_nome(nome):\n"
        "        v = _ctx.get(nome)\n"
        "        return None if v in ('', [], {}) else v\n"
        "    _result = None\n"
        "    try:\n"
        "        cur = conn.cursor(dictionary=True)\n"
        + "\n".join(corpo) + "\n"
        "        conn.commit()\n"
        "        return _result if _result is not None else {'status': 'sucesso'}\n"
        "    except _RegraExecucao as _e:\n"
        "        if getattr(_e, 'sistema_externo', None):\n"
        "            conn.rollback()\n"
        "            return {'status': 'erro', 'error': str(_e), 'sistema_externo': _e.sistema_externo}\n"
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
    _obrig, _opc = entradas_do_contrato(passos)
    return src, {"tarefa": nome, "declarados": len(manifesto), "entradas": _obrig, "entradas_opcionais": _opc,
                 "emitidos": sum(1 for m in manifesto if m["emitido"]),
                 "nao_emitidos": faltando, "passos": manifesto}


# ─────────────────────── runtime emitido junto com o adapters ───────────────────

RUNTIME_PY = r'''
# ── Runtime do tradutor de regras (auto-gerado; usado pelas funções do contrato `steps:`) ──
import json as _rt_json, hashlib as _rt_hashlib, datetime as _rt_dt

class _RegraExecucao(Exception):
    """Falha de regra em tempo de execução, com mensagem legível."""
def _sem_colunas_vazias(sql, params):
    """Tira do INSERT as colunas cujo valor nao existe, para o PADRAO da coluna valer.

    O banco so aplica o valor padrao quando a coluna e OMITIDA. Escrever vazio explicito numa
    coluna obrigatoria e recusado, mesmo que ela tenha padrao — e a gravacao inteira falha.

    A lista de valores costuma trazer funcoes com parenteses (UUID(), NOW()), entao a leitura e
    feita contando a profundidade dos parenteses, e nao por um padrao simples — foi assim que a
    primeira versao desta rotina deixou passar justamente o INSERT do escore de risco.
    """
    import re as _re
    if not params or not isinstance(params, (list, tuple)):
        return sql, params
    texto = (sql or "").strip().rstrip(";")
    m = _re.match(r"(?is)^INSERT\s+(?:IGNORE\s+)?INTO\s+([`\"\w.]+)\s*\(", texto)
    if not m:
        return sql, params

    def _ate_fechar(t, i):
        """Devolve (conteudo, indice depois do fecha) a partir do '(' em i."""
        prof, j = 0, i
        while j < len(t):
            if t[j] == "(":
                prof += 1
            elif t[j] == ")":
                prof -= 1
                if prof == 0:
                    return t[i + 1:j], j + 1
            j += 1
        return None, len(t)

    cols_txt, pos = _ate_fechar(texto, m.end() - 1)
    if cols_txt is None:
        return sql, params
    m2 = _re.match(r"(?is)\s*VALUES\s*\(", texto[pos:])
    if not m2:
        return sql, params
    vals_txt, pos2 = _ate_fechar(texto, pos + m2.end() - 1)
    if vals_txt is None or texto[pos2:].strip():
        return sql, params      # tem mais coisa depois (ON DUPLICATE, etc.): nao mexe

    def _fatiar(t):
        """Divide por virgula, respeitando parenteses."""
        partes, atual, prof = [], "", 0
        for ch in t:
            if ch == "(":
                prof += 1
            elif ch == ")":
                prof -= 1
            if ch == "," and prof == 0:
                partes.append(atual.strip()); atual = ""
            else:
                atual += ch
        if atual.strip():
            partes.append(atual.strip())
        return partes

    colunas, marcas = _fatiar(cols_txt), _fatiar(vals_txt)
    if len(colunas) != len(marcas) or marcas.count("%s") != len(params):
        return sql, params
    guardar, novos, i = [], [], 0
    for col, marca in zip(colunas, marcas):
        if marca != "%s":
            guardar.append((col, marca)); continue
        valor = params[i]; i += 1
        if valor is None:
            continue            # omite a coluna: o padrao dela entra
        guardar.append((col, marca)); novos.append(valor)
    if len(novos) == len(params) or not guardar:
        return sql, params
    novo_sql = (f"INSERT INTO {m.group(1)} (" + ", ".join(c for c, _ in guardar)
                + ") VALUES (" + ", ".join(v for _, v in guardar) + ")")
    return novo_sql, novos



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
def _rt_ordenar(lista, por=None, ordem="asc"):
    """Ordena a lista pelo campo indicado. Sem campo, ordena pelos próprios valores. `ordem=desc`
    inverte. Item sem o campo vai para o fim, e não derruba a ordenação."""
    l = list(_rt_lista(lista))
    desc = str(ordem or "asc").lower().startswith("desc")
    def _chave(x):
        v = _rt_campo(x, por) if por else x
        if v is None:
            return (1, 0)
        try:
            return (0, float(v))
        except Exception:
            return (0, str(v))
    try:
        return sorted(l, key=_chave, reverse=desc)
    except TypeError:
        return sorted(l, key=lambda x: str(_chave(x)), reverse=desc)
def _rt_json_valido(texto):
    """Verdadeiro se o texto é um JSON legível. Objeto/lista já prontos contam como válidos."""
    if isinstance(texto, (dict, list)):
        return True
    try:
        _rt_json.loads(str(texto or ""))
        return True
    except Exception:
        return False


def _rt_de_json(texto):
    """Texto JSON -> objeto. Texto inválido RECUSA com mensagem legível (nunca devolve meia-leitura)."""
    if isinstance(texto, (dict, list)):
        return texto
    try:
        return _rt_json.loads(str(texto or ""))
    except Exception as e:
        raise _RegraExecucao(f"conteúdo recebido não é um JSON válido: {e}")


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
    try:
        saida = fn(**argumentos) if argumentos else fn()
    except Exception as e:
        # sistema externo fora / tempo limite / erro da ferramenta: falha explícita, marcada
        exc = _RegraExecucao(f"sistema externo «{nome}» falhou: {e}")
        exc.sistema_externo = nome
        raise exc
    if isinstance(saida, str):
        try: saida = _rt_json.loads(saida)
        except Exception: return {"texto": saida}
    if isinstance(saida, dict) and saida.get("mcp_error"):
        exc = _RegraExecucao(f"sistema externo «{nome}» falhou: {saida['mcp_error']}")
        exc.sistema_externo = nome
        raise exc
    return saida

def _rt_consultar_modelo(instrucao, dados, devolve, tarefa="", passo=""):
    """REGRA 3 — o programa consulta o modelo NUM PASSO, com os dados já apurados na mão.

    Por que assim e não deixando o modelo se virar: o modelo não tem acesso ao banco nem aos
    sistemas externos, e nem todo provedor sabe pedir o acionamento de uma ferramenta (a nossa
    ponte para o Claude, por exemplo, não transporta esse pedido). Então quem busca é o programa,
    quem julga é o modelo, e quem grava é o programa. O mesmo comportamento em qualquer provedor.

    Devolve um dicionário com EXATAMENTE os nomes de `devolve`. Se o modelo não responder algum
    deles, levanta erro: a tarefa recusa em vez de gravar um julgamento pela metade.
    """
    import os as _o
    _prov = (_o.getenv("LLM_PROVIDER") or "deepseek").lower()
    if _prov == "lmstudio":
        _base = _o.getenv("LMSTUDIO_API_BASE", "http://localhost:1234/v1")
        _model = _o.getenv("LMSTUDIO_MODEL_NAME", "qwen2.5-coder-32b-instruct")
        _key = _o.getenv("LMSTUDIO_API_KEY", "lm-studio")
        _max = int(_o.getenv("LMSTUDIO_MAX_TOKENS", "8000"))
    elif _prov == "claude_code":
        _base = _o.getenv("CLAUDE_CODE_API_BASE", "https://192.168.1.100:4443/v1").rstrip("/")
        if not _base.endswith("/v1"):
            _base += "/v1"
        _model = _o.getenv("CLAUDE_CODE_MODEL_NAME", "claude-code")
        _key = _o.getenv("CLAUDE_CODE_API_KEY", "")
        _max = int(_o.getenv("CLAUDE_CODE_MAX_TOKENS", "8000"))
    elif _prov == "openai":
        _base = _o.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        _model = _o.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        _key = _o.getenv("OPENAI_API_KEY", "")
        _max = int(_o.getenv("OPENAI_MAX_TOKENS", "8000"))
    else:
        _base = _o.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        if not _base.rstrip("/").endswith("/v1"):
            _base = _base.rstrip("/") + "/v1"
        _model = _o.getenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash").split("/")[-1]
        _key = _o.getenv("DEEPSEEK_API_KEY", "")
        _max = int(_o.getenv("DEEPSEEK_MAX_TOKENS", "8000"))
    if not _key:
        raise _RegraExecucao(f"julgamento do passo {passo} não pôde ser feito: falta a chave do "
                             f"modelo ({_prov}) no ambiente do aplicativo")
    _campos = ", ".join(devolve)
    _prompt = (
        instrucao.strip() + "\n\n"
        "DADOS APURADOS PELO SISTEMA (use SOMENTE estes; não invente, não peça mais nada):\n"
        + _rt_json.dumps(dados, ensure_ascii=False, indent=2, default=str) + "\n\n"
        "Responda SOMENTE um objeto JSON, sem texto antes ou depois, com exatamente estas chaves: "
        + _campos + "\n"
        "Se os dados não permitirem concluir, responda o JSON com a chave "
        '"impossivel" explicando em uma frase.'
    )
    try:
        from openai import OpenAI as _OpenAI
        _cli_kw = {"api_key": _key or "sem-chave", "base_url": _base,
                   "timeout": float(_o.getenv("JULGAMENTO_TIMEOUT", "180")), "max_retries": 1}
        if _prov == "claude_code":
            import httpx as _hx, re as _re
            _h = _re.sub(r"^https?://", "", _base).split("/")[0].split(":")[0]
            _ip = bool(_re.match(r"^\d{1,3}(\.\d{1,3}){3}$", _h))
            _cli_kw["http_client"] = _hx.Client(verify=not _ip,
                                                timeout=float(_o.getenv("JULGAMENTO_TIMEOUT", "180")))
        _cli = _OpenAI(**_cli_kw)
        _extra = {"thinking": {"type": "disabled"}} if _prov == "deepseek" else {}
        _r = _cli.chat.completions.create(
            model=_model,
            messages=[{"role": "system", "content":
                       "Você julga com base APENAS nos dados recebidos e responde só JSON."},
                      {"role": "user", "content": _prompt}],
            max_tokens=_max, stream=False, **({"extra_body": _extra} if _extra else {}))
        _txt = (_r.choices[0].message.content or "") if _r.choices else ""
    except Exception as _e:
        raise _RegraExecucao(f"julgamento do passo {passo} falhou ao consultar o modelo: {_e}")
    _t = _txt.strip()
    if _t.startswith("```"):
        _t = _t.split("\n", 1)[-1]
        if _t.rstrip().endswith("```"):
            _t = _t.rstrip()[:-3]
    _i = _t.find("{")
    if _i < 0:
        raise _RegraExecucao(f"julgamento do passo {passo}: o modelo respondeu texto em vez de JSON")
    try:
        _obj, _ = _rt_json.JSONDecoder().raw_decode(_t[_i:])
    except Exception:
        raise _RegraExecucao(f"julgamento do passo {passo}: resposta do modelo ilegível")
    if not isinstance(_obj, dict):
        raise _RegraExecucao(f"julgamento do passo {passo}: resposta do modelo não é um objeto")
    if _obj.get("impossivel"):
        raise _RegraExecucao(f"não foi possível concluir: {_obj['impossivel']}")
    _faltam = [c for c in devolve if _obj.get(c) in (None, "")]
    if _faltam:
        raise _RegraExecucao(f"julgamento do passo {passo} incompleto — o modelo não respondeu: "
                             + ", ".join(_faltam))
    return {c: _obj[c] for c in devolve}


def _rt_sql(v):
    """Valor de parâmetro SQL: dict/list (ex.: antibiograma do laboratório) vira texto JSON para a
    coluna JSON; booleano vira 0/1; o resto passa como está."""
    if isinstance(v, bool): return 1 if v else 0
    if isinstance(v, (dict, list)): return _rt_json.dumps(v, ensure_ascii=False, default=str)
    return v

def _rt_hash_senha(senha):
    """Hash da senha para gravar (SHA-256, o formato que confere_senha reconhece). Senha nunca em claro."""
    return _rt_hashlib.sha256(str(senha or "").encode("utf-8")).hexdigest()

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
