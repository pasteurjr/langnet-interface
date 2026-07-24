import { test } from '@playwright/test';
import * as fs from 'fs';

const URL = 'http://pasteurjr.servehttp.com:8085/crm/';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/crm-serrinha';

test('Explora CRM Serrinha', async ({ page }) => {
  test.setTimeout(180_000);

  // Passo 1: acessar login
  await page.goto(URL);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(2000);
  await page.screenshot({ path: `${OUT}/01-login.png`, fullPage: true });
  console.log('URL após acesso:', page.url());
  console.log('Título:', await page.title());

  // Detecta campos de login
  const loginInfo = await page.evaluate(() => {
    const inputs = Array.from(document.querySelectorAll('input')).map(i => ({
      name: i.name, id: i.id, type: i.type, placeholder: i.placeholder
    }));
    const forms = Array.from(document.querySelectorAll('form')).map(f => ({
      action: f.action, method: f.method
    }));
    const links = Array.from(document.querySelectorAll('a')).slice(0,10).map(a => ({
      text: a.textContent?.trim().slice(0,50), href: a.href
    }));
    return { inputs, forms, links, bodyPreview: document.body.textContent?.slice(0, 500) };
  });
  console.log('Login form:', JSON.stringify(loginInfo, null, 2));

  // Passo 2: preencher e enviar login (várias tentativas de field name)
  const userSelectors = ['input[name="username"]', 'input[name="user"]', 'input[name="login"]', 'input[type="text"]', 'input[type="email"]', 'input[name="email"]'];
  const passSelectors = ['input[name="password"]', 'input[type="password"]', 'input[name="passwd"]', 'input[name="senha"]'];

  let loggedIn = false;
  for (const us of userSelectors) {
    try {
      const el = page.locator(us).first();
      if (await el.count()) {
        await el.fill('admin');
        break;
      }
    } catch {}
  }
  for (const ps of passSelectors) {
    try {
      const el = page.locator(ps).first();
      if (await el.count()) {
        await el.fill('teste');
        break;
      }
    } catch {}
  }

  // submete o form
  try {
    const btn = page.locator('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Entrar"), button:has-text("Acessar")').first();
    await btn.click();
  } catch (e) {
    await page.keyboard.press('Enter');
  }
  await page.waitForTimeout(3500);
  await page.screenshot({ path: `${OUT}/02-pos-login.png`, fullPage: true });
  console.log('URL pós-login:', page.url());
  console.log('Título pós:', await page.title());

  // Passo 3: descobrir menus
  const menus = await page.evaluate(() => {
    const menuLinks = Array.from(document.querySelectorAll('a')).map(a => ({
      text: (a.textContent || '').trim().slice(0, 80),
      href: a.href,
      cls: a.className
    })).filter(l => l.text && !l.text.includes('\n') && l.text.length < 60);
    return menuLinks;
  });
  console.log(`\nLinks encontrados: ${menus.length}`);
  fs.writeFileSync(`${OUT}/menus.json`, JSON.stringify(menus, null, 2));

  // Passo 4: visita as N primeiras entradas de menu (que não sejam externas)
  const baseHost = new URL(page.url()).host;
  const menuInternal = menus.filter(m => {
    try {
      const u = new URL(m.href);
      return u.host === baseHost && !m.text.match(/^(sair|logout|voltar|home)$/i) && m.text.length > 2;
    } catch { return false; }
  });
  const seen = new Set<string>();
  const unique = menuInternal.filter(m => {
    const key = m.href;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, 20);

  console.log('\n=== Visitando ' + unique.length + ' menus ===');
  const pagesInfo: any[] = [];
  for (let i = 0; i < unique.length; i++) {
    const item = unique[i];
    try {
      await page.goto(item.href);
      await page.waitForLoadState('domcontentloaded').catch(() => {});
      await page.waitForTimeout(1500);
      const slug = item.text.replace(/[^a-z0-9]+/gi, '-').toLowerCase().slice(0, 40);
      const shotPath = `${OUT}/menu-${String(i+1).padStart(2,'0')}-${slug}.png`;
      await page.screenshot({ path: shotPath, fullPage: true });

      // Extrai info da página: título, headers, forms, tabelas
      const info = await page.evaluate(() => {
        const h1 = Array.from(document.querySelectorAll('h1,h2,h3')).map(h => h.textContent?.trim()).filter(Boolean).slice(0, 8);
        const tables = document.querySelectorAll('table').length;
        const forms = Array.from(document.querySelectorAll('form')).map(f => ({
          action: f.action, method: f.method,
          inputs: Array.from(f.querySelectorAll('input,select,textarea')).map(i => (i as HTMLInputElement).name).filter(Boolean)
        }));
        const cardsCount = document.querySelectorAll('.card, .box, .panel, [class*="widget"]').length;
        const bodyLen = document.body.textContent?.length || 0;
        return { h1, tables, forms, cardsCount, bodyLen };
      });
      pagesInfo.push({ menu: item.text, url: item.href, screenshot: shotPath, info });
      console.log(`  ${i+1}. [${item.text}] tables=${info.tables} forms=${info.forms.length} h1=${info.h1.join('|')}`);
    } catch (e) {
      console.log(`  ${i+1}. [${item.text}] ERRO: ${e}`);
    }
  }

  fs.writeFileSync(`${OUT}/pages-info.json`, JSON.stringify(pagesInfo, null, 2));
  console.log('\nExploração salva em ' + OUT);
});
