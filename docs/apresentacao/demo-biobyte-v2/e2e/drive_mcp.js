// Atribui os serviços externos (MCP) ao projeto, pela interface.
// Sem isso, o gerador não lê as fichas dos serviços na hora de escrever o código — foi
// exatamente esse o buraco que fez o aplicativo chamar o serviço externo com argumento errado.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '14', 10);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const BASE='http://localhost:3001';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,110));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/mcp`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  await shot(p,'servicos-externos-antes');
  // habilita SÓ os dois servidores deste projeto: laboratório+Cox e notificação por e-mail.
  // Os demais (IBGE, CRM, Fetch) são de outros projetos e ficam de fora de propósito.
  const ALVOS = [/Integra[çc][õo]es \(LIS \+ Cox\)/i, /Notifica[çc][õo]es \(E-?mail\)/i];
  for (const alvo of ALVOS) {
    const feito = await p.evaluate((fonte)=>{
      const re = new RegExp(fonte.slice(1, fonte.lastIndexOf('/')), 'i');
      for (const bt of document.querySelectorAll('button')) {
        if (!/habilitar/i.test(bt.textContent||'')) continue;
        const cartao = bt.closest('div');
        const volta = cartao && cartao.parentElement ? cartao.parentElement.textContent : '';
        if (re.test((cartao?.textContent||'') + ' ' + volta)) { bt.click(); return true; }
      }
      return false;
    }, alvo.toString());
    console.log(feito ? 'habilitado: '+alvo : '!! não achei: '+alvo);
    await sleep(2500);
  }
  await sleep(3000);
  await shot(p,'servicos-externos-habilitados');
  const sugerir = await p.evaluate(()=>{const b=[...document.querySelectorAll('button')].find(e=>/sugerir atribui/i.test(e.textContent||'')); if(!b||b.disabled) return false; b.click(); return true;});
  console.log(sugerir ? 'atribuição de ferramentas aos agentes solicitada' : 'botão de sugerir indisponível');
  await sleep(6000);
  await shot(p,'ferramentas-atribuidas');
  console.log('--- tela final ---');
  console.log(await p.evaluate(()=>document.body.innerText.slice(0,900)));
  await b.close();
})();
