import { test } from '@playwright/test';
test('perm', async ({ page }) => {
  test.setTimeout(60000);
  await page.setViewportSize({ width: 1500, height: 950 });
  await page.goto('http://localhost:3001', { waitUntil:'networkidle', timeout:45000 }).catch(()=>{});
  await page.waitForTimeout(3000);
  await page.getByText('Gerenciamento de Permissões', {exact:false}).first().click().catch(()=>{});
  await page.waitForTimeout(3000);
  await page.screenshot({path:'/tmp/uso-solo-pipeline/shots-f0/03-permissoes-com-botao.png', fullPage:false});
  console.log('[shot] permissoes re-capturado');
});
