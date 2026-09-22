// Refino do Modelo de Dados pela conversa da etapa, com captura.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '183', 10);
const PEDIDO = process.argv[3] || '';
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,90));});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/data-model`,{waitUntil:'domcontentloaded'});
  await sleep(9000);
  await shot(p,'dm-validacao-com-problemas');
  // "Refinar com o agente" abre a conversa da etapa
  const abrir = p.getByRole('button',{name:/refinar com o agente/i}).first();
  if (await abrir.count()) { await abrir.click({force:true}).catch(()=>{}); await sleep(3500); }
  // a caixa do chat desta etapa não tem rótulo previsível: pega a área de texto visível
  // que NÃO é a de "Instruções Adicionais" da configuração
  // A caixa certa é a do painel "Refinar via chat" (placeholder "Ex: adicione tabela ...").
  // A caixa "Instruções Adicionais" da coluna da esquerda serve para REGERAR DO ZERO — foi
  // onde o texto caiu na primeira tentativa, e nada foi enviado.
  let cx = p.getByPlaceholder(/adicione tabela|remova campo|coloque [íi]ndice/i).first();
  if (!(await cx.count())) cx = p.getByPlaceholder(/^Ex:/i).last();
  if (!(await cx.count())) {
    console.log('!! caixa de mensagem não encontrada; botões:',
      await p.evaluate(()=>[...document.querySelectorAll('button')].map(b=>(b.textContent||'').trim()).filter(Boolean).slice(0,20).join(' | ')));
    await b.close(); return;
  }
  await cx.focus(); await p.keyboard.type(PEDIDO,{delay:2});
  await sleep(600); await shot(p,'dm-pedido-de-correcao');
  const enviou = await p.evaluate(()=>{
    const bs=[...document.querySelectorAll('button')].filter(x=>/^enviar$/i.test((x.textContent||'').trim()) && !x.disabled);
    if(!bs.length) return false; bs[bs.length-1].click(); return true;});
  if(!enviou){ console.log('!! botão Enviar indisponível — nada foi enviado'); await b.close(); return; }
  console.log('enviado de fato');
  console.log('▷ refino disparado às', new Date().toLocaleTimeString());
  await sleep(8000); await shot(p,'dm-refino-em-andamento');
  for (let i=0;i<60;i++){
    await sleep(15000);
    const t=await p.evaluate(()=>document.body.innerText);
    if (/Vers[ãa]o v?2|refinad|conclu/i.test(t)) { console.log('▷ concluído'); break; }
  }
  await sleep(3000); await shot(p,'dm-refino-concluido');
  await b.close();
})();
