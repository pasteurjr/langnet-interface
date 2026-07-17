import { test } from '@playwright/test';
const APP='http://localhost:3001';
const OUT='/tmp/quantica-rich/shots';
test.use({viewport:{width:1400,height:920}});
test('agente e relatorio', async ({page})=>{
  test.setTimeout(120000);
  await page.goto(APP); await page.waitForTimeout(4000);
  // Agente: Geração Automática de Conteúdo
  await page.locator('div', {hasText:/^Geração Automática de Conteúdo$/}).last().click().catch(()=>{});
  await page.waitForTimeout(2000);
  await page.screenshot({path:`${OUT}/A-agente.png`, fullPage:true});
  // Executa a tela de agente (dispara com IA) - só clica pra mostrar o loading/estado
  const exec = page.locator('button:has-text("Executar com IA")').first();
  if(await exec.count()>0){ await exec.click(); await page.waitForTimeout(2500); await page.screenshot({path:`${OUT}/A-agente-exec.png`, fullPage:true}); }
  // Relatório: Geração Automática de Relatórios Semanais
  await page.locator('div', {hasText:/^Geração Automática de Relatórios Semanais$/}).last().click().catch(()=>{});
  await page.waitForTimeout(2000);
  await page.screenshot({path:`${OUT}/B-relatorio.png`, fullPage:true});
});
