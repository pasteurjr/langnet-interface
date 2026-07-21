import { test } from '@playwright/test';
import * as fs from 'fs';

const PID = 'b55ef718-0073-44d4-b279-11df89403e92';
const BASE = 'http://localhost:3000';
const TOK = fs.readFileSync('/tmp/uso-solo-pipeline/tok.txt', 'utf8').trim();
const OUT = '/tmp/uso-solo-pipeline/shots-app';

// telas globais + config + operação + interação + projeto (as de pipeline já estão em shots2)
const SCREENS: [string, string][] = [
  ['g00-dashboard', `/`],
  ['g01-projetos', `/projects`],
  ['g02-projeto-detalhe', `/projects/${PID}`],
  ['cfg01-mcp-config-global', `/mcp/config`],
  ['cfg02-mcp-descoberta-servicos', `/mcp/services`],
  ['cfg03-mcp-sincronizacao', `/mcp/state-sync`],
  ['cfg04-configuracoes', `/settings`],
  ['cfg05-ajuda', `/help`],
  ['op01-deploy', `/deployment`],
  ['op02-monitoramento', `/monitoring`],
  ['int01-chat-agentes', `/interactive/agent-chat`],
  ['int02-designer-agentes', `/interactive/agent-designer`],
  ['int03-gestao-artefatos', `/interactive/artifacts`],
  ['int04-estado-sistema', `/interactive/system-state`],
  ['int05-formularios-dinamicos', `/interactive/forms`],
  ['proj-mcp', `/project/${PID}/mcp`],
];

test('captura telas app LangNet', async ({ page }) => {
  test.setTimeout(240000);
  fs.mkdirSync(OUT, { recursive: true });
  await page.addInitScript((t) => {
    localStorage.setItem('accessToken', t);
    localStorage.setItem('token', t);
  }, TOK);
  await page.setViewportSize({ width: 1600, height: 1000 });
  for (const [name, path] of SCREENS) {
    await page.goto(BASE + path, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    await page.waitForTimeout(4500);
    await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true }).catch(async () => {
      await page.screenshot({ path: `${OUT}/${name}.png` });
    });
    console.log(`[shot] ${name}  ${path}`);
  }
});
