/**
 * E2E — Passeio completo pelo LangNet UI usando Quântica como caso-teste.
 * Captura tela em cada etapa do menu do projeto.
 * Se a etapa Modelo de Dados estiver vazia, GERA do zero.
 */
import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/langnet-ui-e2e/screenshots';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';

interface StepLog {
  step: string;
  screenshot: string;
  status: 'OK' | 'PARTIAL' | 'GENERATED' | 'ERROR';
  observation: string;
  duration_ms?: number;
}
const log: StepLog[] = [];

async function snap(page: any, id: string, label: string) {
  const file = path.join(OUT, `${id}.png`);
  await page.screenshot({ path: file, fullPage: true });
  return file;
}

test('LangNet E2E — Passeio Quântica pelas etapas', async ({ page }) => {
  test.setTimeout(1800_000); // 30 min pra caso o Data Model precise gerar

  fs.mkdirSync(OUT, { recursive: true });

  // ══════ Login ══════
  console.log('\n>>> LOGIN');
  await page.goto(APP);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(4500);  // Espera React montar
  await snap(page, '01-tela-inicial', 'Tela inicial');

  // Login com seletores corretos (id="email", id="password", btn "Entrar")
  const emailField = page.locator('#email');
  if (await emailField.count() > 0) {
    await emailField.fill('teste@teste.com');
    await page.locator('#password').fill('buceta123');
    await snap(page, '02-login-preenchido', 'Login preenchido');
    await page.locator('button:has-text("Entrar")').first().click();
    await page.waitForTimeout(4500);
  }
  await page.waitForLoadState('networkidle').catch(() => {});
  await snap(page, '03-dashboard', 'Dashboard após login');
  log.push({ step: 'Login', screenshot: '03-dashboard.png', status: 'OK', observation: 'Login realizado' });

  // ══════ Vai pro projeto Quântica ══════
  console.log('\n>>> Selecionar projeto Quântica');
  await page.goto(`${APP}/projects/${PROJECT_ID}`);
  await page.waitForTimeout(3000);
  await snap(page, '04-project-detail', 'Detalhe do projeto Quântica');
  log.push({ step: 'Projeto', screenshot: '04-project-detail.png', status: 'OK', observation: `Projeto ${PROJECT_ID.slice(0,8)}… aberto` });

  // ══════ Cada etapa do menu ══════
  const etapas: { id: string; label: string; path: string; expectedNonEmpty?: boolean }[] = [
    { id: 'documents', label: 'Documentos', path: `/project/${PROJECT_ID}/documents`, expectedNonEmpty: true },
    { id: 'spec', label: 'Especificação', path: `/project/${PROJECT_ID}/spec`, expectedNonEmpty: true },
    { id: 'data-model', label: 'Modelo de Dados (NOVA ETAPA)', path: `/project/${PROJECT_ID}/data-model`, expectedNonEmpty: false },
    { id: 'agent-task', label: 'Agentes & Tarefas', path: `/projects/${PROJECT_ID}/agent-task`, expectedNonEmpty: true },
    { id: 'task-execution-flow', label: 'Sequência de Tarefas', path: `/project/${PROJECT_ID}/task-execution-flow`, expectedNonEmpty: true },
    { id: 'petri', label: 'Rede de Petri', path: `/projects/${PROJECT_ID}/petri`, expectedNonEmpty: true },
    { id: 'code', label: 'Geração de Código', path: `/projects/${PROJECT_ID}/code`, expectedNonEmpty: true },
  ];

  for (const et of etapas) {
    const t0 = Date.now();
    console.log(`\n>>> ${et.label}`);
    await page.goto(APP + et.path);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(6000);  // Cada page precisa de tempo pra fetch de dados
    const screenshotFile = await snap(page, `05-${et.id}`, et.label);

    // Extrai algum sinal de "conteúdo" na tela
    const info = await page.evaluate(() => {
      const bodyText = document.body.textContent || '';
      const hasTable = document.querySelectorAll('table, .v-table, [class*="table"]').length;
      const codeBlocks = document.querySelectorAll('pre, code').length;
      const cards = document.querySelectorAll('[class*="card"], [class*="Card"]').length;
      const chars = bodyText.length;
      const err = bodyText.toLowerCase().includes('error') || bodyText.toLowerCase().includes('erro');
      return { chars, hasTable, codeBlocks, cards, hasError: err };
    });
    console.log(`  chars=${info.chars} tabelas=${info.hasTable} codeblocks=${info.codeBlocks} cards=${info.cards}`);
    log.push({
      step: et.label, screenshot: `05-${et.id}.png`,
      status: info.chars > 500 && !info.hasError ? 'OK' : 'PARTIAL',
      observation: `chars=${info.chars} elementos: tabelas=${info.hasTable} code=${info.codeBlocks} cards=${info.cards}`,
      duration_ms: Date.now() - t0,
    });

    // ══ ETAPA ESPECIAL: Data Model ══
    // Se estivermos na etapa Data Model e não houver Data Model gerado, GERAR
    if (et.id === 'data-model') {
      // Espera dropdown popular
      await page.waitForTimeout(3000);
      // Verifica se tem spec disponível
      const specOptions = await page.locator('select').first().locator('option').count();
      console.log(`  Opções no dropdown de spec: ${specOptions}`);
      await snap(page, '05a-data-model-antes-gerar', 'Antes de gerar');

      const btnGerar = page.locator('button:has-text("Gerar Modelo de Dados")').first();
      const btnEnabled = await btnGerar.isEnabled().catch(() => false);
      console.log(`  Botão Gerar habilitado? ${btnEnabled}`);

      if (btnEnabled) {
        console.log('  ▶ CLICANDO GERAR MODELO DE DADOS…');
        await btnGerar.click();
        // Espera até 15 min (pipeline demorou 8min anteriormente)
        console.log('  Aguardando geração (pode levar até 15min)…');
        try {
          await page.waitForFunction(() => {
            const bt = document.body.textContent || '';
            return bt.includes('Aprovar') || bt.includes('models.py') || bt.includes('schema') || bt.includes('YAML');
          }, { timeout: 900_000 });
          await page.waitForTimeout(2000);
          console.log('  ✓ Data Model gerado');
          await snap(page, '05b-data-model-gerado', 'Data Model gerado');
          log.push({ step: 'Data Model — GERADO', screenshot: '05b-data-model-gerado.png', status: 'GENERATED', observation: 'Pipeline executado via UI' });

          // Explora abas
          for (const aba of ['Schema SQL', 'models.py', 'Alembic', 'YAML']) {
            try {
              await page.getByRole('button', { name: aba }).click({ timeout: 2000 });
              await page.waitForTimeout(1000);
              await snap(page, `05c-data-model-aba-${aba.toLowerCase().replace(/[^a-z]+/g,'-')}`, `Aba ${aba}`);
            } catch {}
          }
        } catch (e) {
          console.log('  ⚠ Timeout ou erro na geração:', e);
          await snap(page, '05x-data-model-timeout', 'Timeout');
          log.push({ step: 'Data Model — timeout', screenshot: '05x-data-model-timeout.png', status: 'ERROR', observation: `${e}` });
        }
      } else {
        console.log('  Data Model já existente ou botão não disponível');
      }
    }
  }

  // Salva log final
  fs.writeFileSync(OUT + '/../log.json', JSON.stringify(log, null, 2));
  console.log('\n=== RESUMO ===');
  for (const l of log) console.log(`  [${l.status}] ${l.step} — ${l.observation.slice(0,100)}`);
});
