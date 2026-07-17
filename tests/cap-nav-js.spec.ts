import { test } from '@playwright/test';
const APP='http://localhost:3001';
const OUT='/tmp/quantica-rich/shots';
test.use({viewport:{width:1400,height:920}});
async function nav(page, label){
  await page.evaluate((lbl)=>{
    const els=[...document.querySelectorAll('aside nav div')];
    const el=els.find(e=>e.childElementCount<=1 && e.textContent.trim().replace(/^[^A-Za-z]+/,'').startsWith(lbl));
    if(el) el.click();
  }, label);
}
test('nav agente e relatorio', async ({page})=>{
  test.setTimeout(120000);
  await page.goto(APP); await page.waitForTimeout(4000);
  await nav(page,'Geração Automática de Conteúdo'); await page.waitForTimeout(2000);
  await page.screenshot({path:`${OUT}/A-agente.png`, fullPage:true});
  const exec=page.locator('button:has-text("Executar com IA")').first();
  if(await exec.count()>0){ await exec.click(); await page.waitForTimeout(2000); await page.screenshot({path:`${OUT}/A-agente-exec.png`, fullPage:true}); }
  await nav(page,'Geração Automática de Relatórios Semanais'); await page.waitForTimeout(2000);
  await page.screenshot({path:`${OUT}/B-relatorio.png`, fullPage:true});
  // clica Gerar relatório
  const ger=page.locator('button:has-text("Gerar relatório")').first();
  if(await ger.count()>0){ await ger.click(); await page.waitForTimeout(3000); await page.screenshot({path:`${OUT}/B-relatorio-gerado.png`, fullPage:true}); }
});
