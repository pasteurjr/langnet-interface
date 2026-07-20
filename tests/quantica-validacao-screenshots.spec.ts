import { test, expect } from '@playwright/test';
import * as fs from 'fs';

const PID = 'b55ef718-0073-44d4-b279-11df89403e92';
const BASE = 'http://localhost:3000';
const TOK = fs.readFileSync('/tmp/uso-solo-pipeline/tok.txt', 'utf8').trim();
const OUT = '/tmp/uso-solo-pipeline/shots2';

const STAGES: [string, string][] = [
  ['00-documentos', `/project/${PID}/documents`],
  ['01-especificacao', `/project/${PID}/specification`],
  ['02-modelo-dados', `/project/${PID}/data-model`],
  ['03-casos-teste', `/project/${PID}/test-cases`],
  ['04-interface', `/project/${PID}/ui-spec`],
  ['05-agent-task-spec', `/project/${PID}/agent-task`],
  ['06-agents-yaml', `/project/${PID}/agents`],
  ['07-tasks-yaml', `/project/${PID}/tasks`],
  ['08-sequencia-tarefas', `/project/${PID}/task-execution-flow`],
  ['09-rede-petri', `/project/${PID}/petri-net`],
  ['10-codigo', `/project/${PID}/code-generation`],
];

test('captura telas Quântica', async ({ page }) => {
  test.setTimeout(240000);
  fs.mkdirSync(OUT, { recursive: true });

  // injeta token ANTES de qualquer script da app
  await page.addInitScript((t) => {
    localStorage.setItem('accessToken', t);
    localStorage.setItem('token', t);
  }, TOK);

  await page.setViewportSize({ width: 1600, height: 1000 });

  for (const [name, path] of STAGES) {
    await page.goto(BASE + path, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    // dá tempo pro fetch da etapa preencher o viewer; Petri (JointJS) carrega mais devagar
    await page.waitForTimeout(name.includes('petri') ? 9000 : 5000);
    await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true }).catch(async () => {
      await page.screenshot({ path: `${OUT}/${name}.png` });
    });
    console.log(`[shot] ${name}  ${path}`);
  }
});
