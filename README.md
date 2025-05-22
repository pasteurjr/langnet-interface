# Documentação do Projeto LangNet Interface

## Visão Geral

Este projeto implementa uma interface React para o sistema LangNet, conforme especificado nos documentos de requisitos e planejamento de interface. A interface permite a criação, gerenciamento e monitoramento de aplicações baseadas em agentes, com fluxos definidos através de redes de Petri.

## Estrutura do Projeto

O projeto foi estruturado seguindo as melhores práticas de desenvolvimento React, com uma arquitetura modular e escalável:

```
src/
├── assets/            # Imagens, ícones e recursos estáticos
├── components/        # Componentes reutilizáveis
│   ├── common/        # Componentes genéricos
│   ├── layout/        # Componentes de layout (header, sidebar, etc.)
│   ├── dashboard/     # Componentes específicos do dashboard
│   ├── projects/      # Componentes de gerenciamento de projetos
│   ├── documents/     # Componentes para análise de documentos
│   ├── agents/        # Componentes para definição de agentes
│   ├── petri/         # Componentes do editor de Redes de Petri
│   ├── code/          # Componentes para visualização e edição de código
│   └── monitoring/    # Componentes de monitoramento e analytics
├── pages/             # Páginas principais da aplicação
├── hooks/             # Custom hooks
├── services/          # Serviços e APIs
├── store/             # Configuração do Redux e slices
├── types/             # Definições de tipos TypeScript
├── utils/             # Funções utilitárias
└── App.tsx            # Componente raiz da aplicação
```

## Componentes Implementados

1. **Layout Base**
   - `AppLayout`: Container principal que gerencia o layout responsivo
   - `Sidebar`: Menu de navegação lateral com suporte a colapso
   - `Header`: Barra superior com título, busca, notificações e perfil

2. **Dashboard**
   - `Dashboard`: Página inicial com visão geral do sistema
   - `ProjectCard`: Card para exibição de projetos recentes
   - Métricas e atividades recentes

3. **Tipos e Interfaces**
   - Definições TypeScript para projetos, agentes, tarefas, redes de Petri, etc.
   - Interfaces para componentes UI e estado da aplicação

4. **Rotas**
   - Configuração de rotas para todas as páginas principais
   - Estrutura de navegação aninhada para projetos

## Tecnologias Utilizadas

- **React 18** com **TypeScript**
- **React Router** para navegação
- **CSS Modules** para estilização isolada
- Estrutura preparada para integração com **Redux Toolkit**

## Como Executar o Projeto

1. Certifique-se de ter Node.js (versão 16 ou superior) instalado
2. Navegue até o diretório do projeto: `cd langnet-app`
3. Instale as dependências: `npm install`
4. Inicie o servidor de desenvolvimento: `npm start`
5. Acesse a aplicação em: `http://localhost:3000`

## Próximos Passos Recomendados

1. **Implementação de Estado Global**
   - Configurar Redux Toolkit para gerenciamento de estado
   - Criar slices para projetos, agentes, tarefas, etc.

2. **Integração com Backend**
   - Implementar serviços API para comunicação com o backend
   - Adicionar autenticação e autorização

3. **Editor de Redes de Petri**
   - Implementar o editor visual usando React Flow ou D3.js
   - Adicionar funcionalidades de simulação e validação

4. **Componentes Específicos**
   - Desenvolver componentes para cada módulo funcional
   - Implementar formulários para criação e edição de agentes e tarefas

5. **Testes**
   - Adicionar testes unitários com Jest e React Testing Library
   - Implementar testes de integração para fluxos principais

## Considerações de Design

- A interface segue um design moderno e responsivo
- Layout adaptável para diferentes tamanhos de tela
- Suporte a temas claro e escuro (estrutura preparada)
- Componentes modulares e reutilizáveis

## Limitações Atuais

- Implementação atual é focada na estrutura e navegação básica
- Dados são mockados para demonstração
- Funcionalidades avançadas como o editor de Petri precisam ser implementadas
- Integração com backend ainda não está configurada

## Conclusão

Este projeto fornece uma base sólida para o desenvolvimento da interface do sistema LangNet, seguindo as especificações dos documentos de requisitos e planejamento. A arquitetura modular e escalável permite a expansão gradual das funcionalidades, mantendo a qualidade e a manutenibilidade do código.
