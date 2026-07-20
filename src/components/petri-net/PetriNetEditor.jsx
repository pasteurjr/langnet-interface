import React, { useEffect, useRef, useState, useCallback } from "react";
import * as joint from "jointjs";
import PetriNetSimulator from "./PetriNetSimulator";
import SimulationPanel from "./SimulationPanel";
import GeneratePetriNetModal from "./GeneratePetriNetModal";
import ExecutionPanel from "./ExecutionPanel";
import * as petriNetService from "../../services/petriNetService";

// =========== UTILITY FUNCTIONS ===========

/**
 * Wraps text to fit within a maximum width
 */
/**
 * Wraps text to fit within a maximum width
 */
const wrapText = (text, maxWidth) => {
  // Certifique-se de que text seja uma string e não seja undefined/null
  const safeText = String(text || "").trim();

  if (!safeText || safeText.length <= maxWidth) return safeText;

  const words = safeText.split(" ");
  const lines = [];
  let currentLine = words[0] || "";

  for (let i = 1; i < words.length; i++) {
    if (currentLine.length + words[i].length + 1 <= maxWidth) {
      currentLine += " " + words[i]; // Garante espaço entre palavras
    } else {
      lines.push(currentLine);
      currentLine = words[i] || "";
    }
  }

  if (currentLine) {
    lines.push(currentLine);
  }

  // Usar um separador visível que será interpretado corretamente pelo SVG
  return lines.join("\n");
};

/**
 * Formats tokens for display in place nodes
 */
const formatTokens = (tokens) => {
  if (!tokens && tokens !== 0) return "";
  if (tokens >= 10) return tokens.toString();

  return Array(Math.ceil(tokens / 3))
    .fill(0)
    .map((_, rowIndex) => {
      const start = rowIndex * 3;
      const count = Math.min(3, tokens - start);
      return Array(count).fill("●").join("");
    })
    .join("\n");
};

// =========== UI COMPONENTS ===========

/**
 * Base Modal component that can be reused for all modal dialogs
 */
const Modal = ({ isOpen, onClose, title, children, size = "medium" }) => {
  if (!isOpen) return null;

  const getSizeStyles = () => {
    switch (size) {
      case "large":
        return { maxWidth: "800px", width: "95%" };
      case "small":
        return { maxWidth: "400px", width: "90%" };
      default:
        return { maxWidth: "500px", width: "90%" };
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          padding: "20px",
          borderRadius: "5px",
          position: "relative",
          maxHeight: "90vh",
          overflowY: "auto",
          ...getSizeStyles(),
        }}
      >
        <h2 style={{ marginBottom: "20px" }}>{title}</h2>
        <button
          onClick={onClose}
          style={{
            position: "absolute",
            right: "10px",
            top: "10px",
            border: "none",
            background: "none",
            fontSize: "20px",
            cursor: "pointer",
          }}
        >
          ×
        </button>
        {children}
      </div>
    </div>
  );
};

/**
 * Modal para edição de agente
 */
const EditAgentModal = ({ isOpen, onClose, agent, onSave }) => {
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (agent) {
      setFormData({ ...agent });
    }
  }, [agent]);

  if (!agent) return null;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Editar Agente"
    >
      <div>
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          <div>
            <label>Nome: </label>
            <input
              type="text"
              name="nome"
              value={formData.nome || ""}
              onChange={handleChange}
              style={{ marginLeft: "10px" }}
            />
          </div>
        </div>
        <div
          style={{
            marginTop: "20px",
            display: "flex",
            justifyContent: "flex-end",
            gap: "10px",
          }}
        >
          <button onClick={onClose}>Cancelar</button>
          <button onClick={() => onSave(formData)}>Salvar</button>
        </div>
      </div>
    </Modal>
  );
};

/**
 * Modal for editing place, transition, or arc properties
 */

const EditModal = ({ isOpen, onClose, type, element, onSave }) => {
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (element) {
      // Verificar se o nome tem espaços no elemento original

      setFormData({ ...element });
    }
  }, [element]);

  if (!element) return null;

  const handleChange = (e) => {
    const value =
      e.target.type === "number"
        ? e.target.value === ""
          ? ""
          : Number(e.target.value)
        : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  /**
 * Modal para edição de agente
 */


  /**
   * Menu de contexto específico para agentes
   */
  const AgentContextMenu = ({
    x,
    y,
    onEdit,
    onDelete,
    onClose,
    agent
  }) => {
    return (
      <div
        style={{
          position: "fixed",
          top: y,
          left: x,
          backgroundColor: "white",
          border: "1px solid #ccc",
          borderRadius: "4px",
          boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
          zIndex: 1000,
        }}
      >
        {/* Opção Editar */}
        <div
          style={{
            padding: "8px 12px",
            cursor: "pointer",
            hover: { backgroundColor: "#f5f5f5" },
          }}
          onClick={() => {
            onEdit();
            onClose();
          }}
        >
          Editar
        </div>

        {/* Opção Excluir */}
        <div
          style={{
            padding: "8px 12px",
            cursor: "pointer",
            borderTop: "1px solid #eee",
          }}
          onClick={() => {
            onDelete();
            onClose();
          }}
        >
          Excluir
        </div>
      </div>
    );
  };

  // Generic field creation function
  const createField = (label, name, type, options = {}) => (
    <div>
      <label>{label}: </label>
      <input
        type={type}
        name={name}
        value={formData[name] || (type === "number" ? 0 : "")}
        onChange={handleChange}
        style={{ marginLeft: "10px" }}
        {...options}
      />
    </div>
  );

  // Field creation for textarea
  const createTextareaField = (label, name, placeholder = "", rows = 4) => (
    <div>
      <label>{label}: </label>
      <textarea
        name={name}
        value={formData[name] || ""}
        onChange={handleChange}
        placeholder={placeholder}
        rows={rows}
        style={{ 
          marginLeft: "10px", 
          width: "400px", 
          fontFamily: "monospace",
          fontSize: "12px"
        }}
      />
    </div>
  );

  // Field creation for JSON data
  const createJSONField = (label, name, placeholder = "{}") => {
    const handleJSONChange = (e) => {
      try {
        // Tentar parsear JSON
        const parsed = JSON.parse(e.target.value || "{}");
        setFormData({ ...formData, [name]: parsed });
      } catch (error) {
        // Se inválido, manter como string para mostrar erro
        setFormData({ ...formData, [name]: e.target.value });
      }
    };

    return (
      <div>
        <label>{label}: </label>
        <textarea
          name={name}
          value={typeof formData[name] === 'object' ? JSON.stringify(formData[name], null, 2) : formData[name] || placeholder}
          onChange={handleJSONChange}
          placeholder={placeholder}
          rows={3}
          style={{ 
            marginLeft: "10px", 
            width: "400px", 
            fontFamily: "monospace",
            fontSize: "12px"
          }}
        />
      </div>
    );
  };

  const renderFields = () => {
    switch (type) {
      case "place":
        return (
          <div
            style={{ display: "flex", flexDirection: "column", gap: "15px" }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <h4 style={{ margin: "0 0 10px 0", color: "#333" }}>Propriedades Básicas</h4>
              {createField("Nome", "nome", "text")}
              {createField("Tokens", "tokens", "number", { min: "0" })}
              {createField("Delay (ms)", "delay", "number", { min: "0" })}
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <h4 style={{ margin: "0 0 10px 0", color: "#333" }}>Dados e Lógica</h4>
              {createJSONField("Input Data", "input_data", '{"exemplo": "valor"}')}
              {createJSONField("Output Data", "output_data", '{}')}
              {createTextareaField(
                "Lógica de Processamento",
                "logica",
                "// Código JavaScript\n// Exemplo:\nconst output = utils.clone(input);\noutput.processed = true;\nreturn output;",
                6
              )}
            </div>
            
            <div style={{ padding: "10px", backgroundColor: "#f5f5f5", borderRadius: "4px" }}>
              <small>
                <strong>Dica:</strong> A lógica é executada quando o place recebe tokens.
                Use <code>input</code> para dados de entrada e retorne o resultado como <code>output</code>.
              </small>
            </div>
          </div>
        );

      case "transition":
        return (
          <div
            style={{ display: "flex", flexDirection: "column", gap: "15px" }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <h4 style={{ margin: "0 0 10px 0", color: "#333" }}>Propriedades Básicas</h4>
              {createField("Nome", "nome", "text")}
              {createField("Prioridade", "prioridade", "number", { min: "1" })}
              {createField("Probabilidade", "probabilidade", "number", {
                min: "0",
                max: "1",
                step: "0.1",
              })}
              {createField("Tempo", "tempo", "number", { min: "0", step: "0.1" })}
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <h4 style={{ margin: "0 0 10px 0", color: "#333" }}>Guard (Condição)</h4>
              {createTextareaField(
                "Guard",
                "guard",
                "// Código JavaScript que retorna true/false\n// Exemplo:\ntokens.P1 > 0 && places.P1.input_data.status === 'ready'",
                4
              )}
            </div>
            
            <div style={{ padding: "10px", backgroundColor: "#f5f5f5", borderRadius: "4px" }}>
              <small>
                <strong>Dica:</strong> O guard é avaliado antes do disparo da transição.
                Disponível: <code>tokens</code>, <code>places</code>, <code>utils</code>.
                <br />
                <strong>Exemplos:</strong>
                <br />• <code>{"tokens.P1 >= 2"}</code>
                <br />• <code>utils.hasTokens("P1", 3)</code>
                <br />• <code>{"places.P1.input_data.value > 10"}</code>
              </small>
            </div>
          </div>
        );

      case "arc":
        return (
          <div
            style={{ display: "flex", flexDirection: "column", gap: "10px" }}
          >
            {createField("Peso", "peso", "number", { min: "0" })}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Editar ${type === "place"
        ? "Lugar"
        : type === "transition"
          ? "Transição"
          : "Arco"
        }`}
      size={type === "place" || type === "transition" ? "large" : "medium"}
    >
      <div>
        {renderFields()}
        <div
          style={{
            marginTop: "20px",
            display: "flex",
            justifyContent: "flex-end",
            gap: "10px",
          }}
        >
          <button onClick={onClose}>Cancelar</button>
          <button onClick={() => onSave(formData)}>Salvar</button>
        </div>
      </div>
    </Modal>
  );
};

/**
 * Modal for renaming the Petri net
 */
const RenameModal = ({ isOpen, onClose, onSave, currentName }) => {
  const [name, setName] = useState(currentName);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Nome da Rede">
      <div>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ width: "100%", padding: "5px" }}
        />
        <div
          style={{
            marginTop: "20px",
            display: "flex",
            justifyContent: "flex-end",
            gap: "10px",
          }}
        >
          <button onClick={onClose}>Cancelar</button>
          <button onClick={() => onSave(name)}>Confirmar</button>
        </div>
      </div>
    </Modal>
  );
};

/**
 * Context menu for right-click operations
 */
/**
 * Context menu para operações de clique direito
 * Versão corrigida para lidar adequadamente com elementos de interface
 */
const ContextMenu = ({
  x,
  y,
  onEdit,
  onDelete,
  onExplode,
  onClose,
  element,
  type,
}) => {
  // Determina se é uma transição de interface
  const isInterface =
    type === "transition" && element && element.isInterface === true;

  // Determina se é um lugar (para mostrar opção "Explodir")
  const isPlace = type === "place";
  // Determina se é um agente
  const isAgent = type === "agent";
  return (
    <div
      style={{
        position: "fixed",
        top: y,
        left: x,
        backgroundColor: "white",
        border: "1px solid #ccc",
        borderRadius: "4px",
        boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
        zIndex: 1000,
      }}
    >
      {/* A opção Editar é sempre mostrada */}
      <div
        style={{
          padding: "8px 12px",
          cursor: "pointer",
          hover: { backgroundColor: "#f5f5f5" },
        }}
        onClick={() => {
          onEdit();
          onClose();
        }}
      >
        Editar
      </div>

      {/* A opção Excluir é mostrada apenas se NÃO for uma interface */}
      {!isInterface && (
        <div
          style={{
            padding: "8px 12px",
            cursor: "pointer",
            borderTop: "1px solid #eee",
          }}
          onClick={() => {
            onDelete();
            onClose();
          }}
        >
          Excluir
        </div>
      )}

      {/* A opção Explodir é mostrada apenas para lugares */}
      {isPlace && (
        <div
          style={{
            padding: "8px 12px",
            cursor: "pointer",
            borderTop: "1px solid #eee",
          }}
          onClick={() => {
            onExplode();
            onClose();
          }}
        >
          Explodir
        </div>
      )}
    </div>
  );
};
// =========== MAIN COMPONENT ===========

const PetriNetEditor = ({ projectId, autoconnectUrl }) => {
  // Refs
  const graphRef = useRef(null);
  const paperRef = useRef(null);
  const selectionRectRef = useRef(null);

  // LangNet integration state
  const [generateModalOpen, setGenerateModalOpen] = useState(false);
  const [isLoadingNet, setIsLoadingNet] = useState(false);
  const [executionPanelOpen, setExecutionPanelOpen] = useState(Boolean(autoconnectUrl));
  const executionPanelRef = useRef(null);
  const initialLoadDoneRef = useRef(false);

  // Extrai task_name de um place (do label "Pronto para: X" ou nome direto)
  const extractTaskNameFromPlace = (placeNome) => {
    if (!placeNome) return null;
    const m = placeNome.trim().match(/^(?:pronto para|aguardando)\s*[:\-]\s*(.+)$/i);
    return (m ? m[1] : placeNome).trim();
  };

  // Detecta a task selecionada (apenas se 1 place selecionado e tem task_name razoável)
  const getSelectedTask = () => {
    if (!selectedElements || selectedElements.size !== 1) return null;
    const id = Array.from(selectedElements)[0];
    const place = (petriNet.lugares || []).find((p) => p.id === id);
    if (!place) return null;
    const taskName = extractTaskNameFromPlace(place.nome);
    if (!taskName || taskName.length < 2) return null;
    return { placeId: id, taskName, agentId: place.agentId, inputData: place.input_data || {} };
  };

  const handleDispatchSelectedTask = async () => {
    const sel = getSelectedTask();
    if (!sel) return;
    if (executionPanelRef.current?.triggerTask) {
      try {
        await executionPanelRef.current.triggerTask(sel.taskName, sel.inputData);
      } catch (err) {
        console.error("Erro ao disparar task:", err);
      }
    }
  };

  // Se chegou via ?autoconnect=... abre o painel automaticamente
  useEffect(() => {
    if (autoconnectUrl) setExecutionPanelOpen(true);
  }, [autoconnectUrl]);

  // Petri net state
  const [petriNet, setPetriNet] = useState({
    nome: "Rede de Petri",
    lugares: [],
    transicoes: [],
    arcos: [],
    agentes: [],
  });

  const [agentes, setAgentes] = useState([]);
  const [selectedAgente, setSelectedAgente] = useState(null);
  const [creatingAgent, setCreatingAgent] = useState(false);

  const [resizingAgent, setResizingAgent] = useState(null);
  const [resizeDirection, setResizeDirection] = useState(null);

  // Adicionar estado para o modal de edição de agente
  const [editAgentModalOpen, setEditAgentModalOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState(null);
  /**
 * Função para verificar se um place está dentro de algum agente
 * e atribuir automaticamente o agentId
 */
  const verificarPlaceDentroDeAgente = (placeId, newPosition = null) => {
    // Encontrar o elemento visual do place
    const placeElement = graphRef.current.getCell(placeId);
    if (!placeElement) return;

    // Obter a posição atual do place (ou usar a nova posição fornecida)
    const placePos = newPosition || placeElement.position();

    // Calcular o centro do place (os places têm tamanho 50x50)
    const placeCentro = {
      x: placePos.x + 25, // Metade da largura
      y: placePos.y + 25  // Metade da altura
    };

    // Encontrar todos os agentes visíveis no canvas atual
    const agentes = graphRef.current.getElements().filter(el => el.get('type') === 'agent');

    // Verificar se o centro do place está dentro de algum agente
    let novoAgentId = null;

    for (const agente of agentes) {
      const agentePos = agente.position();
      const agenteSize = agente.size();

      // Verificar se o centro do place está dentro do retângulo do agente
      if (
        placeCentro.x >= agentePos.x &&
        placeCentro.x <= agentePos.x + agenteSize.width &&
        placeCentro.y >= agentePos.y &&
        placeCentro.y <= agentePos.y + agenteSize.height
      ) {
        novoAgentId = agente.get('agentId');
        break;
      }
    }

    // Atualizar o modelo de dados
    setPetriNet(prev => {
      const updatedNet = JSON.parse(JSON.stringify(prev));

      if (currentNetId) {
        // Estamos em uma subnet
        const subnet = findNestedSubnet(updatedNet, currentNetId);
        if (subnet && subnet.lugares) {
          const placeIndex = subnet.lugares.findIndex(p => p.id === placeId);
          if (placeIndex >= 0) {
            // Atualizar o agentId do place
            subnet.lugares[placeIndex].agentId = novoAgentId;
          }
        }
      } else {
        // Estamos na rede principal
        const placeIndex = updatedNet.lugares.findIndex(p => p.id === placeId);
        if (placeIndex >= 0) {
          // Atualizar o agentId do place
          updatedNet.lugares[placeIndex].agentId = novoAgentId;
        }
      }

      return updatedNet;
    });
  };

  /**
   * Função para verificar todos os places após uma modificação em um agente
   * (redimensionamento ou movimentação)
   */
  const verificarPlacesDentroDoAgente = (agentId) => {
    // Encontrar o elemento visual do agente
    const agenteElement = graphRef.current.getElements().find(
      el => el.get('type') === 'agent' && el.get('agentId') === agentId
    );

    if (!agenteElement) return;

    const agentePos = agenteElement.position();
    const agenteSize = agenteElement.size();

    // Encontrar todos os places visíveis no canvas atual
    const places = graphRef.current.getElements().filter(
      el => el.attributes.type === "basic.Circle"
    );

    // Array para armazenar IDs de places que estão dentro do agente
    const placesNoAgente = [];
    // Array para armazenar IDs de places fora do agente que precisam ser limpos
    const placesForaDoAgente = new Set();

    // Verificar cada place
    places.forEach(place => {
      const placePos = place.position();
      const placeCentro = {
        x: placePos.x + 25, // Metade da largura
        y: placePos.y + 25  // Metade da altura
      };

      // Verificar se o centro do place está dentro do retângulo do agente
      if (
        placeCentro.x >= agentePos.x &&
        placeCentro.x <= agentePos.x + agenteSize.width &&
        placeCentro.y >= agentePos.y &&
        placeCentro.y <= agentePos.y + agenteSize.height
      ) {
        placesNoAgente.push(place.id);
      } else {
        placesForaDoAgente.add(place.id);
      }
    });

    // Atualizar o modelo de dados para todos os places
    setPetriNet(prev => {
      const updatedNet = JSON.parse(JSON.stringify(prev));

      // Função recursiva para encontrar e atualizar lugares na subnet correta
      const atualizarLugaresEmSubnet = (net, targetId) => {
        // Caso base: estamos na rede principal
        if (targetId === null) {
          // Atualizar todos os places na rede principal
          net.lugares = net.lugares.map(lugar => {
            if (placesNoAgente.includes(lugar.id)) {
              return { ...lugar, agentId: agentId };
            } else if (lugar.agentId === agentId && placesForaDoAgente.has(lugar.id)) {
              return { ...lugar, agentId: null };
            }
            return lugar;
          });
          return net;
        }

        // Procurar a subnet diretamente neste nível
        for (let i = 0; i < net.lugares.length; i++) {
          if (net.lugares[i].id === targetId) {
            // Encontramos a subnet correta
            if (net.lugares[i].subnet && net.lugares[i].subnet.lugares) {
              // Atualizar places na subnet
              net.lugares[i].subnet.lugares = net.lugares[i].subnet.lugares.map(lugar => {
                if (placesNoAgente.includes(lugar.id)) {
                  return { ...lugar, agentId: agentId };
                } else if (lugar.agentId === agentId && placesForaDoAgente.has(lugar.id)) {
                  return { ...lugar, agentId: null };
                }
                return lugar;
              });
            }
            return net;
          }

          // Verificar se este lugar tem uma subnet para busca recursiva
          if (net.lugares[i].subnet && net.lugares[i].subnet.lugares) {
            const resultado = atualizarLugaresEmSubnet(net.lugares[i].subnet, targetId);
            if (resultado !== net.lugares[i].subnet) {
              // A subnet foi modificada, atualizar o lugar
              net.lugares[i] = {
                ...net.lugares[i],
                subnet: resultado
              };
              return net;
            }
          }
        }

        // Não encontrou a subnet, retornar a rede sem modificações
        return net;
      };

      // Iniciar a busca recursiva a partir da rede principal
      return atualizarLugaresEmSubnet(updatedNet, currentNetId);
    });

    // Log para debug
    console.log(`Verificação do agente ${agentId} concluída. Places dentro: ${placesNoAgente.length}`);
  };

  // Função para salvar as alterações do agente
  const handleSaveAgent = (formData) => {
    console.log("Salvando agente:", formData);

    // Atualizar o modelo de dados
    setPetriNet((prev) => {
      const updatedNet = JSON.parse(JSON.stringify(prev));

      if (currentNetId) {
        // Estamos em uma subnet
        const subnet = findNestedSubnet(updatedNet, currentNetId);
        if (subnet && subnet.agentes) {
          const agentIndex = subnet.agentes.findIndex(a => a.id === editingAgent.id);
          if (agentIndex >= 0) {
            subnet.agentes[agentIndex] = {
              ...subnet.agentes[agentIndex],
              nome: formData.nome
            };
          }
        }
      } else {
        // Estamos na rede principal
        const agentIndex = updatedNet.agentes.findIndex(a => a.id === editingAgent.id);
        if (agentIndex >= 0) {
          updatedNet.agentes[agentIndex] = {
            ...updatedNet.agentes[agentIndex],
            nome: formData.nome
          };
        }
      }

      return updatedNet;
    });

    // Atualizar o nome no elemento visual
    const agentElement = graphRef.current.getElements().find(
      el => el.get('type') === 'agent' && el.get('agentId') === editingAgent.id
    );

    if (agentElement) {
      agentElement.attr({
        text: {
          text: formData.nome,
        }
      });
    }

    setEditAgentModalOpen(false);
  };

  // =========== SIMULATION FUNCTIONS ===========

  const handleStartSimulation = () => {
    try {
      // Obter a rede atual para simulação
      const currentNet = getCurrentNet();
      
      // Verificar se a rede é válida
      if (!currentNet) {
        throw new Error("Não foi possível obter a rede atual para simulação");
      }
      
      // Garantir que as estruturas necessárias existam
      if (!currentNet.lugares) currentNet.lugares = [];
      if (!currentNet.transicoes) currentNet.transicoes = [];
      if (!currentNet.arcos) currentNet.arcos = [];
      
      if (currentNet.lugares.length === 0 && currentNet.transicoes.length === 0) {
        throw new Error("A rede atual está vazia (sem lugares nem transições)");
      }
      
      console.log("Iniciando simulação com rede:", currentNet);
      
      // Criar simulador
      const newSimulator = new PetriNetSimulator(currentNet);
      
      // INICIAR a simulação automaticamente
      newSimulator.startSimulation();
      
      setSimulator(newSimulator);
      
      // Abrir painel de simulação
      setSimulationPanelOpen(true);
      
      // MODO PASSO A PASSO SEMPRE INICIA AUTOMATICAMENTE A SIMULAÇÃO
      // Não precisa de botão "Iniciar" no modo step
      console.log("🚀 Programando atualização visual da simulação em 100ms...");
      setTimeout(() => {
        console.log("🎯 EXECUTANDO ATUALIZAÇÃO VISUAL DA SIMULAÇÃO (MODO STEP)");
        console.log("🎯 Transições na rede:", currentNet.transicoes.map(t => ({ id: t.id, nome: t.nome, isInterface: t.isInterface, interfaceType: t.interfaceType })));
        updateSimulationVisualsWithSimulator(newSimulator, true); // true = modo step
      }, 100);
    } catch (error) {
      console.error("Erro ao iniciar simulação:", error);
      alert(`Erro ao iniciar simulação: ${error.message}`);
    }
  };

  const handleTransitionFiredWithSimulator = (affectedPlaces = [], simRef) => {
    // Atualizar visualização após disparo de transição (com simulator direto)
    if (simRef) {
      console.log("🔥 DISPARO REALIZADO (com simRef) - Atualizando visualização");
      
      // PRIMEIRO: Obter marking vector atualizado do simulador
      const markingVector = simRef.getMarkingVector();
      console.log("📊 Marking Vector após disparo:", markingVector);
      
      // SEGUNDO: Restaurar TODOS os places para azul claro (limpar destaques anteriores)
      const allElements = graphRef.current.getElements();
      allElements.forEach(element => {
        if (element.get('type') === 'basic.Circle') {
          element.attr({
            '.body': { fill: 'lightblue' }
          });
        }
      });
      
      // TERCEIRO: Destacar em azul escuro APENAS os places que receberam tokens neste disparo
      if (affectedPlaces && affectedPlaces.length > 0) {
        console.log("🔵 Destacando places que receberam tokens:", affectedPlaces);
        affectedPlaces.forEach(placeInfo => {
          // Só destacar se o place GANHOU tokens (newTokens > previousTokens)
          if (placeInfo.newTokens > placeInfo.previousTokens) {
            const placeElement = graphRef.current.getCell(placeInfo.id);
            if (placeElement && placeElement.get('type') === 'basic.Circle') {
              console.log(`🔵 Destacando place ${placeInfo.id}: ${placeInfo.previousTokens} → ${placeInfo.newTokens}`);
              placeElement.attr({
                '.body': { fill: 'darkblue' }
              });
            }
          }
        });
      }
      
      // QUARTO: Atualizar TODOS os places visuais com novos tokens
      Object.keys(markingVector).forEach(placeId => {
        const placeElement = graphRef.current.getCell(placeId);
        if (placeElement) {
          const newTokens = markingVector[placeId];
          console.log(`🪙 Atualizando tokens do place ${placeId}: ${newTokens}`);
          
          // Atualizar o elemento visual
          placeElement.attr({
            '.tokens': {
              text: formatTokens(newTokens)
            }
          });
        }
      });
      
      // QUINTO: Atualizar o modelo de dados da rede
      const currentNet = getCurrentNet();
      if (currentNet && currentNet.lugares) {
        currentNet.lugares.forEach(lugar => {
          if (markingVector[lugar.id] !== undefined) {
            lugar.tokens = markingVector[lugar.id];
            console.log(`📝 Modelo atualizado - ${lugar.id}: ${lugar.tokens} tokens`);
          }
        });
      }
      
      // SEXTO: Atualizar círculos verdes das transições aptas
      console.log("🔄 Atualizando círculos verdes após disparo");
      updateSimulationVisualsWithSimulator(simRef, true); // sempre step mode nos disparos manuais
    }
  };

  const handleTransitionFired = (affectedPlaces = []) => {
    // Atualizar visualização após disparo de transição
    if (simulator) {
      console.log("🔥 DISPARO REALIZADO - Atualizando visualização");
      
      // PRIMEIRO: Obter marking vector atualizado do simulador
      const markingVector = simulator.getMarkingVector();
      console.log("📊 Marking Vector após disparo:", markingVector);
      
      // SEGUNDO: Restaurar TODOS os places para azul claro (limpar destaques anteriores)
      const allElements = graphRef.current.getElements();
      allElements.forEach(element => {
        if (element.get('type') === 'basic.Circle') {
          console.log(`🔵 Restaurando place ${element.get('id')} para azul claro`);
          element.attr({
            '.body': { fill: 'lightblue' }
          });
        }
      });
      
      // TERCEIRO: Destacar em azul escuro APENAS os places que receberam tokens neste disparo
      if (affectedPlaces && affectedPlaces.length > 0) {
        console.log("🔵 Destacando places que receberam tokens:", affectedPlaces);
        affectedPlaces.forEach(placeInfo => {
          // Só destacar se o place GANHOU tokens (newTokens > previousTokens)
          if (placeInfo.newTokens > placeInfo.previousTokens) {
            const placeElement = graphRef.current.getCell(placeInfo.id);
            if (placeElement && placeElement.get('type') === 'basic.Circle') {
              console.log(`🔵 Destacando place ${placeInfo.id}: ${placeInfo.previousTokens} → ${placeInfo.newTokens}`);
              placeElement.attr({
                '.body': { fill: 'darkblue' }
              });
            }
          }
        });
      }
      
      // QUARTO: Atualizar TODOS os places visuais com novos tokens
      Object.keys(markingVector).forEach(placeId => {
        const placeElement = graphRef.current.getCell(placeId);
        if (placeElement) {
          const newTokens = markingVector[placeId];
          console.log(`🪙 Atualizando tokens do place ${placeId}: ${newTokens}`);
          
          // Atualizar o elemento visual
          placeElement.attr({
            '.tokens': {
              text: formatTokens(newTokens)
            }
          });
        }
      });
      
      // QUINTO: Atualizar o modelo de dados da rede
      const currentNet = getCurrentNet();
      if (currentNet && currentNet.lugares) {
        currentNet.lugares.forEach(lugar => {
          if (markingVector[lugar.id] !== undefined) {
            lugar.tokens = markingVector[lugar.id];
            console.log(`📝 Modelo atualizado - ${lugar.id}: ${lugar.tokens} tokens`);
          }
        });
      }
      
      // SEXTO: Atualizar círculos verdes das transições aptas
      if (simulator && simulator.isSimulating) {
        console.log("🔄 Atualizando círculos verdes após disparo");
        updateSimulationVisualsWithSimulator(simulator, true); // sempre step mode nos disparos manuais
      } else if (simulator && !simulator.isSimulating) {
        console.log("🔄 Simulação parada - limpando visuais");
        clearAllSimulationVisuals();
      } else {
        // Caso especial: forçar atualização mesmo se simulator não existe
        console.log("🔄 Forçando atualização visual");
        setTimeout(() => {
          if (simulator && simulator.isSimulating) {
            updateSimulationVisualsWithSimulator(simulator, true);
          }
        }, 100);
      }
    }
  };

  // Função para adicionar círculo verde com revólver na extremidade da transição
  const addGreenCircleToTransition = (transitionElement, transition, isStepMode, simRef) => {
    try {
      const view = transitionElement.findView(paperRef.current);
      if (!view || !view.el) {
        console.log(`❌ Não encontrou view para ${transition.id}`);
        return;
      }

      // Remover círculos anteriores
      const existingCircles = view.el.querySelectorAll('.green-gun-circle');
      existingCircles.forEach(circle => circle.remove());

      console.log(`🟢 Adicionando círculo verde para ${transition.id} (step: ${isStepMode})`);

      // Obter posição e tamanho da transição
      const bbox = transitionElement.getBBox();
      
      // Criar grupo para o círculo verde
      const circleGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      circleGroup.setAttribute('class', 'green-gun-circle');
      circleGroup.setAttribute('transform', `translate(${bbox.width + 5}, ${bbox.height / 2})`);
      
      // Criar círculo verde
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', '12');
      circle.setAttribute('fill', 'green');
      circle.setAttribute('stroke', 'darkgreen');
      circle.setAttribute('stroke-width', '2');
      
      // Criar texto do revólver
      const gunText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      gunText.textContent = '🔫';
      gunText.setAttribute('x', '0');
      gunText.setAttribute('y', '0');
      gunText.setAttribute('text-anchor', 'middle');
      gunText.setAttribute('dominant-baseline', 'central');
      gunText.setAttribute('font-size', '12');
      gunText.setAttribute('fill', 'white');
      
      // Adicionar elementos ao grupo
      circleGroup.appendChild(circle);
      circleGroup.appendChild(gunText);
      
      // Configurar interação
      if (isStepMode) {
        // Modo passo a passo: clicável
        circleGroup.style.cursor = 'pointer';
        circleGroup.style.pointerEvents = 'all';
        circleGroup.onclick = (e) => {
          e.stopPropagation();
          console.log(`🟢 CLIQUE NO CÍRCULO VERDE: ${transition.id}`);
          console.log(`🟢 Usando simulator direto:`, !!simRef);
          try {
            handleGunClickWithSimulator(transition.id, simRef);
            console.log(`🟢 ✅ handleGunClickWithSimulator executado com sucesso`);
          } catch (error) {
            console.error(`🟢 ❌ Erro no handleGunClickWithSimulator:`, error);
          }
        };
        
        // Efeito hover
        circleGroup.onmouseenter = () => {
          circle.setAttribute('fill', 'lightgreen');
        };
        circleGroup.onmouseleave = () => {
          circle.setAttribute('fill', 'green');
        };
      } else {
        // Modo automático: não clicável
        circleGroup.style.pointerEvents = 'none';
        circleGroup.style.opacity = '0.7';
      }
      
      // Adicionar ao elemento da transição
      const svg = view.el.querySelector('g');
      if (svg) {
        svg.appendChild(circleGroup);
        console.log(`🟢 ✅ Círculo verde adicionado para ${transition.id}`);
      } else {
        console.error(`❌ Não encontrou grupo SVG para ${transition.id}`);
      }
      
    } catch (error) {
      console.error(`❌ Erro ao adicionar círculo verde para ${transition.id}:`, error);
    }
  };

  // Função para remover todos os círculos verdes
  const removeAllGreenCircles = () => {
    const allElements = graphRef.current.getElements();
    allElements.forEach(element => {
      if (element.get('type') === 'basic.Rect') { // transições
        try {
          const view = element.findView(paperRef.current);
          if (view && view.el) {
            const circles = view.el.querySelectorAll('.green-gun-circle');
            circles.forEach(circle => circle.remove());
          }
        } catch (error) {
          // Ignorar erros
        }
      }
    });
    console.log("🧹 Todos os círculos verdes removidos");
  };

  // Função para limpar visual completamente (cores originais)
  const clearAllSimulationVisuals = () => {
    console.log("🧹 LIMPANDO TODOS OS VISUAIS DA SIMULAÇÃO");
    
    // Remover todos os círculos verdes
    removeAllGreenCircles();
    
    const allElements = graphRef.current.getElements();
    allElements.forEach(element => {
      if (element.get('type') === 'basic.Rect') {
        // Restaurar cor original das transições
        element.attr({
          rect: { 
            fill: '#90EE90',  // Verde claro normal
            stroke: '#000000',  // Borda preta normal
            'stroke-width': 1   // Espessura normal
          }
        });
      } else if (element.get('type') === 'basic.Circle') {
        // Restaurar cor original dos places (incluindo os azul escuro)
        console.log(`🎨 Restaurando cores do place: ${element.get('id')}`);
        element.attr({
          '.body': { 
            fill: 'lightblue',    // Azul claro normal
            stroke: '#000000',    // Borda preta normal
            'stroke-width': 1     // Espessura normal
          }
        });
      }
    });
    
    console.log("✅ Visual limpo - cores originais restauradas");
  };

  const updateSimulationVisualsWithSimulator = (simRef, isStepMode = true) => {
    if (!simRef) {
      // Se não há simulador, limpar tudo
      clearAllSimulationVisuals();
      return;
    }
    
    console.log("🎨 Atualizando visual da simulação com simulador direto");
    console.log("🎯 Modo:", isStepMode ? "PASSO A PASSO" : "AUTOMÁTICO");
    
    // Se a simulação não estiver ativa, limpar visuais
    if (!simRef.isSimulating) {
      console.log("⏸️ Simulação não ativa - limpando visuais");
      clearAllSimulationVisuals();
      return;
    }
    
    // Destacar transições aptas em VERDE com ícone de REVÓLVER (SÓ no passo a passo)
    const enabledTransitions = simRef.getEnabledTransitions();
    console.log("🟢 Transições aptas (direto):", enabledTransitions);
    console.log("🟢 IDs das transições aptas:", enabledTransitions.map(t => t.id));
    
    if (enabledTransitions.length === 0) {
      console.warn("⚠️ NENHUMA TRANSIÇÃO APTA ENCONTRADA!");
      console.log("📊 Marking vector atual:", simRef.getMarkingVector());
      console.log("🔍 Estado da simulação:", simRef.getSimulationState());
    }
    
    // Remover círculos verdes existentes e aplicar cores básicas
    removeAllGreenCircles();
    
    const allElements = graphRef.current.getElements();
    allElements.forEach(element => {
      if (element.get('type') === 'basic.Rect') {
        element.attr({
          rect: { 
            fill: '#90EE90',  // Verde claro normal
            stroke: '#000000',  // Borda preta
            'stroke-width': 1   // Espessura normal
          }
        });
      } else if (element.get('type') === 'basic.Circle') {
        // MANTER AZUL PARA PLACES COM TOKENS
        const placeData = getCurrentNet().lugares.find(l => l.id === element.get('id'));
        const hasTokens = placeData && placeData.tokens > 0;
        const fillColor = hasTokens ? 'blue' : 'lightblue';
        
        console.log(`🎨 Place ${element.get('id')}: ${placeData?.tokens || 0} tokens → ${fillColor}`);
        element.attr({
          '.body': { 
            fill: fillColor,      // Azul se tem tokens, azul claro se não tem
            stroke: '#000000',    // Borda preta normal
            'stroke-width': 1     // Espessura normal
          }
        });
      }
    });
    
    // Destacar transições aptas
    enabledTransitions.forEach((transition, index) => {
      console.log(`🔍 Processando transição apta ${index}: ${transition.id}/${transition.nome}`);
      
      const transitionElement = graphRef.current.getCell(transition.id);
      console.log(`🔍 Elemento encontrado para ${transition.id}:`, !!transitionElement);
      
      if (transitionElement && transitionElement.get('type') === 'basic.Rect') {
        console.log(`🎯 APLICANDO VISUAL para transição apta: ${transition.id}`);
        
        // Aplicar visual de transição apta
        transitionElement.attr({
          'rect': { 
            fill: '#32CD32',
            stroke: '#FF0000', 
            'stroke-width': 4
          }
        });
        
        console.log(`✅ Visual aplicado para ${transition.id}`);
        
        // ADICIONAR CÍRCULO VERDE COM REVÓLVER na extremidade da transição
        addGreenCircleToTransition(transitionElement, transition, isStepMode, simRef);
      } else {
        console.error(`❌ Elemento não encontrado ou tipo incorreto para ${transition.id}`);
      }
    });
  };

  const updateSimulationVisuals = () => {
    if (!simulator) return;
    
    console.log("🎨 Atualizando visual da simulação");
    
    // Restaurar cores normais para todos os elementos
    const allElements = graphRef.current.getElements();
    
    allElements.forEach(element => {
      if (element.get('type') === 'transition') {
        element.attr({
          rect: { fill: '#90EE90' } // Cor normal das transições
        });
        // Remover ícone de revólver existente
        element.attr({
          'text.gun': { text: '' }
        });
      } else if (element.get('type') === 'place') {
        element.attr({
          '.body': { fill: 'lightblue' } // Cor normal dos places
        });
      }
    });

    // Destacar places com tokens em AZUL
    const currentNet = getCurrentNet();
    if (currentNet && currentNet.lugares) {
      currentNet.lugares.forEach(lugar => {
        if (lugar.tokens > 0) {
          const placeElement = graphRef.current.getCell(lugar.id);
          if (placeElement) {
            placeElement.attr({
              '.body': { fill: '#4169E1' } // AZUL para places com tokens
            });
          }
        }
      });
    }
    
    // Destacar transições aptas em VERDE com ícone de REVÓLVER
    const enabledTransitions = simulator.getEnabledTransitions();
    console.log("🟢 Transições aptas:", enabledTransitions.map(t => t.id));
    
    enabledTransitions.forEach(transition => {
      const transitionElement = graphRef.current.getCell(transition.id);
      if (transitionElement && transitionElement.get('type') === 'transition') {
        // Verde para transições aptas
        transitionElement.attr({
          rect: { fill: '#32CD32' }
        });
        
        // Adicionar texto de revólver simples
        transitionElement.attr({
          'text.gun': {
            text: '🔫',
            x: 40,
            y: -10,
            'font-size': 12,
            cursor: 'pointer'
          }
        });
      }
    });
  };

  // Função simplificada removida - usando abordagem mais simples

  const handleGunClickWithSimulator = (transitionId, simRef) => {
    console.log(`🔫 CLIQUE NO REVÓLVER (com simulator) - Disparando transição: ${transitionId}`);
    console.log(`🔫 SimRef existe:`, !!simRef);
    console.log(`🔫 SimRef.isSimulating:`, simRef?.isSimulating);
    console.log(`🔫 Transição está apta:`, simRef?.isTransitionEnabled(transitionId));
    
    if (simRef && simRef.isTransitionEnabled(transitionId)) {
      try {
        // Destacar a transição sendo disparada
        handleTransitionHighlight(transitionId);
        
        // Disparar a transição
        const result = simRef.fireTransition(transitionId);
        console.log("🎯 Resultado do disparo:", result);
        
        // Obter places afetados para passar para a visualização
        const lastLogEntry = simRef.simulationLog[simRef.simulationLog.length - 1];
        const affectedPlaces = lastLogEntry ? lastLogEntry.affectedPlaces : [];
        
        // Atualizar a visualização
        handleTransitionFiredWithSimulator(affectedPlaces, simRef);
        
        // Forçar atualização do simulator global para mostrar o log
        setSimulator(simRef);
        
        // Remover destaque após 2 segundos (mesmo tempo dos disparos automáticos)
        setTimeout(() => {
          if (simRef && simRef.isSimulating) {
            updateSimulationVisualsWithSimulator(simRef, true);
          }
        }, 2000);
        
      } catch (error) {
        console.error('❌ Erro ao disparar transição:', error);
        alert(`Erro: ${error.message}`);
      }
    } else {
      console.warn(`⚠️ Transição ${transitionId} não está apta para disparar`);
    }
  };

  const handleGunClick = (transitionId) => {
    console.log(`🔫 CLIQUE NO REVÓLVER - Disparando transição: ${transitionId}`);
    console.log(`🔫 Simulator existe:`, !!simulator);
    console.log(`🔫 Simulator.isSimulating:`, simulator?.isSimulating);
    console.log(`🔫 Transição está apta:`, simulator?.isTransitionEnabled(transitionId));
    
    if (simulator && simulator.isTransitionEnabled(transitionId)) {
      try {
        // Destacar a transição sendo disparada
        handleTransitionHighlight(transitionId);
        
        // Disparar a transição
        const result = simulator.fireTransition(transitionId);
        console.log("🎯 Resultado do disparo:", result);
        
        // Obter places afetados para passar para a visualização
        const lastLogEntry = simulator.simulationLog[simulator.simulationLog.length - 1];
        const affectedPlaces = lastLogEntry ? lastLogEntry.affectedPlaces : [];
        
        // Atualizar a visualização
        handleTransitionFired(affectedPlaces);
        
        // Remover destaque após 2 segundos (mesmo tempo dos disparos automáticos)
        setTimeout(() => {
          if (simulator && simulator.isSimulating) {
            updateSimulationVisualsWithSimulator(simulator, true);
          }
        }, 2000);
        
      } catch (error) {
        console.error('❌ Erro ao disparar transição:', error);
        alert(`Erro: ${error.message}`);
      }
    } else {
      console.warn(`⚠️ Transição ${transitionId} não está apta para disparar`);
    }
  };

  const handleTransitionHighlight = (transitionId) => {
    // Apenas destacar a transição sendo disparada em vermelho
    if (transitionId) {
      const element = graphRef.current.getCell(transitionId);
      if (element && element.get('type') === 'basic.Rect') {
        element.attr({
          rect: { fill: '#FF0000' } // VERMELHO para transição sendo disparada
        });
      }
    }

    setHighlightedTransition(transitionId);
  };

  const getCurrentNet = () => {
    if (currentNetId) {
      // Retornar subnet atual
      const subnet = findNestedSubnet(petriNet, currentNetId);
      console.log("Subnet encontrada para simulação:", subnet);
      console.log("currentNetId:", currentNetId);
      return subnet;
    }
    // Retornar rede principal
    console.log("Retornando rede principal para simulação:", petriNet);
    return petriNet;
  };

  // =========== END SIMULATION FUNCTIONS ===========


  // Counters
  const [placeCount, setPlaceCount] = useState(1);
  const [transitionCount, setTransitionCount] = useState(1);

  // UI State
  const [selectedObject, setSelectedObject] = useState(null);
  const [sourceElement, setSourceElement] = useState(null);
  const [selectedElements, setSelectedElements] = useState(new Set());
  const [isSelecting, setIsSelecting] = useState(false);
  const [dragStartPositions, setDragStartPositions] = useState(null);

  // Modal states
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [renameModalOpen, setRenameModalOpen] = useState(false);
  const [jsonModalOpen, setJsonModalOpen] = useState(false);
  const [pythonModalOpen, setPythonModalOpen] = useState(false);
  const [editingElement, setEditingElement] = useState(null);
  const [editingType, setEditingType] = useState(null);
  const [netStack, setNetStack] = useState([]);
  const [currentNetId, setCurrentNetId] = useState(null); // null = rede principal

  // Context menu state
  const [contextMenu, setContextMenu] = useState({
    visible: false,
    x: 0,
    y: 0,
    element: null,
    type: null,
  });

  // File handling state
  const [currentFile, setCurrentFile] = useState(null);
  const [saveAction, setSaveAction] = useState(null);

  // Simulation states
  const [simulator, setSimulator] = useState(null);
  const [simulationPanelOpen, setSimulationPanelOpen] = useState(false);
  const [highlightedTransition, setHighlightedTransition] = useState(null);
  const [loadedFile, setLoadedFile] = useState(null);

  // Edit operations state
  const [clipboard, setClipboard] = useState(null);

  // History state
  const [undoStack, setUndoStack] = useState([]);
  const [redoStack, setRedoStack] = useState([]);
  const MAX_HISTORY = 50;

  // =========== HISTORY MANAGEMENT (UNDO/REDO) ===========

  /**
   * Records an action for the undo/redo history
   */
  const recordAction = (actionType, data) => {
    setUndoStack((prev) => {
      const newStack = [...prev, { actionType, data }];
      if (newStack.length > MAX_HISTORY) newStack.shift();
      return newStack;
    });
    setRedoStack([]); // Clear redo stack when a new action is recorded
  };

  /**
   * Função para explodir um lugar em uma sub-rede
   */

  /**
   * Função auxiliar para encontrar uma sub-rede em qualquer nível da hierarquia
   * Esta função deve estar disponível globalmente no componente
   */
  const findNestedSubnet = (net, placeId, path = []) => {
    // Verificar se o ID do lugar atual corresponde ao ID buscado
    if (placeId === null) return net; // Caso especial: buscar a rede principal

    // Procurar o lugar diretamente neste nível
    const place = net.lugares.find((l) => l.id === placeId);
    if (place) {
      // Garantir que a subnet existe
      if (!place.subnet)
        place.subnet = {
          nome: `Sub-rede de ${place.nome || placeId}`,
          lugares: [],
          transicoes: [],
          arcos: [],
          entradas: [],
          saidas: [],
        };
      return place.subnet;
    }

    // Se não encontramos neste nível, precisamos examinar cada lugar com sub-rede
    for (let i = 0; i < (net.lugares || []).length; i++) {
      const lugar = net.lugares[i];
      if (lugar.subnet && lugar.subnet.lugares) {
        // Evitar loops infinitos verificando se já visitamos este lugar
        if (path.includes(lugar.id)) continue;

        // Procurar recursivamente nesta sub-rede
        const subnet = findNestedSubnet(lugar.subnet, placeId, [
          ...path,
          lugar.id,
        ]);

        if (subnet && Object.keys(subnet).length > 0) {
          return subnet;
        }
      }
    }

    // Retornar um objeto vazio estruturado em vez de um objeto vazio simples
    return {
      nome: "",
      lugares: [],
      transicoes: [],
      arcos: [],
      entradas: [],
      saidas: [],
    };
  };
  /**
   * Função para encontrar a rede ou subnet que contém um determinado lugar
   * Retorna { net, parent } onde net é a rede contendo o lugar e parent é o ID do lugar pai (se aninhado)
   */
  const findContainingNet = (net, placeId, parentId = null, path = []) => {
    // Verificar se o lugar está diretamente neste nível
    if (net.lugares && net.lugares.some((l) => l.id === placeId)) {
      return { net, parent: parentId };
    }

    // Se não encontramos neste nível, procurar em cada subnet
    for (let i = 0; i < (net.lugares || []).length; i++) {
      const lugar = net.lugares[i];
      if (lugar.subnet && lugar.subnet.lugares) {
        // Evitar loops infinitos
        if (path.includes(lugar.id)) continue;

        // Procurar recursivamente
        const result = findContainingNet(lugar.subnet, placeId, lugar.id, [
          ...path,
          lugar.id,
        ]);

        if (result.net) {
          return result;
        }
      }
    }

    return { net: null, parent: null };
  };
  const updateSubnetInterfaces = (arco) => {
    // Verificar se o arco conecta um lugar que tem sub-rede
    const { origem, destino } = arco;

    // Encontrar o contexto correto para o arco
    const { net: sourceNet } = findContainingNet(petriNet, origem);
    const { net: targetNet } = findContainingNet(petriNet, destino);

    // Função auxiliar para atualizar recursivamente a rede
    const updatePetriNetWithSubnet = (net, placeId, updatedSubnet) => {
      // Procurar o lugar diretamente neste nível
      const placeIndex = net.lugares.findIndex((l) => l.id === placeId);

      if (placeIndex >= 0) {
        // Encontramos o lugar neste nível, atualizar sua sub-rede
        const updatedNet = { ...net };
        updatedNet.lugares = [...net.lugares];
        // Preservar os agentes existentes se a subnet for atualizada
        const agentesAPreservar = net.lugares[placeIndex].subnet?.agentes || [];
        updatedNet.lugares[placeIndex] = {
          ...net.lugares[placeIndex],
          subnet: updatedSubnet,
          agentes: agentesAPreservar

        };
        return updatedNet;
      }

      // Se não encontramos neste nível, procurar recursivamente nas sub-redes
      const updatedNet = { ...net };
      updatedNet.lugares = net.lugares.map((lugar) => {
        if (lugar.subnet && lugar.subnet.lugares) {
          const updatedPlace = { ...lugar };
          const updatedSubnetResult = updatePetriNetWithSubnet(
            lugar.subnet,
            placeId,
            updatedSubnet
          );

          // Se a subnet foi atualizada, atualizar este lugar
          if (updatedSubnetResult !== lugar.subnet) {
            updatedPlace.subnet = updatedSubnetResult;
            return updatedPlace;
          }
        }
        return lugar;
      });

      return updatedNet;
    };

    // Verificar se a origem é um lugar com sub-rede
    if (sourceNet) {
      const origemElement = sourceNet.lugares.find((l) => l.id === origem);
      if (origemElement && origemElement.subnet) {
        console.log(
          "Atualizando interfaces de saída da sub-rede do lugar:",
          origem
        );

        // Trabalhar com uma cópia para evitar problemas de referência
        const updatedSubnet = JSON.parse(JSON.stringify(origemElement.subnet));

        // Adicionar a transição de destino às saídas da sub-rede, se ainda não estiver lá
        if (!updatedSubnet.saidas) updatedSubnet.saidas = [];
        if (!updatedSubnet.saidas.includes(destino)) {
          updatedSubnet.saidas.push(destino);

          // Atualizar o modelo
          setPetriNet((prev) =>
            updatePetriNetWithSubnet(prev, origem, updatedSubnet)
          );
        }
      }
    }

    // Verificar se o destino é um lugar com sub-rede
    if (targetNet) {
      const destinoElement = targetNet.lugares.find((l) => l.id === destino);
      if (destinoElement && destinoElement.subnet) {
        console.log(
          "Atualizando interfaces de entrada da sub-rede do lugar:",
          destino
        );

        // Trabalhar com uma cópia para evitar problemas de referência
        const updatedSubnet = JSON.parse(JSON.stringify(destinoElement.subnet));

        // Adicionar a transição de origem às entradas da sub-rede, se ainda não estiver lá
        if (!updatedSubnet.entradas) updatedSubnet.entradas = [];
        if (!updatedSubnet.entradas.includes(origem)) {
          updatedSubnet.entradas.push(origem);

          // Atualizar o modelo
          setPetriNet((prev) =>
            updatePetriNetWithSubnet(prev, destino, updatedSubnet)
          );
        }
      }
    }
  };
  const createArcWithConsistentWeight = (origem, destino) => {
    // Verificar se é um arco para ou de uma interface
    if (currentNetId) {
      const subnet = findNestedSubnet(petriNet, currentNetId);
      if (subnet && subnet.transicoes) {
        const interfaces = subnet.transicoes.filter((t) => t.isInterface);

        // Verificar se a origem é uma interface
        const sourceInterface = interfaces.find((t) => t.id === origem);
        if (
          sourceInterface &&
          (sourceInterface.interfaceType === "entrada" ||
            sourceInterface.interfaceType === "bidirecional")
        ) {
          // Se a interface tem peso zero, o arco deve ter peso zero
          if (sourceInterface.peso_in === 0) {
            return { origem, destino, peso: 0 };
          }
        }

        // Verificar se o destino é uma interface
        const targetInterface = interfaces.find((t) => t.id === destino);
        if (
          targetInterface &&
          (targetInterface.interfaceType === "saida" ||
            targetInterface.interfaceType === "bidirecional")
        ) {
          // Se a interface tem peso zero, o arco deve ter peso zero
          if (targetInterface.peso_out === 0) {
            return { origem, destino, peso: 0 };
          }
        }
      }
    }

    // Caso padrão: peso 1
    return { origem, destino, peso: 1 };
  };
  const checkInterfaceWeightLimits = (subnet) => {
    if (!subnet.transicoes || !subnet.arcos) return true;

    const interfaces = subnet.transicoes.filter((t) => t.isInterface);

    // Para cada interface, verificar consistência de pesos
    for (const interfaceT of interfaces) {
      const interfaceId = interfaceT.id;

      // Calcular peso utilizado na entrada (arcos saindo da interface)
      if (
        interfaceT.interfaceType === "entrada" ||
        interfaceT.interfaceType === "bidirecional"
      ) {
        const outgoingArcs = subnet.arcos.filter(
          (a) => a.origem === interfaceId
        );

        // Caso especial: peso_in = 0
        if (interfaceT.peso_in === 0) {
          // Se peso é zero, permitir apenas um arco com peso zero
          if (outgoingArcs.length > 1) {
            return {
              valid: false,
              message: `Interface ${interfaceT.nome} tem peso zero, permitido apenas um arco`,
            };
          }

          // Se já existe um arco, garantir que seu peso seja zero
          if (outgoingArcs.length === 1 && outgoingArcs[0].peso !== 0) {
            return {
              valid: false,
              message: `Interface ${interfaceT.nome} tem peso zero, o arco deve ter peso zero`,
            };
          }

          // Atualizar peso restante (sempre 0 neste caso)
          interfaceT.peso_in_restante = 0;
        }
        // Caso normal: peso_in > 0
        else {
          const usedWeight = outgoingArcs.reduce(
            (sum, arc) => sum + (arc.peso || 1),
            0
          );

          // Verificar se excede o limite
          if (usedWeight > interfaceT.peso_in) {
            return {
              valid: false,
              message: `A soma dos pesos dos arcos saindo da interface ${interfaceT.nome} (${usedWeight}) excede o limite (${interfaceT.peso_in})`,
            };
          }

          // Atualizar peso restante
          interfaceT.peso_in_restante = interfaceT.peso_in - usedWeight;

          // Verificar se está próximo do limite
          if (interfaceT.peso_in_restante === 1) {
            console.warn(
              `Apenas 1 token restante para interface de entrada ${interfaceT.nome}`
            );
          }
        }
      }

      // Calcular peso utilizado na saída (arcos entrando na interface)
      if (
        interfaceT.interfaceType === "saida" ||
        interfaceT.interfaceType === "bidirecional"
      ) {
        const incomingArcs = subnet.arcos.filter(
          (a) => a.destino === interfaceId
        );

        // Caso especial: peso_out = 0
        if (interfaceT.peso_out === 0) {
          // Se peso é zero, permitir apenas um arco com peso zero
          if (incomingArcs.length > 1) {
            return {
              valid: false,
              message: `Interface ${interfaceT.nome} tem peso zero, permitido apenas um arco`,
            };
          }

          // Se já existe um arco, garantir que seu peso seja zero
          if (incomingArcs.length === 1 && incomingArcs[0].peso !== 0) {
            return {
              valid: false,
              message: `Interface ${interfaceT.nome} tem peso zero, o arco deve ter peso zero`,
            };
          }

          // Atualizar peso restante (sempre 0 neste caso)
          interfaceT.peso_out_restante = 0;
        }
        // Caso normal: peso_out > 0
        else {
          const usedWeight = incomingArcs.reduce(
            (sum, arc) => sum + (arc.peso || 1),
            0
          );

          // Verificar se excede o limite
          if (usedWeight > interfaceT.peso_out) {
            return {
              valid: false,
              message: `A soma dos pesos dos arcos entrando na interface ${interfaceT.nome} (${usedWeight}) excede o limite (${interfaceT.peso_out})`,
            };
          }

          // Atualizar peso restante
          interfaceT.peso_out_restante = interfaceT.peso_out - usedWeight;

          // Verificar se está próximo do limite
          if (interfaceT.peso_out_restante === 1) {
            console.warn(
              `Apenas 1 token restante para interface de saída ${interfaceT.nome}`
            );
          }
        }
      }
    }

    return { valid: true };
  };
  const handleExplodePetriNet = (placeElement) => {
    if (!placeElement || placeElement.id === undefined) return;
    console.log('===== INICIANDO EXPLOSÃO =====');
    console.log('Estado inicial da rede:', JSON.stringify(petriNet, null, 2));
    console.log('Explodindo lugar:', placeElement.id);

    // Encontrar o contexto que contém o lugar a ser explodido
    const { net: containingNet, parent: parentId } = findContainingNet(
      petriNet,
      placeElement.id
    );

    if (!containingNet) {
      console.error("Contexto contendo o lugar alvo não encontrado");
      return;
    }

    // Identificar o lugar a ser explodido no contexto correto
    const targetPlace = containingNet.lugares.find(
      (l) => l.id === placeElement.id
    );
    if (!targetPlace) {
      console.error("Lugar alvo não encontrado no contexto");
      return;
    }
    // IMPORTANTE: Obter informações do elemento visual também
    const visualElement = graphRef.current.getCell(placeElement.id);
    let visualTokens = 0;

    if (visualElement) {
      const tokensText = visualElement.attr(".tokens/text") || "";
      if (tokensText.includes("●")) {
        // Contar marcadores visuais
        visualTokens = (tokensText.match(/●/g) || []).length;
      } else {
        // Ou usar o valor numérico
        visualTokens = parseInt(tokensText) || 0;
      }
    }

    // Usar tokens visuais ou do modelo, o que for mais recente
    const currentTokens =
      visualTokens > 0 ? visualTokens : targetPlace.tokens || 0;
    console.log("Tokens do lugar a ser explodido:", currentTokens);

    // Verificar se o lugar já tem uma sub-rede definida
    let subnet = targetPlace.subnet || {};
    // Preservar as propriedades das interfaces existentes
    // Preservar as propriedades das interfaces existentes
    // Preservar as propriedades das interfaces existentes
    if (subnet.transicoes && subnet.transicoes.some((t) => t.isInterface)) {
      console.log("Preservando propriedades das interfaces existentes");

      const arcWeights = new Map();
      containingNet.arcos.forEach((arco) => {
        if (
          arco.origem === placeElement.id ||
          arco.destino === placeElement.id
        ) {
          // Criar uma chave única para o arco
          const key =
            arco.origem === placeElement.id
              ? `out_${arco.destino}`
              : `in_${arco.origem}`;
          // Armazenar o peso explicitamente, mesmo se for zero
          arcWeights.set(key, arco.peso !== undefined ? arco.peso : 1);
        }
      });

      subnet.transicoes.forEach((t) => {
        if (t.isInterface) {
          // Usar pesos originais dos arcos quando disponíveis
          if (t.originTransitionId) {
            if (t.interfaceType === "bidirecional") {
              // Verificar se a chave existe antes de usar o operador ||
              const inKey = `in_${t.originTransitionId}`;
              const outKey = `out_${t.originTransitionId}`;

              t.peso_in = arcWeights.has(inKey)
                ? arcWeights.get(inKey)
                : t.peso_in !== undefined
                  ? t.peso_in
                  : 0;

              t.peso_out = arcWeights.has(outKey)
                ? arcWeights.get(outKey)
                : t.peso_out !== undefined
                  ? t.peso_out
                  : 0;
            } else if (t.interfaceType === "entrada") {
              const inKey = `in_${t.originTransitionId}`;
              t.peso_in = arcWeights.has(inKey)
                ? arcWeights.get(inKey)
                : t.peso_in !== undefined
                  ? t.peso_in
                  : 0;
              t.peso_out = 0;
            } else if (t.interfaceType === "saida") {
              t.peso_in = 0;
              const outKey = `out_${t.originTransitionId}`;
              t.peso_out = arcWeights.has(outKey)
                ? arcWeights.get(outKey)
                : t.peso_out !== undefined
                  ? t.peso_out
                  : 0;
            }

            // Atualizar os valores restantes
            t.peso_in_restante =
              t.peso_in_restante !== undefined ? t.peso_in_restante : t.peso_in;
            t.peso_out_restante =
              t.peso_out_restante !== undefined
                ? t.peso_out_restante
                : t.peso_out;
          }
          console.log(
            `Interface ${t.id}: peso_in=${t.peso_in}, peso_out=${t.peso_out}`
          );
        }
      });
    }

    if (!subnet.lugares || subnet.lugares.length === 0) {
      // Inicializar uma nova sub-rede
      subnet = {
        nome: `Sub-rede de ${targetPlace.nome || placeElement.id}`,
        lugares: [],
        transicoes: [],
        arcos: [],
        entradas: [],
        saidas: [],
        agentes: [],
      };

      // Identificar transições de entrada e saída no contexto correto
      subnet.entradas = containingNet.arcos
        .filter((a) => a.destino === placeElement.id)
        .map((a) => a.origem);

      subnet.saidas = containingNet.arcos
        .filter((a) => a.origem === placeElement.id)
        .map((a) => a.destino);

      console.log(
        "Transições identificadas:",
        "entradas:",
        subnet.entradas,
        "saídas:",
        subnet.saidas
      );
      subnet = createInterfaceTransitions(subnet, petriNet, placeElement.id);
    }

    // Criar uma cópia profunda do estado atual
    const updatedNet = JSON.parse(JSON.stringify(petriNet));

    // NOVA ABORDAGEM: Primeiro, capture todos os elementos atuais no canvas
    const canvasElements = graphRef.current.getElements();
    const canvasLinks = graphRef.current.getLinks();

    // Mapear elementos atuais no canvas
    const canvasPlaces = new Map();
    const canvasTransitions = new Map();
    const canvasArcs = new Set();

    // Coletar lugares e transições do canvas
    canvasElements.forEach((element) => {
      const pos = element.position();
      if (element.attributes.type === "basic.Circle") {
        canvasPlaces.set(element.id, {
          id: element.id,
          nome: element.attr(".label/text") || "",
          tokens:
            parseInt(element.attr(".tokens/text")?.replace(/●/g, "")?.trim()) ||
            0,
          coordenadas: { x: pos.x, y: pos.y },
          delay: 0,
        });
      } else if (element.attributes.type === "basic.Rect") {
        canvasTransitions.set(element.id, {
          id: element.id,
          nome: element.attr(".label/text") || "",
          orientacao: element.get("size").width === 3 ? "vert" : "hor",
          coordenadas: { x: pos.x, y: pos.y },
          prioridade: 1,
          probabilidade: 0,
          tempo: 0,
        });
      }
    });

    // Coletar arcos do canvas
    canvasLinks.forEach((link) => {
      if (link.attributes.source.id && link.attributes.target.id) {
        canvasArcs.add(
          `${link.attributes.source.id}-${link.attributes.target.id}`
        );
      }
    });

    // Função para atualizar o modelo de dados com os elementos do canvas
    const syncModelWithCanvas = (netToUpdate, currentNetId) => {
      // Função para atualizar elementos em um determinado nível
      const updateLevel = (net) => {
        if (!net) return;

        // Sincronizar lugares
        if (net.lugares && Array.isArray(net.lugares)) {
          // Atualizar lugares existentes
          net.lugares = net.lugares.map((l) => {
            const canvasPlace = canvasPlaces.get(l.id);
            if (canvasPlace) {
              // Preservar tokens originais se os tokens do canvas forem zero ou indefinidos
              const tokensToUse =
                canvasPlace.tokens > 0 ? canvasPlace.tokens : l.tokens;

              return {
                ...l,
                coordenadas: canvasPlace.coordenadas,
                nome: canvasPlace.nome,
                tokens: tokensToUse, // Usar tokens do canvas apenas se forem positivos
              };
            }
            return l;
          });
          // Adicionar novos lugares que estão no canvas mas não no modelo
          canvasPlaces.forEach((place) => {
            if (!net.lugares.some((l) => l.id === place.id)) {
              net.lugares.push(place);
            }
          });
        }

        // Sincronizar transições
        if (net.transicoes && Array.isArray(net.transicoes)) {
          // Atualizar transições existentes
          net.transicoes = net.transicoes.map((t) => {
            const canvasTrans = canvasTransitions.get(t.id);
            if (canvasTrans) {
              return {
                ...t,
                coordenadas: canvasTrans.coordenadas,
                nome: canvasTrans.nome,
                orientacao: canvasTrans.orientacao,
              };
            }
            return t;
          });

          // Adicionar novas transições que estão no canvas mas não no modelo
          canvasTransitions.forEach((trans) => {
            if (!net.transicoes.some((t) => t.id === trans.id)) {
              net.transicoes.push(trans);
            }
          });
        }

        // Sincronizar arcos
        if (net.arcos && Array.isArray(net.arcos)) {
          // Adicionar novos arcos que estão no canvas mas não no modelo
          canvasLinks.forEach((link) => {
            const sourceId = link.attributes.source.id;
            const targetId = link.attributes.target.id;

            if (
              !net.arcos.some(
                (a) => a.origem === sourceId && a.destino === targetId
              )
            ) {
              net.arcos.push({
                origem: sourceId,
                destino: targetId,
                peso: 1, // valor padrão
              });
            }
          });
        }
      };

      if (currentNetId === null) {
        // Estamos na rede principal
        updateLevel(netToUpdate);
      } else {
        // Estamos em uma subnet
        const findAndUpdateSubnet = (net, targetId) => {
          // Procurar o lugar diretamente neste nível
          const place =
            net.lugares && net.lugares.find((l) => l.id === targetId);
          if (place && place.subnet) {
            updateLevel(place.subnet);
            return true;
          }

          // Se não encontramos neste nível, procurar recursivamente nas sub-redes
          if (net.lugares) {
            for (const lugar of net.lugares) {
              if (lugar.subnet) {
                const found = findAndUpdateSubnet(lugar.subnet, targetId);
                if (found) return true;
              }
            }
          }

          return false;
        };

        findAndUpdateSubnet(netToUpdate, currentNetId);
      }
    };

    // Sincronizar o modelo com os elementos atuais do canvas
    syncModelWithCanvas(updatedNet, currentNetId);

    // Salvar o estado atual antes de navegar para a sub-rede
    // Salvar o estado atual antes de navegar para a sub-rede, incluindo explicitamente os tokens atuais do lugar
    const tokenValidation = () => {
      try {
        return Math.max(
          0,
          Number(visualTokens) || Number(targetPlace.tokens) || 0
        );
      } catch (e) {
        console.error("Erro na validação de tokens:", e);
        return 0;
      }
    };

    setNetStack([
      ...netStack,
      {
        net: updatedNet,
        id: currentNetId,
        placeId: placeElement.id,
        parentId: parentId,
        explodedPlace: {
          id: placeElement.id,
          tokens: tokenValidation(),
          delay: targetPlace.delay || 0,
        },
      },
    ]);

    // Atualizar a sub-rede no lugar correto
    const updateSubnetInPlace = (net, targetId, newSubnet) => {
      const placeIndex = net.lugares.findIndex((l) => l.id === targetId);
      if (placeIndex >= 0) {
        // Preservar os tokens atuais antes de atualizar a subnet
        const currentTokensValue = currentTokens; // Usar os tokens capturados anteriormente

        //net.lugares[placeIndex].subnet = newSubnet;
        net.lugares[placeIndex] = {
          ...net.lugares[placeIndex],
          subnet: {
            ...newSubnet,
            agentes: net.lugares[placeIndex].subnet?.agentes || []  // Preserva agentes na subnet
          },
          tokens: currentTokensValue
        };

        // Garantir que todas as propriedades das interfaces sejam preservadas
        /*
    if (newSubnet.transicoes) {
      newSubnet.transicoes.forEach(t => {
        if (t.isInterface) {
          // Garantir que todas as propriedades importantes tenham valores
          t.peso_in = t.peso_in !== undefined ? t.peso_in : 0;
          t.peso_out = t.peso_out !== undefined ? t.peso_out : 0;
          t.peso_in_restante = t.peso_in_restante !== undefined ? t.peso_in_restante : t.peso_in || 0;
          t.peso_out_restante = t.peso_out_restante !== undefined ? t.peso_out_restante : t.peso_out || 0;
        }
      });
    }
      */

        // Garantir que os tokens não sejam perdidos na atualização
        net.lugares[placeIndex].tokens = currentTokensValue;

        return true;
      }
      // Garantir que todas as propriedades das interfaces sejam preservadas

      // O restante da função pode ficar como está
      for (let i = 0; i < net.lugares.length; i++) {
        if (net.lugares[i].subnet && net.lugares[i].subnet.lugares) {
          const updated = updateSubnetInPlace(
            net.lugares[i].subnet,
            targetId,
            newSubnet
          );
          if (updated) return true;
        }
      }

      return false;
    };

    updateSubnetInPlace(updatedNet, placeElement.id, subnet);

    // Atualizar o estado
    setPetriNet(updatedNet);

    // Navegar para a sub-rede
    setCurrentNetId(placeElement.id);

    // Limpar a área de desenho
    graphRef.current.clear();
    console.log(
      "Verificação de pesos das interfaces ANTES DE explodir:",
      subnet.transicoes
        .filter((t) => t.isInterface)
        .map((t) => ({
          id: t.id,
          type: t.interfaceType,
          peso_in: t.peso_in,
          peso_in_restante: t.peso_in_restante,
          peso_out: t.peso_out,
          peso_out_restante: t.peso_out_restante,
        }))
    );
    checkInterfaceWeightLimits(subnet);
    // Renderizar a sub-rede
    renderSubnet(subnet, placeElement.id);
    // Adicionar este log no final da função handleExplodePetriNet
    // Procure esta linha: renderSubnet(subnet, placeElement.id);
    // E adicione logo após:
    console.log(
      "Verificação de pesos das interfaces após explodir:",
      subnet.transicoes
        .filter((t) => t.isInterface)
        .map((t) => ({
          id: t.id,
          type: t.interfaceType,
          peso_in: t.peso_in,
          peso_in_restante: t.peso_in_restante,
          peso_out: t.peso_out,
          peso_out_restante: t.peso_out_restante,
        }))
    );
    console.log('===== APÓS EXPLOSÃO =====');
    console.log('Estado após explodir:', JSON.stringify(updatedNet, null, 2));
    console.log('Subnet criada para o lugar:', JSON.stringify(subnet, null, 2));
  };

  /**
   * Renderiza uma sub-rede no editor
   */
  const findTransitionById = (net, transitionId) => {
    // Procurar no nível atual
    const transition = net.transicoes.find((t) => t.id === transitionId);
    if (transition) return transition;

    // Procurar recursivamente nas sub-redes
    for (const lugar of net.lugares || []) {
      if (
        lugar.subnet &&
        lugar.subnet.transicoes &&
        lugar.subnet.transicoes.length > 0
      ) {
        const subTransition = findTransitionById(lugar.subnet, transitionId);
        if (subTransition) return subTransition;
      }
    }

    return null;
  };

  /**
   * Função auxiliar para encontrar um lugar pelo ID em qualquer nível da rede
   */
  const findPlaceById = (net, placeId) => {
    // Procurar no nível atual
    const place = net.lugares.find((l) => l.id === placeId);
    if (place) return place;

    // Procurar recursivamente nas sub-redes
    for (const lugar of net.lugares || []) {
      if (
        lugar.subnet &&
        lugar.subnet.lugares &&
        lugar.subnet.lugares.length > 0
      ) {
        const subPlace = findPlaceById(lugar.subnet, placeId);
        if (subPlace) return subPlace;
      }
    }

    return null;
  };

  // =========== PRINT FUNCTIONALITY ===========

  const handlePrintDiagram = () => {
    console.log("🖨️ Iniciando impressão do diagrama");
    
    try {
      // Obter título correto
      const title = getPrintTitle();
      console.log("📄 Título da impressão:", title);
      
      // Calcular dimensões do diagrama
      const bounds = calculateDiagramBounds();
      console.log("📐 Dimensões do diagrama:", bounds);
      
      // Criar versão para impressão
      createPrintVersion(title, bounds);
      
    } catch (error) {
      console.error("❌ Erro na impressão:", error);
      alert("Erro ao preparar impressão: " + error.message);
    }
  };

  const getPrintTitle = () => {
    if (currentNetId) {
      // Estamos em uma subnet - título é o nome do place
      const parentPlace = findPlaceById(petriNet, currentNetId);
      return parentPlace ? parentPlace.nome : currentNetId;
    } else {
      // Nível principal - título é o nome do projeto
      return petriNet.nome || "Rede de Petri";
    }
  };

  const calculateDiagramBounds = () => {
    const elements = graphRef.current.getElements();
    
    if (elements.length === 0) {
      return { minX: 0, minY: 0, maxX: 800, maxY: 600, width: 800, height: 600 };
    }
    
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    
    elements.forEach(element => {
      // Usar getBBox() que retorna coordenadas REAIS independente do zoom
      const bbox = element.getBBox();
      minX = Math.min(minX, bbox.x);
      minY = Math.min(minY, bbox.y);
      maxX = Math.max(maxX, bbox.x + bbox.width);
      maxY = Math.max(maxY, bbox.y + bbox.height);
    });
    
    // Adicionar margem proporcional
    const margin = 30;
    return {
      minX: minX - margin,
      minY: minY - margin,
      maxX: maxX + margin,
      maxY: maxY + margin,
      width: (maxX - minX) + (2 * margin),
      height: (maxY - minY) + (2 * margin)
    };
  };

  const createPrintVersion = (title, bounds) => {
    // Dimensões A4 em paisagem (CSS pixels)
    const A4_LANDSCAPE_WIDTH_MM = 297;
    const A4_LANDSCAPE_HEIGHT_MM = 210;
    const MARGIN_MM = 15; // Reduzir margem de 20mm para 15mm
    
    // Área útil após margens (em mm)
    const USABLE_WIDTH_MM = A4_LANDSCAPE_WIDTH_MM - (2 * MARGIN_MM);   // 267mm
    const USABLE_HEIGHT_MM = A4_LANDSCAPE_HEIGHT_MM - (2 * MARGIN_MM); // 180mm
    
    const TITLE_HEIGHT_MM = 12; // Reduzir altura do título
    const DIAGRAM_HEIGHT_MM = USABLE_HEIGHT_MM - TITLE_HEIGHT_MM - 3; // 165mm para diagrama
    
    // Converter para pixels (1mm ≈ 3.78 pixels)
    const MM_TO_PIXELS = 3.78;
    const USABLE_WIDTH_PX = USABLE_WIDTH_MM * MM_TO_PIXELS;   // ~1009px
    const DIAGRAM_HEIGHT_PX = DIAGRAM_HEIGHT_MM * MM_TO_PIXELS; // ~623px
    
    // Calcular escala para caber na área útil
    const scaleX = USABLE_WIDTH_PX / bounds.width;
    const scaleY = DIAGRAM_HEIGHT_PX / bounds.height;
    const scale = Math.min(scaleX, scaleY, 1); // nunca ampliar
    
    // Dimensões finais do diagrama escalado
    const finalWidth = bounds.width * scale;
    const finalHeight = bounds.height * scale;
    
    console.log(`📏 Área útil: ${USABLE_WIDTH_PX.toFixed(0)}x${DIAGRAM_HEIGHT_PX.toFixed(0)}px`);
    console.log(`📏 Diagrama original: ${bounds.width.toFixed(0)}x${bounds.height.toFixed(0)}px`);
    console.log(`📏 Escala: ${scale.toFixed(3)}`);
    console.log(`📏 Diagrama final: ${finalWidth.toFixed(0)}x${finalHeight.toFixed(0)}px`);
    
    // Criar janela de impressão
    const printWindow = window.open('', '_blank');
    
    const printHTML = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Impressão - ${title}</title>
        <style>
          @page {
            size: A4 landscape;
            margin: ${MARGIN_MM}mm;
          }
          
          * {
            box-sizing: border-box;
          }
          
          body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: white;
            width: ${USABLE_WIDTH_MM}mm;
            height: ${USABLE_HEIGHT_MM}mm;
            overflow: hidden;
          }
          
          .print-container {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
          }
          
          .title {
            font-size: 14px;
            font-weight: bold;
            color: #333;
            margin-bottom: 3mm;
            text-align: left;
            height: ${TITLE_HEIGHT_MM}mm;
            line-height: ${TITLE_HEIGHT_MM}mm;
            flex-shrink: 0;
          }
          
          .diagram-container {
            width: 100%;
            height: ${DIAGRAM_HEIGHT_MM}mm;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            border: 1px solid #eee; /* para debug - remover depois */
          }
          
          .diagram {
            transform: scale(${scale});
            transform-origin: center center;
            width: ${bounds.width}px;
            height: ${bounds.height}px;
          }
          
          @media print {
            body {
              -webkit-print-color-adjust: exact;
              print-color-adjust: exact;
            }
            .diagram-container {
              border: none !important;
            }
          }
        </style>
      </head>
      <body>
        <div class="print-container">
          <div class="title">${title}</div>
          <div class="diagram-container">
            <div class="diagram" id="diagram-content"></div>
          </div>
        </div>
      </body>
      </html>
    `;
    
    printWindow.document.write(printHTML);
    printWindow.document.close();
    
    // Aguardar carregamento e copiar SVG
    setTimeout(() => {
      const paperElement = paperRef.current.el;
      const svgElement = paperElement.querySelector('svg');
      
      if (svgElement) {
        // Clonar SVG
        const clonedSVG = svgElement.cloneNode(true);
        
        // RESETAR qualquer transformação do zoom da tela
        clonedSVG.style.transform = 'none';
        clonedSVG.style.transformOrigin = 'initial';
        
        // Ajustar viewBox para mostrar EXATAMENTE a área do diagrama
        clonedSVG.setAttribute('viewBox', `${bounds.minX} ${bounds.minY} ${bounds.width} ${bounds.height}`);
        
        // Definir dimensões ABSOLUTAS independente do zoom
        clonedSVG.setAttribute('width', bounds.width);
        clonedSVG.setAttribute('height', bounds.height);
        
        // Remover qualquer CSS que possa interferir
        clonedSVG.style.width = bounds.width + 'px';
        clonedSVG.style.height = bounds.height + 'px';
        clonedSVG.style.maxWidth = 'none';
        clonedSVG.style.maxHeight = 'none';
        
        console.log(`🖼️ SVG preparado: ${bounds.width}x${bounds.height}px`);
        console.log(`🖼️ ViewBox: ${bounds.minX} ${bounds.minY} ${bounds.width} ${bounds.height}`);
        
        // Inserir no documento de impressão
        const diagramContainer = printWindow.document.getElementById('diagram-content');
        diagramContainer.appendChild(clonedSVG);
        
        // Aguardar renderização e abrir diálogo de impressão
        setTimeout(() => {
          printWindow.print();
        }, 500);
        
      } else {
        console.error("❌ SVG não encontrado");
        printWindow.close();
      }
    }, 100);
  };

  const enhanceInterfaceArcs = () => {
    if (!currentNetId) return;

    const subnet = findNestedSubnet(petriNet, currentNetId);
    if (!subnet || !subnet.transicoes) return;

    // Interfaces na sub-rede atual
    const interfaces = subnet.transicoes.filter((t) => t.isInterface);

    // Processar todos os arcos
    subnet.arcos.forEach((arco) => {
      const { origem, destino } = arco;

      // Verificar se origem ou destino é uma interface
      const sourceInterface = interfaces.find((t) => t.id === origem);
      const targetInterface = interfaces.find((t) => t.id === destino);

      if (!sourceInterface && !targetInterface) return;

      // Encontrar o elemento visual do arco
      const link = graphRef.current
        .getLinks()
        .find(
          (l) =>
            l.attributes.source.id === origem &&
            l.attributes.target.id === destino
        );

      if (!link) return;

      // Definir estilo baseado no tipo de interface
      let strokeColor = "black";
      let strokeWidth = 2;
      let strokeDasharray = "";

      if (sourceInterface && targetInterface) {
        // Arco entre duas interfaces (caso raro)
        strokeColor = "#990000";
        strokeWidth = 3;
        strokeDasharray = "5,2";
      } else if (sourceInterface) {
        // Arco saindo de uma interface
        if (sourceInterface.interfaceType === "entrada") {
          // Não deveria acontecer devido à validação
          strokeColor = "red";
          strokeDasharray = "3,3";
        } else if (sourceInterface.interfaceType === "saida") {
          strokeColor = "#ff6600";
          strokeWidth = 3;
        } else if (sourceInterface.interfaceType === "bidirecional") {
          strokeColor = "#cc3300";
          strokeWidth = 3;
          strokeDasharray = "5,2";
        }
      } else if (targetInterface) {
        // Arco chegando em uma interface
        if (targetInterface.interfaceType === "saida") {
          // Não deveria acontecer devido à validação
          strokeColor = "red";
          strokeDasharray = "3,3";
        } else if (targetInterface.interfaceType === "entrada") {
          strokeColor = "#ff9966";
          strokeWidth = 3;
        } else if (targetInterface.interfaceType === "bidirecional") {
          strokeColor = "#cc3300";
          strokeWidth = 3;
          strokeDasharray = "5,2";
        }
      }

      // Aplicar estilo ao arco
      link.attr({
        line: {
          stroke: strokeColor,
          "stroke-width": strokeWidth,
          strokeDasharray: strokeDasharray,
        },
      });
    });
  };

  const renderSubnet = (subnet, placeId) => {
    // Se a sub-rede estiver vazia ou não tiver lugares definidos, criar estrutura inicial
    // Adicionar no início da função renderSubnet, após a verificação de subnet.lugares
    console.log("=== INÍCIO RENDERSUBNET ===");
    console.log("Transições de interface antes de processamento:");
    if (subnet.transicoes) {
      subnet.transicoes
        .filter((t) => t.isInterface)
        .forEach((t) => {
          console.log(
            `ID: ${t.id}, Tipo: ${t.interfaceType}, Nome: ${t.nome}, Origem: ${t.originTransitionId}`
          );
        });
    } else {
      console.log("Nenhuma transição encontrada");
    }
    if (subnet.lugares && subnet.lugares.length > 0) {
      // A sub-rede já existe, mas precisamos garantir que suas interfaces estejam atualizadas
      console.log("Sub-rede já existe, atualizando interfaces...");

      // Buscar o contexto correto que contém o lugar atual
      let parentState, containingNet;

      if (netStack.length > 0) {
        parentState = netStack[netStack.length - 1];

        // Encontrar a rede que contém o lugar atual
        const result = findContainingNet(parentState.net, placeId);
        containingNet = result.net;

        // Se não encontramos no estado do pai, buscar na rede atual
        if (!containingNet) {
          containingNet = findContainingNet(petriNet, placeId).net;
        }
      } else {
        containingNet = petriNet;
      }

      if (!containingNet) {
        console.error("Não foi possível encontrar o contexto para", placeId);
        containingNet = petriNet; // Fallback para a rede principal
      }

      // Verificar todas as conexões atuais para este lugar
      const currentPlaceId = placeId;

      // Atualizar entradas - transições que apontam para este lugar
      subnet.entradas = containingNet.arcos
        ? containingNet.arcos
          .filter((a) => a.destino === currentPlaceId)
          .map((a) => a.origem)
        : [];

      // Atualizar saídas - transições para as quais este lugar aponta
      subnet.saidas = containingNet.arcos
        ? containingNet.arcos
          .filter((a) => a.origem === currentPlaceId)
          .map((a) => a.destino)
        : [];
      // ADICIONAR AQUI: Criar interfaces com suporte a bidirecionais
      subnet = createInterfaceTransitions(subnet, petriNet, placeId);

      // Após a chamada a createInterfaceTransitions
      console.log("=== APÓS createInterfaceTransitions ===");
      console.log(`Entradas: ${subnet.entradas.join(", ")}`);
      console.log(`Saídas: ${subnet.saidas.join(", ")}`);
      console.log("Transições de interface criadas:");
      subnet.transicoes
        .filter((t) => t.isInterface)
        .forEach((t) => {
          console.log(
            `ID: ${t.id}, Tipo: ${t.interfaceType}, Nome: ${t.nome}, Origem: ${t.originTransitionId}`
          );
        });

      // Melhorar a busca de transições originais
      const findTransitionInContext = (transId) => {
        // Verificar primeiro no contexto atual
        const directTrans =
          containingNet.transicoes &&
          containingNet.transicoes.find((t) => t.id === transId);
        if (directTrans) return directTrans;

        // Se não encontrou, buscar em todo o modelo
        return findTransitionById(petriNet, transId);
      };
      const bidirectionalInterfaces = detectBidirectionalInterfaces(subnet);

      // Adicionar novas transições de interface para entradas recém-adicionadas
      subnet.entradas.forEach((transId) => {
        // Verificar se esta entrada já tem uma transição de interface
        if (bidirectionalInterfaces.includes(transId)) return;
        const hasInterface = subnet.transicoes.some(
          (t) =>
            t.isInterface &&
            t.interfaceType === "entrada" &&
            t.originTransitionId === transId
        );

        if (!hasInterface) {
          // Buscar a transição no contexto correto
          const transition = findTransitionInContext(transId);
          if (transition) {
            // Determinar o próximo índice para posicionamento
            const existingInputs = subnet.transicoes.filter(
              (t) => t.isInterface && t.interfaceType === "entrada"
            ).length;

            // Criar nova transição de interface
            const interfaceTransition = {
              id: `T_IF_IN_${existingInputs}_${transId}`, // ID mais específico
              nome: transition.nome || "",
              orientacao: transition.orientacao || "vert",
              coordenadas: { x: 200, y: 100 + existingInputs * 100 },
              prioridade: transition.prioridade || 1,
              probabilidade: transition.probabilidade || 0,
              tempo: transition.tempo || 0,
              isInterface: true,
              originTransitionId: transId,
              interfaceType: "entrada",
            };

            subnet.transicoes.push(interfaceTransition);
          }
        }
      });

      // Adicionar novas transições de interface para saídas recém-adicionadas
      subnet.saidas.forEach((transId) => {
        if (bidirectionalInterfaces.includes(transId)) return; // Pule se for bidirecional

        // Verificar se esta saída já tem uma transição de interface
        const hasInterface = subnet.transicoes.some(
          (t) =>
            t.isInterface &&
            t.interfaceType === "saida" &&
            t.originTransitionId === transId
        );

        if (!hasInterface) {
          // Buscar a transição no contexto correto
          const transition = findTransitionInContext(transId);
          if (transition) {
            // Determinar o próximo índice para posicionamento
            const existingOutputs = subnet.transicoes.filter(
              (t) => t.isInterface && t.interfaceType === "saida"
            ).length;

            // Criar nova transição de interface
            const interfaceTransition = {
              id: `T_IF_OUT_${existingOutputs}_${transId}`, // ID mais específico
              nome: transition.nome || "",
              orientacao: transition.orientacao || "vert",
              coordenadas: { x: 300, y: 100 + existingOutputs * 100 },
              prioridade: transition.prioridade || 1,
              probabilidade: transition.probabilidade || 0,
              tempo: transition.tempo || 0,
              isInterface: true,
              originTransitionId: transId,
              interfaceType: "saida",
            };

            subnet.transicoes.push(interfaceTransition);
          }
        }
      });

      // Remover interfaces obsoletas (para transições que foram desconectadas)
      subnet.transicoes = subnet.transicoes.filter((t) => {
        if (!t.isInterface) return true; // Manter transições normais

        if (t.interfaceType === "entrada") {
          return subnet.entradas.includes(t.originTransitionId);
        } else if (t.interfaceType === "saida") {
          return subnet.saidas.includes(t.originTransitionId);
        }

        return true; // Caso padrão
      });

      console.log(
        "Transições de interface criadas:",
        subnet.transicoes.filter((t) => t.isInterface).length,
        "- Entrada:",
        subnet.transicoes.filter(
          (t) => t.isInterface && t.interfaceType === "entrada"
        ).length,
        "- Saída:",
        subnet.transicoes.filter(
          (t) => t.isInterface && t.interfaceType === "saida"
        ).length
      );
    }

    if (!subnet.lugares || subnet.lugares.length === 0) {
      console.log("Sub-rede vazia, criando estrutura inicial...");
      // Inicializar estruturas básicas
      subnet.lugares = [];
      //subnet.transicoes = [];
      subnet.arcos = [];

      // Identificar de qual modelo obter as transições de entrada/saída
      // Depende de onde estamos na hierarquia
      let sourceNet;

      if (netStack.length > 0) {
        // Estamos em um nível aninhado, precisamos obter do nível imediatamente superior
        const parentState = netStack[netStack.length - 1];

        if (parentState.id) {
          // O nível superior é uma sub-rede
          const parentPlace = findPlaceById(parentState.net, parentState.id);
          if (parentPlace && parentPlace.subnet) {
            sourceNet = parentPlace.subnet;
          }
        } else {
          // O nível superior é a rede principal
          sourceNet = parentState.net;
        }
      } else {
        // Estamos no primeiro nível, usar a rede principal
        sourceNet = petriNet;
      }

      if (!sourceNet) {
        console.error(
          "Não foi possível encontrar a rede de origem para as transições de interface"
        );
        return;
      }

      // Após a chamada a createInterfaceTransitions
      console.log("=== APÓS createInterfaceTransitions 2 ===");
      console.log(`Entradas: ${subnet.entradas.join(", ")}`);
      console.log(`Saídas: ${subnet.saidas.join(", ")}`);
      console.log("Transições de interface criadas:");
      subnet.transicoes
        .filter((t) => t.isInterface)
        .forEach((t) => {
          console.log(
            `ID: ${t.id}, Tipo: ${t.interfaceType}, Nome: ${t.nome}, Origem: ${t.originTransitionId}`
          );
        });
    }

    // Desenhar a sub-rede no editor

    // Renderizar lugares
    subnet.lugares.forEach((lugar) => {
      createPlaceElement(lugar.id, lugar.nome, lugar.tokens, lugar.coordenadas);

      // Marcar lugares que têm sub-redes com um indicador visual
      if (
        lugar.subnet &&
        lugar.subnet.lugares &&
        lugar.subnet.lugares.length > 0
      ) {
        const placeElement = graphRef.current.getCell(lugar.id);
        if (placeElement) {
          placeElement.attr({
            ".body": {
              fill: "lightgreen",
              stroke: "green",
              "stroke-width": 2,
            },
          });
        }
      }
    });
    // Justo antes do bloco "Renderizar transições"
    console.log("=== ANTES DE RENDERIZAR TRANSIÇÕES ===");
    console.log("Transições a serem renderizadas:");
    subnet.transicoes
      .filter((t) => t.isInterface)
      .forEach((t) => {
        console.log(
          `ID: ${t.id}, Tipo: ${t.interfaceType}, Nome: ${t.nome}, Coordenadas: (${t.coordenadas.x}, ${t.coordenadas.y})`
        );
      });
    if (currentNetId) {
      checkInterfaceWeightLimits(subnet);
    }
    // Renderizar transições
    subnet.transicoes.forEach((transicao) => {
      // Modificar a função para marcar visualmente as transições de interface
      let interfaceType = null;
      if (transicao.isInterface) {
        interfaceType = transicao.interfaceType; // 'entrada', 'saida' ou 'bidirecional'
      }
      createTransitionElement(
        transicao.id,
        transicao.nome,
        transicao.orientacao || "vert",
        transicao.coordenadas,
        transicao.isInterface,
        interfaceType
      );
    });

    // Renderizar arcos
    subnet.arcos.forEach((arco) => {
      console.log(
        `RENDERIZANDO ARCO EM  RENDERSUBNET: ${arco.origem} -> ${arco.destino}, peso: ${arco.peso}`
      );

      createArcElement(arco);
    });

    setTimeout(() => {
      enhanceInterfaceArcs();
    }, 100);
    // Ao invés de chamar renderAgents(), vamos renderizar os agentes diretamente aqui
    console.log("Renderizando agentes diretamente na subnet");

    // Limpar agentes existentes no gráfico
    const existingAgents = graphRef.current
      .getElements()
      .filter(el => el.get("type") === "agent");
    existingAgents.forEach(agent => agent.remove());

    // Renderizar APENAS os agentes desta subnet específica
    if (subnet.agentes && Array.isArray(subnet.agentes)) {
      console.log(`Renderizando ${subnet.agentes.length} agentes desta subnet específica`);
      subnet.agentes.forEach(agente => {
        console.log(`Renderizando agente: ${agente.id}`);
        createAgentElement(agente);
      });
    } else {
      console.log("Esta subnet não tem agentes ou a propriedade agentes não é um array");
    }
    //renderAgents();
  };

  const renderFullNetwork = (net) => {
    // Renderizar lugares
    net.lugares.forEach((lugar) => {
      createPlaceElement(lugar.id, lugar.nome, lugar.tokens, lugar.coordenadas);

      // Marcar lugares que têm sub-redes com um indicador visual
      if (
        lugar.subnet &&
        lugar.subnet.lugares &&
        lugar.subnet.lugares.length > 0
      ) {
        const placeElement = graphRef.current.getCell(lugar.id);
        if (placeElement) {
          placeElement.attr({
            ".body": {
              fill: "lightgreen", // Cor especial para lugares com sub-rede
              stroke: "green",
              "stroke-width": 2,
            },
          });
        }
      }
    });

    // Renderizar transições
    net.transicoes.forEach((transicao) => {
      createTransitionElement(
        transicao.id,
        transicao.nome,
        transicao.orientacao || "vert",
        transicao.coordenadas
      );
    });

    // Renderizar arcos
    net.arcos.forEach((arco) => {
      createArcElement(arco);
    });
    console.log("Renderizando agentes diretamente na rede principal");

    // Limpar agentes existentes no gráfico
    const existingAgents = graphRef.current
      .getElements()
      .filter(el => el.get("type") === "agent");
    existingAgents.forEach(agent => agent.remove());

    // Renderizar APENAS os agentes da rede principal
    if (net.agentes && Array.isArray(net.agentes)) {
      console.log(`Renderizando ${net.agentes.length} agentes da rede principal`);
      net.agentes.forEach(agente => {
        console.log(`Renderizando agente: ${agente.id}`);
        createAgentElement(agente);
      });
    } else {
      console.log("A rede principal não tem agentes ou a propriedade agentes não é um array");
    }
    //renderAgents();
  };

  /**
   * Função para voltar ao nível hierárquico superior
   */
  const navigateToParent = () => {
    if (netStack.length === 0) return;

    // Primeiro, atualize as posições de todos os elementos no modelo atual
    // antes de extrair a sub-rede
    const elements = graphRef.current.getElements();
    const currentElements = new Map();

    // Coletar as posições atuais de todos os elementos no canvas
    elements.forEach((element) => {
      const pos = element.position();
      currentElements.set(element.id, {
        x: pos.x,
        y: pos.y,
      });
    });

    // Obter o último estado da pilha
    const parentState = netStack[netStack.length - 1];
    const currentNet = JSON.parse(JSON.stringify(parentState.net)); // Clone profundo
    const parentNetId = parentState.id;
    const placeId = parentState.placeId; // ID do lugar que foi explodido
    const parentPlaceId = parentState.parentId; // ID do lugar pai (adicionado na correção 3)

    // Extrair a sub-rede atual com todas as modificações
    // Extrair a sub-rede atual com todas as modificações,
    // agora COM as coordenadas atualizadas
    const currentSubnet = extractCurrentSubnet(currentElements);

    console.log("Navegando para cima com subnet:", currentSubnet);
    console.log("Agentes na subnet:", currentSubnet.agentes?.length || 0);

    console.log("Transições na subnet:", currentSubnet.transicoes.length);
    console.log(
      "Interfaces preservadas:",
      "entradas:",
      currentSubnet.entradas,
      "saídas:",
      currentSubnet.saidas
    );

    // Função recursiva para atualizar a sub-rede no lugar correto na hierarquia
    const updateNestedSubnet = (net, targetPlaceId, subnet) => {
      // Procurar o lugar diretamente neste nível
      const placeIndex = net.lugares.findIndex((l) => l.id === targetPlaceId);

      // Modificação mais precisa para navigateToParent
      // Apenas as linhas alteradas ou adicionadas para corrigir a preservação de tokens

      // Encontre esta linha na função updateNestedSubnet, dentro de navigateToParent
      if (placeIndex >= 0) {
        const tokenSource =
          parentState.explodedPlace?.id === targetPlaceId
            ? parentState.explodedPlace.tokens
            : net.lugares[placeIndex].tokens;

        const validatedTokens = Math.max(0, Number(tokenSource) || 0);

        net.lugares[placeIndex] = {
          ...net.lugares[placeIndex],
          tokens: validatedTokens,
          subnet: {
            ...(net.lugares[placeIndex].subnet || {}),
            ...subnet,
            entradas: subnet.entradas || [],
            saidas: subnet.saidas || [],
            agentes: subnet.agentes || []
          },
        };

        console.log(
          `Tokens restaurados para ${targetPlaceId}:`,
          validatedTokens
        );

        return true;
      }

      // Se não encontramos neste nível, procurar recursivamente nas sub-redes
      for (let i = 0; i < net.lugares.length; i++) {
        if (net.lugares[i].subnet && net.lugares[i].subnet.lugares) {
          // Tentar atualizar nesta sub-rede
          const updated = updateNestedSubnet(
            net.lugares[i].subnet,
            targetPlaceId,
            subnet
          );
          if (updated) return true;
        }
      }

      return false;
    };

    // Atualizar a sub-rede no lugar correto
    const updated = updateNestedSubnet(currentNet, placeId, currentSubnet);

    if (!updated) {
      console.error("Falha ao atualizar a sub-rede aninhada:", placeId);
    }

    // Atualizar o estado
    setPetriNet(currentNet);
    setCurrentNetId(parentNetId);

    // Remover o último estado da pilha
    const newStack = [...netStack];
    newStack.pop();
    setNetStack(newStack);

    // Limpar a área de desenho
    graphRef.current.clear();

    // Renderizar a rede pai
    if (parentNetId) {
      // Estamos voltando para uma sub-rede intermediária
      const parentSubnet = findNestedSubnet(currentNet, parentNetId);
      if (parentSubnet) {
        console.log("Renderizando sub-rede pai:", parentNetId);
        renderSubnet(parentSubnet, parentNetId);
      } else {
        console.error("Sub-rede pai não encontrada:", parentNetId);
      }
    } else {
      // Estamos voltando para a rede principal
      console.log("Renderizando rede principal");
      renderFullNetwork(currentNet);
    }
  };
  /**
   * Extrai a sub-rede atual do gráfico
   */
  const extractCurrentSubnet = (updatedPositions = null) => {
    // <-- NOVO PARÂMETRO ADICIONADO
    if (!currentNetId) return {};

    // Encontrar a subnet atual diretamente usando a função melhorada
    const { net: containingNet } = findContainingNet(petriNet, currentNetId);
    if (!containingNet) {
      console.error(
        "Não foi possível encontrar o contexto para a subnet atual"
      );
      return {
        nome: "",
        lugares: [],
        transicoes: [],
        arcos: [],
        entradas: [],
        saidas: [],
      };
    }

    // Encontrar o lugar atual no contexto
    const currentPlace = containingNet.lugares.find(
      (l) => l.id === currentNetId
    );
    if (!currentPlace) {
      console.error("Lugar atual não encontrado no contexto");
      return {
        nome: "",
        lugares: [],
        transicoes: [],
        arcos: [],
        entradas: [],
        saidas: [],
      };
    }

    // Obter a subnet existente ou criar uma nova
    let existingSubnet = currentPlace.subnet || {
      nome: `Sub-rede de ${currentPlace.nome || currentNetId}`,
      lugares: [],
      transicoes: [],
      arcos: [],
      entradas: [],
      saidas: [],
    };

    // Combinar as informações existentes com os elementos visuais atuais
    const subnet = { ...existingSubnet };

    // Extrair elementos do gráfico atual
    const elements = graphRef.current.getElements();
    const links = graphRef.current.getLinks();

    // Manter um mapa de IDs para preservar propriedades especiais
    const idMap = new Map();

    // Mapear todos os elementos existentes por ID para referência rápida
    existingSubnet.lugares.forEach((lugar) => idMap.set(lugar.id, lugar));
    existingSubnet.transicoes.forEach((trans) => idMap.set(trans.id, trans));

    // Nova lista de lugares baseada nos elementos visuais atuais
    subnet.lugares = [];
    elements.forEach((element) => {
      if (element.attributes.type === "basic.Circle") {
        // INÍCIO DA ALTERAÇÃO
        let position;

        // Usar posição atualizada se fornecida, caso contrário usar a posição no canvas
        if (updatedPositions && updatedPositions.has(element.id)) {
          position = updatedPositions.get(element.id);
        } else {
          position = element.position();
        }
        // FIM DA ALTERAÇÃO

        const id = element.id;

        // Preservar propriedades do lugar original se existir
        const originalPlace = idMap.get(id);
        const safeTokens = () => {
          try {
            return originalPlace?.tokens !== undefined
              ? Number(originalPlace.tokens)
              : Number(
                element.attr(".tokens/text")?.replace(/[^0-9]/g, "") || 0
              );
          } catch (e) {
            console.error("Erro ao capturar tokens:", e);
            return 0;
          }
        };

        subnet.lugares.push({
          id,
          nome: element.attr(".label/text") || "",
          tokens: safeTokens(),
          coordenadas: { x: position.x, y: position.y },
          delay: originalPlace?.delay || 0,
          subnet: originalPlace?.subnet || {},
        });
      }
    });

    // Nova lista de transições baseada nos elementos visuais atuais
    subnet.transicoes = [];
    elements.forEach((element) => {
      if (element.attributes.type === "basic.Rect") {
        // INÍCIO DA ALTERAÇÃO
        let position;

        // Usar posição atualizada se fornecida, caso contrário usar a posição no canvas
        if (updatedPositions && updatedPositions.has(element.id)) {
          position = updatedPositions.get(element.id);
        } else {
          position = element.position();
        }
        // FIM DA ALTERAÇÃO

        const id = element.id;

        // Preservar propriedades especiais da transição original
        const originalTrans = idMap.get(id);

        subnet.transicoes.push({
          id,
          nome: element.attr(".label/text") || "",
          orientacao: element.get("size").width === 3 ? "vert" : "hor",
          coordenadas: { x: position.x, y: position.y }, // <-- USANDO POSITION MODIFICADA
          prioridade: originalTrans?.prioridade || 1,
          probabilidade: originalTrans?.probabilidade || 0,
          tempo: originalTrans?.tempo || 0,
          isInterface: originalTrans?.isInterface || false,
          originTransitionId: originalTrans?.originTransitionId || null,
          interfaceType: originalTrans?.interfaceType || null,
        });
      }
    });

    // Nova lista de arcos baseada nas conexões visuais atuais
    subnet.arcos = [];
    links.forEach((link) => {
      if (link.attributes.source.id && link.attributes.target.id) {
        // Preservar propriedades do arco original se existir
        const originalArc = existingSubnet.arcos.find(
          (a) =>
            a.origem === link.attributes.source.id &&
            a.destino === link.attributes.target.id
        );

        subnet.arcos.push({
          origem: link.attributes.source.id,
          destino: link.attributes.target.id,
          peso: originalArc?.peso !== undefined ? originalArc.peso : 1,
        });
      }
    });

    // Adicionar este trecho na função extractCurrentSubnet
    // Após extrair lugares, transições e arcos

    if (existingSubnet.agentes) {

      // Usar os agentes que já existem na subnet
      subnet.agentes = [...existingSubnet.agentes];

      // Atualizar apenas as posições dos agentes que estão no canvas
      const agentElements = graphRef.current.getElements()
        .filter(el => el.get('type') === 'agent');

      // Criar um mapa de agentes da subnet por ID para acesso rápido
      const subnetAgentMap = new Map();
      subnet.agentes.forEach(agent => subnetAgentMap.set(agent.id, agent));

      // Atualizar apenas as posições dos agentes que pertencem à subnet
      agentElements.forEach(element => {
        const agentId = element.get('agentId');
        if (subnetAgentMap.has(agentId)) {
          const agent = subnetAgentMap.get(agentId);
          const pos = element.position();
          const size = element.size();

          // Atualizar apenas as propriedades visuais
          agent.coordenadas = { x: pos.x, y: pos.y };
          agent.width = size.width;
          agent.height = size.height;
        }
      });
    } else {
      subnet.agentes = [];
    }

    console.log(`Extraídos ${subnet.agentes.length} agentes da subnet ${currentNetId}`);

    // Importante: preservar listas entradas/saídas
    if (existingSubnet.entradas) subnet.entradas = [...existingSubnet.entradas];
    if (existingSubnet.saidas) subnet.saidas = [...existingSubnet.saidas];

    return subnet;
  };

  /**
   * Handles the undo operation
   */
  const handleUndo = () => {
    if (undoStack.length === 0) return;

    const lastAction = undoStack[undoStack.length - 1];

    // Process different action types
    switch (lastAction.actionType) {
      case "delete":
        handleUndoDelete(lastAction);
        break;
      case "add_place":
        handleUndoAddPlace(lastAction);
        break;
      case "add_transition":
        handleUndoAddTransition(lastAction);
        break;
      case "add_arc":
        handleUndoAddArc(lastAction);
        break;
      case "move":
        handleUndoMove(lastAction);
        break;
      case "paste":
        handleUndoPaste(lastAction);
        break;
      case "add_agent":
        handleUndoAddAgent(lastAction);
        break;
      case "resize_agent":
        handleUndoResizeAgent(lastAction);
        break;
      default:
        console.warn("Unknown action type:", lastAction.actionType);
        break;
    }

    // Move action to redo stack
    setRedoStack((prev) => [...prev, lastAction]);
    setUndoStack((prev) => prev.slice(0, -1));
  };

  /**
   * Handles the redo operation
   */
  const handleRedo = () => {
    if (redoStack.length === 0) return;

    const lastAction = redoStack[redoStack.length - 1];

    // Process different action types
    switch (lastAction.actionType) {
      case "delete":
        handleRedoDelete(lastAction);
        break;
      case "add_place":
        handleRedoAddPlace(lastAction);
        break;
      case "add_transition":
        handleRedoAddTransition(lastAction);
        break;
      case "add_arc":
        handleRedoAddArc(lastAction);
        break;
      case "move":
        handleRedoMove(lastAction);
        break;
      case "paste":
        handleRedoPaste(lastAction);
        break;
      case "add_agent":
        handleRedoAddAgent(lastAction);
        break;
      case "resize_agent":
        handleRedoResizeAgent(lastAction);
        break;
      default:
        console.warn("Unknown action type:", lastAction.actionType);
        break;
    }

    // Move action back to undo stack
    setUndoStack((prev) => [...prev, lastAction]);
    setRedoStack((prev) => prev.slice(0, -1));
  };
  const handleAgentSelect = (agentElement) => {
    const agentId = agentElement.get('agentId');

    // Atualizar estado de seleção
    setSelectedAgente(agentId);

    // Destacar o agente selecionado
    const elements = graphRef.current.getElements();
    elements.forEach(el => {
      if (el.get('type') === 'agent') {
        if (el.get('agentId') === agentId) {
          el.attr('rect/stroke', '#2E74B5'); // Azul escuro para destacar
          el.attr('rect/stroke-width', 3);
        } else {
          el.attr('rect/stroke', '#A3C7E3'); // Voltar para a cor padrão
          el.attr('rect/stroke-width', 2);
        }
      }
    });
  };

  /**
   * Handling undo operations for each action type
   */
  const handleUndoDelete = (lastAction) => {
    // Lists to restore in correct order
    const restoredPlaces = [];
    const restoredTransitions = [];
    const restoredArcs = [];
    const restoredAgents = [];

    // 1. First, separate elements by type
    lastAction.data.forEach(({ id, type, data }) => {
      if (type === "place") {
        restoredPlaces.push({ id, data });
      } else if (type === "transition") {
        restoredTransitions.push({ id, data });
      } else if (type === "arc") {
        restoredArcs.push(data);
      } else if (type === "agent") {
        restoredAgents.push({ id, data });
      }
    });

    // 2. Update petriNet state based on current context
    setPetriNet((prev) => {
      // Make a deep copy to avoid mutation issues
      const updatedNet = JSON.parse(JSON.stringify(prev));

      if (currentNetId) {
        // We're in a subnet - need to find and update it
        const updateSubnetRecursively = (net, targetId, path = []) => {
          // Avoid infinite loops
          if (path.includes(targetId)) return net;

          // Check if we found the target subnet at this level
          const placeIndex = net.lugares.findIndex(l => l.id === targetId);
          if (placeIndex >= 0) {
            // Found our target subnet
            if (!net.lugares[placeIndex].subnet) {
              net.lugares[placeIndex].subnet = {
                lugares: [],
                transicoes: [],
                arcos: [],
                agentes: []
              };
            }

            // Add restored elements to this subnet
            const subnet = net.lugares[placeIndex].subnet;

            // Add places
            subnet.lugares = [
              ...subnet.lugares,
              ...restoredPlaces.map(p => p.data)
            ];

            // Add transitions
            subnet.transicoes = [
              ...subnet.transicoes,
              ...restoredTransitions.map(t => t.data)
            ];

            // Add arcs
            subnet.arcos = [
              ...subnet.arcos,
              ...restoredArcs
            ];

            // Add agents
            if (!subnet.agentes) subnet.agentes = [];
            subnet.agentes = [
              ...subnet.agentes,
              ...restoredAgents.map(a => a.data)
            ];

            return net;
          }

          // Search recursively in all subnets at this level
          if (net.lugares) {
            net.lugares = net.lugares.map(lugar => {
              if (lugar.subnet) {
                const newPath = [...path, lugar.id];
                const updatedSubnet = updateSubnetRecursively(
                  lugar.subnet,
                  targetId,
                  newPath
                );
                return { ...lugar, subnet: updatedSubnet };
              }
              return lugar;
            });
          }

          return net;
        };

        // Update the subnet recursively
        return updateSubnetRecursively(updatedNet, currentNetId);
      } else {
        // We're in the main network, original behavior is fine
        return {
          ...updatedNet,
          lugares: [...updatedNet.lugares, ...restoredPlaces.map(p => p.data)],
          transicoes: [...updatedNet.transicoes, ...restoredTransitions.map(t => t.data)],
          arcos: [...updatedNet.arcos, ...restoredArcs],
          agentes: [...(updatedNet.agentes || []), ...restoredAgents.map(a => a.data)]
        };
      }
    });

    // 3. Restore places in the graph (visual elements)
    restoredPlaces.forEach(({ id, data }) => {
      createPlaceElement(id, data.nome, data.tokens, data.coordenadas);
    });

    // 4. Restore transitions in the graph
    restoredTransitions.forEach(({ id, data }) => {
      createTransitionElement(id, data.nome, data.orientacao, data.coordenadas);
    });

    // 5. Restore agents in the graph
    restoredAgents.forEach(({ data }) => {
      createAgentElement(data);
    });

    // 6. Restore arcs in the next render cycle
    setTimeout(() => {
      restoredArcs.forEach(createArcElement);
    }, 0);
  };

  const handleUndoAddPlace = (lastAction) => {
    const placeId = lastAction.data.id;
    const place = graphRef.current.getCell(placeId);
    if (place) place.remove();

    setPetriNet((prev) => ({
      ...prev,
      lugares: prev.lugares.filter((l) => l.id !== placeId),
    }));
  };

  const handleUndoAddTransition = (lastAction) => {
    const transitionId = lastAction.data.id;
    const transition = graphRef.current.getCell(transitionId);
    if (transition) transition.remove();

    setPetriNet((prev) => ({
      ...prev,
      transicoes: prev.transicoes.filter((t) => t.id !== transitionId),
    }));
  };

  const handleUndoAddArc = (lastAction) => {
    const { origem, destino } = lastAction.data;

    // Remove from graph
    const link = graphRef.current
      .getLinks()
      .find(
        (l) =>
          l.attributes.source.id === origem &&
          l.attributes.target.id === destino
      );
    if (link) link.remove();

    // Remove from state
    setPetriNet((prev) => ({
      ...prev,
      arcos: prev.arcos.filter(
        (a) => a.origem !== origem || a.destino !== destino
      ),
    }));
  };

  const handleUndoMove = (lastAction) => {
    // Restaurar posições iniciais
    lastAction.data.initial.forEach((element) => {
      // Verificar se é um agente
      if (element.type === "agent") {
        // Buscar pelo elemento do agente
        const agentElement = graphRef.current.getElements().find(
          el => el.get('type') === 'agent' && el.get('agentId') === element.id
        );

        if (agentElement) {
          // Posicionar o agente na posição inicial
          agentElement.position(element.data.coordenadas.x, element.data.coordenadas.y);

          // Se o agente também foi redimensionado, restaurar tamanho
          if (element.data.width && element.data.height) {
            agentElement.resize(element.data.width, element.data.height);
          }
        }
      } else {
        // Elementos normais (lugares/transições)
        const cell = graphRef.current.getCell(element.id);
        if (cell) {
          cell.position(element.data.coordenadas.x, element.data.coordenadas.y);

          // Atualizar propriedades visuais
          if (element.type === "place") {
            updatePlaceVisuals(cell, element.data);
          } else if (element.type === "transition") {
            updateTransitionVisuals(
              cell,
              element.data,
              selectedElements.has(element.id)
            );
          }
        }
      }
    });

    // Atualizar estado do petriNet
    setPetriNet((prev) => {
      // Clonar para evitar mutação direta
      const updatedNet = JSON.parse(JSON.stringify(prev));

      // Verificar se estamos em uma subnet
      if (lastAction.data.inSubnet) {
        // Função para atualizar a subnet recursivamente
        const updateSubnetRecursively = (net, targetId, path = []) => {
          // Evitar loops infinitos
          if (path.includes(targetId)) return net;

          // Verificar se encontramos a subnet alvo neste nível
          const placeIndex = net.lugares.findIndex(l => l.id === targetId);
          if (placeIndex >= 0) {
            // Encontramos a subnet alvo
            if (!net.lugares[placeIndex].subnet) return net;

            const subnet = net.lugares[placeIndex].subnet;

            // Atualizar lugares
            if (subnet.lugares) {
              subnet.lugares = subnet.lugares.map((l) => {
                const initialElement = lastAction.data.initial.find(
                  (e) => e.type === "place" && e.id === l.id
                );
                return initialElement
                  ? { ...l, coordenadas: initialElement.data.coordenadas }
                  : l;
              });
            }

            // Atualizar transições
            if (subnet.transicoes) {
              subnet.transicoes = subnet.transicoes.map((t) => {
                const initialElement = lastAction.data.initial.find(
                  (e) => e.type === "transition" && e.id === t.id
                );
                return initialElement
                  ? { ...t, coordenadas: initialElement.data.coordenadas }
                  : t;
              });
            }

            // Atualizar agentes
            if (subnet.agentes) {
              subnet.agentes = subnet.agentes.map((a) => {
                const initialElement = lastAction.data.initial.find(
                  (e) => e.type === "agent" && e.id === a.id
                );
                if (initialElement) {
                  return {
                    ...a,
                    coordenadas: initialElement.data.coordenadas,
                    // Se tiver informações de tamanho, restaurá-las também
                    ...(initialElement.data.width ? { width: initialElement.data.width } : {}),
                    ...(initialElement.data.height ? { height: initialElement.data.height } : {})
                  };
                }
                return a;
              });
            }

            return net;
          }

          // Buscar recursivamente
          if (net.lugares) {
            net.lugares = net.lugares.map(lugar => {
              if (lugar.subnet) {
                const newPath = [...path, lugar.id];
                return {
                  ...lugar,
                  subnet: updateSubnetRecursively(lugar.subnet, targetId, newPath)
                };
              }
              return lugar;
            });
          }

          return net;
        };

        // Atualizar a subnet usando o subnetId armazenado na ação
        return updateSubnetRecursively(updatedNet, lastAction.data.subnetId || lastAction.data.inSubnet);
      } else {
        // Estamos na rede principal

        // Atualizar lugares
        updatedNet.lugares = updatedNet.lugares.map((l) => {
          const initialElement = lastAction.data.initial.find(
            (e) => e.type === "place" && e.id === l.id
          );
          return initialElement
            ? { ...l, coordenadas: initialElement.data.coordenadas }
            : l;
        });

        // Atualizar transições
        updatedNet.transicoes = updatedNet.transicoes.map((t) => {
          const initialElement = lastAction.data.initial.find(
            (e) => e.type === "transition" && e.id === t.id
          );
          return initialElement
            ? { ...t, coordenadas: initialElement.data.coordenadas }
            : t;
        });

        // Atualizar agentes
        if (updatedNet.agentes) {
          updatedNet.agentes = updatedNet.agentes.map((a) => {
            const initialElement = lastAction.data.initial.find(
              (e) => e.type === "agent" && e.id === a.id
            );
            if (initialElement) {
              return {
                ...a,
                coordenadas: initialElement.data.coordenadas,
                // Se tiver informações de tamanho, restaurá-las também
                ...(initialElement.data.width ? { width: initialElement.data.width } : {}),
                ...(initialElement.data.height ? { height: initialElement.data.height } : {})
              };
            }
            return a;
          });
        }

        return updatedNet;
      }
    });
  };

  const handleUndoPaste = (lastAction) => {
    // First remove arcs to avoid broken references
    lastAction.data.elements
      .filter((element) => element.type === "arc")
      .forEach((element) => {
        // Remove arcs from graph
        const link = graphRef.current
          .getLinks()
          .find(
            (l) =>
              l.attributes.source.id === element.data.origem &&
              l.attributes.target.id === element.data.destino
          );
        if (link) link.remove();
      });

    // Then remove places and transitions
    lastAction.data.elements
      .filter((element) => element.type !== "arc")
      .forEach((element) => {
        const cell = graphRef.current.getCell(element.id);
        if (cell) cell.remove();
      });

    // Update petriNet state
    setPetriNet((prev) => ({
      ...prev,
      lugares: prev.lugares.filter(
        (l) =>
          !lastAction.data.elements.some(
            (e) => e.type === "place" && e.id === l.id
          )
      ),
      transicoes: prev.transicoes.filter(
        (t) =>
          !lastAction.data.elements.some(
            (e) => e.type === "transition" && e.id === t.id
          )
      ),
      arcos: prev.arcos.filter(
        (a) =>
          !lastAction.data.elements.some(
            (e) =>
              e.type === "arc" &&
              e.data.origem === a.origem &&
              e.data.destino === a.destino
          )
      ),
    }));
  };

  /**
   * Handling redo operations for each action type
   */
  const handleRedoDelete = (lastAction) => {
    // Filter valid items
    const itemsToDelete = lastAction.data.filter(
      (item) => item && item.type && item.id
    );

    // First remove arcs
    itemsToDelete.forEach((item) => {
      if (item.type === "arc" && item.data) {
        const link = graphRef.current
          .getLinks()
          .find(
            (l) =>
              l.attributes.source.id === item.data.origem &&
              l.attributes.target.id === item.data.destino
          );
        if (link) link.remove();
      }
    });

    // Then remove places and transitions


    itemsToDelete.forEach((item) => {
      if ((item.type === "place" || item.type === "transition") && item.id) {
        const cell = graphRef.current.getCell(item.id);
        if (cell) cell.remove();
      } else if (item.type === "agent" && item.id) {
        // Remover agente
        const agentElement = graphRef.current.getElements().find(
          el => el.get('type') === 'agent' && el.get('agentId') === item.id
        );
        if (agentElement) agentElement.remove();
      }
    });

    // Update petriNet state
    setPetriNet((prev) => {
      const newState = { ...prev };

      // Remove places and transitions
      newState.lugares = prev.lugares.filter(
        (l) =>
          !itemsToDelete.some(
            (item) => item.type === "place" && item.id === l.id
          )
      );

      newState.transicoes = prev.transicoes.filter(
        (t) =>
          !itemsToDelete.some(
            (item) => item.type === "transition" && item.id === t.id
          )
      );

      // Remove arcs
      newState.arcos = prev.arcos.filter(
        (a) =>
          !itemsToDelete.some(
            (item) =>
              item.type === "arc" &&
              item.data &&
              item.data.origem === a.origem &&
              item.data.destino === a.destino
          )
      );
      // Remove agents
      if (newState.agentes) {
        newState.agentes = prev.agentes.filter(
          (a) =>
            !itemsToDelete.some(
              (item) => item.type === "agent" && item.id === a.id
            )
        );
      } // Remove agents

      return newState;
    });
  };

  const handleRedoAddPlace = (lastAction) => {
    const { id, nome, tokens, coordenadas, delay } = lastAction.data;
    createPlaceElement(id, nome, tokens, coordenadas);

    setPetriNet((prev) => ({
      ...prev,
      lugares: [...prev.lugares, { id, nome, tokens, coordenadas, delay }],
    }));
  };

  const handleRedoAddTransition = (lastAction) => {
    const {
      id,
      nome,
      coordenadas,
      prioridade,
      probabilidade,
      orientacao = "vert",
    } = lastAction.data;
    createTransitionElement(id, nome, orientacao, coordenadas);

    setPetriNet((prev) => ({
      ...prev,
      transicoes: [
        ...prev.transicoes,
        {
          id,
          nome,
          coordenadas,
          prioridade,
          probabilidade,
          orientacao: orientacao || "vert",
          tempo: lastAction.data.tempo || 0,
        },
      ],
    }));
  };

  const handleRedoAddArc = (lastAction) => {
    const { origem, destino, peso } = lastAction.data;

    // Verify source and target elements exist
    const sourceElement = graphRef.current.getCell(origem);
    const targetElement = graphRef.current.getCell(destino);

    if (sourceElement && targetElement) {
      createArcElement({ origem, destino, peso });

      // Update petriNet state
      setPetriNet((prev) => ({
        ...prev,
        arcos: [...prev.arcos, { origem, destino, peso }],
      }));
    }
  };

  const handleRedoMove = (lastAction) => {
    // Restaurar posições finais
    lastAction.data.final.forEach((element) => {
      // Verificar se é um agente
      if (element.type === "agent") {
        // Buscar pelo elemento do agente
        const agentElement = graphRef.current.getElements().find(
          el => el.get('type') === 'agent' && el.get('agentId') === element.id
        );

        if (agentElement) {
          // Posicionar o agente na posição final
          agentElement.position(element.data.coordenadas.x, element.data.coordenadas.y);

          // Se o agente também foi redimensionado, restaurar tamanho
          if (element.data.width && element.data.height) {
            agentElement.resize(element.data.width, element.data.height);
          }
        }
      } else {
        // Elementos normais (lugares/transições)
        const cell = graphRef.current.getCell(element.id);
        if (cell) {
          cell.position(element.data.coordenadas.x, element.data.coordenadas.y);

          // Atualizar propriedades visuais
          if (element.type === "place") {
            updatePlaceVisuals(cell, element.data);
          } else if (element.type === "transition") {
            updateTransitionVisuals(
              cell,
              element.data,
              selectedElements.has(element.id)
            );
          }
        }
      }
    });

    // Atualizar estado do petriNet
    setPetriNet((prev) => {
      // Clonar para evitar mutação direta
      const updatedNet = JSON.parse(JSON.stringify(prev));

      // Verificar se estamos em uma subnet
      if (lastAction.data.inSubnet) {
        // Função para atualizar a subnet recursivamente
        const updateSubnetRecursively = (net, targetId, path = []) => {
          // Evitar loops infinitos
          if (path.includes(targetId)) return net;

          // Verificar se encontramos a subnet alvo neste nível
          const placeIndex = net.lugares.findIndex(l => l.id === targetId);
          if (placeIndex >= 0) {
            // Encontramos a subnet alvo
            if (!net.lugares[placeIndex].subnet) return net;

            const subnet = net.lugares[placeIndex].subnet;

            // Atualizar lugares
            if (subnet.lugares) {
              subnet.lugares = subnet.lugares.map((l) => {
                const finalElement = lastAction.data.final.find(
                  (e) => e.type === "place" && e.id === l.id
                );
                return finalElement
                  ? { ...l, coordenadas: finalElement.data.coordenadas }
                  : l;
              });
            }

            // Atualizar transições
            if (subnet.transicoes) {
              subnet.transicoes = subnet.transicoes.map((t) => {
                const finalElement = lastAction.data.final.find(
                  (e) => e.type === "transition" && e.id === t.id
                );
                return finalElement
                  ? { ...t, coordenadas: finalElement.data.coordenadas }
                  : t;
              });
            }

            // Atualizar agentes
            if (subnet.agentes) {
              subnet.agentes = subnet.agentes.map((a) => {
                const finalElement = lastAction.data.final.find(
                  (e) => e.type === "agent" && e.id === a.id
                );
                if (finalElement) {
                  return {
                    ...a,
                    coordenadas: finalElement.data.coordenadas,
                    // Se tiver informações de tamanho, restaurá-las também
                    ...(finalElement.data.width ? { width: finalElement.data.width } : {}),
                    ...(finalElement.data.height ? { height: finalElement.data.height } : {})
                  };
                }
                return a;
              });
            }

            return net;
          }

          // Buscar recursivamente
          if (net.lugares) {
            net.lugares = net.lugares.map(lugar => {
              if (lugar.subnet) {
                const newPath = [...path, lugar.id];
                return {
                  ...lugar,
                  subnet: updateSubnetRecursively(lugar.subnet, targetId, newPath)
                };
              }
              return lugar;
            });
          }

          return net;
        };

        // Atualizar a subnet usando o subnetId armazenado na ação
        return updateSubnetRecursively(updatedNet, lastAction.data.subnetId || lastAction.data.inSubnet);
      } else {
        // Estamos na rede principal

        // Atualizar lugares
        updatedNet.lugares = updatedNet.lugares.map((l) => {
          const finalElement = lastAction.data.final.find(
            (e) => e.type === "place" && e.id === l.id
          );
          return finalElement
            ? { ...l, coordenadas: finalElement.data.coordenadas }
            : l;
        });

        // Atualizar transições
        updatedNet.transicoes = updatedNet.transicoes.map((t) => {
          const finalElement = lastAction.data.final.find(
            (e) => e.type === "transition" && e.id === t.id
          );
          return finalElement
            ? { ...t, coordenadas: finalElement.data.coordenadas }
            : t;
        });

        // Atualizar agentes
        if (updatedNet.agentes) {
          updatedNet.agentes = updatedNet.agentes.map((a) => {
            const finalElement = lastAction.data.final.find(
              (e) => e.type === "agent" && e.id === a.id
            );
            if (finalElement) {
              return {
                ...a,
                coordenadas: finalElement.data.coordenadas,
                // Se tiver informações de tamanho, restaurá-las também
                ...(finalElement.data.width ? { width: finalElement.data.width } : {}),
                ...(finalElement.data.height ? { height: finalElement.data.height } : {})
              };
            }
            return a;
          });
        }

        return updatedNet;
      }
    });
  };

  const handleRedoPaste = (lastAction) => {
    // First recreate places and transitions
    lastAction.data.elements
      .filter((element) => element.type !== "arc")
      .forEach((element) => {
        if (element.type === "place") {
          createPlaceElement(
            element.id,
            element.data.nome,
            element.data.tokens,
            element.data.coordenadas
          );
        } else if (element.type === "transition") {
          createTransitionElement(
            element.id,
            element.data.nome,
            element.data.orientacao,
            element.data.coordenadas
          );
        }
      });

    // After a slight delay to ensure elements are created, recreate arcs
    setTimeout(() => {
      lastAction.data.elements
        .filter((element) => element.type === "arc")
        .forEach((element) => {
          createArcElement(element.data);
        });
    }, 0);

    // Update petriNet state
    setPetriNet((prev) => ({
      ...prev,
      lugares: [
        ...prev.lugares,
        ...lastAction.data.elements
          .filter((e) => e.type === "place")
          .map((e) => e.data),
      ],
      transicoes: [
        ...prev.transicoes,
        ...lastAction.data.elements
          .filter((e) => e.type === "transition")
          .map((e) => e.data),
      ],
      arcos: [
        ...prev.arcos,
        ...lastAction.data.elements
          .filter((e) => e.type === "arc")
          .map((e) => e.data),
      ],
    }));
  };
  // Função para desfazer a adição de um agente
  const handleUndoAddAgent = (lastAction) => {
    const agentId = lastAction.data.id;

    // Remover o elemento visual
    const agentElement = graphRef.current.getElements().find(
      el => el.get('type') === 'agent' && el.get('agentId') === agentId
    );
    if (agentElement) agentElement.remove();

    // Atualizar o modelo de dados
    setPetriNet((prev) => {
      const updatedNet = JSON.parse(JSON.stringify(prev));

      if (lastAction.data.inSubnet) {
        // Agente estava em uma subnet
        const subnet = findNestedSubnet(updatedNet, lastAction.data.subnetId);
        if (subnet && subnet.agentes) {
          subnet.agentes = subnet.agentes.filter(a => a.id !== agentId);
        }
      } else {
        // Agente estava na rede principal
        updatedNet.agentes = updatedNet.agentes.filter(a => a.id !== agentId);
      }

      return updatedNet;
    });
  };

  // Função para refazer a adição de um agente
  const handleRedoAddAgent = (lastAction) => {
    const agentData = lastAction.data;

    // Criar elemento visual
    createAgentElement(agentData);

    // Atualizar o modelo de dados
    setPetriNet((prev) => {
      const updatedNet = JSON.parse(JSON.stringify(prev));

      if (agentData.inSubnet) {
        // Agente deve ser adicionado na subnet
        const subnet = findNestedSubnet(updatedNet, agentData.subnetId);
        if (subnet) {
          if (!subnet.agentes) subnet.agentes = [];
          subnet.agentes.push(agentData);
        }
      } else {
        // Agente deve ser adicionado na rede principal
        if (!updatedNet.agentes) updatedNet.agentes = [];
        updatedNet.agentes.push(agentData);
      }

      return updatedNet;
    });
  };

  // Função para desfazer o redimensionamento de um agente
  // Função para desfazer o redimensionamento de um agente
  const handleUndoResizeAgent = (lastAction) => {
    const { id, initial, inSubnet, subnetId } = lastAction.data;

    // Remover o agente atual
    const agentElement = graphRef.current.getElements().find(
      el => el.get('type') === 'agent' && el.get('agentId') === id
    );
    if (agentElement) agentElement.remove();

    // Recriar com as dimensões originais
    const agent = new joint.shapes.basic.Rect({
      id: `agent_${id}`,
      position: { x: initial.coordenadas.x, y: initial.coordenadas.y },
      size: { width: initial.width, height: initial.height },
      attrs: {
        rect: {
          fill: 'rgba(230, 242, 255, 0.4)',
          stroke: '#A3C7E3',
          'stroke-width': 2,
          'vector-effect': 'non-scaling-stroke',
          rx: 10,
          ry: 10
        },
        text: {
          text: initial.nome || 'Agente',
          'font-size': 14,
          'font-weight': 'bold',
          'ref-x': 0.5,
          'ref-y': 15,
          'text-anchor': 'middle',
          fill: '#666'
        }
      },
      markup: `
        <g class="rotatable">
          <g class="scalable">
            <rect/>
          </g>
          <text/>
        </g>
      `,
    });

    // Configurar metadados
    agent.set('type', 'agent');
    agent.set('agentId', id);
    agent.set('z', -10);

    // Adicionar ao gráfico
    graphRef.current.addCell(agent);

    // Atualizar o modelo de dados
    setPetriNet((prev) => {
      const updatedNet = JSON.parse(JSON.stringify(prev));

      if (inSubnet) {
        // Agente está em uma subnet
        const updateSubnetRecursively = (net, targetId, path = []) => {
          // Evitar loops infinitos
          if (path.includes(targetId)) return net;

          // Verificar se encontramos a subnet alvo neste nível
          const placeIndex = net.lugares.findIndex(l => l.id === targetId);
          if (placeIndex >= 0) {
            // Encontramos a subnet alvo
            if (!net.lugares[placeIndex].subnet) return net;

            const subnet = net.lugares[placeIndex].subnet;

            // Inicializar o array de agentes se não existir
            if (!subnet.agentes) subnet.agentes = [];

            // Verificar se o agente existe na subnet
            const agentIndex = subnet.agentes.findIndex(a => a.id === id);
            if (agentIndex >= 0) {
              // Atualizar o agente existente
              subnet.agentes[agentIndex] = {
                ...subnet.agentes[agentIndex],
                coordenadas: initial.coordenadas,
                width: initial.width,
                height: initial.height
              };
            }

            return net;
          }

          // Buscar recursivamente
          if (net.lugares) {
            net.lugares = net.lugares.map(lugar => {
              if (lugar.subnet) {
                const newPath = [...path, lugar.id];
                return {
                  ...lugar,
                  subnet: updateSubnetRecursively(lugar.subnet, targetId, newPath)
                };
              }
              return lugar;
            });
          }

          return net;
        };

        // Atualizar a subnet usando o subnetId
        return updateSubnetRecursively(updatedNet, subnetId);
      } else {
        // Agente está na rede principal
        // Inicializar o array de agentes se não existir
        if (!updatedNet.agentes) updatedNet.agentes = [];

        // Verificar se o agente existe na rede principal
        const agentIndex = updatedNet.agentes.findIndex(a => a.id === id);
        if (agentIndex >= 0) {
          // Atualizar o agente existente
          updatedNet.agentes[agentIndex] = {
            ...updatedNet.agentes[agentIndex],
            coordenadas: initial.coordenadas,
            width: initial.width,
            height: initial.height
          };
        }

        return updatedNet;
      }
    });
  };

  // Função para refazer o redimensionamento de um agente
  const handleRedoResizeAgent = (lastAction) => {
    const { id, final, inSubnet, subnetId } = lastAction.data;

    // 1. Remover o agente atual
    const agentElement = graphRef.current.getElements().find(
      el => el.get('type') === 'agent' && el.get('agentId') === id
    );
    if (agentElement) agentElement.remove();

    // 2. Obter nome do agente atual para manter na recriação
    let agentName = final.nome || 'Agente';

    // 3. Criar um novo agente usando EXATAMENTE os valores finais
    const agent = new joint.shapes.basic.Rect({
      id: `agent_${id}`,
      // IMPORTANTE: Usar posição e tamanho exatamente como estão em final
      position: { x: final.coordenadas.x, y: final.coordenadas.y },
      size: { width: final.width, height: final.height },
      attrs: {
        rect: {
          fill: 'rgba(230, 242, 255, 0.4)',
          stroke: '#A3C7E3',
          'stroke-width': 2,
          'vector-effect': 'non-scaling-stroke',
          rx: 10,
          ry: 10
        },
        text: {
          text: agentName,
          'font-size': 14,
          'font-weight': 'bold',
          'ref-x': 0.5,
          'ref-y': 15,
          'text-anchor': 'middle',
          fill: '#666'
        }
      },
      markup: `
        <g class="rotatable">
          <g class="scalable">
            <rect/>
          </g>
          <text/>
        </g>
      `,
    });

    // Configurar metadados
    agent.set('type', 'agent');
    agent.set('agentId', id);
    agent.set('z', -10);

    // Adicionar ao gráfico
    graphRef.current.addCell(agent);

    // Atualizar o modelo de dados - simplificado para evitar erros
    setPetriNet(prev => {
      const newNet = JSON.parse(JSON.stringify(prev));

      if (inSubnet) {
        const subnet = findNestedSubnet(newNet, subnetId);
        if (subnet && subnet.agentes) {
          const agentIndex = subnet.agentes.findIndex(a => a.id === id);
          if (agentIndex >= 0) {
            // Manter todos os dados do agente, atualizando apenas posição e dimensões
            subnet.agentes[agentIndex] = {
              ...subnet.agentes[agentIndex],
              // IMPORTANTE: Usar exatamente os mesmos valores de final
              coordenadas: { x: final.coordenadas.x, y: final.coordenadas.y },
              width: final.width,
              height: final.height
            };
          }
        }
      } else {
        if (newNet.agentes) {
          const agentIndex = newNet.agentes.findIndex(a => a.id === id);
          if (agentIndex >= 0) {
            // Manter todos os dados do agente, atualizando apenas posição e dimensões
            newNet.agentes[agentIndex] = {
              ...newNet.agentes[agentIndex],
              // IMPORTANTE: Usar exatamente os mesmos valores de final
              coordenadas: { x: final.coordenadas.x, y: final.coordenadas.y },
              width: final.width,
              height: final.height
            };
          }
        }
      }

      return newNet;
    });

    // Para depuração
    console.log('REDO Resize - Valores FINAIS aplicados:', {
      id,
      coordenadas: final.coordenadas,
      width: final.width,
      height: final.height
    });
  }

  // =========== ELEMENT CREATION AND MANIPULATION ===========

  /**
   * Create a place element in the graph
   */
  const createPlaceElement = (id, name, tokens = 0, coordinates) => {
    const place = new joint.shapes.basic.Circle({
      id,
      position: coordinates,
      size: { width: 50, height: 50 },
      markup: `
        <g class="rotatable">
          <g class="scalable">
            <circle class="body"/>
          </g>
          <text class="label"/>
          <text class="tokens"/>
        </g>
      `,
      attrs: {
        ".body": { fill: "lightblue" },
        ".label": {
          text: wrapText(name, 20),
          fill: "black",
          "font-size": 14,
          "ref-y": -30,
          "text-anchor": "middle",
          "ref-x": 0.5,
        },
        ".tokens": {
          text: formatTokens(tokens),
          fill: "red",
          "font-size": 14,
          "text-anchor": "middle",
          "ref-x": 0.5,
          "ref-y": 0.4,
        },
      },
    });

    graphRef.current.addCell(place);
    return place;
  };

  /**
   * Create a transition element in the graph
   */
  const createTransitionElement = (
    id,
    name,
    orientation = "vert",
    coordinates,
    isInterface = false,
    interfaceType = null
  ) => {
    const size =
      orientation === "vert"
        ? { width: 3, height: 50 }
        : { width: 50, height: 3 };

    // Cores diferentes para tipos de interface
    let fillColor = "gray"; // Padrão para transições normais
    if (isInterface) {
      if (interfaceType === "entrada") {
        fillColor = "#ff9966"; // Laranja mais claro para entradas
      } else if (interfaceType === "saida") {
        fillColor = "#ff6600"; // Laranja mais escuro para saídas
      } else if (interfaceType === "bidirecional") {
        fillColor = "#cc3300"; // Vermelho para interfaces bidirecionais
      } else {
        fillColor = "orange"; // Padrão para interfaces não especificadas
      }
    }

    // Ícone ou marcador para indicar direção
    let interfaceMarker = "";
    if (isInterface) {
      if (interfaceType === "entrada") {
        interfaceMarker = "→";
      } else if (interfaceType === "saida") {
        interfaceMarker = "←";
      } else if (interfaceType === "bidirecional") {
        interfaceMarker = "↔";
      }
    }
    // No início da função createTransitionElement
    console.log(
      `Criando transição: ID=${id}, isInterface=${isInterface}, tipo=${interfaceType}`
    );
    console.log(`Cor: ${fillColor}, Marcador: "${interfaceMarker}"`);
    // Adicionar informação de peso para interfaces
    let weightInfo = "";
    if (isInterface && currentNetId) {
      const subnet = findNestedSubnet(petriNet, currentNetId);
      if (subnet && subnet.transicoes) {
        const interfaceT = subnet.transicoes.find((t) => t.id === id);

        if (interfaceT) {
          if (interfaceType === "entrada") {
            weightInfo = `[${interfaceT.peso_in_restante || 0}/${interfaceT.peso_in || 0
              }]`;
          } else if (interfaceType === "saida") {
            weightInfo = `[${interfaceT.peso_out_restante || 0}/${interfaceT.peso_out || 0
              }]`;
          } else if (interfaceType === "bidirecional") {
            weightInfo = `[↓${interfaceT.peso_in_restante || 0}/${interfaceT.peso_in || 0
              }|↑${interfaceT.peso_out_restante || 0}/${interfaceT.peso_out || 0
              }]`;
          }
        }
      }
    }

    const transition = new joint.shapes.basic.Rect({
      id,
      position: coordinates,
      size: size,
      markup: `
      <g class="rotatable">
        <g class="scalable">
          <rect class="body"/>
        </g>
        <text class="label"/>
        <text class="interface-marker"/>
      </g>
    `,
      attrs: {
        ".body": {
          fill: fillColor,
          cursor: "move",
          width: size.width,
          height: size.height,
        },
        ".label": {
          text: wrapText(name, 20),
          fill: "black",
          "font-size": 14,
          "ref-y": -30,
          "text-anchor": "middle",
          "ref-x": 0.5,
        },
        ".interface-marker": {
          text: interfaceMarker,
          fill: "black",
          "font-size": 16,
          "font-weight": "bold",
          "text-anchor": "middle",
          "ref-x": 0.5,
          "ref-y": orientation === "vert" ? -10 : -20,
        },
      },
    });

    graphRef.current.addCell(transition);
    return transition;
  };



  const updateInterfaceWeightsDisplay = () => {
    if (!currentNetId) return;

    const subnet = findNestedSubnet(petriNet, currentNetId);
    if (!subnet || !subnet.transicoes) return;

    // Atualizar os valores de peso restantes
    checkInterfaceWeightLimits(subnet);

    // Atualizar a exibição visual
    subnet.transicoes.forEach((t) => {
      if (t.isInterface) {
        const element = graphRef.current.getCell(t.id);
        if (element) {
          let weightInfo = "";
          if (t.interfaceType === "entrada") {
            weightInfo = `[${t.peso_in_restante || 0}/${t.peso_in || 0}]`;
          } else if (t.interfaceType === "saida") {
            weightInfo = `[${t.peso_out_restante || 0}/${t.peso_out || 0}]`;
          } else if (t.interfaceType === "bidirecional") {
            weightInfo = `[↓${t.peso_in_restante || 0}/${t.peso_in || 0}|↑${t.peso_out_restante || 0
              }/${t.peso_out || 0}]`;
          }

          element.attr(".weight-info/text", weightInfo);
        }
      }
    });
  };

  /**
   * Detecta quais transições são bidirecionais em uma subnet
   * (aparecem tanto nas listas de entrada quanto de saída)
   */
  const detectBidirectionalInterfaces = (subnet) => {
    // Mapear transições para contar ocorrências como entrada e saída
    const transitionCounts = new Map();

    // Contar ocorrências nas entradas
    for (const transId of subnet.entradas || []) {
      if (!transitionCounts.has(transId)) {
        transitionCounts.set(transId, { entrada: 0, saida: 0 });
      }
      const counts = transitionCounts.get(transId);
      counts.entrada++;
    }

    // Contar ocorrências nas saídas
    for (const transId of subnet.saidas || []) {
      if (!transitionCounts.has(transId)) {
        transitionCounts.set(transId, { entrada: 0, saida: 0 });
      }
      const counts = transitionCounts.get(transId);
      counts.saida++;
    }

    // Identificar transições bidirecionais (que aparecem tanto em entradas quanto saídas)
    const bidirectional = [];
    transitionCounts.forEach((counts, transId) => {
      if (counts.entrada > 0 && counts.saida > 0) {
        bidirectional.push(transId);
      }
    });

    return bidirectional;
  };

  /**
   * Cria interfaces na subnet com suporte a conexões bidirecionais
   * Esta função deve ser chamada durante a inicialização ou atualização de uma subnet
   */
  /**
   * Cria interfaces na subnet com suporte a conexões bidirecionais
   * Esta função deve ser chamada durante a inicialização ou atualização de uma subnet
   */

  //AO  APAGAR ISSO RETORNOU AO ESTADO ANTES DA MUDANCA DA INTERFACE DA FUNCAO ABAIXO
  const createInterfaceTransitions = (subnet, parentNet, placeElementId) => {
    const arcosDoLugarExplodido = parentNet.arcos.filter(
      (arco) =>
        arco.origem === placeElementId || arco.destino === placeElementId
    );

    console.log("Arcos encontrados corretamente:", arcosDoLugarExplodido);

    const result = JSON.parse(JSON.stringify(subnet));
    // Salvar posições das interfaces existentes
    const interfacePositions = new Map();
    result.transicoes
      .filter((t) => t.isInterface)
      .forEach((t) => {
        // Usar uma chave única que combine tipo e transição original
        const key = `${t.interfaceType}_${t.originTransitionId}`;
        interfacePositions.set(key, t.coordenadas);
      });

    console.log("Posições salvas:", [...interfacePositions.entries()]);

    const bidirectionalTrans = detectBidirectionalInterfaces(result);
    console.log("Transições bidirecionais detectadas:", bidirectionalTrans);

    result.transicoes = result.transicoes.filter((t) => !t.isInterface);

    const processedIds = new Set();

    // Aqui já não precisa mais buscar parentNet pois já está disponível
    console.log("Informações da rede pai:", {
      netStackLength: netStack.length,
      placeElementId,
      parentNetArcs: parentNet.arcos.length,
    });
    const getArcWeight = (sourceId, targetId, interfaceType) => {
      // Verificar se existe um arco
      const arc = parentNet.arcos.find(
        (a) => a.origem === sourceId && a.destino === targetId
      );

      if (arc) {
        // Arco encontrado, usar seu peso (com verificação explícita para undefined)
        const pesoArco = arc.peso !== undefined ? arc.peso : 1;
        console.log(
          `Arco encontrado: ${sourceId} -> ${targetId}, peso: ${pesoArco}`
        );
        return pesoArco;
      } else {
        // Sem arco - determinar se este é um caso de "peso zero"

        // Para interfaces de entrada (transição→lugar no nível superior)
        if (interfaceType === "entrada") {
          // Verificar se a transição está na lista de entradas
          const isInEntradas = (subnet.entradas || []).includes(sourceId);
          if (isInEntradas) {
            console.log(
              `Transição ${sourceId} está nas entradas sem arco - usando peso 0`
            );
            return 0;
          }
        }

        // Para interfaces de saída (lugar→transição no nível superior)
        if (interfaceType === "saida") {
          // Verificar se a transição está na lista de saídas
          const isInSaidas = (subnet.saidas || []).includes(targetId);
          if (isInSaidas) {
            console.log(
              `Transição ${targetId} está nas saídas sem arco - usando peso 0`
            );
            return 0;
          }
        }

        // Caso padrão
        console.log(
          `Arco não encontrado e não é interface especial: ${sourceId} -> ${targetId}, usando peso 1`
        );
        return 1;
      }
    };
    const getArcWeighty = (sourceId, targetId, interfaceType) => {
      // Verificar se existe um arco
      const arc = parentNet.arcos.find(
        (a) => a.origem === sourceId && a.destino === targetId
      );

      if (arc) {
        // Arco encontrado, usar seu peso (com fallback para 1)
        console.log(
          `Arco encontrado: ${sourceId} -> ${targetId}, peso: ${arc.peso || 1}`
        );
        return arc.peso !== undefined ? arc.peso : 1;
      } else {
        // Sem arco - determinar se este é um caso de "peso zero"

        // Para interfaces de entrada (transição→lugar no nível superior)
        if (interfaceType === "entrada") {
          // Verificar se a transição está na lista de entradas
          const isInEntradas = (subnet.entradas || []).includes(sourceId);
          if (isInEntradas) {
            console.log(
              `Transição ${sourceId} está nas entradas sem arco - usando peso 0`
            );
            return 0;
          }
        }

        // Para interfaces de saída (lugar→transição no nível superior)
        if (interfaceType === "saida") {
          // Verificar se a transição está na lista de saídas
          const isInSaidas = (subnet.saidas || []).includes(targetId);
          if (isInSaidas) {
            console.log(
              `Transição ${targetId} está nas saídas sem arco - usando peso 0`
            );
            return 0;
          }
        }

        // Caso padrão
        console.log(
          `Arco não encontrado e não é interface especial: ${sourceId} -> ${targetId}, usando peso 1`
        );
        return 1;
      }
    };
    const getArcWeightx = (sourceId, targetId) => {
      const arc = parentNet.arcos.find(
        (a) => a.origem === sourceId && a.destino === targetId
      );

      if (arc) {
        console.log(
          `Arco encontrado: ${sourceId} -> ${targetId}, peso: ${arc.peso || 1}`
        );
        return arc.peso || 1;
      } else {
        console.log(`Arco não encontrado: ${sourceId} -> ${targetId}`);
        return 1;
      }
    };

    bidirectionalTrans.forEach((transId, index) => {
      const transition = findTransitionById(petriNet, transId);
      if (!transition) return;

      processedIds.add(transId);

      const peso_in = getArcWeight(transId, placeElementId, "entrada"); // ← CORRIGIDO AQUI
      const peso_out = getArcWeight(placeElementId, transId, "saida"); // ← CORRIGIDO AQUI
      // Verificar se temos posição salva para esta interface
      const savedPosition = interfacePositions.get(`bidirecional_${transId}`);
      // Usar posição salva ou padrão
      const position = savedPosition || { x: 250, y: 100 + index * 100 };
      // Procurar por uma interface existente com os mesmos dados
      const existingInterface = subnet.transicoes.find(
        (t) =>
          t.isInterface &&
          t.interfaceType === "bidirecional" &&
          t.originTransitionId === transId
      );

      result.transicoes.push({
        id: `T_IF_BI_${index}_${transId}`,
        nome: transition.nome || "",
        orientacao: transition.orientacao || "vert",
        coordenadas: position,
        prioridade: transition.prioridade || 1,
        probabilidade: transition.probabilidade || 0,
        tempo: transition.tempo || 0,
        isInterface: true,
        originTransitionId: transId,
        interfaceType: "bidirecional",
        // Usar pesos existentes ou novos
        peso_in: existingInterface?.peso_in || peso_in,
        peso_out: existingInterface?.peso_out || peso_out,
        peso_in_restante: existingInterface?.peso_in_restante || peso_in,
        peso_out_restante: existingInterface?.peso_out_restante || peso_out,
      });
    });

    let inIndex = 0;
    for (const transId of result.entradas || []) {
      if (processedIds.has(transId)) continue;
      processedIds.add(transId);

      const transition = findTransitionById(petriNet, transId);
      if (!transition) continue;

      const peso_in = getArcWeight(transId, placeElementId, "entrada"); // ← CORRIGIDO AQUI
      // Verificar se temos posição salva para esta interface
      const savedPosition = interfacePositions.get(`entrada_${transId}`);
      // Usar posição salva ou padrão
      const position = savedPosition || { x: 150, y: 100 + inIndex * 100 };

      result.transicoes.push({
        id: `T_IF_IN_${inIndex}_${transId}`,
        nome: transition.nome || "",
        orientacao: transition.orientacao || "vert",
        coordenadas: position,
        prioridade: transition.prioridade || 1,
        probabilidade: transition.probabilidade || 0,
        tempo: transition.tempo || 0,
        isInterface: true,
        originTransitionId: transId,
        interfaceType: "entrada",
        peso_in,
        peso_in_restante: peso_in,
      });

      inIndex++;
    }

    let outIndex = 0;
    for (const transId of result.saidas || []) {
      if (processedIds.has(transId)) continue;
      processedIds.add(transId);

      const transition = findTransitionById(petriNet, transId);
      if (!transition) continue;

      const peso_out = getArcWeight(placeElementId, transId, "saida"); // ← CORRIGIDO AQUI
      // Verificar se temos posição salva para esta interface
      const savedPosition = interfacePositions.get(`saida_${transId}`);
      // Usar posição salva ou padrão
      const position = savedPosition || { x: 350, y: 100 + outIndex * 100 };

      result.transicoes.push({
        id: `T_IF_OUT_${outIndex}_${transId}`,
        nome: transition.nome || "",
        orientacao: transition.orientacao || "vert",
        coordenadas: position,
        prioridade: transition.prioridade || 1,
        probabilidade: transition.probabilidade || 0,
        tempo: transition.tempo || 0,
        isInterface: true,
        originTransitionId: transId,
        interfaceType: "saida",
        peso_out,
        peso_out_restante: peso_out,
      });

      outIndex++;
    }

    console.log(
      "Interfaces com pesos definidos:",
      result.transicoes
        .filter((t) => t.isInterface)
        .map((t) => ({
          id: t.id,
          type: t.interfaceType,
          origin: t.originTransitionId,
          peso_in: t.peso_in,
          peso_out: t.peso_out,
        }))
    );

    return result;
  };

  /**
   * Valida se a direção de um arco é compatível com os tipos de interface
   * Retorna true se o arco for válido, false caso contrário
   */
  //ATE AQUI SE CTRL Z
  const validateInterfaceConnection = (sourceId, targetId) => {
    console.log(`Validando: ${sourceId} -> ${targetId}`);

    if (!currentNetId) return true;

    // Verificar diretamente pelo prefixo do ID
    // Para interfaces de entrada
    if (targetId.startsWith("T_IF_IN_")) {
      console.log("BLOQUEADO: Interface de entrada não pode receber arcos");
      alert(
        "Erro: Interfaces de entrada devem ter arcos saindo delas, não chegando."
      );
      return false;
    }

    // Para interfaces de saída
    if (sourceId.startsWith("T_IF_OUT_")) {
      console.log("BLOQUEADO: Interface de saída não pode gerar arcos");
      alert(
        "Erro: Interfaces de saída devem ter arcos chegando nelas, não saindo."
      );
      return false;
    }

    return true;
  };
  /**
   * Create an arc between elements in the graph
   */
  const createArcElement = ({ origem, destino, peso = 1 }) => {
    // Check if source and target elements exist
    const sourceElement = graphRef.current.getCell(origem);
    const targetElement = graphRef.current.getCell(destino);

    if (!sourceElement || !targetElement) {
      console.warn("Cannot create arc: source or target element doesn't exist");
      return null;
    }

    const link = new joint.shapes.standard.Link({
      source: {
        id: origem,
        anchor: { name: "center" },
        connectionPoint: {
          name: "boundary",
          args: { sticky: true },
        },
      },
      target: {
        id: destino,
        anchor: { name: "center" },
        connectionPoint: {
          name: "boundary",
          args: { sticky: true },
        },
      },
      router: { name: "normal" },
      connector: {
        name: "smooth",
        args: {
          type: "cubic",
          smoothness: 0.4,
          allowReverse: false,
        },
      },
      attrs: {
        line: {
          stroke: "black",
          strokeWidth: 2,
          targetMarker: {
            type: "path",
            d: "M 10 -5 0 0 10 5 z",
            fill: "black",
          },
        },
      },
    });

    // Add weight label if not 1
    if (peso !== 1) {
      link.label(0, {
        position: 0.95,
        attrs: {
          text: {
            text: peso.toString(),
            "font-size": 12,
            "font-weight": "bold",
            "ref-x": 15,
            "ref-y": -10,
          },
        },
      });
    }

    graphRef.current.addCell(link);
    return link;
  };

  /**
   * Update place visuals based on its data
   */
  const updatePlaceVisuals = (placeElement, data) => {
    placeElement.attr({
      ".body": { fill: "lightblue" },
      ".label": {
        text: wrapText(data.nome, 20),
        fill: "black",
        "ref-y": -30,
        "font-size": 14,
        "text-anchor": "middle",
        "ref-x": 0.5,
      },
      ".tokens": {
        text: formatTokens(data.tokens),
        fill: "red",
        "font-size": 14,
        "text-anchor": "middle",
        "ref-x": 0.5,
        "ref-y": 0.4,
        "line-height": "0",
      },
    });
  };

  /**
   * Update transition visuals based on its data and selection state
   */
  const updateTransitionVisuals = (
    transitionElement,
    data,
    isSelected = false
  ) => {
    transitionElement.attr({
      ".body": {
        fill: isSelected ? "red" : "gray",
        stroke: isSelected ? "red" : "black",
        "stroke-width": isSelected ? 4 : 1,
      },
      ".label": {
        text: wrapText(data.nome, 20),
        fill: "black",
        "font-size": 14,
        "ref-y": -30,
        "text-anchor": "middle",
        "ref-x": 0.5,
      },
    });
  };

  /**
   * Add a new place at the specified coordinates
   */
  const addPlace = (x, y) => {
    const id = `P${placeCount}`;
    const coordenadas = { x: x - 25, y: y - 25 };

    // Create place element
    createPlaceElement(id, id, 0, coordenadas);

    // Create place data
    const newPlace = {
      id,
      nome: id,
      tokens: 0,
      coordenadas,
      delay: 0,
    };

    // Record action for undo
    recordAction("add_place", newPlace);

    // Update petriNet state based on current level
    if (currentNetId) {
      // We are in a subnet, update it directly
      setPetriNet((prev) => {
        const updatedNet = JSON.parse(JSON.stringify(prev));

        const updateSubnetRecursively = (net, targetId, path = []) => {
          // Verificar se estamos tentando acessar um ID já visitado (evitar loops infinitos)
          if (path.includes(targetId)) {
            console.error("Loop detectado ao procurar subnet:", path);
            return false;
          }

          // Verificar se temos uma rede e lugares definidos
          if (!net || !net.lugares) {
            console.error(
              "Rede ou lista de lugares indefinida para ID:",
              targetId
            );
            return false;
          }

          // Verificar se é o alvo direto
          const placeIndex = net.lugares.findIndex((l) => l.id === targetId);
          if (placeIndex >= 0) {
            // Encontrou o lugar alvo, verificar se ele tem subnet
            if (!net.lugares[placeIndex].subnet) {
              net.lugares[placeIndex].subnet = {
                lugares: [],
                transicoes: [],
                arcos: [],
              };
            }

            // Certificar que lugares existe
            if (!net.lugares[placeIndex].subnet.lugares) {
              net.lugares[placeIndex].subnet.lugares = [];
            }

            // Adicionar lugar à subnet
            net.lugares[placeIndex].subnet.lugares.push(newPlace);
            return true;
          }

          // Não encontrou diretamente, procurar recursivamente em cada lugar com subnet
          for (let i = 0; i < net.lugares.length; i++) {
            const lugar = net.lugares[i];
            // Verificar se o lugar tem uma subnet definida
            if (lugar && lugar.subnet) {
              // Adicionar o ID atual ao caminho para detectar loops
              const newPath = [...path, lugar.id];

              // Fazer a chamada recursiva para procurar na subnet deste lugar
              const found = updateSubnetRecursively(
                lugar.subnet,
                targetId,
                newPath
              );

              if (found) return true;
            }
          }

          return false;
        };

        updateSubnetRecursively(updatedNet, currentNetId);
        return updatedNet;
      });
    } else {
      // We are in the main network
      setPetriNet((prev) => ({
        ...prev,
        lugares: [...prev.lugares, newPlace],
      }));
    }

    // Increment counter
    setPlaceCount((prev) => prev + 1);
    // No final da função addPlace
    setTimeout(() => {
      verificarPlaceDentroDeAgente(id, coordenadas);
    }, 0);
  };

  // Função análoga para adicionar transições, garantindo que o modelo de dados da subnet seja atualizado
  const addTransition = (x, y) => {
    const id = `T${transitionCount}`;
    const coordenadas = { x: x - 1.5, y: y - 25 };

    // Create transition element
    createTransitionElement(id, id, "vert", coordenadas);

    // Create transition data
    const newTransition = {
      id,
      nome: id,
      orientacao: "vert",
      coordenadas,
      prioridade: 1,
      probabilidade: 0,
      tempo: 0,
    };

    // Record action for undo
    recordAction("add_transition", newTransition);

    // Update petriNet state based on current level
    if (currentNetId) {
      // We are in a subnet, update it directly
      setPetriNet((prev) => {
        const updatedNet = JSON.parse(JSON.stringify(prev));

        const updateSubnetRecursively = (net, targetId, path = []) => {
          // Verificar se estamos tentando acessar um ID já visitado (evitar loops infinitos)
          if (path.includes(targetId)) {
            console.error("Loop detectado ao procurar subnet:", path);
            return false;
          }

          // Verificar se temos uma rede e lugares definidos
          if (!net || !net.lugares) {
            console.error(
              "Rede ou lista de lugares indefinida para ID:",
              targetId
            );
            return false;
          }

          // Verificar se é o alvo direto
          const placeIndex = net.lugares.findIndex((l) => l.id === targetId);
          if (placeIndex >= 0) {
            // Encontrou o lugar alvo, verificar se ele tem subnet
            if (!net.lugares[placeIndex].subnet) {
              net.lugares[placeIndex].subnet = {
                lugares: [],
                transicoes: [],
                arcos: [],
              };
            }

            // Certificar que transicoes existe
            if (!net.lugares[placeIndex].subnet.transicoes) {
              net.lugares[placeIndex].subnet.transicoes = [];
            }

            // Adicionar transição à subnet
            net.lugares[placeIndex].subnet.transicoes.push(newTransition);
            return true;
          }

          // Não encontrou diretamente, procurar recursivamente em cada lugar com subnet
          for (let i = 0; i < net.lugares.length; i++) {
            const lugar = net.lugares[i];
            // Verificar se o lugar tem uma subnet definida
            if (lugar && lugar.subnet) {
              // Adicionar o ID atual ao caminho para detectar loops
              const newPath = [...path, lugar.id];

              // Fazer a chamada recursiva para procurar na subnet deste lugar
              const found = updateSubnetRecursively(
                lugar.subnet,
                targetId,
                newPath
              );

              if (found) return true;
            }
          }

          return false;
        };

        updateSubnetRecursively(updatedNet, currentNetId);
        return updatedNet;
      });
    } else {
      // We are in the main network
      setPetriNet((prev) => ({
        ...prev,
        transicoes: [...prev.transicoes, newTransition],
      }));
    }

    // Increment counter
    setTransitionCount((prev) => prev + 1);
  };
  const renderAgents = () => {
    console.log('===== DEPURAÇÃO RENDERAGENTS =====');
    console.log('currentNetId:', currentNetId);
    console.log('Agentes principais:', petriNet.agentes);
    // Limpar agentes existentes no gráfico
    const existingAgents = graphRef.current
      .getElements()
      .filter(el => el.get("type") === "agent");
    existingAgents.forEach(agent => agent.remove());

    if (currentNetId) {
      // Estamos em uma subnet, renderizar APENAS agentes desta subnet
      const currentSubnet = findNestedSubnet(petriNet, currentNetId);
      console.log('Estrutura completa da subnet encontrada:', currentSubnet);
      console.log('Agentes na subnet:', currentSubnet.agentes);
      if (currentSubnet && currentSubnet.agentes) {
        console.log('Renderizando agentes da subnet, quantidade:', currentSubnet.agentes.length);

        currentSubnet.agentes.forEach(agente => {
          console.log('Renderizando agente da subnet:', agente.id, agente.nome);

          createAgentElement(agente);
        });

      }
    } else {
      // Estamos na rede principal, renderizar APENAS agentes da rede principal
      // Estamos na rede principal, renderizar APENAS agentes da rede principal
      console.log('Agentes na rede principal:', petriNet.agentes);

      if (petriNet.agentes) {
        console.log('Renderizando agentes da rede principal, quantidade:', petriNet.agentes.length);

        petriNet.agentes.forEach(agente => {
          console.log('Renderizando agente da rede principal:', agente.id, agente.nome);

          createAgentElement(agente);
        });
      }
    }
    // Verificar após renderização o que realmente está no canvas
    const agentesNoCanvas = graphRef.current
      .getElements()
      .filter(el => el.get("type") === "agent");
    console.log('Agentes no canvas após renderização:', agentesNoCanvas.length);
    agentesNoCanvas.forEach(el => {
      console.log('Agente no canvas:', el.get('agentId'));
    });

  };

  // Função createAgentElement simplificada
  const createAgentElement = (agente) => {
    const width = agente.width || 300;
    const height = agente.height || 200;

    const agent = new joint.shapes.basic.Rect({
      id: `agent_${agente.id}`,
      position: { x: agente.coordenadas.x, y: agente.coordenadas.y },
      size: { width, height },
      attrs: {
        rect: {
          fill: 'rgba(230, 242, 255, 0.4)',
          stroke: '#A3C7E3',
          'stroke-width': 6,
          'vector-effect': 'non-scaling-stroke',
          rx: 10,
          ry: 10
        },
        text: {
          text: agente.nome,
          'font-size': 14,
          'font-weight': 'bold',
          'ref-x': 0.5,           // Centralizar horizontalmente (0.5 = 50% da largura)
          'ref-y': 15,            // Manter na parte superior
          'text-anchor': 'middle',
          fill: '#666'
        }
      },
      markup: `
        <g class="rotatable">
          <g class="scalable">
            <rect/>
          </g>
          <text/>
        </g>
      `,
    });

    // Configurar metadados e z-index
    agent.set('type', 'agent');
    agent.set('agentId', agente.id);
    agent.set('z', -10);

    // Adicionar ao gráfico
    graphRef.current.addCell(agent);

    return agent;
  };

  // Função addAgent corrigida para adicionar agentes no nível correto
  const addAgent = (x, y) => {
    // Gerar ID e nome adequados
    let newId, agentName;

    if (currentNetId) {
      // Estamos em uma subnet
      const currentSubnet = findNestedSubnet(petriNet, currentNetId);
      const subnetAgentes = currentSubnet?.agentes || [];

      newId = `AG_SUB_${subnetAgentes.length + 1}`;
      agentName = `Agente ${subnetAgentes.length + 1}`;

    } else {
      // Estamos na rede principal
      const mainAgentes = petriNet.agentes || [];
      newId = `AG_MAIN_${mainAgentes.length + 1}`;
      agentName = `Agente ${mainAgentes.length + 1}`;
    }

    const coordenadas = { x: x - 150, y: y - 100 };

    // Criar objeto do agente
    const newAgente = {
      id: newId,
      nome: agentName,
      coordenadas,
      width: 300,
      height: 200
    };

    // Criar elemento visual
    createAgentElement(newAgente);

    // Adicionar o agente no nível correto do modelo de dados
    if (currentNetId) {
      // Estamos em uma subnet, adicionar diretamente na subnet correta
      setPetriNet((prev) => {
        const updatedNet = JSON.parse(JSON.stringify(prev));

        // Função para encontrar e atualizar a subnet correta de forma recursiva
        const updateSubnetAgents = (net, targetId, path = []) => {
          // Evitar loops infinitos
          if (path.includes(targetId)) return false;

          // Verificar se o lugar está neste nível
          const placeIndex = net.lugares.findIndex(l => l.id === targetId);
          if (placeIndex >= 0) {
            // Encontrou o lugar que contém a subnet
            if (!net.lugares[placeIndex].subnet) {
              net.lugares[placeIndex].subnet = {
                lugares: [],
                transicoes: [],
                arcos: [],
                agentes: [],
              };
            }

            // Garantir que o array de agentes exista
            if (!net.lugares[placeIndex].subnet.agentes) {
              net.lugares[placeIndex].subnet.agentes = [];
            }

            // Adicionar o agente à subnet
            net.lugares[placeIndex].subnet.agentes.push(newAgente);
            console.log(`Agente ${newAgente.id} adicionado à subnet ${targetId}`);
            return true;
          }

          // Procurar recursivamente em subnets mais profundas
          for (let i = 0; i < net.lugares.length; i++) {
            const lugar = net.lugares[i];
            if (lugar && lugar.subnet) {
              const found = updateSubnetAgents(
                lugar.subnet,
                targetId,
                [...path, lugar.id]
              );
              if (found) return true;
            }
          }

          return false;
        };

        updateSubnetAgents(updatedNet, currentNetId);
        return updatedNet;
      });
    } else {
      // Estamos na rede principal, adicionar na lista principal de agentes
      setPetriNet(prev => ({
        ...prev,
        agentes: [...(prev.agentes || []), newAgente]
      }));
      console.log(`Agente ${newAgente.id} adicionado à rede principal`);
    }
    setTimeout(() => {
      verificarPlacesDentroDoAgente(newId);
    }, 0);
  };



  /**
   * Delete an element and all its connected arcs
   */
  // Substitua toda a função handleDelete por esta versão:

  const handleDelete = (element, type) => {
    if (!element) {
      console.warn("Elemento não encontrado para exclusão");
      return;
    }

    console.log("Excluindo elemento:", type, element);

    // Verificar se estamos em uma sub-rede
    const isInSubnet = currentNetId !== null;

    // Verificar se é uma transição de interface (que não pode ser excluída)
    if (isInSubnet && type === "transition" && element.isInterface) {
      alert("Transições de interface não podem ser excluídas");
      return;
    }

    // Array para armazenar itens excluídos para o undo
    const deletedItems = [];

    if (isInSubnet) {
      // Trabalhando com elementos em uma sub-rede
      const currentPlace = petriNet.lugares.find((l) => l.id === currentNetId);

      if (!currentPlace || !currentPlace.subnet) {
        console.error("Sub-rede não encontrada");
        return;
      }

      // Criar uma cópia da sub-rede para modificação
      const updatedSubnet = { ...currentPlace.subnet };

      if (type === "place" || type === "transition") {
        const elementCell = graphRef.current.getCell(element.id);
        if (!elementCell) {
          console.warn("Elemento gráfico não encontrado:", element.id);
          return;
        }

        // Adicionar o elemento principal aos itens excluídos
        deletedItems.push({
          id: element.id,
          type,
          data: element,
        });

        // Encontrar e adicionar arcos conectados
        const connectedArcs = updatedSubnet.arcos.filter(
          (a) => a.origem === element.id || a.destino === element.id
        );

        connectedArcs.forEach((arco) => {
          deletedItems.push({
            id: `${arco.origem}-${arco.destino}`,
            type: "arc",
            data: arco,
          });
        });

        // Registrar para undo
        recordAction("delete", deletedItems);

        // Remover arcos conectados do gráfico
        const connectedLinks = graphRef.current.getConnectedLinks(elementCell);
        connectedLinks.forEach((link) => link.remove());

        // Remover o elemento do gráfico
        elementCell.remove();

        // Atualizar a sub-rede
        if (type === "place") {
          updatedSubnet.lugares = updatedSubnet.lugares.filter(
            (l) => l.id !== element.id
          );
        } else {
          updatedSubnet.transicoes = updatedSubnet.transicoes.filter(
            (t) => t.id !== element.id
          );
        }

        updatedSubnet.arcos = updatedSubnet.arcos.filter(
          (a) => a.origem !== element.id && a.destino !== element.id
        );
      } else if (type === "agent") {
        // Tratamento específico para agentes em subnet
        const agentElement = graphRef.current.getElements().find(
          el => el.get('type') === 'agent' && el.get('agentId') === element.id
        );

        if (!agentElement) {
          console.warn("Elemento de agente não encontrado:", element.id);
          return;
        }

        // Adicionar o agente aos itens excluídos
        deletedItems.push({
          id: element.id,
          type: "agent",
          data: element,
        });

        // Registrar para undo
        recordAction("delete", deletedItems);

        // Remover o elemento visual
        agentElement.remove();

        // Atualizar a subnet
        if (updatedSubnet.agentes) {
          updatedSubnet.agentes = updatedSubnet.agentes.filter(
            (a) => a.id !== element.id
          );
        }
      } else if (type === "arc") {
        // Registrar o arco para undo
        deletedItems.push({
          id: `${element.origem}-${element.destino}`,
          type: "arc",
          data: element,
        });

        recordAction("delete", deletedItems);

        // Remover o arco do gráfico
        const link = graphRef.current
          .getLinks()
          .find(
            (l) =>
              l.attributes.source.id === element.origem &&
              l.attributes.target.id === element.destino
          );

        if (link) link.remove();

        // Atualizar a sub-rede
        updatedSubnet.arcos = updatedSubnet.arcos.filter(
          (a) => a.origem !== element.origem || a.destino !== element.destino
        );
        if (currentNetId) {
          // Primeiro atualizar o modelo antes de atualizar o display
          setPetriNet((prev) => {
            const updatedPetriNet = {
              ...prev,
              lugares: prev.lugares.map((l) =>
                l.id === currentNetId ? { ...l, subnet: updatedSubnet } : l
              ),
            };

            // Depois que o estado for atualizado, chamar a função para atualizar o display
            setTimeout(() => updateInterfaceWeightsDisplay(), 0);

            return updatedPetriNet;
          });
        } else {
          // Se não estamos em subnet, apenas atualizar o modelo normalmente
          setPetriNet((prev) => ({
            ...prev,
            lugares: prev.lugares.map((l) =>
              l.id === currentNetId ? { ...l, subnet: updatedSubnet } : l
            ),
          }));
        }

        // Retornar aqui para evitar a atualização duplicada
        return;
      }

      // Atualizar o petriNet com a sub-rede modificada
      setPetriNet((prev) => ({
        ...prev,
        lugares: prev.lugares.map((l) =>
          l.id === currentNetId ? { ...l, subnet: updatedSubnet } : l
        ),
      }));
    } else {
      // Código existente para a rede principal
      if (type === "place" || type === "transition") {
        const elementCell = graphRef.current.getCell(element.id);

        // Obter dados do elemento principal
        const elementData = {
          id: element.id,
          type,
          data: petriNet[type === "place" ? "lugares" : "transicoes"].find(
            (e) => e.id === element.id
          ),
        };

        // Obter arcos conectados
        const connectedArcs = petriNet.arcos.filter(
          (a) => a.origem === element.id || a.destino === element.id
        );

        // Adicionar o elemento principal aos itens excluídos
        deletedItems.push({
          id: element.id,
          type,
          data: elementData.data,
        });

        // Adicionar cada arco como um item separado
        connectedArcs.forEach((arco) => {
          deletedItems.push({
            id: `${arco.origem}-${arco.destino}`,
            type: "arc",
            data: {
              origem: arco.origem,
              destino: arco.destino,
              peso: arco.peso || 1,
            },
          });
        });

        // Registrar para undo
        recordAction("delete", deletedItems);

        // Remover arcos conectados do gráfico
        const connectedLinks = graphRef.current.getConnectedLinks(elementCell);
        connectedLinks.forEach((link) => link.remove());

        // Remover o elemento do gráfico
        elementCell.remove();

        // Atualizar o estado petriNet
        setPetriNet((prev) => ({
          ...prev,
          lugares:
            type === "place"
              ? prev.lugares.filter((l) => l.id !== element.id)
              : prev.lugares,
          transicoes:
            type === "transition"
              ? prev.transicoes.filter((t) => t.id !== element.id)
              : prev.transicoes,
          arcos: prev.arcos.filter(
            (a) => a.origem !== element.id && a.destino !== element.id
          ),
        }));
      } else if (type === "agent") {
        // Tratamento específico para agentes na rede principal
        const agentElement = graphRef.current.getElements().find(
          el => el.get('type') === 'agent' && el.get('agentId') === element.id
        );

        if (!agentElement) {
          console.warn("Elemento de agente não encontrado:", element.id);
          return;
        }

        // Adicionar o agente aos itens excluídos
        deletedItems.push({
          id: element.id,
          type: "agent",
          data: element,
        });

        // Registrar para undo
        recordAction("delete", deletedItems);

        // Remover o elemento visual
        agentElement.remove();

        // Atualizar o modelo de dados
        setPetriNet((prev) => ({
          ...prev,
          agentes: prev.agentes.filter((a) => a.id !== element.id),
        }));
      } else if (type === "arc") {
        // Para arcos, salvamos apenas o próprio arco
        deletedItems.push({
          id: `${element.origem}-${element.destino}`,
          type: "arc",
          data: {
            origem: element.origem,
            destino: element.destino,
            peso: element.peso || 1,
          },
        });

        recordAction("delete", deletedItems);

        // Remover o arco do gráfico
        const link = graphRef.current
          .getLinks()
          .find(
            (l) =>
              l.attributes.source.id === element.origem &&
              l.attributes.target.id === element.destino
          );
        if (link) link.remove();

        // Remover o arco do modelo
        setPetriNet((prev) => ({
          ...prev,
          arcos: prev.arcos.filter(
            (a) => a.origem !== element.origem || a.destino !== element.destino
          ),
        }));
      }
    }
    // Após remover um arco, atualizar as interfaces das subnets
    if (type === "arc") {
      // Função auxiliar para remover um ID da lista
      const removeFromList = (list, id) => {
        return list.filter((item) => item !== id);
      };

      // Função auxiliar para atualizar entradas/saídas de uma subnet
      const updateSubnetInterface = (
        net,
        placeId,
        updateEntradas,
        updateSaidas
      ) => {
        // Procurar o lugar diretamente neste nível
        const place = net.lugares.find((l) => l.id === placeId);
        if (place && place.subnet) {
          const updatedSubnet = { ...place.subnet };

          if (updateEntradas && updatedSubnet.entradas) {
            updatedSubnet.entradas = updateEntradas(updatedSubnet.entradas);
          }

          if (updateSaidas && updatedSubnet.saidas) {
            updatedSubnet.saidas = updateSaidas(updatedSubnet.saidas);
          }

          return {
            ...net,
            lugares: net.lugares.map((l) =>
              l.id === placeId ? { ...l, subnet: updatedSubnet } : l
            ),
          };
        }

        // Se não encontramos neste nível, procurar recursivamente nas sub-redes
        return {
          ...net,
          lugares: net.lugares.map((l) => {
            if (l.subnet && l.subnet.lugares) {
              return {
                ...l,
                subnet: updateSubnetInterface(
                  l.subnet,
                  placeId,
                  updateEntradas,
                  updateSaidas
                ),
              };
            }
            return l;
          }),
        };
      };

      // Verificar se a origem é um lugar com subnet
      const { net: sourceNet } = findContainingNet(petriNet, element.origem);
      if (sourceNet) {
        const origemElement = sourceNet.lugares.find(
          (l) => l.id === element.origem
        );
        if (origemElement && origemElement.subnet) {
          console.log(
            "Atualizando interfaces após remoção de arco - saída:",
            element.origem
          );

          // Atualizar o modelo
          setPetriNet((prev) =>
            updateSubnetInterface(prev, element.origem, null, (saidas) =>
              removeFromList(saidas, element.destino)
            )
          );
        }
      }

      // Verificar se o destino é um lugar com subnet
      const { net: targetNet } = findContainingNet(petriNet, element.destino);
      if (targetNet) {
        const destinoElement = targetNet.lugares.find(
          (l) => l.id === element.destino
        );
        if (destinoElement && destinoElement.subnet) {
          console.log(
            "Atualizando interfaces após remoção de arco - entrada:",
            element.destino
          );

          // Atualizar o modelo
          setPetriNet((prev) =>
            updateSubnetInterface(
              prev,
              element.destino,
              (entradas) => removeFromList(entradas, element.origem),
              null
            )
          );
        }
      }
    }
  };

  /**
   * Delete all selected elements
   */
  const deleteSelectedElements = () => {
    if (selectedElements.size === 0) return;

    // Array to store all elements that will be deleted
    const deletedItems = [];
    const elementsToProcess = new Set(selectedElements);

    // First, collect all data before making any removal
    elementsToProcess.forEach((elementId) => {
      const element = graphRef.current.getCell(elementId);
      if (!element) return;

      const type = element.attributes.type;

      if (type === "basic.Circle" || type === "basic.Rect") {
        const elementType = type === "basic.Circle" ? "place" : "transition";

        // Get element data
        const elementData = petriNet[
          elementType === "place" ? "lugares" : "transicoes"
        ].find((e) => e.id === elementId);

        // Add main element to deleted items
        deletedItems.push({
          id: elementId,
          type: elementType,
          data: elementData,
        });

        // Find and add all connected arcs
        const connectedArcs = petriNet.arcos.filter(
          (a) => a.origem === elementId || a.destino === elementId
        );

        // Add each arc as a separate item
        connectedArcs.forEach((arco) => {
          if (
            !deletedItems.some(
              (item) =>
                item.type === "arc" &&
                item.data.origem === arco.origem &&
                item.data.destino === arco.destino
            )
          ) {
            deletedItems.push({
              id: `${arco.origem}-${arco.destino}`,
              type: "arc",
              data: {
                origem: arco.origem,
                destino: arco.destino,
                peso: arco.peso || 1,
              },
            });
          }
        });
      } else if (type === "standard.Link") {
        // For directly selected links
        const sourceId = element.attributes.source.id;
        const targetId = element.attributes.target.id;
        const arco = petriNet.arcos.find(
          (a) => a.origem === sourceId && a.destino === targetId
        );

        if (
          arco &&
          !deletedItems.some(
            (item) =>
              item.type === "arc" &&
              item.data.origem === arco.origem &&
              item.data.destino === arco.destino
          )
        ) {
          deletedItems.push({
            id: `${sourceId}-${targetId}`,
            type: "arc",
            data: {
              origem: sourceId,
              destino: targetId,
              peso: arco.peso || 1,
            },
          });
        }
      } else if (element.get('type') === 'agent') {
        // Para agentes selecionados
        const agentId = element.get('agentId');

        // Encontrar dados do agente no modelo
        const agentData = petriNet.agentes.find(a => a.id === agentId);

        if (agentData) {
          deletedItems.push({
            id: agentId,
            type: "agent",
            data: agentData
          });
        }
      }
    });

    // Record delete action with all collected items
    if (deletedItems.length > 0) {
      recordAction("delete", deletedItems);
    }

    // Now perform the removals
    elementsToProcess.forEach((elementId) => {
      const element = graphRef.current.getCell(elementId);
      if (!element) return;

      const type = element.attributes.type;

      if (type === "basic.Circle" || type === "basic.Rect") {
        // Remove connected arcs from graph
        const connectedLinks = graphRef.current.getConnectedLinks(element);
        connectedLinks.forEach((link) => link.remove());

        // Remove element from graph
        element.remove();
      } else if (type === "standard.Link") {
        // Remove arc from graph
        element.remove();
      } else if (element.get('type') === 'agent') {
        // Remove agent from graph
        element.remove();
      }
    });

    // Update petriNet state
    setPetriNet((prev) => {
      const newState = { ...prev };

      // Remove places and transitions
      newState.lugares = prev.lugares.filter(
        (l) => !elementsToProcess.has(l.id)
      );
      newState.transicoes = prev.transicoes.filter(
        (t) => !elementsToProcess.has(t.id)
      );

      // Remove all affected arcs
      newState.arcos = prev.arcos.filter(
        (a) =>
          !elementsToProcess.has(a.origem) &&
          !elementsToProcess.has(a.destino) &&
          !deletedItems.some(
            (item) =>
              item.type === "arc" &&
              item.data.origem === a.origem &&
              item.data.destino === a.destino
          )
      );
      if (newState.agentes) {
        newState.agentes = prev.agentes.filter(
          (a) => !deletedItems.some(item => item.type === "agent" && item.id === a.id)
        );
      }

      return newState;
    });
    // Remove agents


    // Clear selection
    setSelectedElements(new Set());
  };

  // =========== CLIPBOARD OPERATIONS (COPY/PASTE) ===========

  /**
   * Copy selected elements to clipboard
   * @param {boolean} cut - If true, elements are cut instead of copied
   */
  const handleCopy = (cut = false) => {
    if (selectedElements.size === 0) return;

    const clipboardData = {
      elements: [],
      positions: new Map(),
      relations: [],
    };

    // Calculate center point for paste positioning
    const centerPoint = { x: 0, y: 0 };
    let count = 0;

    // Collect all selected elements
    selectedElements.forEach((id) => {
      const element = graphRef.current.getCell(id);
      if (!element) return;

      const pos = element.position();
      centerPoint.x += pos.x;
      centerPoint.y += pos.y;
      count++;

      if (element.attributes.type === "basic.Circle") {
        const lugar = petriNet.lugares.find((l) => l.id === id);
        if (lugar) {
          clipboardData.elements.push({
            type: "place",
            data: { ...lugar },
          });
          clipboardData.positions.set(id, { x: pos.x, y: pos.y });
        }
      } else if (element.attributes.type === "basic.Rect") {
        const transicao = petriNet.transicoes.find((t) => t.id === id);
        if (transicao) {
          clipboardData.elements.push({
            type: "transition",
            data: { ...transicao },
          });
          clipboardData.positions.set(id, pos);
        }
      } else if (element.isLink()) {
        const arcoData = petriNet.arcos.find(
          (a) =>
            a.origem === element.attributes.source.id &&
            a.destino === element.attributes.target.id
        );
        if (arcoData) {
          clipboardData.relations.push({ ...arcoData });
        }
      }
    });

    if (count > 0) {
      centerPoint.x /= count;
      centerPoint.y /= count;
      clipboardData.center = centerPoint;
    }

    // Collect arcs between selected elements
    petriNet.arcos.forEach((arco) => {
      // Check if both ends of the arc are selected
      // And if the arc hasn't already been added (in case it was directly selected)
      if (
        selectedElements.has(arco.origem) &&
        selectedElements.has(arco.destino) &&
        !clipboardData.relations.some(
          (r) => r.origem === arco.origem && r.destino === arco.destino
        )
      ) {
        clipboardData.relations.push({ ...arco });
      }
    });

    setClipboard(clipboardData);

    if (cut) {
      deleteSelectedElements();
    }
  };

  /**
   * Paste elements from clipboard at current mouse position
   */
  const handlePaste = () => {
    if (!clipboard || !clipboard.elements.length) return;

    // Get current mouse position relative to paper
    const paperRect = paperRef.current.el.getBoundingClientRect();
    const scale = paperRef.current.scale().sx;
    const translation = paperRef.current.translate();

    const mousePosition = {
      x: (window.lastMouseX - paperRect.left - translation.tx) / scale,
      y: (window.lastMouseY - paperRect.top - translation.ty) / scale,
    };

    // Calculate offset based on mouse position
    const offsetX = mousePosition.x - clipboard.center.x;
    const offsetY = mousePosition.y - clipboard.center.y;

    // Map old IDs to new ones
    const idMap = new Map();
    const newElements = new Set();
    let hasPasted = false;
    const finalState = { elements: [] };

    // Local variables to control IDs
    let nextPlaceId = placeCount;
    let nextTransitionId = transitionCount;

    // Create all elements
    clipboard.elements.forEach((element) => {
      const oldId = element.data.id;

      if (element.type === "place") {
        const newId = `P${nextPlaceId++}`;
        idMap.set(oldId, newId);

        const oldPos = element.data.coordenadas;
        const newPos = {
          x: oldPos.x + offsetX,
          y: oldPos.y + offsetY,
        };
        const newElement = {
          ...element.data,
          id: newId,
          coordenadas: newPos,
        };

        // Update petriNet state
        setPetriNet((prev) => ({
          ...prev,
          lugares: [...prev.lugares, newElement],
        }));

        // Create place element
        createPlaceElement(newId, newElement.nome, newElement.tokens, newPos);

        newElements.add(newId);
        hasPasted = true;
        finalState.elements.push({
          id: newId,
          type: "place",
          data: { ...element.data, id: newId, coordenadas: newPos },
        });
      } else if (element.type === "transition") {
        const newId = `T${nextTransitionId++}`;
        idMap.set(oldId, newId);

        const oldPos = element.data.coordenadas;
        const newPos = {
          x: oldPos.x + offsetX,
          y: oldPos.y + offsetY,
        };
        const newElement = {
          ...element.data,
          id: newId,
          coordenadas: newPos,
        };

        // Update petriNet state
        setPetriNet((prev) => ({
          ...prev,
          transicoes: [...prev.transicoes, newElement],
        }));

        // Create transition element
        createTransitionElement(
          newId,
          newElement.nome,
          newElement.orientacao,
          newPos
        );

        newElements.add(newId);
        hasPasted = true;
        finalState.elements.push({
          id: newId,
          type: "transition",
          data: { ...element.data, id: newId, coordenadas: newPos },
        });
      }
    });

    // Update counters after the loop
    setPlaceCount(nextPlaceId);
    setTransitionCount(nextTransitionId);

    // Create arcs using new IDs
    clipboard.relations.forEach((arco) => {
      const newSourceId = idMap.get(arco.origem);
      const newTargetId = idMap.get(arco.destino);

      if (newSourceId && newTargetId) {
        // Create arc with new IDs
        const newArc = {
          origem: newSourceId,
          destino: newTargetId,
          peso: arco.peso,
        };

        createArcElement(newArc);

        // Update petriNet state
        setPetriNet((prev) => ({
          ...prev,
          arcos: [...prev.arcos, newArc],
        }));
        updateSubnetInterfaces(newArc);

        hasPasted = true;
        finalState.elements.push({
          id: `${newSourceId}-${newTargetId}`,
          type: "arc",
          data: newArc,
        });
      }
    });

    if (hasPasted) {
      // Record paste action for undo/redo
      recordAction("paste", {
        elements: finalState.elements,
        mousePosition,
        offset: {
          x: offsetX,
          y: offsetY,
        },
      });
    }
  };

  // =========== FILE OPERATIONS ===========

  /**
   * Handle "Save" or "Save As" operations
   *
   */
  const handleRename = (newName) => {
    // Normalizar a rede antes de salvar
    const updatedNet = {
      ...petriNet,
      nome: newName,
      lugares: petriNet.lugares.map((lugar) => {
        if (!lugar.hasOwnProperty("subnet")) {
          return { ...lugar, subnet: {} };
        }
        return lugar;
      }),
    };

    setPetriNet(updatedNet);


    const fileName = `${newName}.json`;

    const dataStr = JSON.stringify(updatedNet, null, 2);
    console.log("UPDATE NET")
    console.log(updatedNet)

    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    // Atualizar arquivo atual
    setCurrentFile({ name: fileName });
    setRenameModalOpen(false);
    setSaveAction(null);
  };
  /**
   * 5. Função auxiliar para normalizar a rede (garantir que todos os lugares tenham subnet)
   */
  const normalizeNetwork = (net) => {
    // Garantir que todos os lugares tenham subnet definida
    const normalizedLugares = net.lugares.map((lugar) => {
      const hasSubnet = lugar.hasOwnProperty("subnet");

      if (!hasSubnet) {
        return { ...lugar, subnet: {} };
      }

      // Normalizar recursivamente se houver uma sub-rede
      if (
        lugar.subnet &&
        lugar.subnet.lugares &&
        lugar.subnet.lugares.length > 0
      ) {
        return {
          ...lugar,
          subnet: {
            ...lugar.subnet,
            lugares: lugar.subnet.lugares.map((l) => normalizePlace(l)),
          },
        };
      }

      return lugar;
    });

    return {
      ...net,
      lugares: normalizedLugares,
    };
  };

  /**
   * 6. Função auxiliar para normalizar um lugar recursivamente
   */
  const normalizePlace = (place) => {
    const hasSubnet = place.hasOwnProperty("subnet");

    if (!hasSubnet) {
      return { ...place, subnet: {} };
    }

    // Normalizar recursivamente se houver uma sub-rede
    if (
      place.subnet &&
      place.subnet.lugares &&
      place.subnet.lugares.length > 0
    ) {
      return {
        ...place,
        subnet: {
          ...place.subnet,
          lugares: place.subnet.lugares.map((l) => normalizePlace(l)),
        },
      };
    }

    return place;
  };

  /**
   * 7. Função auxiliar para encontrar um lugar em qualquer nível da rede
   */
  const findPlaceInNet = (net, placeId) => {
    // Procurar no nível principal
    const place = net.lugares.find((l) => l.id === placeId);
    if (place) return place;

    // Procurar recursivamente nas sub-redes
    for (const lugar of net.lugares) {
      if (
        lugar.subnet &&
        lugar.subnet.lugares &&
        lugar.subnet.lugares.length > 0
      ) {
        const subPlace = findPlaceInNet(lugar.subnet, placeId);
        if (subPlace) return subPlace;
      }
    }

    return null;
  };
  /**
   * 9. Função auxiliar para atualizar contadores de ID
   */
  const updateCounters = (net) => {
    // Encontrar o maior ID de lugar e transição em toda a hierarquia
    const maxPlaceId = getMaxPlaceId(net);
    const maxTransitionId = getMaxTransitionId(net);

    setPlaceCount(maxPlaceId + 1);
    setTransitionCount(maxTransitionId + 1);
  };

  /**
   * 10. Funções auxiliares para encontrar o maior ID em toda a hierarquia
   */
  const getMaxPlaceId = (net) => {
    let maxId = 0;

    // Verificar no nível atual
    net.lugares.forEach((lugar) => {
      const id = parseInt(lugar.id.replace(/^P/, "")) || 0;
      maxId = Math.max(maxId, id);

      // Verificar recursivamente nas sub-redes
      if (
        lugar.subnet &&
        lugar.subnet.lugares &&
        lugar.subnet.lugares.length > 0
      ) {
        const subMaxId = getMaxPlaceId(lugar.subnet);
        maxId = Math.max(maxId, subMaxId);
      }
    });

    return maxId;
  };

  const getMaxTransitionId = (net) => {
    let maxId = 0;

    // Verificar no nível atual
    net.transicoes.forEach((transicao) => {
      const id = parseInt(transicao.id.replace(/^T/, "")) || 0;
      maxId = Math.max(maxId, id);
    });

    // Verificar recursivamente nas sub-redes
    net.lugares.forEach((lugar) => {
      if (
        lugar.subnet &&
        lugar.subnet.transicoes &&
        lugar.subnet.transicoes.length > 0
      ) {
        const subMaxId = getMaxTransitionId(lugar.subnet);
        maxId = Math.max(maxId, subMaxId);
      }
    });

    return maxId;
  };

  const handleSaveFile = (action) => {
    // Se a ação for "saveAs", abrir o modal de renomeação
    if (action === "saveAs") {
      setSaveAction(action);
      setRenameModalOpen(true);
      return;
    }

    if (action === "save") {
      if (currentFile) {
        // Normalizar a rede antes de salvar (mesmo processo que handleRename)
        const updatedNet = {
          ...petriNet,
          nome: petriNet.nome,
          lugares: petriNet.lugares.map((lugar) => {
            if (!lugar.hasOwnProperty("subnet")) {
              return { ...lugar, subnet: {} };
            }
            return lugar;
          }),
        };

        // Salvar o arquivo diretamente
        const fileName = currentFile.name;
        const dataStr = JSON.stringify(updatedNet, null, 2);
        console.log("SALVANDO REDE");
        console.log(updatedNet);

        const dataBlob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(dataBlob);
        const a = document.createElement("a");
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        // Se não tem arquivo atual, abrir modal para definir nome
        setSaveAction(action);
        setRenameModalOpen(true);
      }
    }
  };
  /**
   * Load a file from disk
   */
  const handleLoad = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        let loadedNet = JSON.parse(e.target.result);
        clearNetwork();
        // Garantir que a estrutura de agentes exista
        if (!loadedNet.agentes) {
          loadedNet.agentes = [];
        }
        // Normalizar a rede para garantir que todos os lugares tenham subnet
        loadedNet = normalizeNetwork(loadedNet);

        // Agora podemos carregar todos os elementos com segurança
        renderFullNetwork(loadedNet);

        setPetriNet(loadedNet);

        // Resetar o estado de navegação para a rede principal
        setNetStack([]);
        setCurrentNetId(null);

        // Atualizar contadores
        updateCounters(loadedNet);

        setCurrentFile({ name: file.name });
      } catch (error) {
        console.error("Erro ao carregar o arquivo:", error);
        alert("Erro ao carregar o arquivo");
      }
    };
    reader.readAsText(file);
  };

  /**
   * Create a new Petri net
   */
  const handleNew = () => {
    clearNetwork();
    setCurrentFile(null);
  };

  /**
   * Load a Petri net dict into the canvas (replaces current network).
   */
  const loadNetIntoCanvas = useCallback((net) => {
    if (!net || typeof net !== "object") return;
    clearNetwork();
    if (!net.agentes) net.agentes = [];
    const normalized = normalizeNetwork(net);
    renderFullNetwork(normalized);
    setPetriNet(normalized);
    setNetStack([]);
    setCurrentNetId(null);
    updateCounters(normalized);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Confirm callback from GeneratePetriNetModal: calls /api/petri-net/{projectId}/generate
   */
  const handleGenerateConfirm = useCallback(async (sel) => {
    if (!projectId) {
      alert("projectId não definido — não é possível gerar a rede.");
      return;
    }
    setGenerateModalOpen(false);
    setIsLoadingNet(true);
    try {
      const net = await petriNetService.generatePetriNet(projectId, sel);
      loadNetIntoCanvas(net);
    } catch (err) {
      console.error("Erro ao gerar rede:", err);
      alert(`Erro ao gerar rede: ${err.message || err}`);
    } finally {
      setIsLoadingNet(false);
    }
  }, [projectId, loadNetIntoCanvas]);

  /**
   * Save current network to backend (projects.project_data)
   */
  const handleSaveToBackend = useCallback(async () => {
    if (!projectId) {
      alert("projectId não definido — não é possível salvar.");
      return;
    }
    try {
      const updatedNet = {
        ...petriNet,
        lugares: (petriNet.lugares || []).map((l) =>
          l && typeof l === "object" && !("subnet" in l) ? { ...l, subnet: {} } : l,
        ),
      };
      await petriNetService.updatePetriNet(projectId, updatedNet);
      alert("Rede salva no banco com sucesso.");
    } catch (err) {
      console.error("Erro ao salvar:", err);
      alert(`Erro ao salvar: ${err.message || err}`);
    }
  }, [projectId, petriNet]);

  /**
   * Initial load: fetch persisted Petri Net from projects.project_data on mount.
   */
  useEffect(() => {
    if (!projectId || initialLoadDoneRef.current) return;
    initialLoadDoneRef.current = true;
    (async () => {
      setIsLoadingNet(true);
      try {
        const net = await petriNetService.getPetriNet(projectId);
        if (net && net.lugares && net.lugares.length > 0) {
          loadNetIntoCanvas(net);
        }
      } catch (err) {
        console.error("Erro ao carregar rede do banco:", err);
      } finally {
        setIsLoadingNet(false);
      }
    })();
  }, [projectId, loadNetIntoCanvas]);

  /**
   * Clear the Petri net
   */
  const clearNetwork = () => {
    graphRef.current.clear();
    setPetriNet({
      nome: "Rede de Petri",
      lugares: [],
      transicoes: [],
      arcos: [],
    });
    setPlaceCount(1);
    setTransitionCount(1);
  };

  /**
   * Handle the "Save" button click for the element being edited
   */
  // Substitua toda a função handleSave por esta versão:

  const handleSave = (formData) => {
    console.log("Salvando elemento:", editingType, formData);

    // Verificar se estamos em uma sub-rede
    const isInSubnet = currentNetId !== null;

    if (isInSubnet) {
      // Trabalhando com elementos em uma sub-rede
      const currentPlace = petriNet.lugares.find((l) => l.id === currentNetId);

      if (!currentPlace || !currentPlace.subnet) {
        console.error("Sub-rede não encontrada");
        setEditModalOpen(false);
        return;
      }

      // Criar uma cópia da sub-rede para modificação
      const updatedSubnet = { ...currentPlace.subnet };

      if (editingType === "place") {
        // Atualizar lugar na sub-rede
        updatedSubnet.lugares = updatedSubnet.lugares.map((l) =>
          l.id === editingElement.id
            ? {
              ...l,
              ...formData,
              coordenadas:
                graphRef.current.getCell(l.id)?.position() || l.coordenadas,
            }
            : l
        );

        // Atualizar visualmente
        const place = graphRef.current.getCell(editingElement.id);
        if (place) {
          // Atualização explícita do texto do label
          place.attr({
            ".label": {
              text: wrapText(formData.nome, 20),
              fill: "black",
              "ref-y": -30,
              "font-size": 14,
              "text-anchor": "middle",
              "ref-x": 0.5,
            },
          });

          // Atualização completa dos visuais
          updatePlaceVisuals(place, {
            ...editingElement,
            ...formData,
          });
        }
      } else if (editingType === "transition") {
        // Verificar se é uma transição de interface
        const isInterface = editingElement.isInterface;

        // Atualizar transição na sub-rede
        updatedSubnet.transicoes = updatedSubnet.transicoes.map((t) =>
          t.id === editingElement.id
            ? {
              ...t,
              ...formData,
              isInterface: isInterface, // Preservar status de interface
              originTransitionId: editingElement.originTransitionId, // Preservar ID original
              coordenadas:
                graphRef.current.getCell(t.id)?.position() || t.coordenadas,
            }
            : t
        );

        // Sincronizar com a transição original se for interface
        if (
          isInterface &&
          editingElement.originTransitionId &&
          netStack.length > 0
        ) {
          const originalId = editingElement.originTransitionId;
          const parentState = { ...netStack[netStack.length - 1] };
          const parentNet = { ...parentState.net };

          // Sincronizar propriedades com a transição original
          parentNet.transicoes = parentNet.transicoes.map((t) =>
            t.id === originalId
              ? {
                ...t,
                nome: formData.nome,
                prioridade: formData.prioridade,
                probabilidade: formData.probabilidade,
                tempo: formData.tempo,
              }
              : t
          );

          // Atualizar o netStack
          const updatedStack = [...netStack];
          updatedStack[updatedStack.length - 1] = {
            ...parentState,
            net: parentNet,
          };
          setNetStack(updatedStack);
        }

        // Atualizar visualmente
        const transition = graphRef.current.getCell(editingElement.id);
        if (transition) {
          // Atualização explícita do texto do label
          transition.attr({
            ".label": {
              text: wrapText(formData.nome, 20),
              fill: "black",
              "font-size": 14,
              "ref-y": -30,
              "text-anchor": "middle",
              "ref-x": 0.5,
            },
          });

          // Atualização completa dos visuais
          updateTransitionVisuals(
            transition,
            {
              ...editingElement,
              ...formData,
            },
            selectedElements.has(editingElement.id)
          );
        }
      } else if (editingType === "arc") {
        // Atualizar arco na sub-rede
        updatedSubnet.arcos = updatedSubnet.arcos.map((a) =>
          a.origem === editingElement.origem &&
            a.destino === editingElement.destino
            ? { ...a, ...formData }
            : a
        );

        // Atualizar visualmente
        const links = graphRef.current.getLinks();
        const link = links.find(
          (l) =>
            l.attributes.source.id === editingElement.origem &&
            l.attributes.target.id === editingElement.destino
        );

        if (link) {
          link.removeLabel(0);
          if (formData.peso !== 1) {
            link.label(0, {
              position: 0.95,
              attrs: {
                text: {
                  text: formData.peso.toString(),
                  "font-size": 12,
                  "font-weight": "bold",
                  "ref-x": 15,
                  "ref-y": -10,
                },
              },
            });
          }
        }
      }

      // Atualizar o petriNet com a sub-rede modificada
      setPetriNet((prev) => ({
        ...prev,
        lugares: prev.lugares.map((l) =>
          l.id === currentNetId ? { ...l, subnet: updatedSubnet } : l
        ),
      }));
    } else {
      // Trabalhando com elementos na rede principal (código existente)
      if (editingType === "place") {
        setPetriNet((prev) => ({
          ...prev,
          lugares: prev.lugares.map((l) =>
            l.id === editingElement.id
              ? {
                ...l,
                ...formData,
                coordenadas:
                  graphRef.current.getCell(l.id)?.position() || l.coordenadas,
              }
              : l
          ),
        }));

        const place = graphRef.current.getCell(editingElement.id);
        if (place) {
          // Atualização explícita do texto do label
          place.attr({
            ".label": {
              text: wrapText(formData.nome, 20),
              fill: "black",
              "ref-y": -30,
              "font-size": 14,
              "text-anchor": "middle",
              "ref-x": 0.5,
            },
          });

          updatePlaceVisuals(place, {
            ...editingElement,
            ...formData,
          });
        }
      } else if (editingType === "transition") {
        setPetriNet((prev) => ({
          ...prev,
          transicoes: prev.transicoes.map((t) =>
            t.id === editingElement.id
              ? {
                ...t,
                ...formData,
                coordenadas:
                  graphRef.current.getCell(t.id)?.position() || t.coordenadas,
              }
              : t
          ),
        }));

        const transition = graphRef.current.getCell(editingElement.id);
        if (transition) {
          // Atualização explícita do texto do label
          transition.attr({
            ".label": {
              text: wrapText(formData.nome, 20),
              fill: "black",
              "font-size": 14,
              "ref-y": -30,
              "text-anchor": "middle",
              "ref-x": 0.5,
            },
          });

          updateTransitionVisuals(
            transition,
            {
              ...editingElement,
              ...formData,
            },
            selectedElements.has(editingElement.id)
          );
        }
      } else if (editingType === "arc") {
        setPetriNet((prev) => ({
          ...prev,
          arcos: prev.arcos.map((a) =>
            a.origem === editingElement.origem &&
              a.destino === editingElement.destino
              ? { ...a, ...formData }
              : a
          ),
        }));

        const links = graphRef.current.getLinks();
        const link = links.find(
          (l) =>
            l.attributes.source.id === editingElement.origem &&
            l.attributes.target.id === editingElement.destino
        );

        if (link) {
          link.removeLabel(0);
          if (formData.peso !== 1) {
            link.label(0, {
              position: 0.95,
              attrs: {
                text: {
                  text: formData.peso.toString(),
                  "font-size": 12,
                  "font-weight": "bold",
                  "ref-x": 15,
                  "ref-y": -10,
                },
              },
            });
          }
        }
      }
    }

    setEditModalOpen(false);
  };

  // =========== INITIALIZATION AND EVENT HANDLERS ===========

  /**
   * Initialize the graph and paper
   * 
   */
  // Adicione este useEffect ao seu componente
  useEffect(() => {
    if (!paperRef.current) return;

    // Handler para verificar places dentro de agentes após movimentação
    const handleAgentMoved = (elementView) => {
      const element = elementView.model;
      if (element.get('type') === 'agent') {
        const agentId = element.get('agentId');
        setTimeout(() => {
          verificarPlacesDentroDoAgente(agentId);
        }, 50);
      }
    };

    // Registrar o event listener
    paperRef.current.on('element:pointerup', handleAgentMoved);

    // Limpar o event listener quando o componente for desmontado
    return () => {
      if (paperRef.current) {
        paperRef.current.off('element:pointerup', handleAgentMoved);
      }
    };
  }, [currentNetId]); // Incluir currentNetId nas dependências para garantir que o handler seja atualizado
  useEffect(() => {
    if (!graphRef.current) {
      graphRef.current = new joint.dia.Graph();
    }

    if (!paperRef.current) {
      paperRef.current = new joint.dia.Paper({
        el: document.getElementById("paper-container"),
        model: graphRef.current,
        width: 1550,
        height: 780,
        gridSize: 10,
        interactive: {
          elementMove: function (cellView) {
            // Permitir movimento apenas se não estiver redimensionando
            const element = cellView.model;
            if (element.get('type') === 'agent') {
              // Se estiver no meio de um redimensionamento, não permitir movimento
              return !resizingAgent;
            }
            return true; // Permitir movimento para outros elementos
          }
        }
      });

      // Variables to control pan and selection
      let isPanning = false;
      let startX, startY;
      let selectionStartX, selectionStartY;

      // Add zoom with scroll
      paperRef.current.el.addEventListener("wheel", (event) => {
        event.preventDefault();
        const delta = event.deltaY > 0 ? 0.9 : 1.1;
        const scale = paperRef.current.scale();
        paperRef.current.scale(scale.sx * delta, scale.sy * delta);
      });

      // Pan and selection handlers
      paperRef.current.on("blank:pointerdown", (evt) => {
        if (evt.ctrlKey) {
          // Convert coordinates considering translate and scale
          const scale = paperRef.current.scale().sx;
          const translation = paperRef.current.translate();

          // Adjust start point coordinates
          selectionStartX = (evt.offsetX - translation.tx) / scale;
          selectionStartY = (evt.offsetY - translation.ty) / scale;

          // Create selection rectangle with adjusted coordinates
          selectionRectRef.current = new joint.shapes.basic.Rect({
            position: {
              x: selectionStartX,
              y: selectionStartY,
            },
            size: { width: 0, height: 0 },
            attrs: {
              rect: {
                fill: "rgba(0, 0, 255, 0.1)",
                stroke: "blue",
                "stroke-dasharray": "3,3",
              },
            },
          });
          graphRef.current.addCell(selectionRectRef.current);
          evt.preventDefault();
        } else if (evt.button === 0) {
          // Original pan
          isPanning = true;
          startX = evt.clientX;
          startY = evt.clientY;
          paperRef.current.$el.css("cursor", "grabbing");
          evt.preventDefault();
        }
      });

      // Mouse move handler for selection rectangle and panning
      document.addEventListener("mousemove", (evt) => {
        if (selectionRectRef.current) {
          // Adjust coordinates considering translate and scale
          const scale = paperRef.current.scale().sx;
          const translation = paperRef.current.translate();

          // Adjust current mouse coordinates
          const currentX = (evt.offsetX - translation.tx) / scale;
          const currentY = (evt.offsetY - translation.ty) / scale;

          const width = currentX - selectionStartX;
          const height = currentY - selectionStartY;

          // Update rectangle with adjusted coordinates
          selectionRectRef.current.resize(Math.abs(width), Math.abs(height));
          selectionRectRef.current.position(
            width < 0 ? currentX : selectionStartX,
            height < 0 ? currentY : selectionStartY
          );
        } else if (isPanning) {
          const dx = evt.clientX - startX;
          const dy = evt.clientY - startY;
          const currentTranslate = paperRef.current.translate();
          paperRef.current.translate(
            currentTranslate.tx + dx,
            currentTranslate.ty + dy
          );
          startX = evt.clientX;
          startY = evt.clientY;
        }
      });

      // Mouse up handler for selection finalization
      document.addEventListener("mouseup", () => {
        if (selectionRectRef.current) {
          // Process selection
          const selectionBBox = selectionRectRef.current.getBBox();
          const elements = graphRef.current.getElements();
          const newSelection = new Set(selectedElements);

          elements.forEach((element) => {
            const elementBBox = element.getBBox();
            if (selectionBBox.intersect(elementBBox)) {
              newSelection.add(element.id);

              // Highlight selected elements
              if (element.attributes.type === "basic.Circle") {
                element.attr("circle/stroke", "red");
                element.attr("circle/stroke-width", 4);
              } else if (element.attributes.type === "basic.Rect") {
                element.attr({
                  ".body": {
                    fill: "red",
                    stroke: "red",
                    "stroke-width": 4,
                  },
                });
              }
            }
          });

          setSelectedElements(newSelection);
          selectionRectRef.current.remove();
          selectionRectRef.current = null;
        }

        if (isPanning) {
          isPanning = false;
          paperRef.current.$el.css("cursor", "");
        }
      });

      // Prevent default context menu
      const paper = document.getElementById("paper-container");
      paper.addEventListener("contextmenu", (e) => e.preventDefault());
    }

    return () => {
      if (graphRef.current) {
        graphRef.current.clear();
      }
      if (paperRef.current && paperRef.current.el) {
        paperRef.current.el.removeEventListener("wheel", () => { });
      }
      if (selectionRectRef.current) {
        selectionRectRef.current.remove();
        selectionRectRef.current = null;
      }
      // Clear context menu event listener
      const paper = document.getElementById("paper-container");
      if (paper) {
        paper.removeEventListener("contextmenu", (e) => e.preventDefault());
      }
    };
  }, []);

  /**
   * Handle clicks on the canvas to create new elements
   */
  const checkResizeArea = useCallback((element, evt) => {
    if (element.get('type') !== 'agent') return false;

    const position = element.position();
    const size = element.size();

    const paperRect = paperRef.current.el.getBoundingClientRect();
    const scale = paperRef.current.scale().sx;
    const translation = paperRef.current.translate();

    // Calcular posição do mouse relativa ao elemento
    const mouseX = (evt.clientX - paperRect.left - translation.tx) / scale - position.x;
    const mouseY = (evt.clientY - paperRect.top - translation.ty) / scale - position.y;

    // Definir a margem para área de redimensionamento
    const margin = 10;

    // Verificar cada borda
    if (mouseX <= margin) {
      // Borda esquerda
      setResizeDirection('left');
      document.body.style.cursor = 'ew-resize';
      element.set('interactive', false);
      return true;
    } else if (mouseX >= size.width - margin) {
      // Borda direita
      setResizeDirection('right');
      document.body.style.cursor = 'ew-resize';
      element.set('interactive', false);
      return true;
    } else if (mouseY <= margin) {
      // Borda superior
      setResizeDirection('top');
      document.body.style.cursor = 'ns-resize';
      element.set('interactive', false);
      return true;
    } else if (mouseY >= size.height - margin) {
      // Borda inferior
      setResizeDirection('bottom');
      document.body.style.cursor = 'ns-resize';
      element.set('interactive', false);
      return true;
    }

    return false;
  }, [paperRef]);
  useEffect(() => {
    if (!paperRef.current) return;

    const handleClick = (event, x, y) => {
      // Limpar seleção de agente
      if (selectedAgente) {
        setSelectedAgente(null);

        // Remover destaque visual
        const elements = graphRef.current.getElements();
        elements.forEach(el => {
          if (el.get('type') === 'agent') {
            el.attr('rect/stroke', '#A3C7E3');
            el.attr('rect/stroke-width', 2);
          }
        });
      }
      if (
        !selectedObject ||
        selectedObject === "arc" ||
        selectedObject === "rotate"
      )
        return;

      if (selectedObject === "place") {
        addPlace(x, y);
      } else if (selectedObject === "transition") {
        addTransition(x, y);
      } else if (selectedObject === "agent") {  // Novo caso para agente
        addAgent(x, y);
      }


      setSelectedObject(null);
    };

    /**
     * Melhora a visualização dos arcos conectados a interfaces
     * Esta função deve ser chamada após a renderização da sub-rede
     */



    const handleElementClick = (elementView, evt) => {
      const clickedElement = elementView.model;

      if (clickedElement.get('type') === 'agent') {
        // Se estamos em modo de criar elementos, ignorar
        if (selectedObject) return;

        // Verificar se estamos nas bordas para redimensionamento
        const isResizing = checkResizeArea(clickedElement, evt);
        if (isResizing) {
          // Importante: parar completamente a propagação do evento
          evt.stopPropagation();
          evt.preventDefault();

          setResizingAgent(clickedElement.get('agentId'));

          return;
        }

        // Selecionar o agente
        handleAgentSelect(clickedElement);
        evt.stopPropagation();
        return;
      }

      if (!selectedObject) return;



      if (selectedObject === "rotate") {
        if (clickedElement.attributes.type === "basic.Rect") {
          const isVertical = clickedElement.get("size").width === 3;
          const currentPos = clickedElement.position();

          if (isVertical) {
            // Rotate from vertical to horizontal
            clickedElement.set({
              size: { width: 50, height: 3 },
              position: {
                x: currentPos.x - 23.5,
                y: currentPos.y + 23.5,
              },
            });

            // Update orientation in model
            setPetriNet((prev) => ({
              ...prev,
              transicoes: prev.transicoes.map((t) =>
                t.id === clickedElement.id ? { ...t, orientacao: "hor" } : t
              ),
            }));
          } else {
            // Rotate from horizontal to vertical
            clickedElement.set({
              size: { width: 3, height: 50 },
              position: {
                x: currentPos.x + 23.5,
                y: currentPos.y - 23.5,
              },
            });

            // Update orientation in model
            setPetriNet((prev) => ({
              ...prev,
              transicoes: prev.transicoes.map((t) =>
                t.id === clickedElement.id ? { ...t, orientacao: "vert" } : t
              ),
            }));
          }
        }
        setSelectedObject(null);
        return;
      }

      if (selectedObject === "arc") {
        if (!sourceElement) {
          setSourceElement(clickedElement);
        } else {
          // Check if connection is valid (place->transition or transition->place)
          const isValidConnection =
            (sourceElement.attributes.type === "basic.Circle" &&
              clickedElement.attributes.type === "basic.Rect") ||
            (sourceElement.attributes.type === "basic.Rect" &&
              clickedElement.attributes.type === "basic.Circle");
          // ADICIONAR: Verificar se a direção do fluxo é válida para interfaces
          const isValidInterfaceFlow = validateInterfaceConnection(
            sourceElement.id,
            clickedElement.id
          );
          console.log(
            "Validação de interface:",
            sourceElement.id,
            "->",
            clickedElement.id,
            "Resultado:",
            isValidInterfaceFlow
          );

          // Check if connection already exists
          const existingLinks = graphRef.current.getLinks().filter((link) => {
            return (
              link.getSourceElement()?.id === sourceElement.id &&
              link.getTargetElement()?.id === clickedElement.id
            );
          });

          if (
            isValidConnection &&
            isValidInterfaceFlow &&
            sourceElement !== clickedElement &&
            existingLinks.length === 0
          ) {
            // Se envolver uma interface, verificar limitações de peso
            const isToInterface =
              clickedElement.attributes.type === "basic.Rect" &&
              clickedElement.attr(".interface-marker/text") !== "";
            const isFromInterface =
              sourceElement.attributes.type === "basic.Rect" &&
              sourceElement.attr(".interface-marker/text") !== "";

            if ((isToInterface || isFromInterface) && currentNetId) {
              // Primeiro, clone a subnet atual
              const currentSubnet = findNestedSubnet(petriNet, currentNetId);
              if (currentSubnet) {
                const testSubnet = JSON.parse(JSON.stringify(currentSubnet));

                // Adicionar o arco teste
                const testArc = createArcWithConsistentWeight(
                  sourceElement.id,
                  clickedElement.id
                );
                testSubnet.arcos.push(testArc);

                // Verificar se excede limites
                const checkResult = checkInterfaceWeightLimits(testSubnet);

                if (!checkResult.valid) {
                  alert(checkResult.message);
                  setSourceElement(null);
                  setSelectedObject(null);
                  return;
                }
              }
            }

            // Create arc
            /*
            const newArc = {
              origem: sourceElement.id,
              destino: clickedElement.id,
              peso: 1,
            };
            */
            // Criar o arco com peso apropriado
            const newArc = createArcWithConsistentWeight(
              sourceElement.id,
              clickedElement.id
            );

            createArcElement(newArc);

            // Record action for undo
            recordAction("add_arc", newArc);

            // Add arc to model at the correct level
            if (currentNetId) {
              setPetriNet((prev) => {
                const updatedNet = JSON.parse(JSON.stringify(prev));

                // Find the subnet and add the arc to it
                // O problema ocorre na parte de criação de arcos dentro do handleElementClick
                // Especificamente onde tenta adicionar o arco ao modelo de dados da subnet
                // Vamos melhorar a função updateSubnetRecursively usada nessa parte

                // Localize o trecho dentro da função handleElementClick que lida com a criação de arcos:
                // (Geralmente dentro do bloco if (selectedObject === "arc"))

                // Substitua apenas a função updateSubnetRecursively por esta versão melhorada:

                const updateSubnetRecursively = (net, targetId, path = []) => {
                  // Evitar loops infinitos
                  if (path.includes(targetId)) {
                    console.error("Loop detectado ao procurar subnet:", path);
                    return false;
                  }

                  // Verificações de segurança
                  if (!net || !net.lugares) {
                    console.error(
                      "Rede ou lista de lugares indefinida para ID:",
                      targetId
                    );
                    return false;
                  }

                  // Procurar o lugar com a subnet diretamente neste nível
                  const placeIndex = net.lugares.findIndex(
                    (l) => l.id === targetId
                  );
                  if (placeIndex >= 0) {
                    // Encontrou o lugar, verificar se ele tem subnet
                    if (!net.lugares[placeIndex].subnet) {
                      net.lugares[placeIndex].subnet = {
                        lugares: [],
                        transicoes: [],
                        arcos: [],
                      };
                    }

                    // Garantir que arcos existe
                    if (!net.lugares[placeIndex].subnet.arcos) {
                      net.lugares[placeIndex].subnet.arcos = [];
                    }

                    // Adicionar o novo arco à subnet
                    net.lugares[placeIndex].subnet.arcos.push(newArc);
                    return true;
                  }

                  // Procurar recursivamente em cada lugar com subnet
                  for (let i = 0; i < net.lugares.length; i++) {
                    const lugar = net.lugares[i];
                    if (lugar && lugar.subnet) {
                      // Adicionar o ID atual ao caminho
                      const newPath = [...path, lugar.id];

                      // Chamada recursiva
                      const found = updateSubnetRecursively(
                        lugar.subnet,
                        targetId,
                        newPath
                      );
                      if (found) return true;
                    }
                  }

                  return false;
                };

                // O resto do código de criação de arcos permanece o mesmo

                updateSubnetRecursively(updatedNet, currentNetId);
                return updatedNet;
              });
            } else {
              setPetriNet((prev) => ({
                ...prev,
                arcos: [...prev.arcos, newArc],
              }));
            }
            if (currentNetId) {
              const subnet = findNestedSubnet(petriNet, currentNetId);
              if (subnet) {
                checkInterfaceWeightLimits(subnet);
              }
            }

            // Update interface connections if needed
            updateSubnetInterfaces(newArc);
          }

          setSourceElement(null);
          setSelectedObject(null);
        }
      }
    };

    paperRef.current.on("blank:pointerdown", handleClick);
    paperRef.current.on("element:pointerdown", handleElementClick);

    return () => {
      paperRef.current.off("blank:pointerdown", handleClick);
      paperRef.current.off("element:pointerdown", handleElementClick);
    };
  }, [selectedObject, sourceElement, selectedAgente]);
  useEffect(() => {
    if (!resizingAgent) return;

    const handleMouseMove = (evt) => {
      // Encontrar o elemento do agente
      const agentElement = graphRef.current.getElements().find(
        el => el.get('type') === 'agent' && el.get('agentId') === resizingAgent
      );

      if (!agentElement) return;

      // Calcular coordenadas do mouse no sistema de coordenadas do papel
      const paperRect = paperRef.current.el.getBoundingClientRect();
      const scale = paperRef.current.scale().sx;
      const translation = paperRef.current.translate();
      const mouseX = (evt.clientX - paperRect.left - translation.tx) / scale;
      const mouseY = (evt.clientY - paperRect.top - translation.ty) / scale;

      // Obter estado atual do elemento
      const originalPos = agentElement.position();
      const originalSize = agentElement.size();

      // Tamanho mínimo
      const minWidth = 100;
      const minHeight = 100;

      // Variáveis para os novos valores
      let newX, newY, newWidth, newHeight;

      // ABORDAGEM COMPLETAMENTE NOVA: Forçar a recriação do elemento
      // em vez de tentar modificar o existente

      // Calcular os novos valores com base na direção de redimensionamento
      switch (resizeDirection) {
        case 'left':
          // Limitar ao tamanho mínimo
          const maxLeftX = originalPos.x + originalSize.width - minWidth;
          newX = Math.min(mouseX, maxLeftX);
          newWidth = originalPos.x + originalSize.width - newX;
          newY = originalPos.y;
          newHeight = originalSize.height;
          break;

        case 'right':
          newX = originalPos.x;
          newWidth = Math.max(minWidth, mouseX - originalPos.x);
          newY = originalPos.y;
          newHeight = originalSize.height;
          break;

        case 'top':
          newX = originalPos.x;
          newWidth = originalSize.width;
          // Limitar ao tamanho mínimo
          const maxTopY = originalPos.y + originalSize.height - minHeight;
          newY = Math.min(mouseY, maxTopY);
          newHeight = originalPos.y + originalSize.height - newY;
          break;

        case 'bottom':
          newX = originalPos.x;
          newWidth = originalSize.width;
          newY = originalPos.y;
          newHeight = Math.max(minHeight, mouseY - originalPos.y);
          break;
      }

      // Remover o elemento atual
      agentElement.remove();

      // Criar um novo elemento com as dimensões calculadas
      const agent = new joint.shapes.basic.Rect({
        id: `agent_${resizingAgent}`,
        position: { x: newX, y: newY },
        size: { width: newWidth, height: newHeight },
        attrs: {
          rect: {
            fill: 'rgba(230, 242, 255, 0.4)',
            stroke: '#A3C7E3',
            'stroke-width': 6,
            'vector-effect': 'non-scaling-stroke',
            rx: 10,
            ry: 10
          },
          text: {
            text: (() => {
              // Buscar o nome do agente no contexto correto
              if (currentNetId) {
                // Se estamos em uma subnet, buscar lá
                const subnet = findNestedSubnet(petriNet, currentNetId);
                return subnet?.agentes?.find(a => a.id === resizingAgent)?.nome || 'Agente';
              } else {
                // Se estamos na rede principal
                return petriNet.agentes?.find(a => a.id === resizingAgent)?.nome || 'Agente';
              }
            })(),
            'font-size': 14,
            'font-weight': 'bold',
            'ref-x': 0.5,           // Centralizar horizontalmente (0.5 = 50% da largura)
            'ref-y': 15,            // Manter na parte superior
            'text-anchor': 'middle',
            fill: '#666'
          }
        },
        markup: `
          <g class="rotatable">
            <g class="scalable">
              <rect/>
            </g>
            <text/>
          </g>
        `,
      });

      // Configurar metadados
      agent.set('type', 'agent');
      agent.set('agentId', resizingAgent);
      agent.set('z', -10);

      // Adicionar ao gráfico
      graphRef.current.addCell(agent);

      // Atualizar o modelo de dados
      // Atualizar o modelo de dados - VERSÃO CORRIGIDA
      setPetriNet(prev => {
        // Fazer uma cópia profunda para evitar modificar o estado diretamente
        const updatedNet = JSON.parse(JSON.stringify(prev));

        if (currentNetId) {
          // Estamos em uma subnet
          const currentSubnet = findNestedSubnet(updatedNet, currentNetId);
          if (currentSubnet && currentSubnet.agentes) {
            // Encontrar o agente na subnet atual
            const agentIndex = currentSubnet.agentes.findIndex(a => a.id === resizingAgent);
            if (agentIndex >= 0) {
              // Atualizar as propriedades do agente na subnet
              currentSubnet.agentes[agentIndex] = {
                ...currentSubnet.agentes[agentIndex],
                coordenadas: { x: newX, y: newY },
                width: newWidth,
                height: newHeight
              };
              console.log(`Agente ${resizingAgent} atualizado na subnet ${currentNetId}:`,
                `coords=(${newX},${newY}), tamanho=${newWidth}x${newHeight}`);
            }
          }
        } else {
          // Estamos na rede principal
          const agentIndex = updatedNet.agentes.findIndex(a => a.id === resizingAgent);
          if (agentIndex >= 0) {
            updatedNet.agentes[agentIndex] = {
              ...updatedNet.agentes[agentIndex],
              coordenadas: { x: newX, y: newY },
              width: newWidth,
              height: newHeight
            };
            console.log(`Agente ${resizingAgent} atualizado na rede principal:`,
              `coords=(${newX},${newY}), tamanho=${newWidth}x${newHeight}`);
            console.log(updatedNet)
          }
        }

        return updatedNet;
      });
    };
    const getInitialAgentState = (agentId) => {
      if (currentNetId) {
        const subnet = findNestedSubnet(petriNet, currentNetId);
        return subnet?.agentes?.find(a => a.id === agentId);
      } else {
        return petriNet.agentes?.find(a => a.id === agentId);
      }
    };

    const handleMouseUp = () => {
      // Encontrar o elemento do agente
      const agentElement = graphRef.current.getElements().find(
        el => el.get('type') === 'agent' && el.get('agentId') === resizingAgent
      );

      if (agentElement) {
        // Obter posição e tamanho final
        const finalPos = agentElement.position();
        const finalSize = agentElement.size();

        // Atualização ÚNICA do estado ao final do redimensionamento
        setPetriNet(prev => {
          const updatedNet = JSON.parse(JSON.stringify(prev));

          if (currentNetId) {
            // Subnet
            const subnet = findNestedSubnet(updatedNet, currentNetId);
            if (subnet && subnet.agentes) {
              const agentIndex = subnet.agentes.findIndex(a => a.id === resizingAgent);
              if (agentIndex >= 0) {
                // Importante: manter as coordenadas originais se não mudaram
                subnet.agentes[agentIndex] = {
                  ...subnet.agentes[agentIndex],
                  width: finalSize.width,
                  height: finalSize.height,
                  // Apenas atualize coordenadas se houve mudança na posição
                  coordenadas: finalPos
                };
              }
            }
          } else {
            // Rede principal
            if (updatedNet.agentes) {
              const agentIndex = updatedNet.agentes.findIndex(a => a.id === resizingAgent);
              if (agentIndex >= 0) {
                updatedNet.agentes[agentIndex] = {
                  ...updatedNet.agentes[agentIndex],
                  width: finalSize.width,
                  height: finalSize.height,
                  // Apenas atualize coordenadas se houve mudança na posição
                  coordenadas: finalPos
                };
              }
            }
          }

          return updatedNet;
        });

        // Registrar ação para undo/redo se necessário
        const initialAgent = getInitialAgentState(resizingAgent);
        if (initialAgent) {
          recordAction("resize_agent", {
            id: resizingAgent,
            initial: initialAgent,
            final: {
              coordenadas: finalPos,
              width: finalSize.width,
              height: finalSize.height
            },
            inSubnet: !!currentNetId,
            subnetId: currentNetId
          });
        }

        // Reabilitar interatividade
        agentElement.set('interactive', true);
      }

      setResizingAgent(null);
      setResizeDirection(null);
      document.body.style.cursor = 'default';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    setTimeout(() => {
      verificarPlacesDentroDoAgente(resizingAgent);
    }, 50);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [resizingAgent, resizeDirection]);
  useEffect(() => {
    if (!paperRef.current) return;


    const handleElementMouseMove = (elementView, evt) => {
      console.log('Evento recebido:', evt);
      // Verificar se evt tem as propriedades necessárias
      if (!evt || typeof evt.clientX === 'undefined' || typeof evt.clientY === 'undefined') {
        console.error('Evento de mouse inválido:', evt);
        return;
      }

      const element = elementView.model;
      if (element.get('type') === 'agent' && !resizingAgent) {
        checkResizeArea(element, evt);
      }
    };

    const handleElementMouseOut = () => {
      if (!resizingAgent) {
        document.body.style.cursor = 'default';
      }
    };

    paperRef.current.on('element:mousemove', handleElementMouseMove);
    paperRef.current.on('element:mouseout', handleElementMouseOut);

    return () => {
      if (paperRef.current) {
        paperRef.current.off('element:mousemove', handleElementMouseMove);
        paperRef.current.off('element:mouseout', handleElementMouseOut);
      }
    };
  }, [resizingAgent, checkResizeArea]);

  // Adicionar esta função para atualizar coordenadas após movimentação
  const handleAgentMoved = (elementView) => {
    const element = elementView.model;

    // Verificar se é um agente
    if (element.get('type') !== 'agent') return;

    const agentId = element.get('agentId');
    const position = element.position();

    // Atualizar coordenadas no modelo de dados
    setPetriNet(prev => {
      const updatedNet = JSON.parse(JSON.stringify(prev));

      if (currentNetId) {
        // Estamos em uma subnet
        const currentSubnet = findNestedSubnet(updatedNet, currentNetId);
        if (currentSubnet && currentSubnet.agentes) {
          const agentIndex = currentSubnet.agentes.findIndex(a => a.id === agentId);
          if (agentIndex >= 0) {
            // Manter dimensões originais, atualizar apenas coordenadas
            currentSubnet.agentes[agentIndex] = {
              ...currentSubnet.agentes[agentIndex],
              coordenadas: { x: position.x, y: position.y }
            };
            console.log(`Agente ${agentId} movido na subnet:`, position);
          }
        }
      } else {
        // Estamos na rede principal
        const agentIndex = updatedNet.agentes.findIndex(a => a.id === agentId);
        if (agentIndex >= 0) {
          updatedNet.agentes[agentIndex] = {
            ...updatedNet.agentes[agentIndex],
            coordenadas: { x: position.x, y: position.y }
          };
          console.log(`Agente ${agentId} movido na rede principal:`, position);
        }
      }

      return updatedNet;
    });
    setTimeout(() => {
      verificarPlacesDentroDoAgente(agentId);
    }, 0);
  };

  // Registrar o evento no paper
  // Registrar o evento no paper
  useEffect(() => {
    if (!paperRef.current) return;

    // Adicionar handler para final de movimento de elementos
    paperRef.current.on('element:pointerup', (elementView, evt) => {
      handleAgentMoved(elementView);
    });

    return () => {
      if (paperRef.current) {
        paperRef.current.off('element:pointerup', handleAgentMoved);
      }
    };
  }, []); // Array de dependências vazio para registrar apenas uma vez
  /**
   * Handle element selection, editing, and context menu
   */
  useEffect(() => {
    if (!paperRef.current) return;

    const handleElementClick = (elementView, evt) => {
      // If in creation mode, don't process the click
      if (selectedObject) return;

      const element = elementView.model;

      // If Ctrl is pressed, handle multi-selection
      if (evt && (evt.ctrlKey || evt.metaKey)) {
        const elementId = element.id;
        const elementType = element.attributes.type;

        setSelectedElements((prev) => {
          const newSelection = new Set(prev);
          if (newSelection.has(elementId)) {
            // Remove from selection
            newSelection.delete(elementId);
            if (elementType === "basic.Circle") {
              element.attr("circle/stroke", "black");
              element.attr("circle/stroke-width", 1);
            } else if (elementType === "basic.Rect") {
              element.attr({
                ".body": {
                  fill: "gray",
                  stroke: "black",
                  "stroke-width": 1,
                },
              });
            } else if (elementType === "standard.Link") {
              element.attr("line/stroke", "black");
              element.attr("line/stroke-width", 2);
            }
          } else {
            // Add to selection
            newSelection.add(elementId);
            if (elementType === "basic.Circle") {
              element.attr("circle/stroke", "red");
              element.attr("circle/stroke-width", 4);
            } else if (elementType === "basic.Rect") {
              element.attr({
                ".body": {
                  fill: "red",
                  stroke: "red",
                  "stroke-width": 4,
                },
              });
            } else if (elementType === "standard.Link") {
              element.attr("line/stroke", "red");
              element.attr("line/stroke-width", 4);
            }
          }
          return newSelection;
        });

        return;
      }

      // If no Ctrl is pressed, clear previous selection
      if (selectedElements.size > 0) {
        selectedElements.forEach((id) => {
          const el = graphRef.current.getCell(id);
          if (el) {
            const elType = el.attributes.type;
            if (elType === "basic.Circle") {
              el.attr("circle/stroke", "black");
              el.attr("circle/stroke-width", 1);
            } else if (elType === "basic.Rect") {
              el.attr({
                ".body": {
                  fill: "gray",
                  stroke: "black",
                  "stroke-width": 1,
                },
              });
            } else if (elType === "standard.Link") {
              el.attr("line/stroke", "black");
              el.attr("line/stroke-width", 2);
            }
          }
        });
        setSelectedElements(new Set());
      }

      // If right-click, show context menu
      // If right-click, show context menu
      // Substitua este bloco exato no seu código - provavelmente dentro de um useEffect que define
      // event handlers para o paper
      // Localize o código que trata de clique direito e usa evt.button === 2

      // Se for um clique direito, mostrar o menu de contexto
      if (evt && evt.button === 2) {
        evt.preventDefault();
        if (element.get('type') === 'agent') {
          const agentId = element.get('agentId');

          // Obter os dados do agente
          let agentData;
          if (currentNetId) {
            // Estamos em uma subnet
            const currentSubnet = findNestedSubnet(petriNet, currentNetId);
            if (currentSubnet && currentSubnet.agentes) {
              agentData = currentSubnet.agentes.find(a => a.id === agentId);
            }
          } else {
            // Estamos na rede principal
            agentData = petriNet.agentes.find(a => a.id === agentId);
          }

          if (agentData) {
            setContextMenu({
              visible: true,
              x: evt.clientX,
              y: evt.clientY,
              element: agentData,
              type: "agent",
            });
          }

          return;
        }
        const type =
          element.attributes.type === "basic.Circle"
            ? "place"
            : element.attributes.type === "basic.Rect"
              ? "transition"
              : "arc";

        // Obter os dados do elemento clicado de acordo com o contexto atual
        let elementData;

        console.log(
          "Clique direito em elemento:",
          type,
          element.id,
          "na rede:",
          currentNetId
        );

        if (type === "arc") {
          // Arcos são mais simples porque eles são locais à sub-rede atual
          if (currentNetId) {
            // Encontrar a sub-rede atual na hierarquia
            const currentSubnet = findNestedSubnet(petriNet, currentNetId);
            if (currentSubnet && currentSubnet.arcos) {
              elementData = currentSubnet.arcos.find(
                (a) =>
                  a.origem === element.attributes.source.id &&
                  a.destino === element.attributes.target.id
              );
            }
          } else {
            // Na rede principal
            elementData = petriNet.arcos.find(
              (a) =>
                a.origem === element.attributes.source.id &&
                a.destino === element.attributes.target.id
            );
          }
        } else {
          // Para lugares e transições
          if (currentNetId) {
            // Estamos em uma sub-rede, precisamos encontrar a sub-rede atual na hierarquia
            const currentSubnet = findNestedSubnet(petriNet, currentNetId);
            if (currentSubnet) {
              if (type === "place") {
                elementData =
                  currentSubnet.lugares &&
                  currentSubnet.lugares.find((l) => l.id === element.id);
              } else {
                // transition
                elementData =
                  currentSubnet.transicoes &&
                  currentSubnet.transicoes.find((t) => t.id === element.id);
              }
            }
          } else {
            // Estamos na rede principal
            if (type === "place") {
              elementData = petriNet.lugares.find((l) => l.id === element.id);
            } else {
              // transition
              elementData = petriNet.transicoes.find(
                (t) => t.id === element.id
              );
            }
          }
        }

        console.log("Elemento encontrado:", elementData);
        if (elementData && type === "transition") {
          // Se o nome tem quebras de linha, substituí-las por espaços
          if (elementData.nome && elementData.nome.includes("\n")) {
            elementData = {
              ...elementData,
              nome: elementData.nome.replace(/\n/g, " "),
            };
            console.log("Nome corrigido:", elementData.nome);
          }

          // Se mesmo assim o nome estiver errado ou vazio, tentar obter do elemento visual
          if (!elementData.nome || elementData.nome === "") {
            const transitionElement = graphRef.current.getCell(element.id);
            if (transitionElement) {
              const visualName = transitionElement.attr(".label/text");
              if (visualName) {
                elementData = {
                  ...elementData,
                  nome: visualName.replace(/\n/g, " "),
                };
                console.log("Nome recuperado do visual:", elementData.nome);
              }
            }
          }
        }

        // Apenas mostrar o menu se encontramos dados para o elemento
        if (elementData) {
          setContextMenu({
            visible: true,
            x: evt.clientX,
            y: evt.clientY,
            element: elementData,
            type: type,
          });
        } else {
          console.warn(
            "Não foi possível encontrar dados para o elemento:",
            element.id
          );
        }

        return;
      }
    };

    // Handler to click outside and close menu
    const handleDocumentClick = (evt) => {
      if (contextMenu.visible) {
        setContextMenu((prev) => ({ ...prev, visible: false }));
      }
    };

    // Event listeners for normal click and context
    paperRef.current.on("element:pointerclick", handleElementClick);
    paperRef.current.on("link:pointerclick", handleElementClick);
    paperRef.current.on("element:contextmenu", handleElementClick);
    paperRef.current.on("link:contextmenu", handleElementClick);
    document.addEventListener("click", handleDocumentClick);

    return () => {
      if (paperRef.current) {
        paperRef.current.off("element:pointerclick", handleElementClick);
        paperRef.current.off("link:pointerclick", handleElementClick);
        paperRef.current.off("element:contextmenu", handleElementClick);
        paperRef.current.off("link:contextmenu", handleElementClick);
      }
      document.removeEventListener("click", handleDocumentClick);
    };
  }, [selectedObject, petriNet, contextMenu.visible, selectedElements]);

  /**
   * Update positions in the petriNet state when elements are moved
   */
  /**
   * Handle element dragging for single or multiple elements
   */
  useEffect(() => {
    if (!paperRef.current) return;

    // Variável para controle do drag em grupo
    let dragStartPosition = null;

    // Handlers para movimento em grupo
    const handleElementDrag = (elementView, evt, x, y) => {
      const element = elementView.model;
      if (selectedElements.has(element.id)) {
        if (!dragStartPosition) {
          dragStartPosition = { x, y };
          return;
        }

        const dx = x - dragStartPosition.x;
        const dy = y - dragStartPosition.y;

        selectedElements.forEach((id) => {
          const el = graphRef.current.getCell(id);
          if (el && el.id !== element.id) {
            const currentPosition = el.position();
            el.position(currentPosition.x + dx, currentPosition.y + dy);
          }
        });

        dragStartPosition = { x, y };
      }
    };

    const handleDragEnd = () => {
      dragStartPosition = null;
    };
    const handleElementDragStart = (elementView, evt) => {
      // Se for um Ctrl+click, não tratar como arrastar
      if (evt && evt.ctrlKey) {
        return;
      }

      const element = elementView.model;

      // Verificar se é um agente
      const isAgent = element.get('type') === 'agent';

      const initialState = {
        positions: new Map(),
        elements: [],
      };

      // Se faz parte de uma seleção em grupo
      if (selectedElements.has(element.id) && selectedElements.size > 1) {
        selectedElements.forEach((id) => {
          const el = graphRef.current.getCell(id);
          if (el) {
            // Determinar o tipo
            let type;
            if (el.get('type') === 'agent') {
              type = "agent";
            } else {
              type = el.attributes.type === "basic.Circle" ? "place" : "transition";
            }

            const pos = el.position();
            initialState.positions.set(id, { x: pos.x, y: pos.y });

            let elementData;
            if (type === "agent") {
              // Buscar dados do agente no contexto correto
              elementData = currentNetId
                ? findNestedSubnet(petriNet, currentNetId).agentes?.find(a => a.id === el.get('agentId'))
                : petriNet.agentes?.find(a => a.id === el.get('agentId'));
            } else {
              // Buscar dados de lugar ou transição no contexto correto
              elementData = type === "place"
                ? (currentNetId
                  ? findNestedSubnet(petriNet, currentNetId).lugares?.find(l => l.id === id)
                  : petriNet.lugares?.find(l => l.id === id))
                : (currentNetId
                  ? findNestedSubnet(petriNet, currentNetId).transicoes?.find(t => t.id === id)
                  : petriNet.transicoes?.find(t => t.id === id));
            }

            if (elementData) {
              initialState.elements.push({
                id: type === "agent" ? el.get('agentId') : id,
                type,
                data: { ...elementData, coordenadas: { x: pos.x, y: pos.y } },
              });
            }
          }
        });
      }
      // Se for um elemento individual
      else {
        const pos = element.position();

        let type, elementId;
        if (isAgent) {
          type = "agent";
          elementId = element.get('agentId');

          // Buscar dados do agente no contexto correto
          let agentData = currentNetId
            ? findNestedSubnet(petriNet, currentNetId).agentes?.find(a => a.id === elementId)
            : petriNet.agentes?.find(a => a.id === elementId);

          if (agentData) {
            initialState.positions.set(elementId, { x: pos.x, y: pos.y });
            initialState.elements.push({
              id: elementId,
              type,
              data: {
                ...agentData,
                coordenadas: { x: pos.x, y: pos.y },
              },
            });
          }
        } else {
          type = element.attributes.type === "basic.Circle" ? "place" : "transition";
          elementId = element.id;

          // Buscar dados do lugar/transição no contexto correto
          let elementData = currentNetId
            ? (type === "place"
              ? findNestedSubnet(petriNet, currentNetId).lugares?.find(l => l.id === elementId)
              : findNestedSubnet(petriNet, currentNetId).transicoes?.find(t => t.id === elementId))
            : (type === "place"
              ? petriNet.lugares?.find(l => l.id === elementId)
              : petriNet.transicoes?.find(t => t.id === elementId));

          if (elementData) {
            initialState.positions.set(elementId, { x: pos.x, y: pos.y });
            initialState.elements.push({
              id: elementId,
              type,
              data: {
                ...elementData,
                coordenadas: { x: pos.x, y: pos.y },
              },
            });
          }
        }
      }

      setDragStartPositions(initialState);
    };

    const handleElementDragEnd = (elementView) => {
      if (!dragStartPositions) return;

      const element = elementView.model;
      const isAgent = element.get('type') === 'agent';

      const finalState = {
        positions: new Map(),
        elements: [],
      };

      // Se faz parte de uma seleção em grupo
      if (selectedElements.has(element.id) && selectedElements.size > 1) {
        selectedElements.forEach((id) => {
          const el = graphRef.current.getCell(id);
          if (el) {
            // Determinar o tipo do elemento
            let type, elementId;
            if (el.get('type') === 'agent') {
              type = "agent";
              elementId = el.get('agentId');
            } else {
              type = el.attributes.type === "basic.Circle" ? "place" : "transition";
              elementId = el.id;
            }

            const pos = el.position();
            finalState.positions.set(elementId, { x: pos.x, y: pos.y });

            // Obter dados do elemento no contexto correto
            let elementData;
            if (currentNetId) {
              // Estamos em uma subnet
              const subnet = findNestedSubnet(petriNet, currentNetId);
              if (subnet) {
                if (type === "place") {
                  elementData = subnet.lugares?.find(l => l.id === elementId);
                } else if (type === "transition") {
                  elementData = subnet.transicoes?.find(t => t.id === elementId);
                } else if (type === "agent") {
                  elementData = subnet.agentes?.find(a => a.id === elementId);
                }
              }
            } else {
              // Estamos na rede principal
              if (type === "place") {
                elementData = petriNet.lugares?.find(l => l.id === elementId);
              } else if (type === "transition") {
                elementData = petriNet.transicoes?.find(t => t.id === elementId);
              } else if (type === "agent") {
                elementData = petriNet.agentes?.find(a => a.id === elementId);
              }
            }

            if (elementData) {
              finalState.elements.push({
                id: elementId,
                type,
                data: {
                  ...elementData,
                  coordenadas: { x: pos.x, y: pos.y },
                  // Para agentes, incluir também largura e altura atualizadas
                  ...(type === "agent" ? {
                    width: el.size().width,
                    height: el.size().height
                  } : {})
                },
              });
            }
          }
        });
      }
      // Se for um elemento individual
      else {
        const pos = element.position();

        let type, elementId;
        if (isAgent) {
          type = "agent";
          elementId = element.get('agentId');

          // Buscar dados do agente no contexto correto
          let agentData;
          if (currentNetId) {
            const subnet = findNestedSubnet(petriNet, currentNetId);
            agentData = subnet?.agentes?.find(a => a.id === elementId);
          } else {
            agentData = petriNet.agentes?.find(a => a.id === elementId);
          }

          if (agentData) {
            finalState.positions.set(elementId, { x: pos.x, y: pos.y });
            finalState.elements.push({
              id: elementId,
              type,
              data: {
                ...agentData,
                coordenadas: { x: pos.x, y: pos.y },
                width: element.size().width,
                height: element.size().height
              },
            });
          }
        } else {
          type = element.attributes.type === "basic.Circle" ? "place" : "transition";
          elementId = element.id;

          // Buscar dados do lugar/transição no contexto correto
          let elementData;
          if (currentNetId) {
            const subnet = findNestedSubnet(petriNet, currentNetId);
            if (type === "place") {
              elementData = subnet?.lugares?.find(l => l.id === elementId);
            } else {
              elementData = subnet?.transicoes?.find(t => t.id === elementId);
            }
          } else {
            if (type === "place") {
              elementData = petriNet.lugares?.find(l => l.id === elementId);
            } else {
              elementData = petriNet.transicoes?.find(t => t.id === elementId);
            }
          }

          if (elementData) {
            finalState.positions.set(elementId, { x: pos.x, y: pos.y });
            finalState.elements.push({
              id: elementId,
              type,
              data: {
                ...elementData,
                coordenadas: { x: pos.x, y: pos.y },
              },
            });
          }
        }
      }

      // Verificar se houve realmente movimento
      let hasMoved = false;
      finalState.elements.forEach((finalEl) => {
        const initialEl = dragStartPositions.elements.find(
          (e) => e.id === finalEl.id && e.type === finalEl.type
        );

        if (initialEl) {
          // Para elementos normais, verificar apenas as coordenadas
          if (
            initialEl.data.coordenadas.x !== finalEl.data.coordenadas.x ||
            initialEl.data.coordenadas.y !== finalEl.data.coordenadas.y
          ) {
            hasMoved = true;
          }
          // Para agentes, verificar também largura e altura
          else if (finalEl.type === "agent" && (
            initialEl.data.width !== finalEl.data.width ||
            initialEl.data.height !== finalEl.data.height
          )) {
            hasMoved = true;
          }
        }
      });

      if (hasMoved) {
        // Adicionar informações de contexto para undo/redo
        const actionData = {
          initial: dragStartPositions.elements,
          final: finalState.elements,
          inSubnet: !!currentNetId,
          subnetId: currentNetId
        };

        // Registrar ação para undo/redo
        recordAction("move", actionData);

        // Atualizar o modelo de dados com as novas posições
        setPetriNet((prev) => {
          const updatedNet = JSON.parse(JSON.stringify(prev));

          if (currentNetId) {
            // Estamos em uma subnet
            const updateSubnetRecursively = (net, targetId, path = []) => {
              // Evitar loops infinitos
              if (path.includes(targetId)) return net;

              // Verificar se encontramos a subnet alvo neste nível
              const placeIndex = net.lugares.findIndex(l => l.id === targetId);
              if (placeIndex >= 0) {
                // Encontramos a subnet alvo
                if (!net.lugares[placeIndex].subnet) return net;

                const subnet = net.lugares[placeIndex].subnet;

                // Atualizar lugares na subnet
                if (subnet.lugares) {
                  subnet.lugares = subnet.lugares.map((l) => {
                    const finalElement = finalState.elements.find(
                      (e) => e.type === "place" && e.id === l.id
                    );
                    return finalElement
                      ? { ...l, coordenadas: finalElement.data.coordenadas }
                      : l;
                  });
                }

                // Atualizar transições na subnet
                if (subnet.transicoes) {
                  subnet.transicoes = subnet.transicoes.map((t) => {
                    const finalElement = finalState.elements.find(
                      (e) => e.type === "transition" && e.id === t.id
                    );
                    return finalElement
                      ? { ...t, coordenadas: finalElement.data.coordenadas }
                      : t;
                  });
                }

                // Atualizar agentes na subnet
                if (subnet.agentes) {
                  subnet.agentes = subnet.agentes.map((a) => {
                    const finalElement = finalState.elements.find(
                      (e) => e.type === "agent" && e.id === a.id
                    );
                    return finalElement
                      ? {
                        ...a,
                        coordenadas: finalElement.data.coordenadas,
                        width: finalElement.data.width,
                        height: finalElement.data.height
                      }
                      : a;
                  });
                }

                return net;
              }

              // Buscar recursivamente em todas as subnets neste nível
              if (net.lugares) {
                net.lugares = net.lugares.map(lugar => {
                  if (lugar.subnet) {
                    const newPath = [...path, lugar.id];
                    const updatedSubnet = updateSubnetRecursively(
                      lugar.subnet,
                      targetId,
                      newPath
                    );
                    return { ...lugar, subnet: updatedSubnet };
                  }
                  return lugar;
                });
              }

              return net;
            };

            // Atualizar a subnet recursivamente
            return updateSubnetRecursively(updatedNet, currentNetId);
          } else {
            // Estamos na rede principal
            // Atualizar lugares
            updatedNet.lugares = updatedNet.lugares.map((l) => {
              const finalElement = finalState.elements.find(
                (e) => e.type === "place" && e.id === l.id
              );
              return finalElement
                ? { ...l, coordenadas: finalElement.data.coordenadas }
                : l;
            });

            // Atualizar transições
            updatedNet.transicoes = updatedNet.transicoes.map((t) => {
              const finalElement = finalState.elements.find(
                (e) => e.type === "transition" && e.id === t.id
              );
              return finalElement
                ? { ...t, coordenadas: finalElement.data.coordenadas }
                : t;
            });

            // Atualizar agentes
            if (updatedNet.agentes) {
              updatedNet.agentes = updatedNet.agentes.map((a) => {
                const finalElement = finalState.elements.find(
                  (e) => e.type === "agent" && e.id === a.id
                );
                return finalElement
                  ? {
                    ...a,
                    coordenadas: finalElement.data.coordenadas,
                    width: finalElement.data.width,
                    height: finalElement.data.height
                  }
                  : a;
              });
            }

            return updatedNet;
          }
        });
      }
      // Adicione após o final do handleElementDragEnd
      if (element.attributes.type === "basic.Circle") {
        verificarPlaceDentroDeAgente(element.id);
      }
      setDragStartPositions(null);

    };

    // Registra todos os event handlers
    paperRef.current.on("element:pointerdown", handleElementDragStart);
    paperRef.current.on("element:pointermove", handleElementDrag);
    paperRef.current.on("element:pointerup", handleElementDragEnd);
    paperRef.current.on("element:pointerup", handleDragEnd);
    // No useEffect que lida com o final do arrasto de elementos

    // Limpa todos os event handlers
    return () => {
      if (paperRef.current) {
        paperRef.current.off("element:pointerdown", handleElementDragStart);
        paperRef.current.off("element:pointermove", handleElementDrag);
        paperRef.current.off("element:pointerup", handleElementDragEnd);
        paperRef.current.off("element:pointerup", handleDragEnd);
      }
    };
  }, [selectedElements, dragStartPositions, petriNet]);
  /**
   * Handle keyboard shortcuts
   */
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Undo/Redo keyboard shortcuts
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
        if (e.shiftKey) {
          handleRedo(); // Ctrl + Shift + Z for redo
        } else {
          handleUndo(); // Ctrl + Z for undo
        }
        e.preventDefault();
      }

      // Delete key handler
      if (e.key === "Delete" && selectedElements.size > 0) {
        deleteSelectedElements();
      }

      // Copy/Cut/Paste shortcuts
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case "c":
            e.preventDefault();
            if (selectedElements.size > 0) {
              handleCopy(false);
            }
            break;
          case "x":
            e.preventDefault();
            if (selectedElements.size > 0) {
              handleCopy(true);
            }
            break;
          case "v":
            e.preventDefault();
            if (clipboard) {
              handlePaste();
            }
            break;
        }
      }
    };

    // Track mouse position for paste operation
    const trackMousePosition = (e) => {
      window.lastMouseX = e.clientX;
      window.lastMouseY = e.clientY;
    };

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("mousemove", trackMousePosition);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("mousemove", trackMousePosition);
    };
  }, [selectedElements, clipboard, undoStack, redoStack]);

  // =========== RENDER COMPONENT ===========

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
      }}
    >
      <div>
        <div style={{ textAlign: "center", marginBottom: "10px" }}>
          {/* LangNet integration: generate via LLM + persist to projects.project_data */}
          <button
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              backgroundColor: "#1976d2",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
            onClick={() => setGenerateModalOpen(true)}
            disabled={isLoadingNet}
            title="Gera a Rede de Petri via agente LLM a partir dos YAMLs e da sequência de tasks"
          >
            {isLoadingNet ? "⏳ Processando..." : "🔗 Gerar Rede"}
          </button>
          <button
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              backgroundColor: "#2e7d32",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
            onClick={handleSaveToBackend}
            disabled={isLoadingNet}
            title="Persiste a rede atual em projects.project_data"
          >
            💾 Salvar no Banco
          </button>

          {/* Element creation controls */}
          <button
            style={{ marginRight: "10px", padding: "5px 10px" }}
            onClick={() => setSelectedObject("place")}
          >
            Adicionar Lugar
          </button>
          <button
            style={{ marginRight: "10px", padding: "5px 10px" }}
            onClick={() => setSelectedObject("transition")}
          >
            Adicionar Transição
          </button>
          <button
            style={{ marginRight: "10px", padding: "5px 10px" }}
            onClick={() => {
              setSelectedObject("arc");
              setSourceElement(null);
            }}
          >
            Adicionar Arco
          </button>
          <button
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              backgroundColor: selectedObject === "agent" ? "#ccc" : "white",
            }}
            onClick={() => setSelectedObject("agent")}
          >
            Adicionar Agente
          </button>

          <button
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              backgroundColor: selectedObject === "rotate" ? "#ccc" : "white",
            }}
            onClick={() => setSelectedObject("rotate")}
          >
            Rotacionar Transição
          </button>

          {/* View controls */}
          <button
            style={{ padding: "5px 10px", marginRight: "10px" }}
            onClick={() => setJsonModalOpen(true)}
          >
            Visualizar JSON
          </button>
          <button
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              backgroundColor: simulationPanelOpen ? "#4CAF50" : "#2196F3",
              color: "white",
              border: "none",
              borderRadius: "4px"
            }}
            onClick={handleStartSimulation}
          >
            {simulationPanelOpen ? "Simulando..." : "Simular"}
          </button>
          <button
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              backgroundColor: executionPanelOpen ? "#7b1fa2" : "#1976d2",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
            onClick={() => setExecutionPanelOpen((v) => !v)}
            title="Conecta no servidor agêntico gerado (websocket_server.py) e abre as 5 abas"
          >
            ▶ Execução Real
          </button>
          {(() => {
            const sel = getSelectedTask();
            return (
              <button
                style={{
                  marginRight: "10px",
                  padding: "5px 10px",
                  backgroundColor: sel ? "#ff5722" : "#cccccc",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: sel ? "pointer" : "not-allowed",
                }}
                onClick={handleDispatchSelectedTask}
                disabled={!sel}
                title={
                  sel
                    ? `Dispara execute_task '${sel.taskName}' no servidor agêntico`
                    : "Selecione um único place com nome de task para habilitar"
                }
              >
                🎯 Disparar {sel ? `'${sel.taskName.substring(0, 20)}${sel.taskName.length > 20 ? '…' : ''}'` : 'task'}
              </button>
            );
          })()}
          <button
            style={{
              marginRight: "10px",
              padding: "5px 10px",
              backgroundColor: "#FF9800",
              color: "white",
              border: "none",
              borderRadius: "4px"
            }}
            onClick={handlePrintDiagram}
          >
            🖨️ Imprimir
          </button>
          {currentNetId && (
            <button
              style={{
                marginRight: "10px",
                padding: "5px 10px",
                backgroundColor: "#4CAF50",
                color: "white",
              }}
              onClick={navigateToParent}
            >
              Nível Acima
            </button>
          )}
          {/*
          <span style={{ 
          marginLeft: '20px', 
          fontWeight: 'bold',
          padding: '5px 10px',
          backgroundColor: currentNetId ? '#f0f0f0' : 'transparent',
          borderRadius: '4px'
          }}>
          {currentNetId 
          ? `Sub-rede: ${petriNet.lugares.find(l => l.id === currentNetId)?.nome || currentNetId}` 
          : `Rede Principal: ${petriNet.nome}`}
          </span>
          */}
        </div>
        {/* Graph container */}
        <div
          id="paper-container"
          style={{
            border: "1px solid black",
            width: "100%",
            maxWidth: "100%",
            height: "780px",
            overflow: "auto",
          }}
        />
        {/* Modals */}
        <Modal
          isOpen={jsonModalOpen}
          onClose={() => setJsonModalOpen(false)}
          title="Estrutura da Rede de Petri"
        >
          <div
            style={{
              maxHeight: "400px",
              overflowY: "auto",
              padding: "10px",
            }}
          >
            <pre
              style={{
                whiteSpace: "pre-wrap",
                wordWrap: "break-word",
                backgroundColor: "#f5f5f5",
                padding: "10px",
                borderRadius: "5px",
                margin: 0,
              }}
            >
              {JSON.stringify(petriNet, null, 2)}
            </pre>
          </div>
        </Modal>
        <RenameModal
          isOpen={renameModalOpen}
          onClose={() => {
            setRenameModalOpen(false);
            setSaveAction(null);
          }}
          onSave={handleRename}
          currentName={petriNet.nome}
        />
        <EditModal
          isOpen={editModalOpen}
          onClose={() => setEditModalOpen(false)}
          type={editingType}
          element={editingElement}
          onSave={handleSave}
        />
        <EditAgentModal
          isOpen={editAgentModalOpen}
          onClose={() => setEditAgentModalOpen(false)}
          agent={editingAgent}
          onSave={handleSaveAgent}
        />
        <GeneratePetriNetModal
          isOpen={generateModalOpen}
          projectId={projectId || ""}
          onClose={() => setGenerateModalOpen(false)}
          onConfirm={handleGenerateConfirm}
        />
        <ExecutionPanel
          ref={executionPanelRef}
          isOpen={executionPanelOpen}
          autoconnectUrl={autoconnectUrl}
          onClose={() => setExecutionPanelOpen(false)}
          onRequestOpen={() => setExecutionPanelOpen(true)}
        />
        <SimulationPanel
          simulator={simulator}
          isOpen={simulationPanelOpen}
          onClose={() => setSimulationPanelOpen(false)}
          onTransitionFired={handleTransitionFired}
          onTransitionHighlight={handleTransitionHighlight}
        />
        {/* Context Menu */}
        
        {contextMenu.visible && (
          <ContextMenu
            x={contextMenu.x}
            y={contextMenu.y}
            element={contextMenu.element}
            type={contextMenu.type}
            onEdit={() => {
              console.log("Editando:", contextMenu.type, contextMenu.element);
              if (contextMenu.type === "agent") {
                // Editar agente
                setEditingAgent(contextMenu.element);
                setEditAgentModalOpen(true);
              } else {
                // Editar lugar, transição ou arco (código existente)
                setEditingType(contextMenu.type);
                setEditingElement(contextMenu.element);
                setEditModalOpen(true);
              }
            }}
            onDelete={() => {
              console.log("Excluindo:", contextMenu.type, contextMenu.element);

              // Excluir lugar, transição,agente ou arco (código existente)
              handleDelete(contextMenu.element, contextMenu.type);

            }}
            onExplode={() => {
              console.log("Explodindo:", contextMenu.type, contextMenu.element);
              if (contextMenu.type === "place") {
                handleExplodePetriNet(contextMenu.element);
              }
            }}
            onClose={() =>
              setContextMenu((prev) => ({ ...prev, visible: false }))
            }
          />
        )}
      </div>
    </div>
  );
};

export default PetriNetEditor;
//tENTATIVA DE CORRECAO 3
