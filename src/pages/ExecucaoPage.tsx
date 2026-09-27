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

const ExecucaoPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [projeto, setProjeto] = useState<any>(null);
  const [erro, setErro] = useState<string | null>(null);

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

  return (
    <div className="bancada bancada-referencia">
      <ExecutorTarefas project={projeto} />
    </div>
  );
};

export default ExecucaoPage;
