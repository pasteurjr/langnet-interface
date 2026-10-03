## 5. Casos de Uso

#### UC-001: Autenticar Usuário com E-mail e Senha

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O usuário acessa a aplicação e o sistema apresenta a tela **"Login"**. | O sistema exibe a tela **"Login"** com os campos **"E-mail"** e **"Senha"**, o botão **"Entrar"** e a mensagem de rodapé **"Acesso sem segundo fator, conforme decisão da CCIH"**. | pronto |
| 2 | O usuário preenche o campo **"E-mail"** com seu e-mail institucional. | O sistema aceita a digitação e não revela se o e-mail existe ou não na base. | pronto |
| 3 | O usuário preenche o campo **"Senha"**. | O sistema mascara os caracteres digitados no campo **"Senha"** e não registra o valor em nenhum log. | pronto |
| 4 | O usuário clica no botão **"Entrar"**. | O sistema aplica a limitação de taxa às chamadas de autenticação (FR-096) e, dentro do limite, valida e-mail e senha contra o resumo criptográfico com sal armazenado (FR-065). | pronto |
| 5 | O usuário aguarda a validação. | O sistema confirma as credenciais, emite o **token de acesso** no login e registra a entrada na trilha de auditoria com o identificador do usuário (FR-005). | pronto |
| 6 | O usuário é conduzido ao sistema. | O sistema mantém a identidade do usuário autenticado durante todo o uso, sem exigir nova identificação a cada tela (FR-004), e exibe a tela inicial com o nome do usuário e seu **papel** no cabeçalho. | pronto |
| 7 | O usuário navega entre as telas do sistema. | O servidor exige, em toda chamada recebida, o **token de acesso** emitido no login e verificado em cada requisição; se o token não vier ou estiver vencido, o servidor recusa a chamada independentemente do que a tela enviou (FR-064). | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O usuário ainda não tem cadastro no sistema. | O usuário clica no link **"Falar com o administrador para solicitar acesso"** na tela **"Login"**. | O sistema exibe a mensagem **"O acesso é criado pelo administrador do sistema. Solicite o cadastro ao administrador do hospital."** e não permite autocadastro. | pronto |
| A2 | O usuário deseja limpar os campos preenchidos antes de enviar. | O usuário clica no botão **"Limpar"** na tela **"Login"**. | O sistema apaga o conteúdo dos campos **"E-mail"** e **"Senha"** e mantém o foco no campo **"E-mail"**. | pronto |
| A3 | O usuário está autenticado e o token de acesso vence durante o uso. | O usuário tenta executar uma ação em qualquer tela. | O servidor recusa a chamada, a sessão expira e o sistema retorna à tela **"Login"** com a mensagem **"Sua sessão expirou. Entre novamente."** | pronto |
| A4 | O usuário é desativado enquanto está autenticado. | O usuário tenta executar uma ação em qualquer tela. | O servidor recusa a chamada por o usuário não estar ativo e o sistema retorna à tela **"Login"** com a mensagem **"Usuário desativado. Procure o administrador do sistema."** | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | E-mail ou senha incorretos. | O sistema exibe na tela **"Login"** a mensagem **"E-mail ou senha inválidos."**, mantém o campo **"E-mail"** preenchido, limpa o campo **"Senha"** e não informa qual dos dois está errado. | pronto |
| E2 | O campo **"E-mail"** ou o campo **"Senha"** foi enviado vazio. | O sistema exibe a mensagem **"Informe e-mail e senha para entrar."** e não realiza a validação de credenciais. | pronto |
| E3 | O limite de tentativas de autenticação foi excedido (FR-096). | O sistema bloqueia temporariamente novas tentativas, exibe a mensagem **"Muitas tentativas de login. Tente novamente mais tarde."** e registra o bloqueio na trilha de auditoria. | pronto |
| E4 | O servidor está indisponível. | O sistema exibe a mensagem **"Não foi possível conectar ao servidor. Tente novamente."** com o botão **"Tentar novamente"**, sem simular login bem-sucedido. | pronto |
| E5 | A senha digitada aparece em algum ponto do processo. | O sistema não exibe nem registra a senha em log, mensagem de erro ou tela (FR-066); qualquer ocorrência é tratada como falha de segurança e bloqueada pela área de segurança do hospital. | pronto |

#### UC-002: Gerenciar Cadastro e Desativação de Usuários

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O administrador acessa a área de gestão de usuários. | O sistema exibe a tela **"Usuários"** com a lista de usuários cadastrados, a busca por nome ou e-mail, a coluna **"Situação"** (Ativo/Desativado) e o botão **"Novo usuário"**. | pronto |
| 2 | O administrador clica no botão **"Novo usuário"**. | O sistema exibe a tela **"Cadastro de usuário"** com os campos **"Nome"**, **"E-mail"**, **"Senha"**, **"Papel"** (com as opções **médico**, **enfermeiro**, **administrador**) e o indicador **"Ativo"**. | pronto |
| 3 | O administrador preenche o campo **"Nome"**. | O sistema aceita o nome completo do usuário. | pronto |
| 4 | O administrador preenche o campo **"E-mail"**. | O sistema aceita o e-mail e sinaliza se o e-mail já estiver em uso por outro usuário. | pronto |
| 5 | O administrador preenche o campo **"Senha"**. | O sistema mascara os caracteres digitados e não exibe nem registra a senha em log, mensagem de erro ou tela (FR-066). | pronto |
| 6 | O administrador seleciona o campo **"Papel"**. | O sistema apresenta exclusivamente as opções **médico**, **enfermeiro** e **administrador** (BR-002). | pronto |
| 7 | O administrador marca o indicador **"Ativo"**. | O sistema registra que o usuário poderá acessar o sistema após o cadastro. | pronto |
| 8 | O administrador clica no botão **"Salvar"**. | O sistema persiste nome, e-mail, senha (como resumo criptográfico com sal, FR-065), papel e indicador de ativo, registra a ação na trilha de auditoria com o administrador responsável (FR-005) e retorna à tela **"Usuários"** com a mensagem **"Usuário cadastrado com sucesso."** | pronto |
| 9 | O administrador localiza um usuário desligado do hospital na lista da tela **"Usuários"**. | O sistema exibe a linha do usuário com o botão **"Desativar"** e a coluna **"Situação"** com o valor **Ativo**. | pronto |
| 10 | O administrador clica no botão **"Desativar"**. | O sistema exibe a confirmação **"Desativar este usuário? O nome dele continuará aparecendo nos registros antigos."** com os botões **"Confirmar desativação"** e **"Cancelar"**. | pronto |
| 11 | O administrador clica no botão **"Confirmar desativação"**. | O sistema altera a **"Situação"** para **Desativado**, mantém o registro do usuário (não apaga) e registra a ação na trilha de auditoria (FR-005). O usuário desativado deixa de acessar o sistema, mas seu nome permanece associado aos registros históricos (FR-003). | código gerado |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O administrador quer corrigir dados de um usuário já cadastrado. | O administrador clica no botão **"Editar"** na linha do usuário na tela **"Usuários"**. | O sistema exibe a tela **"Cadastro de usuário"** com os campos preenchidos, permite alterar **"Nome"**, **"E-mail"**, **"Papel"** e **"Ativo"**, e registra a alteração na trilha de auditoria. | pronto |
| A2 | O administrador quer reativar um usuário desativado. | O administrador clica no botão **"Reativar"** na linha do usuário desativado na tela **"Usuários"**. | O sistema altera a **"Situação"** para **Ativo** e registra a ação na trilha de auditoria. | código gerado |
| A3 | O administrador deseja cancelar o cadastro em andamento. | O administrador clica no botão **"Cancelar"** na tela **"Cadastro de usuário"**. | O sistema fecha a tela **"Cadastro de usuário"** e retorna à tela **"Usuários"** sem salvar dados. | pronto |
| A4 | O administrador tenta acessar dado clínico de paciente para gerenciar usuário. | O administrador tenta abrir uma tela de dado clínico. | O sistema nega o acesso, pois o administrador não precisa ver dado clínico para gerenciar usuário (FR-067), e exibe a mensagem **"Seu papel não permite acessar dados clínicos."** | pronto |
| A5 | O enfermeiro tenta apagar um registro de auditoria. | O enfermeiro tenta executar a exclusão na trilha de auditoria. | O sistema nega a ação, pois cada papel enxerga o que lhe cabe e o enfermeiro não apaga registro de auditoria (FR-067), e exibe a mensagem **"Seu papel não permite apagar registros de auditoria."** | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O administrador tenta salvar sem preencher um campo obrigatório. | O sistema exibe a mensagem **"Preencha nome, e-mail, senha e papel para salvar."** e mantém a tela **"Cadastro de usuário"** aberta, sem persistir nada. | pronto |
| E2 | O e-mail informado já pertence a outro usuário. | O sistema exibe a mensagem **"Este e-mail já está cadastrado."** e não persiste o cadastro. | pronto |
| E3 | O servidor não consegue persistir o cadastro. | O sistema exibe a mensagem **"Não foi possível salvar o usuário. Tente novamente."** com o botão **"Tentar novamente"**, sem simular sucesso. | pronto |
| E4 | O **token de acesso** do administrador está vencido. | O servidor recusa a chamada independentemente do que a tela enviou, a sessão expira e o sistema retorna à tela **"Login"** com a mensagem **"Sua sessão expirou. Entre novamente."** | pronto |
| E5 | A senha aparece em algum ponto do processo de cadastro. | O sistema não exibe nem registra a senha em log, mensagem de erro ou tela (FR-066); a ocorrência é tratada como falha de segurança. | pronto |

#### UC-003: Registrar Ações Relevantes em Trilha de Auditoria

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O usuário executa uma ação relevante no sistema (por exemplo, cadastra um paciente, classifica um caso, sobrescreve uma classificação, desativa um usuário ou envia uma notificação). | O servidor, sem necessidade de ação manual do usuário, gera uma entrada de auditoria contendo **quem fez**, **o que fez**, **sobre qual registro** e **quando** (FR-056), incluindo o identificador do usuário responsável pela ação (FR-005). | pronto |
| 2 | O servidor grava a entrada. | O sistema grava a entrada encadeada, guardando a marca da entrada anterior, de modo que alterações no histórico sejam detectáveis (FR-057). | código gerado |
| 3 | O servidor registra a leitura de dados de paciente, quando houver. | O sistema registra em auditoria todo acesso a dados de paciente, incluindo leitura, com usuário, data/hora e registro acessado (FR-098). | pronto |
| 4 | O administrador acessa a área de auditoria. | O sistema exibe a tela **"Log de auditoria"** com os filtros **"Período"**, **"Usuário"** e **"Tipo de ação"**, a tabela de entradas e o botão **"Verificar integridade"**. | pronto |
| 5 | O administrador seleciona o filtro **"Período"**. | O sistema aceita o período informado e prepara a consulta. | pronto |
| 6 | O administrador seleciona o filtro **"Usuário"**. | O sistema aceita o usuário informado e prepara a consulta. | pronto |
| 7 | O administrador seleciona o filtro **"Tipo de ação"**. | O sistema aceita o tipo de ação informado e prepara a consulta. | pronto |
| 8 | O administrador clica no botão **"Consultar"**. | O sistema consulta o log de auditoria filtrando por período, usuário ou tipo de ação e retorna apenas as entradas correspondentes (FR-058), exibindo na tabela as colunas **"Data/hora"**, **"Usuário"**, **"Ação"**, **"Registro afetado"** e **"Marca da entrada anterior"**. | pronto |
| 9 | O administrador quer conferir se o histórico foi alterado. | O sistema executa a verificação de integridade do encadeamento e exibe o resultado **"Encadeamento íntegro"** ou **"Alteração detectada no encadeamento"** (FR-057). | código gerado |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O administrador quer consultar sem aplicar nenhum filtro. | O administrador clica no botão **"Consultar"** com os filtros **"Período"**, **"Usuário"** e **"Tipo de ação"** vazios. | O sistema retorna as entradas mais recentes do log de auditoria e informa **"Nenhum filtro aplicado — exibindo as entradas mais recentes."** | código gerado |
| A2 | O administrador quer limpar os filtros aplicados. | O administrador clica no botão **"Limpar filtros"**. | O sistema apaga o conteúdo dos filtros **"Período"**, **"Usuário"** e **"Tipo de ação"** e mantém a tabela como está. | pronto |
| A3 | O auditor consulta a rastreabilidade de uma decisão registrada. | O auditor abre o registro da decisão e aciona a rastreabilidade. | O sistema exibe a origem do dado que fundamentou a decisão, pois toda decisão do sistema — risco, classificação, conduta — é registrada e rastreável até a origem do dado (FR-070). | código gerado |
| A4 | O enfermeiro tenta apagar um registro de auditoria. | O enfermeiro tenta executar a exclusão na tela **"Log de auditoria"**. | O sistema nega a ação, pois o enfermeiro não apaga registro de auditoria (FR-067), e exibe a mensagem **"Seu papel não permite apagar registros de auditoria."** | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | A verificação de integridade detecta alteração no encadeamento. | O sistema exibe na tela **"Log de auditoria"** a mensagem **"Alteração detectada no encadeamento da trilha de auditoria."**, destaca a entrada onde o encadeamento quebrou e registra o próprio evento de detecção. | código gerado |
| E2 | A consulta ao log não retorna nenhuma entrada para os filtros aplicados. | O sistema exibe a mensagem **"Nenhuma entrada de auditoria encontrada para os filtros informados."** e mantém os filtros preenchidos. | pronto |
| E3 | O servidor não consegue gravar a entrada de auditoria. | O sistema reporta que falhou, sem simular sucesso, exibindo a mensagem **"Não foi possível registrar a ação na trilha de auditoria."**, pois cada função, ao falhar, diz que falhou (BR-025). | código gerado |
| E4 | O **token de acesso** do administrador está vencido. | O servidor recusa a chamada independentemente do que a tela enviou, a sessão expira e o sistema retorna à tela **"Login"** com a mensagem **"Sua sessão expirou. Entre novamente."** | pronto |
| E5 | O administrador tenta alterar diretamente uma entrada já gravada. | O sistema não oferece edição nem exclusão de entradas de auditoria e exibe a mensagem **"A trilha de auditoria não permite alteração de entradas."** | pronto |

#### UC-004: Cadastrar Paciente com Cateter Venoso Central

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | A CCIH acessa a tela "Cadastro de Paciente com Cateter" e seleciona a aba "Acompanhamento Diário de UTI". | O sistema exibe a tela "Cadastro de Paciente com Cateter" com a aba "Acompanhamento Diário de UTI" ativa, mostrando a lista de pacientes de UTI que estão com cateter venoso central, cada linha com as colunas "Paciente", "Prontuário", "Médico responsável", "Com cateter" e "Dias com cateter". | código gerado |
| 2 | A CCIH clica no botão "Novo Paciente". | O sistema abre o formulário "Cadastro de Paciente com Cateter" com os campos vazios: "Nome do paciente", "Data de nascimento", "Sexo", "Número do prontuário" e "Médico responsável", e com os botões "Salvar" e "Cancelar". Nenhum campo aparece preenchido com valor de exemplo. | pronto |
| 3 | A CCIH preenche o campo "Nome do paciente". | O sistema aceita o texto digitado e mantém o campo editável. | pronto |
| 4 | A CCIH preenche o campo "Data de nascimento" no formato dia/mês/ano. | O sistema valida o formato da data e mantém o valor informado. | pronto |
| 5 | A CCIH seleciona o campo "Sexo" e escolhe uma das opções da lista. | O sistema exibe a lista de opções de "Sexo" e registra a opção escolhida. | pronto |
| 6 | A CCIH preenche o campo "Número do prontuário". | O sistema aceita o número informado e mantém o campo editável. | pronto |
| 7 | A CCIH seleciona o campo "Médico responsável" e escolhe, na lista de médicos ativos, o profissional responsável pelo paciente. | O sistema exibe a lista de médicos cadastrados e ativos, com o nome de cada um, e registra o médico selecionado no campo "Médico responsável". | pronto |
| 8 | A CCIH clica em "Salvar". | O sistema valida que os cinco campos ("Nome do paciente", "Data de nascimento", "Sexo", "Número do prontuário" e "Médico responsável") estão preenchidos, persiste o paciente, grava a entrada de auditoria com o usuário que executou a ação e exibe a mensagem "Paciente cadastrado com sucesso.". | pronto |
| 9 | O sistema retorna à aba "Acompanhamento Diário de UTI". | O sistema atualiza a lista de pacientes: o novo paciente aparece como uma linha com "Paciente", "Prontuário", "Médico responsável", "Com cateter" e "Dias com cateter" preenchidos a partir do cadastro. | código gerado |
| 10 | A CCIH pode opcionalmente: | | pronto |
| 10.1 | Clica no cabeçalho da coluna "Dias com cateter" para ordenar a lista. | O sistema reordena a lista de pacientes pelo número de dias com cateter, permitindo que a CCIH decida quem merece atenção primeiro. | pronto |
| 10.2 | Clica no cabeçalho da coluna "Paciente" para ordenar a lista. | O sistema reordena a lista de pacientes em ordem alfabética pelo nome do paciente. | pronto |
| 10.3 | Clica em uma linha da lista de pacientes. | O sistema abre a visão consolidada do paciente, reunindo em uma mesma tela os dados do prontuário, os resultados do laboratório e a anotação da enfermagem daquele paciente. | código gerado |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | A CCIH não tem o número do prontuário em mãos no momento do cadastro. | A CCIH clica em "Cancelar" no formulário "Cadastro de Paciente com Cateter". | O sistema fecha o formulário sem persistir dado algum e retorna à aba "Acompanhamento Diário de UTI", mantendo a lista de pacientes inalterada. | pronto |
| A2 | O paciente já foi cadastrado anteriormente e a CCIH precisa apenas conferir os dados na lista diária. | A CCIH não clica em "Novo Paciente" e usa a lista da aba "Acompanhamento Diário de UTI" para localizar o paciente já cadastrado. | O sistema mantém a lista visível com as colunas "Paciente", "Prontuário", "Médico responsável", "Com cateter" e "Dias com cateter", sem abrir formulário algum. | pronto |
| A3 | O médico responsável ainda não está cadastrado ou está desativado. | A CCIH abre o campo "Médico responsável" e verifica que o médico desejado não consta na lista de médicos ativos. | O sistema exibe apenas médicos cadastrados e ativos na lista do campo "Médico responsável" e não permite associar ao paciente um médico desativado. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | A CCIH clica em "Salvar" com um ou mais dos cinco campos em branco. | O sistema não persiste o paciente e exibe a mensagem "Preencha o campo [nome do campo faltante]." nomeando exatamente o campo que falta, mantendo o formulário aberto com os demais valores digitados. | pronto |
| E2 | A CCIH informa uma "Data de nascimento" em formato inválido. | O sistema não persiste o paciente e exibe a mensagem "Data de nascimento inválida. Informe no formato dia/mês/ano." mantendo o formulário aberto. | pronto |
| E3 | O servidor recusa a gravação por token de acesso ausente ou vencido. | O sistema exibe a mensagem "Sessão expirada. Entre novamente." encerra a sessão e redireciona a CCIH para a tela de login, sem persistir o paciente. | pronto |
| E4 | A gravação do paciente falha no banco de dados. | A própria função de gravação reporta a falha e o sistema exibe a mensagem "Não foi possível salvar o paciente. Tente novamente." com o botão "Tentar novamente", sem criar registro parcial e sem exibir valor inventado em qualquer campo. | pronto |

#### UC-005: Registrar Episódio e Dados de Risco do Caso Clínico

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | A CCIH abre o caso clínico do paciente cadastrado e seleciona a aba "Episódio e Dados de Risco". | O sistema exibe a tela "Episódio e Dados de Risco do Caso Clínico" com os campos "Idade do paciente na data", "Dias de cateter instalado", "Pontuação APACHE II", "Sítio de inserção do cateter", "Comorbidades relevantes", "Data de início do caso", "Data de encerramento do caso" e "Estado do caso", todos vazios, e com os botões "Salvar Episódio" e "Cancelar". | pronto |
| 2 | A CCIH preenche o campo "Idade do paciente na data". | O sistema aceita o valor e mantém o campo editável. | pronto |
| 3 | A CCIH preenche o campo "Dias de cateter instalado". | O sistema aceita o valor e mantém o campo editável. | pronto |
| 4 | A CCIH preenche o campo "Pontuação APACHE II". | O sistema aceita o valor e mantém o campo editável. | pronto |
| 5 | A enfermeira informa à CCIH o sítio de inserção e a CCIH seleciona o campo "Sítio de inserção do cateter", escolhendo entre "jugular interna", "subclávia" e "femoral". | O sistema exibe as três opções de "Sítio de inserção do cateter" e registra a opção escolhida. | pronto |
| 6 | A CCIH preenche o campo "Comorbidades relevantes". | O sistema aceita o texto informado e mantém o campo editável. | pronto |
| 7 | A CCIH preenche o campo "Data de início do caso". | O sistema valida o formato da data e mantém o valor informado. | pronto |
| 8 | A CCIH clica em "Salvar Episódio". | O sistema verifica se os cinco dados de risco ("Idade do paciente na data", "Dias de cateter instalado", "Pontuação APACHE II", "Sítio de inserção do cateter" e "Comorbidades relevantes") estão preenchidos; estando todos preenchidos, persiste o episódio associado ao caso, grava a entrada de auditoria com o usuário que executou a ação e exibe a mensagem "Episódio registrado. Cálculo de risco liberado.". | código gerado |
| 9 | O sistema mantém o campo "Estado do caso" como "ativo". | O sistema exibe o caso com estado "ativo" e o campo "Data de encerramento do caso" vazio, com a explicação de que o caso ainda não foi encerrado. | pronto |
| 10 | A CCIH pode opcionalmente: | | pronto |
| 10.1 | Encerra o caso preenchendo o campo "Data de encerramento do caso" e alterando o campo "Estado do caso" para "encerrado". | O sistema valida a data de encerramento, grava a alteração de estado do caso e exibe a mensagem "Caso encerrado.". | pronto |
| 10.2 | Clica em "Cancelar". | O sistema fecha a tela "Episódio e Dados de Risco do Caso Clínico" sem persistir alterações e retorna à tela anterior. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | A CCIH precisa registrar o episódio mas ainda não tem a pontuação APACHE II disponível. | A CCIH preenche os demais campos e deixa "Pontuação APACHE II" em branco, clicando em "Salvar Episódio". | O sistema não libera o cálculo de risco, exibe a mensagem "Falta o dado: Pontuação APACHE II. A conta de risco não sai enquanto faltar um dos cinco dados." e mantém o formulário aberto com os demais valores digitados. | código gerado |
| A2 | A enfermeira informa que o cateter foi instalado em sítio diferente do inicialmente anotado. | A CCIH reabre o campo "Sítio de inserção do cateter" e escolhe outra das três opções ("jugular interna", "subclávia" ou "femoral"). | O sistema atualiza o valor do campo "Sítio de inserção do cateter" e, ao clicar em "Salvar Episódio", persiste a alteração e grava a entrada de auditoria correspondente. | pronto |
| A3 | O caso já estava encerrado e a CCIH precisa apenas consultar os dados de risco registrados. | A CCIH abre a aba "Episódio e Dados de Risco" de um caso com "Estado do caso" igual a "encerrado". | O sistema exibe os campos com os valores já registrados e o campo "Data de encerramento do caso" preenchido, sem permitir nova liberação de cálculo de risco para o caso encerrado. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | A CCIH clica em "Salvar Episódio" com um dos cinco dados de risco em branco. | O sistema não persiste o episódio, não libera o cálculo de risco e exibe a mensagem "Falta o dado: [nome do dado faltante]." nomeando exatamente qual dado falta (FR-061), mantendo o formulário aberto. | código gerado |
| E2 | A CCIH informa a "Data de início do caso" em formato inválido. | O sistema não persiste o episódio e exibe a mensagem "Data de início do caso inválida. Informe no formato dia/mês/ano." mantendo o formulário aberto. | pronto |
| E3 | A CCIH tenta alterar o "Estado do caso" para "encerrado" sem informar a "Data de encerramento do caso". | O sistema não persiste a alteração e exibe a mensagem "Informe a Data de encerramento do caso para encerrar o caso." mantendo o campo "Estado do caso" em "ativo". | código gerado |
| E4 | O servidor recusa a gravação por token de acesso ausente ou vencido. | O sistema exibe a mensagem "Sessão expirada. Entre novamente." encerra a sessão e redireciona a CCIH para a tela de login, sem persistir o episódio. | pronto |
| E5 | A gravação do episódio falha no banco de dados. | A própria função de gravação reporta a falha e o sistema exibe a mensagem "Não foi possível salvar o episódio. Tente novamente." com o botão "Tentar novamente", sem criar registro parcial e sem exibir valor inventado. | pronto |

#### UC-006: Consultar Escore de Risco de Cox no Serviço Externo

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | A CCIH abre o caso clínico com os cinco dados de risco preenchidos e clica em "Calcular Escore de Risco". | O sistema verifica se os cinco dados de risco estão preenchidos e exibe a tela "Escore de Risco de Cox" com os campos de entrada preenchidos a partir do cadastro do caso: "Idade" (número inteiro), "Pontuação APACHE II" (número inteiro) e "Tipo de cateter" (texto), sem pedir novamente ao usuário. | código gerado |
| 2 | A CCIH confere os três campos de entrada exibidos na tela "Escore de Risco de Cox". | O sistema exibe "Idade", "Pontuação APACHE II" e "Tipo de cateter" com os valores obtidos do cadastro do caso, e o botão "Consultar Escore". | pronto |
| 3 | A CCIH clica em "Consultar Escore". | O sistema envia "Idade" (inteiro), "Pontuação APACHE II" (inteiro) e "Tipo de cateter" (texto) ao serviço de escore de risco de Cox, sem intervalo de confiança na requisição, e aguarda o retorno dentro do tempo limite configurado. | código gerado |
| 4 | O servidor de estatística do hospital devolve o escore, a faixa de risco, o preditor linear, os fatores de risco e o nome do modelo. | O sistema recebe os campos "Escore", "Faixa de risco" (baixo, moderado ou alto), "Preditor linear", "Fatores de risco" e "Nome do modelo", e não espera nem exige intervalo de confiança. | código gerado |
| 5 | O sistema armazena o retorno associado ao caso. | O sistema persiste "Escore", "Faixa de risco", "Preditor linear", "Fatores de risco" e "Nome do modelo", grava a "Data do cálculo" do escore e registra a "Versão do modelo" usada naquele escore, para que a CCIH saiba qual versão gerou cada número antigo. | código gerado |
| 6 | O sistema exibe o resultado na tela "Escore de Risco de Cox". | O sistema apresenta o "Escore", a "Faixa de risco", o "Preditor linear", os "Fatores de risco", o "Nome do modelo", a "Versão do modelo" e a "Data do cálculo", e exibe a mensagem "Escore consultado e armazenado.". | pronto |
| 7 | O sistema grava a decisão na trilha de auditoria. | O sistema registra a decisão de risco com a origem do dado que a fundamentou, contendo quem fez, o que fez, sobre qual registro e quando. | pronto |
| 8 | A CCIH pode opcionalmente: | | pronto |
| 8.1 | Clica em "Ver histórico de escores" do caso. | O sistema exibe a lista de escores já armazenados para o caso, cada um com "Escore", "Faixa de risco", "Nome do modelo", "Versão do modelo" e "Data do cálculo". | pronto |
| 8.2 | Clica em "Fechar". | O sistema fecha a tela "Escore de Risco de Cox" e retorna à tela do caso clínico, mantendo o escore armazenado. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O nome do modelo devolvido vem como texto livre longo, como "Cox proportional hazards". | A CCIH consulta o escore normalmente. | O sistema armazena o "Nome do modelo" sem truncamento, comportando texto livre longo, e o exibe integralmente na tela "Escore de Risco de Cox". | código gerado |
| A2 | O serviço externo devolve o escore sem intervalo de confiança. | A CCIH consulta o escore normalmente. | O sistema não gera erro nem bloqueio pela ausência de intervalo de confiança e prossegue armazenando os campos previstos (FR-012, BR-005). | código gerado |
| A3 | O caso já possui escore armazenado de uma versão anterior do modelo. | A CCIH abre "Ver histórico de escores" do caso. | O sistema exibe os escores anteriores, cada um com a "Versão do modelo" que o gerou, permitindo que a CCIH saiba qual versão gerou cada número antigo. | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O serviço de escore não responde dentro do tempo limite. | O sistema exibe a mensagem "O serviço de escore não respondeu. Nenhum escore foi gravado." com o botão "Tentar novamente", e nenhum registro de escore é criado para o caso (FR-060, BR-017). | código gerado |
| E2 | Um dos cinco dados de risco está em branco no cadastro do caso. | O sistema não permite executar o cálculo de risco e exibe a mensagem "Falta o dado: [nome do dado faltante]. A conta de risco não sai enquanto faltar um dos cinco dados." (FR-008, FR-061, BR-004). | pronto |
| E3 | O servidor de estatística do hospital devolve erro na consulta. | O sistema exibe a mensagem "Não foi possível obter o escore. Nenhum escore foi gravado." com o botão "Tentar novamente", sem apresentar número que não possa ser defendido em auditoria (FR-075, BR-022). | código gerado |
| E4 | O servidor recusa a chamada por token de acesso ausente ou vencido. | O sistema exibe a mensagem "Sessão expirada. Entre novamente." encerra a sessão e redireciona a CCIH para a tela de login, sem gravar escore. | pronto |
| E5 | A gravação do escore falha no banco de dados. | A própria função de gravação reporta a falha e o sistema exibe a mensagem "Não foi possível armazenar o escore. Tente novamente." com o botão "Tentar novamente", sem criar registro parcial e sem exibir valor inventado. | código gerado |

#### UC-007: Importar Resultado de Hemocultura do Laboratório

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O analista do laboratório de microbiologia informa ao BioByte o número do prontuário do paciente cuja hemocultura deve ser importada. | O sistema exibe a tela **Importação de Hemocultura** com o campo "Número do prontuário" vazio e o botão "Buscar no laboratório" habilitado. | pronto |
| 2 | O BioByte aciona a busca informando o número do prontuário. | O sistema anonimiza os dados do paciente e envia a chamada ao serviço de microbiologia pelo identificador do paciente, exibindo a mensagem "Consultando o laboratório..." e o indicador de progresso. | código gerado |
| 3 | — | O sistema recebe o retorno do laboratório com situação, identificador da amostra, origem, microrganismo, indicação de multirresistência e antibiograma, e exibe o painel **Prévia do Resultado Importado** com os campos "Situação", "Identificador da amostra", "Origem", "Microrganismo" e a lista "Antibiograma". | código gerado |
| 4 | O BioByte confere a prévia e clica em "Confirmar importação". | O sistema persiste o resultado de hemocultura associado ao caso, com identificador da amostra, origem (hemocultura, ponta de cateter ou outra) e antibiograma como lista de antimicrobianos, cada item com classe e resultado (sensível, intermediário ou resistente), e exibe a mensagem "Resultado importado com sucesso". | código gerado |
| 5 | O usuário pode opcionalmente: | — | pronto |
| 5.1 | Clica em "Cancelar". | O sistema fecha o painel **Prévia do Resultado Importado** e retorna à tela **Importação de Hemocultura** sem persistir nenhum dado. | pronto |
| 5.2 | Clica em "Buscar novamente". | O sistema repete a consulta ao laboratório para o mesmo número de prontuário. | código gerado |
| 6 | O BioByte encerra a operação. | O sistema mantém o resultado importado visível na lista "Resultados importados deste caso" com a data e hora da importação. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O laboratório retorna "pendente", sem microrganismo nenhum. | O BioByte confere a prévia e clica em "Confirmar importação". | O sistema registra o estado "pendente" para o caso, exibe a mensagem "Resultado pendente registrado — sem microrganismo e sem antibiograma" e não cria microrganismo nem antibiograma fictício. | código gerado |
| A2 | O laboratório retorna mensagem explicando problema de cadastro da amostra. | O BioByte lê a mensagem e clica em "Registrar ocorrência". | O sistema registra a mensagem de erro de cadastro junto ao caso, exibe "Erro de cadastro da amostra registrado: [mensagem do laboratório]" e não cria resultado fictício nem falha. | código gerado |
| A3 | O mesmo resultado já foi buscado anteriormente. | O BioByte aciona a busca novamente. | O sistema reconhece que o resultado já existe, não cria registro repetido e exibe a mensagem "Este resultado já foi importado em [data/hora]". | código gerado |
| A4 | O laboratório está fora do ar. | O BioByte aciona a busca. | O sistema exibe na tela **Importação de Hemocultura** a mensagem "O laboratório está fora do ar" e não mostra resultado vazio como se fosse resultado normal. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O tempo limite da consulta ao laboratório estoura. | O sistema interrompe a consulta, exibe a mensagem "Não foi possível obter o resultado do laboratório — tempo limite excedido" e oferece o botão "Tentar novamente". | código gerado |
| E2 | O retorno do laboratório traz campos além da situação vazios. | O sistema aceita os campos vazios sem falhar, exibe "Resultado ainda não saiu — campos além da situação vieram vazios" e mantém a importação disponível para nova consulta. | código gerado |
| E3 | A chamada ao laboratório falha por credencial inválida. | O sistema reporta "Falha na chamada ao laboratório: credencial inválida" e não persiste nenhum dado. | código gerado |

#### UC-008: Traduzir Resultado do Laboratório para Nomenclatura do Hospital

| Campo | Detalhe |
|---|---|
| **Natureza** | **agêntica** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O agente de IA recebe o resultado bruto do laboratório associado ao caso. | O sistema exibe a tela **Tradução do Resultado do Laboratório** com o painel "Resultado bruto" contendo o texto original recebido do laboratório e o botão "Traduzir" habilitado. | pronto |
| 2 | O agente de IA lê o resultado bruto e interpreta o que ele é. | O sistema apresenta no painel "Interpretação do agente" a leitura feita sobre o conteúdo recebido. | agente |
| 3 | O agente de IA converte a nomenclatura própria do laboratório para o vocabulário adotado pelo hospital. | O sistema exibe no painel "Resultado traduzido" os termos convertidos para a nomenclatura do hospital. | agente |
| 4 | O agente de IA decide se o resultado é aproveitável. | O sistema exibe o campo "Aproveitável" preenchido com "Sim" ou "Não" e, quando "Sim", o botão "Encaminhar para classificação" fica habilitado. | agente |
| 5 | A equipe assistencial confere o resultado traduzido. | O sistema mantém visíveis lado a lado o "Resultado bruto" e o "Resultado traduzido", com o indicador "Aproveitável". | pronto |
| 6 | O usuário pode opcionalmente: | — | pronto |
| 6.1 | Clica em "Encaminhar para classificação". | O sistema encaminha o resultado traduzido e aproveitável para o fluxo de classificação do caso pela norma vigente. | código gerado |
| 6.2 | Clica em "Ver justificativa". | O sistema exibe a justificativa textual do agente para a decisão de aproveitabilidade. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O resultado recebido está marcado como "pendente". | O agente de IA reconhece a condição. | O sistema exibe o campo "Aproveitável" como "Não" e a mensagem "Resultado pendente — nenhum valor clínico gerado", sem produzir valor inventado. | código gerado |
| A2 | O resultado recebido contém erro. | O agente de IA reconhece a condição. | O sistema sinaliza "Resultado com erro — tradução não aplicável" e não gera valor clínico inventado. | código gerado |
| A3 | O resultado é aproveitável, mas usa termos ambíguos do laboratório. | O agente de IA decide a melhor correspondência para o vocabulário do hospital. | O sistema exibe o termo traduzido acompanhado da justificativa textual da decisão e mantém o resultado bruto visível para conferência. | agente |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O resultado bruto está vazio ou ilegível. | O sistema exibe "Não foi possível ler o resultado bruto" e mantém o botão "Traduzir" indisponível, sem produzir tradução. | código gerado |
| E2 | O agente não consegue mapear um termo para o vocabulário do hospital. | O sistema marca o termo como "Não mapeado" e exibe "Termo sem correspondência no vocabulário do hospital", sem inventar correspondência. | código gerado |
| E3 | A execução do agente falha. | O sistema reporta "A tradução falhou" e oferece o botão "Tentar novamente", sem gravar tradução parcial como se fosse final. | código gerado |

#### UC-009: Classificar Caso pelo Critério NHSN

| Campo | Detalhe |
|---|---|
| **Natureza** | **agêntica** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O sistema recebe a microbiologia do caso. | O sistema exibe a tela **Classificação do Caso pelo Critério NHSN** com o painel "Microbiologia do caso" contendo o microrganismo e o antibiograma e o botão "Classificar pelo critério" habilitado. | pronto |
| 2 | O sistema aciona o agente de IA para aplicar o critério NHSN vigente ao caso. | O sistema exibe a mensagem "Aplicando o critério NHSN vigente..." e o indicador de progresso. | código gerado |
| 3 | O agente de IA decide se o caso é infecção de corrente sanguínea ou não, aplicando a norma vigente. | O sistema exibe no campo "Classificação" o resultado entre "confirmada", "descartada" ou "pendente". | agente |
| 4 | O agente de IA informa em cima de qual critério tomou a decisão. | O sistema exibe os campos "Critério aplicado" e "Versão do critério" preenchidos com o nome do critério e a versão utilizada. | agente |
| 5 | O sistema verifica se o caso é antigo. | O sistema aplica ao caso a norma vigente à época do caso, não a norma atual, e exibe a mensagem "Norma aplicada conforme a vigência na data do caso". | código gerado |
| 6 | O médico confere a classificação e o critério indicado. | O sistema exibe o botão "Assinar classificação" e o campo "Justificativa da sobrescrita" desabilitado. | pronto |
| 7 | O usuário pode opcionalmente: | — | pronto |
| 7.1 | Clica em "Sobrescrever classificação". | O sistema habilita o campo "Justificativa da sobrescrita" e o botão "Salvar sobrescrita". | pronto |
| 7.2 | Clica em "Ver rastreabilidade". | O sistema exibe o critério aplicado, a versão da norma e o responsável pela assinatura, permitindo auditoria da classificação. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O médico sobrescreve a classificação automática. | O médico preenche o campo "Justificativa da sobrescrita" e clica em "Salvar sobrescrita". | O sistema bloqueia a sobrescrita se a justificativa estiver vazia e, com a justificativa preenchida, grava a nova classificação mantendo registrada a classificação original do sistema. | código gerado |
| A2 | O caso é antigo e a norma atual difere da norma da época. | O sistema aplica automaticamente a norma vigente à época do caso. | O sistema exibe a classificação pela versão vigente naquela data e indica a versão utilizada no campo "Versão do critério". | código gerado |
| A3 | Os dados do caso não sustentam a classificação. | O agente de IA declara a insuficiência. | O sistema exibe a classificação "pendente" e a mensagem "Os dados não sustentam uma classificação" com o campo "Critério aplicado" indicando o critério consultado. | agente |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | Não há critério cadastrado vigente para a data do caso. | O sistema exibe "Não há critério vigente para a data do caso" e não atribui classificação, mantendo o caso sem classificação. | código gerado |
| E2 | A microbiologia do caso está incompleta. | O sistema exibe "Dados de microbiologia insuficientes para classificar" e mantém o botão "Classificar pelo critério" indisponível. | código gerado |
| E3 | A execução do agente falha. | O sistema reporta "A classificação falhou" e oferece o botão "Tentar novamente", sem gravar classificação parcial. | pronto |

#### UC-010: Sobrescrever Classificação Automática com Justificativa

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O médico, na tela **"Detalhe do Caso Clínico"**, localiza a seção **"Classificação NHSN"** e clica em **"Sobrescrever classificação"**. | O sistema exibe o modal **"Sobrescrever Classificação Automática"**, mostrando, somente para leitura, a **"Classificação atual do sistema"** (ex.: *Confirmada*), o **"Critério aplicado"** (ex.: *NHSN vigente*) e a **"Versão do critério"**. | pronto |
| 2 | O médico seleciona a nova classificação no campo **"Nova classificação"**, com as opções *Confirmada*, *Descartada* e *Pendente*. | O sistema habilita o campo **"Justificativa da sobrescrita (obrigatória)"**, um campo de texto livre. | pronto |
| 3 | O médico preenche o campo **"Justificativa da sobrescrita (obrigatória)"** com o motivo clínico da alteração. | O sistema habilita o botão **"Confirmar sobrescrita"**. | pronto |
| 4 | O médico clica em **"Confirmar sobrescrita"**. | O sistema valida que a justificativa não está vazia, grava a nova classificação, mantém a classificação original do sistema registrada, grava o registro de auditoria com usuário, ação, registro afetado e data/hora, fecha o modal e atualiza a seção **"Classificação NHSN"** da tela **"Detalhe do Caso Clínico"** exibindo a **"Classificação atual (sobrescrita pelo médico)"** e o link **"Ver classificação original do sistema"**. | código gerado |
| 5 | O médico pode opcionalmente clicar em **"Ver classificação original do sistema"**. | O sistema exibe o painel **"Histórico de Classificação"** com a classificação automática original, o critério, a versão, a nova classificação, a justificativa e o nome do médico que assinou. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O médico já sobrescreveu a classificação anteriormente e deseja alterá-la novamente. | O médico clica em **"Sobrescrever classificação"** na tela **"Detalhe do Caso Clínico"**. | O sistema exibe o modal **"Sobrescrever Classificação Automática"** com o campo **"Classificação atual (sobrescrita pelo médico)"** preenchido com o último valor informado, mantendo também visível a **"Classificação original do sistema"**. | pronto |
| A2 | O médico decide não concluir a sobrescrita. | O médico clica em **"Cancelar"**. | O sistema fecha o modal **"Sobrescrever Classificação Automática"** e retorna à tela **"Detalhe do Caso Clínico"** sem gravar nenhuma alteração. | pronto |
| A3 | O médico seleciona a mesma classificação já vigente. | O médico escolhe em **"Nova classificação"** o mesmo valor já exibido. | O sistema mantém o campo **"Justificativa da sobrescrita (obrigatória)"** habilitado e permite confirmar, registrando a ação em auditoria como uma nova assinatura do médico. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O médico tenta confirmar sem preencher a justificativa. | O sistema bloqueia a ação e exibe a mensagem **"Justificativa da sobrescrita é obrigatória para alterar a classificação automática."**, mantendo o modal **"Sobrescrever Classificação Automática"** aberto e o foco no campo **"Justificativa da sobrescrita (obrigatória)"**. | pronto |
| E2 | O caso não possui classificação automática gerada (etapa de classificação ainda não executada). | O sistema exibe a mensagem **"Não há classificação automática para sobrescrever. Execute a classificação do caso antes de sobrescrever."** e desabilita o botão **"Sobrescrever classificação"**. | código gerado |
| E3 | Falha ao gravar a sobrescrita no banco de dados. | O sistema exibe a mensagem **"Não foi possível gravar a sobrescrita da classificação. Tente novamente."** e mantém o modal **"Sobrescrever Classificação Automática"** aberto com os dados preenchidos, sem alterar a classificação vigente. | pronto |
| E4 | A sessão do usuário expirou durante a operação. | O sistema recusa a gravação, exibe a mensagem **"Sessão expirada. Faça login novamente."** e redireciona para a tela **"Login"**. | pronto |

#### UC-011: Identificar Multirresistência no Antibiograma

| Campo | Detalhe |
|---|---|
| **Natureza** | **agêntica** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O sistema, ao concluir a importação do resultado de hemocultura, aciona o agente de IA para avaliar o antibiograma. | O sistema exibe na tela **"Detalhe do Caso Clínico"**, na seção **"Antibiograma"**, a lista de antimicrobianos com **"Antimicrobiano"**, **"Classe"** e **"Resultado"** (Sensível, Intermediário, Resistente). | pronto |
| 2 | O agente de IA lê a lista de antimicrobianos do antibiograma. | O sistema apresenta o indicador **"Avaliando multirresistência..."** na seção **"Multirresistência"**. | pronto |
| 3 | O agente de IA agrupa os antimicrobianos por classe e conta quantas classes apresentam resultado **"Resistente"**. | O sistema mantém a seção **"Multirresistência"** em estado de processamento, sem exibir valor inventado. | pronto |
| 4 | O agente de IA decide se o microrganismo é multirresistente, aplicando a regra de três ou mais classes resistentes. | O sistema exibe na seção **"Multirresistência"** o campo **"Multirresistente"** com o valor *Sim* ou *Não* e o campo **"Classes resistentes identificadas"** com a contagem e a lista das classes. | agente |
| 5 | O agente de IA registra a justificativa da decisão. | O sistema exibe o campo **"Justificativa da decisão"** com o texto que cita as classes resistentes encontradas, e o botão **"Ver antibiograma completo"**. | agente |
| 6 | O médico, na tela **"Detalhe do Caso Clínico"**, consulta a seção **"Multirresistência"**. | O sistema apresenta o resultado da decisão, a contagem de classes resistentes, a justificativa e o link **"Ver antibiograma completo"**, sem exigir nova ação do médico. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O antibiograma tem menos de três classes resistentes. | O agente de IA avalia a lista e conclui pela ausência de multirresistência. | O sistema exibe na seção **"Multirresistência"** o campo **"Multirresistente"** com o valor *Não* e a justificativa citando as classes resistentes encontradas. | agente |
| A2 | O antibiograma possui antimicrobianos com resultado *Intermediário*. | O agente de IA avalia a lista considerando *Intermediário* como não resistente para a contagem de classes. | O sistema exibe a decisão com a justificativa explicitando que os resultados *Intermediário* não foram contados como resistência. | agente |
| A3 | O médico clica em **"Ver antibiograma completo"**. | O médico abre o detalhamento do antibiograma. | O sistema exibe o painel **"Antibiograma Completo"** com todos os antimicrobianos, suas classes e resultados, destacando as classes contadas como resistentes. | código gerado |
| A4 | O caso não possui antibiograma importado (resultado pendente ou com erro). | O agente de IA não é acionado. | O sistema exibe na seção **"Multirresistência"** a mensagem **"Não há antibiograma disponível para avaliar multirresistência."** e mantém o campo **"Multirresistente"** vazio. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O antibiograma vem sem a classe de um ou mais antimicrobianos. | O sistema exibe na seção **"Multirresistência"** a mensagem **"Não foi possível avaliar multirresistência: classe ausente em um ou mais antimicrobianos."** e não emite decisão. | código gerado |
| E2 | O agente de IA falha ao interpretar o antibiograma. | O sistema exibe na seção **"Multirresistência"** a mensagem **"Não foi possível avaliar multirresistência. Tente novamente."** e mantém o campo **"Multirresistente"** vazio, sem inventar resultado. | código gerado |
| E3 | O resultado de hemocultura está marcado como "pendente". | O sistema exibe a mensagem **"Resultado pendente no laboratório. Não há antibiograma para avaliar."** e não aciona o agente de IA. | código gerado |
| E4 | O resultado de hemocultura contém mensagem de erro de cadastro. | O sistema exibe a mensagem **"Resultado com erro de cadastro no laboratório. Não há antibiograma para avaliar."** e não aciona o agente de IA. | código gerado |
| E5 | A lista de antimicrobianos está vazia. | O sistema exibe a mensagem **"Antibiograma sem antimicrobianos. Não foi possível avaliar multirresistência."** e não emite decisão. | código gerado |

#### UC-012: Abrir e Gerenciar Alerta de Multirresistência

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O sistema detecta multirresistência no caso e abre automaticamente o alerta. | O sistema cria o alerta com os campos **"Tipo"**, **"Gravidade"** e **"Situação"** preenchidos, com a situação inicial *Aberto*, e exibe o alerta na tela **"Alertas de Multirresistência"**. | código gerado |
| 2 | A coordenadora da CCIH abre a tela **"Alertas de Multirresistência"**. | O sistema exibe a lista de alertas com as colunas **"Caso"**, **"Tipo"**, **"Gravidade"**, **"Situação"** e **"Data de abertura"**, com filtro por situação. | pronto |
| 3 | A coordenadora da CCIH seleciona um alerta com situação *Aberto*. | O sistema abre o painel **"Detalhe do Alerta"** com **"Tipo"**, **"Gravidade"**, **"Situação"**, **"Caso vinculado"** e a lista de transições permitidas. | código gerado |
| 4 | A coordenadora da CCIH clica em **"Reconhecer alerta"**. | O sistema altera a situação do alerta para *Reconhecido*, grava o registro de auditoria com usuário, ação, registro afetado e data/hora, e atualiza a coluna **"Situação"** na lista de alertas. | pronto |
| 5 | A enfermeira abre o alerta já reconhecido e conclui a conduta. | O sistema exibe no painel **"Detalhe do Alerta"** a situação *Reconhecido* e o botão **"Encerrar alerta"**. | código gerado |
| 6 | A enfermeira clica em **"Encerrar alerta"**. | O sistema altera a situação do alerta para *Encerrado*, grava o registro de auditoria com usuário, ação, registro afetado e data/hora, e atualiza a coluna **"Situação"** na lista de alertas. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | A coordenadora da CCIH filtra a lista por situação. | A coordenadora seleciona no filtro **"Situação"** o valor *Aberto*, *Reconhecido* ou *Encerrado*. | O sistema atualiza a lista de alertas exibindo apenas os alertas com a situação selecionada. | pronto |
| A2 | A enfermeira reconhece o alerta em vez da coordenadora. | A enfermeira clica em **"Reconhecer alerta"** no painel **"Detalhe do Alerta"**. | O sistema altera a situação para *Reconhecido* e registra em auditoria o usuário enfermeiro que executou a ação. | pronto |
| A3 | A coordenadora da CCIH reabre um alerta encerrado. | A coordenadora clica em **"Reabrir alerta"** no painel **"Detalhe do Alerta"**. | O sistema altera a situação para *Aberto*, grava o registro de auditoria da reabertura e atualiza a lista de alertas. | pronto |
| A4 | O alerta é aberto para um caso já com alerta aberto do mesmo tipo. | O sistema identifica o alerta existente. | O sistema exibe a mensagem **"Já existe alerta aberto para este caso."** e não cria um segundo alerta. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | Falha ao gravar a mudança de situação do alerta. | O sistema exibe a mensagem **"Não foi possível atualizar a situação do alerta. Tente novamente."** e mantém a situação anterior na tela. | pronto |
| E2 | O usuário tenta uma transição não permitida (ex.: encerrar um alerta já encerrado). | O sistema exibe a mensagem **"Transição de situação não permitida para este alerta."** e mantém a situação atual. | código gerado |
| E3 | A sessão do usuário expirou durante a operação. | O sistema recusa a gravação, exibe a mensagem **"Sessão expirada. Faça login novamente."** e redireciona para a tela **"Login"**. | pronto |
| E4 | O alerta não foi encontrado (registro removido ou inexistente). | O sistema exibe a mensagem **"Alerta não encontrado."** e retorna à lista da tela **"Alertas de Multirresistência"**. | pronto |

#### UC-013: Redigir Texto do Alerta para a Equipe

| Campo | Detalhe |
|---|---|
| **Natureza** | **agêntica** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O sistema (após abrir o alerta de multirresistência) aciona o agente de IA para redigir o texto do alerta. | A tela **Alerta de Multirresistência** é exibida com o bloco **Texto do Alerta** em estado "Redigindo…", e o sistema envia ao agente o antibiograma, o microrganismo isolado, a origem da amostra, o resultado da classificação NHSN e a indicação de multirresistência. | código gerado |
| 2 | O agente de IA lê o antibiograma e o contexto do caso recebidos. | O sistema mantém o bloco **Texto do Alerta** em processamento; nenhum texto é exibido até a redação concluir. | código gerado |
| 3 | O agente de IA redige o texto do alerta, informando o que houve (microrganismo multirresistente identificado) e por que importa (risco para o paciente com cateter venoso central). | O sistema preenche o bloco **Texto do Alerta** com o texto redigido, exibindo os campos **Microrganismo**, **Origem da Amostra**, **Tipo do Alerta**, **Gravidade** e **Situação** ao lado do texto. | agente |
| 4 | O agente de IA registra, junto ao alerta, a indicação do critério e da versão usados na decisão de multirresistência. | O sistema exibe no bloco **Fundamentação da Decisão** a linha "Critério: [nome do critério] · Versão: [versão]" e a linha "Multirresistência: resistência a três ou mais classes de antimicrobianos". | código gerado |
| 5 | O enfermeiro responsável abre o alerta na tela **Alerta de Multirresistência**. | O sistema exibe o texto redigido no bloco **Texto do Alerta**, legível, com o microrganismo, a origem da amostra e a fundamentação visíveis. | pronto |
| 6 | O usuário pode opcionalmente: | | pronto |
| 6.1 | Clica em **Reconhecer Alerta**. | O sistema altera a **Situação** do alerta de "aberto" para "reconhecido" e registra a ação na trilha de auditoria com o usuário e a data/hora. | pronto |
| 6.2 | Clica em **Encerrar Alerta**. | O sistema altera a **Situação** do alerta para "encerrado" e registra a ação na trilha de auditoria com o usuário e a data/hora. | pronto |
| 6.3 | Clica em **Notificar Equipe**. | O sistema encaminha o alerta para o fluxo de notificação por e-mail (UC-014). | código gerado |
| 7 | O sistema grava o texto redigido, a fundamentação e a versão do agente usados na decisão. | O sistema confirma na tela **Alerta de Multirresistência** a mensagem "Alerta registrado com texto redigido pelo agente" e mantém o texto disponível para auditoria. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O antibiograma não contém informação suficiente para o agente redigir um texto com fundamento. | O agente de IA não redige texto afirmativo. | O sistema exibe no bloco **Texto do Alerta** a mensagem "Não foi possível redigir o alerta: dados do antibiograma insuficientes" e mantém o alerta com **Situação** "aberto", sem texto inventado. | código gerado |
| A2 | O enfermeiro responsável decide não reconhecer nem encerrar o alerta no momento. | O enfermeiro fecha a tela **Alerta de Multirresistência** sem clicar em **Reconhecer Alerta** nem em **Encerrar Alerta**. | O sistema mantém a **Situação** do alerta como "aberto" e preserva o texto redigido para leitura posterior. | pronto |
| A3 | A coordenadora da CCIH acessa o alerta antes do enfermeiro responsável. | A coordenadora abre a tela **Alerta de Multirresistência** e lê o texto redigido. | O sistema exibe o texto redigido, a fundamentação e a versão do critério, sem alterar a **Situação** do alerta. | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O agente de IA não consegue concluir a redação do texto do alerta no tempo esperado. | O sistema exibe no bloco **Texto do Alerta** a mensagem "Não foi possível redigir o alerta agora" e mantém o alerta com **Situação** "aberto", com o botão **Tentar novamente** disponível. | código gerado |
| E2 | O antibiograma associado ao alerta está marcado como "pendente" ou veio com mensagem de erro do laboratório. | O sistema exibe no bloco **Texto do Alerta** a mensagem "Alerta sem texto: resultado do laboratório pendente ou com erro" e não gera texto inventado. | código gerado |
| E3 | O agente de IA gera um texto que não cita o microrganismo nem a origem da amostra. | O sistema descarta o texto, exibe no bloco **Texto do Alerta** a mensagem "Texto do alerta incompleto — redação não aceita" e mantém o alerta com **Situação** "aberto". | código gerado |

#### UC-014: Notificar Coordenadora e Enfermeiro por E-mail

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | A coordenadora da CCIH abre a tela **Alerta de Multirresistência** e clica em **Notificar Equipe**. | O sistema exibe o modal **Notificar Equipe** com os campos **Destinatários** preenchidos com "coordenadora da CCIH" e "enfermeiro responsável", o campo **Canal** preenchido com "e-mail" e o botão **Enviar Notificação**. | pronto |
| 2 | A coordenadora da CCIH confere os destinatários e clica em **Enviar Notificação**. | O sistema registra o instante de início do envio e aciona o serviço de envio de e-mail (FR-073), enviando o alerta com o texto redigido. | código gerado |
| 3 | O serviço de e-mail devolve confirmação de envio. | O sistema registra a **Notificação** com destinatário, canal "e-mail" e tempo decorrido, e exibe no modal **Notificar Equipe** a mensagem "Notificação enviada para coordenadora da CCIH e enfermeiro responsável". | código gerado |
| 4 | O sistema grava a notificação na trilha de auditoria. | O sistema registra na trilha de auditoria o usuário que disparou a notificação, o alerta afetado e a data/hora (FR-005, FR-056). | pronto |
| 5 | A coordenadora da CCIH fecha o modal **Notificar Equipe**. | O sistema fecha o modal e retorna à tela **Alerta de Multirresistência**, exibindo na lista **Notificações** a entrada recém-criada com destinatário, canal e tempo decorrido. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | A coordenadora da CCIH deseja registrar a notificação sem enviar e-mail imediatamente. | A coordenadora clica em **Cancelar** no modal **Notificar Equipe**. | O sistema fecha o modal **Notificar Equipe** e retorna à tela **Alerta de Multirresistência** sem registrar notificação e sem alterar a **Situação** do alerta. | pronto |
| A2 | O enfermeiro responsável dispara a notificação em vez da coordenadora. | O enfermeiro clica em **Notificar Equipe** e depois em **Enviar Notificação**. | O sistema envia a notificação para coordenadora da CCIH e enfermeiro responsável, registra a **Notificação** com destinatário, canal e tempo decorrido e grava o usuário que disparou. | código gerado |
| A3 | O envio de e-mail não está configurado no servidor. | A coordenadora clica em **Enviar Notificação**. | O sistema exibe no modal **Notificar Equipe** a mensagem "Envio de e-mail não configurado — notificação não enviada" e não marca a notificação como enviada (FR-062, BR-018). | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O serviço de envio de e-mail não responde. | O sistema exibe no modal **Notificar Equipe** a mensagem "Falha no envio da notificação" e registra o status de falha, sem simular sucesso (FR-038), com o botão **Tentar novamente** disponível. | código gerado |
| E2 | O serviço de e-mail devolve erro de destinatário inválido. | O sistema exibe no modal **Notificar Equipe** a mensagem "Não foi possível enviar para [destinatário]" e registra a **Notificação** com status de falha, mantendo o alerta com **Situação** "aberto". | código gerado |
| E3 | O servidor recusa a chamada por token ausente ou vencido. | O sistema encerra a sessão, exibe a mensagem "Sessão expirada — entre novamente" e redireciona para a tela **Login com e-mail e senha** (FR-064). | pronto |

#### UC-015: Recomendar Bundle ao Caso Confirmado

| Campo | Detalhe |
|---|---|
| **Natureza** | **agêntica** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O sistema identifica que o caso foi classificado como confirmado e aciona o agente de IA para recomendar o bundle. | A tela **Recomendação de Tratamento** é exibida com o bloco **Recomendação do Sistema** em estado "Analisando…", e o sistema envia ao agente o resultado do NHSN, a situação de multirresistência e a lista de bundles cadastrados. | código gerado |
| 2 | O agente de IA lê o resultado do NHSN e a situação de multirresistência do caso. | O sistema mantém o bloco **Recomendação do Sistema** em processamento; nenhum bundle é exibido até a análise concluir. | código gerado |
| 3 | O agente de IA seleciona o bundle aplicável entre os cadastrados, considerando o resultado do NHSN e a presença de multirresistência. | O sistema preenche o bloco **Recomendação do Sistema** com o campo **Bundle Recomendado**, o campo **Indicação**, o campo **Redução Média de Risco** e o campo **Intervalo de Confiança** do bundle selecionado. | agente |
| 4 | O agente de IA redige a justificativa da recomendação, citando o resultado do NHSN e a situação de multirresistência. | O sistema preenche o bloco **Justificativa** com o texto gerado, exibindo a linha "Resultado NHSN: [resultado]" e a linha "Multirresistência: [presente/ausente]". | agente |
| 5 | O sistema verifica que o bundle recomendado é compatível com a situação de multirresistência registrada. | O sistema exibe no bloco **Recomendação do Sistema** o selo "Compatível com multirresistência registrada" quando não há multirresistência e o bundle não é de germe multirresistente. | código gerado |
| 6 | O médico abre a tela **Recomendação de Tratamento** e lê a recomendação. | O sistema exibe o **Bundle Recomendado**, a **Justificativa** e os dados de redução de risco, com o botão **Aceitar Recomendação** e o botão **Escolher Outro Bundle** disponíveis. | pronto |
| 7 | O médico pode opcionalmente: | | pronto |
| 7.1 | Clica em **Aceitar Recomendação**. | O sistema registra a aceitação da recomendação original e grava a ação na trilha de auditoria com o usuário e a data/hora. | pronto |
| 7.2 | Clica em **Escolher Outro Bundle**, seleciona outro bundle na lista e confirma. | O sistema registra a escolha médica divergente e mantém a recomendação original do sistema registrada junto (FR-042, BR-031). | código gerado |
| 7.3 | Clica em **Ver Justificativa**. | O sistema expande o bloco **Justificativa** com o texto completo citando o resultado do NHSN e a situação de multirresistência. | pronto |
| 8 | O sistema grava a recomendação, a justificativa e a versão do agente usados na decisão. | O sistema confirma na tela **Recomendação de Tratamento** a mensagem "Recomendação registrada" e mantém a recomendação disponível para auditoria. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | Os dados do caso não sustentam uma recomendação de bundle. | O agente de IA não seleciona bundle. | O sistema exibe no bloco **Recomendação do Sistema** a mensagem "Os dados não sustentam uma recomendação" e registra a declaração de insuficiência em vez de recomendação (FR-044, FR-082). | agente |
| A2 | O caso não tem multirresistência registrada e o bundle candidato é de germe multirresistente. | O agente de IA descarta o bundle incompatível. | O sistema não exibe o bundle de germe multirresistente no bloco **Recomendação do Sistema** e mantém apenas bundles compatíveis com caso sem multirresistência (FR-043, BR-012). | código gerado |
| A3 | O caso não está confirmado. | O sistema não aciona o agente de IA. | O sistema exibe na tela **Recomendação de Tratamento** a mensagem "Recomendação de bundle disponível apenas para caso confirmado" e não gera recomendação (FR-039). | código gerado |
| A4 | O médico escolhe outro bundle após a recomendação do sistema. | O médico clica em **Escolher Outro Bundle** e seleciona outro bundle. | O sistema mantém a recomendação original do sistema registrada no bloco **Recomendação do Sistema** e exibe a escolha médica no bloco **Escolha do Médico** (FR-042, BR-031). | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O agente de IA não consegue concluir a recomendação no tempo esperado. | O sistema exibe no bloco **Recomendação do Sistema** a mensagem "Não foi possível recomendar agora" e mantém o botão **Tentar novamente** disponível, sem exibir bundle inventado. | código gerado |
| E2 | Não há bundle cadastrado compatível com o resultado do NHSN e a situação de multirresistência. | O sistema exibe no bloco **Recomendação do Sistema** a mensagem "Nenhum bundle compatível cadastrado" e não recomenda bundle algum. | código gerado |
| E3 | A justificativa gerada pelo agente não cita o resultado do NHSN nem a situação de multirresistência. | O sistema descarta a justificativa, exibe no bloco **Justificativa** a mensagem "Justificativa incompleta — recomendação não aceita" e mantém a recomendação sem justificativa afirmativa (FR-045). | código gerado |
| E4 | O servidor recusa a chamada por token ausente ou vencido. | O sistema encerra a sessão, exibe a mensagem "Sessão expirada — entre novamente" e redireciona para a tela **Login com e-mail e senha** (FR-064). | pronto |

#### UC-016: Cadastrar Bundles com Dados de Risco

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O `administrador` ou a `coordenadora CCIH` acessa a funcionalidade de gestão de bundles e clica em "Cadastrar Novo Bundle". | O sistema exibe a tela **"Cadastro de Bundle"** com um formulário contendo os campos: "Nome do Bundle", "Indicação", "Redução Média de Risco (%)" e "Intervalo de Confiança". | pronto |
| 2 | O usuário preenche todos os campos do formulário com os dados do novo bundle. | O sistema habilita o botão "Salvar" após o preenchimento dos campos obrigatórios. | pronto |
| 3 | O usuário clica no botão "Salvar". | O sistema valida os dados, persiste o novo bundle no banco de dados e exibe a mensagem de sucesso: "Bundle '[Nome do Bundle]' cadastrado com sucesso." Em seguida, a tela é limpa para um novo cadastro. | pronto |
| 4 | O usuário pode opcionalmente: | | pronto |
| 4.1 | Clicar no botão "Cancelar". | O sistema fecha a tela de cadastro e retorna para a tela anterior (ex: lista de bundles), sem salvar nenhuma informação. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O usuário deseja cadastrar um bundle com um nome que já existe. | O usuário preenche o campo "Nome do Bundle" com um nome já existente e clica em "Salvar". | O sistema impede o cadastro e exibe a mensagem de erro: "Já existe um bundle com este nome. Por favor, utilize um nome diferente." | pronto |
| A2 | O usuário decide não preencher um dos campos obrigatórios. | O usuário deixa o campo "Indicação" em branco e clica em "Salvar". | O sistema impede o cadastro e exibe a mensagem de erro: "O campo 'Indicação' é obrigatório." | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | Falha na conexão com o banco de dados. | O sistema exibe a mensagem de erro: "Não foi possível salvar o bundle. Erro de comunicação com o banco de dados. Tente novamente." e um botão "Tentar novamente". | pronto |
| E2 | O valor inserido no campo "Redução Média de Risco (%)" não é um número. | O sistema exibe a mensagem de erro: "O campo 'Redução Média de Risco' deve conter apenas números." | pronto |

#### UC-017: Registrar Escolha Médica de Outro Bundle

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O `médico` acessa a tela de **"Detalhes do Caso"** de um paciente cujo caso está confirmado e possui uma recomendação de bundle. | O sistema exibe os detalhes do caso, incluindo um painel **"Recomendação de Tratamento"** que mostra o bundle recomendado pelo sistema e sua justificativa. Abaixo, exibe o botão "Escolher Outro Bundle". | pronto |
| 2 | O `médico` clica no botão "Escolher Outro Bundle". | O sistema abre um modal **"Selecionar Bundle Alternativo"** com uma lista de todos os outros bundles disponíveis para seleção. | código gerado |
| 3 | O `médico` seleciona um bundle diferente da lista. | A linha do bundle selecionado é destacada. O sistema habilita o botão "Confirmar Escolha". | pronto |
| 4 | O `médico` clica em "Confirmar Escolha". | O sistema registra a escolha do médico, atualiza o painel "Recomendação de Tratamento" para exibir o bundle escolhido pelo médico como a conduta atual, e move a recomendação original do sistema para uma seção "Histórico da Recomendação". O sistema exibe a mensagem: "Sua escolha pelo bundle '[Nome do Bundle Escolhido]' foi registrada." | código gerado |
| 5 | O usuário pode opcionalmente: | | pronto |
| 5.1 | Clicar no botão "Cancelar" no modal. | O sistema fecha o modal "Selecionar Bundle Alternativo" sem registrar nenhuma alteração. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | Não existem outros bundles cadastrados no sistema. | O `médico` clica em "Escolher Outro Bundle". | O sistema abre o modal "Selecionar Bundle Alternativo" com a mensagem: "Nenhum outro bundle disponível para seleção." e o botão "Confirmar Escolha" desabilitado. | código gerado |
| A2 | O médico deseja ver os detalhes de um bundle antes de escolher. | O `médico` clica no nome de um bundle na lista do modal. | O sistema exibe um pop-up com os detalhes do bundle: nome, indicação, redução média de risco e intervalo de confiança (FR-040). | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | Falha ao registrar a escolha do médico no banco de dados. | O sistema exibe a mensagem de erro: "Não foi possível registrar sua escolha. Erro de comunicação. Tente novamente." e um botão "Tentar novamente". | pronto |
| E2 | O caso não está mais com o status "confirmado" (ex: foi alterado por outro usuário). | O sistema exibe a mensagem: "Não é possível alterar a conduta, pois o status do caso foi modificado para 'descartado'. A página será atualizada." e recarrega a tela de detalhes do caso. | código gerado |

#### UC-018: Estimar Redução de Risco do Tratamento Escolhido

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O `médico` acessa a tela **"Detalhes do Caso"** de um paciente para o qual um tratamento já foi escolhido. | O sistema exibe os detalhes do caso, incluindo o painel **"Estimativa de Redução de Risco"**. Este painel contém um seletor para "Horizonte de Análise" com as opções "30 dias", "90 dias" e "180 dias". | pronto |
| 2 | O `médico` seleciona um horizonte de análise (ex: "90 dias"). | O sistema habilita o botão "Calcular Estimativa". | pronto |
| 3 | O `médico` clica no botão "Calcular Estimativa". | O sistema busca no cadastro do caso os dados clínicos necessários (idade, APACHE II, sítio de inserção) sem solicitá-los novamente. Em seguida, realiza o cálculo e exibe os resultados no painel: "Redução Absoluta", "Redução Relativa" e "Intervalo de Confiança". | código gerado |
| 4 | O `médico` pode opcionalmente: | | pronto |
| 4.1 | Selecionar um horizonte diferente e clicar em "Calcular Estimativa" novamente. | O sistema recalcula a estimativa com o novo horizonte e atualiza os valores no painel de resultados. | código gerado |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | Um dos dados clínicos necessários para o cálculo não está preenchido no cadastro do caso. | O `médico` clica em "Calcular Estimativa". | O sistema não realiza o cálculo e exibe a mensagem de erro: "Não foi possível calcular a estimativa. O dado 'pontuação APACHE II' não está preenchido no cadastro do caso." (FR-061). | código gerado |
| A2 | O usuário com papel `CCIH` acessa a tela do caso e visualiza a estimativa já calculada. | O `CCIH` visualiza o painel "Estimativa de Redução de Risco" com os valores já calculados pelo médico. | O sistema exibe os resultados da última estimativa calculada e salva para o caso. | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O sistema não consegue realizar o cálculo por um erro interno. | O sistema exibe a mensagem: "Não foi possível calcular a estimativa. Ocorreu um erro inesperado. Tente novamente." e um botão "Tentar novamente". | pronto |
| E2 | O tratamento ainda não foi escolhido para o caso. | O sistema exibe o painel "Estimativa de Redução de Risco" com a mensagem: "A estimativa de risco será habilitada após a escolha do tratamento." e não exibe o botão "Calcular Estimativa". | código gerado |

#### UC-019: Executar Ciclo Integrado de um Caso

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | A coordenadora CCIH acessa a tela **Ciclo Integrado do Caso** e seleciona o caso desejado no campo **Caso**. | O sistema exibe a tela **Ciclo Integrado do Caso** com o campo **Caso** preenchido e a lista **Etapas do Ciclo** mostrando as seis etapas na ordem: 1. Buscar microbiologia, 2. Classificar, 3. Detectar multirresistência, 4. Calcular escore, 5. Recomendar, 6. Estimar. Cada etapa aparece com o status **não executada**. | pronto |
| 2 | A coordenadora CCIH clica em **Executar Ciclo**. | O sistema inicia a execução da sequência e atualiza o status de cada etapa na lista **Etapas do Ciclo** conforme ela conclui. | código gerado |
| 3 | O usuário pode opcionalmente: | | pronto |
| 3.1 | Clica em **Cancelar** antes de acionar **Executar Ciclo**. | O sistema fecha a tela **Ciclo Integrado do Caso** e retorna à tela anterior sem executar nenhuma etapa. | pronto |
| 4 | — | O sistema executa a **Etapa 1 — Buscar microbiologia**: consulta o serviço de microbiologia pelo identificador do paciente (com os dados anonimizados) e importa situação, identificador da amostra, origem, microrganismo, indicação de multirresistência e antibiograma. O status da etapa 1 passa a **concluída** e o resultado é exibido na coluna **Resultado da Etapa**. | código gerado |
| 5 | — | O sistema executa a **Etapa 2 — Classificar**: aplica o critério NHSN vigente à época do caso e atribui a classificação confirmada, descartada ou pendente, registrando o critério e a versão aplicados. O status da etapa 2 passa a **concluída** com o resultado exibido. | código gerado |
| 6 | — | O sistema executa a **Etapa 3 — Detectar multirresistência**: lê a lista de antimicrobianos do antibiograma e decide se o germe é multirresistente pela regra de três ou mais classes. O status da etapa 3 passa a **concluída** com o resultado exibido. | código gerado |
| 7 | — | O sistema executa a **Etapa 4 — Calcular escore**: consulta o serviço de escore de risco de Cox enviando idade, pontuação APACHE II e tipo de cateter, e armazena escore, faixa de risco, preditor linear, fatores que pesaram, nome da versão do modelo e data do cálculo. O status da etapa 4 passa a **concluída** com o resultado exibido. | código gerado |
| 8 | — | O sistema executa a **Etapa 5 — Recomendar**: quando o caso estiver confirmado, recomenda o bundle considerando o resultado do NHSN e a presença de multirresistência, com justificativa em texto. O status da etapa 5 passa a **concluída** com o resultado exibido. | código gerado |
| 9 | — | O sistema executa a **Etapa 6 — Estimar**: estima a redução de risco usando os dados clínicos do próprio cadastro do caso, devolvendo redução absoluta, redução relativa e intervalo de confiança. O status da etapa 6 passa a **concluída** com o resultado exibido. | código gerado |
| 10 | A coordenadora CCIH confere a lista **Etapas do Ciclo** com o status e o resultado de cada uma. | O sistema exibe, para cada etapa, se foi concluída e o resultado obtido, e mantém o botão **Ver Detalhe do Caso** disponível para consulta aprofundada. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O caso não tem os cinco dados de risco preenchidos. | A coordenadora CCIH clica em **Executar Ciclo**. | O sistema não inicia a etapa 4 (Calcular escore) e exibe na lista **Etapas do Ciclo** a etapa 4 com status **falhou** e a mensagem "Falta o dado: [nome do dado faltante]. A conta de risco não pode ser executada." As etapas 5 e 6, dependentes do escore, ficam com status **não executada**. | código gerado |
| A2 | O retorno da microbiologia vem como "pendente", sem microrganismo. | A coordenadora CCIH clica em **Executar Ciclo**. | O sistema conclui a etapa 1 registrando o estado pendente, sem criar microrganismo ou antibiograma fictício. A etapa 2 (Classificar) resulta em **pendente** e a etapa 3 (Detectar multirresistência) fica com status **não executada** por falta de antibiograma. | código gerado |
| A3 | A coordenadora CCIH deseja reexecutar o ciclo para o mesmo caso. | A coordenadora CCIH clica em **Executar Ciclo** novamente. | O sistema reconhece que o mesmo resultado de laboratório já foi importado e não cria registro repetido, reexecutando as etapas sobre os dados já existentes. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O laboratório está fora do ar ou o tempo limite da consulta estourou. | O sistema marca a etapa 1 como **falhou** e exibe a mensagem "O laboratório está fora do ar. Não foi possível buscar a microbiologia." com o botão **Tentar novamente**. Nenhum resultado vazio é apresentado como resultado normal. | código gerado |
| E2 | O serviço de escore de Cox não responde. | O sistema marca a etapa 4 como **falhou** e exibe a mensagem "O serviço de escore não respondeu. Nenhum escore foi gravado." Nenhum registro de escore é criado para o caso. | código gerado |
| E3 | O envio da notificação de alerta falha. | O sistema registra e exibe o status de falha da notificação, sem simular sucesso, e mantém o resultado das demais etapas do ciclo. | código gerado |

#### UC-020: Consultar Painel de Vigilância por Período

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | A CCIH acessa a tela **Painel de Vigilância**. | O sistema exibe a tela **Painel de Vigilância** com o filtro **Período** e carrega os indicadores do período padrão. | pronto |
| 2 | A CCIH escolhe o período desejado no filtro **Período**, entre as opções 7, 30, 90 ou 365 dias. | O sistema recalcula e atualiza os seis indicadores conforme o período escolhido. | código gerado |
| 3 | A CCIH lê os cards de indicadores: **Casos Ativos**, **Escore Médio de Risco**, **Casos Classificados pelo NHSN**, **Alertas de Multirresistência Abertos**, **Conformidade por Mês** e **Distribuição dos Casos por Faixa de Risco**. | O sistema exibe os seis indicadores para o período selecionado: os quatro primeiros como cards numéricos, **Conformidade por Mês** como gráfico de barras e **Distribuição dos Casos por Faixa de Risco** como gráfico de pizza. | pronto |
| 4 | O usuário pode opcionalmente: | | pronto |
| 4.1 | Passa o mouse sobre uma barra do gráfico **Conformidade por Mês**. | O sistema exibe o valor exato do mês apontado. | pronto |
| 4.2 | Passa o mouse sobre uma fatia do gráfico **Distribuição dos Casos por Faixa de Risco**. | O sistema exibe a quantidade e o percentual da faixa de risco apontada (baixo, moderado ou alto). | pronto |
| 5 | A CCIH clica em **Atualizar**. | O sistema recarrega os indicadores do período selecionado a partir do banco. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | Não há casos registrados no período selecionado. | A CCIH escolhe o período no filtro **Período**. | O sistema exibe os cards com campo vazio e a explicação "Não há casos registrados neste período.", sem apresentar zero como se fosse resultado de cálculo nem número inventado. | código gerado |
| A2 | Alguns casos do período não têm escore de risco calculado. | A CCIH lê o card **Escore Médio de Risco**. | O sistema calcula a média apenas sobre os casos que possuem escore e indica quantos casos não têm escore, sem inventar valor para os ausentes. | código gerado |
| A3 | A CCIH deseja consultar outro período. | A CCIH troca a opção no filtro **Período**. | O sistema recalcula os seis indicadores para o novo período e atualiza os cards e gráficos. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O banco de dados não responde à consulta dos indicadores. | O sistema exibe a mensagem "Não foi possível carregar o painel. Não consegui obter os indicadores." com o botão **Tentar novamente**, sem apresentar número indefensável. | pronto |
| E2 | O token de acesso está vencido. | O servidor recusa a chamada, a sessão expira e o sistema exige novo login antes de recarregar o painel. | pronto |

#### UC-021: Exportar Relatório de Vigilância em PDF ou CSV

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | A CCIH acessa a tela **Exportar Relatório de Vigilância**. | O sistema exibe a tela **Exportar Relatório de Vigilância** com os campos **Período**, **Formato** e **Filtrar por Paciente**. | pronto |
| 2 | A CCIH seleciona o período desejado no campo **Período**. | O sistema registra o período selecionado. | pronto |
| 3 | A CCIH escolhe o formato no campo **Formato**, entre PDF ou CSV. | O sistema registra o formato escolhido. | pronto |
| 4 | O usuário pode opcionalmente: | | pronto |
| 4.1 | Preenche o campo **Filtrar por Paciente** com o paciente desejado. | O sistema registra o filtro por paciente para restringir o conjunto de registros exportados. | pronto |
| 5 | A CCIH clica em **Gerar Relatório**. | O sistema gera o arquivo no formato escolhido, contendo os casos, os escores, as classificações e os alertas do período e do filtro aplicados. | pronto |
| 6 | — | O sistema exibe a mensagem "Foram exportados [N] registros." e disponibiliza o arquivo gerado no botão **Baixar Arquivo**. | código gerado |
| 7 | A CCIH clica em **Baixar Arquivo**. | O sistema entrega o arquivo do relatório de vigilância para download. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | Não há registros no período e filtro selecionados. | A CCIH clica em **Gerar Relatório**. | O sistema informa "Foram exportados 0 registros." e não disponibiliza arquivo vazio como se fosse relatório com conteúdo. | código gerado |
| A2 | A CCIH deseja exportar o mesmo período em outro formato. | A CCIH troca o campo **Formato** de PDF para CSV e clica em **Gerar Relatório**. | O sistema gera novo arquivo no formato escolhido e atualiza a contagem de registros exportados. | pronto |
| A3 | A CCIH deseja cancelar antes de gerar. | A CCIH clica em **Cancelar**. | O sistema fecha a tela **Exportar Relatório de Vigilância** e retorna à tela anterior sem gerar arquivo. | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O banco de dados não responde à consulta dos registros a exportar. | O sistema exibe a mensagem "Não foi possível gerar o relatório. Não consegui obter os registros." com o botão **Tentar novamente**, sem gerar arquivo com dados inventados. | pronto |
| E2 | A geração do arquivo falha. | O sistema informa "Não foi possível gerar o arquivo." e não marca a exportação como concluída. | código gerado |
| E3 | O token de acesso está vencido. | O servidor recusa a chamada, a sessão expira e o sistema exige novo login antes de gerar o relatório. | pronto |

#### UC-022: Sinalizar Falhas e Dados Faltantes ao Usuário

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O médico abre a tela "Detalhe do Caso Clínico" de um caso que já teve escore de Cox calculado. | O sistema renderiza a tela "Detalhe do Caso Clínico" com todos os campos preenchidos a partir do banco: "Idade na data", "Dias de cateter", "APACHE II", "Sítio de inserção", "Comorbidades relevantes", "Escore de Cox", "Faixa de risco", "Versão do modelo". Nenhum campo exibe valor de exemplo. | pronto |
| 2 | O médico observa que o campo "Escore de Cox" aparece vazio. | O sistema exibe, no lugar do valor, o texto "Sem escore calculado para este caso" e, ao lado, o botão "Calcular escore". Nenhum número fictício é mostrado. | código gerado |
| 3 | O médico clica em "Calcular escore". | O sistema verifica os cinco dados de risco. Como todos estão preenchidos, o sistema aciona o servidor, que consulta o serviço estatístico externo de Cox. | código gerado |
| 4 | O médico aguarda a resposta. | O sistema exibe, na própria tela, o indicador "Consultando serviço de escore..." enquanto a chamada está em andamento. | pronto |
| 5 | O serviço estatístico externo não responde dentro do tempo limite. | O sistema NÃO grava escore nenhum. A tela "Detalhe do Caso Clínico" exibe, no campo "Escore de Cox", a mensagem explícita "Não consegui obter o escore: o serviço de escore não respondeu." e o botão "Tentar novamente". O campo permanece vazio, sem valor numérico. | código gerado |
| 6 | O médico clica em "Tentar novamente". | O sistema repete a consulta ao serviço estatístico externo. | código gerado |
| 7 | O serviço responde com sucesso desta vez. | O sistema preenche os campos "Escore de Cox", "Faixa de risco", "Preditor linear", "Fatores que pesaram" e "Versão do modelo" com os valores reais retornados, e exibe a mensagem "Escore obtido com sucesso." | código gerado |
| 8 | O médico acessa a tela "Detalhe do Caso Clínico" de outro caso, cujo resultado de hemocultura ainda não está pronto. | O sistema exibe, no campo "Microrganismo isolado", o texto "Resultado pendente no laboratório" e, no campo "Antibiograma", o texto "Aguardando resultado". Nenhum microrganismo ou antibiograma fictício é mostrado. | código gerado |
| 9 | O médico abre a tela "Painel de Vigilância" para o período de 30 dias. | O sistema exibe os seis indicadores com valores reais calculados a partir do banco. Para qualquer indicador sem dado no período, o sistema exibe "Sem dados no período selecionado" em vez de zero inventado. | código gerado |
| 10 | O administrador acessa a tela "Consulta ao Log de Auditoria" e filtra por um usuário que não possui ações registradas. | O sistema exibe a mensagem "Nenhum registro de auditoria encontrado para os filtros aplicados" e a tabela permanece vazia, sem linhas de exemplo. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O laboratório está fora do ar no momento da consulta. | O médico clica em "Buscar microbiologia". | O sistema exibe na tela "Detalhe do Caso Clínico" a mensagem "O laboratório está fora do ar. Não foi possível buscar o resultado agora." e o botão "Tentar novamente". Nenhum resultado vazio é apresentado como se fosse resultado normal. | código gerado |
| A2 | Faltam dados para uma conta. | O médico clica em "Calcular escore" com o campo "APACHE II" vazio. | O sistema exibe a mensagem "Não é possível calcular o escore: falta o dado APACHE II." e destaca o campo "APACHE II" na tela. Nenhum cálculo é executado. | código gerado |
| A3 | O envio de e-mail não está configurado. | O administrador tenta disparar uma notificação de alerta. | O sistema exibe a mensagem "O envio de e-mail não está configurado. A notificação não foi enviada." e a notificação NÃO é marcada como enviada. | código gerado |
| A4 | O campo "Versão do modelo" está preenchido, mas o campo "Data do cálculo" está vazio por falha de persistência. | O médico abre a tela "Detalhe do Caso Clínico". | O sistema exibe, no campo "Data do cálculo", o texto "Data do cálculo não registrada" e o botão "Registrar data do cálculo". Nenhuma data fictícia é mostrada. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O servidor retorna erro 500 ao consultar o serviço de escore. | O sistema exibe na tela "Detalhe do Caso Clínico" a mensagem "Não consegui obter o escore: erro no serviço de escore." e o botão "Tentar novamente". Nenhum escore é gravado. | código gerado |
| E2 | O banco de dados está indisponível no momento da renderização da tela. | O sistema exibe a mensagem "Não consegui carregar os dados do caso: banco de dados indisponível." e o botão "Tentar novamente". A tela permanece sem dados, sem valores de exemplo. | pronto |
| E3 | O serviço de laboratório retorna uma mensagem de erro de cadastro da amostra. | O sistema registra a mensagem de erro e exibe na tela "Detalhe do Caso Clínico" o texto "O laboratório retornou um erro de cadastro da amostra: <mensagem>." Nenhum resultado fictício é criado. | código gerado |
| E4 | O tempo limite da consulta ao laboratório estoura. | O sistema exibe a mensagem "A consulta ao laboratório excedeu o tempo limite. Não consegui obter o resultado." e o botão "Tentar novamente". | código gerado |

#### UC-023: Proteger Credenciais e Chamadas Externas do Sistema

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O administrador acessa a tela "Configuração de Serviços Externos" para verificar as credenciais configuradas. | O sistema exibe a tela "Configuração de Serviços Externos" com os campos "URL do laboratório", "URL do motor de risco", "URL do serviço de e-mail" e, para cada um, o campo "Credencial" preenchido com o texto "••••••••" (mascarado). Nenhuma credencial em texto aberto é exibida. | código gerado |
| 2 | O administrador clica em "Testar conexão" ao lado do serviço de laboratório. | O sistema aciona o servidor, que lê a credencial do arquivo de configuração do servidor (nunca do código nem da tela) e realiza uma chamada de teste ao laboratório. | código gerado |
| 3 | O laboratório responde com sucesso. | O sistema exibe a mensagem "Conexão com o laboratório bem-sucedida." | código gerado |
| 4 | O administrador clica em "Testar conexão" ao lado do motor de risco. | O sistema aciona o servidor, que lê a credencial do arquivo de configuração e realiza uma chamada de teste ao motor de risco. | código gerado |
| 5 | O motor de risco responde com sucesso. | O sistema exibe a mensagem "Conexão com o motor de risco bem-sucedida." | código gerado |
| 6 | O administrador clica em "Testar conexão" ao lado do serviço de e-mail. | O sistema aciona o servidor, que lê a credencial do arquivo de configuração e realiza uma chamada de teste ao serviço de e-mail. | código gerado |
| 7 | O serviço de e-mail responde com sucesso. | O sistema exibe a mensagem "Conexão com o serviço de e-mail bem-sucedida." | código gerado |
| 8 | O médico aciona o comando único do ciclo integrado para um caso. | O servidor monta o payload de chamada ao laboratório com os dados do paciente já anonimizados (identificador do caso no lugar do nome, prontuário e data de nascimento). | código gerado |
| 9 | O servidor envia a chamada ao laboratório. | O laboratório recebe apenas o identificador anonimizado e retorna o resultado de microbiologia. | código gerado |
| 10 | O servidor recebe o resultado e o associa ao caso pelo identificador interno. | O sistema exibe na tela "Detalhe do Caso Clínico" o resultado de microbiologia associado ao caso correto. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | A credencial do laboratório não está definida no arquivo de configuração. | O administrador clica em "Testar conexão". | O sistema exibe a mensagem "Credencial do laboratório não configurada no servidor. Configure antes de testar." e não realiza a chamada. | código gerado |
| A2 | O administrador tenta editar a credencial diretamente na tela. | O administrador clica no campo "Credencial". | O sistema exibe a mensagem "A credencial é somente leitura nesta tela. Altere-a no arquivo de configuração do servidor." e o campo permanece mascarado. | pronto |
| A3 | O payload de chamada ao laboratório contém dado identificável do paciente por falha de montagem. | O servidor detecta a presença de nome ou prontuário no payload. | O servidor bloqueia o envio, registra em auditoria "Chamada ao laboratório bloqueada: payload continha dado identificável" e retorna erro à função chamadora. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O arquivo de configuração do servidor não pôde ser lido. | O sistema exibe na tela "Configuração de Serviços Externos" a mensagem "Não consegui ler a configuração do servidor. Verifique o arquivo de configuração." e o botão "Tentar novamente". | código gerado |
| E2 | A chamada de teste ao laboratório falha por credencial inválida. | O sistema exibe a mensagem "Falha na conexão com o laboratório: credencial inválida." Nenhuma credencial é exibida na mensagem. | código gerado |
| E3 | A chamada de teste ao motor de risco excede o tempo limite. | O sistema exibe a mensagem "Falha na conexão com o motor de risco: tempo limite excedido." e o botão "Tentar novamente". | código gerado |
| E4 | O serviço de e-mail retorna erro de autenticação. | O sistema exibe a mensagem "Falha na conexão com o serviço de e-mail: autenticação recusada." Nenhuma credencial é exibida na mensagem. | código gerado |

#### UC-024: Padronizar Nomes de Dados entre Telas e Banco

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | A equipe de desenvolvimento abre a tela "Dicionário de Dados" do sistema. | O sistema exibe a tela "Dicionário de Dados" com a lista de todos os dados padronizados: "Identificador do caso", "Nome do paciente", "Data de nascimento", "Sexo", "Número do prontuário", "Médico responsável", "Idade na data", "Dias de cateter", "APACHE II", "Sítio de inserção", "Comorbidades relevantes", "Escore de Cox", "Faixa de risco", "Preditor linear", "Fatores que pesaram", "Versão do modelo", "Data do cálculo", "Identificador da amostra", "Origem da amostra", "Microrganismo isolado", "Antibiograma", "Classificação", "Critério aplicado", "Versão do critério". | pronto |
| 2 | A equipe de desenvolvimento seleciona o dado "Identificador do caso". | O sistema exibe, no painel lateral, o nome canônico "Identificador do caso" e a lista de todas as telas e tabelas do banco onde esse dado aparece, com o nome usado em cada uma. | pronto |
| 3 | A equipe de desenvolvimento verifica que todas as telas e tabelas usam o nome "Identificador do caso". | O sistema exibe a mensagem "Nenhuma inconsistência de nomenclatura encontrada para o dado Identificador do caso." | código gerado |
| 4 | A equipe de desenvolvimento seleciona o dado "Número do prontuário". | O sistema exibe o nome canônico "Número do prontuário" e a lista de telas e tabelas onde aparece. | pronto |
| 5 | A equipe de desenvolvimento detecta que uma tela usa o nome "Prontuário" em vez de "Número do prontuário". | O sistema destaca a inconsistência em vermelho e exibe a mensagem "Inconsistência de nomenclatura: a tela Detalhe do Caso Clínico usa 'Prontuário' em vez de 'Número do prontuário'." | código gerado |
| 6 | A equipe de desenvolvimento clica em "Corrigir nomenclatura". | O sistema altera o rótulo da tela "Detalhe do Caso Clínico" para "Número do prontuário" e registra a correção em auditoria. | pronto |
| 7 | A equipe de desenvolvimento clica em "Revalidar dicionário". | O sistema reexamina todas as telas e tabelas e exibe a mensagem "Dicionário validado: nenhuma inconsistência encontrada." | código gerado |
| 8 | A equipe de desenvolvimento exporta o dicionário de dados. | O sistema gera um arquivo CSV com a lista de dados padronizados, seus nomes canônicos e as telas e tabelas onde aparecem, e informa "Dicionário exportado: 24 dados padronizados." | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | Um novo dado é adicionado ao sistema sem passar pelo dicionário. | A equipe de desenvolvimento clica em "Adicionar dado ao dicionário". | O sistema exibe o formulário "Novo dado padronizado" com os campos "Nome canônico", "Descrição" e "Telas e tabelas onde aparece". | pronto |
| A2 | Um dado do dicionário não é usado em nenhuma tela ou tabela. | A equipe de desenvolvimento seleciona o dado. | O sistema exibe a mensagem "O dado 'Preditor linear' não é usado em nenhuma tela ou tabela no momento." e o botão "Remover do dicionário". | código gerado |
| A3 | A equipe de desenvolvimento quer ver o nome do dado no banco. | A equipe de desenvolvimento clica em "Ver no banco". | O sistema exibe o nome da coluna no banco correspondente ao dado selecionado, por exemplo "caso_id" para "Identificador do caso". | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O banco de dados está indisponível no momento da validação. | O sistema exibe a mensagem "Não consegui validar o dicionário: banco de dados indisponível." e o botão "Tentar novamente". | pronto |
| E2 | A tela "Detalhe do Caso Clínico" não pôde ser inspecionada por falha de renderização. | O sistema exibe a mensagem "Não consegui inspecionar a tela Detalhe do Caso Clínico. Verifique a renderização." e o botão "Tentar novamente". | código gerado |
| E3 | A correção de nomenclatura falha ao ser gravada. | O sistema exibe a mensagem "Não consegui corrigir a nomenclatura: falha ao gravar a alteração." e o botão "Tentar novamente". Nenhuma alteração parcial é persistida. | pronto |

#### UC-025: Sinalizar Hemocultura Pronta e Suspeita de ICSAC

| Campo | Detalhe |
|---|---|
| **Natureza** | **agêntica** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O analista do laboratório de microbiologia libera o resultado da hemocultura no sistema do laboratório. | O sistema, pela rotina de integração, consulta o sistema do laboratório pelo número do prontuário do paciente e recebe o resultado com identificador da amostra, origem (hemocultura, ponta de cateter ou outra), microrganismo isolado e antibiograma. | código gerado |
| 2 | — | O agente de IA lê o resultado bruto vindo do laboratório e o traduz para a nomenclatura adotada pelo hospital. | agente |
| 2.1 | O analista do laboratório de microbiologia pode, opcionalmente, abrir a tela "Acompanhamento Diário de Pacientes de UTI com Cateter" para conferir o resultado já traduzido. | O sistema exibe na coluna "Resultado traduzido" o microrganismo isolado e a origem da amostra na nomenclatura do hospital. | pronto |
| 3 | — | O agente de IA aplica o critério NHSN vigente à época do caso e decide se o caso configura suspeita de infecção de corrente sanguínea, indicando em cima de qual critério decidiu. | agente |
| 4 | — | O agente de IA examina a lista de antimicrobianos do antibiograma e decide se o germe é multirresistente, aplicando a regra de resistência a três ou mais classes. | agente |
| 5 | — | O sistema sinaliza o caso na lista de acompanhamento diário com o rótulo "Hemocultura pronta — suspeita de ICSAC" e registra o critério e a versão aplicados. | código gerado |
| 6 | — | Quando o agente identifica multirresistência, o sistema destaca o caso como prioritário, aplicando a marca "Prioritário — germe multirresistente" na primeira coluna da lista. | código gerado |
| 7 | O médico ou o enfermeiro abre a tela "Acompanhamento Diário de Pacientes de UTI com Cateter" e seleciona o filtro "Somente prioritários". | O sistema reordena a lista, trazendo primeiro os casos com a marca de urgência, e exibe, para o caso selecionado, o painel "Detalhe da sinalização" com o microrganismo, o antibiograma traduzido, o critério NHSN aplicado, a versão da norma e o motivo da sinalização. | pronto |
| 8 | O médico clica em "Registrar ciência da sinalização". | O sistema grava na trilha de auditoria o usuário, a data/hora e o registro afetado, e passa a exibir a sinalização como "Ciência registrada" para aquele caso. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O laboratório retorna "pendente", sem microrganismo nenhum. | O analista do laboratório de microbiologia mantém o caso em observação. | O sistema registra o estado pendente na coluna "Situação da hemocultura", não cria microrganismo nem antibiograma fictício, não sinaliza suspeita de ICSAC e exibe a mensagem "Hemocultura pendente no laboratório — sem resultado clínico disponível". | código gerado |
| A2 | O laboratório retorna mensagem de erro de cadastro da amostra. | O analista do laboratório de microbiologia corrige o cadastro da amostra no sistema do laboratório. | O sistema registra a mensagem recebida, não sinaliza suspeita de ICSAC e exibe "Laboratório retornou erro de cadastro da amostra: [mensagem do laboratório]" com o botão "Consultar novamente". | código gerado |
| A3 | O mesmo resultado já havia sido buscado antes. | O analista do laboratório de microbiologia aciona "Consultar novamente". | O sistema reconhece que o resultado já foi importado, não cria registro repetido e reaproveita a sinalização existente, exibindo "Resultado já importado — sinalização mantida". | código gerado |
| A4 | O resultado existe, mas o agente conclui que o caso não configura suspeita de ICSAC. | O médico abre o caso na lista de acompanhamento diário. | O sistema não aplica o rótulo de suspeita, exibe "Sem suspeita de ICSAC pelo critério NHSN [versão]" e mantém o caso na lista comum, sem destaque de urgência. | código gerado |
| A5 | O resultado indica germe multirresistente, mas o caso não tem multirresistência registrada anteriormente. | O enfermeiro clica em "Ver antibiograma traduzido". | O sistema exibe a lista de antimicrobianos traduzida, com classe e resultado de cada um, e a marca "Prioritário — germe multirresistente", sem recomendar bundle de germe multirresistente para caso sem multirresistência registrada. | código gerado |
| A6 | O agente não consegue concluir o julgamento por falta de dado clínico do caso. | O médico consulta o "Detalhe da sinalização". | O sistema exibe "Não foi possível concluir a sinalização: falta o dado [nome do dado faltante]" e não apresenta classificação inventada. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O sistema do laboratório está fora do ar. | A tela exibe "Laboratório fora do ar — não foi possível buscar a hemocultura" e não mostra resultado vazio como se fosse resultado normal; o botão "Consultar novamente" fica disponível. | código gerado |
| E2 | A consulta ao laboratório excede o tempo limite. | O sistema falha explicitamente, exibe "Tempo limite excedido na consulta ao laboratório — nenhum resultado foi obtido" e registra a falha na trilha de auditoria, sem criar sinalização. | código gerado |
| E3 | O agente de IA não consegue traduzir a nomenclatura devolvida pelo laboratório. | O sistema marca o resultado como não aproveitável, exibe "Resultado não aproveitável — nomenclatura do laboratório não reconhecida" e não gera sinalização nem valor clínico inventado. | código gerado |
| E4 | O agente de IA fica indisponível no momento da sinalização. | O sistema exibe "Não foi possível executar a sinalização de ICSAC — agente indisponível" e mantém o resultado bruto do laboratório visível, sem classificação. | código gerado |

#### UC-026: Executar Backup Automatizado com RTO e RPO

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O administrador entra com e-mail e senha e abre a tela "Backup Automatizado". | O sistema valida o token de acesso, exibe a tela "Backup Automatizado" com os campos "Periodicidade", "Horário de execução", "Destino do backup", "Retenção (dias)", "RTO alvo" e "RPO alvo", já preenchidos com a configuração vigente. | pronto |
| 2 | O administrador ajusta o campo "Periodicidade" para "Diário" e o campo "Horário de execução" para "02:00". | O sistema aceita os valores e habilita o botão "Salvar configuração". | pronto |
| 3 | O administrador clica em "Salvar configuração". | O sistema persiste a configuração, exibe a mensagem "Configuração de backup salva" e grava na trilha de auditoria quem fez, o que fez, sobre qual registro e quando. | pronto |
| 4 | O administrador clica em "Executar backup agora". | O sistema inicia a execução do backup dos dados clínicos e da trilha de auditoria, exibe a barra "Executando backup..." e desabilita o botão "Executar backup agora" enquanto a execução estiver em curso. | código gerado |
| 5 | — | Ao concluir, o servidor grava no destino configurado o conjunto de backup e registra data/hora, escopo, duração e resultado da execução. | código gerado |
| 6 | — | O sistema atualiza o painel "Última execução" com "Data/hora", "Escopo", "Duração", "Resultado: concluído" e "RPO observado", e reabilita o botão "Executar backup agora". | código gerado |
| 7 | O administrador clica em "Testar restauração". | O sistema executa a restauração do último conjunto de backup em ambiente isolado, compara os registros restaurados com os registros de origem e exibe o painel "Resultado do teste de restauração" com "Registros restaurados", "Divergências encontradas: 0" e "Resultado: bem-sucedido". | código gerado |
| 8 | O administrador clica em "Registrar teste". | O sistema grava o resultado do teste de restauração na trilha de auditoria, com usuário, data/hora, escopo e resultado, e exibe "Teste de restauração registrado". | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O administrador quer consultar o histórico de execuções. | O administrador clica em "Histórico de execuções". | O sistema exibe a lista de execuções com "Data/hora", "Escopo", "Duração", "Resultado" e "RPO observado", ordenada da mais recente para a mais antiga. | pronto |
| A2 | O administrador quer alterar o destino do backup. | O administrador edita o campo "Destino do backup" e clica em "Salvar configuração". | O sistema valida o acesso ao novo destino, persiste a alteração e exibe "Configuração de backup salva". | código gerado |
| A3 | O administrador quer alterar a retenção. | O administrador edita o campo "Retenção (dias)" e clica em "Salvar configuração". | O sistema persiste o novo prazo de retenção e exibe "Configuração de backup salva", respeitando a política de retenção de dados clínicos, de auditoria e de notificações. | código gerado |
| A4 | O administrador quer cancelar a edição da configuração. | O administrador clica em "Cancelar". | O sistema descarta as alterações não salvas e restaura os valores da configuração vigente, sem gravar nada na trilha de auditoria. | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O destino de backup está inacessível ou sem espaço. | O sistema interrompe a execução, exibe "Falha no backup: destino inacessível ou sem espaço disponível" e registra a falha na trilha de auditoria, sem marcar a execução como concluída. | código gerado |
| E2 | A execução do backup falha no meio do processo. | O sistema exibe "Falha no backup: execução interrompida em [etapa]" e mantém o último conjunto de backup válido íntegro, sem sobrescrevê-lo. | código gerado |
| E3 | O teste de restauração encontra divergências entre os registros restaurados e os de origem. | O sistema exibe "Teste de restauração com divergências: [quantidade] registros divergentes" e lista os registros afetados, sem declarar o teste como bem-sucedido. | código gerado |
| E4 | O administrador tenta executar backup sem token válido. | O servidor recusa a chamada, exibe "Sessão expirada — faça login novamente" e encerra a sessão, independentemente do que a tela enviou. | pronto |
| E5 | O RPO observado ultrapassa o RPO alvo configurado. | O sistema exibe "RPO observado acima do alvo configurado — verificar periodicidade do backup" e mantém o alerta visível no painel "Última execução". | código gerado |

#### UC-027: Monitorar Disponibilidade dos Serviços Externos

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O administrador entra com e-mail e senha e abre a tela "Monitoramento dos Serviços Externos". | O sistema valida o token de acesso e exibe a tela "Monitoramento dos Serviços Externos" com os três cards de serviço: "Laboratório", "Motor de risco de Cox" e "Serviço de e-mail". | pronto |
| 2 | — | O servidor executa o health check interno de cada serviço no intervalo configurado e atualiza, em cada card, o "Estado", o "Tempo de resposta" e o "Horário da última verificação". | código gerado |
| 3 | O administrador clica em "Verificar agora". | O sistema dispara imediatamente a verificação dos três serviços, exibe "Verificando..." em cada card e, ao concluir, atualiza "Estado", "Tempo de resposta" e "Horário da última verificação" de todos eles. | código gerado |
| 4 | — | Quando um serviço responde normalmente, o card exibe "Estado: disponível" e o sistema atualiza o indicador "Serviços disponíveis: 3 de 3" no topo da tela. | código gerado |
| 5 | O administrador clica em "Histórico de indisponibilidades". | O sistema exibe a lista de eventos com "Serviço", "Início da indisponibilidade", "Fim da indisponibilidade", "Duração" e "Alerta enviado à TI". | pronto |
| 6 | O administrador clica em "Configurar intervalo de verificação". | O sistema exibe o campo "Intervalo de verificação (segundos)" e o campo "Destinatário do alerta à TI", já preenchidos com a configuração vigente. | pronto |
| 7 | O administrador altera o campo "Intervalo de verificação (segundos)" para "60" e clica em "Salvar configuração". | O sistema persiste a configuração, exibe "Configuração de monitoramento salva" e grava na trilha de auditoria quem fez, o que fez, sobre qual registro e quando. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O serviço de e-mail não está configurado no servidor. | O administrador abre o card "Serviço de e-mail". | O sistema exibe "Estado: não configurado" e a mensagem "Envio de e-mail não configurado — a notificação não será dada por enviada", sem marcar nenhuma notificação como enviada. | código gerado |
| A2 | O administrador quer consultar apenas um serviço. | O administrador seleciona o filtro "Serviço: Laboratório" e clica em "Aplicar". | O sistema exibe somente o card "Laboratório", com "Estado", "Tempo de resposta", "Horário da última verificação" e o histórico de indisponibilidades daquele serviço. | pronto |
| A3 | O administrador quer testar o envio do alerta à TI. | O administrador clica em "Enviar alerta de teste". | O sistema aciona o serviço de e-mail, envia a mensagem de teste ao destinatário configurado e exibe "Alerta de teste enviado à TI" ou, em falha, "Falha no envio do alerta de teste". | código gerado |
| A4 | O administrador quer cancelar a edição da configuração. | O administrador clica em "Cancelar". | O sistema descarta as alterações não salvas e restaura os valores da configuração vigente, sem gravar nada na trilha de auditoria. | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O laboratório fica indisponível. | O card exibe "Estado: indisponível", o sistema envia alerta à TI, registra o evento na trilha de auditoria e passa a exibir, nas telas que dependem do laboratório, "Laboratório fora do ar — não foi possível buscar a hemocultura", sem mostrar resultado vazio como se fosse resultado normal. | código gerado |
| E2 | O motor de risco de Cox fica indisponível. | O card exibe "Estado: indisponível", o sistema envia alerta à TI e passa a exibir, nas telas de escore, "Serviço de escore não responde — nenhum escore foi gravado", sem gravar escore nenhum. | código gerado |
| E3 | O serviço de e-mail fica indisponível. | O card exibe "Estado: indisponível", o sistema envia alerta à TI e registra "Falha no envio da notificação — o sistema não finge que enviou", mantendo o status de falha visível. | código gerado |
| E4 | A verificação de um serviço excede o tempo limite. | O sistema marca o serviço como "Estado: indisponível por tempo limite excedido", registra a falha na trilha de auditoria e não apresenta tempo de resposta inventado. | código gerado |
| E5 | O administrador tenta abrir a tela sem token válido. | O servidor recusa a chamada, exibe "Sessão expirada — faça login novamente" e encerra a sessão, independentemente do que a tela enviou. | pronto |

#### UC-028: Registrar Erros com Correlação por Requisição

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O administrador acessa a tela **Painel de Diagnóstico de Erros** e seleciona o filtro de período em **Período da consulta** (7, 30, 90 ou 365 dias). | O sistema exibe a tela **Painel de Diagnóstico de Erros** com o campo **Período da consulta** preenchido e carrega a lista de erros estruturados do período, com as colunas **Identificador de correlação**, **Data/hora**, **Função de origem**, **Serviço envolvido** e **Mensagem de falha**. | pronto |
| 2 | O administrador clica em uma linha da lista de erros. | O sistema abre o painel lateral **Cadeia de execução da requisição** e exibe todos os eventos registrados com o mesmo **Identificador de correlação**, na ordem cronológica, mostrando em cada evento a **Função de origem**, o **Serviço envolvido** (tela, servidor, laboratório, motor de risco ou serviço de e-mail) e a **Mensagem de falha**. | pronto |
| 3 | O administrador pode opcionalmente: | | pronto |
| 3.1 | Clica no botão **Copiar identificador de correlação**. | O sistema copia o **Identificador de correlação** da requisição selecionada para a área de transferência e exibe a mensagem "Identificador de correlação copiado". | pronto |
| 3.2 | Altera o filtro **Serviço envolvido** para "serviço de e-mail". | O sistema recarrega a lista de erros exibindo somente os registros cujo **Serviço envolvido** é "serviço de e-mail", mantendo o **Período da consulta** selecionado. | pronto |
| 4 | O administrador clica em **Exportar lista de erros**. | O sistema gera o arquivo estruturado com os erros filtrados, incluindo o **Identificador de correlação** de cada um, e exibe a mensagem "Lista de erros exportada com 128 registros" e o botão **Baixar arquivo**. | código gerado |
| 5 | O administrador clica em **Baixar arquivo**. | O sistema disponibiliza o arquivo gerado para download e registra a ação na trilha de auditoria com o usuário administrador, a ação "exportar lista de erros", o período consultado e a data/hora. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O período selecionado não possui nenhum erro registrado. | O administrador mantém o filtro e observa a tela. | O sistema exibe na área da lista a mensagem "Nenhum erro registrado no período selecionado" e mantém o botão **Exportar lista de erros** desabilitado. | pronto |
| A2 | O administrador deseja investigar uma falha de integração específica com o laboratório. | O administrador altera o filtro **Serviço envolvido** para "laboratório". | O sistema recarrega a lista exibindo somente os erros cujo **Serviço envolvido** é "laboratório" e destaca em cada linha o **Identificador de correlação** para consulta cruzada. | pronto |
| A3 | O administrador identifica que o mesmo **Identificador de correlação** aparece em mais de uma função. | O administrador clica em cada linha com o mesmo identificador. | O sistema abre o painel **Cadeia de execução da requisição** e lista, em ordem cronológica, os eventos de todas as funções envolvidas, permitindo reconstruir a cadeia completa de execução. | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O armazenamento de logs estruturados está indisponível no momento da consulta. | O sistema exibe a mensagem "Não foi possível consultar os erros registrados: armazenamento de logs indisponível" e mantém o botão **Tentar novamente** na tela **Painel de Diagnóstico de Erros**. | código gerado |
| E2 | A exportação da lista de erros falha durante a geração do arquivo. | O sistema exibe a mensagem "Não foi possível exportar a lista de erros" e não disponibiliza o botão **Baixar arquivo**, registrando a própria falha com um novo **Identificador de correlação**. | código gerado |
| E3 | O token de acesso do administrador expira durante a consulta. | O sistema recusa a chamada, exibe a mensagem "Sessão expirada. Faça login novamente" e encerra a sessão, exigindo novo login. | pronto |

#### UC-029: Criptografar Dados de Paciente em Repouso

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O administrador acessa a tela **Painel de Segurança de Dados** e visualiza a seção **Criptografia em repouso**. | O sistema exibe a tela **Painel de Segurança de Dados** com a seção **Criptografia em repouso**, mostrando o **Status da criptografia do banco de dados**, o **Status da criptografia dos arquivos de configuração sensíveis** e a **Data da última verificação**. | pronto |
| 2 | O administrador clica em **Verificar criptografia em repouso**. | O sistema executa a verificação e exibe, para cada item, o resultado **Criptografado** ou **Não criptografado**, com a **Data da última verificação** atualizada. | código gerado |
| 3 | O servidor grava um novo dado de paciente (nome, data de nascimento, sexo, número do prontuário ou médico responsável) recebido de uma função do sistema. | O servidor aplica a criptografia em repouso antes da gravação no banco de dados e confirma a persistência do registro criptografado, sem expor o dado em texto aberto. | código gerado |
| 4 | O servidor grava uma credencial de serviço externo (laboratório, motor de risco ou serviço de e-mail) em arquivo de configuração sensível. | O servidor aplica a criptografia em repouso antes da gravação do arquivo de configuração sensível e confirma a persistência do valor criptografado, sem expor a credencial em código ou em tela. | código gerado |
| 5 | O administrador clica em **Exportar relatório de conformidade**. | O sistema gera o relatório com o **Status da criptografia do banco de dados**, o **Status da criptografia dos arquivos de configuração sensíveis** e a **Data da última verificação**, exibe a mensagem "Relatório de conformidade gerado" e disponibiliza o botão **Baixar arquivo**. | pronto |
| 6 | O administrador clica em **Baixar arquivo**. | O sistema disponibiliza o relatório para download e registra a ação na trilha de auditoria com o usuário administrador, a ação "exportar relatório de conformidade de criptografia" e a data/hora. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | A verificação aponta que um arquivo de configuração sensível está **Não criptografado**. | O administrador observa o resultado na tela. | O sistema destaca o item com o status **Não criptografado**, exibe a mensagem "Arquivo de configuração sensível sem criptografia em repouso" e mantém o botão **Verificar criptografia em repouso** disponível para nova verificação após a correção. | código gerado |
| A2 | O administrador deseja conferir apenas o banco de dados. | O administrador seleciona o filtro **Item verificado: banco de dados**. | O sistema executa a verificação somente do banco de dados e exibe apenas o **Status da criptografia do banco de dados** e a **Data da última verificação**. | código gerado |
| A3 | A chave de criptografia em repouso é rotacionada na configuração do servidor. | O administrador aciona a rotação conforme a política de segredos. | O servidor passa a usar a nova chave para novas gravações e mantém a leitura dos registros antigos, sem expor a chave em código, log ou tela. | código gerado |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | A chave de criptografia em repouso não está disponível na configuração do servidor. | O servidor recusa a gravação do dado de paciente, exibe a mensagem "Não foi possível gravar: chave de criptografia em repouso indisponível" e não persiste o registro em texto aberto. | código gerado |
| E2 | A verificação de criptografia falha por indisponibilidade do banco de dados. | O sistema exibe a mensagem "Não foi possível verificar a criptografia em repouso: banco de dados indisponível" e mantém o botão **Tentar novamente** na tela **Painel de Segurança de Dados**. | código gerado |
| E3 | O token de acesso do administrador expira durante a verificação. | O sistema recusa a chamada, exibe a mensagem "Sessão expirada. Faça login novamente" e encerra a sessão, exigindo novo login. | pronto |

#### UC-030: Aplicar Política de Retenção e Descarte de Dados

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O administrador acessa a tela **Gestão de Retenção e Descarte de Dados** e visualiza a seção **Política de retenção**. | O sistema exibe a tela **Gestão de Retenção e Descarte de Dados** com a seção **Política de retenção**, mostrando os prazos cadastrados para **Dados clínicos**, **Dados de auditoria** e **Notificações**, cada um com o **Prazo de guarda** e a **Data de referência do próximo descarte**. | pronto |
| 2 | O administrador clica em **Simular descarte**. | O sistema calcula, sem apagar nada, quantos registros de cada categoria seriam descartados e exibe a **Prévia do descarte** com a contagem por categoria: **Dados clínicos**, **Dados de auditoria** e **Notificações**. | código gerado |
| 3 | O administrador confere a **Prévia do descarte** e clica em **Executar descarte**. | O sistema exibe a confirmação "Confirma o descarte seguro dos registros listados na prévia? Esta ação não pode ser desfeita." com os botões **Confirmar descarte** e **Cancelar**. | pronto |
| 4 | O administrador clica em **Confirmar descarte**. | O sistema executa o descarte seguro dos registros cujo prazo de retenção venceu, em cada categoria, e exibe a mensagem "Descarte concluído: 214 registros descartados". | código gerado |
| 5 | O administrador clica em **Gerar relatório de descarte**. | O sistema gera o relatório com a **Data de execução**, a contagem por categoria descartada e o **Prazo de guarda** aplicado a cada uma, exibe a mensagem "Relatório de descarte gerado" e disponibiliza o botão **Baixar arquivo**. | código gerado |
| 6 | O auditor acessa a tela **Gestão de Retenção e Descarte de Dados** e consulta a seção **Relatórios de descarte**. | O sistema exibe ao auditor, em modo somente leitura, o histórico de execuções com **Data de execução**, **Responsável** e **Quantidade de registros descartados** por categoria. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | A **Prévia do descarte** mostra zero registros em uma categoria. | O administrador observa a prévia. | O sistema exibe, na categoria correspondente, a contagem zero e a mensagem "Nenhum registro vencido nesta categoria", mantendo a categoria fora do descarte. | código gerado |
| A2 | O administrador decide não executar o descarte após ver a prévia. | O administrador clica em **Cancelar** na confirmação. | O sistema fecha a confirmação e retorna à tela **Gestão de Retenção e Descarte de Dados** sem apagar nenhum registro e sem gerar relatório de descarte. | pronto |
| A3 | O administrador deseja alterar o **Prazo de guarda** de uma categoria antes do descarte. | O administrador edita o **Prazo de guarda** da categoria e clica em **Salvar política**. | O sistema persiste o novo **Prazo de guarda**, atualiza a **Data de referência do próximo descarte** e registra a alteração na trilha de auditoria. | código gerado |
| A4 | O auditor precisa comprovar a conformidade de um descarte passado. | O auditor seleciona uma execução na seção **Relatórios de descarte**. | O sistema exibe o relatório da execução selecionada, em modo somente leitura, com **Data de execução**, **Responsável** e **Quantidade de registros descartados** por categoria. | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O descarte falha no meio da execução por indisponibilidade do banco de dados. | O sistema interrompe o descarte, exibe a mensagem "Não foi possível concluir o descarte: banco de dados indisponível" e informa quantos registros foram descartados antes da falha, sem marcar a execução como concluída. | código gerado |
| E2 | A política de retenção não está cadastrada para uma das categorias. | O sistema exibe a mensagem "Política de retenção não cadastrada para a categoria Notificações" e não permite executar o descarte dessa categoria até que o **Prazo de guarda** seja definido. | código gerado |
| E3 | O token de acesso do administrador expira durante a execução do descarte. | O sistema recusa a chamada, exibe a mensagem "Sessão expirada. Faça login novamente" e encerra a sessão, sem executar o descarte. | pronto |
| E4 | O relatório de descarte não pode ser gerado. | O sistema exibe a mensagem "Não foi possível gerar o relatório de descarte" e não disponibiliza o botão **Baixar arquivo**, registrando a falha na trilha de auditoria. | código gerado |

#### UC-031: Gerenciar Segredos e Rotação de Credenciais

| Campo | Detalhe |
|---|---|
| **Natureza** | **convencional** |

#### Fluxo Principal
| # | Ação do Ator | Resposta do Sistema | Executado por |
|---|--------------|--------------------- |---|
| 1 | O administrador acessa a tela "Gestão de Segredos e Credenciais" pelo menu de administração. | O sistema exibe a tela "Gestão de Segredos e Credenciais" com a lista de serviços externos cadastrados (laboratório, motor de risco de Cox, serviço de e-mail), cada um mostrando o identificador da credencial, a origem ("Cofre de segredos"), a data da última rotação e o status da política de rotação ("Ativa"/"Inativa"). Nenhum valor de segredo é exibido — o campo de valor aparece como "•••••••• (armazenado no cofre)". | pronto |
| 2 | O administrador seleciona o serviço externo desejado na lista (por exemplo, "laboratório") e clica em "Rotacionar credencial". | O sistema abre o modal "Rotacionar credencial — laboratório", com o campo "Nova credencial" (entrada mascarada), o campo "Confirmar nova credencial", o seletor "Periodicidade de rotação" (30, 60 ou 90 dias) e os botões "Confirmar rotação" e "Cancelar". | pronto |
| 3 | O administrador digita a nova credencial no campo "Nova credencial" e repete no campo "Confirmar nova credencial". | O sistema mantém os caracteres mascarados e valida em tempo real se os dois campos coincidem, exibindo a mensagem "Credenciais conferem" abaixo do campo de confirmação. | pronto |
| 4 | O administrador escolhe a "Periodicidade de rotação" e clica em "Confirmar rotação". | O sistema grava a nova credencial diretamente no cofre de segredos, sem persistir o valor em banco de aplicação, log ou tela. O sistema atualiza a data da última rotação, registra a entrada de auditoria com usuário, ação ("Rotação de credencial"), serviço externo afetado e data/hora, e exibe a mensagem "Credencial do serviço laboratório rotacionada com sucesso. Próxima rotação automática em 60 dias." | código gerado |
| 5 | O administrador pode opcionalmente: | | pronto |
| 5.1 | Clica em "Ver política de rotação" na linha do serviço. | O sistema exibe o painel "Política de rotação — laboratório" com a periodicidade vigente, a data da última rotação, a data prevista da próxima rotação e o responsável pela última alteração. Nenhum valor de segredo é mostrado. | código gerado |
| 5.2 | Clica em "Testar conexão" na linha do serviço. | O sistema resolve a credencial no cofre e realiza uma chamada de verificação ao serviço externo, exibindo "Conexão com o laboratório bem-sucedida" ou, em caso de falha, a mensagem de erro correspondente, sem jamais exibir a credencial. | código gerado |
| 5.3 | Clica em "Cancelar" no modal de rotação. | O sistema fecha o modal "Rotacionar credencial — laboratório" e retorna à tela "Gestão de Segredos e Credenciais" sem alterar a credencial vigente. | pronto |
| 6 | O administrador encerra a operação fechando a tela. | O sistema mantém a credencial apenas no cofre de segredos e registra na trilha de auditoria o encerramento da sessão de administração de credenciais. | pronto |

#### Fluxos Alternativos
| ID | Condição | Ação do Ator | Resposta do Sistema | Executado por |
|----|----------|--------------|--------------------- |---|
| A1 | O administrador precisa cadastrar uma credencial para um serviço externo ainda não configurado. | O administrador clica em "Adicionar serviço externo", seleciona o tipo ("laboratório", "motor de risco de Cox" ou "serviço de e-mail"), informa o identificador da credencial e a nova credencial, e clica em "Salvar no cofre". | O sistema grava a credencial no cofre de segredos, cria o registro do serviço externo na lista com status "Política de rotação: Inativa" e exibe a mensagem "Serviço externo cadastrado no cofre de segredos. Defina a periodicidade de rotação." | código gerado |
| A2 | A rotação automática periódica é disparada pelo servidor ao vencer o prazo da política. | Nenhuma ação do ator — o servidor executa a rotação agendada. | O servidor solicita ao cofre de segredos a geração de nova credencial para o serviço externo, atualiza a data da última rotação, registra entrada de auditoria automática ("Rotação automática de credencial") e notifica o administrador por e-mail sobre a conclusão. | código gerado |
| A3 | O administrador deseja apenas consultar o histórico de rotações, sem alterar credencial. | O administrador clica em "Histórico de rotações" na linha do serviço externo. | O sistema exibe a lista de rotações com data/hora, tipo ("Manual"/"Automática"), responsável e resultado ("Sucesso"/"Falha"), sem exibir nenhum valor de credencial. | pronto |

#### Fluxos de Exceção
| ID | Erro/Problema | Resposta do Sistema | Executado por |
|----|--------------|--------------------- |---|
| E1 | O cofre de segredos está indisponível no momento da gravação. | O sistema exibe a mensagem "Não foi possível gravar no cofre de segredos. A credencial vigente foi mantida e nenhuma alteração foi aplicada." e oferece o botão "Tentar novamente". A tentativa falha é registrada na trilha de auditoria com status "Falha". | código gerado |
| E2 | Os campos "Nova credencial" e "Confirmar nova credencial" não coincidem. | O sistema bloqueia o botão "Confirmar rotação" e exibe a mensagem "As credenciais informadas não conferem. Verifique os dois campos." Nenhuma gravação é feita no cofre. | pronto |
| E3 | O serviço externo não responde ao teste de conexão com a nova credencial. | O sistema exibe a mensagem "Conexão com o laboratório não foi concluída. A credencial foi gravada no cofre, mas o serviço não respondeu. Verifique o serviço externo." e mantém a credencial gravada, registrando a falha na auditoria. | código gerado |
| E4 | O administrador tenta acessar a tela sem token de acesso válido. | O servidor recusa a chamada independentemente do que a tela enviou, exibe a mensagem "Sessão expirada. Faça login novamente." e encerra a sessão, exigindo novo login. | pronto |
