import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://pasteurjr.servehttp.com:8085/crm/';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/crm-serrinha';

test('CRM - Captura UIDL', async ({ page }) => {
  test.setTimeout(150_000);

  const uidlDumps: any[] = [];

  page.on('response', async (r) => {
    const u = r.url();
    if (u.includes('/UIDL/') || u.includes('UIDL?') || u.includes('/heartbeat')) {
      try {
        const ct = r.headers()['content-type'] || '';
        if (ct.includes('json') || ct.includes('text')) {
          const body = await r.text();
          uidlDumps.push({ url: u.slice(0, 120), status: r.status(), size: body.length, body_preview: body.slice(0, 200), body });
        }
      } catch {}
    }
  });

  await page.goto(APP);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('input[type="text"]').first().fill('admin');
  await page.locator('input[type="password"]').first().fill('teste');
  await page.getByText(/^Entrar$/).click().catch(() => page.keyboard.press('Enter'));
  await page.waitForTimeout(6000);

  // Interage bastante pra gerar UIDLs — abre Menu, Admin, cliques em vários lugares
  await page.mouse.click(50, 30); await page.waitForTimeout(1500);
  await page.mouse.click(50, 52); await page.waitForTimeout(1500);
  await page.mouse.click(50, 128); await page.waitForTimeout(2000);
  await page.mouse.click(772, 408); await page.waitForTimeout(2500);  // "Ir para cliente"
  await page.mouse.click(1160, 6); await page.waitForTimeout(2000);  // notificações "9"
  await page.mouse.click(908, 682); await page.waitForTimeout(1500);  // Total
  await page.mouse.click(962, 682); await page.waitForTimeout(1500);  // No Ano
  await page.mouse.click(1033, 682); await page.waitForTimeout(1500); // No Mês

  await page.screenshot({ path: `${OUT}/06-apos-cliques.png`, fullPage: true });

  // Concatena todo o payload
  const allBody = uidlDumps.map(d => d.body).join('\n');
  fs.writeFileSync(`${OUT}/uidl-full.txt`, allBody);
  console.log(`\nCapturou ${uidlDumps.length} UIDL responses, total ${allBody.length} chars`);

  // Extrai strings dos payloads UIDL — captions, tooltips, menu items, view names
  const captions = Array.from(new Set(allBody.match(/"caption":"[^"]{2,80}"/g) || []))
    .map(s => s.replace('"caption":"', '').replace('"',''));
  const descriptions = Array.from(new Set(allBody.match(/"description":"[^"]{2,80}"/g) || []))
    .map(s => s.replace('"description":"', '').replace('"',''));
  const styleNames = Array.from(new Set(allBody.match(/"styleName":"[^"]{2,60}"/g) || []))
    .map(s => s.replace('"styleName":"', '').replace('"',''));
  const iconRefs = Array.from(new Set(allBody.match(/"icon":"[^"]+"/g) || [])).slice(0, 20);
  // Nomes de componentes / classes Java
  const componentTypes = Array.from(new Set(allBody.match(/"(?:type|component):"[a-z]+"/g) || [])).slice(0, 30);
  const rpcMethods = Array.from(new Set(allBody.match(/"[a-z][a-zA-Z0-9]+_[a-zA-Z]+"/g) || [])).slice(0, 20);

  const out = { captions, descriptions, styleNames, iconRefs, componentTypes, rpcMethods, uidl_count: uidlDumps.length };
  fs.writeFileSync(`${OUT}/uidl-analysis.json`, JSON.stringify(out, null, 2));

  console.log(`\n=== CAPTIONS (${captions.length}) ===`);
  captions.slice(0, 50).forEach(c => console.log('  ' + c));

  console.log(`\n=== DESCRIPTIONS/TOOLTIPS (${descriptions.length}) ===`);
  descriptions.slice(0, 30).forEach(d => console.log('  ' + d));

  console.log(`\n=== STYLE NAMES (${styleNames.length}) ===`);
  styleNames.slice(0, 30).forEach(s => console.log('  ' + s));
});
