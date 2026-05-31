// Element.js - Funções comuns compartilhadas entre elementos

import * as joint from "jointjs";
import { getContext } from "./PetriNetContext";

/**
 * Wraps text to fit within a maximum width
 */
export const wrapText = (text, maxWidth) => {
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
 * Função genérica para criar elemento base (a ser especializado)
 */
export const createElement = (id, name, coordinates, options = {}) => {
  const { graph } = getContext();

  // Base comum para todos os elementos
  const elementBase = {
    id,
    position: coordinates,
    attrs: {
      '.label': {
        text: wrapText(name, 20),
        fill: "black",
        "font-size": 14,
        "text-anchor": "middle",
      }
    }
  };

  return elementBase;
};

/**
 * Função genérica para atualizar visualização de elementos
 */
export const updateElementVisuals = (element, data, isSelected = false) => {
  if (!element) return;

  // Propriedades base - serão sobrescritas pelas especializações
  const baseAttrs = {
    '.label': {
      text: wrapText(data.nome, 20),
      fill: "black",
      "font-size": 14,
      "text-anchor": "middle",
    }
  };

  // Aplicar os atributos base
  element.attr(baseAttrs);
};

/**
 * Função genérica para adicionar elementos
 */
export const addElement = (x, y, type) => {
  const { currentNetId, petriNet, setPetriNet, recordAction } = getContext();

  // Será implementado nas especializações (Place.js, Transition.js, etc.)
  const newElement = { coordenadas: { x, y } };

  // Função auxiliar recursiva para atualizar subnet
  const updateSubnetRecursively = (net, targetId, elementData, path = []) => {
    // Evitar loops infinitos
    if (path.includes(targetId)) {
      console.error("Loop detectado ao procurar subnet:", path);
      return false;
    }

    // Verificações de segurança
    if (!net || !net.lugares) {
      console.error("Rede ou lista de lugares indefinida para ID:", targetId);
      return false;
    }

    // Procurar o lugar com a subnet diretamente neste nível
    const placeIndex = net.lugares.findIndex((l) => l.id === targetId);
    if (placeIndex >= 0) {
      // Encontrou o lugar com subnet
      if (!net.lugares[placeIndex].subnet) {
        net.lugares[placeIndex].subnet = {
          lugares: [],
          transicoes: [],
          arcos: [],
        };
      }

      // Adicionar o elemento ao array correto na subnet (será implementado nas especializações)
      const arrayName = type === 'place' ? 'lugares' :
        type === 'transition' ? 'transicoes' :
          type === 'agent' ? 'agentes' : null;

      if (arrayName && net.lugares[placeIndex].subnet[arrayName]) {
        net.lugares[placeIndex].subnet[arrayName].push(elementData);
        return true;
      }

      return false;
    }

    // Procurar recursivamente nas subnets
    for (let i = 0; i < net.lugares.length; i++) {
      const lugar = net.lugares[i];
      if (lugar && lugar.subnet) {
        const found = updateSubnetRecursively(
          lugar.subnet,
          targetId,
          elementData,
          [...path, lugar.id]
        );

        if (found) return true;
      }
    }

    return false;
  };

  // Estrutura comum para atualizar o modelo (a ser usado pelas especializações)
  if (currentNetId) {
    // Estamos em uma subnet, adiciona elemento à subnet
    setPetriNet((prev) => {
      const updatedNet = JSON.parse(JSON.stringify(prev));
      updateSubnetRecursively(updatedNet, currentNetId, newElement);
      return updatedNet;
    });
  } else {
    // Estamos na rede principal, lógica a ser implementada nas especializações
  }

  return newElement;
};

/**
 * Função genérica para selecionar elementos
 */
export const selectElement = (element, isMultiSelect = false) => {
  const { selectedElements, setSelectedElements, graph } = getContext();

  if (!element) return;

  const elementId = element.id;
  const elementType = element.attributes.type;

  if (isMultiSelect) {
    // Lógica para seleção múltipla (com Ctrl/Cmd)
    setSelectedElements((prev) => {
      const newSelection = new Set(prev);

      // Toggle seleção
      if (newSelection.has(elementId)) {
        newSelection.delete(elementId);
        // Remover destaque visual
        removeElementHighlight(element, elementType);
      } else {
        newSelection.add(elementId);
        // Adicionar destaque visual
        addElementHighlight(element, elementType);
      }

      return newSelection;
    });
  } else {
    // Seleção simples - limpar seleção prévia
    selectedElements.forEach((id) => {
      const el = graph.getCell(id);
      if (el) {
        removeElementHighlight(el, el.attributes.type);
      }
    });

    // Definir nova seleção
    setSelectedElements(new Set([elementId]));
    addElementHighlight(element, elementType);
  }
};

/**
 * Adicionar destaque visual para elemento selecionado
 */
export const addElementHighlight = (element, elementType) => {
  if (!element) return;

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
};

/**
 * Remover destaque visual de elemento não selecionado
 */
export const removeElementHighlight = (element, elementType) => {
  if (!element) return;

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
};

/**
 * Função genérica para excluir elementos
 */
export const deleteElement = (element, type) => {
  const { graph, petriNet, setPetriNet, currentNetId, recordAction } = getContext();

  if (!element) {
    console.warn("Elemento não encontrado para exclusão");
    return;
  }

  console.log("Excluindo elemento:", type, element);

  // Array para armazenar itens excluídos para o undo
  const deletedItems = [];

  // Verificar se estamos em uma subnet
  const isInSubnet = currentNetId !== null;

  if (isInSubnet) {
    // Lógica para excluir em subnet
    const updatedSubnet = findNestedSubnet(petriNet, currentNetId);
    if (!updatedSubnet) return;

    // Encontrar elemento visual
    const elementCell = graph.getCell(element.id);
    if (!elementCell) return;

    // Adicionar o elemento principal aos itens excluídos
    deletedItems.push({
      id: element.id,
      type,
      data: element,
    });

    // Encontrar e adicionar arcos conectados
    const connectedArcs = updatedSubnet.arcos ? updatedSubnet.arcos.filter(
      (a) => a.origem === element.id || a.destino === element.id
    ) : [];

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
    const connectedLinks = graph.getConnectedLinks(elementCell);
    connectedLinks.forEach((link) => link.remove());

    // Remover o elemento do gráfico
    elementCell.remove();

    // A atualização do modelo será feita nas especializações
  } else {
    // Lógica para excluir na rede principal
    const elementCell = graph.getCell(element.id);
    if (!elementCell) return;

    // Determinar a lista do modelo onde buscar o elemento
    const listName =
      type === "place" ? "lugares" :
        type === "transition" ? "transicoes" :
          type === "agent" ? "agentes" : null;

    if (!listName) return;

    // Obter dados do elemento
    const elementData = {
      id: element.id,
      type,
      data: petriNet[listName].find((e) => e.id === element.id),
    };

    // Arcos conectados
    const connectedArcs = petriNet.arcos.filter(
      (a) => a.origem === element.id || a.destino === element.id
    );

    // Adicionar elemento aos itens excluídos
    deletedItems.push({
      id: element.id,
      type,
      data: elementData.data,
    });

    // Adicionar arcos conectados
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

    // Registrar ação para undo
    recordAction("delete", deletedItems);

    // Remover arcos conectados do gráfico
    const connectedLinks = graph.getConnectedLinks(elementCell);
    connectedLinks.forEach((link) => link.remove());

    // Remover elemento do gráfico
    elementCell.remove();

    // A atualização do modelo será feita nas especializações
  }

  return deletedItems;
};

/**
 * Função genérica para desfazer exclusão
 */
export const handleUndoDelete = (lastAction) => {
  const { graph, petriNet, setPetriNet } = getContext();

  // Listas para restaurar na ordem correta
  const restoredPlaces = [];
  const restoredTransitions = [];
  const restoredArcs = [];
  const restoredAgents = [];

  // 1. Separar elementos por tipo
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

  // 2. Atualizar o estado do petriNet
  setPetriNet((prev) => ({
    ...prev,
    lugares: [...prev.lugares, ...restoredPlaces.map((p) => p.data)],
    transicoes: [...prev.transicoes, ...restoredTransitions.map((t) => t.data)],
    arcos: [...prev.arcos, ...restoredArcs],
    agentes: [...(prev.agentes || []), ...restoredAgents.map((a) => a.data)],
  }));

  // 3 & 4 & 6. Restaurar elementos no gráfico - implementado nas especializações

  // 5. Restaurar arcos no próximo ciclo de renderização - para garantir que os nós já estejam criados
  setTimeout(() => {
    restoredArcs.forEach(arc => {
      // A implementação específica será feita em Arc.js
    });
  }, 0);
};

/**
 * Função genérica para refazer exclusão
 */
export const handleRedoDelete = (lastAction) => {
  const { graph, petriNet, setPetriNet } = getContext();

  // Filtrar itens válidos
  const itemsToDelete = lastAction.data.filter(
    (item) => item && item.type && item.id
  );

  // Primeiro remover arcos
  itemsToDelete.forEach((item) => {
    if (item.type === "arc" && item.data) {
      const link = graph.getLinks().find(
        (l) =>
          l.attributes.source.id === item.data.origem &&
          l.attributes.target.id === item.data.destino
      );
      if (link) link.remove();
    }
  });

  // Depois remover lugares, transições e agentes
  itemsToDelete.forEach((item) => {
    if ((item.type === "place" || item.type === "transition") && item.id) {
      const cell = graph.getCell(item.id);
      if (cell) cell.remove();
    } else if (item.type === "agent" && item.id) {
      const agentElement = graph.getElements().find(
        el => el.get('type') === 'agent' && el.get('agentId') === item.id
      );
      if (agentElement) agentElement.remove();
    }
  });

  // Atualizar o estado do petriNet
  setPetriNet((prev) => {
    const newState = { ...prev };

    // Remover lugares e transições
    newState.lugares = prev.lugares.filter(
      (l) => !itemsToDelete.some((item) => item.type === "place" && item.id === l.id)
    );

    newState.transicoes = prev.transicoes.filter(
      (t) => !itemsToDelete.some((item) => item.type === "transition" && item.id === t.id)
    );

    // Remover arcos
    newState.arcos = prev.arcos.filter(
      (a) => !itemsToDelete.some(
        (item) => item.type === "arc" && item.data &&
          item.data.origem === a.origem &&
          item.data.destino === a.destino
      )
    );

    // Remover agentes
    if (newState.agentes) {
      newState.agentes = prev.agentes.filter(
        (a) => !itemsToDelete.some((item) => item.type === "agent" && item.id === a.id)
      );
    }

    return newState;
  });
};

/**
 * Função genérica para mover elementos
 */
export const handleUndoMove = (lastAction) => {
  const { graph } = getContext();

  // Restaurar posições iniciais
  lastAction.data.initial.forEach((element) => {
    const cell = graph.getCell(element.id);
    if (cell) {
      cell.position(element.data.coordenadas.x, element.data.coordenadas.y);

      // Atualizar propriedades visuais com base no tipo
      if (element.type === "place" || element.type === "transition" || element.type === "agent") {
        updateElementVisuals(cell, element.data);
      }
    }
  });

  // Atualizar o estado do modelo - implementado nas especializações
};

/**
 * Função genérica para refazer movimento
 */
export const handleRedoMove = (lastAction) => {
  const { graph } = getContext();

  // Restaurar posições finais
  lastAction.data.final.forEach((element) => {
    const cell = graph.getCell(element.id);
    if (cell) {
      cell.position(element.data.coordenadas.x, element.data.coordenadas.y);

      // Atualizar propriedades visuais com base no tipo
      if (element.type === "place" || element.type === "transition" || element.type === "agent") {
        updateElementVisuals(cell, element.data);
      }
    }
  });

  // Atualizar o estado do modelo - implementado nas especializações
};

/**
 * Função genérica para copiar elementos
 */
export const copyElements = (cut = false) => {
  const { graph, petriNet, selectedElements, setClipboard, deleteSelectedElements } = getContext();

  if (selectedElements.size === 0) return;

  const clipboardData = {
    elements: [],
    positions: new Map(),
    relations: [],
  };

  // Calcular ponto central para posicionamento ao colar
  const centerPoint = { x: 0, y: 0 };
  let count = 0;

  // Coletar todos os elementos selecionados
  selectedElements.forEach((id) => {
    const element = graph.getCell(id);
    if (!element) return;

    const pos = element.position();
    centerPoint.x += pos.x;
    centerPoint.y += pos.y;
    count++;

    // Processa o elemento com base no seu tipo
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

  // Coletar arcos entre elementos selecionados
  petriNet.arcos.forEach((arco) => {
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
 * Função genérica para colar elementos
 */
export const pasteElements = () => {
  const {
    graph,
    petriNet,
    setPetriNet,
    clipboard,
    placeCount,
    setPlaceCount,
    transitionCount,
    setTransitionCount,
    paperRef,
    recordAction,
    createPlaceElement,
    createTransitionElement,
    createArcElement
  } = getContext();

  if (!clipboard || !clipboard.elements.length) return;

  // Obter posição atual do mouse relativa ao papel
  const paperRect = paperRef.el.getBoundingClientRect();
  const scale = paperRef.scale().sx;
  const translation = paperRef.translate();

  const mousePosition = {
    x: (window.lastMouseX - paperRect.left - translation.tx) / scale,
    y: (window.lastMouseY - paperRect.top - translation.ty) / scale,
  };

  // Calcular deslocamento com base na posição do mouse
  const offsetX = mousePosition.x - clipboard.center.x;
  const offsetY = mousePosition.y - clipboard.center.y;

  // Mapear IDs antigos para novos
  const idMap = new Map();
  const newElements = new Set();
  let hasPasted = false;
  const finalState = { elements: [] };

  // Variáveis locais para controlar IDs
  let nextPlaceId = placeCount;
  let nextTransitionId = transitionCount;

  // Criar todos os elementos
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

      // Atualizar o modelo
      setPetriNet((prev) => ({
        ...prev,
        lugares: [...prev.lugares, newElement],
      }));

      // Criar elemento visual
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

      // Atualizar o modelo
      setPetriNet((prev) => ({
        ...prev,
        transicoes: [...prev.transicoes, newElement],
      }));

      // Criar elemento visual
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

  // Atualizar contadores
  setPlaceCount(nextPlaceId);
  setTransitionCount(nextTransitionId);

  // Criar arcos com os novos IDs - após pequeno delay para garantir que elementos foram criados
  setTimeout(() => {
    clipboard.relations.forEach((arco) => {
      const newSourceId = idMap.get(arco.origem);
      const newTargetId = idMap.get(arco.destino);

      if (newSourceId && newTargetId) {
        // Criar arco com os novos IDs
        const newArc = {
          origem: newSourceId,
          destino: newTargetId,
          peso: arco.peso,
        };

        createArcElement(newArc);

        // Atualizar o modelo
        setPetriNet((prev) => ({
          ...prev,
          arcos: [...prev.arcos, newArc],
        }));

        hasPasted = true;
        finalState.elements.push({
          id: `${newSourceId}-${newTargetId}`,
          type: "arc",
          data: newArc,
        });
      }
    });

    if (hasPasted) {
      // Registrar ação para undo/redo
      recordAction("paste", {
        elements: finalState.elements,
        mousePosition,
        offset: {
          x: offsetX,
          y: offsetY,
        },
      });
    }
  }, 0);
};

/**
 * Função genérica para desfazer colagem
 */
export const handleUndoPaste = (lastAction) => {
  const { graph, petriNet, setPetriNet } = getContext();

  // Primeiro remover arcos para evitar referências quebradas
  lastAction.data.elements
    .filter((element) => element.type === "arc")
    .forEach((element) => {
      // Remover arcos do gráfico
      const link = graph.getLinks()
        .find((l) =>
          l.attributes.source.id === element.data.origem &&
          l.attributes.target.id === element.data.destino
        );
      if (link) link.remove();
    });

  // Depois remover lugares e transições
  lastAction.data.elements
    .filter((element) => element.type !== "arc")
    .forEach((element) => {
      const cell = graph.getCell(element.id);
      if (cell) cell.remove();
    });

  // Atualizar o modelo
  setPetriNet((prev) => ({
    ...prev,
    lugares: prev.lugares.filter(
      (l) => !lastAction.data.elements.some(
        (e) => e.type === "place" && e.id === l.id
      )
    ),
    transicoes: prev.transicoes.filter(
      (t) => !lastAction.data.elements.some(
        (e) => e.type === "transition" && e.id === t.id
      )
    ),
    arcos: prev.arcos.filter(
      (a) => !lastAction.data.elements.some(
        (e) => e.type === "arc" &&
          e.data.origem === a.origem &&
          e.data.destino === a.destino
      )
    ),
  }));
};

/**
 * Função genérica para refazer colagem
 */
export const handleRedoPaste = (lastAction) => {
  const { graph, petriNet, setPetriNet, createPlaceElement, createTransitionElement, createArcElement } = getContext();

  // Primeiro recriar lugares e transições
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

  // Depois de um ligeiro atraso para garantir que elementos foram criados, recriar arcos
  setTimeout(() => {
    lastAction.data.elements
      .filter((element) => element.type === "arc")
      .forEach((element) => {
        createArcElement(element.data);
      });
  }, 0);

  // Atualizar o modelo
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

/**
 * Função para encontrar elemento por ID em qualquer nível da rede
 */
export const findElementById = (net, elementId, elementType) => {
  // Verificar no nível atual
  if (net[elementType] && Array.isArray(net[elementType])) {
    const element = net[elementType].find(e => e.id === elementId);
    if (element) return element;
  }

  // Procurar recursivamente nas subnets
  if (net.lugares && Array.isArray(net.lugares)) {
    for (const lugar of net.lugares) {
      if (lugar.subnet) {
        const subnetElement = findElementById(lugar.subnet, elementId, elementType);
        if (subnetElement) return subnetElement;
      }
    }
  }

  return null;
};

/**
 * Encontrar subnet aninhada na rede
 */
/**
 * Encontrar subnet aninhada na rede
 */
export const findNestedSubnet = (net, placeId, path = []) => {
  // Caso especial: buscar a rede principal
  if (placeId === null) return net;

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
 * Encontrar a rede que contém um determinado elemento
 * Retorna { net, parent } onde net é a rede contendo o elemento e parent é o ID do lugar pai (se aninhado)
 */
export const findContainingNet = (net, elementId, parentId = null, path = []) => {
  // Verificar se o elemento está diretamente neste nível (lugar, transição ou agente)
  if (net.lugares && net.lugares.some((l) => l.id === elementId)) {
    return { net, parent: parentId };
  }

  if (net.transicoes && net.transicoes.some((t) => t.id === elementId)) {
    return { net, parent: parentId };
  }

  if (net.agentes && net.agentes.some((a) => a.id === elementId)) {
    return { net, parent: parentId };
  }

  // Se não encontramos neste nível, procurar em cada subnet
  for (let i = 0; i < (net.lugares || []).length; i++) {
    const lugar = net.lugares[i];
    if (lugar.subnet && lugar.subnet.lugares) {
      // Evitar loops infinitos
      if (path.includes(lugar.id)) continue;

      // Procurar recursivamente
      const result = findContainingNet(lugar.subnet, elementId, lugar.id, [
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

/**
 * Atualiza o modelo de dados com os elementos do canvas
 */
export const syncModelWithCanvas = (netToUpdate, currentNetId) => {
  const { graph } = getContext();

  // Coletar elementos do canvas
  const elements = graph.getElements();
  const links = graph.getLinks();

  // Mapear elementos atuais no canvas
  const canvasPlaces = new Map();
  const canvasTransitions = new Map();
  const canvasAgents = new Map();
  const canvasArcs = new Set();

  // Coletar lugares, transições e agentes do canvas
  elements.forEach((element) => {
    const pos = element.position();
    if (element.attributes.type === "basic.Circle") {
      // É um lugar
      canvasPlaces.set(element.id, {
        id: element.id,
        nome: element.attr(".label/text") || "",
        tokens: parseInt(element.attr(".tokens/text")?.replace(/●/g, "")?.trim()) || 0,
        coordenadas: { x: pos.x, y: pos.y },
        delay: 0,
      });
    } else if (element.attributes.type === "basic.Rect") {
      // É uma transição
      canvasTransitions.set(element.id, {
        id: element.id,
        nome: element.attr(".label/text") || "",
        orientacao: element.get("size").width === 3 ? "vert" : "hor",
        coordenadas: { x: pos.x, y: pos.y },
        prioridade: 1,
        probabilidade: 0,
        tempo: 0,
      });
    } else if (element.get('type') === 'agent') {
      // É um agente
      canvasAgents.set(element.get('agentId'), {
        id: element.get('agentId'),
        nome: element.attr("text/text") || "Agente",
        coordenadas: { x: pos.x, y: pos.y },
        width: element.size().width,
        height: element.size().height
      });
    }
  });

  // Coletar arcos do canvas
  links.forEach((link) => {
    if (link.attributes.source.id && link.attributes.target.id) {
      canvasArcs.add(
        `${link.attributes.source.id}-${link.attributes.target.id}`
      );
    }
  });

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

    // Sincronizar agentes
    if (net.agentes && Array.isArray(net.agentes)) {
      // Atualizar agentes existentes
      net.agentes = net.agentes.map((a) => {
        const canvasAgent = canvasAgents.get(a.id);
        if (canvasAgent) {
          return {
            ...a,
            coordenadas: canvasAgent.coordenadas,
            nome: canvasAgent.nome,
            width: canvasAgent.width,
            height: canvasAgent.height
          };
        }
        return a;
      });

      // Adicionar novos agentes que estão no canvas mas não no modelo
      canvasAgents.forEach((agent) => {
        if (!net.agentes.some((a) => a.id === agent.id)) {
          net.agentes.push(agent);
        }
      });
    } else if (canvasAgents.size > 0) {
      // Se não existe array de agentes, mas temos agentes no canvas, criar o array
      net.agentes = Array.from(canvasAgents.values());
    }

    // Sincronizar arcos
    if (net.arcos && Array.isArray(net.arcos)) {
      // Adicionar novos arcos que estão no canvas mas não no modelo
      links.forEach((link) => {
        const sourceId = link.attributes.source.id;
        const targetId = link.attributes.target.id;

        if (!net.arcos.some((a) => a.origem === sourceId && a.destino === targetId)) {
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
      const place = net.lugares && net.lugares.find((l) => l.id === targetId);
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

  return netToUpdate;
};

/**
 * Extrai a subnet atual do gráfico
 */
export const extractCurrentSubnet = (updatedPositions = null) => {
  const { graph, petriNet, currentNetId } = getContext();

  if (!currentNetId) return {};

  // Encontrar a subnet atual diretamente usando a função melhorada
  const { net: containingNet } = findContainingNet(petriNet, currentNetId);
  if (!containingNet) {
    console.error("Não foi possível encontrar o contexto para a subnet atual");
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
  const currentPlace = containingNet.lugares.find((l) => l.id === currentNetId);
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
  const elements = graph.getElements();
  const links = graph.getLinks();

  // Manter um mapa de IDs para preservar propriedades especiais
  const idMap = new Map();

  // Mapear todos os elementos existentes por ID para referência rápida
  existingSubnet.lugares.forEach((lugar) => idMap.set(lugar.id, lugar));
  existingSubnet.transicoes.forEach((trans) => idMap.set(trans.id, trans));

  // Nova lista de lugares baseada nos elementos visuais atuais
  subnet.lugares = [];
  elements.forEach((element) => {
    if (element.attributes.type === "basic.Circle") {
      let position;

      // Usar posição atualizada se fornecida, caso contrário usar a posição no canvas
      if (updatedPositions && updatedPositions.has(element.id)) {
        position = updatedPositions.get(element.id);
      } else {
        position = element.position();
      }

      const id = element.id;

      // Preservar propriedades do lugar original se existir
      const originalPlace = idMap.get(id);
      const safeTokens = () => {
        try {
          return originalPlace?.tokens !== undefined
            ? Number(originalPlace.tokens)
            : Number(element.attr(".tokens/text")?.replace(/[^0-9]/g, "") || 0);
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
      let position;

      // Usar posição atualizada se fornecida, caso contrário usar a posição no canvas
      if (updatedPositions && updatedPositions.has(element.id)) {
        position = updatedPositions.get(element.id);
      } else {
        position = element.position();
      }

      const id = element.id;

      // Preservar propriedades especiais da transição original
      const originalTrans = idMap.get(id);

      subnet.transicoes.push({
        id,
        nome: element.attr(".label/text") || "",
        orientacao: element.get("size").width === 3 ? "vert" : "hor",
        coordenadas: { x: position.x, y: position.y },
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

  // Coletar agentes
  if (existingSubnet.agentes) {
    // Usar os agentes que já existem na subnet
    subnet.agentes = [...existingSubnet.agentes];

    // Atualizar apenas as posições dos agentes que estão no canvas
    const agentElements = graph.getElements()
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

  // Importante: preservar listas entradas/saídas
  if (existingSubnet.entradas) subnet.entradas = [...existingSubnet.entradas];
  if (existingSubnet.saidas) subnet.saidas = [...existingSubnet.saidas];

  return subnet;
};

/**
 * Atualiza uma subnet em um lugar específico na hierarquia
 */
export const updateSubnetInPlace = (net, targetId, newSubnet) => {
  // Procurar o lugar diretamente neste nível
  const placeIndex = net.lugares.findIndex((l) => l.id === targetId);
  if (placeIndex >= 0) {
    // Preservar os tokens atuais antes de atualizar a subnet
    const currentTokens = net.lugares[placeIndex].tokens;

    // Atualizar o lugar com a nova subnet
    net.lugares[placeIndex] = {
      ...net.lugares[placeIndex],
      subnet: {
        ...newSubnet,
        agentes: net.lugares[placeIndex].subnet?.agentes || [] // Preservar agentes existentes
      },
      tokens: currentTokens // Garantir que os tokens são preservados
    };

    return true;
  }

  // Se não encontramos neste nível, procurar recursivamente nas sub-redes
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

/**
 * Obter o elemento apropriado para seleção de acordo com o tipo
 */
export const getElementForSelection = (elementId, type) => {
  const { graph, petriNet } = getContext();

  let element = null;

  if (type === "place" || type === "transition") {
    // Elemento JointJS padrão
    element = graph.getCell(elementId);
  } else if (type === "agent") {
    // Agente especial
    element = graph.getElements().find(
      el => el.get('type') === 'agent' && el.get('agentId') === elementId
    );
  } else if (type === "arc") {
    // Arco
    const arcData = petriNet.arcos.find(
      a => `${a.origem}-${a.destino}` === elementId
    );

    if (arcData) {
      element = graph.getLinks().find(
        l => l.attributes.source.id === arcData.origem &&
          l.attributes.target.id === arcData.destino
      );
    }
  }

  return element;
};

/**
 * Função utilitária para verificar se um elemento existe
 */
export const elementExists = (elementId, type) => {
  const { petriNet } = getContext();

  if (type === "place") {
    return petriNet.lugares.some(l => l.id === elementId);
  } else if (type === "transition") {
    return petriNet.transicoes.some(t => t.id === elementId);
  } else if (type === "agent") {
    return petriNet.agentes && petriNet.agentes.some(a => a.id === elementId);
  } else if (type === "arc") {
    const [origem, destino] = elementId.split('-');
    return petriNet.arcos.some(a => a.origem === origem && a.destino === destino);
  }

  return false;
};