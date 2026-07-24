/**
 * Passo 1: refinar Data Model via chat + aprovar.
 * - Refinamento 1: reordena FKs (3 problemas high)
 * - Refinamento 2: adiciona índices que faltam (2 problemas medium)
 * - Aprovação final
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/langnet-ui-e2e/screenshots';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';

const eventos: Array<{ passo: string; ts: string; obs: string }> = [];
function reg(passo: string, obs: string) {
  eventos.push({ passo, ts: new Date().toISOString(), obs });
  console.log(`[${new Date().toLocaleTimeString()}] ${passo} — ${obs}`);
}

async function snap(page: any, id: string) {
  const file = `${OUT}/${id}.png`;
  await page.screenshot({ path: file, fullPage: true });
  return file;
}

test('Refinar Data Model via chat + aprovar', async ({ page }) => {
  test.setTimeout(2400_000); // 40 min

  // Login + navegação
  await page.goto(APP);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  // Aguarda sair da /login (redirect pro dashboard)
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  reg('login', 'ok — não está mais em /login');

  await page.goto(`${APP}/project/${PROJECT_ID}/data-model`);
  await page.waitForLoadState('networkidle').catch(() => {});
  // Aguarda a tela DataModel montar (procura texto "Modelo de Dados" que só existe nessa page)
  await page.waitForFunction(
    () => (document.body.textContent || '').includes('Modelo de Dados') && (document.body.textContent || '').includes('Refinar via chat'),
    { timeout: 30000 }
  );
  await page.waitForTimeout(3000);
  await snap(page, 'passo1-01-antes');

  // Estado inicial
  const inicial = await page.evaluate(() => {
    const bt = document.body.textContent || '';
    const scoreMatch = bt.match(/score (\d+)\/100/);
    const probMatch = bt.match(/(\d+) problemas/);
    const tabMatch = bt.match(/Tabelas: (\d+)/);
    return {
      score: scoreMatch?.[1] || '?',
      problemas: probMatch?.[1] || '?',
      tabelas: tabMatch?.[1] || '?',
    };
  });
  reg('estado-inicial', `${inicial.tabelas} tabelas, validação score=${inicial.score}/100, ${inicial.problemas} problemas`);

  // ═══════ REFINAMENTO 1: reordenar FKs ═══════
  const chatInput = page.locator('.dm-chat-input input');
  reg('refinamento-1', 'Enviando pedido de reordenação de FKs…');
  const pedido1 = 'Reordene a criação das tabelas para respeitar dependências de FK. As tabelas comentarios, leads devem ser criadas DEPOIS das tabelas que referenciam (empresas_alvo e decisores antes de leads; leads antes de comentarios). Corrija também qualquer outra ordem incorreta que detectar.';
  await chatInput.fill(pedido1);
  await snap(page, 'passo1-02-refino1-antes-enviar');
  await page.locator('.dm-chat-input button').click();
  reg('refinamento-1', 'Aguardando LLM (pode levar ~7 min)…');

  // Espera terminar: input deve reativar (sending some vai)
  // Polling manual (actionTimeout do config trava waitForFunction em 30s)
  {
    let done = false;
    for (let i = 0; i < 180; i++) {  // 180 × 5s = 15 min
      const state = await page.evaluate(() => {
        const inp = document.querySelector('.dm-chat-input input') as HTMLInputElement | null;
        const bt = document.body.textContent || '';
        return {
          disabled: inp?.disabled ?? true,
          hasError: bt.includes('Erro') && bt.includes('HTTP'),
          hasSending: bt.includes('…refinando…'),
        };
      });
      if (!state.disabled && !state.hasSending) { done = true; break; }
      if (state.hasError) { console.log('  ⚠ erro detectado'); break; }
      if (i % 12 === 0) console.log(`  ... ainda aguardando (${i*5}s decorridos)`);
      await page.waitForTimeout(5000);
    }
    if (!done) console.log('  ⚠ timeout de 15min no polling');
  }
  await page.waitForTimeout(3000);
  await snap(page, 'passo1-03-refino1-pronto');
  reg('refinamento-1', 'concluído');

  // Ver score novo
  const pos1 = await page.evaluate(() => {
    const bt = document.body.textContent || '';
    return {
      score: (bt.match(/score (\d+)\/100/) || [])[1] || '?',
      problemas: (bt.match(/(\d+) problemas/) || [])[1] || '?',
      tabelas: (bt.match(/Tabelas: (\d+)/) || [])[1] || '?',
    };
  });
  reg('estado-pos-refino1', `${pos1.tabelas} tabelas, score=${pos1.score}/100, ${pos1.problemas} problemas`);

  // ═══════ REFINAMENTO 2: adicionar índices ═══════
  reg('refinamento-2', 'Enviando pedido de índices…');
  const pedido2 = 'Adicione um índice em tarefas_followup.data_vencimento (idx_tarefas_followup_data_vencimento) para acelerar filtros de tarefas vencidas. Adicione também um índice em logs_auditoria.timestamp (idx_logs_auditoria_timestamp) para consultas por período. Mantenha o resto do modelo inalterado.';
  await chatInput.fill(pedido2);
  await snap(page, 'passo1-04-refino2-antes-enviar');
  await page.locator('.dm-chat-input button').click();
  reg('refinamento-2', 'Aguardando LLM…');

  // Polling manual (actionTimeout do config trava waitForFunction em 30s)
  {
    let done = false;
    for (let i = 0; i < 180; i++) {  // 180 × 5s = 15 min
      const state = await page.evaluate(() => {
        const inp = document.querySelector('.dm-chat-input input') as HTMLInputElement | null;
        const bt = document.body.textContent || '';
        return {
          disabled: inp?.disabled ?? true,
          hasError: bt.includes('Erro') && bt.includes('HTTP'),
          hasSending: bt.includes('…refinando…'),
        };
      });
      if (!state.disabled && !state.hasSending) { done = true; break; }
      if (state.hasError) { console.log('  ⚠ erro detectado'); break; }
      if (i % 12 === 0) console.log(`  ... ainda aguardando (${i*5}s decorridos)`);
      await page.waitForTimeout(5000);
    }
    if (!done) console.log('  ⚠ timeout de 15min no polling');
  }
  await page.waitForTimeout(3000);
  await snap(page, 'passo1-05-refino2-pronto');
  reg('refinamento-2', 'concluído');

  const pos2 = await page.evaluate(() => {
    const bt = document.body.textContent || '';
    return {
      score: (bt.match(/score (\d+)\/100/) || [])[1] || '?',
      problemas: (bt.match(/(\d+) problemas/) || [])[1] || '?',
      tabelas: (bt.match(/Tabelas: (\d+)/) || [])[1] || '?',
    };
  });
  reg('estado-pos-refino2', `${pos2.tabelas} tabelas, score=${pos2.score}/100, ${pos2.problemas} problemas`);

  // ═══════ APROVAR ═══════
  reg('aprovacao', 'Clicando Aprovar…');
  await page.locator('button:has-text("Aprovar")').first().click();
  await page.waitForTimeout(3500);
  await snap(page, 'passo1-06-aprovado');

  const aprovado = await page.evaluate(() => {
    const bt = document.body.textContent || '';
    return {
      aprovado: bt.includes('Aprovado'),
      rascunho: bt.includes('Rascunho'),
    };
  });
  reg('aprovacao', `aprovado=${aprovado.aprovado} rascunho=${aprovado.rascunho}`);

  // Salva log
  fs.writeFileSync(OUT + '/../passo1-log.json', JSON.stringify(eventos, null, 2));
  console.log('\n=== EVENTOS ===');
  eventos.forEach(e => console.log(`  ${e.ts.slice(11,19)} · ${e.passo} · ${e.obs}`));
});
