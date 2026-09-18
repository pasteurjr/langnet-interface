// Etapa 1 — gera o documento de Requisitos a partir da ata anexada.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '8', 10);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const BASE='http://localhost:3001';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
const INSTRUCAO = 'Este documento é a ata de uma reunião de levantamento com a Comissão de Controle de Infecção Hospitalar. Extraia os requisitos funcionais e não funcionais EXATAMENTE do que foi dito pelos participantes, sem inventar funcionalidade que ninguém pediu. Atenção especial: (1) os requisitos de segurança devem nomear o mecanismo — HTTPS, token conferido no servidor a cada requisição, senha com resumo criptográfico, autorização por papel, credencial fora do código; (2) o login é simples, com e-mail e senha, SEM verificação em duas etapas; (3) registre como requisito que a sessão do usuário vale em todas as telas, sem pedir identificação de novo; (4) registre o que os participantes disseram sobre o que os serviços externos NÃO devolvem.';
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,110));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/documents`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  // escreve as instruções para a análise
  const cx = p.getByPlaceholder(/Focar em requisitos|instru/i).first();
  if (await cx.count()) { await cx.focus(); await p.keyboard.type(INSTRUCAO, {delay:2}); console.log('instruções escritas'); }
  else console.log('!! caixa de instruções não achada');
  await sleep(600);
  await shot(p,'instrucoes-e-pesquisa-web');
  const iniciou = await p.evaluate(()=>{const b=[...document.querySelectorAll('button')].find(e=>/iniciar an[áa]lise/i.test(e.textContent||'')&&!e.disabled);
    if(!b) return 'botão Iniciar Análise indisponível'; b.click(); return 'análise iniciada';});
  console.log(iniciou);
  if (!/iniciada/.test(iniciou)) { await b.close(); return; }
  await sleep(6000); await shot(p,'analise-em-andamento');
  await b.close();
})();
