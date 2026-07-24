import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://pasteurjr.servehttp.com:8085/crm/';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/crm-serrinha';

test('CRM - captura tela e extrai texto visível', async ({ page }) => {
  test.setTimeout(180_000);
  await page.goto(APP);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('input[type="text"]').first().fill('admin');
  await page.locator('input[type="password"]').first().fill('teste');
  await page.getByText(/^Entrar$/).click().catch(() => page.keyboard.press('Enter'));
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/dashboard-full.png`, fullPage: true });

  // Extrai TODO texto visível da página
  const allText = await page.evaluate(() => {
    const walk = (node: Node, out: string[]) => {
      if (node.nodeType === 3) {
        const t = (node.textContent || '').trim();
        if (t) out.push(t);
      } else if (node.nodeType === 1) {
        const el = node as HTMLElement;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') return;
        for (const c of Array.from(el.childNodes)) walk(c, out);
      }
    };
    const out: string[] = [];
    walk(document.body, out);
    return out;
  });
  const uniq = Array.from(new Set(allText.filter(t => t.length > 1 && t.length < 100)));
  console.log('=== Todo texto visível no dashboard (dedup) ===');
  uniq.forEach(t => console.log(' ▸', t));
  fs.writeFileSync(`${OUT}/dashboard-text.txt`, uniq.join('\n'));

  // Também captura estruturalmente: divs com widget/panel/box
  const widgetStruct = await page.evaluate(() => {
    const widgets = Array.from(document.querySelectorAll(
      '.v-panel, .v-verticallayout > .v-slot, .v-window, .v-formlayout, .v-grid, .v-table, .v-chart, .v-tabsheet'
    ));
    return widgets.map(w => {
      const r = w.getBoundingClientRect();
      const cls = w.className.split(' ').filter(c => c.startsWith('v-') && c.length < 40).slice(0,4).join(' ');
      const text = (w.textContent || '').trim().slice(0, 150);
      return { cls, text, x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
    }).filter(w => w.w > 30 && w.h > 15 && w.text.length > 0);
  });
  console.log(`\n=== Widgets estruturais (${widgetStruct.length}) ===`);
  widgetStruct.forEach(w => console.log(`  [${w.cls}] @(${w.x},${w.y}) ${w.w}x${w.h} — "${w.text.slice(0,80)}"`));
  fs.writeFileSync(`${OUT}/widget-struct.json`, JSON.stringify(widgetStruct, null, 2));

  // Rola pra baixo e captura mais
  await page.evaluate(() => window.scrollTo(0, 2000));
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${OUT}/dashboard-scroll.png`, fullPage: true });

  // Detecta se existe SVG (Highcharts é SVG)
  const svgInfo = await page.evaluate(() => {
    const svgs = document.querySelectorAll('svg');
    const info: any[] = [];
    svgs.forEach(s => {
      const rect = s.getBoundingClientRect();
      const title = s.querySelector('title')?.textContent;
      const texts = Array.from(s.querySelectorAll('text')).map(t => t.textContent?.trim()).filter(Boolean).slice(0, 10);
      info.push({ w: Math.round(rect.width), h: Math.round(rect.height), title, sample_texts: texts });
    });
    return info;
  });
  console.log(`\n=== SVGs (${svgInfo.length}) ===`);
  svgInfo.forEach(s => console.log(`  ${s.w}x${s.h} title="${s.title || ''}" texts=[${(s.sample_texts||[]).join(', ')}]`));
});
