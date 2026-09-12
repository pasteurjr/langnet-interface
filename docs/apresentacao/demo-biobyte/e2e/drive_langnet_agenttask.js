// Etapa Agentes & Tarefas: escolhe a Especificação de origem pelo histórico e gera.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1394', 10);
const ALVO = process.argv[3] || '';
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
  await p.goto(`${BASE}/project/${PROJ}/agent-task`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  await shot(p,'ats-etapa-aberta');
  // origem: abre o histórico de especificações e escolhe
  const btnOrigem = p.getByRole('button',{name:/Especifica|Origem|Selecionar/i}).first();
  if (await btnOrigem.count()) { await btnOrigem.click({timeout:15000}).catch(()=>{}); await sleep(3000); }
  await shot(p,'ats-modal-origem');
  // O modal lista as especificações pelo NOME, não pelo código — procurar pelo id não acha nada e
  // a etapa acabava gerando da especificação errada (aconteceu: nasceu de af633b8a em vez da que
  // tinha a correção do usuário). O nome vem por argumento.
  const NOME = process.argv[4] || 'DeepSeek flash';
  const listados = await p.evaluate(() => [...document.querySelectorAll('*')]
    .filter((e) => e.children.length === 0 && /Especifica|EM FASES|DeepSeek|cache/i.test(e.textContent || ''))
    .map((e) => (e.textContent || '').trim().slice(0, 60)).slice(0, 10));
  console.log('especificações no modal:', listados.join(' || '));
  const escolhido = await p.evaluate((nome) => {
    const alvo = [...document.querySelectorAll('*')].find(
      (e) => e.children.length === 0 && (e.textContent || '').includes(nome));
    if (!alvo) return 'NÃO ACHEI: ' + nome;
    (alvo.closest('.spec-card, [class*=card], div[role=button], div') || alvo).click();
    return 'escolhido: ' + (alvo.textContent || '').trim().slice(0, 50);
  }, NOME);
  console.log(escolhido);
  await sleep(2500);
  // o modal tem dois passos: o cartão da especificação e, depois, a VERSÃO — cujo link nesta
  // etapa é "Clique para carregar" (nas outras é "Clique para visualizar")
  const verVer = p.locator('text=/Clique para carregar|Clique para visualizar|ver vers/i').first();
  if (await verVer.count()) { await verVer.click({timeout:12000}).catch(()=>{}); await sleep(2500); }
  // Se o modal continuar aberto, o clique não pegou (o elemento fica coberto). Aciona por dentro
  // da página, que é o que o navegador faria se o ponteiro chegasse lá.
  if (await p.locator('text=/Histórico de Versões/i').count()) {
    const acionou = await p.evaluate(() => {
      const alvo = [...document.querySelectorAll('*')].find(
        (e) => /Clique para carregar/i.test(e.textContent || '') && e.children.length === 0);
      if (!alvo) return 'não achei o link';
      (alvo.closest('a,button,div[role=button],div') || alvo).click();
      return 'acionado';
    });
    console.log('carregar versão:', acionou);
    await sleep(3000);
  }
  await shot(p,'ats-origem-escolhida');
  console.log('estado:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(250,520));
  const btn = p.getByRole('button',{name:/Gerar Agentes & Tarefas|Gerar Agentes/i}).first();
  if (!await btn.count()) { console.log('!! botão Gerar não achado'); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ geração disparada às', new Date().toLocaleTimeString());
  await sleep(5000); await shot(p,'ats-gerando');
  for (let i=0;i<180;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/agente|tarefa/i.test(t) && !/Gerando|Processando/i.test(t)) break; }
  await sleep(3000); await shot(p,'ats-pronto');
  console.log('final:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(250,520));
  await b.close();
})();
