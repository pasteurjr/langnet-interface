// Corrige a regra pendente da etapa Ferramentas pela conversa com o agente.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1418', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,100));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/tools-stage`,{waitUntil:'domcontentloaded'});
  await sleep(6000);
  // seleciona a ferramenta pendente para o pedido chegar endereçado
  const linha = p.locator('tr, li, div').filter({hasText:/json_parser_tool/i}).first();
  if (await linha.count()) { await linha.click({timeout:15000}).catch(()=>{}); await sleep(2000); }
  await shot(p,'ferr-pendencia-antes');
  const caixa = p.getByPlaceholder(/validação de senha é determinística/i).first();
  if (!await caixa.count()) { console.log('!! caixa da conversa não achada'); await b.close(); return; }
  await caixa.focus({timeout:15000});
  await p.keyboard.type(process.argv[3] || 'sem instrucao', {delay:6});
  await sleep(600); await shot(p,'ferr-pedido-digitado');
  await p.getByRole('button',{name:/^Enviar$/i}).first().click({timeout:20000});
  console.log('▷ pedido enviado às', new Date().toLocaleTimeString());
  for (let i=0;i<60;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/vira código na geração|Processando/i.test(t) === false && /json_parser_tool/i.test(t)) {
      if (!/Processando|Refinando/i.test(t)) break; } }
  await sleep(4000); await shot(p,'ferr-pendencia-depois');
  await b.close();
})();
