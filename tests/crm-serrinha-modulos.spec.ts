import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://pasteurjr.servehttp.com:8085/crm/';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/crm-serrinha';

test('CRM - módulos Clientes/Chamados/Negócios/Relatórios', async ({ page }) => {
  test.setTimeout(240_000);
  await page.goto(APP);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('input[type="text"]').first().fill('admin');
  await page.locator('input[type="password"]').first().fill('teste');
  await page.getByText(/^Entrar$/).click().catch(() => page.keyboard.press('Enter'));
  await page.waitForTimeout(6000);

  const modulos = ['Clientes', 'Chamados', 'Negócios', 'Relatorios'];
  const collected: any = {};

  for (const m of modulos) {
    console.log(`\n=== CLICANDO em ${m} ===`);
    try {
      await page.getByText(new RegExp('^' + m + '$')).first().click({ timeout: 5000 });
      await page.waitForTimeout(3500);
      const slug = m.toLowerCase().replace(/[^a-z]/g, '');
      await page.screenshot({ path: `${OUT}/modulo-${slug}.png`, fullPage: true });

      const info = await page.evaluate(() => {
        const walk = (n: Node, out: string[]) => {
          if (n.nodeType === 3) { const t = (n.textContent || '').trim(); if (t) out.push(t); }
          else if (n.nodeType === 1) {
            const el = n as HTMLElement;
            const st = window.getComputedStyle(el);
            if (st.display === 'none' || st.visibility === 'hidden') return;
            for (const c of Array.from(el.childNodes)) walk(c, out);
          }
        };
        const out: string[] = [];
        walk(document.body, out);
        // Só texto visível pertinente
        return Array.from(new Set(out.filter(t => t.length > 1 && t.length < 80)));
      });
      collected[m] = info;
      console.log(`Texto extraído (${info.length} itens):`);
      info.slice(0, 60).forEach((t: string) => console.log('  ▸', t));
    } catch (e: any) {
      console.log(`  ERRO em ${m}: ${e.message?.slice(0,80)}`);
    }
    // volta pra Home antes do próximo
    try { await page.getByText(/^Home$/).first().click({ timeout: 3000 }); await page.waitForTimeout(2000); } catch {}
  }

  fs.writeFileSync(`${OUT}/modulos-conteudo.json`, JSON.stringify(collected, null, 2));
});
