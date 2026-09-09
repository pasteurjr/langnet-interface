/**
 * Configurações do Projeto — hoje: o modelo de linguagem que a APLICAÇÃO GERADA vai usar.
 *
 * Por que existe: a escolha do modelo era do arquivo de ambiente da máquina que gerava. O pacote
 * saía sempre apontando para o modelo local, e trocar exigia editar o arquivo à mão depois de
 * gerar. Agora a escolha é do projeto e viaja com o código gerado.
 */
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  obterLlmDoApp, definirLlmDoApp, EscolhaLlm, ProvedorLlm,
} from "../services/projectLlmService";
import "./ProjectSettingsPage.css";

export const ProjectSettingsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [provedores, setProvedores] = useState<Record<string, ProvedorLlm>>({});
  const [escolha, setEscolha] = useState<EscolhaLlm | null>(null);
  const [erro, setErro] = useState("");
  const [aviso, setAviso] = useState("");
  const [ocupado, setOcupado] = useState(false);

  useEffect(() => {
    if (!projectId) return;
    obterLlmDoApp(projectId)
      .then((r) => { setProvedores(r.provedores); setEscolha(r.escolha); })
      .catch((e) => setErro(String(e.message || e)));
  }, [projectId]);

  const gravar = async (cfg: Partial<EscolhaLlm>) => {
    if (!projectId || !escolha) return;
    setOcupado(true); setErro(""); setAviso("");
    try {
      const r = await definirLlmDoApp(projectId, {
        provedor: cfg.provedor ?? escolha.provedor,
        modelo: cfg.modelo ?? escolha.modelo,
        endereco: cfg.endereco ?? escolha.endereco,
        max_tokens: cfg.max_tokens ?? escolha.max_tokens,
      });
      setEscolha(r.escolha);
      setAviso("Escolha gravada. Ela vale para a próxima geração de código deste projeto.");
    } catch (e: any) { setErro(String(e.message || e)); }
    setOcupado(false);
  };

  // Trocar de provedor recarrega modelo e endereço com os padrões dele.
  const trocarProvedor = (p: string) => {
    const base = provedores[p];
    gravar({ provedor: p, modelo: base?.modelo_padrao, endereco: base?.endereco_padrao });
  };

  if (erro && !escolha) return <div className="cfg-projeto"><p className="erro">{erro}</p></div>;
  if (!escolha) return <div className="cfg-projeto"><p>Carregando…</p></div>;

  return (
    <div className="cfg-projeto">
      <h2>Configurações do Projeto</h2>

      <section className="cartao">
        <h3>Modelo de linguagem da aplicação gerada</h3>
        <p className="explica">
          É o modelo que a <b>aplicação</b> vai consultar quando rodar — nos passos de julgamento
          das tarefas e nos agentes. Não é o modelo que o LangNet usa para gerar os artefatos.
          A escolha entra no pacote na próxima geração de código; os outros provedores ficam
          escritos no pacote, comentados, a uma linha de trocar.
        </p>

        <div className="opcoes">
          {Object.entries(provedores).map(([id, p]) => (
            <label key={id} className={`opcao ${escolha.provedor === id ? "escolhida" : ""}`}>
              <input type="radio" name="provedor" checked={escolha.provedor === id}
                     disabled={ocupado} onChange={() => trocarProvedor(id)} />
              <span className="rotulo">{p.rotulo}</span>
              <span className="obs">{p.observacao}</span>
            </label>
          ))}
        </div>

        <div className="campos">
          <label>Modelo</label>
          <input value={escolha.modelo} disabled={ocupado}
                 onChange={(e) => setEscolha({ ...escolha, modelo: e.target.value })}
                 onBlur={(e) => gravar({ modelo: e.target.value })} />

          <label>Endereço</label>
          <input value={escolha.endereco} disabled={ocupado}
                 onChange={(e) => setEscolha({ ...escolha, endereco: e.target.value })}
                 onBlur={(e) => gravar({ endereco: e.target.value })} />

          <label>Tamanho máximo da resposta</label>
          <input type="number" value={escolha.max_tokens} disabled={ocupado}
                 onChange={(e) => setEscolha({ ...escolha, max_tokens: Number(e.target.value) })}
                 onBlur={(e) => gravar({ max_tokens: Number(e.target.value) })} />
        </div>

        <p className="chave">
          A <b>chave</b> deste provedor não é guardada aqui: ela vai como espaço em branco no
          arquivo de ambiente do pacote (<code>{escolha.chave_env}</code>), para ser preenchida
          na máquina onde a aplicação for instalada. Segredo não viaja no código gerado.
        </p>

        {aviso && <p className="aviso">{aviso}</p>}
        {erro && <p className="erro">{erro}</p>}
      </section>
    </div>
  );
};

export default ProjectSettingsPage;
