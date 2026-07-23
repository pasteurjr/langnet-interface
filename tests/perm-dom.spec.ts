import { test } from '@playwright/test';
test('dom', async ({ page }) => {
  await page.goto('http://localhost:3001', { waitUntil:'networkidle', timeout:30000 }).catch(()=>{});
  await page.waitForTimeout(2500);
  await page.getByText('Gerenciamento de Permissões', {exact:false}).first().click().catch(()=>{});
  await page.waitForTimeout(2500);
  const buttons = await page.locator('button').allInnerTexts();
  console.log('BOTOES NO DOM:', JSON.stringify(buttons));
  const salvar = await page.getByRole('button', {name:'Salvar'}).count();
  console.log('botao Salvar presente?', salvar);
});
