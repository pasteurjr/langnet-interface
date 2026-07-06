/**
 * Após ter uma sessão gerada, entra na UI e captura as 5 abas
 * mostrando o Data Model montado pra Quântica.
 */
import { test } from '@playwright/test';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/langnet-ui-e2e/screenshots';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';

test('Capturar Data Model montado na UI', async ({ page }) => {
  test.setTimeout(180_000);

  await page.goto(APP);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForTimeout(4000);

  await page.goto(`${APP}/project/${PROJECT_ID}/data-model`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(8000);
  await page.screenshot({ path: `${OUT}/dm-01-entidades.png`, fullPage: true });
  console.log('URL:', page.url());
  const chars = await page.evaluate(() => (document.body.textContent || '').length);
  console.log('chars:', chars);

  // Captura cada aba
  for (const [id, label] of [['sql', 'Schema SQL'], ['models', 'models.py'], ['alembic', 'Alembic'], ['yaml', 'YAML']] as const) {
    try {
      await page.getByRole('button', { name: label }).click({ timeout: 3000 });
      await page.waitForTimeout(1500);
      await page.screenshot({ path: `${OUT}/dm-02-${id}.png`, fullPage: true });
      console.log(`  ✓ Aba ${label}`);
    } catch (e: any) {
      console.log(`  ✗ Aba ${label}: ${e.message.slice(0, 80)}`);
    }
  }

  // Volta pra entidades e captura numero de tabelas
  await page.getByRole('button', { name: 'Entidades' }).click().catch(() => {});
  await page.waitForTimeout(1000);
  const info = await page.evaluate(() => {
    const cards = document.querySelectorAll('.dm-table-card');
    const names = Array.from(cards).map(c => (c.querySelector('h3')?.textContent || '').trim());
    return { count: cards.length, names };
  });
  console.log('Tabelas na tela:', info.count);
  console.log('Nomes:', info.names.slice(0, 30));
});
