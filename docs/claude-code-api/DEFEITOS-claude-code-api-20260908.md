# Claude Code API — 2 defeitos medidos em 08/09/2026

Ambiente: `https://camerascasas.no-ip.info:4443` (= `https://192.168.1.100:4443`, mesmo servidor).
Cliente: CrewAI 1.15.17 (SDK nativo da OpenAI, SEM litellm) + openai SDK.

O tool calling está FUNCIONANDO — confirmado ponta a ponta (`finish_reason: tool_calls`, volta em
`role: tool`, e a função Python executou de verdade sob CrewAI). Os dois defeitos abaixo são outros.

---

## DEFEITO 1 (GRAVE) — histórico de OUTRAS requisições vaza para dentro de uma requisição nova

### O que acontece
Uma requisição que manda APENAS `[{"role":"user","content":"..."}]`, sem histórico nenhum, às vezes
responde usando conversas de requisições anteriores — inclusive de outros chamadores.

### Reprodução
```bash
B=https://camerascasas.no-ip.info:4443
K=<token>

# 1) manda um segredo numa requisição
curl -sk -X POST $B/v1/chat/completions -H "Authorization: Bearer $K" -H "Content-Type: application/json" \
 -d '{"model":"claude-code","messages":[{"role":"user","content":"Memorize a palavra ABACAXI-7731. Responda apenas OK."}]}'

# 2) requisição SEPARADA, sem histórico. Repita 6x.
curl -sk -X POST $B/v1/chat/completions -H "Authorization: Bearer $K" -H "Content-Type: application/json" \
 -d '{"model":"claude-code","messages":[{"role":"user","content":"Que palavra eu pedi para memorizar? Se nao souber responda NAO SEI."}]}'
```

### Observado
- Em 6 repetições idênticas: **5 responderam "NAO SEI", 1 respondeu "ABACAXI-7731"**.
- Numa requisição limpa perguntando o assunto da mensagem anterior, respondeu sobre **um cálculo de
  escore de risco de Cox de um paciente de 68 anos com APACHE II 22** — chamada que NÃO era minha,
  de outra sessão usando a mesma API.
- O modelo usa a expressão "no histórico que tenho em contexto" nas respostas — ou seja, o histórico
  está sendo INJETADO no prompt, não é o modelo lembrando.
- `GET /v1/context` devolve `total_interactions: 20` com as últimas 20 conversas de QUALQUER chamador.
- `GET /health` devolve `context_items`, acompanhando o mesmo número.

### Sintoma que indica a causa provável
`DELETE /v1/context` respondeu `{"status":"cleared"}` **mas o `GET /health` seguinte continuou
dizendo `context_items: 20`**; minutos depois, outra leitura dizia `0`. Depois de duas requisições
consecutivas, `context_items` marcava `1`, não `2`.

Isso é o padrão de **estado em memória por processo com mais de um worker** (ex.: uvicorn com
`--workers N`): cada worker tem a sua própria lista de contexto; o DELETE limpa só o worker que
atendeu a chamada; e o vazamento é intermitente porque depende de qual worker pegou a requisição.

### Esperado
Cada requisição HTTP deve ser **independente e isolada**. O único contexto considerado deve ser o
array `messages` que veio NA requisição. Nada de estado global entre chamadas, e nada de mistura
entre chamadores diferentes.

### Por que isso é bloqueante aqui
A API alimenta um gerador de aplicações: cada etapa do pipeline (requisitos, especificação, modelo
de dados, tarefas, código) é uma chamada independente sobre um projeto diferente. Com esse
vazamento, a especificação de um projeto entra no prompt de outro, sem aviso, de forma
intermitente — e o resultado muda entre execuções sem nenhuma mudança de entrada. É praticamente
impossível depurar do lado de cá, porque não aparece em lugar nenhum da requisição.

### Correções pedidas (em ordem de preferência)
1. **Desligar a injeção de histórico por padrão.** A requisição já traz tudo em `messages`.
2. Se o histórico serve para algum uso interativo, torná-lo **opt-in explícito** — um campo no corpo
   (`"usar_historico": true`) ou um cabeçalho (`X-Usar-Historico: 1`). O padrão deve ser não usar.
3. Se ficar em memória, **isolar por chave/sessão** (o token do chamador ou um `session_id` que o
   cliente manda), nunca global, e fazer o `DELETE /v1/context` valer para todos os workers
   (armazenamento compartilhado, ou 1 worker só).

---

## DEFEITO 2 (MENOR) — `stream: true` é aceito mas não transmite

### O que acontece
Com `"stream": true`, a API responde **um único objeto JSON completo** (`object: chat.completion`),
em vez do formato de eventos (`text/event-stream` com linhas `data: {...}` e `[DONE]`).

### Reprodução
```bash
curl -sk -N -X POST $B/v1/chat/completions -H "Authorization: Bearer $K" -H "Content-Type: application/json" \
 -d '{"model":"claude-code","messages":[{"role":"user","content":"Conte de 1 a 5, um numero por linha."}],"stream":true}'
```
Observado: `{"id":"chatcmpl-...","object":"chat.completion","choices":[{"message":{...}}],...}` — resposta inteira, sem frames.

### Consequência do lado do cliente
O SDK da OpenAI em modo streaming espera frames SSE; recebendo um corpo JSON simples, ele entrega
**zero pedaços** e a resposta chega vazia — falha silenciosa. Tivemos que desligar streaming só
para este provedor. Além do incômodo, em geração longa o streaming é o que mantém a conexão viva.

### Esperado
Ou implementar o streaming de verdade (`text/event-stream`, `object: chat.completion.chunk`,
terminando em `data: [DONE]`), ou **recusar explicitamente** com um erro claro
(ex.: 400 "streaming não suportado") em vez de aceitar e devolver outro formato.

---

## Observação menor (não é defeito, mas confunde)
O campo `usage` parece estimado: `"Some 15 e 27"` mais uma definição de ferramenta contou
`prompt_tokens: 4`. Se não houver contagem real disponível, vale documentar que é aproximado.

## O que NÃO precisa mudar
Tool calling: funcionando. Medido com CrewAI 1.15.17 usando
`LLM(model="claude-code", custom_openai=True, base_url=..., api_key=...)` — a ferramenta Python
executou de verdade (registro interno + a resposta final igual ao retorno da função).
Atenção: o prefixo `openai/claude-code` sugerido nas instruções **exige litellm**, que não está
instalado neste ambiente; ali o CrewAI recusa com "LiteLLM fallback package is not installed".
