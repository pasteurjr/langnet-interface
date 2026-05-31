// globais.js – estado compartilhado
export const G = {
    /* JointJS */
    graph: null,
    paperRef: null,

    /* Modelo + setters React */
    petriNet: null, setPetriNet: null,

    /* Contadores */
    placeCount: 1, setPlaceCount: null,
    transitionCount: 1, setTransitionCount: null,

    /* Navegação de sub‑redes */
    currentNetId: null, setCurrentNetId: null,
    netStack: [], setNetStack: null,

    /* UI / Seleção */
    selectedElements: new Set(), setSelectedElements: null,
    clipboard: null, setClipboard: null,

    /* Histórico */
    recordAction: null,
};

export const getG = () => G;
export const setG = (updates) => Object.assign(G, updates);
