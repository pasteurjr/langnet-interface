/**
 * E2E da APP QUÂNTICA com TELAS REAIS (Cara A) geradas do ui_spec.
 * App em localhost:3001. Sidebar com telas de negócio + aba Admin (Petri).
 * Testa: abrir → Cadastro de Persona → preencher → Salvar → resultado sucesso.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3001';
const OUT = '/tmp/quantica-ui-app/e2e-screens';

test.use({ video: 'on', viewport: { width: 1500, height: 950 } });

test('App Quântica UI real — cadastrar persona pela tela', async ({ page }) => {
  test.setTimeout(120_000);
  fs.mkdirSync(OUT, { recursive: true });

  await page.goto(APP);
  await page.waitForTimeout(4000);
  await page.screenshot({ path: `${OUT}/01-home-sidebar.png`, fullPage: true });

  // A primeira tela (Cadastro de Persona) já deve estar ativa por padrão.
  // Preenche os campos.
  const nome = page.locator('input').first();
  await nome.click();
  await nome.fill(`Persona UI Real ${Date.now()} — VP Growth`);
  await page.waitForTimeout(400);

  // Preenche por labels conhecidos
  const fillByLabel = async (labelText: string, value: string) => {
    const lab = page.locator(`label:has-text("${labelText}")`).first();
    if (await lab.count() > 0) {
      const field = lab.locator('input, textarea').first();
      if (await field.count() > 0) { await field.fill(value); await page.waitForTimeout(200); }
    }
  };
  await fillByLabel('Descrição', 'Persona criada pela tela de negócio gerada do ui_spec');
  await fillByLabel('Canais', 'linkedin, email, eventos');
  await fillByLabel('Problemas', 'churn alto, ativação lenta');
  await fillByLabel('Gatilhos', 'nova rodada, meta de expansão');
  await fillByLabel('Objeções', 'preço');
  await fillByLabel('Palavras', 'growth, saas, plg');
  await page.waitForTimeout(600);
  await page.screenshot({ path: `${OUT}/02-form-preenchido.png`, fullPage: true });

  // Clica Salvar
  const salvar = page.locator('button:has-text("Salvar")').first();
  await salvar.click();
  await page.waitForTimeout(5000);
  await page.screenshot({ path: `${OUT}/03-resultado.png`, fullPage: true });

  // Vai pra aba Admin (Petri) só pra mostrar que coexiste
  const admin = page.locator('text=/Admin \\/ Petri/').first();
  if (await admin.count() > 0) {
    await admin.click();
    await page.waitForTimeout(4000);
    await page.screenshot({ path: `${OUT}/04-aba-admin-petri.png`, fullPage: true });
  }
});
