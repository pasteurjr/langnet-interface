import { test } from '@playwright/test';
import * as fs from 'fs';

const APP_URL = 'http://pasteurjr.servehttp.com:8085/crm/';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/crm-serrinha';

test('Explora CRM Serrinha (Vaadin)', async ({ page }) => {
  test.setTimeout(180_000);

  await page.goto(APP_URL);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/01-login.png`, fullPage: true });

  // Vaadin: inputs sem name, mas type="text" e "password" existem
  await page.locator('input[type="text"]').first().fill('admin');
  await page.locator('input[type="password"]').first().fill('teste');
  await page.screenshot({ path: `${OUT}/02-login-preenchido.png`, fullPage: true });

  // Clica em Entrar (botão Vaadin — texto no span)
  await page.getByText(/^Entrar$/).click().catch(async () => {
    await page.locator('.v-button:has-text("Entrar")').click().catch(() => page.keyboard.press('Enter'));
  });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: `${OUT}/03-home.png`, fullPage: true });
  console.log('URL após login:', page.url());
  console.log('Título:', await page.title());

  // Vaadin: menus tipicamente são v-button, v-menubar-menuitem, v-tabsheet-tabitemcell
  const menuTexts = await page.evaluate(() => {
    // Coleta textos únicos de elementos clicáveis Vaadin
    const selectors = [
      '.v-button:not([disabled])',
      '.v-menubar-menuitem',
      '.v-tabsheet-tabitemcell',
      '.v-treenode',
      '.v-caption',
      'span[class*="v-nativebutton"]'
    ];
    const set = new Set<string>();
    const items: any[] = [];
    for (const s of selectors) {
      document.querySelectorAll(s).forEach(el => {
        const t = (el.textContent || '').trim();
        if (t && t.length > 1 && t.length < 60 && !set.has(t)) {
          set.add(t);
          const rect = el.getBoundingClientRect();
          items.push({ sel: s, text: t, x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) });
        }
      });
    }
    return items;
  });
  console.log('\nElementos clicáveis Vaadin encontrados:');
  menuTexts.forEach(m => console.log(`  [${m.sel.replace('.v-','').replace(':not(disabled)','')}] ${m.text} @(${m.x},${m.y})`));
  fs.writeFileSync(`${OUT}/menu-items.json`, JSON.stringify(menuTexts, null, 2));

  // Filtra prováveis itens de MENU: v-button ou v-menubar-menuitem, à esquerda/topo, com texto significativo
  const likelyMenus = menuTexts.filter(m =>
    (m.sel.includes('menubar') || m.sel.includes('button')) &&
    m.text.length > 3 &&
    !/^(entrar|sair|logout|cancelar|salvar|voltar|ok|sim|não|fechar)$/i.test(m.text)
  );
  console.log(`\nFiltrado a ${likelyMenus.length} prováveis itens de menu`);

  // Clica em cada — captura tela
  const visited: any[] = [];
  for (let i = 0; i < Math.min(20, likelyMenus.length); i++) {
    const item = likelyMenus[i];
    try {
      // clica por coordenada (mais robusto no Vaadin)
      await page.mouse.click(item.x + item.w/2, item.y + item.h/2);
      await page.waitForTimeout(2500);
      const slug = item.text.replace(/[^a-z0-9]+/gi, '-').toLowerCase().slice(0, 40);
      const shotPath = `${OUT}/menu-${String(i+1).padStart(2,'0')}-${slug}.png`;
      await page.screenshot({ path: shotPath, fullPage: true });

      // Info da tela pós-click
      const info = await page.evaluate(() => {
        const cap = Array.from(document.querySelectorAll('.v-caption, h1, h2')).map(e => (e.textContent||'').trim()).filter(t => t && t.length < 100).slice(0, 8);
        const tables = document.querySelectorAll('table.v-table, .v-grid').length;
        const forms = document.querySelectorAll('form').length;
        const inputs = document.querySelectorAll('input, textarea, select').length;
        const buttons = document.querySelectorAll('.v-button').length;
        return { headers: cap, tables, forms, inputs, buttons };
      });
      visited.push({ menu: item.text, screenshot: shotPath, info });
      console.log(`  ${i+1}. [${item.text}] tables=${info.tables} inputs=${info.inputs} btns=${info.buttons}`);
    } catch (e) {
      console.log(`  ${i+1}. [${item.text}] ERRO`);
    }
  }
  fs.writeFileSync(`${OUT}/visited-menus.json`, JSON.stringify(visited, null, 2));
  console.log('\nDone.');
});
