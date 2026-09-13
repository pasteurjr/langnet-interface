// Etapa Sequência de Tarefas: escolhe os YAML de origem e gera o fluxo.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1460', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
const clicarTexto = (p, re) => p.evaluate((fonte) => {
  const rx = new RegExp(fonte, 'i');
  const a = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && rx.test(e.textContent || ''));
  if (!a) return 'não achei: ' + fonte;
  (a.closest('[class*=card],[class*=item],a,button,div[role=button],div') || a).click();
  return 'cliquei: ' + (a.textContent || '').trim().replace(/\s+/g,' ').slice(0, 55);
}, re);
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,100));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/task-execution-flow`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  await shot(p,'seq-etapa-aberta');
  // A etapa exige TRÊS documentos de origem (especificação + os dois YAML): o botão é "Specs & Docs".
  const btnY = p.getByRole('button',{name:/Specs & Docs/i}).first();
  if (!await btnY.count()) { console.log('!! botão Specs & Docs não achado'); await b.close(); return; }
  await btnY.click({timeout:15000}); await sleep(3500);
  await shot(p,'seq-modal-origem');
  const lista = await p.evaluate(() => [...document.querySelectorAll('*')]
    .filter(e => e.children.length === 0 && /Especifica|agents|tasks|YAML|Agentes/i.test(e.textContent || ''))
    .map(e => (e.textContent || '').trim().replace(/\s+/g,' ').slice(0, 46)).slice(0, 14));
  console.log('no modal:', lista.join(' || '));
  // O modal tem TRÊS ABAS (Especificação Funcional · Especificação de Agentes/Tarefas · Tasks YAML)
  // e pede um cartão em cada. O rodapé conta "x de 3 selecionados".
  const abas = [
    { aba: /Especificação Funcional/i, cartao: 'DeepSeek flash' },   // a que tem a correção do usuário
    { aba: /Especificação de Agent/i,  cartao: null },               // o mais recente
    { aba: /Tasks YAML/i,              cartao: null },
  ];
  for (const alvo of abas) {
    const t = p.getByRole('tab', { name: alvo.aba }).first();
    const t2 = (await t.count()) ? t : p.locator('button,div[role=button],li,a').filter({ hasText: alvo.aba }).first();
    if (await t2.count()) { await t2.click({ timeout: 12000 }).catch(() => {}); await sleep(2500); }
    const r = await p.evaluate((nome) => {
      const modal = [...document.querySelectorAll('*')].find(
        (e) => /Selecionar Specs & Docs/i.test(e.textContent || '') && e.querySelectorAll('*').length < 400);
      const raiz = modal || document;
      // O cartão é o MENOR elemento que contém "CRIADO EM" — o filtro anterior pegava o corpo do
      // modal inteiro numa das abas, e clicar nele não selecionava nada (ficava "2 de 3").
      const candidatos = [...raiz.querySelectorAll('*')].filter(
        (e) => /CRIADO EM/i.test(e.textContent || '') && (!nome || (e.textContent || '').includes(nome)));
      if (!candidatos.length) return 'sem cartões nesta aba';
      candidatos.sort((a, c) => a.querySelectorAll('*').length - c.querySelectorAll('*').length);
      const alvo = candidatos[0];
      alvo.click();
      return 'escolhi: ' + (alvo.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 48);
    }, alvo.cartao);
    console.log('  ', r); await sleep(2000);
    // CONFERE: clicar no cartão nem sempre registra a escolha (o contador do rodapé é a verdade).
    // Sem esta conferência, o driver seguia com "2 de 3" e o botão de gerar ficava desabilitado.
    const conta = () => p.evaluate(() => {
      const e = [...document.querySelectorAll('*')].find(
        (x) => x.children.length === 0 && /de 3 selecionados/i.test(x.textContent || ''));
      return e ? parseInt((e.textContent || '0').trim(), 10) || 0 : -1;
    });
    let n = await conta();
    if (n < abas.indexOf(alvo) + 1) {
      const r2 = await p.evaluate((nome) => {
        const cartoes = [...document.querySelectorAll('*')].filter(
          (e) => /CRIADO EM/i.test(e.textContent || '') && e.querySelectorAll('*').length < 25);
        const alvo = nome ? cartoes.find((c) => (c.textContent || '').includes(nome)) : cartoes[0];
        if (!alvo) return 'sem cartão para repetir';
        const alvo2 = alvo.querySelector('*') || alvo;
        alvo2.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
        return 'repeti o clique';
      }, alvo.cartao);
      await sleep(2000); n = await conta();
      console.log('    (o clique não registrou —', r2, '→ agora', n, 'de 3)');
    }
  }
  console.log('  contador final:', await p.evaluate(() => {
    const e = [...document.querySelectorAll('*')].find(
      (x) => x.children.length === 0 && /de 3 selecionados/i.test(x.textContent || ''));
    return e ? (e.textContent || '').trim() : '(sem contador)';
  }));
  const conf = p.getByRole('button', { name: /Selecione os 3 Documentos|Confirmar|Aplicar/i }).first();
  if (await conf.count()) { await conf.click({ timeout: 12000 }).catch(() => {}); }
  await sleep(3000);
  await shot(p,'seq-origem-escolhida');
  const btn = p.getByRole('button',{name:/Gerar Sequência de Tarefas/i}).first();
  if (!await btn.count()) { console.log('!! botão Gerar não achado'); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ geração disparada às', new Date().toLocaleTimeString());
  await sleep(5000); await shot(p,'seq-gerando');
  for (let i=0;i<150;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (!/Gerando|Processando/i.test(t) && /transi|sequ[êe]ncia|fluxo|tarefa/i.test(t)) break; }
  await sleep(3000); await shot(p,'seq-pronto');
  await b.close();
})();
