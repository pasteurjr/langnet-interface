"""
Prompt: Caso de Uso (fluxos) → Grafo de Causa-Efeito (CEG).

Extrai, de UM caso de uso, o grafo causa-efeito no formato do motor determinístico
(agents/ceg_engine.py), seguindo o método do artigo do Pasteur Ottoni:
  - CAUSAS = ações do ator / condições de entrada (do fluxo principal + condições
    que disparam fluxos alternativos e de exceção)
  - EFEITOS = respostas do sistema
  - Ligações por portas ~ (não), ^ (e), v (ou)
  - Restrições intercausas S/E/C/M
  - Regra crítica do artigo: NÃO identificar causas complementares (ex.: "campos
    preenchidos" e "campos não preenchidos" — a segunda é a negação da primeira).
"""

_CEG_INSTRUCTIONS = """Você é engenheiro de testes especialista na técnica do GRAFO DE CAUSA-EFEITO
(cause-effect graphing) para derivar casos de teste a partir de casos de uso.

Dado UM caso de uso (com fluxo principal, fluxos alternativos e exceções), produza
o grafo causa-efeito como JSON.

DEFINIÇÕES (siga à risca):
- CAUSAS = condições de ENTRADA do sistema, tipicamente as AÇÕES DO ATOR e as
  condições que fazem o fluxo divergir (dos fluxos alternativos/exceção).
  Cada causa é uma condição booleana (verdadeira/falsa).
- EFEITOS = as RESPOSTAS DO SISTEMA (saídas). Cada efeito é uma condição de saída.
- REGRA CRÍTICA: NUNCA crie causas complementares. Se existe a causa
  "campos obrigatórios preenchidos", NÃO crie "campos não preenchidos" — esta é a
  negação (~) da primeira e será obtida no grafo, não como causa separada.
- Para cada efeito, escreva a EXPRESSÃO booleana das causas que o ATIVAM, usando
  os operadores and/or/not.
- RESTRIÇÕES intercausas (quando aplicável):
    "E" = mutuamente exclusivas (no máx. uma verdadeira; ex.: escolher opção A ou B)
    "O" = uma e só uma verdadeira
    "S" = simultâneas (têm o mesmo valor)
    "C" = consequentes (se a 1ª é verdadeira, as demais também; ex.: precisa estar
          autenticado para qualquer ação → autenticação é consequente das demais)

FORMATO DE SAÍDA (JSON, e SOMENTE o JSON):
{{
  "uc": "{uc_id}",
  "causes":  [{{"id":"c1","desc":"ação/condição de entrada"}}, ...],
  "effects": [{{"id":"e1","desc":"resposta do sistema"}}, ...],
  "rules":   [{{"effect":"e1","expr": EXPR}}, ...],
  "constraints": [{{"type":"E","causes":["c1","c2"]}}, ...]
}}

EXPR (expressão booleana):
  "cX"                                  -> a causa cX é verdadeira
  {{"op":"not","arg": EXPR}}            -> negação
  {{"op":"and","args":[EXPR, EXPR]}}    -> e
  {{"op":"or","args":[EXPR, EXPR]}}     -> ou

EXEMPLO (compilador de comando — do método clássico):
Especificação: 1º token deve ser MOVTOX ou MOVTOY; 2º token deve ser letra A-Z.
Se ok → comando correto; se 1º token errado → M1; se 2º token não é letra → M2.
{{
  "uc": "EXEMPLO",
  "causes": [
    {{"id":"c1","desc":"primeiro token é MOVTOX"}},
    {{"id":"c2","desc":"primeiro token é MOVTOY"}},
    {{"id":"c3","desc":"segundo token é letra A-Z"}}
  ],
  "effects": [
    {{"id":"e1","desc":"comando correto"}},
    {{"id":"e2","desc":"mensagem M1 - token 1 incorreto"}},
    {{"id":"e3","desc":"mensagem M2 - token 2 incorreto"}}
  ],
  "rules": [
    {{"effect":"e1","expr":{{"op":"and","args":[{{"op":"or","args":["c1","c2"]}},"c3"]}}}},
    {{"effect":"e2","expr":{{"op":"not","arg":{{"op":"or","args":["c1","c2"]}}}}}},
    {{"effect":"e3","expr":{{"op":"not","arg":"c3"}}}}
  ],
  "constraints": [{{"type":"E","causes":["c1","c2"]}}]
}}

## CASO DE USO A ANALISAR
ID: {uc_id}
Nome: {uc_name}
Ator: {actor}
Objetivo: {objetivo}

### Fluxo Principal (Ação do Ator → Resposta do Sistema)
{fluxo_principal}

### Fluxos Alternativos
{fluxos_alt}

### Fluxos de Exceção
{fluxos_exc}

Gere agora o grafo causa-efeito (apenas o JSON):"""


def build_ceg_prompt(uc: dict) -> str:
    return _CEG_INSTRUCTIONS.format(
        uc_id=uc.get("id", "UC"),
        uc_name=uc.get("name", ""),
        actor=uc.get("actor", "—"),
        objetivo=uc.get("objetivo", "—"),
        fluxo_principal=uc.get("fluxo_principal", "(não informado)"),
        fluxos_alt=uc.get("fluxos_alt", "(nenhum)"),
        fluxos_exc=uc.get("fluxos_exc", "(nenhum)"),
    )
