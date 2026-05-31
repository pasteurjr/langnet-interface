// Place.js - Implementações específicas para lugares (places)

import * as joint from "jointjs";
import { getReferences } from "./PetriNetContext";
import { wrapText, findNestedSubnet, findContainingNet, findElementById } from "./Element";

/**
 * Formats tokens for display in place nodes
 */
export const formatTokens = (tokens) => {
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

/**
 * Create a place element in the graph
 * Mantém a interface original do PetriNetEditor.jsx
 */
export const createPlaceElement = (id, name, tokens = 0, coordinates) => {
  const refs = getReferences();
  const graph = refs.graph;

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

  graph.addCell(place);
  return place;
};

/**
 * Update place visuals based on its data
 * Mantém a interface original do PetriNetEditor.jsx
 */
export const updatePlaceVisuals = (placeElement, data) => {
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
 * Add a new place at the specified coordinates
 * Mantém a interface original do PetriNetEditor.jsx
 */
export const addPlace = (x, y) => {
  const refs = getReferences();
  const currentNetId = refs.getCurrentNetId();
  const placeCount = refs.getCurrentPlaceCount();

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
  refs.recordAction("add_place", newPlace);

  // Update petriNet state based on current level
  if (currentNetId) {
    // We are in a subnet, update it directly
    refs.setPetriNet((prev) => {
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
    refs.setPetriNet((prev) => ({
      ...prev,
      lugares: [...prev.lugares, newPlace],
    }));
  }

  // Increment counter
  refs.setPlaceCount(placeCount + 1);
};

/**
 * Find a place by ID in any level of the network
 * Mantém a interface original, mas usa a função comum
 */
export const findPlaceById = (net, placeId) => {
  return findElementById(net, placeId, 'lugares');
};

/**
 * Find a place in any level of the network
 * Mantém a interface original do PetriNetEditor.jsx
 */
export const findPlaceInNet = (net, placeId) => {
  // Look at main level
  const place = net.lugares.find(l => l.id === placeId);
  if (place) return place;

  // Search recursively in subnets
  for (const lugar of net.lugares) {
    if (lugar.subnet && lugar.subnet.lugares && lugar.subnet.lugares.length > 0) {
      const subPlace = findPlaceInNet(lugar.subnet, placeId);
      if (subPlace) return subPlace;
    }
  }

  return null;
};

/**
 * Operações de Undo/Redo para lugares
 */
export const handleUndoAddPlace = (lastAction) => {
  const refs = getReferences();
  const placeId = lastAction.data.id;
  const place = refs.graph.getCell(placeId);
  if (place) place.remove();

  refs.setPetriNet((prev) => ({
    ...prev,
    lugares: prev.lugares.filter((l) => l.id !== placeId),
  }));
};

export const handleRedoAddPlace = (lastAction) => {
  const { id, nome, tokens, coordenadas, delay } = lastAction.data;
  createPlaceElement(id, nome, tokens, coordenadas);

  const refs = getReferences();
  refs.setPetriNet((prev) => ({
    ...prev,
    lugares: [...prev.lugares, { id, nome, tokens, coordenadas, delay }],
  }));
};

/**
 * Handle delete operation for places
 */
export const handleDelete = (element, type) => {
  if (type !== "place") return; // Apenas para places

  const refs = getReferences();
  const petriNet = refs.petriNet;
  const currentNetId = refs.getCurrentNetId();

  if (!element) {
    console.warn("Elemento não encontrado para exclusão");
    return;
  }

  console.log("Excluindo lugar:", element);

  // Verificar se estamos em uma sub-rede
  const isInSubnet = currentNetId !== null;

  // Array para armazenar itens excluídos para o undo
  const deletedItems = [];

  if (isInSubnet) {
    // Implementação para exclusão em subnet
    // ...
  } else {
    // Código para exclusão na rede principal
    const elementCell = refs.graph.getCell(element.id);

    // Obter dados do elemento principal
    const elementData = {
      id: element.id,
      type,
      data: petriNet.lugares.find((l) => l.id === element.id),
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

    refs.recordAction("delete", deletedItems);

    // Remover arcos conectados do gráfico
    const connectedLinks = refs.graph.getConnectedLinks(elementCell);
    connectedLinks.forEach((link) => link.remove());

    // Remover o elemento do gráfico
    elementCell.remove();

    // Atualizar o estado petriNet
    refs.setPetriNet((prev) => ({
      ...prev,
      lugares: prev.lugares.filter((l) => l.id !== element.id),
      arcos: prev.arcos.filter(
        (a) => a.origem !== element.id && a.destino !== element.id
      ),
    }));
  }
};

/**
 * Copy/Paste operations for places
 */
export const handleCopy = (cut = false) => {
  const refs = getReferences();
  const petriNet = refs.petriNet;
  const selectedElements = refs.getSelectedElements();

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
    const element = refs.graph.getCell(id);
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

  refs.setClipboard(clipboardData);

  if (cut) {
    refs.deleteSelectedElements();
  }
};

export const handlePaste = () => {
  const refs = getReferences();
  const clipboard = refs.clipboard;
  const placeCount = refs.getCurrentPlaceCount();
  const transitionCount = refs.getCurrentTransitionCount();
  const paper = refs.paper;

  if (!clipboard || !clipboard.elements.length) return;

  // Get current mouse position relative to paper
  const paperRect = paper.el.getBoundingClientRect();
  const scale = paper.scale().sx;
  const translation = paper.translate();

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
      refs.setPetriNet((prev) => ({
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
      // Código para transições será implementado em Transition.js
      // ...
    }
  });

  // Update counters
  refs.setPlaceCount(nextPlaceId);
  refs.setTransitionCount(nextTransitionId);

  // Create arcs using new IDs
  clipboard.relations.forEach((arco) => {
    const newSourceId = idMap.get(arco.origem);
    const newTargetId = idMap.get(arco.destino);

    if (newSourceId && newTargetId) {
      // Criar arco com createArcElement
      if (refs.createArcElement) {
        refs.createArcElement({
          origem: newSourceId,
          destino: newTargetId,
          peso: arco.peso
        });
      }

      // Update model
      refs.setPetriNet((prev) => ({
        ...prev,
        arcos: [...prev.arcos, {
          origem: newSourceId,
          destino: newTargetId,
          peso: arco.peso
        }],
      }));

      // Atualizar interfaces se necessário
      if (refs.updateSubnetInterfaces) {
        refs.updateSubnetInterfaces({
          origem: newSourceId,
          destino: newTargetId,
          peso: arco.peso
        });
      }

      finalState.elements.push({
        id: `${newSourceId}-${newTargetId}`,
        type: "arc",
        data: {
          origem: newSourceId,
          destino: newTargetId,
          peso: arco.peso
        },
      });

      hasPasted = true;
    }
  });

  if (hasPasted) {
    // Record paste action for undo/redo
    refs.recordAction("paste", {
      elements: finalState.elements,
      mousePosition,
      offset: {
        x: offsetX,
        y: offsetY,
      },
    });
  }
};