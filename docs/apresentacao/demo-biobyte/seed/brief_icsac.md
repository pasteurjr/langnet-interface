# BioByte Sentinela — Vigilância de ICSAC (Infecção de Corrente Sanguínea Associada a Cateter)

## Contexto e objetivo
Sistema para a Comissão de Controle de Infecção Hospitalar (CCIH) apoiar a **vigilância da Infecção de
Corrente Sanguínea Associada a Cateter Central (ICSAC / CLABSI)** em pacientes de UTI. O sistema prioriza
pacientes por risco, confirma o caso quando sai a hemocultura, e recomenda a conduta estimando o efeito do
pacote (bundle) de prevenção. Deve ser **auditável e rastreável** (software de saúde, LGPD).

## Escopo funcional (três frentes)
1. **Prognóstico / risco (avaliação de risco):** para cada paciente com cateter central, calcular um
   **escore de risco de ICSAC** a partir de fatores (dias de cateter, internação em UTI, nutrição parenteral,
   neutropenia, idade). Priorizar a vigilância pelos de maior risco. Base metodológica: escore de risco e
   **modelo de perigos proporcionais de Cox**.
2. **Diagnóstico:** ao chegar o resultado de **hemocultura/antibiograma** (integração externa com o laboratório),
   aplicar o **critério de definição de caso** (padrão NHSN) e **classificar**: é ICSAC confirmada? qual patógeno?
   é multirresistente? Base: classificação (regressão logística / florestas aleatórias).
3. **Tratamento / conduta:** recomendar o **bundle de prevenção** e a conduta, e **estimar a redução de risco**
   do bundle na coorte (efeito do tratamento). Base: **redução de risco absoluta** e **efeito médio do tratamento**.
4. **Laudo/notificação:** gerar o laudo/notificação da CCIH consolidando risco, classificação e conduta.

## Entidades principais (modelo de dados)
- **paciente**: nome, leito, em_uti (sim/não), comorbidades, neutropenia (sim/não), idade.
- **dispositivo**: paciente, tipo (cateter_central), data_insercao, dias_uso, nutricao_parenteral (sim/não).
- **cultura**: paciente, data_coleta, fonte (hemocultura), patogeno, perfil_resistencia (obtida via integração externa).
- **avaliacao_iras**: paciente, escore_risco, classificacao_caso (confirmada/descartada/pendente), conduta,
  reducao_risco_estimada, status.
- **laudo_ccih**: paciente, conteudo, data_emissao.

## Integrações externas (serão tools MCP)
- **consultar_microbiologia(paciente_id)** — consulta hemocultura e antibiograma no sistema laboratorial (LIS) externo.
- **escore_risco_cox(dias_cateter, uti, nutricao_parenteral, neutropenia, idade)** — serviço externo que calcula o
  escore de risco pelo modelo de Cox.

## Requisitos não-funcionais
- **LGPD / segurança:** dados de paciente protegidos; anonimização antes de chamadas externas.
- **Auditabilidade / rastreabilidade:** toda decisão (risco, classificação, conduta) registrada e rastreável até a origem.
- **Desempenho:** priorização do painel em poucos segundos; latência da consulta de microbiologia aceitável.
- **Confiabilidade:** operação contínua na rotina da CCIH.

## Caso de uso central
**Avaliar paciente sentinela:** cadastrar paciente e dispositivo → calcular escore de risco → importar
microbiologia e classificar o caso → recomendar conduta e estimar a redução de risco → emitir laudo da CCIH.
Prever fluxos alternativos (ex.: sem cultura disponível ainda; geometria/dado faltante) e de exceção
(ex.: paciente sem parâmetros; serviço de microbiologia indisponível).
