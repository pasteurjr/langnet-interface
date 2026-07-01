import { test } from '@playwright/test';
import * as fs from 'fs';

test('Inspect state após passos', async ({ page }) => {
  test.setTimeout(500_000);

  await page.goto('http://localhost:3001');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.evaluate(() => {
    const card = document.querySelector('div[style*="cursor: pointer"]') as HTMLElement | null;
    card?.click();
  });
  await page.waitForTimeout(2500);

  async function clickNext() {
    await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button')).find((b) =>
        /próximo passo/i.test((b.textContent || '').trim())
      ) as HTMLButtonElement | undefined;
      btn?.click();
    });
  }

  // Instrumentar o simulator: expor globalmente
  await page.evaluate(() => {
    // O hook expõe _simulator via retorno, mas MainExecutor não expõe global.
    // Vou pegar via React fiber
    console.log('[inspect] setup');
  });

  console.log('>>> Passo 1');
  await clickNext();
  await page.waitForTimeout(100000);

  const snap1 = await page.evaluate(() => {
    // Descobre a instância do simulator pesquisando em qualquer <div> do MainExecutor
    // Não é fácil sem exposição. Vamos usar heurística: verificar bodyText pra tokens em P_T001
    const t = document.body.textContent || '';
    const m = t.match(/P_T001[^t]*tokens?:\s*(\d+)/);
    return t.match(/P_T001[^\n]*/)?.[0] || 'not found';
  });
  console.log('após P1 — P_T001 line:', snap1);

  console.log('>>> Passo 2');
  await clickNext();
  await page.waitForTimeout(15000);  // 15s pro intermediário rodar
  console.log('>>> Passo 3');
  await clickNext();
  await page.waitForTimeout(15000);

  // Vou capturar via window object se conseguir
  const state = await page.evaluate(() => {
    // Procura pelo simulator na árvore React
    const root = document.getElementById('root');
    // Usar hackage: passa por todos os React fibers pra encontrar
    function findFiber(node: any): any {
      const key = Object.keys(node).find(k => k.startsWith('__reactFiber'));
      return key ? node[key] : null;
    }
    // Alternativa: consulta outputs via texto na tela — não visível.
    // Tenta expor via console DIRETO — precisa modificar código.
    return { note: 'sem acesso direto ao simulator do fora' };
  });
  console.log('state:', JSON.stringify(state));

  console.log('>>> Passo 4');
  await clickNext();
  await page.waitForTimeout(120000);

  // Salva HTML final pra análise
  const html = await page.content();
  fs.writeFileSync('/tmp/petri-final-html.html', html);
});
