import { test, expect } from '@playwright/test';
const OUT='/tmp/uso-solo-pipeline/shots-crud';
const EMP = ["MedAI Diagnósticos","https://medai.com.br","42.318.900/0001-55","HealthTech / Diagnóstico por Imagem","São Paulo, SP","120","LinkedIn Sales Navigator"];
test('crud empresa', async ({ page }) => {
  test.setTimeout(90000);
  await page.setViewportSize({ width: 1500, height: 1000 });
  await page.goto('http://localhost:3001', { waitUntil:'networkidle', timeout:45000 }).catch(()=>{});
  await page.waitForTimeout(3500);
  // clica o item de menu e espera o título mudar
  await page.getByText('Empresas Alvo', {exact:false}).first().click();
  await page.getByRole('heading', { name: 'Empresas Alvo' }).first().waitFor({ timeout: 6000 });
  await page.waitForTimeout(1000);
  await page.screenshot({ path:`${OUT}/01-empresas-lista-vazia.png` });
  await page.getByText('＋ Novo', {exact:false}).first().click();
  await page.waitForTimeout(1200);
  const ctrls = page.locator('input:visible, textarea:visible');
  for (let i=0; i<EMP.length; i++) await ctrls.nth(i).fill(EMP[i]);
  await page.waitForTimeout(500);
  await page.screenshot({ path:`${OUT}/02-empresa-form.png` });
  await page.getByRole('button', { name: /^Salvar/i }).first().click();
  await page.waitForTimeout(3500);
  await page.screenshot({ path:`${OUT}/03-empresa-lista.png` });
  console.log('[shot] ok');
});
