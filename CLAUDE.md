# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LangNet Interface is a React/TypeScript application for managing multi-agent systems with Petri nets. The system integrates with MCP (Model Context Protocol) services and provides interactive interfaces for agent design, task management, and system monitoring.

## Development Commands

```bash
# Start development server
npm start                 # Opens on http://localhost:3000

# Build for production
npm run build

# Run tests
npm test                  # Interactive test runner
npm test -- --watchAll=false   # Run all tests once

# Other
npm run eject            # Eject from Create React App (irreversible)
```

## Architecture Overview

### Core Structure
- **React 19** with **TypeScript** and **Create React App**
- **React Router 6.20.0** for navigation with nested routes
- **CSS Modules** for component-specific styling
- **Context API** for state management (NavigationContext)

### Key Architectural Patterns

#### Routing System
- **Dual-context navigation**: Global routes vs Project-specific routes
- **Dynamic route generation**: Project routes are prefixed with `/project/:projectId`
- **NavigationContext** manages project context switching and menu generation
- Routes in `src/App.tsx:38-162` support both global and project-scoped access

#### Component Organization
```
src/components/
├── layout/          # AppLayout, Header, Sidebar
├── agents/          # Agent management and chat interfaces  
├── code/            # Code generation and editing
├── deployment/      # Deployment configuration
├── documents/       # Document upload and analysis
├── monitoring/      # System monitoring and LangFuse integration
├── projects/        # Project management
├── settings/        # Application settings
├── specification/   # Functional specification generation
├── tasks/           # Task definition and management
└── yaml/            # YAML configuration management
```

#### State Management
- **NavigationContext** (`src/contexts/NavigationContext.tsx:22-286`) manages:
  - Project context switching
  - Dynamic menu generation based on context
  - Route path generation with project prefixes
- **Component-level state** with React hooks
- **Props drilling** for data flow between components

#### Type System
- Comprehensive TypeScript definitions in `src/types/index.ts` (1187 lines)
- Key domain types: `Project`, `Agent`, `Task`, `PetriNet`, `McpServer`, `Document`
- Status enums for state management: `ProjectStatus`, `AgentStatus`, `TaskStatus`
- Complex MCP (Model Context Protocol) type definitions for service integration

### Key Features

#### Multi-Agent System Management
- **Agent Designer**: Interactive agent creation and modification
- **Task Management**: Task definition with input/output specifications
- **Petri Net Editor**: Visual workflow definition (implementation pending)

#### MCP Integration
- **Global MCP Configuration**: Server discovery and connection management
- **Project-level MCP**: Service integration per project
- **Service Discovery**: Automatic detection and cataloging of available services

#### Interactive Interface System
- **Agent Chat**: Real-time communication with agents
- **AI Design Assistant**: Automated design suggestions
- **System State Monitoring**: Live system status and metrics

#### Document Processing
- **Document Upload**: Multi-format document ingestion
- **Requirements Extraction**: Automated analysis and requirement generation
- **Specification Generation**: Functional specification document creation

## Important Implementation Notes

### Navigation System
The navigation system uses a context-switching pattern:
- `enterProjectContext(projectId, projectName)` switches to project-specific routes
- `exitProjectContext()` returns to global navigation
- Menu items are dynamically generated based on current context
- Project routes are automatically prefixed: `/project/:projectId/...`

### MCP Service Integration
- MCP servers defined with comprehensive configuration (security, circuit breakers, credentials)
- Services support multiple categories: authentication, data_storage, ml_services, analytics, etc.
- Project-level service mappings enable selective service integration
- Connection status monitoring with health checks and performance metrics

### Code Generation System
- Multi-framework support (CrewAI, AutoGen, LangChain, Custom)
- Configurable LLM providers (OpenAI, Anthropic, Azure, Local)
- Memory system integration (Redis, PostgreSQL, In-Memory)
- Deployment target support (Docker, Kubernetes, Local, Cloud)

### Component Development Patterns
- Each major feature has dedicated page components in `src/pages/`
- Modal components for creation/editing workflows
- Card components for list/grid displays
- Form components with validation and state management
- CSS files co-located with components using descriptive class names

## Testing
- Uses `@testing-library/react` and `@testing-library/jest-dom`
- Test files should be co-located with components using `.test.tsx` extension
- Focus on user interactions and component behavior rather than implementation details

## Styling Guidelines
- CSS Modules for component isolation
- Responsive design with mobile-first approach
- Consistent color scheme and typography
- Dark/light theme structure prepared but not fully implemented

## Development Workflow
1. **Component Development**: Create page → add components → implement logic → add routing
2. **Feature Integration**: Update types → implement services → add UI components → update navigation
3. **MCP Integration**: Define service interfaces → implement connection logic → add UI controls
4. **Testing**: Write component tests → integration tests → manual testing across contexts
- database langnet