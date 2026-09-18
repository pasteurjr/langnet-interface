// Refinamento pela tela: manda uma correção pontual no chat e acompanha.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '110', 10);
const PEDIDO = process.argv[3] || '';
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
  await p.goto(`${BASE}/project/${PROJ}/documents`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  // A tela abre SEM sessão selecionada ("Documento não gerado"), mesmo havendo análise pronta.
  // É preciso abrir o Histórico e escolher a sessão para o documento carregar e o chat se ligar
  // a ela — senão o pedido de refino não tem a que se referir.
  const hist = p.getByRole('button', { name: /hist[óo]rico/i }).first();
  if (await hist.count()) {
    await hist.click({ timeout: 15000, force: true }).catch(()=>{});
    await sleep(3000);
    await shot(p,'historico-de-analises');
    // O modal abre na lista de VERSÕES (vazia quando nenhuma sessão está escolhida). Primeiro
    // voltar para a lista de análises, depois escolher a mais recente.
    const voltar = p.getByRole('button', { name: /voltar para lista de documentos/i }).first();
    if (await voltar.count()) { await voltar.click({force:true}).catch(()=>{}); await sleep(2500); }
    await shot(p,'historico-lista-de-analises');
    const ok = await p.evaluate(()=>{
      const alvos=[...document.querySelectorAll('div,li,tr,button')]
        .filter(e=>/Document Analysis/i.test(e.textContent||'')
                   && (e.textContent||'').length < 200
                   && e.querySelectorAll('div,li,tr').length < 4);
      if(!alvos.length) return false;
      alvos[0].click(); return true;
    });
    console.log(ok ? 'sessão selecionada no histórico' : '!! nenhuma sessão clicável no histórico');
    await sleep(4000);
    // abrir a versão carrega o documento na tela principal e liga o chat a essa sessão
    const ver = p.getByText(/Clique para visualizar/i).first();
    if (await ver.count()) {
      await ver.click({ timeout: 15000, force: true }).catch(()=>{});
      console.log('versão aberta'); await sleep(4000);
    } else console.log('!! link de visualizar não encontrado');
    const fechar = p.getByRole('button', { name: /^fechar$/i }).first();
    if (await fechar.count()) { await fechar.click({force:true}).catch(()=>{}); await sleep(2500); }
  } else console.log('!! botão Histórico não encontrado');
  await shot(p,'documento-antes-do-refino');
  const cx = p.getByPlaceholder(/Digite sua mensagem para refinar/i).first();
  if (!(await cx.count())) { console.log('!! caixa de refino não encontrada'); await b.close(); return; }
  await cx.focus(); await p.keyboard.type(PEDIDO, {delay:2});
  await sleep(500); await shot(p,'pedido-de-correcao-escrito');
  // Clique de VERDADE: o clique feito por dentro da página não é registrado pelo React —
  // mesmo atrito já enfrentado no driver de criação do projeto.
  let env = false;
  const bt = p.getByRole('button', { name: /enviar/i }).last();
  if (await bt.count()) {
    await bt.scrollIntoViewIfNeeded().catch(()=>{});
    await bt.click({ timeout: 20000, force: true }).then(()=>{env=true})
      .catch(async e => { console.log('clique falhou:', String(e.message).split('\n')[0]);
                          await p.keyboard.press('Enter'); env = true; });
  }
  console.log(env ? 'pedido enviado' : '!! botão Enviar não encontrado');
  if(!env){ await b.close(); return; }
  await sleep(8000); await shot(p,'refino-em-andamento');
  // A comparação entre versões ABRE SOZINHA quando a resposta chega — por isso é preciso
  // FICAR na tela. Sair e voltar perde o momento (a comparação vem na mensagem do chat).
  for (let i=0; i<40; i++) {
    await sleep(6000);
    const pronto = await p.evaluate(()=>/Diferen|diff|refinad/i.test(document.body.innerText));
    if (pronto) break;
  }
  await sleep(3000);
  await shot(p,'comparacao-entre-versoes');
  const verDif = p.getByRole('button',{name:/ver diferen/i}).first();
  if (await verDif.count()) { await verDif.click({force:true}).catch(()=>{}); await sleep(3000);
                              await shot(p,'comparacao-aberta'); }
  console.log(await p.evaluate(()=>document.body.innerText.slice(0,400).replace(/\n+/g,' | ')));
  await b.close();
})();
