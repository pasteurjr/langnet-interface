import { test } from '@playwright/test';
import * as fs from 'fs';

const APP_URL = 'http://pasteurjr.servehttp.com:8085/crm/';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/crm-serrinha';

test('Serrinha - explora Menu principal e Admin', async ({ page }) => {
  test.setTimeout(240_000);

  await page.goto(APP_URL);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('input[type="text"]').first().fill('admin');
  await page.locator('input[type="password"]').first().fill('teste');
  await page.getByText(/^Entrar$/).click().catch(() => page.keyboard.press('Enter'));
  await page.waitForTimeout(5000);

  await page.screenshot({ path: `${OUT}/03-home-full.png`, fullPage: true });

  // === 1. Clica no Menu principal (canto superior esquerdo) ===
  console.log('\n=== Clicando em "Menu" ===');
  await page.mouse.click(30, 30);  // aproxima do "Menu" que estava em (0,0) com padding
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/04-menu-aberto.png`, fullPage: true });

  const menuItems = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('.v-button, .v-menubar-menuitem, .v-treenode, .v-panel-caption, .v-caption'))
      .map(el => {
        const rect = el.getBoundingClientRect();
        return {
          text: (el.textContent || '').trim(),
          cls: el.className.split(' ').filter(c => c.startsWith('v-')).slice(0,3).join(' '),
          x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height)
        };
      })
      .filter(m => m.text && m.text.length > 1 && m.text.length < 60 && m.w > 20 && m.h > 15);
    return items;
  });
  fs.writeFileSync(`${OUT}/menu-aberto-items.json`, JSON.stringify(menuItems, null, 2));
  console.log(`Encontrados ${menuItems.length} elementos após abrir Menu`);
  menuItems.slice(0, 40).forEach(m => console.log(`  @(${m.x},${m.y}) [${m.cls}] ${m.text}`));

  // === 2. Clica no Admin (o "► Admin" era em (16,52)) ===
  console.log('\n=== Clicando em "Admin" ===');
  await page.mouse.click(50, 52);
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/05-admin-aberto.png`, fullPage: true });

  const adminItems = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('.v-menubar-menuitem, .v-menubar-popup .v-menubar-menuitem, .v-treenode'))
      .map(el => {
        const rect = el.getBoundingClientRect();
        return {
          text: (el.textContent || '').trim(),
          x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height)
        };
      })
      .filter(m => m.text && m.text.length > 1 && m.text.length < 80 && m.w > 20);
    return items;
  });
  console.log(`Admin: ${adminItems.length} items`);
  adminItems.forEach(m => console.log(`  @(${m.x},${m.y}) ${m.text}`));

  // === 3. Sniff de rede: captura endpoints XHR quando naveg ===
  const requests: any[] = [];
  page.on('request', r => {
    const u = r.url();
    if (u.includes('/crm/') && (u.includes('UIDL') || u.includes('rest') || u.includes('api'))) {
      requests.push({ method: r.method(), url: u.slice(0, 200) });
    }
  });

  // === 4. Explora entradas do menu top-level (todas que estão numa faixa Y do menu) ===
  // Reabre menu
  await page.mouse.click(50, 30);
  await page.waitForTimeout(1500);
  const topMenus = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.v-menubar-menuitem'))
      .map(el => {
        const rect = el.getBoundingClientRect();
        return {
          text: (el.textContent || '').trim(),
          x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height)
        };
      })
      .filter(m => m.text && m.text.length > 1 && m.y < 100);  // barra de menu no topo
  });
  console.log(`\n=== Menu top-level (${topMenus.length} itens) ===`);
  topMenus.forEach(m => console.log(`  ${m.text} @(${m.x},${m.y})`));

  // Visita cada
  for (let i = 0; i < Math.min(15, topMenus.length); i++) {
    const item = topMenus[i];
    try {
      await page.mouse.click(item.x + item.w/2, item.y + item.h/2);
      await page.waitForTimeout(2000);
      const slug = item.text.replace(/[►\s\W]+/g, '-').toLowerCase().slice(0, 30);
      await page.screenshot({ path: `${OUT}/top-${String(i+1).padStart(2,'0')}-${slug}.png`, fullPage: true });
      const sub = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('.v-menubar-popup .v-menubar-menuitem, .v-menubar-menuitem-selected + * .v-menubar-menuitem'))
          .map(e => (e.textContent||'').trim()).filter(t => t && t.length < 60);
      });
      console.log(`  ${i+1}. ${item.text} → submenu: [${sub.join(', ')}]`);
    } catch {}
  }

  fs.writeFileSync(`${OUT}/network-endpoints.json`, JSON.stringify(requests.slice(0, 30), null, 2));
  console.log('\nEndpoints capturados:', requests.length);
});
