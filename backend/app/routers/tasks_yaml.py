import re
"""
API Router: Tasks YAML Generation
Gera tasks.yaml a partir de documentos MD de especificação de agentes/tarefas
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import uuid
import re
import json
from datetime import datetime

from app.database import get_db_connection
from app.database import (
    create_tasks_yaml_session, get_tasks_yaml_session, update_tasks_yaml_session,
    list_tasks_yaml_sessions, create_tasks_yaml_version, get_tasks_yaml_versions,
    save_tasks_yaml_chat_message, get_tasks_yaml_chat_messages,
    get_agent_task_spec_session  # Para buscar documento MD base
)
from app.routers.auth import get_current_user
from app.llm import get_llm_response_async
from prompts.generate_tasks_yaml import get_tasks_yaml_prompt
from prompts.generate_single_task_yaml import (
    parse_task_blocks, parse_schema_tables, select_relevant_tables,
    build_sub_schema, needs_persistence, validate_task_yaml,
    build_single_task_prompt, extract_task_block,
)
from prompts.review_tasks_yaml import get_review_tasks_yaml_prompt



def _projeto_da_sessao(tabela: str, session_id: str) -> str:
    """Descobre o projeto a partir da sessão — a função de geração só recebe a sessão."""
    from app.database import get_db_connection as _conn
    try:
        with _conn() as c:
            cur = c.cursor(dictionary=True)
            cur.execute(f"SELECT project_id FROM {tabela} WHERE id=%s", (session_id,))
            row = cur.fetchone()
            cur.close()
        return str(row["project_id"]) if row and row.get("project_id") else ""
    except Exception:
        return ""


def _ferramentas_do_inventario(project_id: str) -> dict:
    """Devolve {quem_usa: [ferramentas]} a partir do inventário da etapa Ferramentas.

    POR QUE: a etapa Ferramentas resolve QUEM implementa cada serviço, e guarda em cada
    ferramenta a lista de quem a usa (`agente:nome`, `tarefa:nome`). Essa informação não chegava
    ao YAML: medido no BioByte em 22/09/2026, os 15 agentes e as 45 tarefas saíram SEM NENHUMA
    ferramenta declarada — o aplicativo gerado não teria como chamar o laboratório, o escore de
    Cox nem o e-mail, que são as três integrações reais do sistema.

    Quem liga as duas pontas é o programa, não o modelo: a resposta já está gravada.
    Ferramenta que o inventário marcou como NÃO resolvida fica de fora — declarar ferramenta que
    ninguém implementa seria pior que a falta.
    """
    import json as _json
    from app.database import get_db_connection as _conn
    uso: dict = {}
    try:
        with _conn() as c:
            cur = c.cursor(dictionary=True)
            cur.execute(
                """SELECT tools_json FROM tool_sessions
                   WHERE project_id=%s AND status='completed'
                   ORDER BY created_at DESC LIMIT 1""", (project_id,))
            row = cur.fetchone()
            cur.close()
        if not row or not row.get("tools_json"):
            return uso
        dados = _json.loads(row["tools_json"])
        ferramentas = dados if isinstance(dados, list) else (dados.get("tools") or [])
        for f in ferramentas:
            if not f.get("resolvida"):
                continue
            nome = str(f.get("nome") or "").strip()
            if not nome:
                continue
            for quem in (f.get("usada_por") or []):
                q = str(quem).strip()
                if ":" in q:
                    q = q.split(":", 1)[1].strip()
                if q:
                    uso.setdefault(q, [])
                    if nome not in uso[q]:
                        uso[q].append(nome)
    except Exception as e:
        print(f"[YAML] inventário de ferramentas indisponível: {e}")
    return uso


def _acrescentar_ferramentas_ao_yaml(conteudo: str, uso: dict) -> str:
    """Escreve `tools:` em cada bloco do YAML cujo nome aparece no inventário.

    Trabalha no texto para não reescrever o arquivo inteiro (comentários e ordem se mantêm).
    Bloco que já declara `tools:` não é tocado.
    """
    if not conteudo or not uso:
        return conteudo
    linhas = conteudo.splitlines()
    saida, i, n = [], 0, len(linhas)
    while i < n:
        linha = linhas[i]
        saida.append(linha)
        m = re.match(r"^([A-Za-z_][\w\-]*):\s*$", linha)
        if m:
            nome = m.group(1)
            ferramentas = uso.get(nome)
            if ferramentas:
                # varre o bloco para ver se já tem tools:
                j, tem_tools, recuo = i + 1, False, ""
                while j < n and (not linhas[j].strip() or linhas[j].startswith((" ", "\t"))):
                    if re.match(r"^\s+tools\s*:", linhas[j]):
                        tem_tools = True
                    # o recuo é o da PRIMEIRA linha do bloco: pegar o de uma linha mais funda
                    # (um campo aninhado) escreve `tools:` num nível errado e quebra o arquivo.
                    if not recuo and linhas[j].strip() and not linhas[j].strip().startswith("#"):
                        recuo = linhas[j][: len(linhas[j]) - len(linhas[j].lstrip())]
                    j += 1
                recuo = recuo or "  "
                if not tem_tools:
                    saida.append(f"{recuo}tools:")
                    for f in ferramentas:
                        saida.append(f"{recuo}  - {f}")
        i += 1
    novo = "\n".join(saida) + ("\n" if conteudo.endswith("\n") else "")
    # Trava: se o acréscimo estragou o arquivo, fica o original. Um YAML quebrado derruba a
    # geração de código inteira, e um recuo errado já fez exatamente isso em 22/09/2026.
    try:
        import yaml as _yaml
        _yaml.safe_load(re.sub(r"^```[a-z]*\n|```\s*$", "", novo.strip(), flags=re.M))
    except Exception as e:
        print(f"[YAML] acréscimo de ferramentas descartado — quebraria o arquivo: {e}")
        return conteudo
    return novo

router = APIRouter(prefix="/tasks-yaml", tags=["tasks-yaml"])


# ═══════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════

class GenerateRequest(BaseModel):
    agent_task_spec_session_id: str
    agent_task_spec_version: int = 1
    custom_instructions: Optional[str] = None


class RefineRequest(BaseModel):
    message: str
    action_type: str = "refine"


# ═══════════════════════════════════════════════════════════
# GERAÇÃO INICIAL
# ═══════════════════════════════════════════════════════════

@router.post("/")
async def generate_tasks_yaml(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera tasks.yaml a partir de documento MD de agentes/tarefas
    """
    user_id = current_user['id']
    session_id = str(uuid.uuid4())

    # Buscar documento MD base
    spec_session = get_agent_task_spec_session(request.agent_task_spec_session_id)
    if not spec_session:
        raise HTTPException(status_code=404, detail="Especificação de agentes/tarefas não encontrada")

    if not spec_session.get("agent_task_spec_document"):
        raise HTTPException(status_code=400, detail="Documento de especificação vazio")

    # Criar sessão
    session_data = {
        "id": session_id,
        "project_id": spec_session["project_id"],
        "user_id": user_id,
        "agent_task_spec_session_id": request.agent_task_spec_session_id,
        "agent_task_spec_version": request.agent_task_spec_version,
        "session_name": f"tasks_yaml_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "generating",
        "execution_metadata": {}
    }

    create_tasks_yaml_session(session_data)

    # Busca schema_sql do Data Model mais recente do projeto — permite ao LLM
    # gerar Process steps SQL corretos respeitando o schema real das tabelas.
    _schema_sql = ""
    try:
        from app.database import get_db_connection as _gdb
        with _gdb() as _c:
            _cur = _c.cursor(dictionary=True)
            _cur.execute("""
                SELECT schema_sql FROM data_model_sessions
                WHERE project_id=%s AND schema_sql IS NOT NULL
                  AND CHAR_LENGTH(schema_sql) > 0
                ORDER BY created_at DESC LIMIT 1
            """, (spec_session["project_id"],))
            _r = _cur.fetchone()
            if _r:
                _schema_sql = _r["schema_sql"]
            _cur.close()
    except Exception as _e:
        print(f"[TASKS_YAML] warning: falha ao carregar schema: {_e}")

    # Background task
    background_tasks.add_task(
        execute_tasks_yaml_generation,
        session_id,
        spec_session["agent_task_spec_document"],
        request.custom_instructions,
        user_id,
        _schema_sql,
    )

    return {
        "session_id": session_id,
        "status": "generating",
        "message": "Geração de tasks.yaml iniciada"
    }


async def execute_tasks_yaml_generation(
    session_id: str,
    agent_task_spec_document: str,
    custom_instructions: Optional[str],
    user_id: str,
    data_model_schema_sql: str = "",
):
    """
    Background task: Gera tasks.yaml via LLM.

    Estratégia atual (chunked):
      1. Parseia tasks do ATS.
      2. Parseia schema em tabelas individuais.
      3. Para cada task: seleciona sub-schema relevante, chama LLM com prompt
         focado em UMA task, valida (INSERT/UPDATE/DELETE presente se persistir),
         retenta 1x com hint em caso de falha.
      4. Concatena todas em tasks.yaml final.

    Fallback: se >50% das tasks falharem mesmo após retry, cai pro single-shot
    legado (get_tasks_yaml_prompt).
    """
    try:
        print(f"\n{'='*80}")
        print(f"[TASKS_YAML] Starting generation for session {session_id}")
        print(f"[TASKS_YAML] schema_sql: {len(data_model_schema_sql)} chars")
        print(f"{'='*80}\n")

        start_time = datetime.now()

        # ── Parse ──
        task_blocks = parse_task_blocks(agent_task_spec_document)
        tables = parse_schema_tables(data_model_schema_sql) if data_model_schema_sql else {}
        print(f"[TASKS_YAML] parsed {len(task_blocks)} tasks, {len(tables)} tables")

        if not task_blocks:
            print("[TASKS_YAML] ⚠️ no task blocks parsed — falling back to single-shot")
            tasks_yaml_content = await _fallback_single_shot(
                agent_task_spec_document, custom_instructions, data_model_schema_sql
            )
        else:
            # ── Chunked per-task generation ──
            chunks, stats = await _generate_task_by_task(
                task_blocks, tables, custom_instructions, agent_task_spec_document
            )
            fail_ratio = stats["failed"] / max(stats["total"], 1)
            if fail_ratio > 0.5:
                print(f"[TASKS_YAML] ⚠️ {stats['failed']}/{stats['total']} tasks failed — falling back to single-shot")
                tasks_yaml_content = await _fallback_single_shot(
                    agent_task_spec_document, custom_instructions, data_model_schema_sql
                )
            else:
                tasks_yaml_content = "\n".join(chunks)
                tasks_yaml_content = _sanitize_task_keys(tasks_yaml_content)
                tasks_yaml_content = _garantir_arquivo_legivel(tasks_yaml_content)
                print(f"[TASKS_YAML] chunked OK: {stats['ok']} ok, {stats['retried']} retried, "
                      f"{stats['failed']} failed, {stats['with_sql']} with SQL")

        # O tasks.yaml segue o padrão do framework (CrewAI): description e expected_output.
        # Ferramenta, agente, natureza e rastreabilidade NÃO entram aqui — estão no documento de
        # Agentes e Tarefas (colunas Tools, Agent, UC/RF Relacionado) e é de lá que a geração de
        # código as lê. Foram desviadas para o YAML entre 16/07 e 23/09/2026 e revertidas em
        # 24/09/2026 a pedido.

        end_time = datetime.now()
        generation_time_ms = int((end_time - start_time).total_seconds() * 1000)

        print(f"[TASKS_YAML] ✅ Generated {len(tasks_yaml_content)} chars in {generation_time_ms}ms")

        # Contar tasks (linhas top-level com nome_snake:)
        import re
        task_matches = re.findall(r'^[a-z_][\w]*:\s*$', tasks_yaml_content, re.MULTILINE)
        total_tasks = len(task_matches)

        update_tasks_yaml_session(session_id, {
            "status": "completed",
            "tasks_yaml_content": tasks_yaml_content,
            "total_tasks": total_tasks,
            "generation_time_ms": generation_time_ms,
            "finished_at": datetime.now()
        })

        create_tasks_yaml_version({
            "session_id": session_id,
            "version": 1,
            "tasks_yaml_content": tasks_yaml_content,
            "created_by": user_id,
            "change_type": "initial_generation",
            "change_description": "Geração inicial do tasks.yaml (chunked por task)",
            "doc_size": len(tasks_yaml_content)
        })

        print(f"[TASKS_YAML] ✅ Session completed: {total_tasks} tasks")

    except Exception as e:
        print(f"[TASKS_YAML] ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

        update_tasks_yaml_session(session_id, {
            "status": "failed",
            "generation_log": str(e)
        })


def _sanitize_task_keys(yaml_text: str) -> str:
    """Garante que TODA chave de task no topo seja um identificador YAML válido:
    remove crases (`` `nome`: `` -> `nome:`), translitera acento e troca espaço/':' por '_'
    (o `T-005-001: Edição...:` que invalidava o yaml.safe_load do ws-server). Só reescreve
    linhas de chave que PRECISAM — não toca em valores indentados nem em chaves já limpas."""
    import re as _re
    import unicodedata as _ud
    out = []
    for ln in yaml_text.split("\n"):
        if ln[:1] in (" ", "\t", "#", "-", ""):
            out.append(ln)
            continue
        m = _re.match(r'^\s*`?\s*(.+?)\s*`?\s*:\s*$', ln)
        if m:
            raw = m.group(1)
            key = _ud.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")
            key = _re.sub(r'[^A-Za-z0-9_]+', '_', key).strip('_').lower()
            if key and ln.strip() != f"{key}:":
                out.append(f"{key}:")
                continue
        out.append(ln)
    return "\n".join(out)


def _inject_traceability(chunk: str, task: dict) -> str:
    """Injeta DETERMINISTICAMENTE um bloco `traceability: {uc, fr}` logo após a linha
    `task_name:` do YAML, a partir do UC/RF Relacionado extraído do ATS. Rastreabilidade
    requisito→UC no artefato downstream (o ws-server ignora a chave extra em TASKS_CONFIG)."""
    ucs = task.get("uc_related") or []
    frs = task.get("fr_related") or []
    if not ucs and not frs:
        return chunk
    def _yaml_val(items):
        items = [str(x) for x in items]
        return items[0] if len(items) == 1 else "[" + ", ".join(items) + "]"
    lines = ["  traceability:"]
    if ucs:
        lines.append(f"    uc: {_yaml_val(ucs)}")
    if frs:
        lines.append(f"    fr: {_yaml_val(frs)}")
    block = "\n".join(lines)
    out = chunk.split("\n")
    for i, ln in enumerate(out):
        # primeira linha que abre a task (ex.: "consultar_regramentos:") — sem indentação, termina em ':'
        if ln and not ln.startswith((" ", "\t")) and ln.rstrip().endswith(":"):
            out.insert(i + 1, block)
            return "\n".join(out)
    return block + "\n" + chunk  # fallback


async def _generate_task_by_task(
    task_blocks: list,
    tables: dict,
    custom_instructions: Optional[str],
    ats_md: str = "",
):
    """
    Gera 1 task por chamada LLM, com sub-schema focado e retry.
    Retorna (chunks, stats).
    """
    chunks = []
    # De quem cada tarefa recebe dado, lido do ATS. O programa escreve isso na entrada da tarefa
    # porque pedir ao modelo não bastou (0 de 45 obedeceram).
    dependencias = _dependencias_do_ats(ats_md)
    print(f"[TASKS_YAML] dependências declaradas no ATS: {len(dependencias)} tarefa(s)")
    stats = {"total": len(task_blocks), "ok": 0, "retried": 0, "failed": 0, "with_sql": 0}

    for idx, task in enumerate(task_blocks, 1):
        task_name = task.get("name", f"task_{idx}")
        picked = select_relevant_tables(task, tables)
        sub_schema = build_sub_schema(picked, tables)
        pers = needs_persistence(task)

        print(f"[TASKS_YAML] [{idx}/{stats['total']}] {task_name} persist={pers} tables={picked}")

        result = await _generate_one_task_with_retry(task, sub_schema, pers, custom_instructions,
                                                     dependencias)

        if result is None:
            stats["failed"] += 1
            print(f"[TASKS_YAML]   ❌ {task_name} failed after retry")
            continue

        chunk, was_retried = result
        chunks.append(chunk)
        if was_retried:
            stats["retried"] += 1
        stats["ok"] += 1
        if any(op in chunk for op in ("INSERT INTO", "UPDATE ", "DELETE FROM")):
            stats["with_sql"] += 1

    return chunks, stats


async def _generate_one_task_with_retry(
    task: dict,
    sub_schema: str,
    persistence: bool,
    custom_instructions: Optional[str],
    dependencias: Optional[dict] = None,
):
    """
    Gera + valida + retenta 1x. Retorna (yaml_chunk, was_retried) ou None.
    """
    task_name = task.get("name", "")

    # Attempt 1
    prompt = build_single_task_prompt(task, sub_schema, persistence)
    if custom_instructions:
        prompt = f"{prompt}\n\n## INSTRUÇÕES ADICIONAIS DO USUÁRIO\n{custom_instructions}"

    raw = await get_llm_response_async(
        prompt=prompt,
        system="Você é especialista em CrewAI e YAML. Gere APENAS um bloco YAML de task.",
        temperature=0.2,
        max_tokens=3500,
    )
    chunk = extract_task_block(task_name, raw or "")
    chunk = _escrever_procedencia(chunk, task_name, (dependencias or {}).get(task_name) or [])
    ok, reason = validate_task_yaml(task_name, chunk, persistence)
    if ok:
        return chunk, False

    print(f"[TASKS_YAML]   ⚠️ attempt 1 failed: {reason} — retrying")

    # Attempt 2 with explicit hint
    prompt2 = build_single_task_prompt(task, sub_schema, persistence, retry_hint=reason)
    raw2 = await get_llm_response_async(
        prompt=prompt2,
        system="Você é especialista em CrewAI e YAML. Gere APENAS um bloco YAML de task.",
        temperature=0.1,
        max_tokens=3500,
    )
    chunk2 = extract_task_block(task_name, raw2 or "")
    chunk2 = _escrever_procedencia(chunk2, task_name, (dependencias or {}).get(task_name) or [])
    ok2, reason2 = validate_task_yaml(task_name, chunk2, persistence)
    if ok2:
        return chunk2, True

    # TERCEIRA TENTATIVA quando o que falta são OS PASSOS. A lógica já está escrita na descrição
    # que veio do documento de Agentes e Tarefas — é transcrição, não invenção; insistir resolve.
    if "steps" in (reason2 or ""):
        print(f"[TASKS_YAML]   ⚠️ attempt 2 sem steps: {reason2} — 3ª tentativa")
        prompt3 = build_single_task_prompt(
            task, sub_schema, persistence,
            retry_hint=("VOCÊ ESQUECEU `steps:` DE NOVO. Não invente nada: pegue os itens "
                        "numerados de `Process steps` da descrição e transcreva CADA UM como um "
                        "passo, na ordem, usando os tipos permitidos. O YAML é RECUSADO sem isso."))
        raw3 = await get_llm_response_async(
            prompt=prompt3,
            system="Você é especialista em CrewAI e YAML. Gere APENAS um bloco YAML de task.",
            temperature=0.0,
            max_tokens=3500,
        )
        chunk3 = extract_task_block(task_name, raw3 or "")
        chunk3 = _escrever_procedencia(chunk3, task_name, (dependencias or {}).get(task_name) or [])
        ok3, reason3 = validate_task_yaml(task_name, chunk3, persistence)
        if ok3:
            return chunk3, True
        chunk2, reason2 = (chunk3 or chunk2), reason3

    # Nem depois das tentativas: a tarefa ENTRA (senão some do aplicativo), mas SÓ se o bloco
    # for YAML legível. Medido em 23/09/2026: um bloco com uma frase contendo dois-pontos entrou
    # por esta porta e deixou o arquivo INTEIRO ilegível — 45 tarefas perdidas por causa de uma.
    # Tenta-se o melhor bloco disponível, da última tentativa para a primeira.
    import yaml as _yaml_saida
    for _cand, _mot in ((chunk2, reason2), (chunk, reason)):
        if not (_cand and task_name in _cand and "description:" in _cand):
            continue
        try:
            _yaml_saida.safe_load(_cand)
        except Exception as _e:
            print(f"[TASKS_YAML]   ⛔ bloco de {task_name} descartado (não é YAML legível): "
                  f"{str(_e)[:80]}")
            continue
        print(f"[TASKS_YAML]   ❌ {task_name} entrou INCOMPLETA: {_mot}")
        return _cand, True

    print(f"[TASKS_YAML]   ⛔ {task_name} FICOU DE FORA — nenhuma tentativa devolveu YAML legível")
    return None


def _garantir_arquivo_legivel(conteudo: str) -> str:
    """O arquivo que sai da etapa TEM de abrir. Um bloco malformado tornava o tasks.yaml inteiro
    ilegível — 45 tarefas perdidas por causa de uma. Aqui, se o arquivo não abre, os blocos são
    conferidos um a um e o que não abre é retirado, dito pelo nome."""
    import re as _re
    import yaml as _y
    try:
        _y.safe_load(conteudo)
        return conteudo
    except Exception as _e:
        print(f"[TASKS_YAML] ⛔ arquivo não abre ({str(_e)[:90]}) — conferindo bloco a bloco")
    linhas = conteudo.split("\n")
    cabecas = [i for i, l in enumerate(linhas) if _re.match(r"^[A-Za-z_]\w*:\s*$", l)]
    blocos = []
    for k, ini in enumerate(cabecas):
        fim = cabecas[k + 1] if k + 1 < len(cabecas) else len(linhas)
        blocos.append((linhas[ini].rstrip(":"), "\n".join(linhas[ini:fim])))
    bons, ruins = [], []
    for nome, txt in blocos:
        try:
            _y.safe_load(txt)
            bons.append(txt)
        except Exception:
            ruins.append(nome)
    if ruins:
        print(f"[TASKS_YAML] ⛔ retirada(s) por não abrir: {', '.join(ruins)}")
    saida = "\n".join(bons)
    try:
        _y.safe_load(saida)
    except Exception as _e2:
        print(f"[TASKS_YAML] ⛔ mesmo assim não abre: {str(_e2)[:90]}")
    return saida


def _dependencias_do_ats(ats_md: str) -> dict:
    """Mapa {nome_da_tarefa: [tarefas de quem ela recebe dado]}, lido do ATS.

    O ATS já declara isso: cada tarefa tem cabeçalho "#### T-CAS-002: encerrar_caso" e a linha
    "| **Dependencies** | T-CAS-001 |". A informação não era levada ao tasks.yaml, e por isso a
    Rede de Petri não sabia quem alimenta quem — desenhava em paralelo o que era sequencial.

    O padrão do framework (framework/tasks.yaml, TropicalSales) exige a procedência escrita na
    entrada da tarefa. Pedir isso ao modelo não bastou: medido em 22/09/2026, com a regra no
    prompt, ZERO das 45 tarefas nomearam a produtora. Então quem escreve é o programa.
    """
    import re as _re
    texto = ats_md or ""
    id_para_nome = dict(_re.findall(r"####\s*(T-[A-Z]+-\d+)\s*:\s*([a-z][a-z0-9_]{2,60})", texto))
    depende = {}
    for m in _re.finditer(r"####\s*(T-[A-Z]+-\d+)\s*:\s*([a-z][a-z0-9_]{2,60})(.*?)(?=\n####|\Z)",
                          texto, _re.S):
        tid, nome, bloco = m.group(1), m.group(2), m.group(3)
        m_dep = _re.search(r"\*\*(?:Dependencies|Depend[êe]ncias|Depende)\*\*\s*\|\s*([^|\n]+)", bloco)
        if not m_dep:
            continue
        alvos = []
        for ref in _re.findall(r"T-[A-Z]+-\d+", m_dep.group(1)):
            alvo = id_para_nome.get(ref)
            if alvo and alvo != nome and alvo not in alvos:
                alvos.append(alvo)
        if alvos:
            depende[nome] = alvos
    return depende


def _escrever_procedencia(chunk: str, task_name: str, produtoras: list) -> str:
    """Escreve na entrada da tarefa de quem ela recebe dado, no formato do framework.

    Se a tarefa não tem a seção `Input data format`, ela é CRIADA — antes de `Process steps`, ou
    no fim da descrição. Sem isso, 14 das 38 tarefas com dependência declarada ficavam de fora só
    porque o modelo não escreveu a seção (medido em 22/09/2026: 24 de 38).
    """
    if not chunk or not produtoras or "JSON da task" in chunk:
        return chunk
    import re as _re
    linhas = chunk.splitlines()

    def _linhas_de_procedencia(recuo):
        return [f"{recuo}  - JSON da task {p} contendo os campos que ela entrega" for p in produtoras]

    for i, l in enumerate(linhas):
        if _re.match(r"\s*Input data format\s*:", l):
            recuo = l[: len(l) - len(l.lstrip())]
            return "\n".join(linhas[: i + 1] + _linhas_de_procedencia(recuo) + linhas[i + 1:])

    # não havia a seção: criar antes de "Process steps"
    for i, l in enumerate(linhas):
        if _re.match(r"\s*Process steps\s*:", l):
            recuo = l[: len(l) - len(l.lstrip())]
            bloco = [f"{recuo}Input data format:"] + _linhas_de_procedencia(recuo) + [""]
            return "\n".join(linhas[:i] + bloco + linhas[i:])

    # nem isso: pendurar no fim da descrição (antes de expected_output)
    for i, l in enumerate(linhas):
        if _re.match(r"\s*expected_output\s*:", l):
            recuo = "    "
            bloco = [f"{recuo}Input data format:"] + _linhas_de_procedencia(recuo) + [""]
            return "\n".join(linhas[:i] + bloco + linhas[i:])
    return chunk


async def _fallback_single_shot(
    agent_task_spec_document: str,
    custom_instructions: Optional[str],
    data_model_schema_sql: str,
) -> str:
    """Original monolithic prompt — used when chunked path can't recover."""
    prompt = get_tasks_yaml_prompt(
        agent_task_spec_document,
        custom_instructions or "",
        data_model_schema_sql=data_model_schema_sql,
    )
    return await get_llm_response_async(
        prompt=prompt,
        system="Você é um especialista em CrewAI e geração de arquivos YAML.",
        temperature=0.3,
        max_tokens=16000,
    )


# ═══════════════════════════════════════════════════════════
# GET SESSION
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}")
async def get_session(session_id: str):
    """
    Retorna dados da sessão (usado para polling)
    """
    session = get_tasks_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return session


# ═══════════════════════════════════════════════════════════
# LIST SESSIONS
# ═══════════════════════════════════════════════════════════

@router.get("/")
async def list_sessions(project_id: str):
    """
    Lista todas as sessões de tasks.yaml de um projeto
    """
    sessions = list_tasks_yaml_sessions(project_id)
    return {
        "sessions": sessions,
        "total": len(sessions)
    }


# ═══════════════════════════════════════════════════════════
# REFINAMENTO
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/refine")
async def refine_tasks_yaml(
    session_id: str,
    request: RefineRequest,
    background_tasks: BackgroundTasks
):
    """
    Refina tasks.yaml via chat (ASYNC)
    """
    session = get_tasks_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    if not session.get("tasks_yaml_content"):
        raise HTTPException(status_code=400, detail="Nenhum YAML para refinar")

    # Salvar mensagem do usuário
    save_tasks_yaml_chat_message({
        "session_id": session_id,
        "sender_type": "user",
        "message_text": request.message,
        "message_type": "chat"
    })

    # Background task
    background_tasks.add_task(
        execute_tasks_yaml_refinement,
        session_id,
        request.message
    )

    return {
        "status": "refining",
        "message": "Refinamento iniciado"
    }



# ═══════════════════════════════════════════════════════════
# REFINO CIRÚRGICO — só as tarefas citadas no pedido
# ═══════════════════════════════════════════════════════════

def _blocos_de_tarefa(texto: str) -> dict:
    """Recorta o texto em blocos por tarefa (a chave de primeiro nível e tudo que vem abaixo)."""
    import re as _re
    corpo = texto
    cerca = _re.search(r"```(?:ya?ml)?\s*\n(.*?)\n```", texto, _re.S)
    if cerca:
        corpo = cerca.group(1)
    pontos = [(m.start(), m.group(1)) for m in _re.finditer(r"(?m)^([a-z][a-z0-9_]*):\s*$", corpo)]
    blocos = {}
    for i, (ini, nome) in enumerate(pontos):
        fim = pontos[i + 1][0] if i + 1 < len(pontos) else len(corpo)
        blocos[nome] = corpo[ini:fim]
    return blocos


def _yaml_valido(texto: str):
    """(ok, erro) — o texto é YAML que abre? Evita gravar documento cortado no meio."""
    import re as _re
    import yaml as _yaml
    corpo = texto
    cerca = _re.search(r"```(?:ya?ml)?\s*\n(.*?)\n```", texto, _re.S)
    if cerca:
        corpo = cerca.group(1)
    try:
        d = _yaml.safe_load(corpo)
        if not isinstance(d, dict) or not d:
            return False, "o conteúdo não é um mapa de tarefas"
        return True, ""
    except Exception as e:  # noqa: BLE001
        return False, str(e).split("\n")[0][:200]


def _tarefas_citadas(pedido: str, blocos: dict) -> list:
    """Quais tarefas o pedido menciona pelo nome."""
    baixo = (pedido or "").lower()
    return [n for n in blocos if n.lower() in baixo]

async def execute_tasks_yaml_refinement(session_id: str, user_message: str):
    """
    Background: Refina tasks.yaml com contexto completo
    Baseado em execute_refinement() de agent_task_spec.py
    """
    try:
        import re
        import time

        # 1. ATUALIZAR STATUS PARA 'GENERATING'
        update_tasks_yaml_session(session_id, {
            "status": "generating"
        })

        # 2. BUSCAR SESSÃO ATUAL
        session = get_tasks_yaml_session(session_id)
        if not session:
            raise Exception(f"Sessão {session_id} não encontrada")

        current_yaml = session.get("tasks_yaml_content", "")

        # 3. BUSCAR DOCUMENTO MD BASE (ESPECIFICAÇÃO DE AGENTES/TAREFAS)
        agent_task_spec_document = ""
        if session.get("agent_task_spec_session_id"):
            from app.database import get_db_connection
            with get_db_connection() as db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("""
                    SELECT agent_task_spec_document
                    FROM agent_task_specification_sessions
                    WHERE id = %s
                    LIMIT 1
                """, (session["agent_task_spec_session_id"],))
                spec_result = cursor.fetchone()
                cursor.close()

                if spec_result:
                    agent_task_spec_document = spec_result.get("agent_task_spec_document", "")

        # 4. BUSCAR REFINAMENTOS ANTERIORES (HISTÓRICO)
        from app.database import get_previous_tasks_yaml_refinements

        previous_refinements = get_previous_tasks_yaml_refinements(session_id, limit=10)

        # Formatar histórico
        refinement_history = ""
        if previous_refinements:
            refinement_history = "\n## REFINAMENTOS ANTERIORES:\n"
            for idx, ref in enumerate(previous_refinements, 1):
                refinement_history += f"\n**Refinamento {idx}:**\n{ref['message_text']}\n"

        # 5. SALVAR MENSAGEM DE PROGRESSO
        save_tasks_yaml_chat_message({
            "session_id": session_id,
            "sender_type": "system",
            "message_text": "🔄 Processando refinamento...",
            "message_type": "progress"
        })

        # 6. REFINO CIRÚRGICO — só as tarefas citadas no pedido.
        #
        # DEFEITO QUE ISTO CORRIGE (13/09/2026): o refino mandava REESCREVER O DOCUMENTO INTEIRO
        # com teto de 16 mil tokens. O contrato do BioByte tem 93 mil caracteres (~30 mil tokens):
        # a resposta vinha CORTADA no meio de uma frase, e era gravada assim, como nova versão,
        # com a mensagem "refinado com sucesso". O contrato de passos das 14 tarefas — o que impede
        # a lógica de sumir — ia junto. Agora reescreve-se só o que foi pedido, e confere-se antes
        # de gravar.
        blocos = _blocos_de_tarefa(current_yaml)
        alvos = _tarefas_citadas(user_message, blocos)
        start_time = time.time()
        falhas = []

        if alvos and len(alvos) < len(blocos):
            print(f"[TASKS_YAML_REFINE] 🎯 cirúrgico em {len(alvos)} de {len(blocos)} tarefas: {', '.join(alvos)}")
            refined_yaml = current_yaml
            for nome in alvos:
                pedido_tarefa = f"""# REFINAMENTO DE UMA TAREFA DO TASKS.YAML

Abaixo está UMA tarefa do arquivo de tarefas. Aplique NELA a parte do pedido que lhe diz respeito.

## TAREFA ATUAL

```yaml
{blocos[nome]}
```

## PEDIDO DO USUÁRIO (aplique só a parte que é desta tarefa)

{user_message}

## REGRAS

1. Devolva a tarefa COMPLETA, do nome dela até o fim, em YAML válido.
2. NÃO mude o nome da tarefa nem remova campos existentes (traceability, execution, agent,
   description, expected_output, steps). Se ela tem `steps:`, devolva os passos INTEIROS.
3. Mexa APENAS no que o pedido determina. O resto fica idêntico, caractere por caractere.
4. Sem preâmbulo, sem explicação, sem cerca de código. Só o YAML da tarefa.
"""
                bloco_novo = await get_llm_response_async(
                    prompt=pedido_tarefa,
                    system="Você é um especialista em CrewAI e configuração de tarefas.",
                    temperature=0.2,
                    max_tokens=16000,
                )
                import re as _re
                _c = _re.search(r"```(?:ya?ml)?\s*\n(.*?)\n```", bloco_novo or "", _re.S)
                bloco_novo = (_c.group(1) if _c else (bloco_novo or "")).strip("\n")
                ok, erro = _yaml_valido(bloco_novo)
                tinha_passos = "steps:" in blocos[nome]
                if not ok:
                    falhas.append(f"{nome}: resposta não é YAML válido ({erro})")
                    continue
                if tinha_passos and "steps:" not in bloco_novo:
                    falhas.append(f"{nome}: a resposta perdeu o contrato de passos — descartada")
                    continue
                if not bloco_novo.lstrip().startswith(f"{nome}:"):
                    falhas.append(f"{nome}: a resposta não começa pela própria tarefa — descartada")
                    continue
                refined_yaml = refined_yaml.replace(blocos[nome], bloco_novo + "\n")
                print(f"[TASKS_YAML_REFINE]   ✓ {nome}: {len(blocos[nome])} → {len(bloco_novo)} caracteres")
        else:
            # Pedido que não nomeia tarefa: reescreve tudo, mas com teto proporcional ao tamanho.
            teto = max(16000, min(60000, int(len(current_yaml) / 2.5) + 4000))
            print(f"[TASKS_YAML_REFINE] documento inteiro, teto de {teto} tokens para {len(current_yaml)} caracteres")
            refinement_prompt = f"""# REFINAMENTO DE TASKS.YAML CREWAI

Você é um especialista em CrewAI e configuração de tarefas.

## TASKS.YAML ATUAL

{current_yaml}

## ESPECIFICAÇÃO DE AGENTES/TAREFAS (REFERÊNCIA - NÃO REPRODUZA)

{agent_task_spec_document[:15000] if agent_task_spec_document else "Não disponível"}

{refinement_history}

## SOLICITAÇÃO DE REFINAMENTO

{user_message}

## INSTRUÇÕES CRÍTICAS

1. Preserve a estrutura YAML existente e os nomes das tarefas.
2. Aplique APENAS as mudanças pedidas; o resto fica idêntico.
3. Se uma tarefa tem `steps:`, devolva os passos INTEIROS.
4. Retorne o tasks.yaml COMPLETO, sem preâmbulo nem explicação.
"""
            refined_yaml = await get_llm_response_async(
                prompt=refinement_prompt,
                system="Você é um especialista em CrewAI e configuração de tarefas.",
                temperature=0.3,
                max_tokens=teto,
            )

        generation_time_ms = int((time.time() - start_time) * 1000)
        print(f"[TASKS_YAML_REFINE] ✅ {len(refined_yaml)} chars em {generation_time_ms/1000:.1f}s")

        # 7. PORTÃO: documento cortado ou quebrado NÃO é gravado.
        ok, erro = _yaml_valido(refined_yaml)
        if not ok:
            raise Exception(
                f"o refino devolveu documento inválido ({erro}) — a versão anterior foi mantida"
            )
        antes, depois = len(_blocos_de_tarefa(current_yaml)), len(_blocos_de_tarefa(refined_yaml))
        if depois < antes:
            raise Exception(
                f"o refino devolveu {depois} tarefas e o documento tinha {antes} — "
                "a versão anterior foi mantida"
            )
        passos_antes = current_yaml.count("steps:")
        if passos_antes and refined_yaml.count("steps:") < passos_antes:
            raise Exception(
                f"o refino perdeu contrato de passos ({refined_yaml.count('steps:')} de "
                f"{passos_antes}) — a versão anterior foi mantida"
            )

        # 8. CONTAR TASKS
        task_matches = re.findall(r'^[a-z_]+:', refined_yaml, re.MULTILINE)
        total_tasks = len([t for t in task_matches if not t.startswith(('description:', 'expected_output:'))])

        # 9. BUSCAR PRÓXIMA VERSÃO
        versions = get_tasks_yaml_versions(session_id)
        current_version = max([v["version"] for v in versions]) if versions else 0
        new_version = current_version + 1

        # 10. ATUALIZAR SESSÃO
        update_tasks_yaml_session(session_id, {
            "tasks_yaml_content": refined_yaml,
            "total_tasks": total_tasks,
            "status": "completed",
            "finished_at": datetime.now(),
            "generation_time_ms": generation_time_ms
        })

        # 11. CRIAR NOVA VERSÃO
        create_tasks_yaml_version({
            "session_id": session_id,
            "version": new_version,
            "tasks_yaml_content": refined_yaml,
            "created_by": None,
            "change_type": "ai_refinement",
            "change_description": user_message[:500],
            "doc_size": len(refined_yaml)
        })

        print(f"[TASKS_YAML_REFINE] 📦 Versão {new_version} criada: {total_tasks} tarefas")

        # 12. SALVAR MENSAGEM DE SUCESSO
        save_tasks_yaml_chat_message({
            "session_id": session_id,
            "sender_type": "agent",
            "message_text": (
                f"✅ YAML refinado com sucesso!\n\n📊 {total_tasks} tarefas.\n"
                f"📌 Versão {new_version} criada."
                + ("\n\n⚠️ O que NÃO foi aplicado:\n- " + "\n- ".join(falhas) if falhas else "")
            ),
            "message_type": "result"
        })

    except Exception as e:
        # SALVAR ERRO
        print(f"[TASKS_YAML_REFINE] ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

        update_tasks_yaml_session(session_id, {
            "status": "failed",
            "finished_at": datetime.now()
        })
        # O erro precisa APARECER na conversa. Antes ele só ia para o registro do servidor e a
        # tela ficava girando — quem pediu a correção não sabia que ela tinha sido recusada.
        try:
            save_tasks_yaml_chat_message({
                "session_id": session_id,
                "sender_type": "agent",
                "message_text": f"❌ O refinamento NÃO foi aplicado: {str(e)}",
                "message_type": "result",
            })
        except Exception:  # noqa: BLE001
            pass


# ═══════════════════════════════════════════════════════════
# RESTAURAR VERSÃO
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/restore/{version}")
async def restore_tasks_yaml_version(session_id: str, version: int):
    """Torna VIGENTE uma versão do histórico.

    Antes disto, escolher uma versão no histórico só trocava o que aparecia na tela: o conteúdo
    vigente continuava sendo o da última alteração, e o refino seguinte partia dele. Quando um
    refino estragava o documento (13/09/2026: resposta cortada gravada como boa), não havia como
    voltar pela interface. A etapa da Rede de Petri já tinha isso; esta não.
    """
    session = get_tasks_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    versoes = get_tasks_yaml_versions(session_id) or []
    alvo = next((v for v in versoes if int(v.get("version") or 0) == int(version)), None)
    if not alvo or not alvo.get("tasks_yaml_content"):
        raise HTTPException(status_code=404, detail=f"Versão {version} não encontrada")
    conteudo = alvo["tasks_yaml_content"]
    ok, erro = _yaml_valido(conteudo)
    if not ok:
        raise HTTPException(status_code=400, detail=f"A versão {version} está quebrada ({erro})")
    nova = max([int(v.get("version") or 0) for v in versoes]) + 1
    update_tasks_yaml_session(session_id, {
        "tasks_yaml_content": conteudo,
        "total_tasks": len(_blocos_de_tarefa(conteudo)),
        "status": "completed",
        "finished_at": datetime.now(),
    })
    create_tasks_yaml_version({
        "session_id": session_id,
        "version": nova,
        "tasks_yaml_content": conteudo,
        "created_by": None,
        # A coluna aceita uma lista fechada de tipos e 'restore' não está nela; a restauração é
        # uma edição deliberada do usuário sobre o documento vigente.
        "change_type": "manual_edit",
        "change_description": f"restaurada a versão {version}",
        "doc_size": len(conteudo),
    })
    save_tasks_yaml_chat_message({
        "session_id": session_id,
        "sender_type": "agent",
        "message_text": f"♻️ Versão {version} restaurada como vigente (gravada como versão {nova}).",
        "message_type": "result",
    })
    return {"status": "restored", "de": version, "nova_versao": nova, "tamanho": len(conteudo)}


# ═══════════════════════════════════════════════════════════
# REVISÃO (REVIEW)
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/review")
async def review_tasks_yaml(
    session_id: str
):
    """
    Revisa tasks.yaml e retorna sugestões (SÍNCRONO - sem autenticação para evitar expiração)
    """
    session = get_tasks_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    if not session.get("tasks_yaml_content"):
        raise HTTPException(status_code=400, detail="Nenhum YAML para revisar")

    try:
        print(f"[TASKS_YAML_REVIEW] Session {session_id}")

        # Prompt de revisão
        prompt = get_review_tasks_yaml_prompt(session["tasks_yaml_content"])

        suggestions = await get_llm_response_async(
            prompt=prompt,
            system="Você é um especialista em análise de tasks.yaml CrewAI.",
            temperature=0.7,
            max_tokens=4096
        )

        # Salvar mensagem de revisão
        review_msg_id = str(uuid.uuid4())
        save_tasks_yaml_chat_message({
            "id": review_msg_id,
            "session_id": session_id,
            "sender_type": "agent",
            "message_text": suggestions,
            "message_type": "chat"
        })

        print(f"[TASKS_YAML_REVIEW] ✅ Review completed")

        return {
            "review_message_id": review_msg_id,
            "suggestions": suggestions,
            "status": "success",
            "message": "Revisão concluída"
        }

    except Exception as e:
        print(f"[TASKS_YAML_REVIEW] ❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# VERSÕES
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}/versions")
async def get_versions(session_id: str):
    """
    Lista todas as versões de tasks.yaml
    """
    versions = get_tasks_yaml_versions(session_id)
    return {
        "versions": versions,
        "total": len(versions)
    }


# ═══════════════════════════════════════════════════════════
# CHAT HISTORY
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}/chat-history")
async def get_chat_history(session_id: str):
    """
    Retorna histórico de chat
    """
    messages = get_tasks_yaml_chat_messages(session_id)
    return {
        "messages": messages,
        "total": len(messages)
    }


# ─────────────── ESTRUTURAR PASSOS (tradutor de regras) ───────────────
#
# A descrição de cada tarefa mistura passos de banco com passos de regra em prosa; o gerador de
# código só traduz com garantia o que está em `steps:` (tipos fechados + mini-linguagem). Esta
# ação pede ao agente a conversão da prosa em `steps:`, VALIDA cada passo e cada expressão ANTES
# de gravar, guarda uma versão nova do YAML e devolve, por tarefa, o que entrou e o que voltou
# para o usuário refinar. Mesmo padrão das outras etapas: gerar → refinar → aprovar.

class EstruturarRequest(BaseModel):
    apenas_tarefas: Optional[List[str]] = None   # restringe a algumas tarefas; ausente = todas sem steps


def _ferramentas_resolvidas_do_projeto(project_id: str) -> Optional[dict]:
    """Ferramentas com implementação declarada na etapa Ferramentas: nome -> argumentos aceitos
    (a ferramenta MCP declara a entrada; a da biblioteca não restringe -> None)."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT tools_json FROM tool_sessions WHERE project_id=%s "
                        "ORDER BY (approval_status='approved') DESC, created_at DESC LIMIT 1", (project_id,))
            row = cur.fetchone(); cur.close()
        if not row or not row.get("tools_json"):
            return None
        doc = json.loads(row["tools_json"])
        # só o que TEM código: biblioteca do gerador e MCP. Ferramenta "determinística" da etapa
        # é regra declarada ainda sem implementação — não serve de alvo para `externo`.
        return {t["nome"]: {"argumentos": list(t.get("entrada") or []), "saida": list(t.get("saida") or [])}
                for t in doc.get("tools", []) if t.get("resolvida") and t.get("origem") in ("biblioteca", "mcp")}
    except Exception:
        return None


def _resumo_modelo_de_dados(project_id: str) -> str:
    """Tabelas e colunas do DDL aprovado, compactas, para o agente escrever SQL que existe."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT schema_sql FROM data_model_sessions WHERE project_id=%s "
                        "AND schema_sql IS NOT NULL AND CHAR_LENGTH(schema_sql)>0 "
                        "ORDER BY created_at DESC LIMIT 1", (project_id,))
            row = cur.fetchone(); cur.close()
    except Exception:
        return ""
    ddl = (row or {}).get("schema_sql") or ""
    linhas = []
    for m in re.finditer(r"(?is)create\s+table\s+(?:if\s+not\s+exists\s+)?`?(\w+)`?\s*\((.*?)\)\s*(?:engine|comment|;|$)", ddl):
        cols = []
        for l in m.group(2).splitlines():
            l = l.strip().rstrip(",")
            if not l or re.match(r"(?i)^(primary|foreign|unique|key|index|constraint|check)\b", l):
                continue
            cols.append(l.split()[0].strip("`"))
        if cols:
            linhas.append(f"{m.group(1)}({', '.join(cols)})")
    return "; ".join(linhas)[:3000]


def _ui_spec_do_projeto(project_id: str) -> dict:
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT ui_spec_json FROM ui_spec_sessions WHERE project_id=%s "
                        "ORDER BY created_at DESC LIMIT 1", (project_id,))
            row = cur.fetchone(); cur.close()
        ui = (row or {}).get("ui_spec_json") or "{}"
        return json.loads(ui) if isinstance(ui, str) else (ui or {})
    except Exception:
        return {}


def _entradas_disponiveis_por_tarefa(tarefas: dict, ui_spec: dict, ddl: str) -> dict:
    """Para cada tarefa, os nomes que ela PODE ler: campos das telas que a disparam, identificadores
    do contexto corrente (<tabela>_id) e dados de sistema (usuario_id, ip_origem). Tarefa que nenhuma
    tela dispara (vem do fluxo) recebe os campos de todas as telas. É a lista que o agente vê e que
    a validação cobra — acaba com `micro_id` inventado quando a tela manda `microbiologia_id`."""
    try:
        from agents import langnetagents as _la
        tf = {n: _la._parse_task_input_fields((c or {}).get("description", "") or "")
              for n, c in tarefas.items() if isinstance(c, dict)}
        try:
            _la._TASK_UCS.clear()
            for n, c in tarefas.items():
                if isinstance(c, dict):
                    _uc = ((c.get("traceability") or {}).get("uc") or [])
                    _la._TASK_UCS[n] = list(_uc) if isinstance(_uc, list) else [str(_uc)]
        except Exception:
            pass
        resolver = _la._resolve_task_target
    except Exception:
        tf, resolver = {}, None
    ids = {"usuario_id", "ip_origem"}
    for m in re.finditer(r"(?is)create\s+table\s+(?:if\s+not\s+exists\s+)?`?(\w+)`?", ddl or ""):
        t = m.group(1).lower()
        sing = t[:-1] if t.endswith("s") else t
        ids |= {f"{t}_id", f"{sing}_id"}
    todos_campos = set()
    por_tarefa: dict = {}
    for scr in (ui_spec or {}).get("screens") or []:
        campos = {c.get("field") for c in (scr.get("components") or []) if c.get("field")}
        todos_campos |= campos
        for a in scr.get("actions") or []:
            if a.get("kind") != "task" or not a.get("target"):
                continue
            alvo = None
            if resolver:
                try:
                    alvo = resolver(a["target"], tf, scr.get("name"), screen_ucs=scr.get("uc"),
                                    entity=scr.get("entity"), kind="task")
                except Exception:
                    alvo = None
            if alvo in tarefas:
                por_tarefa.setdefault(alvo, set()).update(campos)
    saida = {}
    for n in tarefas:
        base = por_tarefa.get(n)
        saida[n] = (set(base) if base else set(todos_campos)) | ids
    return saida


_BD_CONFERENCIA = {}


def _conferir_sql_no_modelo(steps: list, ddl: str) -> list:
    """Roda EXPLAIN de cada SQL do contrato num banco TEMPORÁRIO criado do DDL aprovado (mesmo
    servidor do LangNet): sintaxe, tabela e coluna erradas aparecem aqui, não na mão do operador.
    Parâmetros recebem valor fictício 1 (EXPLAIN não executa). Erros de restrição (FK, NOT NULL,
    duplicidade) não são erro do SQL e são ignorados."""
    if not ddl or not steps:
        return []
    import hashlib
    nome_bd = "langnet_chk_" + hashlib.sha1(ddl.encode("utf-8")).hexdigest()[:10]
    problemas = []
    try:
        import mysql.connector
        from app.config import settings as _st
        cfg = dict(host=getattr(_st, "db_host", "127.0.0.1"), port=int(getattr(_st, "db_port", 3306)),
                   user=getattr(_st, "db_user", ""), password=getattr(_st, "db_password", ""))
        conn = mysql.connector.connect(**cfg)
        cur = conn.cursor()
        if nome_bd not in _BD_CONFERENCIA:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{nome_bd}`")
            cur.execute(f"USE `{nome_bd}`")
            cur.execute("SET FOREIGN_KEY_CHECKS=0")
            cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s", (nome_bd,))
            if (cur.fetchone() or [0])[0] == 0:
                for stmt in [x.strip() for x in re.split(r";\s*\n", ddl) if x.strip()]:
                    if re.match(r"(?is)^\s*(create|alter|set)\b", stmt):
                        try:
                            cur.execute(stmt)
                        except Exception:
                            pass
            conn.commit()
            _BD_CONFERENCIA[nome_bd] = True
        else:
            cur.execute(f"USE `{nome_bd}`")

        def _varre(lista, pre=""):
            for i, p in enumerate(lista or [], 1):
                n = f"{pre}{i}"
                if not isinstance(p, dict):
                    continue
                if p.get("tipo") in ("consulta", "escrita") and isinstance(p.get("sql"), str):
                    sql = p["sql"]
                    params = tuple([1] * sql.count("%s"))
                    if p.get("tipo") == "consulta":
                        _lq = _leque_de_juncao(sql, ddl)
                        if _lq:
                            problemas.append({"passo": n, "motivo": _lq})
                    try:
                        cur.execute("EXPLAIN " + sql, params)
                        cur.fetchall()
                    except Exception as e:
                        msg = str(e)
                        # constrição de dado não é erro de SQL; EXPLAIN de INSERT simples não existe
                        # em toda versão → tenta a execução com rollback só para checar a forma
                        if re.search(r"^1(452|048|062|364|366)\b", msg):
                            pass
                        elif p.get("tipo") == "escrita" and "1064" in msg and re.match(r"(?is)^\s*insert", sql):
                            try:
                                cur.execute("START TRANSACTION"); cur.execute(sql, params); cur.execute("ROLLBACK")
                            except Exception as e2:
                                cur.execute("ROLLBACK")
                                m2 = str(e2)
                                if not re.search(r"^1(452|048|062|364|366|265|292)\b", m2):
                                    problemas.append({"passo": n, "motivo": f"SQL inválido no modelo de dados: {m2[:160]}"})
                        else:
                            problemas.append({"passo": n, "motivo": f"SQL inválido no modelo de dados: {msg[:160]}"})
                if isinstance(p.get("passos"), list):
                    _varre(p["passos"], f"{n}.")
        _varre(steps)
        cur.close(); conn.close()
    except Exception as e:  # noqa: BLE001 — sem banco de conferência, não inventa problema
        print(f"[ESTRUTURAR] conferência de SQL indisponível: {e}")
    return problemas


def _filhas_no_modelo(ddl: str) -> dict:
    """tabela -> conjunto de tabelas-mãe (pela coluna <mae>_id / <mae_singular>_id ou FOREIGN KEY)."""
    tabelas = {}
    for m in re.finditer(r"(?is)create\s+table\s+(?:if\s+not\s+exists\s+)?`?(\w+)`?\s*\((.*?)\)\s*(?:engine|comment|;|$)", ddl or ""):
        tabelas[m.group(1).lower()] = m.group(2)
    maes = {t: set() for t in tabelas}
    for t, corpo in tabelas.items():
        for ref in re.findall(r"(?i)references\s+`?(\w+)`?", corpo):
            if ref.lower() in tabelas and ref.lower() != t:
                maes[t].add(ref.lower())
        for col in re.findall(r"(?im)^\s*`?(\w+)_id`?\s", corpo):
            for cand in (col.lower(), col.lower() + "s", col.lower() + "es"):
                if cand in tabelas and cand != t:
                    maes[t].add(cand)
    return maes


def _leque_de_juncao(sql: str, ddl: str) -> str:
    """Duas ou mais tabelas FILHAS da mesma tabela juntas numa consulta sem GROUP BY/DISTINCT:
    as linhas se multiplicam (N×M por registro-mãe). Devolve a explicação, ou ''."""
    if re.search(r"(?i)\bgroup\s+by\b|\bdistinct\b", sql):
        return ""
    nomes = [m.group(1).lower() for m in re.finditer(r"(?i)\b(?:from|join)\s+`?(\w+)`?", sql)]
    if len(nomes) < 3:
        return ""
    maes = _filhas_no_modelo(ddl)
    for mae in set(nomes):
        filhas = [t for t in set(nomes) if t != mae and mae in maes.get(t, set())]
        if len(filhas) >= 2:
            return (f"junção em leque: {', '.join(sorted(filhas))} são filhas de «{mae}» e entram juntas sem "
                    f"agregação — as linhas se multiplicam (N×M por {mae}). Agregue com GROUP BY ou traga uma "
                    f"linha por {mae} (a mais recente de cada filha, em subconsulta)")
    return ""


def _sanear_passos(steps: list, problemas: list) -> list:
    """Passo que não valida NÃO entra como está: vira `agente` com o passo original e o motivo,
    para o usuário ver e refinar — o contrato nunca grava expressão que não compila."""
    ruins = {p["passo"].split(".")[0] for p in problemas}
    saida = []
    for i, st in enumerate(steps, 1):
        if str(i) in ruins and isinstance(st, dict):
            motivos = "; ".join(p["motivo"] for p in problemas if p["passo"].split(".")[0] == str(i))
            saida.append({"tipo": "agente",
                          "instrucao": f"[NÃO VALIDADO: {motivos}] {json.dumps(st, ensure_ascii=False)[:400]}"})
        else:
            saida.append(st)
    return saida


def _desmarcar(steps: list) -> list:
    """Devolve os passos com os `[NÃO VALIDADO: …] {json}` de volta à forma original (para
    revalidar/reparar); o que não der para ler fica como está."""
    saida = []
    for st in steps or []:
        if isinstance(st, dict) and st.get("tipo") == "agente" and \
                str(st.get("instrucao", "")).startswith("[NÃO VALIDADO"):
            m = re.search(r"\]\s*(\{.*\})\s*$", st["instrucao"], re.S)
            try:
                orig = json.loads(m.group(1)) if m else None
            except Exception:
                orig = None
            saida.append(orig if isinstance(orig, dict) else st)
        else:
            saida.append(st)
    return saida


_GUIA_STEPS = """Você converte a descrição em PROSA de uma tarefa num CONTRATO de passos em JSON.

Tipos permitidos (use exatamente estes nomes de campo):
- {"tipo":"consulta","sql":"SELECT ...","params":["expr",...],"guarda_em":"nome","forma":"escalar|linha|linhas"}
- {"tipo":"escrita","sql":"INSERT/UPDATE/DELETE ...","params":["expr",...]}
- {"tipo":"verificacao","condicao":"expr que PRECISA ser verdadeira para continuar","mensagem":"frase de recusa dada quando ela é falsa"}  (ex.: condicao "existe(paciente)", mensagem "Paciente não encontrado")
  ou {"tipo":"verificacao","recusa_se":"expr que, sendo verdadeira, RECUSA","mensagem":"..."}  (ex.: recusa_se "dados.idade == nulo ou dados.apache_ii == nulo", mensagem "PARAMS_MISSING") — prefira recusa_se quando a prosa diz "se X, recuse"
- {"tipo":"calculo","atribui":"nome","expressao":"expr"}
- {"tipo":"condicao","se":"expr booleana","passos":[...]}
- {"tipo":"laco","para_cada":"item","em":"expr de lista","passos":[...]}
- {"tipo":"externo","ferramenta":"nome_da_tool","argumentos":{"param":"expr"},"guarda_em":"nome","mapeia":{"campo_devolvido":"variavel"}}
- {"tipo":"tarefa","nome":"outra_tarefa_deste_sistema","entrada":{"campo":"expr"},"guarda_em":"nome","mapeia":{...}}  -> orquestração: encadeia OUTRA tarefa determinística (nunca uma de agente)
- {"tipo":"retorno","campos":["nome", "resposta.campo", "usuario.id como usuario_id", ...]}  (`como` dá o nome de saída)
- {"tipo":"agente","instrucao":"o julgamento a fazer, em uma frase","usa":["expr","expr"],"devolve":["nome1","nome2"]}
  -> SÓ quando a tarefa exige JULGAMENTO que não cabe em regra (escolher um pacote de tratamento,
     redigir uma justificativa, classificar por critério subjetivo). REGRA DE OURO: o modelo não
     consulta banco, não aciona ferramenta e não grava nada. Ponha ANTES dele os passos `consulta`
     e `externo` que apuram os dados, liste esses valores em `usa`, e ponha DEPOIS dele os passos
     `escrita` que gravam o que ele respondeu. `devolve` é obrigatório e nomeia exatamente os
     valores que o modelo tem de responder — eles ficam disponíveis para os passos seguintes.
     Ex.: {"tipo":"agente","instrucao":"Escolha o pacote de tratamento adequado e redija a
     justificativa clínica","usa":["microrganismo","multirresistente","valor_escore"],
     "devolve":["bundle_nome","justificativa"]}

Mini-linguagem das expressões: nomes (entradas e variáveis guardadas), acesso a campo (usuario.papel),
+ - * /, == != < <= > >=, e / ou / nao, literais ('texto', 12, verdadeiro, falso, nulo, [lista]) e as funções:
conta_valor(json,'R'), tamanho(x), confere_senha(senha, hash), existe(x), entre(x,a,b), em(x,[...]),
arredonda(x,n), hoje(), dias_entre(a,b), texto(x), numero(x), maiusculas(x), minusculas(x),
contem(texto,parte), soma(lista,campo), media(lista,campo), primeiro(lista), vazio(x),
codigo_valido(codigo, tamanho), json_valido(texto), de_json(texto), hash_senha(senha) (para gravar senha_hash — senha NUNCA em claro),
opcional(nome) (valor da entrada se veio, senão nulo — para filtros
que podem ficar vazios: SQL "(%s IS NULL OR col >= %s)" com params ["opcional(data_inicio)","opcional(data_inicio)"]).
Só leia nomes da lista ENTRADAS DISPONÍVEIS ou produzidos por passo anterior; nunca invente nome
(micro_id, admin_id). Se a prosa espera um COMANDO que a tela não envia (ex.: acao = CRIAR/EDITAR),
derive-o dos campos que a tela envia, com `condicao`: existe(usuario_id) → editar, senão criar; um
campo de status igual a 'Inativo' → desativar. Constantes de retorno ('sucesso') viram `calculo`
(atribui status, expressao 'sucesso') antes do `retorno`. Valores de EXEMPLO da especificação
("ex.: -35", "[-20, -50]") NUNCA viram resultado: resultado se calcula dos dados ou é passo `agente`.
Filtros de consulta (datas, tipo, busca) são opcional(nome) com SQL "(%s IS NULL OR coluna >= %s)". Período sem entrada na tela é literal no SQL (INTERVAL 30 DAY), nunca %s.
Ao encadear resultados para as telas seguintes, devolva identificadores com o nome do contexto
(usuario_id, caso_id, microbiologia_id) usando `como`. Token/JWT SÓ com a ferramenta jwt_tool
(argumentos sub, role, exp_horas; devolve token_jwt) — nunca montado com texto. Arquivo (PDF/CSV) SÓ
com pdf_generator_tool/csv_exporter_tool (data = a lista de linhas consultada, output_path = nome do
arquivo); elas devolvem path e filename — mapeie `path` para `arquivo_gerado` e devolva-o no retorno. Marcador de SQL
é %s (nunca ?).
Nos `params`, cada item é UMA expressão (normalmente o nome de uma entrada, ex.: "email"); a
quantidade de itens deve ser IGUAL à de marcadores %s do SQL — sem marcador, `params` é [].
NUNCA escreva chaves: {campo} da prosa vira apenas campo. Em `externo`, `ferramenta` tem de ser
EXATAMENTE um dos nomes da lista FERRAMENTAS RESOLVIDAS, com os argumentos que ela aceita; se a
prosa diz "chame api_call_tool com a função X" / "service_call_X", o nome genérico NÃO é ferramenta —
use X (se está na lista) ou, se X é outra tarefa deste sistema, o passo `tarefa`. Só é `externo` o
que sai do sistema (laboratório, e-mail, PDF, token); validar código, senha, prazo ou saldo é
`verificacao`/`calculo` com as funções acima. BANCO DE DADOS NUNCA é `externo` (nem database_tool,
nem database_query): banco é `consulta`/`escrita` com o SQL no campo `sql`. Use apenas tabelas e
colunas do MODELO DE DADOS. Argumento de ferramenta: passe o dado com o MESMO significado — nunca
encaixe outro campo só para preencher (uti não é apache_ii); se o sistema não tem o dado, use uma
ENTRADA da tarefa com o nome do argumento e registre isso em `observacao`. Depois de um `externo`,
use os campos que a ferramenta DEVOLVE (via `mapeia` ou resposta.campo) — nunca outro nome; para
conferir se um campo veio preenchido use `resposta.campo != nulo` (contem() só olha texto).
"Notificar" usuários do sistema sem canal externo na lista = registrar na tabela de alertas/
notificações do MODELO (`escrita`); e-mail só com email_sender_tool. Não invente ferramenta.
Um SELECT que precisa de várias colunas usa forma "linha" e depois acessa nome.campo.
Verificações de regra ("validar senha", "se X então recuse") viram `verificacao` com a MENSAGEM que o
caso de uso especifica. Nunca invente valores de exemplo como resultado. Responda SÓ JSON:
{"steps":[...], "observacao": "o que não coube no contrato, se houver"}"""


_ESTRUTURAR_JOBS: dict = {}


@router.post("/{session_id}/estruturar-passos")
def estruturar_passos(session_id: str, req: EstruturarRequest, current_user: dict = Depends(get_current_user)):
    """Dispara a estruturação em segundo plano e devolve um `job_id` para acompanhar.

    A ação chama o agente para cada tarefa com problema (até 3 rodadas) — minutos, às vezes. Como
    chamada única ela caía na mão do navegador ("NetworkError") mesmo com a versão gravada no
    banco; agora a página consulta o andamento e o relatório aparece quando termina."""
    import threading, uuid as _uuid, datetime as _dt
    job_id = str(_uuid.uuid4())
    _ESTRUTURAR_JOBS[job_id] = {"job_id": job_id, "session_id": session_id, "status": "rodando",
                                "inicio": _dt.datetime.utcnow().isoformat()}

    def _rodar():
        try:
            res = _estruturar_passos_impl(session_id, req, current_user)
            _ESTRUTURAR_JOBS[job_id].update({"status": "concluido", "resultado": res})
        except HTTPException as e:
            _ESTRUTURAR_JOBS[job_id].update({"status": "erro", "erro": str(e.detail)})
        except Exception as e:  # noqa: BLE001
            _ESTRUTURAR_JOBS[job_id].update({"status": "erro", "erro": str(e)[:300]})
        _ESTRUTURAR_JOBS[job_id]["fim"] = _dt.datetime.utcnow().isoformat()

    threading.Thread(target=_rodar, daemon=True, name=f"estruturar-{job_id[:8]}").start()
    return {"job_id": job_id, "session_id": session_id, "status": "rodando"}


@router.get("/{session_id}/estruturar-passos/{job_id}")
def estruturar_passos_andamento(session_id: str, job_id: str, current_user: dict = Depends(get_current_user)):
    job = _ESTRUTURAR_JOBS.get(job_id)
    if not job or job.get("session_id") != session_id:
        raise HTTPException(404, "Estruturação não encontrada (o servidor pode ter reiniciado); a versão gravada está no histórico")
    return job


def _estruturar_passos_impl(session_id: str, req: EstruturarRequest, current_user: dict):
    import yaml as _yaml
    from agents.langnetagents import _direct_llm_complete
    from agents.langnetregras import validar_passos

    session = get_tasks_yaml_session(session_id)
    if not session or not session.get("tasks_yaml_content"):
        raise HTTPException(404, "Sessão de tasks.yaml não encontrada ou vazia")
    try:
        tarefas = _yaml.safe_load(session["tasks_yaml_content"]) or {}
    except Exception as e:
        raise HTTPException(400, f"tasks.yaml inválido: {e}")
    from agents.langnetregras import reparar_passos_mecanicos, com_biblioteca
    project_id = session.get("project_id") or ""
    resolvidas = com_biblioteca(_ferramentas_resolvidas_do_projeto(project_id))
    tarefas_sys = {n: str(c.get("execution") or "deterministic")
                   for n, c in tarefas.items() if isinstance(c, dict)}
    from agents.langnetregras import FERRAMENTAS_DE_BANCO
    def _assinatura(n, v):
        a = (v or {}).get("argumentos") if isinstance(v, dict) else v
        d = (v or {}).get("saida") if isinstance(v, dict) else None
        txt = f"{n}({', '.join(a)})" if a else n
        return txt + (f" -> devolve {{{', '.join(d)}}}" if d else "")
    ferramentas_txt = ", ".join(
        _assinatura(n, v) for n, v in sorted((resolvidas or {}).items())
        if n not in FERRAMENTAS_DE_BANCO) or "nenhuma"
    tarefas_txt = ", ".join(f"{n} [{e}]" for n, e in sorted(tarefas_sys.items()))
    modelo_txt = _resumo_modelo_de_dados(project_id)
    ddl_txt = ""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            # DEFEITO CORRIGIDO (12/09/2026): ordenava por `version` ANTES da data — e a versão
            # é contada DENTRO de cada sessão. Um modelo antigo que passou por um refino (v2)
            # ganhava de um modelo NOVO recém-gerado (v1). No BioByte isso fez a conferência do
            # SQL rodar contra o modelo de 01/09 (8 tabelas) em vez do de ontem (16 tabelas):
            # 26 passos CORRETOS foram recusados com "Unknown column 'prontuario'" e afins,
            # por colunas que existem no modelo certo. A data é que diz qual é o mais recente.
            cur.execute("SELECT schema_sql FROM data_model_sessions WHERE project_id=%s AND schema_sql IS NOT NULL "
                        "AND CHAR_LENGTH(schema_sql)>0 ORDER BY created_at DESC LIMIT 1", (project_id,))
            ddl_txt = ((cur.fetchone() or {}).get("schema_sql") or ""); cur.close()
    except Exception:
        ddl_txt = ""
    disponiveis = _entradas_disponiveis_por_tarefa(tarefas, _ui_spec_do_projeto(project_id), ddl_txt)

    def _validar(nome, steps, execution):
        probs = validar_passos(steps, execution, resolvidas, tarefas_do_sistema=tarefas_sys,
                               entradas_disponiveis=disponiveis.get(nome))
        probs += _conferir_sql_no_modelo(steps, ddl_txt)
        return probs
    contexto = (f"FERRAMENTAS RESOLVIDAS (as únicas aceitas em `externo`, com os argumentos): {ferramentas_txt}\n"
                f"TAREFAS DO SISTEMA (para o passo `tarefa`; só as [deterministic] se encadeiam): {tarefas_txt}\n"
                f"MODELO DE DADOS: {modelo_txt or 'não disponível'}\n")

    def _pedir_ao_agente(nome, cfg, execution, atuais=None, problemas=None):
        """Uma chamada ao agente: estruturar do zero, ou CORRIGIR o contrato atual dados os motivos."""
        ent_txt = ", ".join(sorted(disponiveis.get(nome) or [])) or "nenhuma"
        cab = (f"TAREFA: {nome}\nEXECUÇÃO: {execution}\n{contexto}"
               f"ENTRADAS DISPONÍVEIS PARA ESTA TAREFA (únicos nomes que podem ser lidos sem passo anterior; "
               f"usuario_id e ip_origem vêm do sistema): {ent_txt}\n\n")
        if atuais is None:
            prompt = (cab +
                      f"DESCRIÇÃO EM PROSA:\n{cfg.get('description', '')}\n\n"
                      f"SAÍDA ESPERADA:\n{cfg.get('expected_output', '')}\n")
        else:
            probs = "\n".join(f"- passo {p['passo']}: {p['motivo']}" for p in (problemas or []))
            prompt = (cab +
                      f"DESCRIÇÃO EM PROSA:\n{cfg.get('description', '')}\n\n"
                      f"CONTRATO ATUAL (JSON):\n{json.dumps({'steps': atuais}, ensure_ascii=False)}\n\n"
                      f"PROBLEMAS QUE IMPEDEM O CONTRATO DE VIRAR CÓDIGO:\n{probs}\n\n"
                      "Corrija SOMENTE o necessário para eliminar esses problemas, mantendo os demais "
                      "passos iguais, e devolva o contrato COMPLETO.")
        bruto = _direct_llm_complete(prompt, "JSON puro com a chave steps", _GUIA_STEPS)
        m = re.search(r"\{.*\}", bruto or "", re.S)
        dados = json.loads(m.group(0)) if m else {}
        steps = dados.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("agente não devolveu passos" + (f" — {dados.get('observacao')}" if dados.get("observacao") else ""))
        return steps, dados.get("observacao", "")

    relatorio: List[dict] = []
    alteradas = 0
    for nome, cfg in tarefas.items():
        if not isinstance(cfg, dict):
            continue
        if req.apenas_tarefas and nome not in req.apenas_tarefas:
            continue
        execution = str(cfg.get("execution") or "deterministic")
        item = {"tarefa": nome, "reparos": [], "problemas": [], "observacao": ""}
        forcar_do_zero = bool(req.apenas_tarefas)
        antes = json.dumps(cfg.get("steps"), ensure_ascii=False, sort_keys=True) if cfg.get("steps") else None

        if cfg.get("steps") and not forcar_do_zero:
            # Tarefa que já tem contrato: 1) volta os passos marcados à forma original; 2) reparos
            # mecânicos (evidência no próprio passo); 3) revalida; 4) o que ainda não valida vai ao
            # agente COM os motivos — em vez de ficar marcado para sempre.
            steps = _desmarcar(cfg["steps"])
            steps, reparos = reparar_passos_mecanicos(steps, resolvidas)
            item["reparos"] = reparos
            problemas = _validar(nome, steps, execution)
            item["situacao"] = "já tinha contrato"
            # Até TRÊS rodadas com o agente: a correção fica se faz PROGRESSO — nenhum dos problemas
            # apontados sobrevive (os que surgirem a jusante vão para a rodada seguinte). (Resolver um problema
            # pode revelar o seguinte, ex.: acertar os argumentos da ferramenta e então a leitura de
            # um campo que ela não devolve; isso é avanço, não regressão.)
            rodadas = 0
            while problemas and rodadas < 3:
                rodadas += 1
                try:
                    novos, obs = _pedir_ao_agente(nome, cfg, execution, atuais=steps, problemas=problemas)
                except Exception as e:  # noqa: BLE001
                    item["erro_agente"] = str(e)[:200]
                    break
                novos, rep2 = reparar_passos_mecanicos(novos, resolvidas)
                probs_novos = _validar(nome, novos, execution)
                antigos = {(q["passo"], q["motivo"]) for q in problemas}
                sobreviventes = [q for q in probs_novos if (q["passo"], q["motivo"]) in antigos]
                # progresso = os problemas apontados sumiram (os que surgirem a jusante vão para a
                # rodada seguinte) OU sobraram menos problemas do que havia; regressão = nada disso
                progresso = (not sobreviventes) or len(probs_novos) < len(problemas)
                if progresso:
                    steps, problemas = novos, probs_novos
                    item["reparos"] += rep2
                    item["observacao"] = obs
                    item["situacao"] = "corrigida pelo agente" if not problemas else "corrigida em parte"
                else:
                    item["situacao"] = "correção do agente descartada (não fez progresso)"
                    item["problemas_da_correcao"] = probs_novos
                    break
            steps = _sanear_passos(steps, problemas)
        else:
            try:
                steps, obs = _pedir_ao_agente(nome, cfg, execution)
            except Exception as e:  # noqa: BLE001
                relatorio.append({"tarefa": nome, "situacao": "falha do agente", "erro": str(e)[:200]})
                continue
            item["observacao"] = obs
            steps, reparos = reparar_passos_mecanicos(steps, resolvidas)
            item["reparos"] = reparos
            problemas = _validar(nome, steps, execution)
            item["situacao"] = "estruturada"
            steps = _sanear_passos(steps, problemas)

        item["passos"] = len(steps)
        item["problemas"] = problemas
        item["invalidos"] = sum(1 for x in steps if isinstance(x, dict) and
                                str(x.get("instrucao", "")).startswith("[NÃO VALIDADO"))
        depois = json.dumps(steps, ensure_ascii=False, sort_keys=True)
        if depois != antes:
            cfg["steps"] = steps
            alteradas += 1
        else:
            item["situacao"] = item.get("situacao", "") + " · sem mudança"
        relatorio.append(item)

    if not alteradas:
        return {"session_id": session_id, "alteradas": 0, "relatorio": relatorio}

    novo_yaml = _yaml.safe_dump(tarefas, allow_unicode=True, sort_keys=False, width=100)
    versions = get_tasks_yaml_versions(session_id)
    nova_versao = (max([v["version"] for v in versions]) if versions else 0) + 1
    update_tasks_yaml_session(session_id, {"tasks_yaml_content": novo_yaml, "status": "completed"})
    create_tasks_yaml_version({
        "session_id": session_id, "version": nova_versao, "tasks_yaml_content": novo_yaml,
        "created_by": current_user.get("id") if isinstance(current_user, dict) else None,
        # a coluna é um ENUM fechado: usa o valor permitido e diz o que foi na descrição
        "change_type": "ai_refinement",
        "change_description": f"estruturar passos: contrato `steps:` em {alteradas} tarefa(s)",
        "doc_size": len(novo_yaml),
    })
    try:
        save_tasks_yaml_chat_message({
            "session_id": session_id, "sender_type": "agent", "sender_name": "Tradutor de regras",
            "message_text": f"Passos estruturados em {alteradas} tarefa(s); versão v{nova_versao}.",
            "message_type": "result",
        })
    except Exception as e:  # noqa: BLE001 — a mensagem é registro; a versão já está gravada
        print(f"[ESTRUTURAR] aviso: mensagem de chat não gravada: {e}")
    for r in relatorio:
        print(f"[ESTRUTURAR] {r.get('tarefa')}: {r.get('situacao')} · passos={r.get('passos')} "
              f"invalidos={r.get('invalidos')} reparos={r.get('reparos')} problemas={r.get('problemas')}"
              + (f" erro_agente={r.get('erro_agente')}" if r.get('erro_agente') else "")
              + (f" problemas_da_correcao={r.get('problemas_da_correcao')}" if r.get('problemas_da_correcao') else ""))
    return {"session_id": session_id, "version": nova_versao, "alteradas": alteradas, "relatorio": relatorio}
