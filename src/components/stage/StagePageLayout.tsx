import React from "react";
// Reutiliza EXATAMENTE o mesmo CSS da página de Especificação / Documentos,
// garantindo uniformidade visual entre todas as etapas do pipeline.
import "../../pages/DocumentsPage.css";
import "./StagePageLayout.css";

export interface StagePageLayoutProps {
  /** Título grande no cabeçalho (ex.: "🧪 Casos de Teste & Validação"). */
  title: string;
  /** Subtítulo/descrição abaixo do título. */
  subtitle?: string;

  /** Botões extras da barra lateral (ex.: seleção de origem, upload). */
  sourceButtons?: React.ReactNode;
  /** Banner da origem selecionada, logo abaixo do header da sidebar. */
  sourceBanner?: React.ReactNode;

  /** Controles de configuração específicos da etapa, acima do textarea. */
  configExtras?: React.ReactNode;

  /** Texto do bloco "Instruções Adicionais". */
  instructions: string;
  onInstructionsChange: (v: string) => void;

  /** Ação do botão "Gerar". */
  onGenerate: () => void;
  generating: boolean;
  generateLabel?: string;
  canGenerate?: boolean;

  /** Ação do botão "Revisar" (opcional). */
  onReview?: () => void;
  reviewing?: boolean;
  canReview?: boolean;

  /** Abre o histórico de versões. */
  onHistory: () => void;

  /** Interface de chat (coluna do meio). */
  chat: React.ReactNode;

  /** Miolo: visualizador do artefato da etapa (coluna direita/principal). */
  children: React.ReactNode;

  /** Modais da página. */
  modals?: React.ReactNode;

  /** Título da lista da sidebar (default: "📁 Origem"). */
  sidebarTitle?: string;

  /** Banner de erro no topo (opcional). */
  error?: React.ReactNode;

  /** Miolo largo (grafo/editor/mockups): chat vira coluna estreita e o
   *  visualizador ocupa a área principal. Default false (etapas de documento). */
  wideViewer?: boolean;

  /** Sidebar de config recolhível: começa recolhida e o miolo usa a largura TOTAL;
   *  a config abre como painel sobreposto (para editores de tela cheia, ex.: Petri). */
  collapsibleSidebar?: boolean;
}

/**
 * Shell de layout padrão de uma etapa do pipeline LangNet.
 *
 * Replica exatamente a estrutura de 3 colunas da página de Especificação
 * (`.documents-page-chat` → `.page-header` + `.documents-chat-container`),
 * reutilizando as classes do `DocumentsPage.css` para uniformidade visual.
 * Somente o miolo (coluna direita `.actions-panel`) varia por etapa.
 */
const StagePageLayout: React.FC<StagePageLayoutProps> = ({
  title,
  subtitle,
  sourceButtons,
  sourceBanner,
  configExtras,
  instructions,
  onInstructionsChange,
  onGenerate,
  generating,
  generateLabel = "🚀 Gerar",
  canGenerate = true,
  onReview,
  reviewing = false,
  canReview = true,
  onHistory,
  chat,
  children,
  modals,
  sidebarTitle = "📁 Origem",
  error,
  wideViewer = false,
  collapsibleSidebar = false,
}) => {
  // Em modo viewer-largo o chat começa recolhido (o miolo/grafo usa a largura toda);
  // nas etapas de documento o chat fica sempre visível.
  const [chatOpen, setChatOpen] = React.useState(!wideViewer);
  const showChat = !wideViewer || chatOpen;
  // Sidebar recolhível: começa fechada; o miolo usa a largura toda e a config abre sobreposta.
  const [sidebarOpen, setSidebarOpen] = React.useState(!collapsibleSidebar);
  return (
    <div className="documents-page-chat">
      <div className="page-header">
        <div className="header-content">
          <h1>{title}</h1>
          {subtitle && <p>{subtitle}</p>}
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {collapsibleSidebar && (
        <button
          className="btn-sidebar-toggle"
          onClick={() => setSidebarOpen((v) => !v)}
          title="Mostrar/ocultar configuração"
        >
          {sidebarOpen ? "✕ Fechar config" : "⚙️ Configuração"}
        </button>
      )}
      <div
        className={`documents-chat-container${wideViewer ? " stage-wide-viewer" : ""}${
          wideViewer && !chatOpen ? " chat-collapsed" : ""
        }${collapsibleSidebar ? " sidebar-collapsible" : ""}${
          collapsibleSidebar && !sidebarOpen ? " sidebar-off" : ""
        }`}
      >
        {/* COLUNA ESQUERDA: origem + configuração */}
        <div className="documents-sidebar">
          <div className="sidebar-header">
            <h3>{sidebarTitle}</h3>
            <div className="header-buttons">
              <button
                className="btn-history-compact"
                onClick={onHistory}
                title="Histórico de versões"
              >
                📜 Histórico
              </button>
              {sourceButtons}
            </div>
          </div>

          {sourceBanner}

          <div className="analysis-config">
            <h4>⚙️ Configuração</h4>

            {configExtras}

            <label>Instruções Adicionais</label>
            <textarea
              value={instructions}
              onChange={(e) => onInstructionsChange(e.target.value)}
              placeholder="Ex: focar em cenários de erro, detalhar validações…"
              rows={3}
            />

            <button
              className="btn-start-analysis"
              onClick={onGenerate}
              disabled={generating || !canGenerate}
            >
              {generating ? "⏳ Gerando..." : generateLabel}
            </button>

            {onReview && (
              <button
                className="btn-review"
                onClick={onReview}
                disabled={reviewing || !canReview}
                title="Revisar e obter sugestões de melhoria"
              >
                {reviewing ? "⏳ Revisando..." : "🔍 Revisar"}
              </button>
            )}

            {wideViewer && (
              <button
                className="btn-chat-toggle"
                onClick={() => setChatOpen((v) => !v)}
                title="Mostrar/ocultar o chat de refino"
              >
                {chatOpen ? "💬 Ocultar chat" : "💬 Refinar com o agente"}
              </button>
            )}
          </div>
        </div>

        {/* COLUNA DO MEIO: chat (recolhível em modo viewer-largo) */}
        {showChat && <div className="chat-area">{chat}</div>}

        {/* COLUNA DIREITA / PRINCIPAL: miolo (visualizador do artefato) */}
        <div className="actions-panel">{children}</div>
      </div>

      {modals}
    </div>
  );
};

export default StagePageLayout;
