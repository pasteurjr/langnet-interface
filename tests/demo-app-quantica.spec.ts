/**
 * DEMO da APLICAÇÃO QUÂNTICA GERADA (não o LangNet).
 *
 * A app roda em localhost:3001 (frontend React) + localhost:8001 (backend
 * que serve project.json) + localhost:5003 (ws-server que executa tasks).
 *
 * Roteiro:
 *   1. Abre a app → tela do projeto Quântica com stats
 *   2. Aba Execução → Petri Net (lugares/tokens/transições)
 *   3. Aba Operação → seleciona cadastrar_persona_alvo, preenche input,
 *      clica Executar, captura resultado {status: sucesso, persona_id}
 *   4. Aba Logs → evento da execução
 *
 * Gera screenshots numerados + vídeo.
 */
import { test, expect } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3001';
const OUT = '/tmp/quantica-det-app/demo-screens';

const PERSONA_INPUT = JSON.stringify({
  nome: `Persona Demo UI ${Date.now()} — CTO Fintech BR`,
  descricao: 'Persona criada AO VIVO pela UI da app Quântica gerada pelo LangNet',
  canais: ['linkedin', 'email', 'eventos'],
  problemas: ['integração bancária lenta', 'compliance PIX'],
  gatilhos_de_compra: ['nova regulação BACEN', 'rodada de investimento'],
  objecoes: ['prazo de implementação'],
  palavras_chave: ['fintech', 'PIX', 'open finance'],
}, null, 2);

test.use({ video: 'on', viewport: { width: 1500, height: 950 } });

test('Demo app Quântica gerada — executar cadastrar_persona_alvo', async ({ page }) => {
  test.setTimeout(180_000);
  fs.mkdirSync(OUT, { recursive: true });

  // ── 1. Abre a app ──
  await page.goto(APP);
  await page.waitForTimeout(4000);
  await page.screenshot({ path: `${OUT}/01-home.png`, fullPage: true });

  // ── 2. Aba Execução (Petri Net) ──
  const execTab = page.locator('button:has-text("Execução")').first();
  if (await execTab.count() > 0) {
    await execTab.click();
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `${OUT}/02-execucao-petri.png`, fullPage: true });
  }

  // ── 3. Aba Operação ──
  const opTab = page.locator('button:has-text("Operação")').first();
  await opTab.click();
  await page.waitForTimeout(2000);
  await page.screenshot({ path: `${OUT}/03-operacao-vazia.png`, fullPage: true });

  // Seleciona a task cadastrar_persona_alvo
  const select = page.locator('select').first();
  await select.selectOption({ label: 'cadastrar_persona_alvo' }).catch(async () => {
    await select.selectOption('cadastrar_persona_alvo').catch(() => {});
  });
  await page.waitForTimeout(800);

  // Preenche o input JSON
  const textarea = page.locator('textarea').first();
  await textarea.click();
  await textarea.fill(PERSONA_INPUT);
  await page.waitForTimeout(1000);
  await page.screenshot({ path: `${OUT}/04-operacao-preenchida.png`, fullPage: true });

  // Clica Executar
  const execBtn = page.locator('button:has-text("Executar")').first();
  await execBtn.click();

  // Espera o resultado aparecer (deterministic é rápido, mas dá margem)
  await page.waitForTimeout(4000);
  await page.screenshot({ path: `${OUT}/05-resultado.png`, fullPage: true });

  // Tenta capturar o texto do resultado
  const resultBox = page.locator('text=/persona_id|sucesso/').first();
  if (await resultBox.count() > 0) {
    await resultBox.scrollIntoViewIfNeeded().catch(() => {});
    await page.waitForTimeout(1000);
    await page.screenshot({ path: `${OUT}/06-resultado-zoom.png`, fullPage: true });
  }

  // ── 4. Aba Logs ──
  const logsTab = page.locator('button:has-text("Logs")').first();
  if (await logsTab.count() > 0) {
    await logsTab.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${OUT}/07-logs.png`, fullPage: true });
  }

  // ── 5. Aba Outputs ──
  const outTab = page.locator('button:has-text("Outputs")').first();
  if (await outTab.count() > 0) {
    await outTab.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${OUT}/08-outputs.png`, fullPage: true });
  }

  await page.waitForTimeout(1500);
});
