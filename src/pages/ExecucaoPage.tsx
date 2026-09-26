/**
 * ExecucaoPage — a Bancada de Execução.
 *
 * É a nossa ferramenta de diagnóstico: mostra a rede do projeto executando de
 * verdade, lugar por lugar, contra o servidor de agentes. O cliente nunca vê
 * esta tela — ele vê a ação de negócio na tela dele.
 *
 * Quem faz o quê:
 *   - PetriNetSimulator  decide quem está apto e dispara
 *   - PlaceProcessor     executa o código de cada lugar quando o token chega
 *   - fakeWebSocket      intercepta a conversa que o código do lugar abre...
 *   - CentralWSClient    ...e mantém UMA ligação por porta, com fila e cache
 *
 * A tela não calcula nada: ela roteia, por tipo, o que o servidor conta.
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { PetriNetSimulator } from "../components/petri-net/PetriNetSimulator";
import { CentralWSClient } from "../components/petri-net/utils_exec/centralWSClient";
import { FakeWebSocket } from "../components/petri-net/utils_exec/fakeWebSocket";
// Componente trazido INTEIRO da máquina de referência, em JavaScript. O
// TypeScript não consegue inferir as propriedades de um forwardRef em JS, e
// não vamos alterar o arquivo de lá só por isso — por isso o empréstimo de tipo.
// @ts-ignore
import PetriNetEditorExecOriginal from "../components/petri-net/PetriNetEditorExec";
const PetriNetEditorExec: any = PetriNetEditorExecOriginal;
import "./ExecucaoPage.css";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

type Aba = "operacao" | "execucao" | "entradas" | "saidas" | "registro" | "etiquetas";

const ABAS: { id: Aba; rotulo: string; icone: string }[] = [
  { id: "operacao", rotulo: "Operação", icone: "⚡" },
  { id: "execucao", rotulo: "Execução", icone: "⚙️" },
  { id: "entradas", rotulo: "Entradas", icone: "📥" },
  { id: "saidas", rotulo: "Saídas", icone: "📦" },
  { id: "registro", rotulo: "Registro", icone: "📄" },
  { id: "etiquetas", rotulo: "Etiquetas", icone: "🏷️" },
];

/** O endereço do servidor de agentes está escrito dentro do código dos lugares. */
function descobrirEnderecoDoServidor(rede: any): string | null {
  for (const lugar of rede?.lugares || []) {
    const achado = String(lugar?.logica || "").match(/wss?:\/\/[^"'`\s)]+/);
    if (achado) return achado[0];
  }
  return null;
}

/** Nome de tarefa que cada lugar chama, para a bancada listar o que o projeto faz. */
function tarefasDaRede(rede: any): string[] {
  const nomes: string[] = [];
  for (const lugar of rede?.lugares || []) {
    const achado = String(lugar?.logica || "").match(/task_name["':\s]+["']([A-Za-z0-9_]+)/);
    if (achado && !nomes.includes(achado[1])) nomes.push(achado[1]);
  }
  return nomes;
}

const ExecucaoPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();

  const [rede, setRede] = useState<any>(null);
  const [erroDeCarga, setErroDeCarga] = useState<string | null>(null);
  const [aba, setAba] = useState<Aba>("operacao");
  const [modo, setModo] = useState<"continua" | "passo">("continua");
  const [rodando, setRodando] = useState(false);
  const [tique, setTique] = useState(0);
  const [registro, setRegistro] = useState<string[]>([]);
  const [passos, setPassos] = useState<any[]>([]);
  const [etiquetas, setEtiquetas] = useState<Record<string, any>>({});
  const [painelAberto, setPainelAberto] = useState(false);

  const simRef = useRef<any>(null);
  const editorRef = useRef<any>(null);
  const laçoRef = useRef<any>(null);

  const anotar = useCallback((texto: string) => {
    const hora = new Date().toLocaleTimeString();
    setRegistro((r) => [...r.slice(-400), `[${hora}] ${texto}`]);
  }, []);

  // ── carregar a rede do projeto ──────────────────────────────────────────
  useEffect(() => {
    if (!projectId) return;
    const token = localStorage.getItem("accessToken") || localStorage.getItem("token");
    fetch(`${API_BASE}/petri-net/${projectId}`, {
      headers: { Authorization: token ? `Bearer ${token}` : "", "Content-Type": "application/json" },
    })
      .then((r) => r.json())
      .then((d) => {
        const n = d?.petri_net || d?.petriNet || d;
        if (!n || !Array.isArray(n.lugares) || n.lugares.length === 0) {
          setErroDeCarga("Este projeto ainda não tem Rede de Petri. Gere a rede na etapa anterior.");
          return;
        }
        setRede(n);
        anotar(`rede carregada: ${n.lugares.length} lugares, ${n.transicoes?.length || 0} transições`);
      })
      .catch((e) => setErroDeCarga(`Não consegui carregar a rede: ${e.message}`));
  }, [projectId, anotar]);

  const endereco = useMemo(() => (rede ? descobrirEnderecoDoServidor(rede) : null), [rede]);
  const tarefas = useMemo(() => (rede ? tarefasDaRede(rede) : []), [rede]);

  // ── preparar o simulador e a ligação única ──────────────────────────────
  useEffect(() => {
    if (!rede) return;
    // O código de cada lugar abre "uma conversa". O interceptador redireciona
    // todas para o cliente central — UMA ligação por porta, com fila e cache.
    if (endereco) {
      try {
        // "localhost" pode resolver para IPv6 no navegador, enquanto o servidor
        // de agentes costuma escutar só em IPv4 — a ligação silenciosamente não
        // chega. Fixamos IPv4 para não depender da ordem de resolução.
        const alvo = endereco.replace("//localhost:", "//127.0.0.1:");
        (window as any).V7_WS_URI = alvo;
        localStorage.setItem("V7_WS_URI", alvo);
      } catch { /* navegador sem armazenamento — segue assim mesmo */ }
    }
    const sim = new PetriNetSimulator(JSON.parse(JSON.stringify(rede)));
    // O interceptador vai DENTRO da caixa onde o código do lugar roda — não no
    // objeto global. Assim o cliente central continua usando o WebSocket de
    // verdade para falar com o servidor de agentes.
    sim.placeProcessor.WebSocketClass = FakeWebSocket;
    sim.placeProcessor.setCallbacks({
      onPlaceProcessed: (id: string) => {
        anotar(`lugar ${id} concluiu`);
        setTique((t) => t + 1);
      },
      onError: (id: string, erro: any) => {
        anotar(`lugar ${id} FALHOU: ${erro?.message || erro}`);
        setTique((t) => t + 1);
      },
    });
    simRef.current = sim;
    setTique((t) => t + 1);

    // Ouvir o que o servidor conta, e distribuir por gaveta.
    try {
      const central = CentralWSClient.getInstance();
      const ouvir = (p: any) => {
        setPassos((lista) => [...lista.slice(-300), p]);
        if (p?.type === "tags_extracted" || p?.tags) setEtiquetas(p.tags || p?.data?.tags || {});
      };
      central.setVerboseCallback(ouvir);
      central.setOperationCallback(ouvir);
    } catch { /* cliente central indisponível — a bancada ainda mostra a rede */ }

    return () => { if (laçoRef.current) clearInterval(laçoRef.current); };
  }, [rede, endereco, anotar]);

  // ── laço que dispara as transições aptas ────────────────────────────────
  const darUmPasso = useCallback(() => {
    const sim = simRef.current;
    if (!sim) return false;
    const aptas = sim.getEnabledTransitions();
    if (!aptas.length) return false;
    const t = aptas[0];
    try {
      sim.fireTransition(t.id);
      anotar(`disparou ${t.id} — ${String(t.nome || "").replace(/\n/g, " ")}`);
    } catch (e: any) {
      anotar(`não consegui disparar ${t.id}: ${e.message}`);
      return false;
    }
    setTique((x) => x + 1);
    return true;
  }, [anotar]);

  const iniciar = useCallback(async () => {
    setRodando(true);
    anotar("execução iniciada");

    // Como a tela de referência faz: abre a rodada no servidor de agentes e
    // manda o próprio desenho da rede simular. Quem executa é o editor.
    try {
      await Promise.race([
        CentralWSClient.getInstance().sendGenericCommand("iniciar_execucao", {
          timestamp: new Date().toISOString(),
          projeto: rede?.nome || "",
        }),
        new Promise((r) => setTimeout(r, 4000)),
      ]);
      anotar("rodada aberta no servidor de agentes");
    } catch (e: any) {
      anotar(`não consegui abrir a rodada: ${e?.message || e}`);
    }

    try {
      editorRef.current?.startAutoSimulation();
    } catch (e: any) {
      anotar(`não consegui iniciar a simulação: ${e?.message || e}`);
      setRodando(false);
    }
  }, [anotar, rede]);

  const reiniciar = useCallback(() => {
    if (laçoRef.current) clearInterval(laçoRef.current);
    setRodando(false);
    setRegistro([]); setPassos([]); setEtiquetas({});
    const sim = simRef.current;
    if (sim) { sim.cancelAllProcessing(); sim.resetSimulation(); }
    if (rede) {
      const novo = new PetriNetSimulator(JSON.parse(JSON.stringify(rede)));
      simRef.current = novo;
    }
    setTique((t) => t + 1);
    anotar("reiniciado");
  }, [rede, anotar]);

  // ── números do cabeçalho ────────────────────────────────────────────────
  const sim = simRef.current;
  const lugares = sim?.petriNet?.lugares || [];
  const comTrabalho = lugares.filter((l: any) => l.agentId || (l.logica || "").trim());
  const concluidos = comTrabalho.filter((l: any) => l.status === "completed").length;
  const comErro = comTrabalho.filter((l: any) => l.status === "error").length;
  const executando = comTrabalho.filter((l: any) => l.status === "running").length;
  const progresso = comTrabalho.length ? Math.round((concluidos / comTrabalho.length) * 100) : 0;
  const aptas = sim ? sim.getEnabledTransitions().map((t: any) => t.id) : [];
  const lugarCorrente = comTrabalho.find((l: any) => l.status === "running");

  const relatorio = useMemo(() => {
    if (!passos.length) return "";
    return passos.slice(-40).map((p: any) => {
      const d = p?.data || p;
      return `- **${d?.step_type || p?.type || "passo"}** — ${d?.step_description || ""}`;
    }).join("\n");
  }, [passos]);

  if (erroDeCarga) {
    return <div className="bancada"><div className="bancada-aviso">⚠️ {erroDeCarga}</div></div>;
  }
  if (!rede) {
    return <div className="bancada"><div className="bancada-aviso">Carregando a rede do projeto…</div></div>;
  }

  return (
    // data-geracao existe para o React redesenhar quando o estado da rede muda
    <div className="bancada" data-geracao={tique}>
      <header className="bancada-topo">
        <div>
          <h1>▶️ Execução de Agentes</h1>
          <p className="bancada-sub">
            {rede.nome || "Rede do projeto"} · servidor de agentes: <code>{endereco || "não encontrado"}</code>
          </p>
        </div>
        <div className="bancada-numeros">
          <div><strong>{comTrabalho.length}</strong><span>tarefas</span></div>
          <div className="ok"><strong>{concluidos}</strong><span>concluídas</span></div>
          <div className="rodando"><strong>{executando}</strong><span>executando</span></div>
          <div className="erro"><strong>{comErro}</strong><span>com erro</span></div>
          <div><strong>{progresso}%</strong><span>progresso</span></div>
        </div>
      </header>

      <section className="bancada-controles">
        <div className="grupo-modo">
          <button className={modo === "continua" ? "sel" : ""} onClick={() => setModo("continua")}>Contínua</button>
          <button className={modo === "passo" ? "sel" : ""} onClick={() => setModo("passo")}>Passo a passo</button>
        </div>
        <button className="btn-iniciar" onClick={iniciar} disabled={rodando}>▶️ Iniciar</button>
        {modo === "passo" && <button className="btn-passo" onClick={darUmPasso}>⏭️ Um passo</button>}
        <button className="btn-reiniciar" onClick={reiniciar}>🔄 Reiniciar</button>
        <button className="btn-painel" onClick={() => setPainelAberto((v) => !v)}>
          {painelAberto ? "Fechar acompanhamento" : "Abrir acompanhamento"}
        </button>
      </section>

      {/* Desenho E execução: é o PetriNetEditor da máquina de referência, com as
          mesmas propriedades que a tela de lá usa. Ele desenha com JointJS
          (lugares, transições, ARCOS, faixas dos agentes) e roda a simulação. */}
      <section className="bancada-rede">
        <PetriNetEditorExec
          ref={editorRef}
          externalData={sim?.petriNet || rede}
          onDataLoad={() => anotar("rede desenhada e pronta")}
          compactMode={true}
          suppressVerbosePanel={false}
          onSimulationStart={() => {
            anotar("simulação iniciada pelo painel da rede");
            try {
              CentralWSClient.getInstance().sendGenericCommand("iniciar_execucao", {
                timestamp: new Date().toISOString(),
              });
            } catch { /* servidor de agentes indisponível */ }
          }}
        />
      </section>

      <nav className="bancada-abas">
        {ABAS.map((a) => (
          <button key={a.id} className={aba === a.id ? "sel" : ""} onClick={() => setAba(a.id)}>
            {a.icone} {a.rotulo}
          </button>
        ))}
      </nav>

      <section className="bancada-conteudo">
        {aba === "operacao" && (
          <div className="duas-colunas">
            <div>
              <h3>Transições aptas</h3>
              {aptas.length ? <ul>{aptas.map((id: string) => <li key={id}>{id}</li>)}</ul>
                            : <p className="vazio">nenhuma no momento</p>}
              <h3>Estado dos lugares</h3>
              <ul className="lista-estado">
                {lugares.map((l: any) => (
                  <li key={l.id}>
                    <code>{l.id}</code> {String(l.nome || "").replace(/\n/g, " ")} —
                    <strong> {sim?.markingVector?.[l.id] || 0}</strong> token(s)
                    <em className={l.status}> {l.status || "pendente"}</em>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3>Log de disparos</h3>
              <pre className="caixa-log">{(sim?.simulationLog || []).map((d: any, i: number) =>
                `${i + 1}. ${d.transitionId || d.transicao || "?"} — ${d.timestamp || ""}`).join("\n") || "nenhum disparo ainda"}</pre>
            </div>
          </div>
        )}

        {aba === "execucao" && (
          <div>
            <h3>Tarefa corrente</h3>
            {lugarCorrente ? (
              <>
                <p><code>{lugarCorrente.id}</code> {String(lugarCorrente.nome || "").replace(/\n/g, " ")}</p>
                <h4>Entrou</h4>
                <pre className="caixa">{JSON.stringify(lugarCorrente.input_data || {}, null, 2)}</pre>
              </>
            ) : <p className="vazio">nenhuma tarefa em execução</p>}
            <h4>Últimos passos contados pelo servidor</h4>
            <pre className="caixa">{passos.slice(-12).map((p: any) =>
              JSON.stringify(p?.data || p).slice(0, 220)).join("\n") || "nada ainda"}</pre>
          </div>
        )}

        {aba === "entradas" && (
          <div>{lugares.map((l: any) => (
            <div key={l.id} className="bloco">
              <h4><code>{l.id}</code> {String(l.nome || "").replace(/\n/g, " ")}</h4>
              <pre className="caixa">{JSON.stringify(l.input_data || {}, null, 2)}</pre>
            </div>
          ))}</div>
        )}

        {aba === "saidas" && (
          <div>{lugares.map((l: any) => (
            <div key={l.id} className="bloco">
              <h4>
                <code>{l.id}</code> {String(l.nome || "").replace(/\n/g, " ")}
                <em className={l.status}> {l.status || "pendente"}</em>
              </h4>
              <pre className="caixa">{JSON.stringify(l.output_data || {}, null, 2)}</pre>
            </div>
          ))}</div>
        )}

        {aba === "registro" && <pre className="caixa-log alto">{registro.join("\n") || "nada ainda"}</pre>}

        {aba === "etiquetas" && (
          <div>
            <h3>Etiquetas da última tarefa</h3>
            {Object.keys(etiquetas).length ? (
              <table className="tabela-etiquetas">
                <tbody>
                  {Object.entries(etiquetas).map(([k, v]) => (
                    <tr key={k}>
                      <th>{k}</th>
                      <td><pre>{typeof v === "string" ? v : JSON.stringify(v, null, 2)}</pre></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="vazio">
                As etiquetas aparecem quando o servidor de agentes as envia ao fim de cada tarefa
                (nome do agente, ferramenta usada, o que ele pensou, o que a ferramenta respondeu).
              </p>
            )}
          </div>
        )}
      </section>

      {/* O painel móvel de acompanhamento é aberto pelo próprio PetriNetViewer,
          como na tela de referência — não abrimos um segundo aqui. */}

    </div>
  );
};

export default ExecucaoPage;
