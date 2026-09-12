// Etapa YAML: gera agents.yaml e tasks.yaml a partir do documento de Agentes & Tarefas escolhido.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1426', 10);
const ABA = (process.argv[3] || 'agents');  // agents | tasks
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
  await p.goto(`${BASE}/project/${PROJ}/yaml-generation`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  // aba
  const aba = p.getByRole('button',{name: ABA==='tasks' ? /Tasks YAML/i : /Agents YAML/i}).first();
  if (await aba.count()) { await aba.click({timeout:15000}).catch(()=>{}); await sleep(2500); }
  await shot(p,`yaml-${ABA}-aberta`);
  // origem: documento de agentes e tarefas (o mais recente concluído)
  const btnOrigem = p.getByRole('button',{name:/Especifica|Origem|Documento|Selecionar/i}).first();
  if (await btnOrigem.count()) { await btnOrigem.click({timeout:15000}).catch(()=>{}); await sleep(3000); }
  await shot(p,`yaml-${ABA}-modal-origem`);
  // O modal desta etapa lista por nome/data/contagem ("14 agentes, 15 tarefas") e tem DOIS
  // passos: "Clique para ver versões" no cartão e depois "Clique para carregar" na versão.
  const escolhido = await p.evaluate(() => {
    const links = [...document.querySelectorAll('*')].filter(
      (e) => e.children.length === 0 && /Clique para ver vers/i.test(e.textContent || ''));
    if (!links.length) return 'nenhum cartão de origem';
    const cartao = links[0].closest('[class*=card], [class*=item], div');
    const rotulo = cartao ? (cartao.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 60) : '';
    links[0].click();
    return 'cartão mais recente: ' + rotulo;
  });
  console.log(escolhido); await sleep(3000);
  const carregar = await p.evaluate(() => {
    // Nesta etapa a versão NÃO tem link "carregar": escolhe-se clicando no próprio cartão dela.
    const link = [...document.querySelectorAll('*')].find(
      (e) => e.children.length === 0 && /Clique para carregar|Clique para visualizar/i.test(e.textContent || ''));
    if (link) { (link.closest('a,button,div[role=button],div') || link).click(); return 'versão carregada (link)'; }
    const versao = [...document.querySelectorAll('*')].find(
      (e) => e.children.length === 0 && /^Vers[ãa]o\s*\d+/i.test((e.textContent || '').trim()));
    if (!versao) return 'sem versão na lista';
    (versao.closest('[class*=card], [class*=item], div[role=button], div') || versao).click();
    return 'versão escolhida pelo cartão';
  });
  console.log(carregar); await sleep(3000);
  await shot(p,`yaml-${ABA}-origem-escolhida`);
  const btn = p.getByRole('button',{name: ABA==='tasks' ? /Gerar tasks\.yaml/i : /Gerar agents\.yaml/i}).first();
  if (!await btn.count()) { console.log('!! botão Gerar não achado'); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ geração disparada às', new Date().toLocaleTimeString());
  await sleep(5000); await shot(p,`yaml-${ABA}-gerando`);
  for (let i=0;i<180;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/agent|task/i.test(t) && !/Gerando|Processando/i.test(t)) break; }
  await sleep(3000); await shot(p,`yaml-${ABA}-pronto`);
  await b.close();
})();
