import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://pasteurjr.servehttp.com:8085/crm/';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/crm-serrinha';

test('CRM - sniff completo', async ({ page }) => {
  test.setTimeout(180_000);

  const responses: any[] = [];

  page.on('response', async (r) => {
    const u = r.url();
    // pula estáticos óbvios (imagens/css)
    if (/\.(png|jpg|jpeg|gif|svg|ico|css|woff2?|ttf)/i.test(u)) return;
    try {
      const status = r.status();
      const ct = r.headers()['content-type'] || '';
      const body = await r.text();
      if (body.length > 100) {
        responses.push({
          url: u,
          status,
          ct,
          size: body.length,
          body,
        });
      }
    } catch {}
  });

  await page.goto(APP);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('input[type="text"]').first().fill('admin');
  await page.locator('input[type="password"]').first().fill('teste');
  await page.getByText(/^Entrar$/).click().catch(() => page.keyboard.press('Enter'));
  await page.waitForTimeout(6000);

  // Interação intensa
  const clicks = [
    [50, 30], [50, 52], [50, 128], [772, 408], [1160, 6],
    [908, 682], [962, 682], [1033, 682], [676, 175], [1209, 175]
  ];
  for (const [x, y] of clicks) {
    await page.mouse.click(x, y);
    await page.waitForTimeout(1200);
  }

  console.log(`\n=== ${responses.length} respostas capturadas ===`);
  responses.slice(0, 20).forEach((r, i) => {
    const short = r.url.slice(r.url.indexOf('/crm/') + 5, r.url.indexOf('/crm/') + 100);
    console.log(`  ${i+1}. ${r.status} ${r.size}b [${r.ct.slice(0,40)}] .../${short}`);
  });

  // Salva JSON+XML+HTML responses grandes
  fs.writeFileSync(`${OUT}/all-responses.json`, JSON.stringify(
    responses.map(r => ({url: r.url, status: r.status, ct: r.ct, size: r.size})), null, 2
  ));

  // Junta bodies não binários
  const bigBodies = responses.filter(r => r.size > 500).map(r => r.body).join('\n');
  fs.writeFileSync(`${OUT}/all-bodies.txt`, bigBodies);
  console.log(`\nTotal chars: ${bigBodies.length}`);

  // Extrai strings pt-BR e nomes de classe/componente
  const ptWords = Array.from(new Set(
    (bigBodies.match(/[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+(?:\s[A-ZÁÉÍÓÚÂÊÔÃÕÇa-záéíóúâêôãõç]+){0,4}/g) || [])
      .filter(w => w.length > 4 && w.length < 40)
  ));
  const compNames = Array.from(new Set(
    (bigBodies.match(/br\.intertrack[\w\.$]+/g) || [])
  ));
  const menuLike = Array.from(new Set(
    (bigBodies.match(/"caption":"[^"]{2,60}"/g) || []).map(s => s.replace('"caption":"','').replace('"',''))
  ));

  const summary = {
    responses_count: responses.length,
    total_chars: bigBodies.length,
    pt_words_sample: ptWords.slice(0, 100),
    intertrack_classes: compNames,
    captions: menuLike,
  };
  fs.writeFileSync(`${OUT}/sniff-summary.json`, JSON.stringify(summary, null, 2));

  console.log('\n=== CAPTIONS ===');
  menuLike.slice(0, 60).forEach(c => console.log(' •', c));
  console.log('\n=== CLASSES br.intertrack ===');
  compNames.forEach(c => console.log(' •', c));
});
