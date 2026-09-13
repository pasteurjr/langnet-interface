// Corrige o CONTRATO das tarefas pela conversa com o agente, na etapa de YAML (aba Tasks).
// Cada pedido é uma correção apontada pela revisão da Rede de Petri: quem entrega o quê.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1540', 10);
const PEDIDO = process.argv[3] || '';
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,110));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/yaml-generation`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  await shot(p,'tasks-etapa-aberta');
  // A etapa tem duas abas (Agents YAML / Tasks YAML). O contrato das tarefas está na de Tasks —
  // e o rótulo começa com um ícone, então casar por "^Tasks" não pega nada.
  const trocou = await p.evaluate(() => {
    const alvo = [...document.querySelectorAll('button,div[role=button],li,a,span')].find(
      (e) => /Tasks\s*YAML/i.test(e.textContent || '') && e.querySelectorAll('*').length < 4);
    if (!alvo) return 'aba Tasks YAML não achada';
    (alvo.closest('button,div[role=button],li,a') || alvo).click();
    return 'aba Tasks YAML aberta';
  });
  console.log(trocou); await sleep(3500);
  // A aba abre VAZIA: o refino só existe depois de carregar a versão vigente pelo Histórico.
  const hist = p.getByRole('button', { name: /Histórico/i }).first();
  if (await hist.count()) { await hist.click({ timeout: 12000 }).catch(() => {}); await sleep(3500); }
  await shot(p,'tasks-historico');
  const carregou = await p.evaluate(() => {
    const linhas = [...document.querySelectorAll('*')].filter(
      (e) => /Clique para (carregar|visualizar)|CRIADO EM|vers/i.test(e.textContent || '')
             && e.querySelectorAll('*').length < 12);
    if (!linhas.length) return 'nada no histórico';
    linhas[0].click();
    return 'carreguei: ' + (linhas[0].textContent || '').trim().replace(/\s+/g, ' ').slice(0, 60);
  });
  console.log(carregou); await sleep(3500);
  // Segundo passo: dentro do "Histórico de Versões" é preciso acionar "Clique para carregar" na
  // versão mais nova. Sem isso o modal fica aberto e a conversa nunca aparece.
  if (await p.locator('text=/Histórico de Versões/i').count()) {
    const abriu = await p.evaluate(() => {
      const link = [...document.querySelectorAll('*')].find(
        (e) => /Clique para carregar/i.test(e.textContent || '') && e.children.length === 0);
      if (!link) return 'link de carregar não achado';
      (link.closest('a,button,div[role=button],div') || link).click();
      return 'versão carregada';
    });
    console.log(abriu); await sleep(6000);
  }
  // Se o modal insistir em ficar aberto, fecha.
  const fechar = p.getByRole('button', { name: /^Fechar$/i }).first();
  if (await fechar.count()) { await fechar.click({ timeout: 8000 }).catch(() => {}); await sleep(2500); }
  await shot(p,'tasks-versao-carregada');
  const texto = await p.evaluate(()=>document.body.innerText);
  console.log('estado:', texto.replace(/\n+/g,' | ').slice(0,300));
  // Nesta etapa o miolo é largo e a conversa começa RECOLHIDA — é preciso abrir pelo botão
  // "Refinar com o agente", senão a caixa de mensagem simplesmente não existe na página.
  const abrirChat = p.getByRole('button', { name: /Refinar com o agente/i }).first();
  if (await abrirChat.count()) {
    await abrirChat.click({ timeout: 12000 }).catch(() => {});
    await sleep(2500);
    console.log('conversa aberta');
  } else {
    console.log('(botão de abrir a conversa não achado — talvez já esteja aberta)');
  }
  // A conversa é a caixa de mensagem do painel do meio.
  const caixa = p.getByPlaceholder(/Digite sua mensagem/i).first();
  if (!await caixa.count()) { console.log('!! caixa da conversa não achada'); await shot(p,'tasks-sem-caixa'); await b.close(); return; }
  await caixa.focus({timeout:15000});
  await p.keyboard.type(PEDIDO, {delay:4});
  await sleep(800); await shot(p,'tasks-pedido-digitado');
  // O botão de enviar fica ao lado; se o clique não pegar, Enter envia.
  const enviar = p.getByRole('button',{name:/Enviar|Send/i}).first();
  if (await enviar.count()) { await enviar.click({timeout:15000}).catch(()=>p.keyboard.press('Enter')); }
  else { await p.keyboard.press('Enter'); }
  console.log('▷ pedido enviado às', new Date().toLocaleTimeString());
  for (let i=0;i<90;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (!/Processando|Refinando|⏳/i.test(t)) break; }
  await sleep(4000); await shot(p,'tasks-refinado');
  const fim = await p.evaluate(()=>document.body.innerText);
  const i = fim.search(/aplicad|refinad|resumo|erro/i);
  console.log('RESPOSTA:', fim.slice(i, i+900).replace(/\n{2,}/g,'\n'));
  await b.close();
})();
