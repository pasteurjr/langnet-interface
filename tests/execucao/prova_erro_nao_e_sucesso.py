"""Resposta com erro NUNCA vira sucesso — no servidor de agentes gerado e no cliente das telas.

Medido no BioByte v5 em 03/10/2026: o banco recusou o cadastro de paciente (vínculo com usuário
inexistente) e de sítio de inserção (valor fora da lista fechada); o servidor respondeu
`task_completed` com `success: true` e o erro dentro, e a tela voltou para a lista sem aviso.
"""
import sys, os, ast, json, asyncio, subprocess, tempfile, textwrap
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import warnings; warnings.filterwarnings("ignore")
import agents.langnetagents as M

falhas = []; casos = 0
def confere(nome, cond):
    global casos; casos += 1
    print(("OK   " if cond else "FALHA"), nome)
    if not cond: falhas.append(nome)

# --- servidor: extrai as duas funções do código que o gerador emite ---
fonte = M._template_websocket_server_py(5099)
arv = ast.parse(fonte)
pegar = {"_erro_de_banco_em_palavras", "_concluir_tarefa"}
trechos = [ast.get_source_segment(fonte, n) for n in arv.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in pegar]
confere("o servidor gerado tem as duas funções", len(trechos) == 2)
enviados = []
ns = {"time": __import__("time"), "datetime": __import__("datetime").datetime,
      "_ETIQUETAS": {}, "_etiqueta": lambda k, v: None,
      "_msg_negocio": lambda t, tipo, tec: tec}
async def _passo(ws, *a, **k): pass
async def _consolidar(ws, t, concluiu): enviados.append(("tags", concluiu))
async def _send(ws, tipo, dados): enviados.append((tipo, dados))
ns.update({"_passo": _passo, "_consolidar_etiquetas": _consolidar, "_send": _send})
exec("\n\n".join(trechos), ns)

erro_fk = {"status": "erro", "error": "1452 (23000): Cannot add or update a child row: a foreign key constraint fails (`app`.`pacientes`, CONSTRAINT `pacientes_ibfk_1` FOREIGN KEY (`medico_responsavel_id`) REFERENCES `usuarios` (`id`))"}
asyncio.run(ns["_concluir_tarefa"](None, "criar_pacientes", erro_fk, 0.0))
tipos = [e[0] for e in enviados]
confere("erro de vínculo sai como 'error', não 'task_completed'", "error" in tipos and "task_completed" not in tipos)
msg = [e[1] for e in enviados if e[0] == "error"][0]
confere("success é False", msg.get("success") is False)
confere("mensagem em português cita o campo", "medico responsavel id" in msg["error"] and "não existe" in msg["error"])
confere("detalhe técnico preservado à parte", "1452" in msg["detalhe_tecnico"])
confere("etiquetas fecham como não concluída", ("tags", False) in enviados)

enviados.clear()
asyncio.run(ns["_concluir_tarefa"](None, "criar_sitios_insercao", {"status": "erro", "error": "1265 (01000): Data truncated for column 'nome' at row 1"}, 0.0))
m2 = [e[1] for e in enviados if e[0] == "error"]
confere("valor fora da lista fechada sai como erro e cita o campo", bool(m2) and "nome" in m2[0]["error"])

enviados.clear()
asyncio.run(ns["_concluir_tarefa"](None, "criar_pacientes", {"status": "sucesso", "id": "x"}, 0.0))
confere("sucesso continua 'task_completed' com success True", any(e[0] == "task_completed" and e[1].get("success") is True for e in enviados))

# --- cliente das telas: roda o runTask gerado com um WebSocket falso ---
cliente = M._template_ws_client(5099).replace("export function", "function").replace("process.env.REACT_APP_WS_URL", "undefined")
js = cliente + textwrap.dedent('''
  ;const cenarios = JSON.parse(process.argv[2]);
  async function roda(resposta) {
    global.WebSocket = class { constructor(){ setTimeout(()=>this.onopen&&this.onopen(),1); }
      send(t){ const m=JSON.parse(t); if(m.type==="execute_task") setTimeout(()=>this.onmessage({data:JSON.stringify(resposta)}),1); }
      close(){} };
    try { const r = await runTask("t", {}); return "resolveu:" + JSON.stringify(r); }
    catch(e) { return "rejeitou:" + e.message; }
  }
  (async()=>{ const out=[]; for (const c of cenarios) out.push(await roda(c)); console.log(JSON.stringify(out)); })();
''')
f = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False); f.write(js); f.close()
cen = [
  {"type": "task_completed", "data": {"success": True, "result": {"status": "erro", "error": "1452 vínculo"}}},
  {"type": "task_completed", "data": {"success": False, "result": {}, "error": "falhou"}},
  {"type": "task_completed", "data": {"success": True, "result": {"status": "sucesso", "id": "1"}}},
  {"type": "error", "data": {"error": "Não foi possível salvar"}},
]
out = json.loads(subprocess.run(["node", f.name, json.dumps(cen)], capture_output=True, text=True, timeout=30).stdout.strip())
confere("cliente: resultado com status erro é rejeitado", out[0].startswith("rejeitou:1452"))
confere("cliente: success False é rejeitado", out[1].startswith("rejeitou:"))
confere("cliente: sucesso resolve", out[2].startswith("resolveu:"))
confere("cliente: mensagem 'error' é rejeitada com o texto", out[3] == "rejeitou:Não foi possível salvar")
os.unlink(f.name)
print(f"\ncasos: {casos} | falharam: {len(falhas)}")
sys.exit(1 if falhas else 0)
