# BioByte Sentinela — o que o sistema TEM QUE FAZER × o que ESTÁ LÁ

Comparação tela a tela entre o que a **Especificação** manda (fluxo do caso de uso + wireframe
aprovado) e o que o **aplicativo gerado** entrega. Três colunas: o exigido, o que existia antes
desta rodada, e o que existe depois das correções feitas no gerador.

Isto não é um relatório de teste. É a conferência que faltava: comparar o desenho aprovado com
a interface que saiu, campo por campo.

---

## Resumo

| | Antes | Depois |
|---|---|---|
| Telas de negócio com o conteúdo especificado | 2 de 12 | 12 de 12 |
| Telas que nasciam com **só um título e um botão** | 7 | 0 |
| Cartões de indicador exigidos pela especificação | 4 exigidos, 0 renderizados | 4 renderizados |
| Gráficos exigidos | 3 exigidos, 0 renderizados | 3 renderizados |
| Tabelas exigidas dentro de telas de negócio | 2 exigidas, 0 renderizadas | 2 renderizadas |
| Listas de itens (protocolo de tratamento) | 1 exigida, 0 | 1 |
| Marcações de critério (norma NHSN) | 3 exigidas, 0 | 3 |
| Texto de outro domínio ("Shapefile/GeoJSON") em tela de hospital | 4 telas | 0 |

**A causa era uma só.** A Especificação de Interface declarava tudo isso corretamente — cartão de
indicador, gráfico, tabela, valor de leitura, marcação, lista. O gerador de código só sabia
desenhar campo de texto, número, data e seleção, e **descartava silenciosamente** todo o resto.
Por isso o Dashboard de Vigilância, que a especificação define com três indicadores e dois
gráficos, nascia com um título e um botão.

---

## Tela a tela

### UC-001 — Autenticar Usuário com MFA · tela "Login e MFA"
**Exigido:** e-mail, senha, botão Entrar; depois código MFA com validade, botões Confirmar e
Reenviar código; mensagens "Credenciais inválidas" e "Código incorreto".
**Antes:** os três campos e um botão. As mensagens especificadas não existiam — o usuário via
"verificação (pós) falhou: output_has:usuario_id".
**Depois:** os três campos, o botão, e as mensagens do caso de uso na tela. *Continua faltando:*
o contador de validade do código e o botão Reenviar (não há tarefa de reenvio no sistema).

### UC-002 — Iniciar Importação · tela "Importação de Microbiologia"
**Exigido:** paciente e caso em leitura, campo ID da Amostra, botões Consultar Externo e Cancelar.
**Antes:** só o campo da amostra e um botão. Paciente e caso não apareciam.
**Depois:** paciente e caso exibidos em leitura a partir do caso aberto, o campo da amostra e o
botão. *Continua faltando:* o botão Cancelar (não corresponde a nenhuma tarefa).

### UC-003 — Integração com o laboratório · tela "Prévia de Resultados"
**Exigido:** amostra, microrganismo, lista de sensibilidades, botões Confirmar Importação e Descartar.
**Antes:** nenhum campo. Só um botão. O resultado saía como JSON cru.
**Depois:** amostra, microrganismo e sensibilidades exibidos em leitura; o resultado do laboratório
aparece com nome de negócio. Dado fora do padrão bloqueia a importação com a mensagem certa.

### UC-004 — Classificar conforme NHSN · tela "Detalhe do Caso Clínico"
**Exigido:** paciente, selo de status (ICSAC Confirmado / Não ICSAC / Classificação Pendente) e as
três marcações dos critérios: cateter presente, hemocultura positiva, correlação clínica.
**Antes:** nenhum campo, nenhum critério, nenhum selo. Um botão "Confirmar Importação" e uma caixa
para arrastar **"Shapefile/GeoJSON"** — resíduo de outro projeto, num sistema de hospital.
**Depois:** paciente, status, classificação e data em leitura; as três marcações da norma refletindo
a resposta do agente; o selo colorido quando a classificação vem no vocabulário especificado; a
justificativa citando a regra aplicada. Sem o texto geoespacial.

### UC-005 — Alerta de multirresistência · tela "Alerta MDR"
**Exigido:** aviso destacado, microrganismo e as classes de resistência, botões para ver o
microrganismo e sugerir bundle de isolamento.
**Antes e depois:** os seis campos declarados aparecem. *Continua faltando:* o alerta não é enviado
por e-mail nem por notificação — o sistema grava o alerta, não avisa ninguém.

### UC-006 — Escore de risco (Cox) · tela "Detalhe do Caso"
**Exigido:** escore numérico, barra de nível de risco, lista de fatores de risco, botão Calcular.
**Antes:** os campos existiam, mas o resultado saía como texto; sem barra.
**Depois:** escore com **barra de progresso** (24%, nível Baixo), fatores de risco listados e o
modelo usado. O cálculo recusa quando faltam os parâmetros clínicos, listando quais faltam.

### UC-007 — Recomendar bundle · tela "Recomendação de Bundle"
**Exigido:** nome do bundle, justificativa, lista dos itens do protocolo, botões Aprovar e Rejeitar.
**Antes:** nenhum campo. Um botão. Nem nome, nem justificativa, nem itens.
**Depois:** "Bundle MRSA Cateter-Relacionado", a justificativa clínica completa (idade, UTI, dias de
cateter, nutrição parenteral, APACHE II, escore), microrganismo associado e status de
multirresistência. *Continua faltando:* o botão Rejeitar (sem tarefa correspondente).

### UC-008 — Estimar redução de risco · tela "Resultado da Estimativa"
**Exigido:** redução de risco, intervalo de confiança de 95%, bundle aprovado.
**Antes:** nenhum campo; um gráfico de barras genérico que nunca tinha dados.
**Depois:** os três valores como cartão de indicador e valores de leitura. Sem tratamento aprovado,
o agente **declara dados insuficientes** em vez de inventar um número.

### UC-009 — Dashboard de Vigilância
**Exigido:** três indicadores (casos ICSAC em 30 dias, taxa de MDR, escore médio), gráfico de
evolução de casos e gráfico de distribuição.
**Antes:** **título e um botão.** Nada mais.
**Depois:** os três indicadores preenchidos com dados reais do banco (taxa de MDR 56,5%, escore
médio 0,2437) e os dois gráficos, que dizem "sem dados para o período" enquanto não há série —
em vez de fingir que há.

### UC-010 — Gerenciar Usuários · tela "Gestão de Usuários"
**Exigido:** busca, botão Novo Usuário e **tabela** de usuários com nome, e-mail, papel e ações.
**Antes:** o formulário de cadastro, sem tabela nenhuma. Não dava para ver os usuários existentes.
**Depois:** a tabela de usuários além do formulário; a senha deixou de ser campo de texto aberto.

### UC-011 — Consultar Logs de Auditoria
**Exigido:** filtros de período e usuário, botões Filtrar e Exportar CSV, tabela com data/hora,
usuário, ação e IP.
**Antes:** os quatro filtros; a consulta devolvia vazio mesmo com registros.
**Depois:** filtros, tabela de registros, exportação em CSV e a mensagem "Nenhum registro
encontrado para os filtros aplicados" quando o período não tem nada.

### UC-012 — Exportar Relatório de Vigilância
**Exigido:** formato, período, filtro de paciente, botão Gerar Relatório e o download do arquivo.
**Antes:** os campos existiam; **nenhum arquivo era gerado** — a tarefa devolvia os dados e pronto.
**Depois:** o arquivo é gerado de fato, em PDF e em CSV, e o caminho volta na resposta.

---

## O que continua fora, e por quê

| O que falta | Por quê |
|---|---|
| Envio de e-mail e notificação por push do alerta MDR | não implementado no sistema gerado |
| Contador de validade e reenvio do código MFA | não há tarefa de reenvio |
| Botões Cancelar, Descartar, Rejeitar, Voltar | não correspondem a nenhuma tarefa; preferi não desenhar botão de enfeite |
| Tratamento de tempo esgotado e processamento assíncrono | não implementados |
| Carregamento animado durante consultas lentas | não implementado |
| Casos de teste do caso de uso de gestão de usuários | a etapa de Casos de Teste não gerou nenhum para o UC-010 |

## Correções feitas no gerador nesta rodada

Todas no gerador, nenhuma no aplicativo, cada uma seguida de regeneração e implantação pela
interface do LangNet:

1. a tela passa a renderizar **todos** os tipos de componente declarados (indicador, gráfico de
   linha, gráfico de pizza, tabela, lista, valor de leitura, marcação);
2. a Especificação funcional passou a chegar ao gerador de código, levando junto o vocabulário
   que cada tela deve exibir;
3. o valor é buscado pelo nome declarado e, se o agente devolver nome diferente, por semelhança —
   nunca por posição;
4. metadado da chamada (status, carimbo de tempo) deixou de ser tratado como dado clínico;
5. as marcações de critério refletem a resposta do agente;
6. campo de senha deixou de ser texto aberto;
7. fim do texto geoespacial herdado de outro projeto.
