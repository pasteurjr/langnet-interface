// Etapa 2: gera a ESPECIFICAÇÃO do v3 (c4871aaf) a partir da versao 4 de requisitos (unificada).
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const PROJ = 'c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const REQ_VERSION_LABEL = 'Versão 4';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const INSTR = [
  "OBRIGATORIO: gere TODAS as 14 secoes numeradas (1 a 14), SEM PARAR antes da secao 14. Inclua",
  "explicitamente: 9. Fluxos de Trabalho, 10. Analise de Arquitetura, 11. Controle de Qualidade,",
  "12. Glossario, 13. Rastreabilidade (matriz FR/UC/BR), 14. Apendices. Seja CONCISO nos wireframes",
  "(no maximo 1 por caso de uso) para ter orcamento de tokens para as 14 secoes.",
  "Este app UNIFICA gestao operacional municipal + CALCULOS urbanisticos. Cubra os eixos:",
  "(1) URBANISTICO: parametros por zona (CA, TO, permeabilidade, recuos, gabarito, area minima, usos) e ZONEAMENTO poligonal;",
  "(2) AMBIENTAL: APP/Codigo Florestal, Reserva Legal, declividade;",
  "(3) CALCULO/CONFORMIDADE: para CADA regra, a tela/UC CALCULA o valor (ex.: CA=area_construida/area_terreno,",
  "TO=area_projecao/area_terreno) e confronta com o exigido pela zona -> conforme/nao conforme, com fundamentacao legal;",
  "(4) OPERACIONAL: cadastros, licenciamento/alvara, fiscalizacao, notificacoes, dashboard.",
  "Modelo de dados com entidades geoespaciais (zona, lote, edificacao, geometria/poligonais) e colunas de calculo",
  "(ca_maximo, to_maxima, area_terreno, area_construida, ca_calculado). UC-chave: Consulta de Conformidade Consolidada."
].join(" ");

(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1500, height: 1200 } });
  const log=(...a)=>console.log(...a);
  let genFired = false, genStatus = 0, genBody = '';
  p.on('response', async r => {
    const u = r.url();
    if (r.request().method() === 'POST' && /\/specifications\/?$/.test(u)) {
      genFired = true; genStatus = r.status();
      try { genBody = JSON.stringify(await r.json()).slice(0, 200); } catch (e) {}
    }
  });
  await p.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  // navegar com retry (DB remoto flaky)
  let ok=false;
  for(let a=1;a<=4&&!ok;a++){
    await p.goto(`http://localhost:3000/project/${PROJ}/specification`, { waitUntil: 'domcontentloaded' }).catch(()=>{});
    ok=await p.waitForSelector('button.btn-requirements-compact',{timeout:40000}).then(()=>true).catch(()=>false);
    log('nav spec #'+a, ok);
  }
  if(!ok){log('ERRO: pagina de especificacao nao carregou');await b.close();process.exit(3);}
  await sleep(1500);

  // 1) abre modal de selecao de requisitos
  await p.locator('button.btn-requirements-compact').first().click(); await sleep(2500);
  await p.screenshot({ path: `${OUT}/13-spec-modal-req.png`, fullPage: true });
  // 2) sessao mais recente (dc66b1e7) = primeiro card
  await p.locator('.session-item').first().click(); await sleep(2500);
  await p.screenshot({ path: `${OUT}/14-spec-versoes.png`, fullPage: true });
  // 3) versao 4 (por texto)
  const v4 = p.locator('.session-item', { hasText: REQ_VERSION_LABEL }).first();
  if(!(await v4.count())){log('ERRO: '+REQ_VERSION_LABEL+' nao encontrada');await p.screenshot({path:`${OUT}/14b-sem-v4.png`,fullPage:true});await b.close();process.exit(2);}
  await v4.click(); await sleep(2500);
  await p.screenshot({ path: `${OUT}/15-spec-preview-v4.png`, fullPage: true });
  // 4) confirmar selecao
  const confirmBtn = p.locator('button.btn-select', { hasText: /Selecionar este/ }).first();
  if(!(await confirmBtn.count())){log('ERRO: botao Selecionar este Documento nao encontrado');await b.close();process.exit(2);}
  await confirmBtn.click(); await sleep(2000);
  log('selecao confirmada (v4)');
  await p.screenshot({ path: `${OUT}/16-spec-req-selecionado.png`, fullPage: true });

  // 5) instrucao
  const instr = p.locator('textarea').first();
  if (await instr.count()) { try { await instr.click(); await instr.fill(''); await instr.pressSequentially(INSTR, { delay: 1 }); log('instrucao definida', INSTR.length); } catch (e) { log('sem textarea', e.message); } }

  // 6) disparar geracao
  const startBtn = p.locator('button.btn-start-analysis').first();
  if (await startBtn.isDisabled()) { log('ERRO: botao Gerar desabilitado (selecao nao pegou)'); await p.screenshot({ path: `${OUT}/16b-spec-ERRO.png`, fullPage: true }); await b.close(); process.exit(3); }
  await startBtn.click();
  log('geracao de especificacao disparada; aguardando POST /specifications...');
  for (let i = 0; i < 30; i++) { await sleep(3000); if (genFired) break; }
  await sleep(1500);
  log('POST status:', genStatus, '| body:', genBody);
  await p.screenshot({ path: `${OUT}/17-spec-iniciada.png`, fullPage: true });
  log(genFired ? 'SPEC_INICIADA' : 'SPEC_NAO_DISPAROU');
  await b.close(); log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
