/**
 * Etapa 2 do pipeline LangNet — Especificação Funcional Quântica Comercial.
 * A partir da versão v2 do requirements (refinada, 38k chars), gera nova spec
 * via UI. Aguarda coder-32b processar. Documenta antes/depois.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';

test('Gerar Spec Quântica (Etapa 2)', async ({ page }) => {
  test.setTimeout(2400_000);

  fs.mkdirSync(OUT, { recursive: true });

  await page.goto(APP);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  console.log('[1] login OK');

  // Vai pra spec page do projeto
  await page.goto(`${APP}/project/${PROJECT_ID}/spec`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/etapa2-01-spec-inicial.png`, fullPage: true });
  console.log('[2] tela spec carregada');

  // Selecionar documento de requisitos — botão "📋 Requisitos"
  const reqBtn = page.locator('button:has-text("Requisitos")').first();
  if (await reqBtn.count() > 0) {
    await reqBtn.click();
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `${OUT}/etapa2-02-selecao-req.png`, fullPage: true });
    console.log('[3] painel Selecionar Requisitos aberto');

    // Primeira session no modal (15/06 13:42, 39.56 KB) = a nossa
    // Clica em "Clique para ver versões →" pra abrir a lista de versões
    const verVersoes = page.locator('text=/Clique para ver vers/i').first();
    if (await verVersoes.count() > 0) {
      await verVersoes.click();
      await page.waitForTimeout(2500);
      await page.screenshot({ path: `${OUT}/etapa2-03-versoes-listadas.png`, fullPage: true });
      console.log('[3b] versões listadas');
    }

    // Seleciona v2 (mais recente); se não achar, cai em v1
    const v2Selector = page.locator('text=/Versão 2|v2|Version 2/i').first();
    let selectedVer = '';
    if (await v2Selector.count() > 0) {
      await v2Selector.click();
      selectedVer = 'v2';
    } else {
      const v1Selector = page.locator('text=/Versão 1|v1|Version 1/i').first();
      if (await v1Selector.count() > 0) {
        await v1Selector.click();
        selectedVer = 'v1';
      }
    }
    console.log(`  selecionou: ${selectedVer || 'nada'}`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${OUT}/etapa2-03b-selecionado.png`, fullPage: true });

    // Confirma
    const confBtn = page.locator('button:has-text("Confirmar"), button:has-text("Selecionar"), button:has-text("Usar")').first();
    if (await confBtn.count() > 0) {
      await confBtn.click();
      await page.waitForTimeout(2500);
    }
  }

  await page.screenshot({ path: `${OUT}/etapa2-04-antes-gerar.png`, fullPage: true });

  // Adiciona custom_instructions (por enquanto foco em "gerar do zero e ver o que sai")
  const customArea = page.locator('textarea[placeholder*="instru" i], textarea[placeholder*="customizada" i]').first();
  if (await customArea.count() > 0 && await customArea.isVisible().catch(() => false)) {
    await customArea.fill('Gere a especificação completa. Use os IDs originais do requirements (FR-XXX, NFR-XXX, BR-XXX) — NÃO renomeie para RF ou RNF. Cada UC deve rastrear a pelo menos 1 FR real.');
    console.log('[4] custom instructions preenchidas');
  }

  // Clica em "Gerar Especificação"
  const genBtn = page.locator('button:has-text("Gerar Especificação"), button:has-text("Gerar Nova"), button.btn-start-analysis').first();
  const btnEnabled = await genBtn.isEnabled().catch(() => false);
  console.log(`  botão Gerar: enabled=${btnEnabled}`);
  await genBtn.click({ timeout: 5000 });
  console.log('[5] clicou em Gerar Especificação');
  await page.screenshot({ path: `${OUT}/etapa2-05-gerando.png`, fullPage: true });

  // Aguarda geração (até 30 min)
  let done = false;
  for (let i = 0; i < 240; i++) {
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => {
      const txt = document.body.textContent || '';
      const hasCompleted = /completed|conclu|success|especifica.{0,20}(gerada|pronta)|Download/i.test(txt);
      const hasError = /error|erro.{0,10}(gera|processa)|failed|falhou/i.test(txt);
      return { hasCompleted, hasError, len: txt.length };
    });
    if (state.hasCompleted) { done = true; console.log(`  ${(i+1)*10}s: spec GERADA`); break; }
    if (state.hasError) { console.log(`  ${(i+1)*10}s: erro detectado`); break; }
    if (i % 6 === 0) console.log(`  ${(i+1)*10}s: aguardando (body=${state.len} chars)`);
  }

  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa2-06-gerada.png`, fullPage: true });
  console.log('[6] fim');
});
