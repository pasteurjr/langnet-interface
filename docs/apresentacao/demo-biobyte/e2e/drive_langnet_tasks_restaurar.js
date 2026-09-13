// Torna vigente uma versão do histórico do contrato de tarefas, pela interface.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1560', 10);
const VERSAO = process.argv[3] || '4';
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
  await p.evaluate(() => {
    const a=[...document.querySelectorAll('button,div[role=button],li,a,span')].find(
      e=>/Tasks\s*YAML/i.test(e.textContent||'') && e.querySelectorAll('*').length<4);
    if(a) (a.closest('button,div[role=button],li,a')||a).click();
  });
  await sleep(3500);
  const hist = p.getByRole('button',{name:/Histórico/i}).first();
  if (await hist.count()) { await hist.click({timeout:12000}).catch(()=>{}); await sleep(3500); }
  await p.evaluate(() => {
    const l=[...document.querySelectorAll('*')].filter(e=>/CRIADO EM|Criado em/i.test(e.textContent||'') && e.querySelectorAll('*').length<12);
    if(l.length) l[0].click();
  });
  await sleep(3500);
  await shot(p,'restaurar-historico');
  // escolhe a versão pedida pelo número
  const escolheu = await p.evaluate((v) => {
    const alvos = [...document.querySelectorAll('*')].filter(
      (e) => e.textContent && e.textContent.indexOf('Versão ' + v) >= 0 && e.querySelectorAll('*').length < 20);
    if (!alvos.length) return 'versão ' + v + ' não achada';
    const alvo = alvos[alvos.length - 1];
    const link = [...alvo.querySelectorAll('*')].find(
      (e) => /Clique para carregar/i.test(e.textContent || '') && e.children.length === 0);
    (link ? (link.closest('a,button,div[role=button],div') || link) : alvo).click();
    return 'carreguei a versão ' + v;
  }, VERSAO);
  console.log(escolheu); await sleep(6000);
  const fechar = p.getByRole('button',{name:/^Fechar$/i}).first();
  if (await fechar.count()) { await fechar.click({timeout:8000}).catch(()=>{}); await sleep(2500); }
  await shot(p,'restaurar-versao-carregada');
  console.log('estado do botão:', await p.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find((x) => /Tornar vigente/i.test(x.textContent || ''));
    return b ? { texto: (b.textContent || '').trim(), desabilitado: b.disabled } : 'não existe';
  }));
  const botao = p.getByRole('button',{name:/Tornar vigente/i}).first();
  if (!await botao.count()) { console.log('!! botão Tornar vigente não achado'); await b.close(); return; }
  await botao.click({timeout:15000}).catch(async()=>{
    await p.evaluate(()=>{const x=[...document.querySelectorAll('button')].find(e=>/Tornar vigente/i.test(e.textContent||'')); if(x) x.click();});
  });
  await sleep(8000);
  await shot(p,'restaurado');
  const t = await p.evaluate(()=>document.body.innerText);
  const i = t.search(/vigente|restaur|Não deu/i);
  console.log('RESULTADO:', t.slice(i, i+300).replace(/\n{2,}/g,'\n'));
  await b.close();
})();
