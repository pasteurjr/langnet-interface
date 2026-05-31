// PetriNetContext.js - Gerenciador de referências simplificado

/**
 * Objeto que armazena referências úteis para serem acessadas
 * por funções em diferentes arquivos, sem depender de hooks do React.
 */
let references = {
    // Referências ao gráfico e elementos visuais
    graph: null,           // graphRef.current 
    paper: null,           // paperRef.current

    // Estado atual (sem hooks)
    petriNet: null,        // Valor atual do estado petriNet

    // Funções de callback para manipular estado
    setPetriNet: null,     // Função do useState para atualizar petriNet
    recordAction: null,    // Função para registrar ações para undo/redo

    // Getters para valores que mudam com frequência (funções que retornam valores atuais)
    getCurrentNetId: () => null,
    getCurrentPlaceCount: () => 1,
    getCurrentTransitionCount: () => 1,
    getSelectedElements: () => new Set(),

    // Setters para contadores
    setPlaceCount: null,
    setTransitionCount: null,

    // Referências para funções comuns de manipulação da rede
    createArcElement: null,
    updateSubnetInterfaces: null
};

/**
 * Inicializa as referências com valores e funções do componente principal
 */
export const initReferences = (newRefs) => {
    references = { ...references, ...newRefs };
};

/**
 * Retorna as referências atuais para uso em funções
 */
export const getReferences = () => references;

/**
 * Atualiza referências específicas sem substituir todo o objeto
 */
export const updateReferences = (updates) => {
    Object.assign(references, updates);
};