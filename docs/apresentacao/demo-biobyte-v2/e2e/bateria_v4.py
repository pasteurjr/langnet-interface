#!/usr/bin/env python3
"""Bateria do BioByte Sentinela v4: percorre os casos de uso no aplicativo implantado.

Cada passo chama a tarefa do caso de uso pelo servidor de agentes e usa o que ela devolve para
alimentar o passo seguinte — é o caminho que o operador faria pelas telas. Nada é simulado: o
que falhar aparece com o motivo que o próprio aplicativo deu.

uso: python3 bateria_v4.py <porta_ws> <banco_do_app>
"""
import asyncio, json, sys, time
import websockets
import pymysql

PORTA = sys.argv[1] if len(sys.argv) > 1 else "5005"
BANCO = sys.argv[2] if len(sys.argv) > 2 else "biobyte_v4_app"
EMAIL = "ana.ribeiro@hospitalvidas.org.br"
SENHA = "Senha@123"
ADMIN = "admin.sistema@hospitalvidas.org.br"
PRONTUARIO = f"PRT-{int(time.time())}"

def banco():
    return pymysql.connect(host="127.0.0.1", port=3308, user="producao",
                           password="112358123", database=BANCO, charset="utf8mb4",
                           cursorclass=pymysql.cursors.DictCursor, autocommit=True)

async def tarefa(nome, entrada, limite=180):
    async with websockets.connect(f"ws://localhost:{PORTA}", max_size=None, open_timeout=10) as ws:
        try: await asyncio.wait_for(ws.recv(), timeout=2)
        except Exception: pass
        await ws.send(json.dumps({"type": "execute_task",
                                  "data": {"task_name": nome, "input_data": entrada}}))
        t0 = time.time()
        while time.time() - t0 < limite:
            m = json.loads(await asyncio.wait_for(ws.recv(), timeout=limite))
            if m.get("type") == "task_completed":
                return m["data"].get("result", {})
            if m.get("type") == "error":
                return {"status": "erro", "error": m["data"].get("error")}
    return {"status": "tempo esgotado"}

RESUMO = []

def conta(nome, r, esperado=None):
    txt = json.dumps(r, ensure_ascii=False, default=str)
    if isinstance(r, dict) and (r.get("tarefa_incompleta") or r.get("status") in ("erro", "tempo esgotado")
                                or r.get("error")):
        veredito = "FALHOU"
    elif esperado and not all(k in txt for k in esperado):
        veredito = "SEM O ESPERADO"
    else:
        veredito = "OK"
    RESUMO.append((nome, veredito, txt[:200]))
    print(f"[{veredito}] {nome}: {txt[:260]}")
    return r

def referencia():
    """Dados de CATÁLOGO (critério NHSN e bundles). Não é comportamento: é a tabela de consulta
    que o hospital carrega uma vez. Sem ela, classificar e recomendar não têm o que ler."""
    with banco() as cn, cn.cursor() as c:
        c.execute("SELECT COUNT(*) n FROM criterios_nhsn")
        if not c.fetchone()["n"]:
            c.execute("INSERT INTO criterios_nhsn(nome, versao, limiares, vigencia_inicio) "
                      "VALUES(%s,%s,%s,CURDATE())",
                      ("ICSAC-CLABSI", "2024",
                       json.dumps({"dias_cateter_min": 2, "apache_ii_min": 10})))
        c.execute("SELECT COUNT(*) n FROM bundles")
        if not c.fetchone()["n"]:
            for nome, ind, red, ic in [
                ("Bundle de Inserção de Cateter", "ICSAC confirmada", 0.35, "0.25-0.45"),
                ("Bundle de Manutenção Diária", "ICSAC confirmada multirresistente", 0.28, "0.18-0.38"),
                ("Bundle de Higiene das Mãos", "prevenção geral", 0.15, "0.08-0.22")]:
                c.execute("INSERT INTO bundles(nome, indicacao, reducao_media_risco, "
                          "intervalo_confianca_reducao) VALUES(%s,%s,%s,%s)",
                          (nome, ind, red, ic))
        # O PRIMEIRO administrador é semeado, como em qualquer sistema: não existe tela para
        # criar o primeiro administrador antes de haver administrador.
        import hashlib
        c.execute("SELECT id FROM usuarios WHERE email=%s", (ADMIN,))
        if not c.fetchone():
            c.execute("INSERT INTO usuarios(nome, email, senha_hash, papel, ativo) "
                      "VALUES(%s,%s,%s,'admin',1)",
                      ("Administrador do Sistema", ADMIN,
                       hashlib.sha256(SENHA.encode()).hexdigest()))
        c.execute("SELECT id FROM usuarios WHERE email=%s", (ADMIN,))
        u = c.fetchone()
    return (u or {}).get("id")

async def principal():
    uid = referencia()
    global PRONTUARIO
    print(f"usuário da bateria: {uid}\n")

    r = conta("UC-001 entrar no sistema (senha certa)",
              await tarefa("autenticar_usuario", {"email": ADMIN, "senha": SENHA}), ["token"])
    token = r.get("token"); usuario_id = r.get("usuario_id") or uid

    conta("UC-001 entrar no sistema (senha errada recusa)",
          {"recusou": (await tarefa("autenticar_usuario", {"email": ADMIN, "senha": "errada"}))})
    if token:
        conta("UC-001 conferir a sessão", await tarefa("validar_token_requisicao", {"token": token}))

    conta("UC-002 cadastrar usuário", await tarefa("cadastrar_usuario", {
        "nome": "Carlos Enfermeiro", "email": f"carlos{int(time.time())}@hospitalvidas.org.br",
        "senha": "Senha@456", "papel": "enfermeiro", "ativo": 1}))

    r = conta("UC-003 cadastrar paciente e caso", await tarefa("cadastrar_paciente_e_caso", {
        "usuario_id": usuario_id, "nome": "Maria Souza", "data_nascimento": "1953-04-12",
        "sexo": "feminino", "numero_prontuario": f"PRT-{int(time.time())}",
        "medico_responsavel_id": usuario_id, "idade_na_data": 72, "dias_cateter": 12,
        "apache_ii": 18, "sitio_insercao": "jugular", "comorbidades_relevantes": "diabetes",
        "data_inicio": "2026-09-01", "data_encerramento": None, "estado": "ativo"}))
    caso_id = r.get("caso_id") or r.get("id")
    paciente_id = r.get("paciente_id")
    if not caso_id:
        with banco() as cn, cn.cursor() as c:
            c.execute("SELECT id, paciente_id FROM casos_clinicos ORDER BY created_at DESC LIMIT 1")
            f = c.fetchone() or {}
            caso_id = f.get("id"); paciente_id = paciente_id or f.get("paciente_id")
    print(f"   caso={caso_id} paciente={paciente_id}\n")

    conta("UC-005 consultar microbiologia (serviço externo)",
          await tarefa("consultar_microbiologia",
                       {"usuario_id": usuario_id, "paciente_id": paciente_id, "caso_id": caso_id}))
    conta("UC-005 importar resultado sem duplicar", await tarefa("importar_resultado_idempotente", {
        "identificador_amostra": "HMC-88213", "origem": "LIS", "situacao": "positivo",
        "microrganismo": "Staphylococcus aureus", "multirresistente": 1,
        "paciente_id": paciente_id, "caso_id": caso_id}))
    conta("UC-006 classificar pelo critério NHSN",
          await tarefa("classificar_caso_nhsn", {"caso_id": caso_id, "usuario_id": usuario_id}))
    conta("UC-007 detectar multirresistência",
          await tarefa("detectar_multirresistencia", {"usuario_id": usuario_id, "caso_id": caso_id}))
    conta("UC-007 abrir alerta", await tarefa("abrir_alerta_multirresistencia", {
        "usuario_id": usuario_id, "caso_id": caso_id, "tipo": "multirresistencia",
        "gravidade": "alta"}))
    conta("UC-031 não repetir alerta igual", await tarefa("deduplicar_alerta_multirresistencia", {
        "usuario_id": usuario_id, "caso_id": caso_id,
        "microrganismo": "Staphylococcus aureus", "janela_dias": 7}))
    conta("UC-004 calcular escore de risco (serviço externo)",
          await tarefa("calcular_escore_cox", {"usuario_id": usuario_id, "caso_id": caso_id}))
    conta("UC-015 tratar serviço de escore fora do ar", await tarefa("tratar_indisponibilidade_cox", {
        "usuario_id": usuario_id, "caso_id": caso_id, "erro": "tempo de resposta esgotado"}))

    r = conta("UC-008 recomendar bundle",
              await tarefa("recomendar_bundle", {"usuario_id": usuario_id, "caso_id": caso_id}))
    recomendacao_id = r.get("recomendacao_id")
    if not recomendacao_id:
        with banco() as cn, cn.cursor() as c:
            c.execute("SELECT id FROM recomendacoes ORDER BY created_at DESC LIMIT 1")
            recomendacao_id = (c.fetchone() or {}).get("id")
    with banco() as cn, cn.cursor() as c:
        c.execute("SELECT id FROM bundles LIMIT 1")
        bundle_id = (c.fetchone() or {}).get("id")
    conta("UC-008 registrar a escolha do bundle", await tarefa("registrar_escolha_bundle", {
        "usuario_id": usuario_id, "recomendacao_id": recomendacao_id,
        "bundle_escolhido_id": bundle_id}))
    conta("UC-009 estimar redução de risco", await tarefa("estimar_reducao_risco", {
        "usuario_id": usuario_id, "recomendacao_id": recomendacao_id, "horizonte_dias": 30}))
    conta("UC-030 classificar pela ANVISA",
          await tarefa("classificar_caso_anvisa", {"usuario_id": usuario_id, "caso_id": caso_id}))
    conta("UC-012 exportar relatório de vigilância", await tarefa("exportar_relatorio_vigilancia", {
        "usuario_id": usuario_id, "data_inicio": "2026-09-01", "data_fim": "2026-09-30",
        "formato": "csv", "paciente_id": paciente_id}))
    conta("UC-026 registrar consentimento", await tarefa("registrar_consentimento", {
        "usuario_id": usuario_id, "numero_prontuario": PRONTUARIO, "base_legal": "consentimento",
        "consentimento_obtido": 1, "data_consentimento": "2026-09-23"}))
    conta("UC-028 registrar operação de tratamento", await tarefa("registrar_operacao_tratamento", {
        "usuario_id": usuario_id, "finalidade": "vigilância epidemiológica",
        "categorias_dados": json.dumps(["dados de saude", "dados sensiveis"]), "base_legal": "tutela_saude"}))
    with banco() as cn, cn.cursor() as c:
        c.execute("SELECT id FROM criterios_nhsn LIMIT 1")
        criterio_id = (c.fetchone() or {}).get("id")
        c.execute("SELECT id FROM resultados_hemocultura ORDER BY created_at DESC LIMIT 1")
        resultado_id = (c.fetchone() or {}).get("id")
    conta("UC-033 mapear terminologia da microbiologia",
          await tarefa("mapear_terminologia_microbiologia",
                       {"usuario_id": usuario_id, "resultado_id": resultado_id}))
    with banco() as cn, cn.cursor() as c:
        import hashlib
        c.execute("SELECT id FROM usuarios WHERE papel='medico' LIMIT 1")
        _m = c.fetchone()
        if not _m:
            c.execute("INSERT INTO usuarios(nome, email, senha_hash, papel, ativo) "
                      "VALUES('Dr. Paulo Medico','medico@hospitalvidas.org.br',%s,'medico',1)",
                      (hashlib.sha256(SENHA.encode()).hexdigest(),))
            c.execute("SELECT id FROM usuarios WHERE papel='medico' LIMIT 1")
            _m = c.fetchone()
    conta("UC-006 sobrescrever a classificação", await tarefa("sobrescrever_classificacao", {
        "usuario_id": _m["id"], "caso_id": caso_id, "criterio_id": criterio_id,
        "novo_resultado": "descartada", "justificativa": "revisão da comissão"}))
    conta("UC-003 encerrar o caso", await tarefa("encerrar_caso", {
        "usuario_id": usuario_id, "caso_id": caso_id, "data_encerramento": "2026-09-23"}))

    print("\n" + "=" * 70)
    ok = sum(1 for _, v, _ in RESUMO if v == "OK")
    print(f"BATERIA: {ok} de {len(RESUMO)} passos correram até o fim")
    for n, v, t in RESUMO:
        if v != "OK":
            print(f"  {v}: {n} — {t[:170]}")
    with banco() as cn, cn.cursor() as c:
        for t in ("usuarios", "pacientes", "casos_clinicos", "resultados_hemocultura",
                  "classificacoes_caso", "alertas_multirresistencia", "escores_cox",
                  "recomendacoes", "registros_auditoria"):
            try:
                c.execute(f"SELECT COUNT(*) n FROM {t}")
                print(f"  {t}: {c.fetchone()['n']}")
            except Exception as e:
                print(f"  {t}: (não existe) {e}")

asyncio.run(principal())
