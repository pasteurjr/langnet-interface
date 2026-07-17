import { test } from '@playwright/test';
import * as fs from 'fs';
const APP = 'http://localhost:3001';
const OUT = '/tmp/quantica-rich/shots';
test.use({ viewport: { width: 1500, height: 950 } });

test('App rica — CRUD completo + relatório + agente', async ({ page }) => {
  test.setTimeout(150_000);
  fs.mkdirSync(OUT, { recursive: true });
  await page.goto(APP);
  await page.waitForTimeout(4000);
  // 1) Home = tela CRUD Persona em modo LISTA + sidebar agrupado
  await page.screenshot({ path: `${OUT}/01-crud-lista.png`, fullPage: true });

  // 2) Clica Novo → formulário
  const novo = page.locator('button:has-text("Novo")').first();
  if (await novo.count() > 0) { await novo.click(); await page.waitForTimeout(1500); }
  await page.screenshot({ path: `${OUT}/02-crud-form-novo.png`, fullPage: true });

  // preenche e salva
  const nome = page.locator('input').first();
  await nome.fill(`CRUD Rico ${Date.now()}`);
  const fill = async (l: string, v: string) => {
    const lab = page.locator(`label:has-text("${l}")`).first();
    if (await lab.count() > 0) { const el = lab.locator('xpath=following-sibling::*[1]').first(); if (await el.count() > 0) await el.fill(v); }
  };
  await fill('Descri', 'persona via CRUD rico');
  await fill('Canais', 'linkedin, email');
  await fill('Problemas', 'p1, p2');
  await page.waitForTimeout(400);
  const salvar = page.locator('button:has-text("Salvar")').first();
  await salvar.click();
  await page.waitForTimeout(3500);
  await page.screenshot({ path: `${OUT}/03-crud-apos-salvar-lista.png`, fullPage: true });

  // 3) Editar a primeira linha
  const editar = page.locator('button:has-text("Editar")').first();
  if (await editar.count() > 0) { await editar.click(); await page.waitForTimeout(2500); }
  await page.screenshot({ path: `${OUT}/04-crud-editar.png`, fullPage: true });
  // cancela
  const cancelar = page.locator('button:has-text("Cancelar")').first();
  if (await cancelar.count() > 0) { await cancelar.click(); await page.waitForTimeout(1000); }

  // 4) Excluir (inline confirm)
  const excluir = page.locator('button:has-text("Excluir")').first();
  if (await excluir.count() > 0) {
    await excluir.click(); await page.waitForTimeout(600);
    await page.screenshot({ path: `${OUT}/05-crud-confirma-excluir.png`, fullPage: true });
    const conf = page.locator('button:has-text("Confirmar")').first();
    if (await conf.count() > 0) { await conf.click(); await page.waitForTimeout(2500); }
  }
  await page.screenshot({ path: `${OUT}/06-crud-apos-excluir.png`, fullPage: true });

  // 5) Tela de relatório
  const rel = page.locator('aside >> text=/Relat/').first();
  if (await rel.count() > 0) { await rel.click(); await page.waitForTimeout(2000); }
  await page.screenshot({ path: `${OUT}/07-relatorio.png`, fullPage: true });

  // 6) Tela de agente
  const ag = page.locator('aside >> text=/Gera.*Conte|Classifica/').first();
  if (await ag.count() > 0) { await ag.click(); await page.waitForTimeout(2000); }
  await page.screenshot({ path: `${OUT}/08-agente.png`, fullPage: true });
});
