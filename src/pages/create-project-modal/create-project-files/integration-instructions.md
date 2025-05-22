# Instruções de Integração da Tela de Criação de Projeto

Este documento contém instruções para integrar a tela de criação de novo projeto ao código React existente do LangNet.

## Arquivos Fornecidos

1. `CreateProjectModal.tsx` - Componente principal do modal de criação de projeto
2. `CreateProjectModal.css` - Estilos para o modal
3. `ProjectCreationButton.tsx` - Componente de botão para abrir o modal

## Passos para Integração

### 1. Copie os arquivos para o projeto

Copie os três arquivos fornecidos para as seguintes pastas do seu projeto:

```
src/components/projects/CreateProjectModal.tsx
src/components/projects/CreateProjectModal.css
src/components/projects/ProjectCreationButton.tsx
```

### 2. Modifique o Dashboard.tsx

Abra o arquivo `src/pages/Dashboard.tsx` e faça as seguintes alterações:

1. Adicione os imports no topo do arquivo:

```tsx
import { useState } from 'react';
import CreateProjectModal from '../components/projects/CreateProjectModal';
import ProjectCreationButton from '../components/projects/ProjectCreationButton';
```

2. Adicione o estado para controlar a visibilidade do modal dentro do componente Dashboard:

```tsx
const Dashboard: React.FC = () => {
  // Estado existente...
  
  // Adicione este estado:
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  // Resto do código...
```

3. Adicione as funções para manipular o modal:

```tsx
const handleOpenModal = () => {
  setIsCreateModalOpen(true);
};

const handleCloseModal = () => {
  setIsCreateModalOpen(false);
};

const handleCreateProject = (projectData: any) => {
  console.log('Novo projeto:', projectData);
  // Aqui você implementaria a lógica para criar o projeto
  // Por exemplo, adicionar à lista de projetos recentes
  handleCloseModal();
};
```

4. Substitua o botão "Novo Projeto" existente pelo componente ProjectCreationButton:

Encontre o código que renderiza o botão "Novo Projeto" (provavelmente na seção dashboard-header):

```tsx
<button className="new-project-btn" onClick={handleNewProject}>
  + Novo Projeto
</button>
```

E substitua por:

```tsx
<ProjectCreationButton onOpenModal={handleOpenModal} />
```

5. Adicione o componente do modal no final do JSX, antes do fechamento da div principal:

```tsx
{/* Adicione o modal aqui, antes do fechamento da div principal */}
<CreateProjectModal 
  isOpen={isCreateModalOpen}
  onClose={handleCloseModal}
  onCreateProject={handleCreateProject}
/>
```

### 3. Ajuste a função handleNewProject (opcional)

Se você já tinha uma função `handleNewProject` no Dashboard, você pode:

1. Remover a função se ela não for mais necessária, ou
2. Modificá-la para chamar `handleOpenModal` se quiser manter comportamentos adicionais:

```tsx
const handleNewProject = () => {
  // Código existente que você quer manter...
  
  // Abrir o modal
  handleOpenModal();
};
```

## Exemplo de Fluxo de Uso

1. Usuário acessa o Dashboard
2. Clica no botão "+ Novo Projeto"
3. O modal de criação de projeto é exibido
4. Usuário preenche os campos e clica em "CREATE"
5. O projeto é criado e o modal é fechado

## Próximos Passos de Desenvolvimento

1. Implementar a lógica real de criação de projeto na função `handleCreateProject`
2. Adicionar validação de formulário
3. Conectar com backend para salvar os dados do projeto
4. Implementar navegação para a página de detalhes do projeto após a criação
