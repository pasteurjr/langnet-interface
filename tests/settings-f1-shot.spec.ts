import { test } from '@playwright/test';
import * as fs from 'fs';
const TOK = fs.readFileSync('/tmp/uso-solo-pipeline/tok.txt','utf8').trim();
test('settings f1 test', async ({ page }) => {
  test.setTimeout(90000);
  await page.addInitScript((t)=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOK);
  await page.setViewportSize({ width: 1500, height: 1000 });
  await page.goto('http://localhost:3000/settings', { waitUntil:'networkidle', timeout:45000 }).catch(()=>{});
  await page.waitForTimeout(3500);
  // clica o botão "Testar Conexão" do BANCO (o primeiro)
  const btns = page.getByRole('button', { name: /Testar Conexão/i });
  await btns.first().click().catch(()=>{});
  await page.waitForTimeout(7000);  // conexão ao banco remoto
  await page.screenshot({ path:'/tmp/uso-solo-pipeline/shots-f1/02-testar-banco.png' });
  console.log('[shot] testar-banco (banco)');
  // testa LLM também
  await btns.nth(1).click().catch(()=>{});
  await page.waitForTimeout(6000);
  await page.screenshot({ path:'/tmp/uso-solo-pipeline/shots-f1/03-testar-llm.png', fullPage:true });
  console.log('[shot] testar-llm');
});
