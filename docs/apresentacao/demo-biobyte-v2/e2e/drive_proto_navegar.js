// Navega o protótipo fora do LangNet e fotografa telas escolhidas.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
let N = parseInt(process.argv[2] || '347', 10);
const BASE = process.argv[3];
const PAGS = process.argv.slice(4);
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1000}});
  for (const pg of PAGS) {
    await p.goto(`${BASE}/${pg}.html`,{waitUntil:'domcontentloaded'}); await sleep(1800);
    const f=`${OUT}/${String(N).padStart(3,'0')}-prototipo-${pg}.png`;
    await p.screenshot({path:f}); console.log('📸', f.split('/').pop()); N++;
  }
  await b.close();
})();
