/**
 * Etapa FERRAMENTAS do pipeline.
 *
 * Mostra o inventário de ferramentas do sistema e, para cada uma, DE ONDE vem a
 * implementação: biblioteca do gerador, servidor MCP, função determinística com regra
 * declarada, ou pendente. Ferramenta pendente bloqueia a aprovação — é o que impede a
 * geração de código de escrever ferramenta de mentira.
 *
 * Mesmo padrão das demais etapas: origem + versão, gerar, refinar por chat, editar,
 * histórico de versões e aprovar.
 */
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import {
  DocumentoFerramentas, Ferramenta, aprovarFerramentas, gerarFerramentas, historicoChat,
  listarSessoes, listarVersoes, obterSessao, obterVersao, refinarFerramentas, salvarFerramentas,
  ultimaSessao,
} from "../services/toolsStageService";
import "./ToolsStagePage.css";

const CORES: Record<string, string> = {
  biblioteca: "origem-biblioteca",
  mcp: "origem-mcp",
  deterministica: "origem-deterministica",
  externa: "origem-externa",
  pendente: "origem-pendente",
};

const ROTULOS: Record<string, string> = {
  biblioteca: "Biblioteca do gerador",
  mcp: "Servidor MCP",
  deterministica: "Determinística",
  externa: "Externa (registrar no MCP)",
  pendente: "Sem implementação",
};

export default function ToolsStagePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [sessionId, setSessionId] = useState<string>("");
  const [doc, setDoc] = useState<DocumentoFerramentas | null>(null);
  const [versao, setVersao] = useState<number>(0);
  const [sessoes, setSessoes] = useState<any[]>([]);
  const [versoes, setVersoes] = useState<any[]>([]);
  const [mensagens, setMensagens] = useState<{ role: string; content: string }[]>([]);
  const [instrucao, setInstrucao] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [erro, setErro] = useState("");
  const [selecionada, setSelecionada] = useState<string>("");

  const carregar = useCallback(async () => {
    if (!projectId) return;
    try {
      const s = await ultimaSessao(projectId);
      setSessionId(s.id);
      setDoc(s.tools_json);
      setVersao(s.version);
      const [ls, lv, ch] = await Promise.all([
        listarSessoes(projectId), listarVersoes(s.id), historicoChat(s.id),
      ]);
      setSessoes(ls.sessions || []);
      setVersoes(lv.versions || []);
      setMensagens(ch.messages || []);
    } catch (e) {
      setDoc(null);
    }
  }, [projectId]);

  useEffect(() => { carregar(); }, [carregar]);

  const gerar = async () => {
    if (!projectId) return;
    setOcupado(true); setErro("");
    try {
      const r = await gerarFerramentas(projectId);
      setSessionId(r.session_id); setDoc(r); setVersao(r.version);
      await carregar();
    } catch (e: any) { setErro(String(e.message || e)); }
    setOcupado(false);
  };

  const refinar = async () => {
    if (!sessionId || !instrucao.trim()) return;
    setOcupado(true); setErro("");
    try {
      const r = await refinarFerramentas(sessionId, instrucao.trim());
      setDoc(r); setVersao(r.version); setInstrucao("");
      const [lv, ch] = await Promise.all([listarVersoes(sessionId), historicoChat(sessionId)]);
      setVersoes(lv.versions || []); setMensagens(ch.messages || []);
    } catch (e: any) { setErro(String(e.message || e)); }
    setOcupado(false);
  };

  const aprovar = async () => {
    if (!sessionId) return;
    setOcupado(true); setErro("");
    try {
      const r = await aprovarFerramentas(sessionId, true);
      setErro(r.gate?.aprovado ? "" : r.gate?.mensagem || "");
      await carregar();
    } catch (e: any) { setErro(String(e.message || e)); }
    setOcupado(false);
  };

  const editarCampo = async (nome: string, campo: keyof Ferramenta, valor: any) => {
    if (!doc) return;
    const tools = doc.tools.map((t) =>
      t.nome === nome ? { ...t, [campo]: valor,
        resolvida: campo === "regra"
          ? (t.origem === "deterministica" && String(valor).trim().length > 0)
          : t.resolvida } : t);
    const novo = { ...doc, tools };
    setDoc(novo);
    if (sessionId) {
      try {
        const r = await salvarFerramentas(sessionId, novo, `ajuste em ${nome}`);
        setVersao(r.version);
        const lv = await listarVersoes(sessionId); setVersoes(lv.versions || []);
      } catch (e: any) { setErro(String(e.message || e)); }
    }
  };

  const verVersao = async (v: number) => {
    if (!sessionId) return;
    const d = await obterVersao(sessionId, v);
    setDoc(d); setVersao(v);
  };

  const abrirSessao = async (id: string) => {
    const s = await obterSessao(id);
    setSessionId(id); setDoc(s.tools_json); setVersao(s.version);
    const [lv, ch] = await Promise.all([listarVersoes(id), historicoChat(id)]);
    setVersoes(lv.versions || []); setMensagens(ch.messages || []);
  };

  const resumo = doc?.resumo;
  const pendentes = useMemo(() => (doc?.tools || []).filter((t) => !t.resolvida), [doc]);
  const detalhe = useMemo(
    () => (doc?.tools || []).find((t) => t.nome === selecionada) || null, [doc, selecionada]);

  return (
    <div className="ferramentas-pagina">
      <header className="ferramentas-cabecalho">
        <div>
          <h1>🧰 Ferramentas</h1>
          <p>
            Cada ferramenta citada na especificação de Agentes e Tarefas precisa dizer{" "}
            <b>de onde vem a implementação</b>. Sem isso, a geração de código escreve ferramenta
            de mentira — que devolve valor fixo e parece funcionar.
          </p>
        </div>
        <div className="ferramentas-acoes">
          <select value={sessionId} onChange={(e) => abrirSessao(e.target.value)}>
            <option value="">Sessões desta etapa…</option>
            {sessoes.map((s) => (
              <option key={s.id} value={s.id}>
                v{s.version} · {s.total_resolvidas}/{s.total_tools} resolvidas ·{" "}
                {new Date(s.created_at).toLocaleString("pt-BR")}
              </option>
            ))}
          </select>
          <button className="btn-primario" onClick={gerar} disabled={ocupado}>
            {ocupado ? "Processando…" : "Gerar a partir do ATS"}
          </button>
          <button className="btn-secundario" onClick={aprovar}
                  disabled={ocupado || !doc || (pendentes.length > 0)}>
            Aprovar etapa
          </button>
        </div>
      </header>

      {erro && <div className="ferramentas-erro">⚠ {erro}</div>}

      {!doc && (
        <div className="ferramentas-vazio">
          Nenhum inventário ainda. Clique em <b>Gerar a partir do ATS</b> para levantar as
          ferramentas que os agentes e as tarefas citam.
        </div>
      )}

      {doc && (
        <>
          <div className="ferramentas-indicadores">
            <div className="indicador">
              <span>Ferramentas</span><b>{resumo?.total ?? 0}</b>
            </div>
            <div className="indicador ok">
              <span>Com implementação</span><b>{resumo?.resolvidas ?? 0}</b>
            </div>
            <div className={`indicador ${pendentes.length ? "falha" : ""}`}>
              <span>Pendentes</span><b>{resumo?.pendentes ?? 0}</b>
            </div>
            <div className="indicador"><span>Versão</span><b>v{versao}</b></div>
          </div>

          <div className={`portao ${pendentes.length ? "portao-bloqueado" : "portao-liberado"}`}>
            {pendentes.length
              ? `Geração de código bloqueada — sem implementação: ${pendentes.map((p) => p.nome).join(", ")}`
              : "Todas as ferramentas têm implementação declarada. Etapa pronta para aprovação."}
          </div>

          <div className="ferramentas-corpo">
            <table className="ferramentas-tabela">
              <thead>
                <tr><th>Ferramenta</th><th>Origem</th><th>Implementação</th><th>Usada por</th></tr>
              </thead>
              <tbody>
                {doc.tools.map((t) => (
                  <tr key={t.nome} className={selecionada === t.nome ? "selecionada" : ""}
                      onClick={() => setSelecionada(t.nome)}>
                    <td><code>{t.nome}</code></td>
                    <td><span className={`selo ${CORES[t.origem] || ""}`}>{ROTULOS[t.origem] || t.origem}</span></td>
                    <td>{t.implementacao || <i>não definida</i>}</td>
                    <td className="usos">{(t.usada_por || []).join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <aside className="ferramentas-lateral">
              {detalhe ? (
                <div className="detalhe">
                  <h3>{detalhe.nome}</h3>
                  <label>Origem</label>
                  <select value={detalhe.origem}
                          onChange={(e) => editarCampo(detalhe.nome, "origem", e.target.value)}>
                    {Object.keys(ROTULOS).map((o) => <option key={o} value={o}>{ROTULOS[o]}</option>)}
                  </select>
                  <label>O que faz</label>
                  <textarea value={detalhe.descricao} rows={2}
                            onChange={(e) => editarCampo(detalhe.nome, "descricao", e.target.value)} />
                  <label>Entrada</label>
                  <input value={(detalhe.entrada || []).join(", ")}
                         onChange={(e) => editarCampo(detalhe.nome, "entrada",
                           e.target.value.split(",").map((x) => x.trim()).filter(Boolean))} />
                  <label>Saída</label>
                  <input value={(detalhe.saida || []).join(", ")}
                         onChange={(e) => editarCampo(detalhe.nome, "saida",
                           e.target.value.split(",").map((x) => x.trim()).filter(Boolean))} />
                  <label>Regra (obrigatória para determinística)</label>
                  <textarea value={detalhe.regra} rows={3}
                            placeholder="Ex.: conferir a senha informada contra o hash guardado e devolver verdadeiro ou falso"
                            onChange={(e) => editarCampo(detalhe.nome, "regra", e.target.value)} />
                </div>
              ) : (
                <div className="detalhe vazio">Selecione uma ferramenta na tabela para ver e editar o contrato.</div>
              )}

              <div className="refino">
                <h4>Refinar com o agente</h4>
                <div className="mensagens">
                  {mensagens.slice(-6).map((m, i) => (
                    <div key={i} className={`msg ${m.role}`}>{m.content}</div>
                  ))}
                </div>
                <textarea rows={2} value={instrucao} placeholder="Ex.: a validação de senha é determinística; a regra é conferir o hash"
                          onChange={(e) => setInstrucao(e.target.value)} />
                <button className="btn-primario" onClick={refinar} disabled={ocupado || !instrucao.trim()}>
                  Enviar
                </button>
              </div>

              <div className="versoes">
                <h4>Versões</h4>
                <ul>
                  {versoes.map((v) => (
                    <li key={v.version}>
                      <button onClick={() => verVersao(v.version)}>v{v.version}</button>
                      <span>{v.change_description || v.change_type}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </aside>
          </div>
        </>
      )}
    </div>
  );
}
