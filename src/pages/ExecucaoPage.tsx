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
      .then((d) => {
        const rede = d?.petri_net || d?.petriNet || d;
        if (!rede || !Array.isArray(rede.lugares) || rede.lugares.length === 0) {
          setErro("Este projeto ainda não tem Rede de Petri. Gere a rede na etapa anterior.");
          return;
        }

        // "localhost" pode resolver para IPv6 no navegador, enquanto o servidor
        // de agentes costuma escutar só em IPv4 — a ligação não chega, calada.
        const comConversa = rede.lugares.find((l: any) => /wss?:\/\//.test(String(l?.logica || "")));
        const achado = String(comConversa?.logica || "").match(/wss?:\/\/[^"'`\s)]+/);
        const endereco = achado ? achado[0].replace("//localhost:", "//127.0.0.1:") : "";
        if (endereco) {
          try {
            (window as any).V7_WS_URI = endereco;
            localStorage.setItem("V7_WS_URI", endereco);
          } catch { /* navegador sem armazenamento */ }
        }

        // A tela de referência espera o projeto com a rede em `project_data`,
        // que é o mesmo nome da coluna do banco.
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
