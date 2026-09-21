// Etapa Agentes & Tarefas: escolhe a Especificação de origem, gera com as instruções que
// carregam as lições das rodadas anteriores, e captura cada momento para o roteiro.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '290', 10);
const BASE='http://localhost:3001';
const PROJ=fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};

const INSTRUCOES = [
'Um nome por dado em todo o documento: se o dado do usuário logado se chama usuario_id, ele se',
'chama usuario_id em toda tarefa e em todo agente — nunca id_usuario. Mesma regra para caso_id e',
'periodo_dias. Divergência de nome faz a tarefa recusar com o dado em mãos.',
'',
'Toda tarefa declara: quem executa (um agente), o que recebe, o que devolve e por qual passo cada',
'saída prometida é produzida. Saída prometida sem passo que a produza é defeito.',
'',
'Tarefa que chama serviço externo declara o serviço pelo nome e obedece à ficha dele: a consulta de',
'microbiologia e o escore de risco de Cox são servidos por MCP; o envio de e-mail também.',
'',
'Campo usado apenas dentro de uma condição não é entrada obrigatória da tarefa.',
'',
'Texto fixo vai entre aspas para não ser lido como dado a fornecer.',
'',
'Cada tarefa cita os requisitos funcionais e o caso de uso que atende.'
].join('\n');

(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,150));});
  let sess='';
  p.on('response',async r=>{const u=r.url();
    if(r.request().method()==='POST'&&/agent-task/.test(u)){try{const j=await r.json();if(j.session_id){sess=j.session_id;console.log('▷ sessão',sess,'status',r.status());}}catch(e){}}});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/agent-task`,{waitUntil:'domcontentloaded'});
  await sleep(6000);
  await shot(p,'ats-etapa-aberta');

  // origem: a Especificação
  const abrir = p.locator('button:has-text("Selecionar Especificação"), button[title="Selecionar Especificação Funcional Base"]').first();
  if (!await abrir.count()) { console.log('!! botão de origem não achado'); await b.close(); return; }
  await abrir.click(); await sleep(2500);
  await p.waitForSelector('.session-item',{timeout:15000}).catch(()=>{});
  await shot(p,'ats-escolhendo-a-especificacao');
  const itens = await p.locator('.session-item').evaluateAll(es=>es.map(e=>(e.innerText||'').replace(/\n/g,' | ').slice(0,90)));
  console.log('sessões de especificação:', JSON.stringify(itens));
  await p.locator('.session-item').first().click(); await sleep(2500);
  const vers = await p.locator('.session-item').evaluateAll(es=>es.map(e=>(e.innerText||'').replace(/\n/g,' | ').slice(0,90)));
  console.log('versões:', JSON.stringify(vers));
  if (vers.length) { await p.locator('.session-item').first().click(); await sleep(2500); }
  await p.keyboard.press('Escape').catch(()=>{}); await sleep(1200);
  await shot(p,'ats-origem-escolhida');
  console.log('base na tela:', (await p.evaluate(()=>document.body.innerText)).split('\n').filter(l=>/Base:/.test(l)).join(' / '));

  // instruções
  const ta = p.locator('textarea').first();
  if (await ta.count()) { await ta.click(); await ta.pressSequentially(INSTRUCOES,{delay:0}); await sleep(800); }
  else console.log('!! textarea de instruções não achado');
  await shot(p,'ats-instrucoes');

  const btn = p.getByRole('button',{name:/Gerar Agentes|Regenerar/i}).first();
  if (!await btn.count()) { console.log('!! botão Gerar não achado'); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ geração disparada às', new Date().toLocaleTimeString());
  await sleep(5000); await shot(p,'ats-gerando');
  for (let i=0;i<180;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/Nenhum Documento Gerado/.test(t)) continue;
    if (/Download|Visualizar|Exportar/i.test(t) && !/GERANDO DOCUMENTO/i.test(t)) break; }
  await sleep(2000); await shot(p,'ats-pronto');
  console.log('sessão gerada:', sess);
  console.log('final:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,400));
  await b.close();
})();
