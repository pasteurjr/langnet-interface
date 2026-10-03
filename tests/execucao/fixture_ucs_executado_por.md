## 5. Casos de Uso

#### UC-001: Autenticar Usuário com E-mail e Senha

| Campo | Detalhe |
|-------|---------|
| **Ator Principal** | médico; enfermeiro; administrador |
| **Atores Secundários** | servidor |
| **Natureza** | **convencional** |
| **Decisão do Agente** | Não se aplica. |
| **Objetivo** | Permitir que o usuário entre no sistema informando e-mail e senha, sem segundo fator, mantendo a identidade durante todo o uso e protegendo o acesso por token. |
| **Pré-condições** | O usuário deve estar previamente cadastrado e ativo (ver UC-002). O servidor deve estar no ar e com a configuração de segurança carregada. |
| **Pós-condições** | O usuário está autenticado, o sistema mantém sua identidade durante o uso e um token de acesso foi emitido e é verificado em cada requisição. A senha permanece armazenada apenas como resumo criptográfico com sal e nunca aparece em logs, erros ou telas. |
| **RFs Relacionados** | FR-001, FR-004, FR-064, FR-065, FR-066, FR-096 |
| **RNs Aplicáveis** | BR-002, BR-019, BR-020 |

#### Fluxo Principal

| # | Ação do Ator | Resposta do Sistema |
|---|--------------|---------------------|
| 1 | O usuário acessa a aplicação e o sistema apresenta a tela **"Login"**. | O sistema exibe a tela **"Login"** com os campos **"E-mail"** e **"Senha"**, o botão **"Entrar"** e a mensagem de rodapé **"Acesso sem segundo fator, conforme decisão da CCIH"**. |
| 2 | O usuário preenche o campo **"E-mail"** com seu e-mail institucional. | O sistema aceita a digitação e não revela se o e-mail existe ou não na base. |
| 3 | O usuário preenche o campo **"Senha"**. | O sistema mascara os caracteres digitados no campo **"Senha"** e não registra o valor em nenhum log. |
| 4 | O usuário clica no botão **"Entrar"**. | O sistema aplica a limitação de taxa às chamadas de autenticação (FR-096) e, dentro do limite, valida e-mail e senha contra o resumo criptográfico com sal armazenado (FR-065). |
| 5 | O usuário aguarda a validação. | O sistema confirma as credenciais, emite o **token de acesso** no login e registra a entrada na trilha de auditoria com o identificador do usuário (FR-005). |
| 6 | O usuário é conduzido ao sistema. | O sistema mantém a identidade do usuário autenticado durante todo o uso, sem exigir nova identificação a cada tela (FR-004), e exibe a tela inicial com o nome do usuário e seu **papel** no cabeçalho. |
| 7 | O usuário navega entre as telas do sistema. | O servidor exige, em toda chamada recebida, o **token de acesso** emitido no login e verificado em cada requisição; se o token não vier ou estiver vencido, o servidor recusa a chamada independentemente do que a tela enviou (FR-064). |

#### Fluxos Alternativos

| ID | Condição | Ação do Ator | Resposta do Sistema |
|----|----------|--------------|---------------------|
| A1 | O usuário ainda não tem cadastro no sistema. | O usuário clica no link **"Falar com o administrador para solicitar acesso"** na tela **"Login"**. | O sistema exibe a mensagem **"O acesso é criado pelo administrador do sistema. Solicite o cadastro ao administrador do hospital."** e não permite autocadastro. |
| A2 | O usuário deseja limpar os campos preenchidos antes de enviar. | O usuário clica no botão **"Limpar"** na tela **"Login"**. | O sistema apaga o conteúdo dos campos **"E-mail"** e **"Senha"** e mantém o foco no campo **"E-mail"**. |
| A3 | O usuário está autenticado e o token de acesso vence durante o uso. | O usuário tenta executar uma ação em qualquer tela. | O servidor recusa a chamada, a sessão expira e o sistema retorna à tela **"Login"** com a mensagem **"Sua sessão expirou. Entre novamente."** |
| A4 | O usuário é desativado enquanto está autenticado. | O usuário tenta executar uma ação em qualquer tela. | O servidor recusa a chamada por o usuário não estar ativo e o sistema retorna à tela **"Login"** com a mensagem **"Usuário desativado. Procure o administrador do sistema."** |

#### Fluxos de Exceção

| ID | Erro/Problema | Resposta do Sistema |
|----|--------------|---------------------|
| E1 | E-mail ou senha incorretos. | O sistema exibe na tela **"Login"** a mensagem **"E-mail ou senha inválidos."**, mantém o campo **"E-mail"** preenchido, limpa o campo **"Senha"** e não informa qual dos dois está errado. |
| E2 | O campo **"E-mail"** ou o campo **"Senha"** foi enviado vazio. | O sistema exibe a mensagem **"Informe e-mail e senha para entrar."** e não realiza a validação de credenciais. |
| E3 | O limite de tentativas de autenticação foi excedido (FR-096). | O sistema bloqueia temporariamente novas tentativas, exibe a mensagem **"Muitas tentativas de login. Tente novamente mais tarde."** e registra o bloqueio na trilha de auditoria. |
| E4 | O servidor está indisponível. | O sistema exibe a mensagem **"Não foi possível conectar ao servidor. Tente novamente."** com o botão **"Tentar novamente"**, sem simular login bem-sucedido. |
| E5 | A senha digitada aparece em algum ponto do processo. | O sistema não exibe nem registra a senha em log, mensagem de erro ou tela (FR-066); qualquer ocorrência é tratada como falha de segurança e bloqueada pela área de segurança do hospital. |

#### Autenticação e Autorização

O login é feito exclusivamente com e-mail e senha, sem código enviado por mensagem e sem aplicativo autenticador (FR-001), por inviabilidade de uso na UTI, onde a pessoa às vezes está de luva. O **papel** do usuário (médico, enfermeiro ou administrador) é carregado no momento do login e determina o que cada usuário enxerga e pode fazer durante a sessão. O servidor não confia na tela: o **token de acesso** é verificado em cada requisição (BR-020) e a sessão expira exigindo novo login.

#### Dados Sensíveis e LGPD

A senha é armazenada apenas como resumo criptográfico com **sal**, nunca em texto aberto (FR-065), e não aparece em registro de log, mensagem de erro ou tela (FR-066). O e-mail do usuário é dado pessoal e não é usado para nenhuma finalidade além da autenticação e da identificação na trilha de auditoria. Nenhum dado do paciente trafega nesta tela.

#### Registros de Auditoria

Cada tentativa de login é registrada na trilha de auditoria com o usuário (quando identificado), o resultado (sucesso, credencial inválida, bloqueio por limite de tentativas) e a data/hora. Todo registro de auditoria traz o usuário que executou a ação (FR-005), e a validação de token é registrada por requisição (FR-064).

#### Riscos de Segurança e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Ataque de força bruta contra o login, agravado pela ausência de segundo fator. | Limitação de taxa nas chamadas de autenticação, bloqueio temporário e registro em auditoria (FR-096). |
| Vazamento de senha em logs, erros ou telas. | Proibição de exibir ou registrar a senha (FR-066) e armazenamento apenas com hash e sal (FR-065). |
| Uso de token roubado ou vencido. | Verificação do token em cada requisição e expiração da sessão exigindo novo login (FR-064). |
| Adivinhação de credenciais por mensagem genérica. | Mensagem única **"E-mail ou senha inválidos."**, sem revelar qual campo está errado. |

#### Wireframe da Interface

**Tela:** Login

```
┌─────────────────────────────────────────────┐
│  Login                                      │
├─────────────────────────────────────────────┤
│  E-mail: [____________________________]     │
│  Senha:  [____________________________]     │
│                                             │
│  [ Entrar ]   [ Limpar ]                    │
│                                             │
│  Falar com o administrador para solicitar   │
│  acesso                                     │
│                                             │
│  Acesso sem segundo fator, conforme decisão │
│  da CCIH                                    │
└─────────────────────────────────────────────┘
```

---

---

**UC-011: Identificar Multirresistência no Antibiograma**

| Campo | Detalhe |
|-------|---------|
| **Ator Principal** | agente de IA |
| **Atores Secundários** | sistema; médico |
| **Natureza** | **agêntica** |
| **Decisão do Agente** | Examinar a lista de antimicrobianos do antibiograma e julgar se o microrganismo isolado é multirresistente, aplicando a regra de resistência a três ou mais classes. |
| **Objetivo** | Ler o antibiograma recebido do laboratório, interpretar cada antimicrobiano com sua classe e resultado, e decidir se o microrganismo é multirresistente, deixando o resultado disponível para o médico e para os fluxos de alerta e recomendação. |
| **Pré-condições** | O resultado de hemocultura foi importado do laboratório com antibiograma preenchido (FR-019, FR-023). O resultado não está marcado como "pendente" nem contém mensagem de erro (FR-020, FR-021). O caso está associado ao resultado importado. |
| **Pós-condições** | O sistema registra a decisão de multirresistência (sim/não) associada ao caso e ao antibiograma, com a lista de antimicrobianos e classes que sustentaram a decisão. A decisão fica rastreável até a origem do dado (FR-070) e disponível para os fluxos de alerta (FR-033) e recomendação (FR-041). |
| **RFs Relacionados** | FR-031, FR-032, FR-080 |
| **RNs Aplicáveis** | BR-009 |

#### Fluxo Principal

| # | Ação do Ator | Resposta do Sistema |
|---|--------------|---------------------|
| 1 | O sistema, ao concluir a importação do resultado de hemocultura, aciona o agente de IA para avaliar o antibiograma. | O sistema exibe na tela **"Detalhe do Caso Clínico"**, na seção **"Antibiograma"**, a lista de antimicrobianos com **"Antimicrobiano"**, **"Classe"** e **"Resultado"** (Sensível, Intermediário, Resistente). |
| 2 | O agente de IA lê a lista de antimicrobianos do antibiograma. | O sistema apresenta o indicador **"Avaliando multirresistência..."** na seção **"Multirresistência"**. |
| 3 | O agente de IA agrupa os antimicrobianos por classe e conta quantas classes apresentam resultado **"Resistente"**. | O sistema mantém a seção **"Multirresistência"** em estado de processamento, sem exibir valor inventado. |
| 4 | O agente de IA decide se o microrganismo é multirresistente, aplicando a regra de três ou mais classes resistentes. | O sistema exibe na seção **"Multirresistência"** o campo **"Multirresistente"** com o valor *Sim* ou *Não* e o campo **"Classes resistentes identificadas"** com a contagem e a lista das classes. |
| 5 | O agente de IA registra a justificativa da decisão. | O sistema exibe o campo **"Justificativa da decisão"** com o texto que cita as classes resistentes encontradas, e o botão **"Ver antibiograma completo"**. |
| 6 | O médico, na tela **"Detalhe do Caso Clínico"**, consulta a seção **"Multirresistência"**. | O sistema apresenta o resultado da decisão, a contagem de classes resistentes, a justificativa e o link **"Ver antibiograma completo"**, sem exigir nova ação do médico. |

#### Fluxos Alternativos

| ID | Condição | Ação do Ator | Resposta do Sistema |
|----|----------|--------------|---------------------|
| A1 | O antibiograma tem menos de três classes resistentes. | O agente de IA avalia a lista e conclui pela ausência de multirresistência. | O sistema exibe na seção **"Multirresistência"** o campo **"Multirresistente"** com o valor *Não* e a justificativa citando as classes resistentes encontradas. |
| A2 | O antibiograma possui antimicrobianos com resultado *Intermediário*. | O agente de IA avalia a lista considerando *Intermediário* como não resistente para a contagem de classes. | O sistema exibe a decisão com a justificativa explicitando que os resultados *Intermediário* não foram contados como resistência. |
| A3 | O médico clica em **"Ver antibiograma completo"**. | O médico abre o detalhamento do antibiograma. | O sistema exibe o painel **"Antibiograma Completo"** com todos os antimicrobianos, suas classes e resultados, destacando as classes contadas como resistentes. |
| A4 | O caso não possui antibiograma importado (resultado pendente ou com erro). | O agente de IA não é acionado. | O sistema exibe na seção **"Multirresistência"** a mensagem **"Não há antibiograma disponível para avaliar multirresistência."** e mantém o campo **"Multirresistente"** vazio. |

#### Fluxos de Exceção

| ID | Erro/Problema | Resposta do Sistema |
|----|--------------|---------------------|
| E1 | O antibiograma vem sem a classe de um ou mais antimicrobianos. | O sistema exibe na seção **"Multirresistência"** a mensagem **"Não foi possível avaliar multirresistência: classe ausente em um ou mais antimicrobianos."** e não emite decisão. |
| E2 | O agente de IA falha ao interpretar o antibiograma. | O sistema exibe na seção **"Multirresistência"** a mensagem **"Não foi possível avaliar multirresistência. Tente novamente."** e mantém o campo **"Multirresistente"** vazio, sem inventar resultado. |
| E3 | O resultado de hemocultura está marcado como "pendente". | O sistema exibe a mensagem **"Resultado pendente no laboratório. Não há antibiograma para avaliar."** e não aciona o agente de IA. |
| E4 | O resultado de hemocultura contém mensagem de erro de cadastro. | O sistema exibe a mensagem **"Resultado com erro de cadastro no laboratório. Não há antibiograma para avaliar."** e não aciona o agente de IA. |
| E5 | A lista de antimicrobianos está vazia. | O sistema exibe a mensagem **"Antibiograma sem antimicrobianos. Não foi possível avaliar multirresistência."** e não emite decisão. |

#### 🔴 Subseções Específicas Pedidas pelas Instruções Customizadas

**Autenticação/Autorização:** a consulta ao resultado pelo médico exige token de acesso válido (FR-064). O agente de IA opera no servidor, sem acesso direto à tela. O enfermeiro não executa esta ação; o administrador não acessa dado clínico (FR-067).

**Dados Sensíveis / LGPD:** o antibiograma é dado clínico do paciente. A chamada ao laboratório é feita com dados anonimizados (FR-069, NFR-010). Nenhum dado identificável do paciente é enviado ao agente.

**Registros de Auditoria:** a decisão do agente é registrada com entrada (antibiograma), saída (multirresistente sim/não), classes resistentes identificadas, justificativa e data/hora, rastreável até a origem do dado (FR-070, BR-030).

**Riscos de Segurança e Mitigações:** risco de decisão sem evidência — mitigado pela justificativa obrigatória que cita as classes resistentes e pela exibição do antibiograma completo. Risco de invenção de resultado — mitigado pela proibição de exibir valor inventado quando a avaliação falha (FR-063, BR-016).

#### Wireframe da Interface

**Tela:** Detalhe do Caso Clínico — seção "Multirresistência"

```
┌───────────────────────────────────────────────────────────────┐
│  Detalhe do Caso Clínico                                      │
├───────────────────────────────────────────────────────────────┤
│  Seção: Antibiograma                                          │
│  ┌──────────────────┬────────────────────┬──────────────────┐ │
│  │ Antimicrobiano   │ Classe             │ Resultado        │ │
│  ├──────────────────┼────────────────────┼──────────────────┤ │
│  │ [nome]           │ [classe]           │ Resistente       │ │
│  │ [nome]           │ [classe]           │ Sensível         │ │
│  │ [nome]           │ [classe]           │ Intermediário    │ │
│  └──────────────────┴────────────────────┴──────────────────┘ │
├───────────────────────────────────────────────────────────────┤
│  Seção: Multirresistência                                     │
│  Multirresistente: [ Sim / Não ]                              │
│  Classes resistentes identificadas: [contagem] — [lista]      │
│  Limiar da regra: 3 classes resistentes (BR-009)              │
│  Justificativa da decisão:                                    │
│  [texto gerado pelo agente citando as classes resistentes]    │
│  [ Ver antibiograma completo ]                                │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  Painel: Antibiograma Completo                                │
├───────────────────────────────────────────────────────────────┤
│  ┌──────────────────┬────────────────────┬──────────────────┐ │
│  │ Antimicrobiano   │ Classe             │ Resultado        │ │
│  ├──────────────────┼────────────────────┼──────────────────┤ │
│  │ [nome]           │ [classe] *         │ Resistente       │ │
│  │ [nome]           │ [classe] *         │ Resistente       │ │
│  │ [nome]           │ [classe] *         │ Resistente       │ │
│  └──────────────────┴────────────────────┴──────────────────┘ │
│  * classes contadas como resistentes                          │
└───────────────────────────────────────────────────────────────┘
```
