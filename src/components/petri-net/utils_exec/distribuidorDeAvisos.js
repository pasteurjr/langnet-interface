/**
 * distribuidorDeAvisos — um canal, vários interessados.
 *
 * O cliente central tem UM lugar só para o ouvinte dos avisos de execução
 * (setVerboseCallback). Na máquina de referência isso bastava, porque só um
 * painel ficava de pé por vez. Aqui a Bancada tem o painel móvel de
 * acompanhamento E o painel de etiquetas ao mesmo tempo — e cada um registrava
 * por cima do outro, anulando o anterior ao sair de cena. O resultado: o
 * painel de etiquetas ficava vazio, sem ninguém reclamar.
 *
 * Este distribuidor ocupa aquele lugar único uma vez e repassa a todos os
 * inscritos. Quem se inscreve recebe de volta a função de se desinscrever, e
 * sair não derruba os demais.
 */
import { CentralWSClient } from './centralWSClient';

const inscritos = new Set();
let instalado = false;

function instalar() {
  if (instalado) return;
  const central = CentralWSClient.getInstance();
  central.setVerboseCallback((aviso) => {
    inscritos.forEach((ouvinte) => {
      try { ouvinte(aviso); } catch (e) { console.warn('[distribuidor] ouvinte falhou:', e); }
    });
  });
  instalado = true;
}

export function inscrever(ouvinte) {
  if (typeof ouvinte !== 'function') return () => {};
  instalar();
  inscritos.add(ouvinte);
  return () => { inscritos.delete(ouvinte); };
}

export function quantosInscritos() {
  return inscritos.size;
}
