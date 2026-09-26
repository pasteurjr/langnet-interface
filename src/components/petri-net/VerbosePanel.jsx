/**
 * Ponte de nome. O PetriNetViewer, trazido inteiro da máquina de referência,
 * importa "./VerbosePanel". Aqui esse painel chama-se VerbosePanelMovel, para
 * não colidir com o painel de etiquetas (que lá se chamava VerbosePanel.js,
 * noutra pasta). Reexportamos, e assim o arquivo de referência fica intocado.
 */
export { default } from './VerbosePanelMovel';
