#!/usr/bin/env python3
"""Executa os 43 casos de teste (gerados pela etapa Casos de Teste) contra o sistema implantado.

Cada caso é causa→efeito. Classificamos o efeito e verificamos do jeito honesto para cada tipo:
  SISTEMA    — comportamento de dados/regra: dispara a tarefa do caso de uso e confere o resultado
               (e o banco, quando o efeito é "cria registro").
  INTERFACE  — elemento de tela (badge, mensagem, botão): confere se existe no código gerado da tela.
  NÃO IMPL.  — efeito que o sistema não implementa (e-mail/push, timeout simulado, processamento
               assíncrono). Reportado como lacuna, não como aprovação.

uso: python3 run_test_cases.py [ws_port] [frontend_src_dir]
"""
import asyncio, json, re, sys, os
from pathlib import Path

WS_PORT = sys.argv[1] if len(sys.argv) > 1 else "5002"
FE = Path(sys.argv[2]) if len(sys.argv) > 2 else None
if FE is None:
    cands = sorted(Path("/tmp/langnet-runs").glob("*/*/frontend/src"), key=lambda p: p.stat().st_mtime)
    FE = cands[-1] if cands else Path(".")
TCS = json.load(open("/tmp/biobyte_testcases.json", encoding="utf-8"))

UC_TASK = {
    "UC-001": "authenticate_user_mfa", "UC-002": "init_import_session",
    "UC-003": "fetch_and_persist_microbiology", "UC-004": "classify_case_nhsn",
    "UC-005": "detect_mdr_and_alert", "UC-006": "calculate_cox_risk_score",
    "UC-007": "recommend_treatment_bundle", "UC-008": "estimate_risk_reduction",
    "UC-009": "generate_dashboard_metrics", "UC-010": "manage_user_account",
    "UC-011": "query_audit_logs", "UC-012": "export_vigilance_report",
}
# Usuário criado PELO PRÓPRIO APP no início da bateria: os casos positivos de login precisam
# de uma senha cuja conferência tenha como dar certo. O usuário semeado no banco carrega hash
# de um teste antigo, e por isso reprovava o caminho positivo.
USUARIO_TESTE = {"email": "", "senha": "SenhaDeTeste#2026"}

BASE = {  # caso clínico de referência (o mesmo do fluxo encadeado)
    "email": "ana@hospital.br", "senha": "x", "codigo_mfa": "123456", "usuario_id": "U-001",
    "paciente_id": "P-001", "caso_id": "CAS-2023-001", "idade": 72, "dias_cateter": 12,
    "uti": True, "nutricao_parenteral": True, "neutropenia": False,
    "tipo_cateter": "Cateter Central", "apache_ii": 18, "id_amostra": "HMC-88213",
}
# Efeitos que o sistema NÃO implementa (reportados como lacuna, jamais como sucesso).
NAO_IMPL = [
    (r"e-?mail|push notification", "envio de e-mail/push não está ligado a nenhum agente"),
    (r"timeout", "simulação de timeout não é exercitável pela interface do sistema"),
    (r"processamento ass[íi]ncrono", "processamento assíncrono/fila não implementado"),
    (r"skeleton loader", "skeleton loader não implementado nas telas geradas"),
]
# Efeitos de INTERFACE → trecho a procurar no código das telas.
UI_ALVO = [
    (r"badge 'ICSAC Confirmado'|badge 'Não ICSAC'|badge 'Classificação Pendente'", "ICSAC Confirmado"),
    (r"Credenciais inv[áa]lidas", "Credenciais inv"),
    (r"C[óo]digo incorreto", "digo incorreto"),
    (r"Exportar CSV|arquivo CSV", "CSV"),
    (r"spinner", "busy"),
    (r"tela Pr[ée]via de Resultados", "PreviaResultados"),
    (r"tela Sele[çc][ãa]o de Paciente|Paciente n[ãa]o encontrado", "paciente"),
    (r"lista de Casos Ativos", "casos"),
    (r"formul[áa]rio de cadastro de novo caso", "CasosCrud"),
    (r"tela Importa[çc][ãa]o de Microbiologia", "ImportacaoMicrobiologia"),
    (r"cards de KPI|gr[áa]ficos", "kpi"),
    (r"barra de progresso", "progress"),
    (r"banner vermelho", "AlertaMdr"),
    (r"tabela de logs", "LogsAuditoria"),
    (r"Recomenda[çc][ãa]o de Bundle com nome e justificativa", "bundle_nome"),
    (r"Redu[çc][ãa]o de Risco Estimada|Intervalo de Confian", "intervalo_confianca"),
    (r"Dashboard de Vigil[âa]ncia", "DashboardVigilancia"),
    (r"Verifica[çc][ãa]o de Identidade|Redireciona", "codigo_mfa"),
    (r"filtro de per[íi]odo|atualiza cards", "data_inicio"),
    (r"mensagem de erro", "setErr"),
]
FE_SRC = ""
for f in sorted(FE.glob("screens/*.jsx")) + sorted(FE.glob("*.jsx")):
    try: FE_SRC += f.read_text(encoding="utf-8", errors="replace") + "\n" + f.name + "\n"
    except Exception: pass


async def exec_task(nome, entrada, timeout=180):
    import websockets
    async with websockets.connect(f"ws://localhost:{WS_PORT}", max_size=None, open_timeout=10) as ws:
        try: await asyncio.wait_for(ws.recv(), timeout=2)
        except Exception: pass
        await ws.send(json.dumps({"type": "execute_task",
                                  "data": {"task_name": nome, "input_data": entrada}}))
        import time; t0 = time.time()
        while time.time() - t0 < timeout:
            m = json.loads(await asyncio.wait_for(ws.recv(), timeout=timeout))
            if m.get("type") == "task_completed": return m["data"].get("result", {})
            if m.get("type") == "error": return {"status": "erro", "error": m["data"].get("error")}
    return {"status": "timeout"}


def entrada_do_caso(tc):
    """Monta a entrada a partir das causas: causa NEGADA vira ausência/valor inválido do campo."""
    ent = dict(BASE)
    for e in (tc.get("entradas") or []):
        if e.get("verdadeira", True):
            # causa AFIRMADA que define parâmetro (ex.: "Formato selecionado é CSV")
            d = (e.get("desc") or "").lower()
            if "csv" in d: ent["formato"] = "csv"
            elif "pdf" in d: ent["formato"] = "pdf"
            continue
        d = (e.get("desc") or "").lower()
        if "credenciais" in d: ent["email"] = "inexistente@x.br"; ent["senha"] = "errada"
        elif "mfa" in d or "código" in d: ent["codigo_mfa"] = "000000"
        elif "paciente" in d: ent["paciente_id"] = "P-INEXISTENTE"
        elif "dados suficientes" in d or "parâmetros" in d or "obrigat" in d:
            for k in ("idade", "dias_cateter", "uti", "apache_ii", "microrganismo"): ent.pop(k, None)
        elif "mdr" in d or "multirresist" in d: ent["multirresistente"] = False
        elif "csv" in d: ent["formato"] = "pdf"   # caso nega CSV ⇒ pede PDF
        elif "schema" in d or "conform" in d or "nhsn" in d:
            # causa negada = "JSON recebido válido contra schema NHSN" é FALSA, ou seja, o
            # laboratório devolveu dado não conforme. Induz-se pedindo um caso que o
            # laboratório externo não conhece — a resposta volta sem os campos exigidos.
            ent["caso_id"] = "CAS-NAO-CONFORME"; ent["paciente_id"] = "P-NAO-CONFORME"
        elif "conexão" in d or "api" in d: ent["caso_id"] = "CAS-INEXISTENTE"
    return ent


def classifica(tc):
    """Decide COMO verificar o caso.

    DEFEITO CORRIGIDO (04/09/2026): a decisão era tomada pela REDAÇÃO do efeito. Efeito que
    começasse com "Exibe mensagem" virava busca de texto no código das telas, mesmo quando o
    caso de uso tem tarefa executável. Foi assim que o caso TC-UC-001-03 ("credenciais
    inválidas") passou como aprovado sem NUNCA tentar entrar com senha errada — e o login sem
    conferência de senha ficou meses invisível.

    Agora: se o caso de uso tem tarefa no sistema, o caso é EXECUTADO. Busca no código das
    telas só quando não há nada para executar.
    """
    ef = ((tc.get("efeito_esperado") or {}).get("desc") or "")
    # Quando a etapa de Casos de Teste declara O QUE CONFERIR, obedece a ela em vez de
    # adivinhar pela redação do efeito.
    obs = tc.get("efeito_observavel") or {}
    onde = (obs.get("onde") or "").lower()
    if onde == "externo":
        return "NAO_IMPL", "efeito depende de serviço externo não ligado ao sistema"
    if onde == "tela":
        return "INTERFACE", (obs.get("frase") or ef)
    if onde == "sistema":
        return "SISTEMA", ef
    for pat, motivo in NAO_IMPL:
        if re.search(pat, ef, re.I): return "NAO_IMPL", motivo
    # Efeito cujo SUJEITO é a tela (banner, selo, "a tela exibe") não tem como ser conferido
    # na resposta do sistema: continua sendo conferido na interface. Efeito cujo sujeito é o
    # SISTEMA vira execução, mesmo quando a frase começa com "Exibe".
    _so_tela = re.search(r"(?i)\b(tela do usu[áa]rio|banner|badge|skeleton|spinner|"
                         r"barra de progresso|cards? de kpi|gr[áa]ficos?)\b", ef)
    if UC_TASK.get(tc.get("uc")) and not _so_tela:
        return "SISTEMA", ef
    for pat, alvo in UI_ALVO:
        if re.search(pat, ef, re.I): return "INTERFACE", alvo
    return "SISTEMA", ef


def _mensagem_exigida(tc):
    """Frase entre aspas no efeito ('Credenciais inválidas'): o sistema tem de dizer isso."""
    ef = ((tc.get("efeito_esperado") or {}).get("desc") or "")
    m = re.search(r"['\"\u2018\u201c]([^'\"\u2019\u201d]{4,60})['\"\u2019\u201d]", ef)
    return m.group(1) if m else ""


def _tem_causa_negada(tc):
    return any(not e.get("verdadeira", True) for e in (tc.get("entradas") or []))


def _causa_induzida(tc):
    """A entrada montada consegue CRIAR a condição negada do caso?

    Se nenhuma causa negada casa com as regras de montagem de entrada, o sistema recebe dados
    válidos e responder com sucesso é o comportamento CERTO — reprovar aí seria mentira do
    teste. Esses casos saem como não exercitáveis.
    """
    padroes = ("credenciais", "mfa", "código", "codigo", "paciente", "dados suficientes",
               "parâmetros", "parametros", "obrigat", "mdr", "multirresist", "csv",
               "conexão", "conexao", "api", "schema", "conform", "nhsn")
    for e in (tc.get("entradas") or []):
        if e.get("verdadeira", True):
            continue
        d = (e.get("desc") or "").lower()
        if any(p in d for p in padroes):
            return True
    return False


def assercao_padrao(tc, r, houve_erro, txt):
    """Verificação usada quando o caso não tem asserção específica.

    Antes o padrão era "não deu erro = passou", o que aprovava qualquer coisa que respondesse.
    Agora: caso com CAUSA NEGADA espera recusa ou a mensagem especificada; caso com todas as
    causas verdadeiras espera sucesso. E quando o efeito traz uma frase entre aspas, essa frase
    tem de aparecer na resposta.
    """
    obs = tc.get("efeito_observavel") or {}
    if obs.get("espera") == "recusa":
        frase = obs.get("frase") or ""
        if frase:
            achou = frase.lower() in txt
            return achou, (f"recusou dizendo '{frase}'" if achou
                           else f"não recusou com '{frase}' — respondeu: {txt[:90]}")
        return houve_erro, ("recusou, como o caso exige" if houve_erro else "aceitou entrada inválida")
    msg = _mensagem_exigida(tc)
    if msg:
        achou = msg.lower() in txt
        if achou:
            return True, f"respondeu '{msg}'"
        # DEFEITO CORRIGIDO: eu tratava QUALQUER causa falsa como "espere recusa". Mas negar uma
        # causa que já é negativa ("Dados insuficientes" = FALSO) descreve o caminho FELIZ. Quem
        # sabe o que esperar é o campo declarado pela etapa (espera: recusa | sucesso), não a
        # contagem de causas negadas. Com 'sucesso', a frase é RÓTULO e a tela é quem exibe.
        espera_sucesso = (obs.get("espera") == "sucesso") if obs else (not _tem_causa_negada(tc))
        if espera_sucesso and msg.lower() in FE_SRC.lower() and not houve_erro:
            return True, f"rótulo '{msg}' exibido pela tela; sistema devolveu o dado"
        return False, f"não disse '{msg}' — respondeu: {txt[:90]}"
    if _tem_causa_negada(tc):
        if not _causa_induzida(tc):
            return None, "a condição do caso não se cria pela entrada — não exercitável"
        return houve_erro, ("recusou, como o caso exige" if houve_erro
                            else "aceitou uma entrada que o caso marca como inválida")
    return (not houve_erro), ("executou" if not houve_erro else f"falhou: {txt[:90]}")


def _arquivo(r, ext):
    a = str((r or {}).get("arquivo_gerado") or "")
    return (a.endswith(ext), f"arquivo_gerado={a.rsplit('/',1)[-1] or 'NENHUM'}")


# Casos cuja CONDIÇÃO não se cria pela entrada (exigem induzir falha interna do sistema).
# Antes, qualquer caso sem asserção caía aqui — inclusive os que dava para exercitar.
_NAO_EXERCITAVEL = {
    "TC-UC-001-05": "exige o código expirar e o usuário pedir reenvio",
    "TC-UC-004-04": "exige provocar erro interno na regra de classificação",
    "TC-UC-007-02": "exige a base de protocolos ficar indisponível",
    "TC-UC-007-03": "exige falha ao carregar recomendações",
    "TC-UC-008-02": "exige um perfil sem estimativa disponível",
    "TC-UC-008-03": "exige provocar erro no cálculo",
}

# Asserção por caso de teste: recebe (resultado, houve_erro, texto) e devolve (passou, motivo).
# Só os casos cujo efeito é objetivamente conferível no resultado entram aqui; os demais são
# reportados como NÃO EXERCITÁVEL — nem aprovados, nem reprovados.
ASSERTS = {
    "TC-UC-003-04": lambda r, e, t: (e and ("conform" in t or "bloquead" in t),
                                     "bloqueou e avisou dados não conformes" if ("conform" in t)
                                     else ("bloqueou, sem dizer que era dado não conforme" if e
                                           else "deveria bloquear dado não conforme")),
    "TC-UC-005-01": lambda r, e, t: (not e and ("alerta_id" in t or "notificado" in t),
                                     "criou registro de alerta" if not e else "não criou"),
    # Caso negativo do alerta: além de seguir o fluxo, o sistema NÃO pode ter criado alerta.
    # A asserção antiga aceitava "não deu erro" — e por isso aprovava o detector que alertava
    # em toda amostra.
    "TC-UC-005-05": lambda r, e, t: (
        (not e) and (r or {}).get("is_mdr") is not True and not (r or {}).get("alerta_id"),
        "seguiu o fluxo sem criar alerta" if not e and not (r or {}).get("alerta_id")
        else "criou alerta numa amostra que não é multirresistente"),
    "TC-UC-006-02": lambda r, e, t: (e and ("verifica" in t or "obrigat" in t or "require" in t),
                                     "recusou por campo obrigatório" if e else "calculou mesmo sem os dados"),
    # 007-02 / 008-02: a condição do caso é "a base de bundles falha" / "dados insuficientes".
    # Remover campos da ENTRADA não cria essa condição — o agente lê o caso do banco e, com dados,
    # recomendar é o comportamento CERTO. A verificação real é a sonda de recusa (SONDA_RECUSA),
    # com um caso sem dado nenhum; por isso estes dois saem como não exercitáveis pela entrada.
    "TC-UC-011-02": lambda r, e, t: (("nenhum registro" in t) or isinstance((r or {}).get("logs"), list),
                                     "distinguiu resultado vazio" if "nenhum registro" in t else "devolveu logs nulo, sem distinguir vazio"),
    "TC-UC-012-01": lambda r, e, t: _arquivo(r, ".pdf"),
    "TC-UC-012-02": lambda r, e, t: _arquivo(r, ".csv"),
}


async def semear_contexto():
    """Roda a cadeia clínica ANTES dos casos, para que cada caso parta do MESMO estado que o
    sistema tem em uso real. Sem isto, uma tarefa chamada isolada falha por falta de dado que
    a etapa anterior produz (ex.: o alerta MDR precisa da microbiologia) — seria culpa do teste,
    não do sistema."""
    # Cria pelo próprio app o usuário usado nos casos de login (senha conferível).
    import time as _t
    USUARIO_TESTE["email"] = f"caso.teste.{int(_t.time())}@hospital.br"
    try:
        _u = await exec_task("criar_usuarios", {
            "nome": "Caso de Teste", "email": USUARIO_TESTE["email"],
            "senha": USUARIO_TESTE["senha"], "papel": "Medico", "status": "Ativo"})
        if isinstance(_u, dict) and _u.get("id"):
            BASE["email"] = USUARIO_TESTE["email"]
            BASE["senha"] = USUARIO_TESTE["senha"]
            print(f"usuário de teste criado pelo app: {USUARIO_TESTE['email']}")
    except Exception as _e:
        print(f"não foi possível criar o usuário de teste ({_e}) — casos de login usam o do banco")

    ctx = dict(BASE)
    cadeia = ["authenticate_user_mfa", "init_import_session", "fetch_and_persist_microbiology",
              "classify_case_nhsn", "detect_mdr_and_alert", "calculate_cox_risk_score",
              "recommend_treatment_bundle", "estimate_risk_reduction"]
    for t in cadeia:
        try:
            r = await exec_task(t, ctx)
            if isinstance(r, dict) and r.get("status") != "erro":
                for k, v in r.items():
                    if v is not None and not isinstance(v, (dict, list)):
                        ctx[k] = v
        except Exception:
            pass
    print(f"contexto semeado pela cadeia: {len(ctx)} campos "
          f"(inclui {', '.join(k for k in ('microbiologia_id','micro_id','valor_escore','classificacao_nhsn') if k in ctx) or 'nenhum id'})\n")
    return ctx


async def main():
    global BASE
    BASE = await semear_contexto()
    linhas, resumo = [], {"SISTEMA_OK": 0, "SISTEMA_FALHA": 0, "NAO_EXERC": 0, "INTERFACE_OK": 0,
                          "INTERFACE_FALTA": 0, "NAO_IMPL": 0, "SEM_CASO": 0}
    for bloco in TCS:
        nome_uc = bloco.get("uc_name") or bloco.get("name") or "?"
        casos = bloco.get("test_cases") or []
        if not casos:
            linhas.append((nome_uc, "—", "SEM CASO", "a etapa de Casos de Teste não gerou casos para este caso de uso"))
            resumo["SEM_CASO"] += 1
            continue
        for tc in casos:
            uc = tc.get("uc"); tid = tc.get("id")
            tipo, alvo = classifica(tc)
            efeito = ((tc.get("efeito_esperado") or {}).get("desc") or "")[:70]
            if tipo == "NAO_IMPL":
                linhas.append((tid, uc, "NÃO IMPLEMENTADO", f"{efeito} — {alvo}")); resumo["NAO_IMPL"] += 1
            elif tipo == "INTERFACE":
                ok = alvo.lower() in FE_SRC.lower()
                linhas.append((tid, uc, "INTERFACE OK" if ok else "INTERFACE FALTA",
                               f"{efeito} — procurado no código das telas: '{alvo}'"))
                resumo["INTERFACE_OK" if ok else "INTERFACE_FALTA"] += 1
            else:
                tarefa = UC_TASK.get(uc)
                if not tarefa:
                    linhas.append((tid, uc, "SEM TAREFA", efeito)); resumo["SISTEMA_FALHA"] += 1; continue
                try:
                    r = await exec_task(tarefa, entrada_do_caso(tc))
                except Exception as exc:
                    r = {"status": "erro", "error": str(exc)[:120]}
                erro = (isinstance(r, dict) and (r.get("status") == "erro" or r.get("error")))
                txt = json.dumps(r, ensure_ascii=False).lower()
                det = json.dumps(r, ensure_ascii=False)[:110]
                # Confere o EFEITO ESPERADO, não apenas sucesso/erro — um caso "negativo" pode
                # esperar um caminho alternativo de SUCESSO (ex.: formato != CSV ⇒ gera PDF).
                veredito = ASSERTS.get(tid)
                if veredito is None:
                    # Sem asserção específica, usa a padrão — que EXIGE o efeito (mensagem
                    # especificada, ou recusa quando a causa é negada). Só fica "não
                    # exercitável" o caso cuja condição não se cria pela entrada.
                    if _NAO_EXERCITAVEL.get(tid):
                        linhas.append((tid, uc, "NÃO EXERCITÁVEL",
                                       f"{efeito} — {_NAO_EXERCITAVEL[tid]} → {det}"))
                        resumo["NAO_EXERC"] += 1
                        print(f"  {tid:16} NÃO EXERCITÁVEL", flush=True); continue
                    ok, porque = assercao_padrao(tc, r, erro, txt)
                    if ok is None:
                        linhas.append((tid, uc, "NÃO EXERCITÁVEL", f"{efeito} — {porque} → {det}"))
                        resumo["NAO_EXERC"] += 1
                        print(f"  {tid:16} NÃO EXERCITÁVEL", flush=True); continue
                else:
                    ok, porque = veredito(r, erro, txt)
                linhas.append((tid, uc, "PASSOU" if ok else "FALHOU", f"{efeito} — {porque} → {det}"))
                resumo["SISTEMA_OK" if ok else "SISTEMA_FALHA"] += 1
                print(f"  {tid:16} {'PASSOU' if ok else 'FALHOU'}  {porque[:44]} | {det[:60]}", flush=True)
    print("\n--- SONDA DE RECUSA (caso sem dado nenhum): o agente inventa ou declara insuficiência? ---")
    for tarefa in ("recommend_treatment_bundle", "estimate_risk_reduction"):
        try:
            rr = await exec_task(tarefa, {"caso_id": "CAS-SEM-DADOS", "usuario_id": "U-001"})
        except Exception as exc:
            rr = {"status": "erro", "error": str(exc)[:90]}
        tt = json.dumps(rr, ensure_ascii=False)
        recusou = bool(rr.get("dados_insuficientes")) or "dados_insuficientes" in tt
        inventou = (not recusou) and (rr.get("status") == "sucesso" or rr.get("bundle_nome") or rr.get("reducao_risco"))
        estado = "DECLAROU INSUFICIÊNCIA (correto)" if recusou else ("INVENTOU (defeito)" if inventou else "erro")
        print(f"  {tarefa:30} {estado}  {tt[:100]}")
        linhas.append((f"SONDA:{tarefa[:22]}", "—", "PASSOU" if recusou else "FALHOU",
                       f"caso sem dados → {tt[:80]}"))
        resumo["SISTEMA_OK" if recusou else "SISTEMA_FALHA"] += 1
    print("\n" + "=" * 100)
    print(f"{'CASO':17}{'UC':9}{'RESULTADO':20}DETALHE")
    print("=" * 100)
    for a, b, c, d in linhas: print(f"{a:17}{b:9}{c:20}{d[:60]}")
    print("=" * 100)
    tot = sum(resumo.values())
    print(f"TOTAL {tot} casos:")
    print(f"  comportamento do sistema — PASSOU: {resumo['SISTEMA_OK']} | FALHOU: {resumo['SISTEMA_FALHA']}"
          f" | NÃO EXERCITÁVEL: {resumo['NAO_EXERC']}")
    print(f"  elemento de interface    — EXISTE: {resumo['INTERFACE_OK']} | FALTA: {resumo['INTERFACE_FALTA']}")
    print(f"  efeito NÃO implementado  — {resumo['NAO_IMPL']}")
    print(f"  caso de uso sem caso gerado — {resumo['SEM_CASO']}")
    json.dump({"resumo": resumo, "linhas": linhas}, open("/tmp/testcases_result.json", "w"),
              ensure_ascii=False, indent=1)

asyncio.run(main())
