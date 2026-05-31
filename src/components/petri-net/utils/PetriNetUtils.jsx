/**
 * Função auxiliar para encontrar uma sub-rede em qualquer nível da hierarquia
 */
export const findNestedSubnet = (net, placeId, path = []) => {
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
  export const findContainingNet = (net, placeId, parentId = null, path = []) => {
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
  
  /**
   * Função auxiliar para encontrar um lugar pelo ID em qualquer nível da rede
   */
  export const findPlaceById = (net, placeId) => {
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
  
  /**
   * Função auxiliar para encontrar uma transição pelo ID em qualquer nível da rede
   */
  export const findTransitionById = (net, transitionId) => {
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