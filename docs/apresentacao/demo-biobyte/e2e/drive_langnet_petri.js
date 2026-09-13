// Etapa Rede de Petri: gera a rede e pede a revisão ao agente.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1480', 10);
const SO_REVISAR = process.argv[3] === 'revisar';
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
  await p.goto(`${BASE}/project/${PROJ}/petri-net`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  await shot(p,'petri-etapa-aberta');
  if (!SO_REVISAR) {
    const btn = p.getByRole('button',{name:/Gerar Rede/i}).last();
    if (!await btn.count()) { console.log('!! botão Gerar Rede não achado'); await b.close(); return; }
    await btn.click({timeout:20000});
    await sleep(3500);
    await shot(p,'petri-modal-origem');
    // O botão abre um MODAL de origem (arquivo de agentes + arquivo de tarefas + sequência).
    // Sem preenche-lo, nada e gerado — e a etapa segue mostrando a rede ANTIGA, o que parece
    // sucesso. Escolhe a opção mais recente de cada seletor (as listas vêm da mais nova).
    // Escolher por `sel.value = …` NÃO funciona aqui: o React não registra a mudança feita
    // por fora, o botão de confirmar continua desabilitado e NADA é gerado — a etapa segue
    // mostrando a rede antiga, o que parece sucesso. `selectOption` faz do jeito que o navegador
    // faria, e a tela reage.
    const seletores = p.locator('select');
    const qtd = await seletores.count();
    const escolhas = [];
    for (let i = 0; i < qtd; i++) {
      const s = seletores.nth(i);
      const ops = await s.locator('option').evaluateAll((os) =>
        os.filter((o) => o.value).map((o) => ({ v: o.value, t: (o.textContent || '').trim() })));
      if (!ops.length) { escolhas.push('(vazio)'); continue; }
      await s.selectOption(ops[0].v);
      escolhas.push(ops[0].t.slice(0, 42));
      await sleep(600);
    }
    console.log('origens escolhidas:', escolhas.join(' || '));
    await sleep(2000); await shot(p,'petri-origem-escolhida');
    // O botão de confirmar do modal se chama "Gerar Rede" — o MESMO nome do da barra. Clicar
    // "pelo nome" pegava o de fora e nada era gerado (a etapa seguia mostrando a rede antiga,
    // o que parece sucesso). Aciona o botão que está DENTRO do modal e está habilitado.
    // O botão de confirmar do modal se chama "Gerar Rede" — o MESMO nome do da barra. Pega-se o
    // que está ao lado do "Cancelar", que só existe dentro do modal.
    const confirmar = p.locator('button', { hasText: /^Gerar Rede$/ }).last();
    const habilitado = await confirmar.isEnabled().catch(() => false);
    console.log('botão de confirmar habilitado:', habilitado);
    if (!habilitado) { console.log('!! as origens não foram registradas'); await b.close(); return; }
    await confirmar.click({ timeout: 20000 });
    console.log('▷ geração disparada às', new Date().toLocaleTimeString());
    await sleep(5000); await shot(p,'petri-gerando');
    for (let i=0;i<150;i++){ await sleep(10000);
      const t = await p.evaluate(()=>document.body.innerText);
      if (!/Gerando|Processando/i.test(t) && /lugar|transi|Revisar/i.test(t)) break; }
    await sleep(3000); await shot(p,'petri-pronta');
  }
  // revisão pelo agente
  // "Revisar" pelo nome casava com o ícone de busca do cabeçalho (🔍). Pega o botão da etapa.
  // O botão existe e está habilitado, mas o clique do ponteiro estoura: ele fica coberto (é o
  // mesmo atrito visto na Especificação e na Interface). Aciona por dentro da página.
  const acionou = await p.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find(
      (x) => /Revisar/.test(x.textContent || '') && !/Refinar/.test(x.textContent || '') && !x.disabled);
    if (!b) return 'botão Revisar não achado';
    b.click(); return 'revisão acionada';
  });
  console.log(acionou);
  if (!/acionada/.test(acionou)) { await b.close(); return; }
  console.log('▷ revisão pedida às', new Date().toLocaleTimeString());
  for (let i=0;i<90;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/sugest|deadlock|cobertura|Revisão/i.test(t) && !/Revisando|Processando/i.test(t)) break; }
  await sleep(3000); await shot(p,'petri-revisao');
  const texto = await p.evaluate(()=>document.body.innerText);
  const i = texto.search(/sugest|revis[ãa]o/i);
  console.log('REVISÃO:', texto.slice(i, i+1200).replace(/\n{2,}/g,'\n'));
  await b.close();
})();
