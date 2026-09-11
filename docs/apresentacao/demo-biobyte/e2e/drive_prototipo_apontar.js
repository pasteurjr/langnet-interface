// O TESTE QUE O USUÁRIO PEDIU: apontar um componente no protótipo, mandar a mudança pelo agente,
// e ver o protótipo se remontar sozinho com o resultado.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1379', 10);
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
  await p.goto(`${BASE}/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'});
  await sleep(8000);

  const q = p.frameLocator('iframe[title="protótipo"]');
  // vai para a tela do escore de Cox (Prognóstico)
  const item = q.locator('a,li,div').filter({hasText:/Progn|Escore de Risco de Cox/i}).first();
  if (await item.count()) { await item.click({timeout:15000}).catch(()=>{}); await sleep(2500); }
  await shot(p,'apontar-antes');
  const antes = await q.locator('body').innerText().catch(()=>'');
  console.log('ANTES — tela mostra:', antes.replace(/\n/g,' · ').slice(0,200));

  // 1) liga o modo de apontar
  const btnApontar = p.getByRole('button',{name:/Apontar componente/i}).first();
  if (!await btnApontar.count()) { console.log('!! botão Apontar não achado'); await b.close(); return; }
  await btnApontar.click({timeout:15000});
  await sleep(1200); await shot(p,'apontar-ligado');

  // 2) clica num componente dentro do protótipo
  const alvo = q.locator('button, label, input').first();
  if (await alvo.count()) { await alvo.click({timeout:15000}).catch(()=>{}); await sleep(2000); }
  await shot(p,'apontar-componente-escolhido');
  const alvoTxt = await p.evaluate(()=>{
    const el=[...document.querySelectorAll('*')].find(e=>/alvo|Apontado|componente:/i.test(e.textContent||'')&&e.children.length<3);
    return el ? (el.textContent||'').trim().slice(0,120) : '(sem indicação de alvo na tela)';});
  console.log('ALVO apontado:', alvoTxt);

  // 3) abre a conversa e pede a mudança
  const btnChat = p.getByRole('button',{name:/Refinar com o agente/i}).first();
  if (await btnChat.count()) { await btnChat.click({timeout:15000}).catch(()=>{}); await sleep(2000); }
  const caixa = p.getByPlaceholder(/mensagem|instru|refin/i).first();
  if (!await caixa.count()) { console.log('!! caixa da conversa não achada'); await b.close(); return; }
  await caixa.focus({timeout:15000});
  await p.keyboard.type('Nesta tela, mova o botao principal de acao para o TOPO do painel, '
    + 'acima dos campos, e renomeie-o para "Calcular agora".', {delay: 8});
  await sleep(800); await shot(p,'apontar-pedido-digitado');
  // Nesta conversa o Enter NÃO envia (a caixa é de texto livre): quem envia é o botão.
  const btnRefinar = p.getByRole('button',{name:/^Refinar$|Refinar$/i}).last();
  await btnRefinar.click({timeout:20000});
  console.log('▷ pedido enviado às', new Date().toLocaleTimeString());
  for (let i=0;i<60;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/Protótipo atualizado/i.test(t)) { console.log('✔ o protótipo se remontou sozinho'); break; }
    if (/Falha no refino/i.test(t)) { console.log('✘ falha no refino'); break; } }
  await sleep(3000); await shot(p,'apontar-depois');
  const depois = await q.locator('body').innerText().catch(()=>'');
  console.log('DEPOIS — tela mostra:', depois.replace(/\n/g,' · ').slice(0,200));
  console.log('mudou?', antes.slice(0,400) !== depois.slice(0,400) ? 'SIM' : 'não');
  await b.close();
})();
