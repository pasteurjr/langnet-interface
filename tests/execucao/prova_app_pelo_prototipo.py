"""Aplicativo = protótipo aprovado + executores do padrão (F4 do plano v1.1).

Trava o que a prova ao vivo de 03/10/2026 mostrou e os defeitos do BioByte v5: tela feita de outro
molde (zero uso do desenho), sem login, senha_hash na resposta, console Admin/Petri no aplicativo,
nome de tela/rota/tarefa inventado no comportamento.
"""
import sys, os, json, re
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import warnings; warnings.filterwarnings("ignore")
from agents.langnetappapi import emitir_backend_main, meta_do_modelo
from agents.langnetapptelas import (corpo_da_tela, componente_jsx, conferir_controlador, montar_regras_py,
                                    app_jsx, index_html, LNX_JS, ARQUIVOS_QUE_SAEM)

falhas = []; casos = 0
def confere(nome, cond):
    global casos; casos += 1
    print(("OK   " if cond else "FALHA"), nome)
    if not cond: falhas.append(nome)

schema = open(os.path.join(os.path.dirname(__file__), "fixture_schema_biobyte_v5.sql")).read()
meta = meta_do_modelo(schema)
confere("acha a tabela de login e a de auditoria", meta["login"] == "usuarios" and meta["auditoria"] == "logs_auditoria")
confere("lê as listas fechadas do modelo", meta["enums"]["usuarios"]["papel"] == ["medico", "enfermeiro", "administrador"])
src = emitir_backend_main(schema, "BioByte", True, {"classify_case_by_nhsn_criterion": {"criterios_candidatos": "banco criterios_nhsn"}})
compile(src, "main", "exec")
confere("backend gerado compila", True)
confere("login com token e rota protegida", "/api/auth/login" in src and "Depends(usuario)" in src and "jwt.encode" in src)
confere("dado sensível nunca sai (filtro em toda resposta)", "def limpo(" in src and "SENSIVEL" in src)
confere("erro do banco vira palavras, nunca sucesso", "HTTPException(422" in src and "aponta para um registro que não existe" in src)
confere("origens das entradas do agente embutidas", '"criterios_candidatos": "banco criterios_nhsn"' in src and "/api/agente/entradas/" in src)

html = ('<!doctype html><html><head><script src="https://cdn.tailwindcss.com"></script></head><body><div class="flex min-h-screen">'
        '<aside>menu do mockup</aside><main><button data-acao="acao-1">Salvar</button>'
        '<script>alert(1)</script></main></div></body></html>')
c = corpo_da_tela(html)
confere("tela do app usa o DESENHO aprovado (sem o menu próprio nem script)", 'data-acao="acao-1"' in c and "<aside" not in c and "alert(1)" not in c)
jsx = componente_jsx("Tela", {"name": "T", "uc": ["UC-001"], "mockup_html": html})
confere("componente põe o desenho e chama o controlador", "dangerouslySetInnerHTML" in jsx and 'from "../controladores/Tela"' in jsx)

tela = {"id": "t1", "actions": [{"id": "acao-1", "label": "Salvar", "executado_por": "pronto"},
                                {"id": "acao-2", "label": "Avaliar", "executado_por": "agente"}]}
bom = ('export default function montar(raiz, lnx) { lnx.acao(raiz, "acao-1", async () => lnx.api.post("/api/dados/usuarios", {}));'
       ' lnx.acao(raiz, "acao-2", async () => lnx.agente("evaluate_multidrug_resistance", {}, null));'
       ' lnx.acao(raiz, "acao-3", async () => lnx.api.post("/api/uc/UC-002/desativar", {})); lnx.navegar("t1"); }')
py = 'def rotas(app, ctx):\n    @app.post("/api/uc/UC-002/desativar")\n    def _x(corpo: dict):\n        return {}\n'
confere("controlador correto é aprovado", conferir_controlador(bom, py, tela, "evaluate_multidrug_resistance", meta["tabelas"], ["t1"]) == [])
ruim = 'export default function montar(raiz, lnx) { fetch("/x"); lnx.api.get("/api/dados/tabela_inventada"); lnx.navegar("tela-inventada"); lnx.api.post("/api/uc/UC-9/nao_existe") }'
p = conferir_controlador(ruim, "", tela, "evaluate_multidrug_resistance", meta["tabelas"], ["t1"])
confere("ação não ligada é acusada", any("acao-1" in x for x in p))
confere("agente sem chamar a tarefa é acusado", any("evaluate_multidrug_resistance" in x for x in p))
confere("rede por fora da biblioteca é acusada", any("por fora" in x for x in p))
confere("cadastro inventado é acusado", any("tabela_inventada" in x for x in p))
confere("tela de destino inventada é acusada", any("tela-inventada" in x for x in p))
confere("rota de regra inexistente é acusada", any("/api/uc/UC-9/nao_existe" in x for x in p))
confere("regra com erro de sintaxe é acusada", any("sintaxe" in x for x in conferir_controlador(bom, "def rotas(app, ctx):\n  x = (", tela, "evaluate_multidrug_resistance", meta["tabelas"], ["t1"])))
r = montar_regras_py({"t1": py, "t2": py})
compile(r, "regras", "exec")
confere("regras de várias telas viram um módulo que compila", "rotas_t1" in r and "rotas_t2" in r and "def instalar" in r)

a = app_jsx([{"comp": "Login", "id": "login", "nome": "Login", "login": True},
             {"comp": "Multi", "id": "m", "nome": "Multirresistência", "agente": True}], "BioByte")
confere("menu marca ✦ a tela com agente; Assistente fixo; sem seção de IA", "✦ Assistente" in a and "t.agente ?" in a and "Agentes de IA" not in a)
confere("sem sessão, só a tela de login", "if (!sessao && login)" in a)
confere("sem console Admin/Petri", "MainExecutor" not in a and "Petri" not in a)
confere("console Admin/Petri sai do pacote", "frontend/src/petri-engine/" in ARQUIVOS_QUE_SAEM and "backend/project.json" in ARQUIVOS_QUE_SAEM)
confere("biblioteca: erro da API vira mensagem, 401 leva ao login", "throw new Error" in LNX_JS and "r.status === 401" in LNX_JS)
confere("index carrega o estilo do desenho", "cdn.tailwindcss.com" in index_html("X", []))

print(f"\n{casos} casos, {len(falhas)} falhas")
sys.exit(1 if falhas else 0)
