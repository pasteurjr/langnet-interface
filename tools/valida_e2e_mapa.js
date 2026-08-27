const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/validacao-ui-rica/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  let wsMsgs=[];
  p.on('websocket', ws=>{ ws.on('framesent',f=>wsMsgs.push('→'+String(f.payload).slice(0,80))); ws.on('framereceived',f=>wsMsgs.push('←'+String(f.payload).slice(0,120))); });
  await p.goto('http://127.0.0.1:3900/', {waitUntil:'networkidle'}); await sleep(2000);
  await p.locator('text=/Consulta de Regramentos/i').first().click(); await sleep(4000);
  const map = p.locator('.leaflet-container').first();
  const box = await map.boundingBox();
  console.log('mapa box:', box ? 'ok' : 'NAO ACHOU');
  // clica a ferramenta RETANGULO
  const rect = p.locator('.leaflet-draw-draw-rectangle').first();
  console.log('botao retangulo:', await rect.count());
  await rect.click(); await sleep(600);
  // desenha o retangulo: drag do centro-esq ao centro-dir
  const x0=box.x+box.width*0.35, y0=box.y+box.height*0.35, x1=box.x+box.width*0.65, y1=box.y+box.height*0.65;
  await p.mouse.move(x0,y0); await p.mouse.down(); await p.mouse.move(x1,y1,{steps:12}); await p.mouse.up();
  await sleep(1200);
  const capt = await p.locator('text=/Geometria capturada/i').count();
  console.log('geometria capturada no UI:', capt>0);
  await p.screenshot({path:`${OUT}/e2e-1-desenhado.png`});
  // clica Nova Consulta
  await p.locator('button', {hasText:/Nova Consulta|Consultar/i}).first().click();
  console.log('▷ consulta enviada; aguardando resposta...');
  // espera o painel de resultado mostrar as regras
  let ok=false;
  for(let i=0;i<20;i++){ await sleep(1500);
    const txt = await p.locator('body').innerText();
    if(/ZUR-1|Licenca ambiental|Estudo de Impacto|recuo frontal|lista_regras|sucesso/i.test(txt)){ ok=true; break; }
  }
  console.log('RESULTADO no painel:', ok);
  await p.screenshot({path:`${OUT}/e2e-2-resultado.png`});
  // extrai o texto do painel de resultado
  const panel = await p.locator('pre').first().innerText().catch(()=>'(sem pre)');
  console.log('PAINEL:', panel.slice(0,400).replace(/\s+/g,' '));
  console.log('WS:', wsMsgs.slice(0,4).join(' | '));
  await b.close(); console.log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message); process.exit(1);});
