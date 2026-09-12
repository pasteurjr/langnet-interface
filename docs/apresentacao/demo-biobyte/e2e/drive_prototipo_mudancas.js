// Mede O QUE de fato muda quando se pede pela conversa: acrescentar campo, reordenar, renomear.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1391', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};

const PEDIDOS = [
  {tag:'reordenar-2', txt:'Mova o campo "Codigo de 6 digitos" para ser o PRIMEIRO campo da tela, '
    + 'antes do e-mail e da senha.', procurar:null},
];

(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,90));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  const q = p.frameLocator('iframe[title="protótipo"]');
  const btnChat = p.getByRole('button',{name:/Refinar com o agente/i}).first();
  if (await btnChat.count()) { await btnChat.click({timeout:15000}).catch(()=>{}); await sleep(2000); }

  for (const ped of PEDIDOS) {
    const antes = await q.locator('body').innerText().catch(()=>'');
    const ordemAntes = (antes.match(/E-mail institucional|Senha|Código de 6 dígitos|Unidade/gi)||[]).join(' > ');
    const caixa = p.getByPlaceholder(/Refinar|mensagem|instru/i).first();
    if (!await caixa.count()) { console.log('!! caixa não achada'); break; }
    await caixa.focus({timeout:15000});
    await p.keyboard.type(ped.txt, {delay:6});
    await sleep(600);
    await p.getByRole('button',{name:/^Refinar$/i}).last().click({timeout:20000});
    console.log(`▷ [${ped.tag}] enviado`);
    let ok=false;
    for (let i=0;i<60;i++){ await sleep(10000);
      const t = await p.evaluate(()=>document.body.innerText);
      if (/Protótipo atualizado/i.test(t)) { ok=true; break; }
      if (/Falha no refino/i.test(t)) { console.log(`  [${ped.tag}] FALHA no refino`); break; } }
    await sleep(3000); await shot(p, `mudanca-${ped.tag}`);
    const depois = await q.locator('body').innerText().catch(()=>'');
    const ordemDepois = (depois.match(/E-mail institucional|Senha|Código de 6 dígitos|Unidade/gi)||[]).join(' > ');
    console.log(`  [${ped.tag}] remontou: ${ok?'sim':'não'}`);
    console.log(`     ordem antes : ${ordemAntes}`);
    console.log(`     ordem depois: ${ordemDepois}`);
    if (ped.procurar) console.log(`     apareceu o que foi pedido? ${ped.procurar.test(depois)?'SIM':'NÃO'}`);
  }
  await b.close();
})();
