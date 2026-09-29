/**
 * ExecucaoPage — a Bancada de Execução.
 *
 * Esta página é apenas a MOLDURA. Ela carrega a Rede de Petri do projeto (do
 * nosso back-end, do mesmo banco) e entrega para a tela de execução trazida
 * inteira da máquina de referência — `ExecutorTarefasNew`, 4.922 linhas.
 *
 * É essa tela que desenha a rede, dispara a execução, roteia as mensagens do
 * servidor de agentes por aba e abre os painéis. Nada disso é reescrito aqui:
 * a tentativa anterior de montar as peças na mão custou vários defeitos que a
 * tela de lá já resolvia (painel que desmontava, canal de avisos disputado,
 * início antes de o desenho terminar de carregar).
 */
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
// @ts-ignore — tela trazida da máquina de referência, em JavaScript
import ExecutorTarefasOriginal from "../components/petri-net/ExecutorTarefasNew";
import "./ExecucaoPage.css";

const ExecutorTarefas: any = ExecutorTarefasOriginal;
const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

// Campos de controle que a rede acrescenta sozinha — não são entrada do operador.
const CAMPOS_DE_CONTROLE = new Set(["from_transition", "received_at", "tokens_received", "status", "timestamp"]);

/**
 * O que a execução precisa receber de quem a dispara.
 *
 * A rede nasce com os lugares de tarefa já declarando os campos que esperam
 * (`input_data` com os valores em branco). Até aqui ninguém os preenchia: a Bancada
 * não tinha onde o operador dizer QUAL caso analisar, a primeira tarefa recebia tudo
 * vazio, respondia "não aproveitável" e a cadeia inteira seguia com "sem dado"
 * (medido no BioByte v5 em 29/09/2026). Os campos pedidos são os das primeiras
 * tarefas — as que a transição de início alimenta — lidos da própria rede.
 */
function camposDeEntrada(rede: any): string[] {
  const lugares: any[] = rede?.lugares || [];
  const arcos: any[] = rede?.arcos || [];
  const inicio = new Set(lugares.filter((l) => Number(l?.tokens) > 0).map((l) => l.id));
  const transicoesDeInicio = new Set(arcos.filter((a) => inicio.has(a.origem)).map((a) => a.destino));
  const primeiras = new Set(arcos.filter((a) => transicoesDeInicio.has(a.origem)).map((a) => a.destino));
  const campos: string[] = [];
  lugares.filter((l) => primeiras.has(l.id)).forEach((l) => {
    Object.keys(l?.input_data || {}).forEach((k) => {
      if (!CAMPOS_DE_CONTROLE.has(k) && !campos.includes(k)) campos.push(k);
    });
  });
  // identificadores primeiro: são eles que dizem sobre QUEM a execução trabalha
  return campos.sort((a, b) => Number(/_id$|^id_/.test(b)) - Number(/_id$|^id_/.test(a)));
}

/** Copia os valores para todo lugar que espera o mesmo campo. Só nesta execução. */
function aplicarEntrada(rede: any, valores: Record<string, string>): any {
  const nova = JSON.parse(JSON.stringify(rede));
  (nova.lugares || []).forEach((l: any) => {
    if (!l?.input_data || typeof l.input_data !== "object") return;
    Object.entries(valores).forEach(([k, v]) => {
      if (String(v).trim() !== "" && k in l.input_data) l.input_data[k] = String(v).trim();
    });
  });
  return nova;
}

const ExecucaoPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [projeto, setProjeto] = useState<any>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [redeOriginal, setRedeOriginal] = useState<any>(null);
  const [valores, setValores] = useState<Record<string, string>>({});
  const [aplicado, setAplicado] = useState<Record<string, string>>({});
  const [montagem, setMontagem] = useState(0);

  useEffect(() => {
    if (!projectId) return;
    const token = localStorage.getItem("accessToken") || localStorage.getItem("token");
    fetch(`${API_BASE}/petri-net/${projectId}`, {
      headers: { Authorization: token ? `Bearer ${token}` : "", "Content-Type": "application/json" },
    })
      .then((r) => r.json())
      .then(async (d) => {
        const rede = d?.petri_net || d?.petriNet || d;
        if (!rede || !Array.isArray(rede.lugares) || rede.lugares.length === 0) {
          setErro("Este projeto ainda não tem Rede de Petri. Gere a rede na etapa anterior.");
          return;
        }

        // PORTA DO SERVIDOR QUE ESTÁ NO AR.
        // A rede nasce com a porta padrão (5002) escrita dentro de cada lugar. A
        // implantação, porém, escolhe uma porta LIVRE — se a padrão estiver ocupada,
        // sobe na 5023, por exemplo. A Bancada então falava sozinha com uma porta onde
        // não há ninguém, e a execução morria em "WebSocket error" sem dizer por quê.
        // Aqui a moldura pergunta ao back-end qual implantação deste projeto está no ar
        // e reescreve a porta nos lugares, para a Bancada falar com o servidor de verdade.
        let portaDoServidor: number | null = null;
        try {
          const rr = await fetch(`${API_BASE}/code-generation/project/${projectId}/runs`, {
            headers: { Authorization: token ? `Bearer ${token}` : "" },
          });
          const runs = await rr.json();
          const lista = Array.isArray(runs) ? runs : runs?.runs || [];
          const noAr = lista.find((r: any) => r?.status === "running");
          const servico = (noAr?.services || []).find((s: any) =>
            String(s?.url || "").startsWith("ws://"));
          const portaViva = servico?.port;
          portaDoServidor = portaViva || null;
          if (portaViva) {
            let trocados = 0;
            rede.lugares.forEach((l: any) => {
              if (typeof l?.logica === "string" && /const PORT\s*=\s*\d+/.test(l.logica)) {
                l.logica = l.logica.replace(/const PORT\s*=\s*\d+/, `const PORT = ${portaViva}`);
                trocados += 1;
              }
            });
            if (trocados) {
              console.log(`[Bancada] servidor de agentes no ar na porta ${portaViva} — `
                + `${trocados} lugar(es) apontados para ela`);
            }
          }
        } catch {
          /* sem implantação no ar: a rede segue com a porta que trouxe */
        }

        // "localhost" pode resolver para IPv6 no navegador, enquanto o servidor
        // de agentes costuma escutar só em IPv4 — a ligação não chega, calada.
        // O endereço é MONTADO com a porta viva. Antes era copiado do texto do lugar,
        // onde a porta é um molde (`ws://localhost:${PORT}`): o navegador recebia o molde
        // como endereço e recusava — "The URL 'ws://127.0.0.1:${PORT}' is invalid".
        const endereco = portaDoServidor ? `ws://127.0.0.1:${portaDoServidor}` : "";
        if (endereco) {
          try {
            (window as any).V7_WS_URI = endereco;
            localStorage.setItem("V7_WS_URI", endereco);
          } catch { /* navegador sem armazenamento */ }
        }

        // A tela de referência espera o projeto com a rede em `project_data`,
        // que é o mesmo nome da coluna do banco. Publicamos o mesmo objeto para o
        // carregador de dentro dela não ir buscar o projeto noutro servidor.
        const carregado = {
          id: projectId,
          name: rede.nome || "Projeto",
          description: rede.description || "",
          project_data: rede,
          petri_net_data: rede,
          petriNet: rede,   // nome que o carregador da tela de referência procura
        };
        try { (window as any).V7_PROJECT = carregado; } catch { /* sem window */ }
        setRedeOriginal(JSON.parse(JSON.stringify(rede)));
        setProjeto({
          id: projectId,
          name: rede.nome || "Projeto",
          description: rede.description || "",
          project_data: rede,
        });
      })
      .catch((e) => setErro(`Não consegui carregar a rede: ${e.message}`));
  }, [projectId]);

  if (erro) return <div className="bancada"><div className="bancada-aviso">⚠️ {erro}</div></div>;
  if (!projeto) return <div className="bancada"><div className="bancada-aviso">Carregando a rede do projeto…</div></div>;

  const campos = camposDeEntrada(redeOriginal);
  const aplicar = () => {
    const rede = aplicarEntrada(redeOriginal, valores);
    const carregado = {
      id: projectId, name: rede.nome || "Projeto", description: rede.description || "",
      project_data: rede, petri_net_data: rede, petriNet: rede,
    };
    try { (window as any).V7_PROJECT = carregado; } catch { /* sem window */ }
    setProjeto({ ...projeto, project_data: rede });
    setAplicado(Object.fromEntries(Object.entries(valores).filter(([, v]) => String(v).trim() !== "")));
    setMontagem((m) => m + 1);   // a tela de execução relê a rede com a entrada preenchida
  };

  return (
    <div className="bancada bancada-referencia">
      {campos.length > 0 && (
        <div className="bancada-entrada">
          <div className="bancada-entrada-titulo">
            📥 Entrada da execução
            <span>o que esta execução vai analisar — vale para todas as tarefas que esperam o mesmo campo</span>
          </div>
          <div className="bancada-entrada-campos">
            {campos.map((c) => (
              <label key={c}>
                <span>{c}</span>
                <input
                  value={valores[c] || ""}
                  onChange={(e) => setValores({ ...valores, [c]: e.target.value })}
                  placeholder="(em branco)"
                />
              </label>
            ))}
          </div>
          <div className="bancada-entrada-acoes">
            <button onClick={aplicar}>Aplicar à execução</button>
            {Object.keys(aplicado).length > 0 ? (
              <span className="bancada-entrada-ok">
                ✓ aplicado: {Object.entries(aplicado).map(([k, v]) => `${k} = ${v}`).join(" · ")}
              </span>
            ) : (
              <span className="bancada-entrada-vazia">nenhum valor aplicado — a execução roda com a entrada em branco</span>
            )}
          </div>
        </div>
      )}
      <ExecutorTarefas key={montagem} project={projeto} />
    </div>
  );
};

export default ExecucaoPage;
