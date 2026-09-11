// Abre a Especificação nova, captura, e pede o refino pela CONVERSA da etapa (cena-chave do vídeo:
// a correção que o usuário faz na especificação desce pelo pipeline).
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1330', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,150));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/spec`,{waitUntil:'domcontentloaded'});
  await sleep(6000);
  await shot(p,'spec-nova-aberta');
  // rola até o caso de uso do escore de Cox, para o vídeo mostrar o croqui ANTES
  await p.evaluate(()=>{const el=[...document.querySelectorAll('*')].find(e=>/Calcular Escore de Risco/i.test(e.textContent||'')&&e.children.length===0);el&&el.scrollIntoView({block:'center'});});
  await sleep(1500); await shot(p,'spec-croqui-cox-antes');

  // A caixa da conversa é a do texto de apoio "Digite sua mensagem". Pegar "a última caixa da
  // página" deixou de funcionar quando a etapa passou a abrir já com o documento carregado.
  const caixa = p.getByPlaceholder(/Digite sua mensagem/i).first();
  const msg = 'No caso de uso UC-004 (Calcular Escore de Risco com Modelo de Cox), o croqui da tela '
            + 'ainda nao mostra o APACHE II. Acrescente o campo "APACHE II (0-71)" no desenho da tela, '
            + 'junto de Idade e Tempo de Cateter, e cite-o no passo do fluxo principal em que o medico '
            + 'revisa as covariaveis. Nao mude mais nada do documento.';
  if (await caixa.count()) {
    // fecha qualquer janela sobreposta antes de escrever (clique forçado já abriu o modal de
    // comparação por engano) e volta ao topo — rolar até o croqui tira a caixa da área clicável
    await p.keyboard.press('Escape').catch(()=>{});
    await p.evaluate(()=>window.scrollTo(0,0)); await sleep(1000);
    await caixa.scrollIntoViewIfNeeded({timeout:15000}).catch(()=>{});
    // `click` estoura: o painel do documento cobre a caixa para efeito de ponteiro. `focus` não
    // depende disso, e digitar pelo teclado gera os mesmos eventos que a tela espera.
    await caixa.focus({timeout:15000});
    await p.keyboard.type(msg, {delay: 8});
    await sleep(800); await shot(p,'spec-refino-digitado');
    const escrito = await caixa.inputValue().catch(()=>'');
    console.log('texto na caixa:', escrito.length, 'chars');
    if (escrito.length < 20) { console.log('!! o texto nao entrou na caixa'); await b.close(); return; }
    // O botão "Refinar" é o envio do formulário da conversa: Enter na caixa faz o mesmo, e não
    // esbarra no painel do documento que cobre o botão para efeito de ponteiro.
    const btn = p.getByRole('button',{name:/Refinar/i}).first();
    if (await btn.count()) {
      await p.keyboard.press('Enter');
      console.log('▷ refino pedido às', new Date().toLocaleTimeString());
      await sleep(4000); await shot(p,'spec-refino-processando');
      for (let i=0;i<90;i++){ await sleep(10000);
        const t = await p.evaluate(()=>document.body.innerText);
        if (/APACHE II \(0-71\)|APACHE II \(0–71\)/i.test(t)) { console.log('✔ APACHE apareceu na tela'); break; } }
      await sleep(2000); await shot(p,'spec-refino-pronto');
    } else console.log('!! botão Refinar não achado');
  } else console.log('!! caixa de mensagem não achada');
  await b.close();
})();
