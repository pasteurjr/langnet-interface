# Claude Code API — revalidação do commit 7b8efdc e 4 pedidos

Medido em 09/09/2026 a partir de 192.168.1.115, contra https://camerascasas.no-ip.info:4443.
Cliente: SDK OpenAI e CrewAI 1.15.17 (provedor nativo da OpenAI, sem litellm).

## Confirmado corrigido — obrigado

**Vazamento de contexto:** rodei a mesma reprodução do relatório anterior (ABACAXI-7731, seis
requisições independentes seguidas): **0 de 6 vazaram** (antes 1 de 6). `GET /v1/context` devolve 0.
Seis leituras de `context_items` depois do `DELETE`: `0 0 0 0 0 0`.
*Não pude testar o isolamento ENTRE chaves diferentes — só tenho uma chave. Se você tiver duas,
vale a prova cruzada: gravar com a chave A e tentar ler com a chave B.*

**Streaming:** o SDK da OpenAI consome sem erro, os quadros vêm como `chat.completion.chunk` e
termina em `[DONE]`. A falha silenciosa (resposta vazia) acabou.

**Chamada de ferramenta:** continua funcionando depois das correções — ida e volta completa, e a
função Python executando de verdade sob CrewAI.

**usage:** o caso de `prompt_tokens: 4` agora dá 56. Estimativa, como você explicou. Está ok.

---

## PEDIDO 1 — batimento durante a geração (é o que mais me atrapalha hoje)

O formato do streaming está certo, mas **não chega byte nenhum enquanto o modelo gera**. Medi com
uma geração longa (texto técnico de 1500 palavras), marcando o tempo de chegada de cada linha:

```
 64.34s  data: {"id":"chatcmpl-7be0de83b748","object":"chat.completion.chunk"...
 64.34s  data: ...
 64.35s  data: ...        <- todos os quadros de uma vez, aos 64 segundos
```

64 segundos de silêncio absoluto, e depois tudo junto.

**Não estou pedindo entrega incremental** — entendi que o `claude -p` devolve de uma vez só, e tudo
bem. O problema é outro: uma conexão sem tráfego nenhum por minutos é derrubada por proxy, NAT ou
temporizador de leitura no meio do caminho, e do meu lado isso é indistinguível de um travamento.
As minhas gerações de documento levam vários minutos.

**O que peço:** enviar um batimento enquanto o CLI trabalha — uma linha de comentário SSE
(`: ping\n\n`) a cada 10 ou 15 segundos, até o primeiro quadro real. O SDK ignora comentários, então
não quebra nada e não muda o resultado.

**Por que importa para mim:** com os outros modelos eu uso o intervalo entre bytes para detectar
conexão morta e refazer a chamada rápido. Com esta API tive que desligar essa proteção, senão ela
mataria gerações legítimas. Com o batimento, eu religo o streaming e volto a ter a proteção.

---

## PEDIDO 2 — `include_context: true` está inerte (nada é gravado)

Sequência medida, nesta ordem:

1. `DELETE /v1/context`
2. uma requisição normal: "Memorize a palavra CAJU-55. Responda apenas OK." → respondeu OK
3. `GET /v1/context` → **`total_interactions: 0`**
4. requisição com `"include_context": true` perguntando a palavra → **"NÃO SEI"**

Ou seja: **nada está sendo gravado no histórico**, então a opção não tem o que injetar.

Para o meu uso isso está ótimo — eu quero isolamento total, e é exatamente o que preciso. Só estou
registrando a divergência: o comportamento hoje não é "opt-in", é "desligado". Se a gravação por
escopo deveria continuar funcionando, tem um defeito aí. Se você desligou de propósito, me diga que
eu paro de contar com a opção.

---

## PEDIDO 3 — a memória de projeto do CLI entra nas minhas chamadas (achado novo)

Isso não estava no relatório anterior. Nas respostas dos testes de vazamento, o modelo descreveu o
que tinha consultado:

> "Verifiquei minha **memória persistente deste projeto** (`~/.claude/projects/-mnt-kin...`)"
> "Meu **diretório de memória persistente** para este projeto está vazio (só existe um arquivo de lock)"

Ou seja: o CLI atrás da ponte roda dentro de um diretório de projeto e **lê a memória persistente
desse diretório**. Hoje ela está vazia, então não atrapalha nada.

**O risco:** se alguém usar aquela máquina para trabalhar e essa pasta ganhar conteúdo, esse
conteúdo passa a entrar em **todas** as minhas chamadas de geração. É exatamente a contaminação do
defeito 1 entrando por outra porta — e essa eu não consigo ver nem limpar daqui, porque não aparece
em requisição nenhuma.

**O que peço:** rodar o CLI da ponte com a memória de projeto desabilitada, ou dentro de um
diretório dedicado e vazio que ninguém use para trabalhar. E, se puder, me confirmar qual das duas
ficou, para eu registrar.

---

## PEDIDO 4 — o certificado vence em 18/09/2026 (nove dias)

O certificado apresentado em `:4443` é da Let's Encrypt, emitido para o nome
`camerascasas.no-ip.info`, válido de 20/06/2026 a **18/09/2026**.

Quando ele vencer, **o pipeline inteiro para de conectar** — e o sintoma vai ser um erro genérico de
conexão, que não parece ter nada a ver com certificado. Já perdi tempo com isso hoje por outro
motivo parecido.

**O que peço:** confirmar que a renovação automática está funcionando — normalmente
`certbot renew --dry-run` responde isso. Reparei que o nome sugere que o certificado foi criado
originalmente para outro serviço (as câmeras); se for o caso, a renovação pode depender daquele
serviço continuar de pé, o que vale checar.

**O que NÃO preciso:** um certificado que cubra o IP `192.168.1.100`. Resolvi isso do meu lado
(faço o nome resolver para o endereço local aqui na minha máquina, então o certificado do nome
continua valendo e o tráfego não sai da rede). Só a renovação me interessa.

---

## Contexto de por que estou cobrando essas coisas

Esta API alimenta um gerador de aplicações: cada etapa do pipeline (requisitos, especificação,
modelo de dados, tarefas, código, casos de teste) é uma chamada independente sobre um projeto
diferente, e várias delas levam minutos. Qualquer estado que atravesse requisições contamina
artefatos de projetos distintos sem deixar rastro, e qualquer conexão silenciosa vira travamento
que eu não consigo distinguir de erro.

Depois de aplicar, me diga o que ficou e eu revalido do mesmo jeito — com medição, não com
"deve estar funcionando".
