"""
LangNet Agents Implementation
Based on tropicalagentssalesv6.py Context State List pattern

This module implements the complete multi-agent system for LangNet:
- Document analysis and requirements extraction
- Agent and task design
- Workflow modeling with Petri Nets
- YAML and code generation

Pattern: Context State List + Task Registry + Input/Output Functions
"""
import os
import sys
import json
from json import JSONDecoder
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

# Add framework to path
framework_path = Path(__file__).parent.parent.parent / "framework"
sys.path.insert(0, str(framework_path))

# Import framework components
from frameworkagentsadapterv4 import FrameworkAdapterFactory
from langchain_openai import ChatOpenAI

# Import LangNet components
from .langnetstate import (
    LangNetFullState,
    init_full_state,
    log_task_start,
    log_task_complete,
    log_task_error
)
from .langnettools import create_langnet_tools


# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


# Load agent and task configurations
CONFIG_DIR = Path(__file__).parent.parent / "config"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
AGENTS_CONFIG = load_yaml_config(CONFIG_DIR / "langnet_agents.yaml")
TASKS_CONFIG = load_yaml_config(CONFIG_DIR / "langnet_tasks.yaml")


def load_template(template_name: str) -> str:
    """Load a Markdown template from templates directory"""
    template_path = TEMPLATES_DIR / template_name
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


# ============================================================================
# FRAMEWORK SETUP
# ============================================================================

# Get framework adapters (using v4 with LangGraph support)
adapters = FrameworkAdapterFactory.get_framework_adapters(version="crewai")
AgentClass = adapters["agent"]
TaskClass = adapters["task"]
TeamClass = adapters["team"]
ToolClass = adapters["tool"]
ProcessClass = adapters["process"]
ProcessType = adapters["processtype"]

# LLM instances (lazy initialization)
_llm_cache = {}

def get_llm(use_deepseek: bool = False):
    """
    Get LLM instance based on configuration (with caching)

    Args:
        use_deepseek: If True, returns DeepSeek LLM; if False, checks LLM_PROVIDER env var

    Returns:
        LLM instance
    """
    # Check LLM_PROVIDER environment variable
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

    # Override with use_deepseek parameter
    if use_deepseek:
        llm_provider = "deepseek"

    cache_key = llm_provider

    if cache_key not in _llm_cache:
        if llm_provider == "claude_code":
            # Claude Code via local API using CrewAI's LLM class
            from crewai import LLM

            claude_api_base = os.getenv("CLAUDE_CODE_API_BASE", "http://localhost:8807")
            print(f"[LangNet] Using Claude Code API at {claude_api_base}/v1")

            _llm_cache[cache_key] = LLM(
                model="openai/claude-code",  # Use openai/ prefix for LiteLLM compatibility
                base_url=f"{claude_api_base}/v1",
                api_key="dummy",  # Required by CrewAI but not validated
                temperature=0.3,
                max_tokens=16384
            )

        elif llm_provider == "lmstudio":
            # LM Studio local — API OpenAI-compatible, zero custo por token.
            # Modelo típico: deepseek-r1-distill-qwen-32b (context 40k+).
            # Timeout ALTO (60 min) — modelo local 32B pode demorar em outputs longos.
            from crewai import LLM as CrewLLM
            lm_base = os.getenv("LMSTUDIO_API_BASE", "http://192.168.1.115:1234/v1")
            lm_model = os.getenv("LMSTUDIO_MODEL_NAME", "openai/deepseek-r1-distill-qwen-32b")
            # CrewAI/LiteLLM exige provider prefix "openai/" para APIs OpenAI-compatible.
            # O app/llm.py (OpenAI SDK direto) rejeita esse prefix, então mantemos o
            # .env sem prefix e adicionamos aqui só para o CrewAI LLM.
            if lm_model and not lm_model.startswith("openai/") and "/" not in lm_model:
                lm_model = f"openai/{lm_model}"
            print(f"[LangNet] Using LM Studio at {lm_base} — model={lm_model}")
            _llm_cache[cache_key] = CrewLLM(
                model=lm_model,
                api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
                base_url=lm_base,
                temperature=0.3,
                max_tokens=int(os.getenv("LMSTUDIO_MAX_TOKENS", "16000")),
                timeout=int(os.getenv("LMSTUDIO_TIMEOUT", "3600")),  # 60 min padrão
            )

        elif llm_provider == "deepseek":
            # DeepSeek configuration
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

            # CrewAI LLM via litellm (necessário pq Agents internamente chamam litellm —
            # se passarmos langchain ChatOpenAI, CrewAI extrai o model field e cai em
            # litellm sem provider). LLM da CrewAI exige prefix "deepseek/" e ele mesmo
            # strippa antes de chamar a API.
            from crewai import LLM as CrewLLM

            deepseek_model = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash")
            if not deepseek_model.startswith("deepseek/"):
                deepseek_model = f"deepseek/{deepseek_model}"

            max_tokens_value = int(os.getenv("DEEPSEEK_MAX_TOKENS", "32768"))
            reasoning_enabled = (os.getenv("DEEPSEEK_REASONING", "false").lower() == "true")

            _llm_cache[cache_key] = CrewLLM(
                model=deepseek_model,
                api_key=deepseek_api_key,
                base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
                temperature=0.3,
                max_tokens=max_tokens_value,
                extra_body={"reasoning": {"enabled": reasoning_enabled}},
            )
        else:
            # Default OpenAI
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")

            _llm_cache[cache_key] = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                openai_api_key=openai_api_key,
                temperature=0.3,
                max_tokens=16384
            )

    return _llm_cache[cache_key]

# Default LLM instance (for backward compatibility)
llm = None  # Will be initialized on first use

# Create custom tools
LANGNET_TOOLS = create_langnet_tools()


# ============================================================================
# AGENT CREATION FUNCTIONS (WITH MEMORY SUPPORT)
# ============================================================================

def create_document_analyst_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Document Analyst agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "document_analyst_agent",
        "config": AGENTS_CONFIG['document_analyst_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_requirements_engineer_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Requirements Engineer agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "requirements_engineer_agent",
        "config": AGENTS_CONFIG['requirements_engineer_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_requirements_validator_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Requirements Validator agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "requirements_validator_agent",
        "config": AGENTS_CONFIG['requirements_validator_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_generator_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Generator agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "specification_generator_agent",
        "config": AGENTS_CONFIG['specification_generator_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_agent_specifier_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Agent Specifier agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "agent_specifier_agent",
        "config": AGENTS_CONFIG['agent_specifier_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_task_decomposer_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Task Decomposer agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "task_decomposer_agent",
        "config": AGENTS_CONFIG['task_decomposer_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_petri_net_designer_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Petri Net Designer agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "petri_net_designer_agent",
        "config": AGENTS_CONFIG['petri_net_designer_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_yaml_generator_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create YAML Generator agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "yaml_generator_agent",
        "config": AGENTS_CONFIG['yaml_generator_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_code_generator_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Code Generator agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "code_generator_agent",
        "config": AGENTS_CONFIG['code_generator_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_web_researcher_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Web Researcher agent with optional memory and custom LLM"""
    # Note: Tools will be added separately in TASK_REGISTRY
    agent_kwargs = {
        "name": "web_researcher_agent",
        "config": AGENTS_CONFIG['web_researcher_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


# =============================================================================
# SPECIFICATION GENERATION AGENTS (Multi-Step Pipeline)
# Based on Generative Computing principles - IBM Research
# =============================================================================

def create_specification_router_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Router agent for intent classification"""
    agent_kwargs = {
        "name": "specification_router_agent",
        "config": AGENTS_CONFIG['specification_router_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_entity_extractor_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Entity Extractor agent"""
    agent_kwargs = {
        "name": "specification_entity_extractor_agent",
        "config": AGENTS_CONFIG['specification_entity_extractor_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_composer_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Composer agent"""
    agent_kwargs = {
        "name": "specification_composer_agent",
        "config": AGENTS_CONFIG['specification_composer_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_verifier_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Verifier agent for grounding validation"""
    agent_kwargs = {
        "name": "specification_verifier_agent",
        "config": AGENTS_CONFIG['specification_verifier_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_compliance_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Compliance agent"""
    agent_kwargs = {
        "name": "specification_compliance_agent",
        "config": AGENTS_CONFIG['specification_compliance_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_formatter_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Formatter agent with fallback support"""
    agent_kwargs = {
        "name": "specification_formatter_agent",
        "config": AGENTS_CONFIG['specification_formatter_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_web_researcher_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Web Researcher agent for external knowledge enrichment"""
    agent_kwargs = {
        "name": "specification_web_researcher_agent",
        "config": AGENTS_CONFIG['specification_web_researcher_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


# Agents cache (lazy initialization)
_agents_cache = {}

def get_agent(agent_name: str, use_deepseek: bool = False):
    """
    Get agent instance with lazy initialization

    Args:
        agent_name: Name of the agent
        use_deepseek: If True, uses DeepSeek LLM

    Returns:
        Agent instance
    """
    cache_key = f"{agent_name}_{'deepseek' if use_deepseek else 'openai'}"

    if cache_key not in _agents_cache:
        llm_instance = get_llm(use_deepseek) if use_deepseek else None

        agent_creators = {
            "document_analyst": create_document_analyst_agent,
            "requirements_engineer": create_requirements_engineer_agent,
            "requirements_validator": create_requirements_validator_agent,
            "specification_generator": create_specification_generator_agent,
            "agent_specifier": create_agent_specifier_agent,
            "task_decomposer": create_task_decomposer_agent,
            "petri_net_designer": create_petri_net_designer_agent,
            "yaml_generator": create_yaml_generator_agent,
            "code_generator": create_code_generator_agent,
            "web_researcher": create_web_researcher_agent,
            # Specification multi-step pipeline agents
            "specification_router": create_specification_router_agent,
            "specification_entity_extractor": create_specification_entity_extractor_agent,
            "specification_web_researcher": create_specification_web_researcher_agent,
            "specification_composer": create_specification_composer_agent,
            "specification_verifier": create_specification_verifier_agent,
            "specification_compliance": create_specification_compliance_agent,
            "specification_formatter": create_specification_formatter_agent
        }

        if agent_name not in agent_creators:
            raise ValueError(f"Unknown agent: {agent_name}")

        _agents_cache[cache_key] = agent_creators[agent_name](llm_instance=llm_instance)

    return _agents_cache[cache_key]

# Initialize all agents (for backward compatibility - lazy loaded)
AGENTS = {
    "document_analyst": None,  # Loaded on first use
    "requirements_engineer": None,
    "requirements_validator": None,
    "specification_generator": None,
    "agent_specifier": None,
    "task_decomposer": None,
    "petri_net_designer": None,
    "yaml_generator": None,
    "code_generator": None,
    "web_researcher": None,
    # Specification multi-step pipeline agents
    "specification_router": None,
    "specification_entity_extractor": None,
    "specification_web_researcher": None,
    "specification_composer": None,
    "specification_verifier": None,
    "specification_compliance": None,
    "specification_formatter": None
}


# ============================================================================
# INPUT FUNCTIONS (Extract data from context state for each task)
# ============================================================================

def analyze_document_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for analyze_document task"""
    print(f"\n{'='*80}")
    print(f"[PHASE 3] analyze_document_input_func() called")
    print(f"[PHASE 3] state['document_content'] length: {len(state.get('document_content', ''))} chars")
    print(f"[PHASE 3] state['additional_instructions'] length: {len(state.get('additional_instructions', ''))} chars")
    print(f"{'='*80}\n")

    task_input = {
        "document_path": state.get("document_path", ""),
        "document_type": state.get("document_type", ""),
        "document_content": state.get("document_content", ""),  # Pre-extracted chunked content
        "additional_instructions": state.get("additional_instructions", ""),
        "project_name": state.get("project_name", ""),
        "project_description": state.get("project_description", "")
    }

    print(f"\n{'='*80}")
    print(f"[PHASE 3] analyze_document_input_func() RETURNED")
    print(f"[PHASE 3] task_input['document_content'] length: {len(task_input.get('document_content', ''))} chars")
    print(f"[PHASE 3] task_input['document_content'] preview (first 300 chars):")
    print(f"{task_input.get('document_content', '(EMPTY!)')[:300]}")
    print(f"{'='*80}\n")

    return task_input


def extract_requirements_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for extract_requirements task"""
    print(f"\n{'='*80}")
    print(f"[PHASE 3] extract_requirements_input_func() called")
    print(f"[PHASE 3] state['document_content'] length: {len(state.get('document_content', ''))} chars")
    print(f"[PHASE 3] state['additional_instructions'] length: {len(state.get('additional_instructions', ''))} chars")
    print(f"{'='*80}\n")

    task_input = {
        "document_content": state.get("document_content", ""),
        "additional_instructions": state.get("additional_instructions", ""),
        "project_name": state.get("project_name", ""),
        "project_description": state.get("project_description", ""),
        "analysis_json": state.get("document_analysis_json", "{}")  # BUG FIX: Add analysis from task 1
    }

    print(f"\n{'='*80}")
    print(f"[PHASE 3] extract_requirements_input_func() RETURNED")
    print(f"[PHASE 3] task_input['document_content'] length: {len(task_input.get('document_content', ''))} chars")
    print(f"[PHASE 3] task_input['document_content'] preview (first 300 chars):")
    print(f"{task_input.get('document_content', '(EMPTY!)')[:300]}")
    print(f"{'='*80}\n")

    return task_input


def research_additional_info_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for research_additional_info task"""
    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "document_content": state.get("document_content", ""),  # BUG FIX: Add document content for context
        "additional_instructions": state.get("additional_instructions", ""),
        "project_name": state.get("project_name", "")
    }


def validate_requirements_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for validate_requirements task - includes template"""
    from datetime import datetime

    # Load the Requirements Document template
    template = load_template("requirements_document_template.md")

    # Provide ALL template variables with defaults to avoid interpolation errors
    # The LLM will fill in the actual values based on the requirements and research
    default_placeholder = "To be filled by analysis"
    template_vars = {
        # Project info
        "project_name": state.get("project_name", ""),
        "project_description": state.get("project_description", ""),
        "project_objectives": state.get("additional_instructions", "")[:200] if state.get("additional_instructions") else default_placeholder,
        "project_context": "See additional instructions for context",
        "project_domain": state.get("project_domain", ""),
        "scope_includes": default_placeholder,
        "scope_excludes": default_placeholder,

        # Document metadata
        "document_id": state.get("document_id", ""),
        "document_path": state.get("document_path", ""),
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "document_status": "Draft",
        "documents_table": default_placeholder,
        "total_documents": "1",
        "total_pages": "N/A",
        "total_words": str(len(state.get("document_content", "").split())),
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "processing_time": "N/A",
        "total_processing_time": "N/A",

        # Requirements sections
        "functional_requirements_by_category": default_placeholder,
        "functional_requirements_list": default_placeholder,
        "non_functional_requirements_list": default_placeholder,
        "business_rules_by_domain": default_placeholder,
        "business_rules_list": default_placeholder,
        "actors_list": default_placeholder,
        "entities_description": default_placeholder,
        "workflows_overview": default_placeholder,
        "workflows_detailed": default_placeholder,
        "glossary_table": default_placeholder,
        "glossary_entries": default_placeholder,

        # NFR categories
        "nfr_performance": default_placeholder,
        "nfr_security": default_placeholder,
        "nfr_usability": default_placeholder,
        "nfr_reliability": default_placeholder,
        "nfr_scalability": default_placeholder,
        "nfr_maintainability": default_placeholder,

        # Quality analysis
        "consistency_analysis": default_placeholder,
        "conflicts_table": default_placeholder,
        "conflicts_entries": default_placeholder,
        "ambiguities_analysis": default_placeholder,
        "ambiguities_list": default_placeholder,
        "ambiguous_text": default_placeholder,
        "clarification_questions": default_placeholder,
        "high_priority_questions": default_placeholder,
        "medium_priority_questions": default_placeholder,
        "low_priority_questions": default_placeholder,

        # Completeness scores
        "completeness_score": "N/A",
        "fr_completeness": "N/A",
        "nfr_completeness": "N/A",
        "br_completeness": "N/A",
        "actors_completeness": "N/A",
        "entities_completeness": "N/A",
        "workflows_completeness": "N/A",

        # Quality scores
        "clarity_score": "N/A",
        "clarity_status": "N/A",
        "clarity_notes": "N/A",
        "consistency_score": "N/A",
        "consistency_status": "N/A",
        "consistency_notes": "N/A",
        "testability_score": "N/A",
        "testability_status": "N/A",
        "testability_notes": "N/A",
        "traceability_score": "N/A",
        "traceability_status": "N/A",
        "traceability_notes": "N/A",
        "completeness_status": "N/A",
        "completeness_notes": "N/A",

        # Gaps and issues
        "critical_gaps": default_placeholder,
        "information_requests": default_placeholder,
        "information_requests_list": default_placeholder,
        "essential_coverage_analysis": default_placeholder,
        "essential_coverage_table": default_placeholder,
        "application_type": "Web Application",
        "issues_summary": default_placeholder,
        "issues_detailed_list": default_placeholder,
        "critical_issues_count": "0",
        "high_issues_count": "0",
        "medium_issues_count": "0",
        "low_issues_count": "0",
        "severity": "N/A",

        # Diagrams and visualizations
        "entity_relationship_diagram": default_placeholder,
        "entity_attributes_table": default_placeholder,
        "workflow_sequence_diagram": default_placeholder,
        "prioritization_chart_data": default_placeholder,
        "dependencies_graph": default_placeholder,
        "critical_path_analysis": default_placeholder,
        "critical_requirements_list": default_placeholder,
        "coverage_mindmap": default_placeholder,
        "traceability_matrix": default_placeholder,

        # Web research
        "industry_best_practices": default_placeholder,
        "recommended_standards": default_placeholder,
        "suggested_technologies": default_placeholder,
        "compliance_checklist": default_placeholder,
        "compliance_entries": default_placeholder,
        "missing_requirements_discovered": default_placeholder,

        # Improvements
        "general_recommendations": default_placeholder,
        "fr_improvements": default_placeholder,
        "nfr_improvements": default_placeholder,
        "br_improvements": default_placeholder,
        "documentation_improvements": default_placeholder,

        # Next steps
        "immediate_actions": default_placeholder,
        "validations_needed": default_placeholder,
        "spec_preparation": default_placeholder,

        # System metadata
        "framework_version": "LangNet v1.0",
        "llm_provider": "OpenAI",
        "llm_model": "GPT-4",
        "web_research_enabled": "Yes",
        "has_additional_instructions": "Yes" if state.get("additional_instructions") else "No",
        "version_history": "N/A",

        # Other
        "abbreviations_table": default_placeholder
    }

    # ========== FIX: Format template with actual values BEFORE sending to LLM ==========
    # This ensures dates are correct and not invented by the LLM
    try:
        formatted_template = template.format(**template_vars)
        print(f"[TEMPLATE] ✅ Template formatado com {len(template_vars)} variáveis")
        print(f"[TEMPLATE] 📅 Data de geração: {template_vars['generation_date']}")
        print(f"[TEMPLATE] 📅 Data da análise: {template_vars['analysis_date']}")
    except KeyError as e:
        print(f"[TEMPLATE] ⚠️ Erro ao formatar template: {e}")
        formatted_template = template  # Fallback to unformatted

    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "research_findings_json": state.get("research_findings_json", "{}"),
        "document_content": state.get("document_content", ""),  # BUG FIX: Add document content for LLM context
        "additional_instructions": state.get("additional_instructions", ""),  # BUG FIX: Add instructions for LLM context
        "template": formatted_template,  # ← Template já formatado com datas corretas
        **template_vars  # Spread all template variables
    }


def generate_specification_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for generate_specification task"""
    validation_data = state.get("validation_data", {})
    return {
        "validated_requirements": json.dumps(validation_data.get("valid_requirements", []))
    }


def suggest_agents_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for suggest_agents task"""
    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "specification_data": json.dumps(state.get("specification_data", {}))
    }


def decompose_tasks_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for decompose_tasks task"""
    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "agents_json": json.dumps(state.get("agents_data", []))
    }


def design_petri_net_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for design_petri_net task"""
    return {
        "tasks_json": json.dumps(state.get("tasks_data", [])),
        "dependencies": json.dumps(state.get("dependencies", {})),
        "agents_json": json.dumps(state.get("agents_data", []))
    }


def generate_yaml_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for generate_yaml_files task"""
    return {
        "agents_json": json.dumps(state.get("agents_data", [])),
        "tasks_json": json.dumps(state.get("tasks_data", []))
    }


def generate_code_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for generate_python_code task.

    The task now produces only tools.py + adapters.py (LLM-heavy parts).
    The rest of the project (main.py, websocket_server.py, requirements, docker,
    petri_net.json with real logica) is built deterministically in the
    output_func by ``_build_project_templates``.
    """
    petri = state.get("petri_net_data") or {}
    return {
        "agents_yaml": state.get("agents_yaml", ""),
        "tasks_yaml": state.get("tasks_yaml", ""),
        "petri_net_json": json.dumps(petri, ensure_ascii=False) if petri else "{}",
    }


# =============================================================================
# SPECIFICATION PIPELINE INPUT FUNCTIONS
# =============================================================================

def classify_specification_intent_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for classify_specification_intent task (Router)"""
    return {
        "requirements_document": state.get("requirements_document", ""),
        "requirements_version": state.get("requirements_version", 1),
        "project_name": state.get("project_name", "Sistema"),
        "detail_level": state.get("spec_detail_level", "detailed"),
        "target_audience": state.get("spec_target_audience", "mixed")
    }


def extract_specification_entities_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for extract_specification_entities task (EntityExtractor)"""
    return {
        "requirements_document": state.get("requirements_document", ""),
        "classification_json": state.get("spec_classification_json", "{}"),
        "project_name": state.get("project_name", "Sistema")
    }


def compose_spec_use_cases_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for compose_spec_use_cases task - generates only section 5 (Use Cases)"""
    return {
        "entities_json": state.get("spec_entities_json", "{}"),
        "requirements_document": state.get("requirements_document", ""),
        "project_name": state.get("project_name", "Sistema"),
        "wireframe_format": state.get("wireframe_format", "ascii"),
    }


def compose_spec_document_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for compose_spec_document task - generates sections 1-4 and 6-14"""
    return {
        "entities_json": state.get("spec_entities_json", "{}"),
        "research_context_json": state.get("spec_research_context_json", "{}"),
        "use_cases_json": state.get("spec_use_cases_json", "{}"),
        "project_name": state.get("project_name", "Sistema"),
        "requirements_version": state.get("requirements_version", 1),
        "requirements_created_at": state.get("requirements_created_at", datetime.now().strftime("%Y-%m-%d")),
        "detail_level": state.get("spec_detail_level", "detailed"),
        "target_audience": state.get("spec_target_audience", "mixed")
    }


def verify_specification_grounding_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for verify_specification_grounding task (Verifier)"""
    return {
        "draft_sections_json": state.get("spec_draft_sections_json", "{}"),
        "entities_json": state.get("spec_entities_json", "{}"),
        "requirements_document": state.get("requirements_document", "")
    }


def validate_specification_compliance_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for validate_specification_compliance task (Compliance)"""
    return {
        "draft_sections_json": state.get("spec_draft_sections_json", "{}"),
        "verification_results_json": state.get("spec_verification_json", "{}"),
        "target_audience": state.get("spec_target_audience", "mixed")
    }


def apply_spec_corrections_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for apply_spec_corrections task - applies verification and compliance corrections"""
    return {
        "draft_sections_json": state.get("spec_draft_sections_json", "{}"),
        "verification_results_json": state.get("spec_verification_json", "{}"),
        "compliance_results_json": state.get("spec_compliance_json", "{}")
    }


def render_final_specification_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for render_final_specification task - renders final Markdown document"""
    return {
        "corrected_sections_json": state.get("spec_corrected_sections_json", "{}"),
        "project_name": state.get("project_name", "Sistema"),
        "requirements_version": state.get("requirements_version", 1),
        "requirements_created_at": state.get("requirements_created_at", datetime.now().strftime("%Y-%m-%d"))
    }


# ============================================================================
# OUTPUT FUNCTIONS (Update context state with task results)
# ============================================================================

def analyze_document_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with analyze_document results"""
    # Parse result
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {"error": "Failed to parse JSON", "raw": output_json}

    # Update state
    # IMPORTANTE: NÃO sobrescrever document_content (precisa ser preservado para próximas tasks)
    updated_state = {
        **state,
        "document_analysis_json": output_json,
        # "document_content": parsed.get("content", ""),  # REMOVIDO: mantém original intacto
        "document_structure": parsed.get("structure", {}),
        "document_metadata": parsed.get("metadata", {})
    }

    return log_task_complete(updated_state, "analyze_document", output_json[:200])


def extract_requirements_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with extract_requirements results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "requirements_json": output_json,
        "requirements_data": parsed
    }

    return log_task_complete(updated_state, "extract_requirements", output_json[:200])


def research_additional_info_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with research_additional_info results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "research_findings_json": output_json,
        "research_findings_data": parsed
    }

    return log_task_complete(updated_state, "research_additional_info", output_json[:200])


def validate_requirements_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with validate_requirements results and extract requirements document"""
    print(f"\n{'='*80}")
    print(f"[DEBUG] validate_requirements_output_func - Processing result")
    print(f"[DEBUG] Result type: {type(result)}")

    # CrewAI returns CrewOutput object (pydantic model), not a dict
    # Must extract content properly using .raw, .json_dict, or .model_dump()
    if hasattr(result, 'raw'):
        # CrewOutput object - get raw string output
        output_json = result.raw
        print(f"[DEBUG] Extracted from CrewOutput.raw")
    elif hasattr(result, 'json_dict') and result.json_dict:
        # CrewOutput with pre-parsed JSON dictionary
        output_json = json.dumps(result.json_dict)
        print(f"[DEBUG] Extracted from CrewOutput.json_dict")
    elif hasattr(result, 'model_dump'):
        # Pydantic model - convert to dict then JSON
        output_json = json.dumps(result.model_dump())
        print(f"[DEBUG] Extracted from CrewOutput.model_dump()")
    elif isinstance(result, dict):
        # Already a dict (shouldn't happen with CrewAI but keep as fallback)
        output_json = json.dumps(result)
        print(f"[DEBUG] Result is already a dict")
    else:
        # Last resort - string conversion (likely won't work correctly)
        output_json = str(result)
        print(f"[DEBUG] WARNING: Using str() fallback - may not work correctly")

    print(f"[DEBUG] output_json type: {type(output_json)}")
    print(f"[DEBUG] output_json length: {len(output_json)}")
    print(f"[DEBUG] output_json preview: {output_json[:500]}")

    try:
        parsed = json.loads(output_json)
        print(f"[DEBUG] JSON parsing SUCCESS")
        print(f"[DEBUG] Parsed keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'NOT A DICT'}")
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON parsing FAILED: {e}")
        parsed = {}

    # Extract the requirements document MD from the validation output
    requirements_doc_md = ""

    # CRUCIAL FIX: CrewAI wraps the response in "team_result" with markdown code blocks
    if isinstance(parsed, dict) and "team_result" in parsed:
        print(f"[DEBUG] Found 'team_result' key, extracting nested JSON...")
        team_result_str = parsed["team_result"]

        # Remove markdown code blocks (```json and ```)
        if isinstance(team_result_str, str):
            # Remove ```json at start and ``` at end
            team_result_str = team_result_str.strip()
            if team_result_str.startswith("```json"):
                team_result_str = team_result_str[7:]  # Remove ```json
            elif team_result_str.startswith("```"):
                team_result_str = team_result_str[3:]  # Remove ```
            if team_result_str.endswith("```"):
                team_result_str = team_result_str[:-3]  # Remove trailing ```
            team_result_str = team_result_str.strip()

            print(f"[DEBUG] After removing markdown, length: {len(team_result_str)}")

            # Detect if using Claude Code (check provider from config or state)
            is_claude_code = False
            try:
                # Try to detect from environment or config
                import os
                from app.config import settings
                is_claude_code = settings.llm_provider.lower() == "claude_code"
                print(f"[DEBUG] Detected LLM provider: {settings.llm_provider}")
            except:
                # Fallback: assume Claude if team_result exists
                is_claude_code = True
                print(f"[DEBUG] Could not detect provider, assuming Claude-like behavior")

            # Parse the NESTED JSON - use different strategy for Claude vs GPT
            try:
                if is_claude_code:
                    # CLAUDE CODE: Use raw_decode to handle extra text after JSON
                    print(f"[DEBUG] Using raw_decode for Claude Code (handles extra text)")
                    decoder = JSONDecoder()
                    nested_parsed, json_end_index = decoder.raw_decode(team_result_str)

                    print(f"[DEBUG] Nested JSON parsing SUCCESS via raw_decode")
                    print(f"[DEBUG] JSON ends at index {json_end_index} of {len(team_result_str)}")
                    print(f"[DEBUG] Nested keys: {list(nested_parsed.keys()) if isinstance(nested_parsed, dict) else 'NOT A DICT'}")

                    # Extra text after JSON is ignored automatically by raw_decode
                    if json_end_index < len(team_result_str):
                        extra_text_preview = team_result_str[json_end_index:json_end_index+100].strip()
                        print(f"[DEBUG] Extra text found after JSON (ignored): {extra_text_preview[:50]}...")
                else:
                    # GPT-4o-mini and others: Use standard json.loads (expects pure JSON)
                    print(f"[DEBUG] Using json.loads for standard LLM (expects pure JSON)")
                    nested_parsed = json.loads(team_result_str)
                    print(f"[DEBUG] Nested JSON parsing SUCCESS via json.loads")
                    print(f"[DEBUG] Nested keys: {list(nested_parsed.keys()) if isinstance(nested_parsed, dict) else 'NOT A DICT'}")

                # NOW extract requirements_document_md from the nested JSON
                requirements_doc_md = nested_parsed.get("requirements_document_md", "")
                print(f"[DEBUG] requirements_doc_md from NESTED JSON: length={len(requirements_doc_md)}")

                # Update parsed to use the nested data
                parsed = nested_parsed

            except json.JSONDecodeError as e2:
                print(f"[DEBUG] Nested JSON parsing FAILED: {e2}")

                # FALLBACK: Extract requirements_document_md directly from string using regex
                # This handles cases where the JSON is malformed but the field exists
                print(f"[DEBUG] Attempting regex extraction of requirements_document_md...")
                import re
                match = re.search(r'"requirements_document_md"\s*:\s*"((?:[^"\\]|\\.)*)"', team_result_str, re.DOTALL)
                if match:
                    # Unescape the JSON string
                    requirements_doc_md = match.group(1).encode().decode('unicode_escape')
                    print(f"[DEBUG] REGEX EXTRACTION SUCCESS: length={len(requirements_doc_md)}")
                else:
                    print(f"[DEBUG] REGEX EXTRACTION FAILED: field not found")

    # Fallback: try direct extraction
    if not requirements_doc_md:
        requirements_doc_md = parsed.get("requirements_document_md", "")
        print(f"[DEBUG] requirements_doc_md from parsed (direct): length={len(requirements_doc_md)}")

    # If not in JSON, try to extract from raw output (agent might return MD directly)
    if not requirements_doc_md and isinstance(result, dict):
        requirements_doc_md = result.get("requirements_document_md", "")
        print(f"[DEBUG] requirements_doc_md from result dict: length={len(requirements_doc_md)}")

    print(f"[DEBUG] FINAL requirements_doc_md length: {len(requirements_doc_md)}")
    if requirements_doc_md:
        print(f"[DEBUG] FINAL requirements_doc_md preview:\n{requirements_doc_md[:300]}")
    else:
        print(f"[DEBUG] ⚠️  WARNING: requirements_document_md is EMPTY!")
    print(f"{'='*80}\n")

    updated_state = {
        **state,
        "validation_json": output_json,
        "validation_data": parsed,
        "requirements_document_md": requirements_doc_md  # Add the generated document
    }

    return log_task_complete(updated_state, "validate_requirements")


def enrich_requirements_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for enrich_requirements task"""
    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "research_findings_json": state.get("research_findings_json", "{}"),
        "business_context": state.get("business_context", "{}"),
        "project_name": state.get("project_name", "")
    }


def enrich_requirements_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with enrich_requirements results"""
    # Extract output (same pattern as other output funcs)
    if hasattr(result, 'raw'):
        output_json = result.raw
    elif hasattr(result, 'json_dict') and result.json_dict:
        output_json = json.dumps(result.json_dict)
    elif hasattr(result, 'model_dump'):
        output_json = json.dumps(result.model_dump())
    elif isinstance(result, dict):
        output_json = json.dumps(result)
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
        # Handle nested team_result if present (Claude Code pattern)
        if isinstance(parsed, dict) and "team_result" in parsed:
            team_result_str = parsed["team_result"]
            if isinstance(team_result_str, str):
                # Remove markdown code blocks
                team_result_str = team_result_str.strip()
                if team_result_str.startswith("```json"):
                    team_result_str = team_result_str[7:]
                elif team_result_str.startswith("```"):
                    team_result_str = team_result_str[3:]
                if team_result_str.endswith("```"):
                    team_result_str = team_result_str[:-3]
                parsed = json.loads(team_result_str.strip())
    except json.JSONDecodeError as e:
        print(f"[ERROR] enrich_requirements JSON parsing failed: {e}")
        parsed = {}

    updated_state = {
        **state,
        "enriched_requirements": parsed.get("enriched_requirements", {}),
        "validation_status": parsed.get("validation_status", "UNKNOWN"),
        "validation_message": parsed.get("validation_message", ""),
        "completeness_flags": parsed.get("completeness_flags", {})
    }

    return log_task_complete(updated_state, "enrich_requirements")


def validate_quality_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for validate_quality task"""
    return {
        "enriched_requirements": json.dumps(state.get("enriched_requirements", {})),
        "business_context": state.get("business_context", "{}"),
        "project_name": state.get("project_name", "")
    }


def validate_quality_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with validate_quality results"""
    # Extract output (same pattern as other output funcs)
    if hasattr(result, 'raw'):
        output_json = result.raw
    elif hasattr(result, 'json_dict') and result.json_dict:
        output_json = json.dumps(result.json_dict)
    elif hasattr(result, 'model_dump'):
        output_json = json.dumps(result.model_dump())
    elif isinstance(result, dict):
        output_json = json.dumps(result)
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
        # Handle nested team_result if present (Claude Code pattern)
        if isinstance(parsed, dict) and "team_result" in parsed:
            team_result_str = parsed["team_result"]
            if isinstance(team_result_str, str):
                # Remove markdown code blocks
                team_result_str = team_result_str.strip()
                if team_result_str.startswith("```json"):
                    team_result_str = team_result_str[7:]
                elif team_result_str.startswith("```"):
                    team_result_str = team_result_str[3:]
                if team_result_str.endswith("```"):
                    team_result_str = team_result_str[:-3]
                parsed = json.loads(team_result_str.strip())
    except json.JSONDecodeError as e:
        print(f"[ERROR] validate_quality JSON parsing failed: {e}")
        parsed = {}

    updated_state = {
        **state,
        "quality_validation": parsed,
        "quality_scores": parsed.get("quality_scores", {}),
        "issues_found": parsed.get("issues_found", []),
        "critical_gaps": parsed.get("critical_gaps", [])
    }

    return log_task_complete(updated_state, "validate_quality")


def generate_document_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for generate_document task - includes template"""
    from datetime import datetime

    # Load the Requirements Document template
    template = load_template("requirements_document_template.md")

    # Provide ALL template variables with defaults
    default_placeholder = "To be filled by analysis"
    template_vars = {
        # Project info
        "project_name": state.get("project_name", ""),
        "project_description": state.get("project_description", ""),
        "project_objectives": state.get("additional_instructions", "")[:200] if state.get("additional_instructions") else default_placeholder,
        "project_context": "See additional instructions for context",
        "project_domain": state.get("project_domain", ""),
        "scope_includes": default_placeholder,
        "scope_excludes": default_placeholder,

        # Document metadata
        "document_id": state.get("document_id", ""),
        "document_path": state.get("document_path", ""),
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "document_status": "Draft",
        "documents_table": default_placeholder,
        "total_documents": "1",
        "total_pages": "N/A",
        "total_words": str(len(state.get("document_content", "").split())),
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "processing_time": "N/A",
        "total_processing_time": "N/A",

        # Requirements sections
        "functional_requirements_by_category": default_placeholder,
        "functional_requirements_list": default_placeholder,
        "non_functional_requirements_list": default_placeholder,
        "business_rules_by_domain": default_placeholder,
        "business_rules_list": default_placeholder,
        "actors_list": default_placeholder,
        "entities_description": default_placeholder,
        "workflows_overview": default_placeholder,
        "workflows_detailed": default_placeholder,
        "glossary_table": default_placeholder,
        "glossary_entries": default_placeholder,

        # NFR categories
        "nfr_performance": default_placeholder,
        "nfr_security": default_placeholder,
        "nfr_usability": default_placeholder,
        "nfr_reliability": default_placeholder,
        "nfr_scalability": default_placeholder,
        "nfr_maintainability": default_placeholder,

        # Quality analysis
        "consistency_analysis": default_placeholder,
        "conflicts_table": default_placeholder,
        "conflicts_entries": default_placeholder,
        "ambiguities_analysis": default_placeholder,
        "ambiguities_list": default_placeholder,
        "ambiguous_text": default_placeholder,
        "clarification_questions": default_placeholder,
        "high_priority_questions": default_placeholder,
        "medium_priority_questions": default_placeholder,
        "low_priority_questions": default_placeholder,

        # Completeness scores
        "completeness_score": "N/A",
        "fr_completeness": "N/A",
        "nfr_completeness": "N/A",
        "br_completeness": "N/A",
        "actors_completeness": "N/A",
        "entities_completeness": "N/A",
        "workflows_completeness": "N/A",

        # Quality scores
        "clarity_score": "N/A",
        "clarity_status": "N/A",
        "clarity_notes": "N/A",
        "consistency_score": "N/A",
        "consistency_status": "N/A",
        "consistency_notes": "N/A",
        "testability_score": "N/A",
        "testability_status": "N/A",
        "testability_notes": "N/A",
        "traceability_score": "N/A",
        "traceability_status": "N/A",
        "traceability_notes": "N/A",
        "completeness_status": "N/A",
        "completeness_notes": "N/A",

        # Gaps and issues
        "critical_gaps": default_placeholder,
        "information_requests": default_placeholder,
        "information_requests_list": default_placeholder,
        "essential_coverage_analysis": default_placeholder,
        "essential_coverage_table": default_placeholder,
        "application_type": "Web Application",
        "issues_summary": default_placeholder,
        "issues_detailed_list": default_placeholder,
        "critical_issues_count": "0",
        "high_issues_count": "0",
        "medium_issues_count": "0",
        "low_issues_count": "0",
        "severity": "N/A",

        # Diagrams and visualizations
        "entity_relationship_diagram": default_placeholder,
        "entity_attributes_table": default_placeholder,
        "workflow_sequence_diagram": default_placeholder,
        "prioritization_chart_data": default_placeholder,
        "dependencies_graph": default_placeholder,
        "critical_path_analysis": default_placeholder,
        "critical_requirements_list": default_placeholder,
        "coverage_mindmap": default_placeholder,
        "traceability_matrix": default_placeholder,

        # Web research
        "industry_best_practices": default_placeholder,
        "recommended_standards": default_placeholder,
        "suggested_technologies": default_placeholder,
        "compliance_checklist": default_placeholder,
        "compliance_entries": default_placeholder,
        "missing_requirements_discovered": default_placeholder,

        # Improvements
        "general_recommendations": default_placeholder,
        "fr_improvements": default_placeholder,
        "nfr_improvements": default_placeholder,
        "br_improvements": default_placeholder,
        "documentation_improvements": default_placeholder,

        # Next steps
        "immediate_actions": default_placeholder,
        "validations_needed": default_placeholder,
        "spec_preparation": default_placeholder,

        # System metadata
        "framework_version": "LangNet v1.0",
        "llm_provider": "DeepSeek",
        "llm_model": "DeepSeek Reasoner",
        "web_research_enabled": "Yes",
        "has_additional_instructions": "Yes" if state.get("additional_instructions") else "No",
        "version_history": "N/A",

        # Other
        "abbreviations_table": default_placeholder
    }

    # Format template with actual values BEFORE sending to LLM
    try:
        formatted_template = template.format(**template_vars)
        print(f"[TEMPLATE] ✅ Template formatado com {len(template_vars)} variáveis")
        print(f"[TEMPLATE] 📅 Data de geração: {template_vars['generation_date']}")
    except KeyError as e:
        print(f"[TEMPLATE] ⚠️ Erro ao formatar template: {e}")
        formatted_template = template

    return {
        "enriched_requirements": json.dumps(state.get("enriched_requirements", {})),
        "quality_validation": json.dumps(state.get("quality_validation", {})),
        "research_findings_json": state.get("research_findings_json", "{}"),
        "template": formatted_template,
        "project_name": state.get("project_name", ""),
        **template_vars
    }


def generate_document_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with generate_document results and extract requirements document"""
    print(f"\n{'='*80}")
    print(f"[DEBUG] generate_document_output_func - Processing result")
    print(f"[DEBUG] Result type: {type(result)}")

    # Extract output (same pattern as validate_requirements_output_func)
    if hasattr(result, 'raw'):
        output_json = result.raw
    elif hasattr(result, 'json_dict') and result.json_dict:
        output_json = json.dumps(result.json_dict)
    elif hasattr(result, 'model_dump'):
        output_json = json.dumps(result.model_dump())
    elif isinstance(result, dict):
        output_json = json.dumps(result)
    else:
        output_json = str(result)

    print(f"[DEBUG] output_json length: {len(output_json)}")
    print(f"[DEBUG] output_json preview (first 500 chars): {output_json[:500]}")

    try:
        parsed = json.loads(output_json)
        print(f"[DEBUG] Parsed type: {type(parsed)}")
        if isinstance(parsed, dict):
            print(f"[DEBUG] Parsed keys: {list(parsed.keys())}")
            print(f"[DEBUG] Has 'requirements_document_md' key: {'requirements_document_md' in parsed}")
            if 'requirements_document_md' in parsed:
                print(f"[DEBUG] requirements_document_md type: {type(parsed['requirements_document_md'])}")
                print(f"[DEBUG] requirements_document_md length: {len(str(parsed['requirements_document_md']))}")

        # Handle nested team_result if present
        if isinstance(parsed, dict) and "team_result" in parsed:
            team_result_str = parsed["team_result"]
            if isinstance(team_result_str, str):
                # Remove markdown code blocks
                team_result_str = team_result_str.strip()
                if team_result_str.startswith("```json"):
                    team_result_str = team_result_str[7:]
                elif team_result_str.startswith("```"):
                    team_result_str = team_result_str[3:]
                if team_result_str.endswith("```"):
                    team_result_str = team_result_str[:-3]
                
                # Parse the nested JSON
                nested_parse_failed = False
                try:
                    parsed = json.loads(team_result_str.strip())
                except json.JSONDecodeError as nested_err:
                    print(f"[DEBUG] Nested team_result JSON parse FAILED: {nested_err}")
                    nested_parse_failed = True
                # Regex fallback — string-level extraction directly from team_result_str
                if nested_parse_failed and isinstance(team_result_str, str):
                    import re as _re
                    m = _re.search(r'"requirements_document_md"\s*:\s*"((?:[^"\\]|\\.)*)"', team_result_str, _re.DOTALL)
                    if m:
                        try:
                            extracted = json.loads('"' + m.group(1) + '"')
                            parsed = {"requirements_document_md": extracted}
                            print(f"[DEBUG] Regex fallback OK — extracted {len(extracted)} chars")
                        except Exception as exc:
                            print(f"[DEBUG] Regex fallback decode failed: {exc}")
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON parsing FAILED: {e}")
        parsed = {}

    # Extract the requirements document MD
    requirements_doc_md = ""
    if isinstance(parsed, dict):
        requirements_doc_md = parsed.get("requirements_document_md", "")

    # Last-resort: regex direct na string output_json se ainda vazio
    if not requirements_doc_md and output_json:
        import re as _re
        m = _re.search(r'"requirements_document_md"\s*:\s*"((?:[^"\\]|\\.)*)"', output_json, _re.DOTALL)
        if m:
            try:
                requirements_doc_md = json.loads('"' + m.group(1) + '"')
                print(f"[DEBUG] Last-resort regex on output_json OK — {len(requirements_doc_md)} chars")
            except Exception as exc:
                print(f"[DEBUG] Last-resort regex decode failed: {exc}")

    print(f"[DEBUG] FINAL requirements_doc_md length: {len(requirements_doc_md)}")
    if requirements_doc_md:
        print(f"[DEBUG] FINAL requirements_doc_md preview:\n{requirements_doc_md[:300]}")
    else:
        print(f"[DEBUG] ⚠️  WARNING: requirements_document_md is EMPTY!")
    print(f"{'='*80}\n")

    # ─── BUILD REFERENCES SECTION (100% Python, zero LLM cost) ─────────────────
    if requirements_doc_md:
        from datetime import datetime

        ref_lines = [
            "\n\n---\n",
            "## 📚 Referências\n"
        ]

        # 16.1 — Source documents
        doc_path = state.get("document_path", "")
        doc_names = []
        if doc_path.startswith("Multiple documents: "):
            raw = doc_path.replace("Multiple documents: ", "")
            doc_names = [d.strip() for d in raw.split(",") if d.strip()]
        elif doc_path:
            doc_names = [doc_path.strip()]

        if doc_names:
            ref_lines.append("\n### 16.1 Documentos Analisados\n")
            ref_lines.append("| # | Documento |")
            ref_lines.append("|---|-----------|")
            for i, name in enumerate(doc_names, 1):
                ref_lines.append(f"| {i} | {name} |")
            ref_lines.append(f"\n*Analisados em: {datetime.now().strftime('%d/%m/%Y %H:%M')}*")

        # 16.2 — Web sources
        research_json = state.get("research_findings_json", "{}")
        try:
            research = json.loads(research_json) if isinstance(research_json, str) else research_json
        except (json.JSONDecodeError, TypeError):
            research = {}

        web_sources = []
        seen_urls = set()

        def add_source(name, url):
            if url and url not in seen_urls and url.startswith("http"):
                seen_urls.add(url)
                web_sources.append((name, url))

        for sys_item in research.get("analogous_systems", []):
            add_source(sys_item.get("name", "Sistema"), sys_item.get("source_url", ""))

        for bp in research.get("best_practices", []):
            add_source(bp.get("title", bp.get("source", "Referência")), bp.get("url", bp.get("source_url", "")))

        for comp in research.get("compliance_requirements", []):
            add_source(comp.get("standard", comp.get("name", "Norma")), comp.get("source_url", comp.get("url", "")))

        for tech in research.get("recommended_technologies", []):
            add_source(tech.get("name", "Tecnologia"), tech.get("source_url", tech.get("url", "")))

        if web_sources:
            ref_lines.append("\n### 16.2 Fontes Web Consultadas\n")
            ref_lines.append("| # | Fonte | URL |")
            ref_lines.append("|---|-------|-----|")
            for i, (name, url) in enumerate(web_sources, 1):
                ref_lines.append(f"| {i} | {name} | [{url}]({url}) |")
        elif research:
            ref_lines.append("\n### 16.2 Pesquisa Web\n")
            ref_lines.append("*Pesquisa web realizada sem URLs externas rastreáveis nos resultados.*")

        requirements_doc_md += "\n".join(ref_lines)
        print(f"[REFS] ✅ Seção de referências adicionada: {len(doc_names)} documentos, {len(web_sources)} fontes web")
    # ────────────────────────────────────────────────────────────────────────────

    updated_state = {
        **state,
        "validation_json": output_json,
        "validation_data": parsed,
        "requirements_document_md": requirements_doc_md,
        "document_metadata": parsed.get("document_metadata", {}),
        "quality_summary": parsed.get("quality_summary", {}),
        "source_distribution": parsed.get("source_distribution", {})
    }

    return log_task_complete(updated_state, "generate_document")


def generate_specification_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with generate_specification results"""
    if isinstance(result, dict):
        output_md = result.get("raw_output", str(result))
    else:
        output_md = str(result)

    updated_state = {
        **state,
        "specification_md": output_md,
        "specification_data": {"markdown": output_md}
    }

    return log_task_complete(updated_state, "generate_specification")


def suggest_agents_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with suggest_agents results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {"agents": []}

    updated_state = {
        **state,
        "agents_suggestions_json": output_json,
        "agents_data": parsed.get("agents", [])
    }

    return log_task_complete(updated_state, "suggest_agents")


def decompose_tasks_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with decompose_tasks results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {"tasks": [], "dependencies": {}}

    updated_state = {
        **state,
        "tasks_decomposition_json": output_json,
        "tasks_data": parsed.get("tasks", []),
        "dependencies": parsed.get("dependencies", {}),
        "execution_order": parsed.get("execution_order", []),
        "parallel_groups": parsed.get("parallel_groups", [])
    }

    return log_task_complete(updated_state, "decompose_tasks")


def _adapt_petri_net(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Adapter that normalizes LLM output to the petri-net-editor schema (PT-BR).

    Tolerates EN keys, fills defaults, computes layout via topological BFS,
    and ensures place.agentId references exist in agentes[].
    """
    key_map = {
        "places": "lugares", "transitions": "transicoes",
        "arcs": "arcos", "agents": "agentes",
        "name": "nome", "source": "origem", "target": "destino",
        "weight": "peso", "agent_id": "agentId", "logic": "logica",
        "coordinates": "coordenadas",
    }
    root = {key_map.get(k, k): v for k, v in parsed.items()}
    root.setdefault("nome", "Rede de Petri")
    root.setdefault("lugares", [])
    root.setdefault("transicoes", [])
    root.setdefault("arcos", [])
    root.setdefault("agentes", [])

    def remap(item: Dict[str, Any]) -> Dict[str, Any]:
        return {key_map.get(k, k): v for k, v in item.items()}

    lugares = [remap(p) for p in root["lugares"]]
    transicoes = [remap(t) for t in root["transicoes"]]
    arcos = [remap(a) for a in root["arcos"]]
    agentes = [remap(a) for a in root["agentes"]]

    agent_ids = {a.get("id") for a in agentes}
    for p in lugares:
        p.setdefault("id", "")
        p.setdefault("nome", p["id"])
        p.setdefault("tokens", 0)
        p.setdefault("delay", 0)
        p.setdefault("input_data", {})
        p.setdefault("output_data", {})
        p.setdefault("logica", "")
        p.setdefault("subnet", {})
        aid = p.get("agentId")
        p["agentId"] = aid if aid in agent_ids else None

    for t in transicoes:
        t.setdefault("id", "")
        t.setdefault("nome", t["id"])
        t.setdefault("orientacao", "vert")
        t.setdefault("prioridade", 1)
        t.setdefault("probabilidade", 0)
        t.setdefault("tempo", 0)
        t.setdefault("guard", "")

    for a in arcos:
        a.setdefault("peso", 1)

    for ag in agentes:
        ag.setdefault("id", "")
        ag.setdefault("nome", ag["id"])
        ag.setdefault("width", 300)
        ag.setdefault("height", 200)

    # Layout: BFS por níveis a partir dos lugares com tokens>0
    place_ids = {p["id"] for p in lugares}
    trans_ids = {t["id"] for t in transicoes}
    out_edges: Dict[str, List[str]] = {}
    for a in arcos:
        out_edges.setdefault(a.get("origem", ""), []).append(a.get("destino", ""))

    level: Dict[str, int] = {}
    queue: List[str] = [p["id"] for p in lugares if p.get("tokens", 0) > 0]
    if not queue and lugares:
        queue = [lugares[0]["id"]]
    for nid in queue:
        level[nid] = 0
    head = 0
    while head < len(queue):
        nid = queue[head]
        head += 1
        for nxt in out_edges.get(nid, []):
            if nxt not in level and nxt in (place_ids | trans_ids):
                level[nxt] = level[nid] + 1
                queue.append(nxt)
    # Nós não alcançados ficam no nível máximo + 1
    fallback_level = (max(level.values()) + 1) if level else 0
    for p in lugares:
        level.setdefault(p["id"], fallback_level)
    for t in transicoes:
        level.setdefault(t["id"], fallback_level)

    # Posiciona por nível
    by_level: Dict[int, List[str]] = {}
    for nid, lv in level.items():
        by_level.setdefault(lv, []).append(nid)
    pos: Dict[str, Dict[str, int]] = {}
    for lv, ids in by_level.items():
        for i, nid in enumerate(sorted(ids)):
            pos[nid] = {"x": 100 + lv * 150, "y": 100 + i * 120}

    for p in lugares:
        if not p.get("coordenadas"):
            p["coordenadas"] = pos.get(p["id"], {"x": 100, "y": 100})
    for t in transicoes:
        if not t.get("coordenadas"):
            t["coordenadas"] = pos.get(t["id"], {"x": 200, "y": 100})
    for ag in agentes:
        ag.setdefault("coordenadas", {"x": 50, "y": 50})

    root["lugares"] = lugares
    root["transicoes"] = transicoes
    root["arcos"] = arcos
    root["agentes"] = agentes
    return root


def design_petri_net_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with design_petri_net results, adapted to petri-net-editor schema."""
    import re as _re

    def _extract_json_string(obj: Any) -> str:
        """Unwrap CrewAI result variants down to the raw JSON string."""
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            for key in ("team_result", "raw_output", "raw", "output", "final_output", "result"):
                if key in obj:
                    return _extract_json_string(obj[key])
            return json.dumps(obj)
        return getattr(obj, "raw", None) or str(obj)

    output_json = _extract_json_string(result)

    def _try_parse(s: str) -> Dict[str, Any]:
        try:
            return json.loads(s)
        except (json.JSONDecodeError, TypeError):
            pass
        # Strip ```json fences and try again
        fence = _re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, _re.DOTALL)
        if fence:
            try:
                return json.loads(fence.group(1))
            except json.JSONDecodeError:
                pass
        # Last resort: take the outermost {...}
        outer = _re.search(r"\{.*\}", s, _re.DOTALL)
        if outer:
            try:
                return json.loads(outer.group(0))
            except json.JSONDecodeError:
                return {}
        return {}

    parsed = _try_parse(output_json)
    # Unwrap once more if the LLM nested the net under a single key (e.g. {"petri_net": {...}})
    if isinstance(parsed, dict) and not any(
        k in parsed for k in ("lugares", "places", "transicoes", "transitions")
    ):
        for v in parsed.values():
            if isinstance(v, dict) and any(
                k in v for k in ("lugares", "places", "transicoes", "transitions")
            ):
                parsed = v
                break

    adapted = _adapt_petri_net(parsed if isinstance(parsed, dict) else {})
    print(
        f"[PETRI OUT] adapted: lugares={len(adapted.get('lugares', []))} "
        f"transicoes={len(adapted.get('transicoes', []))} "
        f"arcos={len(adapted.get('arcos', []))}"
    )

    # Validação estrutural — emite warnings se detectarmos antipatterns
    petri_warnings = _validate_petri_net_topology(adapted)
    if petri_warnings:
        print(f"[PETRI WARN] {len(petri_warnings)} aviso(s) de topologia:")
        for w in petri_warnings:
            print(f"  ⚠ {w}")

    updated_state = {
        **state,
        "petri_net_json": json.dumps(adapted, ensure_ascii=False),
        "petri_net_data": adapted,
        "petri_net_warnings": petri_warnings,
    }

    return log_task_complete(updated_state, "design_petri_net")


def _validate_petri_net_topology(net: Dict[str, Any]) -> List[str]:
    """Detecta antipatterns na Petri Net gerada pelo LLM.

    Retorna lista de warnings (strings). Cada warning começa com uma categoria:
      - dead_transition: transição sem entrada ou sem saída
      - massive_fanout: transição com >3 saídas paralelas
      - branch_no_guards: transição com múltiplas saídas mas guards vazios em todas
      - orphan_place: lugar sem nenhum arco entrando E sem nenhum arco saindo
      - no_start_token: nenhum lugar com tokens=1
      - missing_dependency: lugar B referencia output de A mas não há arco A→T→B
    """
    if not isinstance(net, dict):
        return ["invalid_structure: petri_net não é um dict"]

    places = net.get("lugares", []) or []
    transitions = net.get("transicoes", []) or []
    arcs = net.get("arcos", []) or []
    warnings: List[str] = []

    place_ids = {p.get("id") for p in places if isinstance(p, dict)}
    trans_ids = {t.get("id") for t in transitions if isinstance(t, dict)}

    # 1) Dead transitions (sem entrada OU sem saída)
    for t in transitions:
        if not isinstance(t, dict):
            continue
        tid = t.get("id")
        ins = [a for a in arcs if a.get("destino") == tid]
        outs = [a for a in arcs if a.get("origem") == tid]
        if not ins and not outs:
            warnings.append(f"dead_transition: {tid} sem nenhum arco (entrada nem saída)")
        elif not ins:
            warnings.append(f"dead_transition: {tid} sem arco de entrada (fonte). Aceitável só se for T_start saindo de P0.")
        elif not outs:
            warnings.append(f"dead_transition: {tid} sem arco de saída (sumidouro)")

    # 2) Massive fan-out: transição com >3 saídas paralelas
    for t in transitions:
        tid = t.get("id") if isinstance(t, dict) else None
        if not tid:
            continue
        outs = [a for a in arcs if a.get("origem") == tid]
        if len(outs) > 3:
            dest_names = [str(a.get("destino")) for a in outs[:6]]
            warnings.append(
                f"massive_fanout: {tid} dispara {len(outs)} places em paralelo — provavelmente "
                f"esconde dependências sequenciais. Destinos: {', '.join(dest_names)}"
            )

    # 3) Branching sem guards: transição com múltiplas saídas (de mesma origem) sem guards
    # Detecta: 1 place A → várias transições T_x, T_y — se todas guards vazias é fan-out
    # (não branching real)
    for p in places:
        pid = p.get("id") if isinstance(p, dict) else None
        if not pid:
            continue
        # Transições alimentadas só por esse lugar
        feeding = [a.get("destino") for a in arcs if a.get("origem") == pid and a.get("destino") in trans_ids]
        if len(feeding) >= 2:
            # Verifica se TODAS têm guard vazio
            empty_guards = 0
            for tid in feeding:
                t = next((x for x in transitions if isinstance(x, dict) and x.get("id") == tid), None)
                if t and not (t.get("guard") or "").strip():
                    empty_guards += 1
            if empty_guards == len(feeding):
                warnings.append(
                    f"branch_no_guards: {pid} alimenta {len(feeding)} transições "
                    f"({', '.join(feeding)}) e nenhuma tem guard — vai disparar todas (concorrência)"
                )

    # 4) Orphan places
    referenced_in_arcs = {a.get("origem") for a in arcs} | {a.get("destino") for a in arcs}
    for p in places:
        pid = p.get("id") if isinstance(p, dict) else None
        if pid and pid not in referenced_in_arcs:
            warnings.append(f"orphan_place: {pid} não tem nenhum arco — não pode receber nem ceder tokens")

    # 5) No start token
    has_start = any((p.get("tokens") or 0) > 0 for p in places if isinstance(p, dict))
    if not has_start:
        warnings.append("no_start_token: nenhum lugar inicia com tokens>0 — a Petri Net é inerte")

    return warnings


def generate_yaml_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with generate_yaml_files results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "yaml_files_json": output_json,
        "agents_yaml": parsed.get("agents_yaml", ""),
        "tasks_yaml": parsed.get("tasks_yaml", "")
    }

    return log_task_complete(updated_state, "generate_yaml_files")


_PLACE_LOGICA_TEMPLATE = """// place.logica para task '{task_name}' — executado pelo PlaceProcessor do petri-net-editor.
// utils.merge e utils.getPlaceOutput vêm do contexto da sandbox; WebSocket/Date/JSON são globais.
const PORT = {ws_port};
const TASK_NAME = '{task_name}';
const PREV_PLACE_IDS = {prev_places_json};
const TIMEOUT_MS = {timeout_ms};

// Deep merge — essencial pra JOIN multi-predecessor (outputs.X de cada lado coexistem).
function deepMerge(target, source) {{
  if (!source || typeof source !== 'object') return target;
  for (const k of Object.keys(source)) {{
    const sv = source[k];
    const tv = target[k];
    if (sv && typeof sv === 'object' && !Array.isArray(sv) &&
        tv && typeof tv === 'object' && !Array.isArray(tv)) {{
      deepMerge(tv, sv);
    }} else {{
      target[k] = sv;
    }}
  }}
  return target;
}}

// Distingue payload útil de só metadata do PlaceProcessor (from_transition, etc).
function hasUsefulPayload(o) {{
  if (!o || typeof o !== 'object') return false;
  const meta = new Set(['from_transition','received_at','tokens_received','status','timestamp']);
  return Object.keys(o).some(k => !meta.has(k));
}}

const output = JSON.parse(JSON.stringify(input || {{}}));
try {{
  // Agrega outputs de TODOS os predecessores (espera com deadline grande
  // pq predecessores podem estar processando WS upstream — 90s).
  if (PREV_PLACE_IDS.length > 0) {{
    const deadline = Date.now() + 90000;
    for (const pid of PREV_PLACE_IDS) {{
      let prev = utils.getPlaceOutput(pid);
      while (!hasUsefulPayload(prev) && Date.now() < deadline) {{
        await new Promise(r => setTimeout(r, 300));
        prev = utils.getPlaceOutput(pid);
      }}
      if (prev && typeof prev === 'object') deepMerge(output, prev);
    }}
  }}

  const ws = new WebSocket(`ws://localhost:${{PORT}}`);
  const result = await new Promise((resolve, reject) => {{
    const t = setTimeout(() => {{ ws.close(); reject(new Error('timeout')); }}, TIMEOUT_MS);
    ws.onopen = () => ws.send(JSON.stringify({{
      type: 'execute_task',
      data: {{ task_name: TASK_NAME, input_data: output }}
    }}));
    ws.onmessage = (e) => {{
      const r = JSON.parse(e.data);
      if (r.type === 'task_completed' || r.type === 'task_result') {{
        clearTimeout(t); ws.close();
        resolve((r.data && r.data.result) || r.data || {{}});
      }} else if (r.type === 'error') {{
        clearTimeout(t); ws.close();
        reject(new Error((r.data && r.data.error) || 'task error'));
      }}
    }};
    ws.onerror = () => {{ clearTimeout(t); reject(new Error('WebSocket error')); }};
  }});

  if (result && typeof result === 'object') {{
    deepMerge(output, result);
  }} else {{
    output.result = result;
  }}
  output.status = 'completed';
  output.timestamp = new Date().toISOString();
}} catch (err) {{
  output.status = 'error';
  output.error = err.message;
}}
return output;
"""


def _build_petri_net_with_real_logica(
    petri_net: Dict[str, Any],
    websocket_port: int,
    known_task_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Substitui o placeholder em ``place.logica`` por código WebSocket real.

    Mantém intactos os demais campos (lugares/transicoes/arcos/agentes/coordenadas).
    Resolve dependências de cada place lendo ``arcos`` (lugar→transição→lugar próximo).

    Se ``known_task_names`` for fornecido, faz match do task_name extraído contra
    a lista — limpa sufixos comuns (_pronta/_ready/_in) e fuzzy match. Places cuja
    task derivada NÃO está em known_task_names recebem template intermediário
    (apenas propagam input).
    """
    if not isinstance(petri_net, dict):
        return petri_net
    arcs = petri_net.get("arcos", []) or []
    transitions = {t.get("id"): t for t in petri_net.get("transicoes", []) if isinstance(t, dict)}

    # Predecessores: para cada lugar, encontra os lugares que alimentam suas transições de entrada.
    # transitions_into_place = { lugar_id: [trans_id] }
    trans_into_place: Dict[str, List[str]] = {}
    places_into_trans: Dict[str, List[str]] = {}
    for a in arcs:
        if not isinstance(a, dict):
            continue
        origin, dest = a.get("origem"), a.get("destino")
        if origin in transitions and dest:
            trans_into_place.setdefault(dest, []).append(origin)
        if dest in transitions and origin:
            places_into_trans.setdefault(dest, []).append(origin)

    # Set de task names válidos (do tasks.yaml)
    valid_tasks = set(known_task_names or [])

    # Intermediário no padrão PlaceProcessor real: usa utils.merge / globals.
    # Agrega outputs dos predecessores conhecidos pra propagar contexto adiante.
    # Intermediário: aguarda cada predecessor ter output não-vazio (com
    # deadline pra não travar), depois deepMerge os outputs e propaga.
    # Wait loop necessário pq processPlace dispara quando token chega, mas
    # places WS upstream podem estar processando DeepSeek (~45s).
    _INTERMEDIATE_LOGICA = (
        "// place intermediário — aguarda predecessores e propaga outputs deep-merged\n"
        "function deepMerge(target, source) {\n"
        "  if (!source || typeof source !== 'object') return target;\n"
        "  for (const k of Object.keys(source)) {\n"
        "    const sv = source[k]; const tv = target[k];\n"
        "    if (sv && typeof sv === 'object' && !Array.isArray(sv) && tv && typeof tv === 'object' && !Array.isArray(tv)) deepMerge(tv, sv);\n"
        "    else target[k] = sv;\n"
        "  }\n"
        "  return target;\n"
        "}\n"
        "function hasUsefulPayload(o) {\n"
        "  if (!o || typeof o !== 'object') return false;\n"
        "  const meta = new Set(['from_transition','received_at','tokens_received','status','timestamp']);\n"
        "  return Object.keys(o).some(k => !meta.has(k));\n"
        "}\n"
        "const output = JSON.parse(JSON.stringify(input || {}));\n"
        "const PREV = (typeof PREV_PLACE_IDS !== 'undefined' ? PREV_PLACE_IDS : []);\n"
        "const WAIT_DEADLINE = Date.now() + 90000;\n"
        "for (const pid of PREV) {\n"
        "  let prev = utils.getPlaceOutput(pid);\n"
        "  while (!hasUsefulPayload(prev) && Date.now() < WAIT_DEADLINE) {\n"
        "    await new Promise(r => setTimeout(r, 300));\n"
        "    prev = utils.getPlaceOutput(pid);\n"
        "  }\n"
        "  if (prev && typeof prev === 'object') deepMerge(output, prev);\n"
        "}\n"
        "output.status = 'completed';\n"
        "output.timestamp = new Date().toISOString();\n"
        "return output;"
    )

    def _resolve_task_name(candidate: str) -> Optional[str]:
        """Tenta casar candidate com algum task_name conhecido (limpando sufixos)."""
        if not candidate:
            return None
        if not valid_tasks:
            return candidate  # sem lista, aceita qualquer
        if candidate in valid_tasks:
            return candidate
        # Limpa sufixos comuns adicionados pelo LLM
        for suf in ("_pronta", "_pronto", "_ready", "_in", "_out", "_start", "_finished"):
            if candidate.endswith(suf):
                trimmed = candidate[: -len(suf)]
                if trimmed in valid_tasks:
                    return trimmed
        # Fuzzy: substring de algum task name
        for t in valid_tasks:
            if t in candidate or candidate in t:
                return t
        return None

    out = {**petri_net, "lugares": []}
    for lugar in petri_net.get("lugares", []) or []:
        if not isinstance(lugar, dict):
            out["lugares"].append(lugar)
            continue
        lid = lugar.get("id", "")

        # Calcula prev_places do GRAFO (predecessores via transição de entrada).
        # Filtra "sources" (places sem entrada, como P0 "Início do Fluxo") —
        # eles nunca terão output útil, apenas metadata; ficariam presos no
        # wait loop até o deadline expirar.
        prev_places: List[str] = []
        for trans_id in trans_into_place.get(lid, []):
            prev_places.extend(places_into_trans.get(trans_id, []))
        prev_places = sorted(set(p for p in prev_places if p and p != lid))
        # Remove sources (nenhuma transição alimenta esse place)
        prev_places = [p for p in prev_places if trans_into_place.get(p)]

        # Places SEM agentId não chamam WS (são intermediários: _out, _in,
        # ready, fim do fluxo). JS agrega outputs dos predecessores para propagar.
        if not lugar.get("agentId"):
            new_lugar = {**lugar}
            new_lugar["logica"] = (
                f"const PREV_PLACE_IDS = {json.dumps(prev_places)};\n"
                + _INTERMEDIATE_LOGICA
            )
            out["lugares"].append(new_lugar)
            continue

        # Extrai task_name nessa ordem:
        #   1. task_name explícito no campo (se houver)
        #   2. regex no stub original da logica  (output.task_name = 'X')
        #   3. QUALQUER substring snake_case do nome do place que case com valid_tasks
        #   4. dentro de parênteses no nome do place  (ex: "(suggest_weekly_themes)")
        #   5. fallback: slug do nome do place
        task_name = (lugar.get("task_name") or "").strip()
        if not task_name:
            import re as _re_tn
            orig_logica = str(lugar.get("logica") or "")
            m = _re_tn.search(r"task_name\s*[:=]\s*['\"]([A-Za-z0-9_]+)['\"]", orig_logica)
            if m:
                task_name = m.group(1)
        # NOVA estratégia: tenta achar QUALQUER nome de task válido no nome do place
        if not task_name and valid_tasks:
            place_name_low = (lugar.get("nome") or "").lower()
            # match exato com tasks.yaml (prioriza nome mais longo pra evitar partial match errado)
            for vt in sorted(valid_tasks, key=len, reverse=True):
                if vt in place_name_low:
                    task_name = vt
                    break
        if not task_name:
            import re as _re_tn2
            # Pega TODOS os parênteses, prefere o que tem mais chars (geralmente o task name real)
            all_parens = _re_tn2.findall(r"\(([A-Za-z0-9_]+)\)", str(lugar.get("nome") or ""))
            if all_parens:
                task_name = max(all_parens, key=len)
        if not task_name:
            task_name = (lugar.get("nome") or lid).split(":")[-1].strip().replace(" ", "_").lower()

        # Resolve contra tasks.yaml — se não casa, vira intermediário
        resolved = _resolve_task_name(task_name)
        if not resolved:
            # Place com agentId mas task name não bate com tasks.yaml — virou intermediário
            new_lugar = {**lugar}
            new_lugar["logica"] = _INTERMEDIATE_LOGICA
            new_lugar["_unresolved_task"] = task_name  # debug hint
            out["lugares"].append(new_lugar)
            continue
        task_name = resolved

        # Timeout adaptativo: tasks com 'classify' ou 'analyze' levam mais tempo
        timeout_ms = 180000 if any(k in task_name for k in ("classif", "analy", "search", "extrac")) else 60000

        new_lugar = {**lugar}
        new_lugar["logica"] = _PLACE_LOGICA_TEMPLATE.format(
            task_name=task_name,
            ws_port=websocket_port,
            prev_places_json=json.dumps(prev_places),
            timeout_ms=timeout_ms,
        )
        out["lugares"].append(new_lugar)
    return out


def _parse_yaml_keys(yaml_text: str) -> List[str]:
    """Extract top-level keys from a YAML string (e.g. agent ids, task ids)."""
    try:
        parsed = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError:
        return []
    return list(parsed.keys()) if isinstance(parsed, dict) else []


def _parse_tools_from_spec(md: str) -> Dict[str, Dict[str, List[str]]]:
    """Extrai mapping de tools a partir do agent_task_spec_document (markdown).

    Procura as duas seções canônicas (`## 2. ESPECIFICAÇÃO ... AGENTES` e
    `## 3. ... TAREFAS`), em cada bloco `###`/`####` lê as linhas
    `| **Nome** | xxx |` e `| **Tools** | a, b, c |` e devolve:
    ``{"agents": {agent_id: [tool, ...]}, "tasks": {task_id: [tool, ...]}}``.
    """
    import re as _re

    def _extract_blocks(section_text: str) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        if not section_text:
            return result
        for block in _re.split(r"\n(?=#{3,4}\s)", section_text):
            nome = _re.search(r"\|\s*\*\*\s*Nome\s*\*\*\s*\|\s*([^|]+?)\s*\|", block)
            tools = _re.search(r"\|\s*\*\*\s*Tools\s*\*\*\s*\|\s*([^|]+?)\s*\|", block)
            if not (nome and tools):
                continue
            name = nome.group(1).strip()
            raw_tools = tools.group(1)
            # PRIMEIRO remove parênteses com conteúdo (evita quebrar vírgulas
            # internas em nomes tipo "database_tool (CRUD, histórico)").
            # Faz até 3 passadas pra lidar com parênteses aninhados.
            for _ in range(3):
                raw_tools = _re.sub(r"\s*\([^()]*\)\s*", " ", raw_tools)
            # AGORA sim splita por vírgula
            tools_list = [t.strip() for t in raw_tools.split(",")]
            # Normaliza cada tool: só primeira palavra "snake_case" antes de espaço
            def _norm(t: str) -> str:
                t = t.strip()
                # tira asteriscos/backticks/aspas comuns em markdown
                t = _re.sub(r"[`*'\"]+", "", t)
                # se veio "database_tool blabla", pega só o primeiro token
                m = _re.match(r"([a-z][a-z0-9_]+)", t)
                return m.group(1) if m else ""
            tools_list = [_norm(t) for t in tools_list]
            tools_list = [t for t in tools_list if t]
            if name:
                result[name] = tools_list
        return result

    if not md:
        return {"agents": {}, "tasks": {}}
    agents_match = _re.search(
        r"##\s*2\.\s*ESPECIFICA[ÇC][ÃA]O DETALHADA DOS AGENTES.*?(?=##\s*[3-9])",
        md, _re.DOTALL | _re.IGNORECASE,
    )
    tasks_match = _re.search(
        r"##\s*3\.\s*ESPECIFICA[ÇC][ÃA]O DETALHADA DAS TAREFAS.*?(?=##\s*[4-9])",
        md, _re.DOTALL | _re.IGNORECASE,
    )
    return {
        "agents": _extract_blocks(agents_match.group() if agents_match else ""),
        "tasks": _extract_blocks(tasks_match.group() if tasks_match else ""),
    }


def _template_main_py(project_name: str, ws_port: int) -> str:
    safe_name = (project_name or "Sistema Agêntico").replace('"', '\\"')
    return f'''"""
{project_name} — entrypoint
Sobe o servidor WebSocket na porta {ws_port} que recebe execute_task
e dispara a task CrewAI correspondente.
"""
import asyncio
import os
from dotenv import load_dotenv

from websocket_server import run_websocket_server

load_dotenv()

PROJECT_NAME = "{safe_name}"


def main():
    port = int(os.getenv("WEBSOCKET_PORT", "{ws_port}"))
    host = os.getenv("WEBSOCKET_HOST", "localhost")
    print(f"🚀 {{PROJECT_NAME}} — WebSocket server em ws://{{host}}:{{port}}")
    asyncio.run(run_websocket_server(host=host, port=port))


if __name__ == "__main__":
    main()
'''


def _template_websocket_server_py(ws_port: int) -> str:
    return f'''"""
WebSocket server compatível com o padrão visualtasksexec.
Recebe {{"type":"execute_task", "data":{{"task_name", "input_data"}}}}
e emite task_start / verbose / task_completed / error.
"""
import asyncio
import json
import os
import traceback
from datetime import datetime
from typing import Any, Dict

import websockets
import yaml
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

load_dotenv()

import tools as tools_module
import adapters as adapters_module


# ─── LLM: 3 providers configuráveis via LLM_PROVIDER ─────────────────────────
# - deepseek (default): API cloud, custa tokens. V4 Flash/Pro.
# - lmstudio: LM Studio local, R1 distill Qwen 32B. Zero custo/token.
# - openai: fallback.
#
# Estratégia: 2 LLMs pré-construídos, um "fast" e um "reasoning".
# - FLASH_LLM: pura geração de texto/JSON. Rápido. Agentes SEM tools.
# - PRO_LLM: raciocina antes de decidir chamar tool. Agentes COM tools.
# _build_agent escolhe automaticamente com base em `AGENT_TOOLS[agent_id]`.
def _current_provider() -> str:
    return (os.getenv("LLM_PROVIDER") or "deepseek").lower()


def _build_llm_flash() -> LLM:
    prov = _current_provider()
    if prov == "lmstudio":
        # LM Studio API OpenAI-compatible. Sem custo por token.
        # Modelo FAST (mesmo do reasoning aqui — LM Studio típico só tem R1 carregado).
        _m = os.getenv("LMSTUDIO_MODEL_NAME", "openai/deepseek-r1-distill-qwen-32b")
        if _m and not _m.startswith("openai/") and "/" not in _m:
            _m = f"openai/{{_m}}"
        return LLM(
            model=_m,
            api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
            base_url=os.getenv("LMSTUDIO_API_BASE", "http://192.168.1.115:1234/v1"),
            temperature=0.7,
            max_tokens=int(os.getenv("LMSTUDIO_MAX_TOKENS", "16000")),
        )
    if prov == "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
        return LLM(
            model=os.getenv("DEEPSEEK_MODEL_NAME", "deepseek/deepseek-v4-flash"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            temperature=0.7,
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "32768")),
            extra_body={{"reasoning": {{"enabled": False}}}},
        )
    return LLM(model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
               api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7)


def _build_llm_pro() -> LLM:
    prov = _current_provider()
    if prov == "lmstudio":
        # R1 já raciocina por padrão — sem flag necessário. Mesmo modelo do flash aqui.
        _m = os.getenv("LMSTUDIO_MODEL_NAME_PRO", os.getenv("LMSTUDIO_MODEL_NAME", "openai/deepseek-r1-distill-qwen-32b"))
        if _m and not _m.startswith("openai/") and "/" not in _m:
            _m = f"openai/{{_m}}"
        return LLM(
            model=_m,
            api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
            base_url=os.getenv("LMSTUDIO_API_BASE", "http://192.168.1.115:1234/v1"),
            temperature=0.3,
            max_tokens=int(os.getenv("LMSTUDIO_MAX_TOKENS_PRO", "24000")),
        )
    if prov == "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
        return LLM(
            model=os.getenv("DEEPSEEK_MODEL_NAME_PRO", "deepseek/deepseek-v4-pro"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            temperature=0.3,
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS_PRO", "32768")),
            extra_body={{"reasoning": {{"enabled": True}}}},
        )
    return LLM(model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
               api_key=os.getenv("OPENAI_API_KEY"), temperature=0.3)


FLASH_LLM = _build_llm_flash()
PRO_LLM = _build_llm_pro()
# Compat: código legado que ainda referencia SHARED_LLM funciona.
SHARED_LLM = FLASH_LLM


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {{}}


AGENTS_CONFIG = _load_yaml("agents.yaml")
TASKS_CONFIG = _load_yaml("tasks.yaml")


TOOL_REGISTRY = getattr(tools_module, "TOOL_REGISTRY", {{}})
TASK_TOOLS = getattr(adapters_module, "TASK_TOOLS", {{}})
AGENT_TOOLS = getattr(adapters_module, "AGENT_TOOLS", {{}})


def _resolve_tools(names):
    """Converte lista de nomes em instâncias de tool via TOOL_REGISTRY."""
    out = []
    for name in names or []:
        inst = TOOL_REGISTRY.get(name)
        if inst is not None:
            out.append(inst)
    return out


def _agent_for_task(task_id: str) -> str:
    """Resolve o agente da task — preferindo task.agent, com fallback
    para o primeiro agente em AGENT_TOOLS que mencione essa task."""
    cfg = TASKS_CONFIG.get(task_id, {{}}) or {{}}
    agent_id = cfg.get("agent") or cfg.get("agent_id")
    if agent_id:
        return agent_id
    # Fallback: primeiro agente da lista (degradação graceful)
    if AGENTS_CONFIG:
        return next(iter(AGENTS_CONFIG.keys()))
    return ""


def _build_agent(agent_id: str) -> Agent:
    cfg = AGENTS_CONFIG.get(agent_id, {{}})
    tool_names = AGENT_TOOLS.get(agent_id, [])
    tools = _resolve_tools(tool_names)
    # Se o agente tem TOOLS reais, usa PRO_LLM (com reasoning) — necessário
    # pra CrewAI conseguir fazer tool call. Sem tools, usa FLASH_LLM (mais barato/rápido).
    chosen_llm = PRO_LLM if tools else FLASH_LLM
    return Agent(
        role=cfg.get("role", agent_id),
        goal=cfg.get("goal", ""),
        backstory=cfg.get("backstory", ""),
        verbose=cfg.get("verbose", True),
        allow_delegation=cfg.get("allow_delegation", False),
        tools=tools,
        llm=chosen_llm,
    )


def _build_task(task_id: str, agent: Agent, description: str) -> Task:
    cfg = TASKS_CONFIG.get(task_id, {{}})
    tool_names = TASK_TOOLS.get(task_id, [])
    return Task(
        description=description or cfg.get("description", ""),
        expected_output=cfg.get("expected_output", ""),
        agent=agent,
        tools=_resolve_tools(tool_names),
    )


async def _send(ws, msg_type: str, data: Any) -> None:
    # default=str serializa datetime/date/Decimal/UUID vindos do banco (SELECT *).
    await ws.send(json.dumps({{
        "type": msg_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
    }}, default=str, ensure_ascii=False))


async def _execute_task(ws, task_name: str, input_data: Dict[str, Any]) -> None:
    await _send(ws, "task_start", {{"task_name": task_name, "input_data": input_data}})

    # Deterministic-first: se adapters.py define <task>_deterministic, roda direto
    # em Python (sem CrewAI/LLM). Vale inclusive para tasks CRUD auto-geradas
    # (listar_/atualizar_/excluir_<entidade>) que NÃO estão no tasks.yaml — por
    # isso este check vem ANTES da validação em TASKS_CONFIG.
    det_fn = getattr(adapters_module, f"{{task_name}}_deterministic", None)
    if callable(det_fn):
        try:
            payload = input_data if isinstance(input_data, dict) else {{}}
            loop = asyncio.get_running_loop()
            det_result = await loop.run_in_executor(None, det_fn, payload)
            await _send(ws, "task_completed", {{"task_name": task_name, "result": det_result}})
        except Exception as _exc:
            await _send(ws, "error", {{"task_name": task_name, "error": str(_exc), "traceback": traceback.format_exc()}})
        return

    task_cfg = TASKS_CONFIG.get(task_name)
    if not task_cfg:
        await _send(ws, "error", {{"task_name": task_name, "error": f"task '{{task_name}}' não definida em tasks.yaml"}})
        return

    agent_id = task_cfg.get("agent") or task_cfg.get("agent_id")
    if not agent_id:
        await _send(ws, "error", {{"task_name": task_name, "error": "task sem agente vinculado"}})
        return

    try:
        agent = _build_agent(agent_id)

        # Aplica input_func (extrai dados de input_data → kwargs)
        input_fn = getattr(adapters_module, f"{{task_name}}_input_func", None)
        prepared = input_fn(input_data) if callable(input_fn) else input_data

        # Formata a descrição da task com inputs — usa format_map com dict que
        # devolve string vazia p/ chaves ausentes, evitando fallback silencioso
        # que deixa {{placeholders}} literais no prompt do agente.
        description = task_cfg.get("description", "")
        if prepared:
            class _SafeDict(dict):
                def __missing__(self, key):
                    return ""  # placeholder ausente vira vazio (não quebra)
            # Achata prepared em strings pra evitar KeyError em __missing__
            try:
                description = description.format_map(_SafeDict(prepared))
            except Exception:
                pass  # último recurso: mantém description literal

        task = _build_task(task_name, agent, description)
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, crew.kickoff)

        raw = getattr(result, "raw", None) or str(result)

        output_fn = getattr(adapters_module, f"{{task_name}}_output_func", None)
        if callable(output_fn):
            try:
                parsed = output_fn(input_data, raw)
            except Exception:
                parsed = {{"raw": raw}}
        else:
            parsed = {{"raw": raw}}

        await _send(ws, "task_completed", {{"task_name": task_name, "result": parsed}})
    except Exception as exc:
        await _send(ws, "error", {{"task_name": task_name, "error": str(exc), "traceback": traceback.format_exc()}})


async def _handle_client(ws):
    await _send(ws, "connected", {{"available_tasks": list(TASKS_CONFIG.keys())}})
    async for message in ws:
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            await _send(ws, "error", {{"error": "invalid JSON"}})
            continue

        msg_type = payload.get("type")
        data = payload.get("data") or {{}}

        if msg_type == "execute_task":
            await _execute_task(ws, data.get("task_name"), data.get("input_data") or {{}})
        elif msg_type == "ping":
            await _send(ws, "pong", {{"timestamp": datetime.utcnow().isoformat()}})
        elif msg_type == "get_task_info":
            await _send(ws, "task_info", {{"tasks": list(TASKS_CONFIG.keys())}})
        else:
            await _send(ws, "error", {{"error": f"unknown message type: {{msg_type}}"}})


async def run_websocket_server(host: str = "localhost", port: int = {ws_port}):
    async with websockets.serve(_handle_client, host, port, ping_interval=30, ping_timeout=10):
        print(f"🌐 WebSocket aceitando conexões em ws://{{host}}:{{port}}")
        await asyncio.Future()  # run forever
'''


def _template_requirements_txt(_extra_pkgs: List[str] = None) -> str:
    base = [
        "crewai>=0.30.0",
        "crewai-tools>=0.1.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.1.0",
        "openai>=1.0.0",
        "websockets>=11.0.3",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        # Database (para database_tool real)
        "mysql-connector-python>=8.0.0",
    ]
    if _extra_pkgs:
        for p in _extra_pkgs:
            if p not in base:
                base.append(p)
    return "\n".join(base) + "\n"


def _template_database_tool_py() -> str:
    """Template do database_tool.py real, com conexão MySQL configurável.

    O tool aceita queries SQL parametrizadas e retorna resultados como JSON.
    Suporta SELECT (retorna linhas), INSERT/UPDATE/DELETE (retorna affected rows +
    last insert id). Conexão via variáveis de ambiente DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME.
    """
    return '''"""Database Tool — CrewAI BaseTool que executa queries reais em MySQL.

Configuração via ambiente:
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

O tool é seguro por padrão: SELECT retorna linhas como JSON, mutations retornam
row count + last_insert_id. Aceita params posicionais via placeholder %s.

Uso pelos agentes CrewAI:
    result = database_tool.run(query="SELECT * FROM leads WHERE score > 70")
    result = database_tool.run(
        query="INSERT INTO leads (nome, empresa, score) VALUES (%s, %s, %s)",
        params=["Fulano", "Beltrano SA", 85]
    )
"""
from __future__ import annotations

import json
import os
import logging
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

import mysql.connector

log = logging.getLogger(__name__)


class DatabaseToolSchema(BaseModel):
    query: str = Field(..., description="Query SQL. Use %s como placeholder pra parâmetros.")
    params: Optional[List[Any]] = Field(
        default=None,
        description="Lista de parâmetros posicionais pra bindings %s da query."
    )


class DatabaseTool(BaseTool):
    name: str = "database_tool"
    description: str = (
        "Executa queries SQL no banco de dados da aplicação (MySQL). "
        "Para SELECT retorna as linhas em JSON. Para INSERT/UPDATE/DELETE retorna "
        "affected_rows e last_insert_id. Sempre use placeholders %s pra parâmetros "
        "(evita SQL injection e formata datas/strings corretamente)."
    )
    args_schema: type[BaseModel] = DatabaseToolSchema

    def _connect(self):
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", ""),
            connection_timeout=10,
            autocommit=False,
        )

    def _run(self, query: str, params: Optional[List[Any]] = None) -> str:
        q = (query or "").strip()
        if not q:
            return json.dumps({"error": "query vazia"}, ensure_ascii=False)

        is_select = q.lstrip("(").lower().startswith(("select", "show", "describe", "explain"))
        conn = None
        try:
            conn = self._connect()
            cur = conn.cursor(dictionary=True)
            cur.execute(q, tuple(params) if params else None)

            if is_select:
                rows = cur.fetchall()
                # Serializa datas/UUIDs pra string
                out = json.dumps(
                    {"rows": rows, "row_count": len(rows)},
                    ensure_ascii=False, default=str,
                )
            else:
                conn.commit()
                out = json.dumps(
                    {
                        "affected_rows": cur.rowcount,
                        "last_insert_id": cur.lastrowid,
                    },
                    ensure_ascii=False,
                )
            cur.close()
            return out

        except mysql.connector.Error as e:
            if conn:
                try: conn.rollback()
                except Exception: pass
            log.exception("DatabaseTool error")
            return json.dumps(
                {"error": str(e), "errno": e.errno if hasattr(e, "errno") else None},
                ensure_ascii=False,
            )
        except Exception as e:
            log.exception("DatabaseTool unexpected error")
            return json.dumps({"error": str(e)}, ensure_ascii=False)
        finally:
            if conn:
                try: conn.close()
                except Exception: pass


# Instância pronta pra ser importada pelo TOOL_REGISTRY
database_tool = DatabaseTool()
'''


def _template_env_example(detected_tools: List[str]) -> str:
    lines = [
        "# Configurações do servidor WebSocket",
        "WEBSOCKET_HOST=localhost",
        "WEBSOCKET_PORT=5002",
        "",
        "# LLM — escolha um (DeepSeek é o padrão; deixe vazio para usar OpenAI)",
        "LLM_PROVIDER=deepseek",
        "DEEPSEEK_API_KEY=sk-...",
        "DEEPSEEK_API_BASE=https://api.deepseek.com",
        "DEEPSEEK_MODEL_NAME=deepseek/deepseek-v4-flash",
        "# Reasoning OFF por padrão (libera o budget de output só pra content).",
        "# Ligue (=true) só em tasks que precisam de raciocínio explícito.",
        "DEEPSEEK_REASONING=false",
        "DEEPSEEK_MAX_TOKENS=32768",
        "",
        "# Alternativa OpenAI",
        "OPENAI_API_KEY=sk-...",
        "OPENAI_MODEL_NAME=gpt-4o-mini",
        "",
        "# Desabilita telemetria/banner interativo do CrewAI (essencial em background)",
        "CREWAI_TESTING=true",
        "OTEL_SDK_DISABLED=true",
        "",
        "# Banco de dados (usado por database_tool)",
        "DB_HOST=camerascasas.no-ip.info",
        "DB_PORT=3308",
        "DB_USER=producao",
        "DB_PASSWORD=112358123",
        "DB_NAME=quantica_ops",
        "",
        "# LM Studio local (economia total em dev — troque LLM_PROVIDER=lmstudio)",
        "# LLM_PROVIDER=lmstudio",
        "LMSTUDIO_API_BASE=http://192.168.1.115:1234/v1",
        "LMSTUDIO_MODEL_NAME=openai/deepseek-r1-distill-qwen-32b",
        "LMSTUDIO_API_KEY=lm-studio",
        "LMSTUDIO_MAX_TOKENS=16000",
        "LMSTUDIO_MAX_TOKENS_PRO=24000",
        "",
    ]
    tools_lower = " ".join(detected_tools).lower()
    if "email" in tools_lower or "imap" in tools_lower or "smtp" in tools_lower:
        lines.extend([
            "# Email",
            "SMTP_HOST=smtp.gmail.com",
            "SMTP_PORT=465",
            "IMAP_HOST=imap.gmail.com",
            "IMAP_PORT=993",
            "EMAIL_USERNAME=",
            "EMAIL_PASSWORD=",
            "",
        ])
    if "mindsdb" in tools_lower:
        lines.extend([
            "# MindsDB",
            "MINDSDB_HOST=localhost",
            "MINDSDB_PORT=47334",
            "MINDSDB_USER=admin",
            "MINDSDB_PASSWORD=password123",
            "",
        ])
    return "\n".join(lines)


def _template_docker_compose(project_name: str, ws_port: int) -> str:
    slug = project_name.lower().replace(" ", "_").replace("-", "_") or "agentic_app"
    return f'''version: "3.9"

services:
  {slug}:
    build: .
    container_name: {slug}_ws
    environment:
      - WEBSOCKET_HOST=0.0.0.0
      - WEBSOCKET_PORT={ws_port}
    env_file:
      - .env
    ports:
      - "{ws_port}:{ws_port}"
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
'''


def _template_dockerfile() -> str:
    return '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
'''


def _template_readme(project_name: str, ws_port: int, file_list: List[str]) -> str:
    files_md = "\n".join(f"- `{p}`" for p in file_list)
    return f'''# {project_name}

Sistema multi-agente CrewAI orquestrado por Rede de Petri, gerado pelo LangNet Interface.

## Arquitetura

- `main.py` sobe o servidor WebSocket na porta `{ws_port}`.
- `websocket_server.py` recebe `execute_task` e dispara CrewAI com `Agent`/`Task` de `agents.yaml`/`tasks.yaml`.
- `adapters.py` contém `input_func`/`output_func` por task.
- `tools.py` contém tools customizadas.
- `petri_net.json` é a Rede de Petri, com `place.logica` JavaScript que abre WebSocket para esse servidor.

A Rede de Petri é executada pelo `petri-net-editor` (frontend) ou pelo runner Node.js do `experimental_petri`.

## Como rodar

```bash
cp .env.example .env
# preencha as variáveis em .env

pip install -r requirements.txt
python main.py
```

Ou com Docker:

```bash
docker-compose up --build
```

## Estrutura

{files_md}
'''


def _detect_extra_packages(tools_py: str) -> List[str]:
    """Detecta pacotes Python a adicionar ao requirements baseado em imports do tools.py."""
    extras: List[str] = []
    txt = (tools_py or "").lower()
    # Mapping determinístico: token no código → pacote pip
    mapping = [
        (("imap_tools", "from imaplib"), "imap-tools>=1.0.0"),
        (("mindsdb",), "mindsdb-sdk>=1.7.0"),
        (("pandas",), "pandas>=2.0.0"),
        (("requests",), "requests>=2.31.0"),
        (("feedparser",), "feedparser>=6.0.0"),
        (("beautifulsoup", "bs4"), "beautifulsoup4>=4.12.0"),
        (("lxml",), "lxml>=4.9.0"),
        (("httpx",), "httpx>=0.25.0"),
        (("aiohttp",), "aiohttp>=3.9.0"),
        (("linkedin_api",), "linkedin-api>=2.0.0"),
        (("pdfplumber",), "pdfplumber>=0.10.0"),
        (("pypdf",), "pypdf>=3.0.0"),
        (("docx",), "python-docx>=1.0.0"),
        (("openpyxl",), "openpyxl>=3.1.0"),
        (("google.oauth2", "googleapiclient"), "google-api-python-client>=2.100.0"),
        (("slack_sdk",), "slack-sdk>=3.20.0"),
        (("boto3",), "boto3>=1.28.0"),
        (("psycopg", "psycopg2"), "psycopg2-binary>=2.9.0"),
        (("redis",), "redis>=5.0.0"),
        (("sqlalchemy",), "sqlalchemy>=2.0.0"),
    ]
    for tokens, pkg in mapping:
        if any(t in txt for t in tokens):
            extras.append(pkg)
    return extras


def _empty_tools_py(detected: List[str]) -> str:
    return f'''"""Tools customizadas detectadas: {", ".join(detected) or "nenhuma"}.

Esqueleto: adicione classes que herdem de crewai.tools.BaseTool conforme necessário.
"""
from typing import Any
from crewai.tools import BaseTool


# (Sem tools customizadas detectadas — adicione conforme necessário.)
'''


def _empty_adapters_py() -> str:
    return '''"""Adapters de input/output por task.

Padrão:
def <task_id>_input_func(input_data: dict) -> dict:
    # extrai kwargs para a task
    return input_data

def <task_id>_output_func(input_data: dict, result: str) -> dict:
    # parseia o resultado retornado pelo CrewAI
    return {"raw": result}
"""
from typing import Any, Dict
'''


def _inject_task_tools_into_adapters(adapters_py: str, agents_map: Dict[str, List[str]], tasks_map: Dict[str, List[str]]) -> str:
    """Anexa AGENT_TOOLS e TASK_TOOLS dicts no fim do adapters.py.

    O websocket_server.py importa adapters_module.TASK_TOOLS / AGENT_TOOLS
    para amarrar tools por nome via tools_module.TOOL_REGISTRY.
    """
    block_lines = ["", "", "# ─── Bindings de tools (deterministic, extraído do agent_task_spec) ───"]
    block_lines.append("AGENT_TOOLS = {")
    for agent_id, tools in sorted(agents_map.items()):
        block_lines.append(f"    {agent_id!r}: {tools!r},")
    block_lines.append("}")
    block_lines.append("")
    block_lines.append("TASK_TOOLS = {")
    for task_id, tools in sorted(tasks_map.items()):
        block_lines.append(f"    {task_id!r}: {tools!r},")
    block_lines.append("}")
    block_lines.append("")
    return adapters_py.rstrip() + "\n" + "\n".join(block_lines) + "\n"


def _inject_input_placeholders_in_task_descriptions(tasks_yaml: str, tasks_map: dict = None) -> str:
    """Adiciona placeholders Jinja `{campo}` + instrução de uso obrigatório das
    tools nas descriptions das tasks.

    - Placeholder block: expõe cada input do WS via `{key}` (CrewAI só interpola
      se aparecer como `{key}` na description).
    - Instrução mandatória: força o LLM a USAR as tools em vez de alucinar
      respostas (padrão comum quando a description é só "inserir na tabela").
    """
    import re as _re
    if not tasks_yaml:
        return tasks_yaml
    try:
        import yaml as _yaml
        parsed = _yaml.safe_load(tasks_yaml)
    except Exception:
        return tasks_yaml
    if not isinstance(parsed, dict):
        return tasks_yaml
    tasks_map = tasks_map or {}

    changed = 0
    for task_name, cfg in parsed.items():
        if not isinstance(cfg, dict):
            continue
        desc = cfg.get("description") or ""
        if not isinstance(desc, str) or not desc:
            continue

        # Extrai chaves do bloco Input data format
        # Aceita variações: "Input data format:", "Input:", "Inputs:"
        m = _re.search(
            r"(?:Input(?:s|\s+data\s+format)?):\s*\n((?:\s*-\s*[a-z_][a-z0-9_]*\s*:.*\n?)+)",
            desc, _re.IGNORECASE,
        )
        keys: list = []
        if m:
            for line in m.group(1).split("\n"):
                km = _re.match(r"\s*-\s*([a-z_][a-z0-9_]*)\s*:", line)
                if km:
                    keys.append(km.group(1))
        # Fallback: se não achou bloco, tenta pegar qualquer "- key: tipo" no doc
        if not keys:
            for line in desc.split("\n"):
                km = _re.match(r"\s*-\s*([a-z_][a-z0-9_]*)\s*:\s*(?:string|integer|int|uuid|date|datetime|boolean|bool|array|list|dict|object|float)",
                               line, _re.IGNORECASE)
                if km:
                    keys.append(km.group(1))

        keys = list(dict.fromkeys(keys))  # dedup mantendo ordem
        if not keys:
            continue

        # Se todos os placeholders já estão presentes, pula
        if all(("{" + k + "}") in desc for k in keys):
            continue

        # Tools da task (pra montar instrução mandatória)
        tools_of_task = tasks_map.get(task_name, []) if isinstance(tasks_map, dict) else []
        # Instrução mandatória de uso das tools
        # IMPORTANTE: qualquer `{...}` que NÃO seja placeholder de input deve usar
        # `{{` e `}}` — senão str.format_map falha e a description vai literal.
        if tools_of_task:
            tool_names = ", ".join(f"`{t}`" for t in tools_of_task)
            mandatory = (
                f"⚠️ REGRAS OBRIGATÓRIAS PARA ESTA TAREFA:\n"
                f"1. Você DEVE usar as ferramentas: {tool_names}. NÃO simule resultados.\n"
                f"2. Se a tarefa exige INSERT/UPDATE/DELETE, chame `database_tool` com a query SQL real.\n"
                f"3. Não invente UUIDs, IDs nem confirmações — pegue do resultado real da tool.\n"
                f"4. Se uma consulta falhar (retornar chave 'error' no JSON), reporte o erro no output; não maquie.\n\n"
            )
        else:
            mandatory = ""

        # Blinda o resto da description contra format_map: escapa qualquer `{`
        # ou `}` que NÃO seja um dos placeholders conhecidos (as chaves em keys).
        # Isso permite que o LLM escreva `{"chave": ...}` em exemplos sem quebrar.
        known = set(keys)
        parts: list = []
        i = 0
        while i < len(desc):
            ch = desc[i]
            if ch in "{}":
                # detecta placeholder legítimo: {key} onde key ∈ known
                if ch == "{":
                    end = desc.find("}", i + 1)
                    if end != -1:
                        candidate = desc[i + 1 : end]
                        if candidate in known:
                            parts.append(desc[i : end + 1])
                            i = end + 1
                            continue
                # não é placeholder legítimo → duplica pra escapar
                parts.append(ch * 2)
                i += 1
                continue
            parts.append(ch)
            i += 1
        desc = "".join(parts)

        placeholder_block = (
            "📥 INPUTS RECEBIDOS (use esses valores nas suas queries e chamadas de tool):\n"
            + "\n".join(f"  - {k} = {{{k}}}" for k in keys)
            + "\n\n"
        )
        cfg["description"] = mandatory + placeholder_block + desc
        changed += 1

    if changed == 0:
        return tasks_yaml
    try:
        return _yaml.safe_dump(parsed, sort_keys=False, allow_unicode=True, default_flow_style=False)
    except Exception:
        return tasks_yaml


def _rewrite_input_funcs_pass_input_data(adapters_py: str) -> str:
    """Reescreve todos os `<task>_input_func(state)` gerados pelo LLM pra sempre
    passar `state["input_data"]` como inputs do agente, evitando o padrão comum
    do LLM de hardcodar dados de exemplo (ex.: ``{"nome": "João Silva"}``).

    Estratégia: sobrescreve o CORPO da função por um passthrough determinístico
    que combina `input_data` do WS + qualquer output já acumulado em `state["outputs"]`
    (necessário pra JOIN entre tasks).
    """
    import re as _re
    if not adapters_py:
        return adapters_py

    # Padrão: def <name>_input_func(<args>) -> <ret>: ... até próxima def/class ou fim
    pattern = _re.compile(
        r"(^def\s+(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)_input_func\s*\([^)]*\)[^:]*:\n)"
        r"(?P<body>(?:[ \t]+.*\n|[ \t]*\n)+)",
        _re.MULTILINE,
    )

    def _replace(m: "_re.Match[str]") -> str:
        header = m.group(1)
        # Novo corpo determinístico
        new_body = (
            "    # Passthrough determinístico injetado pelo LangNet: encaminha o\n"
            "    # input_data do WS + outputs acumulados; ignora corpo original do LLM\n"
            "    # (que costumava hardcodar dados de exemplo).\n"
            "    payload = state.get('input_data') if isinstance(state, dict) else None\n"
            "    if not isinstance(payload, dict):\n"
            "        payload = state if isinstance(state, dict) else {}\n"
            "    upstream = state.get('outputs') if isinstance(state, dict) else None\n"
            "    if isinstance(upstream, dict) and upstream:\n"
            "        merged = dict(payload)\n"
            "        merged['upstream_outputs'] = upstream\n"
            "        return merged\n"
            "    return payload\n"
            "\n"
        )
        return header + new_body

    new_txt, n = pattern.subn(_replace, adapters_py)
    if n > 0:
        # Marca no topo pra rastreabilidade
        marker = "# NOTE: input_funcs reescritos determinísticamente pelo LangNet (evitando hardcode do LLM).\n"
        if marker not in new_txt:
            new_txt = marker + new_txt
    return new_txt


def _generate_deterministic_adapters(tasks_yaml: str) -> str:
    """Parse each task's `description` (which by v4 convention embeds SQL steps
    of the form ``query="..."`` / ``params=[...]``) and emit a Python function
    ``<task_name>_deterministic(input_data)`` that executes those steps directly
    against MySQL — bypassing the LLM entirely for CRUD tasks.

    Returns a Python source snippet (may be empty if no CRUD task detected).
    The snippet is appended to adapters.py; websocket_server checks for the
    ``_deterministic`` suffix before dispatching to CrewAI.

    Supported patterns per step (order-preserving):
      - INSERT INTO <t>(<cols>) VALUES(<placeholders>)  params=[{a}, {b}]
      - UPDATE <t> SET ... WHERE ...                    params=[{a}, {id}]
      - DELETE FROM <t> WHERE ...                       params=[{id}]
      - SELECT id FROM <t> WHERE ...                    params=[{key}]     → capture as <t>_id
      - LOOP header: "Para CADA <item> em {<lista>}:" preceding INSERT
        → for item in input_data.get(lista): INSERT with params substituting <item>
      - Captured var references (e.g. persona_id) map to variables set by an
        earlier SELECT step.

    Anything not matching is skipped — the task falls through to the CrewAI path.
    """
    import re as _re
    try:
        import yaml as _yaml
        parsed = _yaml.safe_load(tasks_yaml) or {}
    except Exception:
        return ""
    if not isinstance(parsed, dict):
        return ""

    generated: List[str] = []
    generated_names: List[str] = []
    for task_name, cfg in parsed.items():
        if not isinstance(cfg, dict):
            continue
        desc = cfg.get("description") or ""
        if not isinstance(desc, str):
            continue

        body = _parse_task_description_to_python(desc)
        if not body:
            continue

        # Emit function
        fn_src = (
            f"def {task_name}_deterministic(input_data):\n"
            f"    \"\"\"Auto-generated by LangNet: executes {task_name}'s CRUD steps\n"
            f"    directly against MySQL, bypassing the CrewAI agent.\"\"\"\n"
            f"    import os\n"
            f"    import mysql.connector\n"
            f"    conn = mysql.connector.connect(\n"
            f"        host=os.getenv('DB_HOST', 'localhost'),\n"
            f"        port=int(os.getenv('DB_PORT', '3306')),\n"
            f"        user=os.getenv('DB_USER', 'root'),\n"
            f"        password=os.getenv('DB_PASSWORD', ''),\n"
            f"        database=os.getenv('DB_NAME', ''),\n"
            f"    )\n"
            f"    try:\n"
            f"        cur = conn.cursor(dictionary=True)\n"
            f"{body}"
            f"        conn.commit()\n"
            f"        return _result\n"
            f"    except Exception as _e:\n"
            f"        conn.rollback()\n"
            f"        return {{'status': 'erro', 'error': str(_e)}}\n"
            f"    finally:\n"
            f"        try: cur.close()\n"
            f"        except Exception: pass\n"
            f"        conn.close()\n"
        )
        generated.append(fn_src)
        generated_names.append(task_name)

    if not generated:
        return ""

    header = (
        "\n\n# ─── Deterministic CRUD adapters (auto-generated by LangNet) ───\n"
        "# Cada função <task>_deterministic(input_data) executa os passos SQL da\n"
        "# description da task DIRETO no MySQL, sem chamar LLM/CrewAI. O\n"
        "# websocket_server usa essas funções por padrão quando existem, caindo\n"
        "# de volta pro agente CrewAI só quando não há função deterministic.\n"
        f"# Tasks geradas: {', '.join(generated_names)}\n"
    )
    return header + "\n\n".join(generated) + "\n"


# ─────────────────────────────────────────────────────────────────────
# CRUD determinístico completo por entidade (list / obter / atualizar / excluir)
# ─────────────────────────────────────────────────────────────────────
_TECH_COLS = {"created_at", "updated_at"}

def _schema_model(schema_sql: str) -> Dict[str, dict]:
    """Modela o schema: {tabela: {cols:[(nome,tipo)], pk, uniques:[..], children:[(child,fk_col,val_col)]}}."""
    import re as _re
    tables = _parse_schema_tables_full(schema_sql)
    model: Dict[str, dict] = {}
    # 1ª passada: colunas, pk, uniques
    for t, ddl in tables.items():
        cols = []
        for m in _re.finditer(r'^\s*[`"]?(\w+)[`"]?\s+(CHAR|VARCHAR|TEXT|LONGTEXT|INT|BIGINT|TINYINT|DECIMAL|FLOAT|DOUBLE|DATE|DATETIME|TIMESTAMP|ENUM|GEOMETRY|BOOLEAN|JSON)', ddl, _re.I | _re.M):
            cols.append((m.group(1), m.group(2).upper()))
        pk = "id"
        pkm = _re.search(r'[`"]?(\w+)[`"]?\s+[^\n,]*PRIMARY KEY', ddl, _re.I) or _re.search(r'PRIMARY KEY\s*\(\s*[`"]?(\w+)', ddl, _re.I)
        if pkm:
            pk = pkm.group(1)
        uniques = _re.findall(r'UNIQUE(?:\s+INDEX|\s+KEY)?[^\n(]*\(\s*[`"]?(\w+)', ddl, _re.I)
        model[t] = {"cols": cols, "pk": pk, "uniques": uniques, "children": [], "ddl": ddl}
    # 2ª passada: FKs → filhos
    for t, ddl in tables.items():
        for m in _re.finditer(r'FOREIGN KEY\s*\(\s*[`"]?(\w+)[`"]?\s*\)\s*REFERENCES\s*[`"]?(\w+)', ddl, _re.I):
            fk_col, ref = m.group(1), m.group(2)
            if ref in model:
                # coluna de valor da filha = 1ª coluna que não é id/fk/técnica
                val_col = None
                for cn, _ct in model[t]["cols"]:
                    if cn in (fk_col, model[t]["pk"]) or cn in _TECH_COLS:
                        continue
                    val_col = cn; break
                model[ref]["children"].append((t, fk_col, val_col))
    return model


def _parse_schema_tables_full(schema_sql: str) -> Dict[str, str]:
    import re as _re
    tables: Dict[str, str] = {}
    if not schema_sql:
        return tables
    n = len(schema_sql); i = 0
    while i < n:
        m = _re.match(r'\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?\s*\(', schema_sql[i:], _re.I)
        if m:
            name = m.group(1); paren = i + m.end() - 1; depth = 1; j = paren + 1
            while j < n and depth > 0:
                if schema_sql[j] == '(': depth += 1
                elif schema_sql[j] == ')': depth -= 1
                j += 1
            end = schema_sql.find(';', j)
            if end < 0: end = n
            tables[name] = schema_sql[i:end+1].strip(); i = end + 1
        else:
            i += 1
    return tables


def _generate_crud_adapters(entities: List[str], schema_sql: str) -> str:
    """Gera listar_/obter_/atualizar_/excluir_<entidade>_deterministic pra cada
    entidade que existe no schema, com base nas colunas e tabelas filhas."""
    model = _schema_model(schema_sql)
    out_fns: List[str] = []
    names: List[str] = []
    conn_block = (
        "    import os, mysql.connector\n"
        "    conn = mysql.connector.connect(host=os.getenv('DB_HOST','localhost'),\n"
        "        port=int(os.getenv('DB_PORT','3306')), user=os.getenv('DB_USER','root'),\n"
        "        password=os.getenv('DB_PASSWORD',''), database=os.getenv('DB_NAME',''))\n"
    )
    seen = set()
    for ent in entities:
        if not ent or ent not in model or ent in seen:
            continue
        seen.add(ent)
        m = model[ent]
        pk = m["pk"]
        editable = [c for c, t in m["cols"] if c != pk and c not in _TECH_COLS]
        display = [pk] + [c for c in editable][:5]
        children = m["children"]

        # LISTAR
        cols_sql = ", ".join(display)
        listar = (
            f"def listar_{ent}_deterministic(input_data):\n"
            f"    \"\"\"Lista registros de {ent} (auto-gerado).\"\"\"\n"
            + conn_block +
            "    try:\n"
            "        cur = conn.cursor(dictionary=True)\n"
            f"        cur.execute(\"SELECT {cols_sql} FROM {ent} ORDER BY created_at DESC LIMIT 200\")\n"
            "        rows = cur.fetchall()\n"
            "        return {'rows': rows, 'total': len(rows)}\n"
            "    except Exception as _e:\n"
            "        return {'status':'erro','error':str(_e)}\n"
            "    finally:\n"
            "        try: cur.close()\n"
            "        except Exception: pass\n"
            "        conn.close()\n"
        )
        out_fns.append(listar); names.append(f"listar_{ent}")

        # CRIAR (main + filhos) — INSERT pai, captura id via SELECT, INSERTs filhos
        uniq = m["uniques"][0] if m["uniques"] else (editable[0] if editable else pk)
        ins_cols = ", ".join(editable)
        ins_ph = ", ".join(["%s"] * len(editable))
        ins_params = ", ".join(f"input_data.get('{c}')" for c in editable)
        child_ins = ""
        for ch, fk, val in children:
            if not val: continue
            child_ins += (
                f"        for _v in (input_data.get('{ch}') or []):\n"
                f"            cur.execute(\"INSERT INTO {ch}({fk}, {val}) VALUES(%s,%s)\", [_new_id, _v])\n"
            )
        criar = (
            f"def criar_{ent}_deterministic(input_data):\n"
            f"    \"\"\"Cria um registro de {ent} + filhos (auto-gerado).\"\"\"\n"
            + conn_block +
            "    try:\n"
            "        cur = conn.cursor(dictionary=True)\n"
            f"        cur.execute(\"INSERT INTO {ent}({ins_cols}) VALUES({ins_ph})\", [{ins_params}])\n"
            f"        cur.execute(\"SELECT {pk} AS id FROM {ent} WHERE {uniq}=%s ORDER BY created_at DESC LIMIT 1\", [input_data.get('{uniq}')])\n"
            "        _row = cur.fetchone(); _new_id = _row['id'] if _row else None\n"
            + child_ins +
            "        conn.commit()\n"
            f"        return {{'status':'sucesso','{pk}':_new_id}}\n"
            "    except Exception as _e:\n"
            "        conn.rollback(); return {'status':'erro','error':str(_e)}\n"
            "    finally:\n"
            "        try: cur.close()\n"
            "        except Exception: pass\n"
            "        conn.close()\n"
        )
        out_fns.append(criar); names.append(f"criar_{ent}")

        # OBTER (+ filhos)
        child_fetch = ""
        for ch, fk, val in children:
            if not val: continue
            child_fetch += (
                f"        cur.execute(\"SELECT {val} FROM {ch} WHERE {fk}=%s\", [_id])\n"
                f"        item['{ch}'] = [r['{val}'] for r in cur.fetchall()]\n"
            )
        obter = (
            f"def obter_{ent}_deterministic(input_data):\n"
            f"    \"\"\"Obtém um registro de {ent} + filhos (auto-gerado).\"\"\"\n"
            + conn_block +
            "    try:\n"
            "        cur = conn.cursor(dictionary=True)\n"
            f"        _id = input_data.get('{pk}') or input_data.get('id')\n"
            f"        cur.execute(\"SELECT * FROM {ent} WHERE {pk}=%s\", [_id])\n"
            "        item = cur.fetchone()\n"
            "        if not item: return {'status':'erro','error':'não encontrado'}\n"
            + child_fetch +
            "        return item\n"
            "    except Exception as _e:\n"
            "        return {'status':'erro','error':str(_e)}\n"
            "    finally:\n"
            "        try: cur.close()\n"
            "        except Exception: pass\n"
            "        conn.close()\n"
        )
        out_fns.append(obter); names.append(f"obter_{ent}")

        # ATUALIZAR (main + substitui filhos)
        set_clause = ", ".join(f"{c}=%s" for c in editable)
        set_params = ", ".join(f"input_data.get('{c}')" for c in editable)
        child_upd = ""
        for ch, fk, val in children:
            if not val: continue
            # nome da lista no input: usa o nome da tabela filha
            child_upd += (
                f"        cur.execute(\"DELETE FROM {ch} WHERE {fk}=%s\", [_id])\n"
                f"        for _v in (input_data.get('{ch}') or []):\n"
                f"            cur.execute(\"INSERT INTO {ch}({fk}, {val}) VALUES(%s,%s)\", [_id, _v])\n"
            )
        atualizar = (
            f"def atualizar_{ent}_deterministic(input_data):\n"
            f"    \"\"\"Atualiza {ent} e substitui filhos (auto-gerado).\"\"\"\n"
            + conn_block +
            "    try:\n"
            "        cur = conn.cursor(dictionary=True)\n"
            f"        _id = input_data.get('{pk}') or input_data.get('id')\n"
            f"        cur.execute(\"UPDATE {ent} SET {set_clause} WHERE {pk}=%s\", [{set_params}, _id])\n"
            + child_upd +
            "        conn.commit()\n"
            f"        return {{'status':'sucesso','{pk}':_id}}\n"
            "    except Exception as _e:\n"
            "        conn.rollback(); return {'status':'erro','error':str(_e)}\n"
            "    finally:\n"
            "        try: cur.close()\n"
            "        except Exception: pass\n"
            "        conn.close()\n"
        )
        out_fns.append(atualizar); names.append(f"atualizar_{ent}")

        # EXCLUIR (cascade cuida dos filhos)
        excluir = (
            f"def excluir_{ent}_deterministic(input_data):\n"
            f"    \"\"\"Exclui um registro de {ent} (auto-gerado; cascade nos filhos).\"\"\"\n"
            + conn_block +
            "    try:\n"
            "        cur = conn.cursor()\n"
            f"        _id = input_data.get('{pk}') or input_data.get('id')\n"
            f"        cur.execute(\"DELETE FROM {ent} WHERE {pk}=%s\", [_id])\n"
            "        conn.commit()\n"
            "        return {'status':'sucesso','excluidos':cur.rowcount}\n"
            "    except Exception as _e:\n"
            "        conn.rollback(); return {'status':'erro','error':str(_e)}\n"
            "    finally:\n"
            "        try: cur.close()\n"
            "        except Exception: pass\n"
            "        conn.close()\n"
        )
        out_fns.append(excluir); names.append(f"excluir_{ent}")

    if not out_fns:
        return ""
    header = (
        "\n\n# ─── CRUD determinístico completo por entidade (auto-gerado) ───\n"
        f"# Entidades: {', '.join(sorted(seen))}\n"
    )
    return header + "\n\n".join(out_fns) + "\n"


def _parse_task_description_to_python(desc: str) -> str:
    """Parses a task description's SQL steps and returns the Python body (indented
    with 8 spaces to fit inside ``try:`` of the wrapper). Returns "" if no SQL."""
    import re as _re
    lines_out: List[str] = []
    captured_vars: List[str] = []  # variable names bound by SELECT id captures

    # Split into logical "steps": lines that start with a number "N. " or bare SQL.
    # We rely on the v4 canonical format:
    #   query="..."
    #   params=[...]
    # Optionally preceded by "Para CADA <it> em {<lista>}:" for loops.
    query_re = _re.compile(r'query="([^"]+)"')
    params_re = _re.compile(r'params=\[([^\]]*)\]')
    loop_re = _re.compile(r'Para CADA\s+([\wÀ-ÿ]+)\s+em\s+\{(\w+)\}\s*:', _re.I | _re.U)
    capture_re = _re.compile(r'Guarde em\s+(\w+)', _re.I)

    # Normalize: work line-by-line, sliding a small state (inside a loop or not).
    raw_lines = desc.split("\n")
    i = 0
    n = len(raw_lines)
    while i < n:
        line = raw_lines[i]
        loop_m = loop_re.search(line)
        in_loop = False
        loop_item = None
        loop_list = None
        if loop_m:
            in_loop = True
            # Normalize accents so the emitted variable name is a valid Python
            # identifier that also matches the string used inside params=[...].
            _raw_item = loop_m.group(1)
            import unicodedata as _ud
            loop_item = _ud.normalize('NFKD', _raw_item).encode('ascii', 'ignore').decode('ascii')
            loop_list = loop_m.group(2)  # canais, problemas, ...
            i += 1  # move past the "Para CADA" line
            # skip lines until we find a query=
            while i < n and 'query=' not in raw_lines[i]:
                i += 1
            if i >= n:
                break

        # Now expect a query= line, then possibly a params= line
        query_m = query_re.search(raw_lines[i])
        if not query_m:
            i += 1
            continue
        query = query_m.group(1).strip()

        # Params: look on same line first, then next few lines
        params_str = ""
        params_m = params_re.search(raw_lines[i])
        if params_m:
            params_str = params_m.group(1)
        else:
            for j in range(i + 1, min(i + 4, n)):
                pm = params_re.search(raw_lines[j])
                if pm:
                    params_str = pm.group(1)
                    break

        # Detect a "Guarde em X" instruction — capture SELECT result as X
        capture_var = None
        for j in range(i, min(i + 5, n)):
            cm = capture_re.search(raw_lines[j])
            if cm:
                capture_var = cm.group(1)
                break

        py = _emit_sql_step(query, params_str, in_loop, loop_item, loop_list,
                            capture_var, captured_vars)
        if py:
            lines_out.extend(py)
        i += 1

    if not lines_out:
        return ""

    # Result envelope: if there's a captured id, expose it in _result along with status.
    result_parts = ["'status': 'sucesso'"]
    for v in captured_vars:
        result_parts.append(f"{v!r}: {v}")
    result_line = "        _result = {" + ", ".join(result_parts) + "}\n"

    body = "\n".join("        " + ln for ln in lines_out) + "\n" + result_line
    return body


def _emit_sql_step(query: str, params_str: str, in_loop: bool, loop_item: str,
                   loop_list: str, capture_var: str, captured_vars: List[str]) -> List[str]:
    """Emit Python lines for a single SQL step."""
    import re as _re
    query_lower = query.strip().lower()
    is_select = query_lower.startswith("select")

    # Build params Python expression list
    py_params = _translate_params(params_str, captured_vars, loop_item)

    lines: List[str] = []
    if in_loop and loop_list:
        lines.append(f"for {loop_item} in (input_data.get({loop_list!r}) or []):")
        indent = "    "
    else:
        indent = ""

    q_repr = repr(query)
    if py_params is not None:
        lines.append(f"{indent}cur.execute({q_repr}, {py_params})")
    else:
        lines.append(f"{indent}cur.execute({q_repr})")

    if is_select and capture_var:
        lines.append(f"{indent}_row = cur.fetchone()")
        lines.append(f"{indent}{capture_var} = _row['id'] if _row else None")
        if capture_var not in captured_vars:
            captured_vars.append(capture_var)

    return lines


def _translate_params(params_str: str, captured_vars: List[str], loop_item: str) -> str:
    """Turn ``{nome}, {descricao}, persona_id, canal`` into a Python list literal
    ``[input_data.get('nome'), input_data.get('descricao'), persona_id, canal]``."""
    if not params_str or not params_str.strip():
        return "[]"
    import re as _re
    parts = [p.strip() for p in params_str.split(",") if p.strip()]
    py_parts: List[str] = []
    for p in parts:
        m = _re.match(r'^\{(\w+)\}$', p)
        if m:
            key = m.group(1)
            py_parts.append(f"input_data.get({key!r})")
            continue
        if p in captured_vars or p == loop_item:
            py_parts.append(p)
            continue
        # Fallback: assume it's a python identifier already in scope; if it's
        # a string literal or number, keep as-is.
        py_parts.append(p)
    return "[" + ", ".join(py_parts) + "]"


def _inject_tools_into_agents_yaml(agents_yaml: str, agents_map: dict) -> str:
    """Injeta a lista de tools em cada agente do agents.yaml usando o mapping
    extraído do agent_task_spec. Sobrescreve `tools:` existente (comumente vazio
    ou incompleto quando vindo do LLM).
    """
    import re as _re
    if not agents_yaml or not agents_map:
        return agents_yaml

    try:
        import yaml as _yaml
        parsed = _yaml.safe_load(agents_yaml) or {}
    except Exception:
        # Se falhou parsear, retorna original
        return agents_yaml

    if not isinstance(parsed, dict):
        return agents_yaml

    changed = 0
    for agent_id, tools in agents_map.items():
        if agent_id in parsed and isinstance(parsed[agent_id], dict):
            # Só sobrescreve se yaml estava vazio ou com tools genéricas.
            current = parsed[agent_id].get("tools") or []
            new_tools = sorted(set(tools))
            if list(current) != new_tools:
                parsed[agent_id]["tools"] = new_tools
                changed += 1

    if changed == 0:
        return agents_yaml

    # Re-dump preservando ordem original das chaves
    try:
        return _yaml.safe_dump(
            parsed, sort_keys=False, allow_unicode=True, default_flow_style=False
        )
    except Exception:
        return agents_yaml


def _fix_common_tool_imports(tools_py: str) -> str:
    """LLM comumente escreve ``from crewai_tools import BaseTool`` — errado em
    versões atuais do CrewAI (BaseTool vive em ``crewai.tools``)."""
    import re as _re
    if not tools_py:
        return tools_py
    # Substitui import mal — se o LLM importou BaseTool de crewai_tools, troca
    # pra crewai.tools. Se tem outros nomes na mesma linha, preserva eles em
    # linha separada de crewai_tools.
    def _repl(m):
        items = [x.strip() for x in m.group(1).split(",") if x.strip()]
        has_basetool = "BaseTool" in items
        others = [x for x in items if x != "BaseTool"]
        lines = []
        if has_basetool:
            lines.append("from crewai.tools import BaseTool")
        if others:
            lines.append("from crewai_tools import " + ", ".join(others))
        return "\n".join(lines)
    tools_py = _re.sub(
        r"^from\s+crewai_tools\s+import\s+([^\n]+)$",
        _repl, tools_py, flags=_re.MULTILINE,
    )
    return tools_py


def _fix_pydantic_type_hint_typos(tools_py: str) -> str:
    """Corrige padrão inválido que o LLM comumente gera em classes BaseTool:
    ``field: "string"`` ou ``field: '''texto'''`` (sem ``str = ``). Pydantic
    tenta interpretar isso como forward reference e falha com SyntaxError.

    Também converte ``description: "..."`` sem ``str = `` no formato correto.
    """
    import re as _re
    if not tools_py:
        return tools_py

    # Padrão: campo com type hint que é literal string (aspas triplas ou simples/duplas)
    # e SEM ``= `` — sinal de que o LLM esqueceu o tipo e default.
    # Ex: ``description: """texto"""`` → ``description: str = """texto"""``
    lines = tools_py.split("\n")
    fields_to_str = ("name", "description")
    for i, ln in enumerate(lines):
        for field in fields_to_str:
            # ``    description: """xxx"""`` (aspas triplas) sem ``str = ``
            m = _re.match(rf"^(\s+){field}\s*:\s*(\"\"\"|''')", ln)
            if m:
                indent, quote = m.group(1), m.group(2)
                rest = ln[m.end():]
                lines[i] = f"{indent}{field}: str = {quote}{rest}"
                continue
            # ``    description: "xxx"`` (aspas simples ou duplas)
            m = _re.match(rf"^(\s+){field}\s*:\s*([\"'])", ln)
            if m and not _re.match(rf"^\s+{field}\s*:\s*(str|int|type\[)", ln):
                indent, quote = m.group(1), m.group(2)
                rest = ln[m.end():]
                # Só se a linha claramente é literal (termina com mesma aspa e sem `=`)
                if "=" not in ln[:m.end()]:
                    lines[i] = f"{indent}{field}: str = {quote}{rest}"
    return "\n".join(lines)


def _inject_real_database_tool(tools_py: str) -> str:
    """Substitui a classe DatabaseTool stub (se existir) por reexport do módulo real.

    O `database_tool.py` já injetado tem DatabaseTool + instância `database_tool`.
    Aqui removemos qualquer redefinição no tools.py pra evitar shadowing.
    """
    import re as _re
    if not tools_py:
        tools_py = ""

    # Remove classe DatabaseTool/DatabaseToolSchema se estiver no tools.py (stubs)
    # Padrão: "class DatabaseTool..." até próxima class/def de nível 0 ou fim
    def strip_class(src: str, class_name: str) -> str:
        pattern = rf"^class\s+{class_name}\b.*?(?=^(?:class|def|from|import|@|#\s*[-=])|\Z)"
        return _re.sub(pattern, "", src, flags=_re.MULTILINE | _re.DOTALL)

    tools_py = strip_class(tools_py, "DatabaseToolSchema")
    tools_py = strip_class(tools_py, "DatabaseTool")

    # Injeta import no TOPO absoluto — depois de docstring (se houver) mas antes
    # de qualquer código. Evita colocar dentro de try/except.
    import_line = "from database_tool import DatabaseTool, database_tool"
    if import_line not in tools_py:
        lines = tools_py.split("\n")
        insert_idx = 0
        # pula docstring inicial (aspas triplas em bloco)
        if lines and lines[0].lstrip().startswith(('"""', "'''")):
            quote = lines[0].lstrip()[:3]
            # docstring de 1 linha
            if lines[0].count(quote) >= 2:
                insert_idx = 1
            else:
                # multiline — acha a linha de fechamento
                for i in range(1, len(lines)):
                    if quote in lines[i]:
                        insert_idx = i + 1
                        break
        lines.insert(insert_idx, import_line)
        tools_py = "\n".join(lines)

    # No TOOL_REGISTRY (dict), garante que "database_tool": database_tool esteja lá
    if "TOOL_REGISTRY" in tools_py:
        # substitui referências antigas
        tools_py = _re.sub(
            r"['\"]database_tool['\"]\s*:\s*DatabaseTool\(\)",
            "'database_tool': database_tool",
            tools_py,
        )
    return tools_py


def _inject_tool_registry_stub(tools_py: str, all_tool_names: List[str]) -> str:
    """Garante que tools.py exporte TOOL_REGISTRY no final.

    Se o LLM já incluiu o dict, não duplica. Caso contrário, gera um stub que
    instancia (best-effort) classes detectadas no tools.py via heurística snake→Pascal,
    ou deixa registry vazio com aviso. O websocket_server faz getattr() com default {}.
    """
    if "TOOL_REGISTRY" in tools_py:
        return tools_py
    if not all_tool_names:
        return tools_py
    snake_to_pascal = lambda s: "".join(p.capitalize() for p in s.split("_"))
    entries = []
    for name in sorted(set(all_tool_names)):
        cls = snake_to_pascal(name)
        # Só inclui se a classe parece estar no tools_py (best-effort)
        if cls in tools_py:
            entries.append(f"        {name!r}: {cls}(),")
        else:
            # Fallback: registra None — websocket_server descarta None silenciosamente
            entries.append(f"        {name!r}: None,  # TODO: classe {cls} não detectada no tools.py")
    stub = "\n\n# ─── Registro automático de tools (best-effort) ───\ntry:\n    TOOL_REGISTRY = {\n"
    stub += "\n".join(entries)
    stub += "\n    }\n    TOOL_REGISTRY = {k: v for k, v in TOOL_REGISTRY.items() if v is not None}\nexcept Exception as _e:\n    TOOL_REGISTRY = {}\n    print(f'[tools] WARN: TOOL_REGISTRY skeleton falhou: {_e}')\n"
    return tools_py.rstrip() + "\n" + stub


def _autofill_tasks_yaml_agents(
    tasks_yaml: str,
    agents_yaml: str,
    agents_map: Dict[str, List[str]],
    tasks_map: Dict[str, List[str]],
) -> str:
    """Preenche o campo `agent:` em tasks que vieram sem ele.

    Estratégia (ordem):
      1. Mantém `agent:` se já existir e for válido.
      2. Tenta inferir pelo cruzamento de tools: agente cujo set de tools
         contém todas as tools da task.
      3. Heurística por nome: substring do task_id no agent_id.
      4. Fallback: primeiro agente listado em agents.yaml.
    Não bloqueia se o tasks.yaml for inválido — retorna o original.
    """
    if not tasks_yaml:
        return tasks_yaml
    try:
        tasks = yaml.safe_load(tasks_yaml) or {}
        agents = yaml.safe_load(agents_yaml) or {} if agents_yaml else {}
    except yaml.YAMLError:
        return tasks_yaml
    if not isinstance(tasks, dict):
        return tasks_yaml

    agent_ids = list(agents.keys()) if isinstance(agents, dict) else list(agents_map.keys())
    if not agent_ids:
        return tasks_yaml
    default_agent = agent_ids[0]

    def _pick_agent(task_id: str, task_tools: List[str]) -> str:
        task_tool_set = set(task_tools or [])
        # 2. melhor match por tools
        if task_tool_set:
            best, best_score = None, 0
            for aid in agent_ids:
                atools = set(agents_map.get(aid, []))
                score = len(task_tool_set & atools)
                if score > best_score:
                    best_score = score
                    best = aid
            if best:
                return best
        # 3. substring do task_id no agent_id (sem sufixo _agent)
        tid_low = task_id.lower()
        for aid in agent_ids:
            tag = aid.lower().replace("_agent", "")
            if tag and tag in tid_low:
                return aid
        # 4. fallback
        return default_agent

    changed = False
    for tid, cfg in tasks.items():
        if not isinstance(cfg, dict):
            continue
        existing = cfg.get("agent") or cfg.get("agent_id")
        if existing and existing in agent_ids:
            continue
        cfg["agent"] = _pick_agent(tid, tasks_map.get(tid, []))
        changed = True

    if not changed:
        return tasks_yaml
    return yaml.dump(tasks, sort_keys=False, allow_unicode=True)


def _slugify_project(name: str) -> str:
    """Slug ascii-safe: 'Quântica Comercial' → 'quantica-comercial'."""
    import re as _re_sl
    import unicodedata
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = _re_sl.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "projeto"


# Diretório dos templates visualtasksexec — frontend React + backend FastAPI + ws-server
_VTE_TEMPLATES_DIR = Path(__file__).parent / "templates" / "visualtasksexec"


def _render_visualtasksexec_templates(
    project_name: str,
    project_id: str,
    petri_net: Dict[str, Any],
    agents_yaml: str,
    tasks_yaml: str,
    *,
    ws_port: int = 5002,
    backend_port: int = 8001,
    frontend_port: int = 3001,
) -> List[Dict[str, str]]:
    """Lê o diretório de templates e devolve arquivos do pacote completo
    (frontend React + backend FastAPI + docker-compose + README).

    O ws-server fica num subdiretório, montado depois com os arquivos LLM
    (agents.yaml, tasks.yaml, tools.py, adapters.py, websocket_server.py).

    Cada arquivo .tpl tem extensão removida no destino. Placeholders:
      {{PROJECT_NAME}}, {{PROJECT_SLUG}}, {{PROJECT_ID}}
      {{WS_PORT}}, {{BACKEND_PORT}}, {{FRONTEND_PORT}}
    """
    if not _VTE_TEMPLATES_DIR.exists():
        return []

    project_slug = _slugify_project(project_name)

    # Builds the project.json that the backend serves
    import yaml as _yaml_for_render
    try:
        agents_list = list((_yaml_for_render.safe_load(agents_yaml) or {}).items())
    except Exception:
        agents_list = []
    try:
        tasks_list = list((_yaml_for_render.safe_load(tasks_yaml) or {}).items())
    except Exception:
        tasks_list = []

    project_json = {
        "id": project_id,
        "name": project_name,
        "description": f"Sistema agêntico gerado pelo LangNet — {project_name}",
        "petriNet": petri_net or {},
        "agents": [
            {"id": aid, "role": (cfg or {}).get("role", aid), "goal": (cfg or {}).get("goal", "")}
            for aid, cfg in agents_list
            if isinstance(cfg, dict) or cfg is None
        ],
        "tasks": [
            {
                "id": tid,
                "name": tid,
                "description": (cfg or {}).get("description", "")[:200] if isinstance(cfg, dict) else "",
                "agent": (cfg or {}).get("agent") if isinstance(cfg, dict) else None,
            }
            for tid, cfg in tasks_list
        ],
    }

    placeholders = {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_SLUG}}": project_slug,
        "{{PROJECT_ID}}": project_id,
        "{{WS_PORT}}": str(ws_port),
        "{{BACKEND_PORT}}": str(backend_port),
        "{{FRONTEND_PORT}}": str(frontend_port),
    }

    def _render(text: str) -> str:
        for k, v in placeholders.items():
            text = text.replace(k, v)
        return text

    out: List[Dict[str, str]] = []
    for path in sorted(_VTE_TEMPLATES_DIR.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(_VTE_TEMPLATES_DIR).as_posix()
        # arquivos .tpl perdem o sufixo no destino
        if rel.endswith(".tpl"):
            rel = rel[:-4]
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        content = _render(content)
        # detect language por extensão
        ext = rel.rsplit(".", 1)[-1].lower()
        lang = {
            "py": "python", "js": "javascript", "jsx": "jsx", "json": "json",
            "yml": "yaml", "yaml": "yaml", "html": "html", "md": "markdown",
            "txt": "text", "dockerfile": "dockerfile",
        }.get(ext, "text")
        if rel.endswith("Dockerfile") or rel.endswith("/Dockerfile"):
            lang = "dockerfile"
        out.append({"path": rel, "content": content, "language": lang})

    # Adiciona o project.json (lido pelo backend FastAPI)
    out.append({
        "path": "backend/project.json",
        "content": json.dumps(project_json, ensure_ascii=False, indent=2),
        "language": "json",
    })

    return out


def _build_project_templates(state: LangNetFullState, llm_files: Dict[str, Any]) -> List[Dict[str, str]]:
    """Monta a árvore completa de arquivos do projeto agêntico.

    - tools.py / adapters.py vêm do LLM (se ausentes, gera esqueletos).
    - main.py, websocket_server.py, requirements.txt, .env.example, docker-compose.yml,
      Dockerfile, README.md, agents.yaml, tasks.yaml, petri_net.json são templates.
    - AGENT_TOOLS / TASK_TOOLS são injetados deterministicamente parseando o
      agent_task_spec_document do state (coluna `| Tools |` em cada tabela).
    """
    project_name = state.get("project_name") or "Sistema Agêntico"
    ws_port = int(state.get("websocket_port") or 5002)
    agents_yaml = state.get("agents_yaml", "") or ""
    tasks_yaml = state.get("tasks_yaml", "") or ""
    petri_net = state.get("petri_net_data") or {}
    detected_tools: List[str] = llm_files.get("detected_tools", []) or []
    spec_md: str = state.get("agent_task_spec_document", "") or ""

    # Parse deterministic do agent_task_spec → bindings de tools
    binding = _parse_tools_from_spec(spec_md)
    agents_map = binding.get("agents", {})
    tasks_map = binding.get("tasks", {})
    all_tool_names: List[str] = sorted({
        t for tools in list(agents_map.values()) + list(tasks_map.values()) for t in tools
    })
    if all_tool_names:
        detected_tools = sorted(set(detected_tools) | set(all_tool_names))

    tools_py = (llm_files.get("tools_py") or "").strip() or _empty_tools_py(detected_tools)
    adapters_py = (llm_files.get("adapters_py") or "").strip() or _empty_adapters_py()

    # Corrige typo comum do LLM: ``field: "string"`` sem ``str = `` (quebra Pydantic).
    tools_py = _fix_common_tool_imports(tools_py)
    tools_py = _fix_pydantic_type_hint_typos(tools_py)

    # Injeta TOOL_REGISTRY no tools.py (se LLM não incluiu) e AGENT_TOOLS/TASK_TOOLS no adapters.py
    tools_py = _inject_tool_registry_stub(tools_py, all_tool_names)
    adapters_py = _inject_task_tools_into_adapters(adapters_py, agents_map, tasks_map)

    # Reescreve todos os `<task>_input_func` gerados pelo LLM pra sempre passar
    # o `state["input_data"]` como inputs do agente (evita hardcode/exemplo do LLM).
    adapters_py = _rewrite_input_funcs_pass_input_data(adapters_py)

    # Gera funções <task>_deterministic(input_data) parseando os passos SQL
    # canonicais das descriptions do tasks.yaml. O websocket_server chama
    # essas funções antes do agente CrewAI quando existem — modelos locais
    # como Qwen2.5-coder-32b travam depois de ~4 tool calls sequenciais em
    # cadeia, então CRUD determinístico em Python é a única forma robusta
    # de executar tasks de persistência em cascata.
    _det_snippet = _generate_deterministic_adapters(tasks_yaml)
    if _det_snippet:
        adapters_py = (adapters_py.rstrip() + "\n" + _det_snippet)

    # CRUD determinístico completo (listar/obter/atualizar/excluir) por entidade
    # das telas — permite telas ricas de cadastro (lista + novo + editar + excluir),
    # não só "salvar". Só gera pra entidades que existem no schema.
    _schema_sql_cg = state.get("data_model_schema_sql") or ""
    if not _schema_sql_cg:
        # tenta do ui_spec/state ou busca a mais recente do projeto
        try:
            from app.database import get_db_connection as _gdb2
            with _gdb2() as _c2:
                _cur2 = _c2.cursor(dictionary=True)
                _cur2.execute(
                    "SELECT schema_sql FROM data_model_sessions WHERE project_id=%s "
                    "AND schema_sql IS NOT NULL AND CHAR_LENGTH(schema_sql)>0 "
                    "ORDER BY created_at DESC LIMIT 1", (str(state.get('project_id') or ''),))
                _r2 = _cur2.fetchone()
                if _r2:
                    _schema_sql_cg = _r2["schema_sql"]
                _cur2.close()
        except Exception:
            pass
    _ui_spec_cg = state.get("ui_spec") or {}
    _entities = []
    for _s in (_ui_spec_cg.get("screens") or []):
        _e = _s.get("entity")
        if _e and _e not in _entities:
            _entities.append(_e)
    if _entities and _schema_sql_cg:
        _crud_snippet = _generate_crud_adapters(_entities, _schema_sql_cg)
        if _crud_snippet:
            adapters_py = adapters_py.rstrip() + "\n" + _crud_snippet

    # Injeta a lista de tools no agents.yaml — o LLM comumente deixa `tools: []`,
    # matando qualquer capacidade real do agente. Bindings vêm do agent_task_spec.
    agents_yaml = _inject_tools_into_agents_yaml(agents_yaml, agents_map)

    # Autofill 'agent:' nas tasks do tasks.yaml — sem isso o websocket_server
    # rejeita execute_task com "task sem agente vinculado"
    tasks_yaml = _autofill_tasks_yaml_agents(tasks_yaml, agents_yaml, agents_map, tasks_map)

    # Injeta placeholders Jinja {campo} + instrução de uso obrigatório das tools
    # nas descriptions das tasks — CrewAI só interpola os inputs do kickoff se
    # aparecem como {key} na description; e sem instrução mandatória o LLM
    # alucina "sucesso" sem chamar as tools.
    tasks_yaml = _inject_input_placeholders_in_task_descriptions(tasks_yaml, tasks_map)

    # Extrai task names do tasks.yaml para validar contra os place.task_name do LLM
    try:
        _tasks_parsed = yaml.safe_load(tasks_yaml) if tasks_yaml else {}
        known_task_names = list(_tasks_parsed.keys()) if isinstance(_tasks_parsed, dict) else []
    except Exception:
        known_task_names = []
    petri_with_logica = _build_petri_net_with_real_logica(petri_net, ws_port, known_task_names) if petri_net else {}

    files: List[Dict[str, str]] = []

    def add(path: str, content: str, language: str = "python"):
        files.append({"path": path, "content": content, "language": language})

    # ws-server: o componente Python+CrewAI+WebSocket (antes era a raiz do ZIP).
    # Agora vai como subdir 'ws-server/' do pacote visualtasksexec.
    add("ws-server/main.py", _template_main_py(project_name, ws_port))
    add("ws-server/websocket_server.py", _template_websocket_server_py(ws_port))
    add("ws-server/database_tool.py", _template_database_tool_py())
    # Injeta import do database_tool real e substitui classe stub se existir
    tools_py = _inject_real_database_tool(tools_py)
    add("ws-server/tools.py", tools_py if tools_py.endswith("\n") else tools_py + "\n")
    add("ws-server/adapters.py", adapters_py if adapters_py.endswith("\n") else adapters_py + "\n")
    if agents_yaml:
        add("ws-server/agents.yaml", agents_yaml if agents_yaml.endswith("\n") else agents_yaml + "\n", "yaml")
    if tasks_yaml:
        add("ws-server/tasks.yaml", tasks_yaml if tasks_yaml.endswith("\n") else tasks_yaml + "\n", "yaml")
    if petri_with_logica:
        add("ws-server/petri_net.json", json.dumps(petri_with_logica, ensure_ascii=False, indent=2), "json")
    add("ws-server/requirements.txt", _template_requirements_txt(_detect_extra_packages(tools_py)), "text")
    add("ws-server/.env.example", _template_env_example(detected_tools), "text")
    add("ws-server/Dockerfile", _template_dockerfile(), "dockerfile")

    # === Pacote visualtasksexec: frontend React + backend FastAPI + docker-compose ===
    project_id = state.get("project_id") or "default"
    vte_files = _render_visualtasksexec_templates(
        project_name=project_name,
        project_id=str(project_id),
        petri_net=petri_with_logica or petri_net or {},
        agents_yaml=agents_yaml or "",
        tasks_yaml=tasks_yaml or "",
        ws_port=ws_port,
        backend_port=8001,
        frontend_port=3001,
    )
    for f in vte_files:
        # README.md.tpl e docker-compose.yml.tpl vão pra raiz
        files.append(f)

    # === Cara A: telas de negócio reais a partir do ui_spec (se existir) ===
    # Gera componentes React por tela e SUBSTITUI o App.jsx do template para
    # que a UI de negócio seja a principal e o executor de Petri vire aba Admin.
    ui_spec = state.get("ui_spec") or {}
    if ui_spec and ui_spec.get("screens"):
        # schema pra montar telas CRUD ricas (mesma fonte do CRUD determinístico)
        _schema_for_ui = locals().get("_schema_sql_cg") or state.get("data_model_schema_sql") or ""
        # módulos das tasks (pra agrupar o menu lateral)
        _modules = _parse_task_modules(spec_md)
        screen_files = _generate_business_screens(ui_spec, ws_port, project_name, tasks_yaml,
                                                  schema_sql=_schema_for_ui, task_modules=_modules)
        # Remove o App.jsx do template (vamos sobrescrever)
        files = [f for f in files if f["path"] != "frontend/src/App.jsx"]
        files.extend(screen_files)

    return files


def _parse_task_modules(spec_md: str) -> Dict[str, str]:
    """Extrai {task_name: módulo} do agent_task_spec (coluna | **Módulo** | e | **Nome** |
    dentro de cada bloco #### T-...). Usado pra agrupar o menu lateral."""
    import re as _re
    modules: Dict[str, str] = {}
    if not spec_md:
        return modules
    for block in _re.split(r'(?=####\s+T-)', spec_md):
        if not block.startswith("####"):
            continue
        nm = _re.search(r'\|\s*\*\*Nome\*\*\s*\|\s*(\w+)\s*\|', block)
        md = _re.search(r'\|\s*\*\*M[oó]dulo\*\*\s*\|\s*([^|]+?)\s*\|', block)
        if nm and md:
            modules[nm.group(1)] = md.group(1).strip()
    return modules


def _norm_field(s: str) -> str:
    """Normaliza um nome de campo pra casar variações: minúsculas, sem acento,
    sem underscores e sem a stopword 'de' (gatilhos_de_compra ~ gatilhos_compra)."""
    import unicodedata as _ud
    s = _ud.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode("ascii").lower()
    s = s.replace("_de_", "_").replace("-", "_")
    toks = [t for t in s.split("_") if t and t != "de"]
    return "".join(toks)


_STOP_TOK = {"de", "do", "da", "o", "a", "e", "por", "com", "novamente", "automatico",
             "automatica", "automaticas", "automaticamente", "manualmente"}

def _tokens(s: str):
    """Tokens normalizados (sem acento, sem stopwords) pra casar nomes de task."""
    import unicodedata as _ud
    import re as _re
    s = _ud.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode("ascii").lower()
    raw = _re.split(r'[^a-z]+', s)
    out = []
    for t in raw:
        if not t or t in _STOP_TOK:
            continue
        # singulariza plural simples
        if len(t) > 4 and t.endswith("s"):
            t = t[:-1]
        out.append(t)
    return out


def _parse_task_input_fields(task_description: str) -> Dict[str, bool]:
    """Extrai os campos de input de uma task a partir da sua description canônica.
    Retorna {campo: is_list}. is_list=True quando aparece 'Para CADA x em {campo}'.
    Fonte de verdade dos nomes que o adapter/determinístico espera."""
    import re as _re
    fields: Dict[str, bool] = {}
    if not task_description:
        return fields
    # placeholders {campo}
    for m in _re.finditer(r'\{(\w+)\}', task_description):
        fields.setdefault(m.group(1), False)
    # listas: "Para CADA <item> em {<lista>}"
    for m in _re.finditer(r'Para CADA\s+[\wÀ-ÿ]+\s+em\s+\{(\w+)\}', task_description, _re.I | _re.U):
        fields[m.group(1)] = True
    return fields


# ─────────────────────────────────────────────────────────────────────
# Cara A — geração de telas React de negócio a partir do ui_spec
# ─────────────────────────────────────────────────────────────────────
def _pascal_case(s: str) -> str:
    import re as _re
    parts = _re.split(r'[^a-zA-Z0-9]+', s or "")
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "Screen"


def _classify_screen(screen: dict, entity_exists: bool) -> str:
    """Classifica a tela: crud | report | agent | form."""
    name = (screen.get("name", "") + " " + screen.get("id", "")).lower()
    layout = screen.get("layout", "form")
    if any(k in name for k in ("relat", "export")):
        return "report"
    if entity_exists and layout in ("form", "table", "detail"):
        return "crud"
    agent_kw = ("gerar", "gera ", "classific", "coletar", "coleta", "verific", "publicar",
                "publica", "identific", "sincroniz", "aprovar", "sugest", "revis", "monitor")
    if any(name.strip().startswith(k) or k in name for k in agent_kw) or layout in ("dashboard", "detail"):
        return "agent"
    return "form"


def _generate_business_screens(ui_spec: dict, ws_port: int, project_name: str, tasks_yaml: str = "",
                               schema_sql: str = "", task_modules: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
    """Emite os arquivos React das telas de negócio + wsClient + App shell.

    Cada tela é classificada e gera um componente rico conforme o tipo:
      - crud   → lista (tabela + Novo + Editar/Excluir) + formulário (Salvar/Cancelar)
      - report → filtros + tabela de resultados + Exportar
      - agent  → inputs + Executar com IA + painel de resultado formatado
      - form   → formulário simples (fallback)
    """
    out: List[Dict[str, str]] = []
    screens = ui_spec.get("screens", [])
    task_modules = task_modules or {}
    model = _schema_model(schema_sql) if schema_sql else {}

    # Mapa task_name → {campo: is_list} a partir das descriptions do tasks.yaml
    task_fields: Dict[str, Dict[str, bool]] = {}
    try:
        parsed = yaml.safe_load(tasks_yaml) if tasks_yaml else {}
        if isinstance(parsed, dict):
            for tname, cfg in parsed.items():
                if isinstance(cfg, dict):
                    task_fields[tname] = _parse_task_input_fields(cfg.get("description", "") or "")
    except Exception:
        pass

    def add(path, content, lang="javascript"):
        out.append({"path": path, "content": content if content.endswith("\n") else content + "\n", "language": lang})

    add("frontend/src/screens/wsClient.js", _template_ws_client(ws_port))

    comp_meta = []  # (id, name, comp_name, route, kind, module)
    for s in screens:
        comp_name = _pascal_case(s.get("id") or s.get("name") or "Screen")
        entity = s.get("entity")
        entity_exists = bool(entity and entity in model)
        kind = _classify_screen(s, entity_exists)
        # módulo: pela task alvo → módulo do agent_task_spec, senão heurística
        target = None
        for a in (s.get("actions") or []):
            if a.get("kind") in ("task", "crud") and a.get("target"):
                target = a["target"]; break
        module = task_modules.get(_resolve_module_task(target, task_modules)) if target else None
        module = module or _infer_module(s)

        if kind == "crud":
            src = _crud_screen(s, comp_name, entity, model.get(entity, {}))
        elif kind == "report":
            src = _report_screen(s, comp_name, task_fields)
        elif kind == "agent":
            src = _agent_screen(s, comp_name, task_fields)
        else:
            src = _react_component_for_screen(s, comp_name, task_fields)
        add(f"frontend/src/screens/{comp_name}.jsx", src)
        comp_meta.append((s.get("id"), s.get("name", comp_name), comp_name, s.get("route", "/"), kind, module))

    idx_lines = [f'export {{ default as {c} }} from "./{c}";' for _, _, c, _, _, _ in comp_meta]
    add("frontend/src/screens/index.js", "\n".join(idx_lines))
    add("frontend/src/App.jsx", _template_business_app(comp_meta, project_name))
    add("frontend/public/index.html", _template_business_index_html(project_name), "html")
    return out


def _resolve_module_task(target, task_modules):
    """Casa o alvo (às vezes inventado) com a task real do dict de módulos."""
    if not target:
        return target
    if target in task_modules:
        return target
    tset = set(_tokens(target))
    best, best_s = target, 0
    for real in task_modules:
        s = len(tset & set(_tokens(real)))
        if s > best_s:
            best, best_s = real, s
    return best if best_s >= 2 else target


_MODULE_KW = [
    ("Cadastros", ("persona", "usuario", "permiss", "pilar", "cadastr")),
    ("Conteúdo", ("calendario", "conteudo", "conteúdo", "tema", "sugest", "revis", "fato")),
    ("Publicação", ("agendar", "agendamento", "publica")),
    ("Engajamento", ("metric", "métric", "coment", "resposta", "lead", "engaj")),
    ("Relatórios", ("relat", "export")),
    ("Integrações", ("google", "calendar", "sincron", "ide")),
]

def _infer_module(screen: dict) -> str:
    name = (screen.get("name", "") + " " + screen.get("id", "")).lower()
    for mod, kws in _MODULE_KW:
        if any(k in name for k in kws):
            return mod
    return "Geral"


def _template_business_index_html(project_name: str) -> str:
    title = project_name.replace("<", "").replace(">", "")
    return (
        '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n'
        '  <meta charset="utf-8" />\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1" />\n'
        '  <meta name="theme-color" content="#4f46e5" />\n'
        '  <script src="https://cdn.tailwindcss.com"></script>\n'
        '  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />\n'
        '  <style>body{font-family:\'Inter\',sans-serif}</style>\n'
        f'  <title>{title}</title>\n'
        '</head>\n<body class="bg-slate-100">\n'
        '  <noscript>JavaScript precisa estar habilitado.</noscript>\n'
        '  <div id="root"></div>\n'
        '</body>\n</html>\n'
    )


def _template_ws_client(ws_port: int) -> str:
    return (
        'const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:' + str(ws_port) + '";\n\n'
        '// Dispara uma task no ws-server e resolve com o resultado (task_completed).\n'
        'export function runTask(taskName, inputData) {\n'
        '  return new Promise((resolve, reject) => {\n'
        '    let ws;\n'
        '    try { ws = new WebSocket(WS_URL); } catch (e) { reject(e); return; }\n'
        '    const timer = setTimeout(() => { try { ws.close(); } catch (e) {} reject(new Error("timeout")); }, 120000);\n'
        '    ws.onopen = () => ws.send(JSON.stringify({ type: "execute_task", data: { task_name: taskName, input_data: inputData || {} } }));\n'
        '    ws.onmessage = (ev) => {\n'
        '      let m; try { m = JSON.parse(ev.data); } catch (e) { return; }\n'
        '      if (m.type === "task_completed" || m.type === "task_result") {\n'
        '        clearTimeout(timer); ws.close(); resolve(m.data && m.data.result !== undefined ? m.data.result : (m.data || {}));\n'
        '      } else if (m.type === "error") {\n'
        '        clearTimeout(timer); ws.close(); reject(new Error((m.data && m.data.error) || "erro na task"));\n'
        '      }\n'
        '    };\n'
        '    ws.onerror = () => { clearTimeout(timer); reject(new Error("WebSocket error")); };\n'
        '  });\n'
        '}\n\n'
        '// Converte "a, b, c" em ["a","b","c"] (campos de lista → tabela filha)\n'
        'export function splitList(v) {\n'
        '  if (Array.isArray(v)) return v;\n'
        '  if (!v) return [];\n'
        '  return String(v).split(",").map((x) => x.trim()).filter(Boolean);\n'
        '}\n'
    )


def _resolve_task_target(target, task_fields):
    """Casa o alvo da ação (às vezes inventado pelo UI Spec) com a task real
    (chave em task_fields) por similaridade de tokens. Nível de módulo p/ reuso."""
    if not target or not task_fields:
        return target
    if target in task_fields:
        return target
    tnorm = _norm_field(target)
    best, best_score = None, 0
    for real in task_fields:
        rnorm = _norm_field(real)
        shared = len(set(_tokens(target)) & set(_tokens(real)))
        contains = 1 if (tnorm in rnorm or rnorm in tnorm) else 0
        score = shared * 2 + contains
        if score > best_score:
            best, best_score = real, score
    return best if best_score >= 2 else target


def _humanize(col: str) -> str:
    s = str(col or "").replace("_", " ").strip()
    return s[:1].upper() + s[1:] if s else col


def _crud_fields(entity_model: dict, screen: dict):
    """Descritores de campo (main cols editáveis + tabelas filhas) + colunas de lista."""
    pk = entity_model.get("pk", "id")
    cols = entity_model.get("cols", [])
    children = entity_model.get("children", [])
    coltype = {c: t for c, t in cols}
    editable = [c for c, t in cols if c != pk and c not in _TECH_COLS and t != "GEOMETRY"]
    # labels vindos do ui_spec (por nome normalizado)
    lab = {}
    for comp in (screen.get("components") or []):
        if comp.get("field") and comp.get("label"):
            lab[_norm_field(comp["field"])] = comp["label"]
    def label_for(k):
        return lab.get(_norm_field(k), _humanize(k))
    fields = []
    for c in editable:
        t = coltype.get(c, "VARCHAR")
        ftype = "textarea" if t in ("TEXT", "LONGTEXT") else ("date" if t in ("DATE", "DATETIME", "TIMESTAMP") else ("number" if t in ("INT", "BIGINT", "DECIMAL", "FLOAT", "DOUBLE", "TINYINT") else "text"))
        fields.append({"key": c, "label": label_for(c), "type": ftype, "list": False})
    for ch, fk, val in children:
        if not val:
            continue
        fields.append({"key": ch, "label": _humanize(ch), "type": "list", "list": True})
    display = [pk] + [f["key"] for f in fields if not f["list"]][:4]
    return fields, display, pk


_CRUD_BODY = r'''
const emptyForm = () => Object.fromEntries(FIELDS.map((f) => [f.key, ""]));

export default function %COMP%() {
  const [mode, setMode] = useState("list");
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState(emptyForm());
  const [editId, setEditId] = useState(null);
  const [busy, setBusy] = useState(false);
  const [confirmId, setConfirmId] = useState(null);
  const [err, setErr] = useState(null);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const load = async () => {
    try { const r = await runTask(T.list, {}); setRows((r && r.rows) || []); }
    catch (e) { setErr(e.message); }
  };
  useEffect(() => { load(); }, []);

  const novo = () => { setForm(emptyForm()); setEditId(null); setErr(null); setMode("form"); };
  const editar = async (id) => {
    setErr(null);
    try {
      const r = await runTask(T.get, { id });
      const f = emptyForm();
      FIELDS.forEach((fd) => { let v = r ? r[fd.key] : ""; if (Array.isArray(v)) v = v.join(", "); f[fd.key] = v == null ? "" : v; });
      setForm(f); setEditId(id); setMode("form");
    } catch (e) { setErr(e.message); }
  };
  const excluir = async (id) => {
    try { await runTask(T.del, { id }); setConfirmId(null); load(); }
    catch (e) { setErr(e.message); }
  };
  const salvar = async () => {
    setBusy(true); setErr(null);
    try {
      const payload = {};
      FIELDS.forEach((fd) => { payload[fd.key] = fd.list ? splitList(form[fd.key]) : form[fd.key]; });
      if (editId) { payload.id = editId; await runTask(T.update, payload); }
      else { await runTask(T.create, payload); }
      setMode("list"); load();
    } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  const IN = "w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none";

  return (
    <div className="max-w-6xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-slate-800">%TITLE%</h1>
          <p className="text-xs text-slate-400 mt-0.5">%SUBTITLE%</p>
        </div>
        {mode === "list" && (
          <button className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium shadow-sm hover:bg-indigo-700" onClick={novo}>＋ Novo</button>
        )}
      </div>
      {err && <div className="mb-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">⚠ {err}</div>}

      {mode === "list" && (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                {COLS.map((c) => <th key={c} className="text-left px-4 py-3 font-semibold">{c}</th>)}
                <th className="px-4 py-3 text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 && (
                <tr><td colSpan={COLS.length + 1} className="px-4 py-8 text-center text-slate-400">Nenhum registro. Clique em “＋ Novo”.</td></tr>
              )}
              {rows.map((row, i) => (
                <tr key={row.id || i} className="border-b border-slate-100 hover:bg-slate-50">
                  {COLS.map((c) => <td key={c} className="px-4 py-2.5 text-slate-700">{String(row[c] ?? "")}</td>)}
                  <td className="px-4 py-2.5 text-right whitespace-nowrap">
                    <button className="text-indigo-600 hover:underline mr-3" onClick={() => editar(row.id)}>Editar</button>
                    {confirmId === row.id ? (
                      <span>
                        <button className="text-red-600 font-medium mr-1" onClick={() => excluir(row.id)}>Confirmar</button>
                        <button className="text-slate-500" onClick={() => setConfirmId(null)}>✕</button>
                      </span>
                    ) : (
                      <button className="text-red-600 hover:underline" onClick={() => setConfirmId(row.id)}>Excluir</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {mode === "form" && (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-7 max-w-3xl">
          <h2 className="text-base font-semibold text-slate-700 mb-5">{editId ? "Editar registro" : "Novo registro"}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {FIELDS.map((fd) => (
              <div key={fd.key} className={fd.type === "textarea" ? "md:col-span-2" : ""}>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">{fd.label}</label>
                {fd.type === "textarea" ? (
                  <textarea className={IN} rows={2} value={form[fd.key]} onChange={(e) => set(fd.key, e.target.value)} />
                ) : fd.type === "list" ? (
                  <input className={IN} placeholder="separe por vírgula" value={form[fd.key]} onChange={(e) => set(fd.key, e.target.value)} />
                ) : (
                  <input type={fd.type === "number" ? "number" : fd.type === "date" ? "date" : "text"} className={IN} value={form[fd.key]} onChange={(e) => set(fd.key, e.target.value)} />
                )}
              </div>
            ))}
          </div>
          <div className="mt-6 pt-5 border-t border-slate-100 flex justify-end gap-2">
            <button className="px-4 py-2 rounded-lg border border-slate-300 text-slate-600 text-sm hover:bg-slate-50" onClick={() => setMode("list")}>Cancelar</button>
            <button className="px-5 py-2.5 rounded-lg bg-indigo-600 text-white text-sm font-medium shadow-sm hover:bg-indigo-700 disabled:opacity-60" disabled={busy} onClick={salvar}>{busy ? "Salvando…" : "Salvar"}</button>
          </div>
        </div>
      )}
    </div>
  );
}
'''


def _crud_screen(screen: dict, comp_name: str, entity: str, entity_model: dict) -> str:
    fields, display, pk = _crud_fields(entity_model, screen)
    T = {
        "list": f"listar_{entity}", "create": f"criar_{entity}",
        "update": f"atualizar_{entity}", "get": f"obter_{entity}", "del": f"excluir_{entity}",
    }
    header = (
        'import React, { useState, useEffect } from "react";\n'
        'import { runTask, splitList } from "./wsClient";\n\n'
        f'const T = {json.dumps(T)};\n'
        f'const FIELDS = {json.dumps(fields, ensure_ascii=False)};\n'
        f'const COLS = {json.dumps(display, ensure_ascii=False)};\n'
    )
    body = (_CRUD_BODY
            .replace("%COMP%", comp_name)
            .replace("%TITLE%", screen.get("name", comp_name).replace('"', ""))
            .replace("%SUBTITLE%", f"{'/'.join(screen.get('uc', []))} · cadastro"))
    return header + body


_AGENT_BODY = r'''
export default function %COMP%() {
  const [form, setForm] = useState(Object.fromEntries(INPUTS.map((f) => [f.key, ""])));
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const IN = "w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 outline-none";

  const executar = async () => {
    setBusy(true); setResult(null); setErr(null);
    try { const r = await runTask(TASK, form); setResult(r); }
    catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  const renderResult = (r) => {
    if (r == null) return null;
    if (typeof r === "string") return <p className="text-slate-700 whitespace-pre-wrap">{r}</p>;
    if (Array.isArray(r)) return <ul className="list-disc pl-5 text-slate-700">{r.map((x, i) => <li key={i}>{typeof x === "object" ? JSON.stringify(x) : String(x)}</li>)}</ul>;
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {Object.entries(r).map(([k, v]) => (
          <div key={k} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="text-xs text-slate-400 uppercase">{k}</div>
            <div className="text-sm text-slate-800 mt-0.5 break-words">{typeof v === "object" ? JSON.stringify(v) : String(v)}</div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-800">%TITLE%</h1>
        <p className="text-xs text-slate-400 mt-0.5">%SUBTITLE% · executado por agente de IA</p>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-7">
        {INPUTS.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-4">
            {INPUTS.map((fd) => (
              <div key={fd.key}>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">{fd.label}</label>
                <input className={IN} value={form[fd.key]} onChange={(e) => set(fd.key, e.target.value)} />
              </div>
            ))}
          </div>
        )}
        <div className="flex items-center gap-3">
          <button className="px-5 py-2.5 rounded-lg bg-indigo-600 text-white text-sm font-medium shadow-sm hover:bg-indigo-700 disabled:opacity-60 inline-flex items-center gap-2" disabled={busy} onClick={executar}>
            {busy && <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />}
            {busy ? "Executando com IA…" : "▷ Executar com IA"}
          </button>
          <span className="text-xs text-slate-400">Dispara o agente <code>{TASK}</code></span>
        </div>
      </div>
      {err && <div className="mt-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">⚠ {err}</div>}
      {result != null && (
        <div className="mt-5">
          <h3 className="text-sm font-semibold text-slate-600 mb-2">Resultado</h3>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">{renderResult(result)}</div>
        </div>
      )}
    </div>
  );
}
'''


def _agent_screen(screen: dict, comp_name: str, task_fields: dict) -> str:
    actions = screen.get("actions") or []
    target = None
    for a in actions:
        if a.get("kind") in ("task", "crud") and a.get("target"):
            target = a["target"]; break
    target = _resolve_task_target(target, task_fields)
    # inputs = componentes de entrada da tela
    inp = []
    for c in (screen.get("components") or []):
        if c.get("type") in ("text", "number", "date", "select", "multiselect", "textarea") and c.get("field"):
            inp.append({"key": c["field"], "label": c.get("label", _humanize(c["field"]))})
    header = (
        'import React, { useState } from "react";\n'
        'import { runTask } from "./wsClient";\n\n'
        f'const TASK = {json.dumps(target or screen.get("id"))};\n'
        f'const INPUTS = {json.dumps(inp, ensure_ascii=False)};\n'
    )
    body = (_AGENT_BODY.replace("%COMP%", comp_name)
            .replace("%TITLE%", screen.get("name", comp_name).replace('"', ""))
            .replace("%SUBTITLE%", "/".join(screen.get("uc", []))))
    return header + body


_REPORT_BODY = r'''
export default function %COMP%() {
  const [filtros, setFiltros] = useState(Object.fromEntries(FILTROS.map((f) => [f.key, ""])));
  const [rows, setRows] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const set = (k, v) => setFiltros((f) => ({ ...f, [k]: v }));
  const IN = "rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none";

  const gerar = async () => {
    setBusy(true); setErr(null); setRows(null);
    try {
      const r = await runTask(TASK, filtros);
      setRows(r && r.rows ? r.rows : (Array.isArray(r) ? r : (r ? [r] : [])));
    } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };
  const exportarCsv = () => {
    if (!rows || !rows.length) return;
    const cols = Object.keys(rows[0]);
    const csv = [cols.join(",")].concat(rows.map((r) => cols.map((c) => JSON.stringify(r[c] ?? "")).join(","))).join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = "%COMP%.csv"; a.click();
  };

  return (
    <div className="max-w-6xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-slate-800">%TITLE%</h1>
          <p className="text-xs text-slate-400 mt-0.5">%SUBTITLE% · relatório</p>
        </div>
        {rows && rows.length > 0 && (
          <button className="px-4 py-2 rounded-lg border border-slate-300 text-slate-600 text-sm hover:bg-slate-50" onClick={exportarCsv}>⭳ Exportar CSV</button>
        )}
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 mb-5 flex flex-wrap items-end gap-4">
        {FILTROS.map((fd) => (
          <div key={fd.key}>
            <label className="block text-xs font-medium text-slate-500 mb-1">{fd.label}</label>
            <input type={fd.type || "text"} className={IN} value={filtros[fd.key]} onChange={(e) => set(fd.key, e.target.value)} />
          </div>
        ))}
        <button className="px-5 py-2.5 rounded-lg bg-indigo-600 text-white text-sm font-medium shadow-sm hover:bg-indigo-700 disabled:opacity-60" disabled={busy} onClick={gerar}>{busy ? "Gerando…" : "Gerar relatório"}</button>
      </div>
      {err && <div className="mb-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">⚠ {err}</div>}
      {rows && (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          {rows.length === 0 ? (
            <div className="px-4 py-8 text-center text-slate-400">Sem dados para os filtros informados.</div>
          ) : (
            <table className="w-full text-sm">
              <thead><tr className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                {Object.keys(rows[0]).map((c) => <th key={c} className="text-left px-4 py-3 font-semibold">{c}</th>)}
              </tr></thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                    {Object.keys(rows[0]).map((c) => <td key={c} className="px-4 py-2.5 text-slate-700">{typeof r[c] === "object" ? JSON.stringify(r[c]) : String(r[c] ?? "")}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
'''


def _report_screen(screen: dict, comp_name: str, task_fields: dict) -> str:
    actions = screen.get("actions") or []
    target = None
    for a in actions:
        if a.get("kind") in ("task", "crud") and a.get("target"):
            target = a["target"]; break
    target = _resolve_task_target(target, task_fields)
    filt = []
    for c in (screen.get("components") or []):
        if c.get("type") in ("date", "select", "text", "number") and c.get("field"):
            filt.append({"key": c["field"], "label": c.get("label", _humanize(c["field"])),
                         "type": "date" if c.get("type") == "date" else "text"})
    if not filt:
        filt = [{"key": "periodo", "label": "Período", "type": "text"}]
    header = (
        'import React, { useState } from "react";\n'
        'import { runTask } from "./wsClient";\n\n'
        f'const TASK = {json.dumps(target or screen.get("id"))};\n'
        f'const FILTROS = {json.dumps(filt, ensure_ascii=False)};\n'
    )
    body = (_REPORT_BODY.replace("%COMP%", comp_name)
            .replace("%TITLE%", screen.get("name", comp_name).replace('"', ""))
            .replace("%SUBTITLE%", "/".join(screen.get("uc", []))))
    return header + body


def _react_component_for_screen(screen: dict, comp_name: str, task_fields: Optional[Dict[str, Dict[str, bool]]] = None) -> str:
    """Gera o componente funcional de UMA tela a partir da estrutura do ui_spec.

    Se a ação primária aponta pra uma task conhecida (task_fields), o payload é
    montado com os NOMES DE CAMPO REAIS DA TASK (fonte de verdade), casando com
    os componentes da tela por similaridade de nome. Isso evita divergência entre
    o nome que o LLM da UI escolheu e o nome que o adapter/determinístico lê.
    """
    task_fields = task_fields or {}
    name = screen.get("name", comp_name)
    layout = screen.get("layout", "form")
    components = screen.get("components", []) or []
    actions = screen.get("actions", []) or []

    # Campos que viram estado do form (input controlado)
    input_types = {"text", "textarea", "number", "date", "select", "multiselect", "checkbox"}
    fields = [c for c in components if c.get("type") in input_types and c.get("field")]
    readonly = [c for c in components if c.get("type") == "readonly" or c.get("type") == "table"]

    # Estado inicial
    init_state = ", ".join(f'{json.dumps(c["field"])}: ""' for c in fields)

    # Ação primária (task/crud). Pega a primeira com kind task/crud.
    primary = None
    for a in actions:
        if a.get("kind") in ("task", "crud") and a.get("target"):
            primary = a
            break

    # Índice de campos da tela por nome normalizado → nome do campo no form
    screen_by_norm = {_norm_field(c["field"]): c["field"] for c in fields}
    multiselect_norm = {_norm_field(c["field"]) for c in fields if c.get("type") == "multiselect"}

    # Resolve o alvo da ação (botão) pro nome REAL da task no tasks.yaml.
    # O UI Spec roda antes do tasks.yaml e às vezes inventa um nome de task que
    # não existe (ex.: "aprovar_calendario_mensal" vs real "gerar_calendario_mensal").
    # Casamos pelo nome mais próximo (similaridade normalizada) pra o botão apontar
    # pra uma task que de fato existe no servidor.
    def _resolve_task(target):
        if not target or not task_fields:
            return target
        if target in task_fields:
            return target
        tnorm = _norm_field(target)
        best, best_score = None, 0
        for real in task_fields:
            rnorm = _norm_field(real)
            # score por tokens compartilhados
            a = set(_tokens(target))
            b = set(_tokens(real))
            shared = len(a & b)
            # bônus se um contém o outro
            contains = 1 if (tnorm in rnorm or rnorm in tnorm) else 0
            score = shared * 2 + contains
            if score > best_score:
                best, best_score = real, score
        return best if best_score >= 2 else target

    payload_lines = []
    raw_target = primary.get("target") if primary else None
    target_task = _resolve_task(raw_target)
    if primary and target_task:
        primary["target"] = target_task  # usa o nome real no runTask
    tf = task_fields.get(target_task) if target_task else None
    if tf:
        for tfield, is_list in tf.items():
            norm = _norm_field(tfield)
            src = screen_by_norm.get(norm)  # campo correspondente na tela (se houver)
            src_expr = f'form[{json.dumps(src)}]' if src else '""'
            if is_list or norm in multiselect_norm:
                payload_lines.append(f'      {json.dumps(tfield)}: splitList({src_expr})')
            else:
                payload_lines.append(f'      {json.dumps(tfield)}: {src_expr}')
    else:
        # Sem task conhecida: usa os campos da tela como estão
        for c in fields:
            f = c["field"]
            if c.get("type") == "multiselect":
                payload_lines.append(f'      {json.dumps(f)}: splitList(form[{json.dumps(f)}])')
            else:
                payload_lines.append(f'      {json.dumps(f)}: form[{json.dumps(f)}]')
    payload_body = ",\n".join(payload_lines) if payload_lines else ""

    # ── JSX dos inputs (Tailwind) ──
    INPUT_CLS = "w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
    LABEL_CLS = "block text-sm font-medium text-slate-700 mb-1.5"
    jsx_fields = []
    for c in fields:
        f = c["field"]
        label = c.get("label", f)
        t = c.get("type")
        wide = ' className="md:col-span-2"' if t == "textarea" else ""
        if t == "textarea":
            ctrl = f'<textarea className="{INPUT_CLS}" rows={{2}} value={{form[{json.dumps(f)}]}} onChange={{(e) => set({json.dumps(f)}, e.target.value)}} />'
        elif t == "multiselect":
            ctrl = f'<input className="{INPUT_CLS}" placeholder="separe por vírgula" value={{form[{json.dumps(f)}]}} onChange={{(e) => set({json.dumps(f)}, e.target.value)}} />'
        elif t == "number":
            ctrl = f'<input type="number" className="{INPUT_CLS}" value={{form[{json.dumps(f)}]}} onChange={{(e) => set({json.dumps(f)}, e.target.value)}} />'
        elif t == "date":
            ctrl = f'<input type="date" className="{INPUT_CLS}" value={{form[{json.dumps(f)}]}} onChange={{(e) => set({json.dumps(f)}, e.target.value)}} />'
        else:
            ctrl = f'<input className="{INPUT_CLS}" value={{form[{json.dumps(f)}]}} onChange={{(e) => set({json.dumps(f)}, e.target.value)}} />'
        jsx_fields.append(
            f'          <div{wide}>\n'
            f'            <label className="{LABEL_CLS}">{label}</label>\n'
            f'            {ctrl}\n'
            f'          </div>'
        )
    jsx_fields_str = "\n".join(jsx_fields) if jsx_fields else '          <p className="text-slate-400 text-sm">Sem campos de entrada.</p>'

    # ── JSX dos readonly (cards de métrica) ──
    jsx_readonly = ""
    if readonly:
        cards = []
        for c in readonly:
            lbl = c.get("label", c.get("field", ""))
            cards.append(
                '          <div className="bg-white rounded-2xl border border-slate-200 p-5">\n'
                f'            <div className="text-xs text-slate-400 uppercase tracking-wide">{lbl}</div>\n'
                '            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>\n'
                '          </div>'
            )
        jsx_readonly = (
            '        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">\n'
            + "\n".join(cards) + '\n        </div>\n'
        )

    # ── Botão principal ──
    if primary:
        target = primary["target"]
        btn_label = primary.get("label", "Executar")
        action_fn = (
            '  const onPrimary = async () => {\n'
            '    setBusy(true); setResult(null); setErr(null);\n'
            '    try {\n'
            '      const payload = {\n' + payload_body + '\n      };\n'
            f'      const r = await runTask({json.dumps(target)}, payload);\n'
            '      setResult(r);\n'
            '    } catch (e) { setErr(e.message); } finally { setBusy(false); }\n'
            '  };\n'
        )
        primary_btn = (
            '        <div className="mt-6 pt-5 border-t border-slate-100 flex justify-end">\n'
            '          <button className="px-5 py-2.5 rounded-lg bg-indigo-600 text-white text-sm font-medium shadow-sm hover:bg-indigo-700 disabled:opacity-60" '
            f'disabled={{busy}} onClick={{onPrimary}}>{{busy ? "Processando…" : {json.dumps(btn_label)}}}</button>\n'
            '        </div>'
        )
    else:
        action_fn = '  const onPrimary = () => {};\n'
        primary_btn = ''

    subtitle = f"{'/'.join(screen.get('uc', []))} · {layout}"

    return (
        'import React, { useState } from "react";\n'
        'import { runTask, splitList } from "./wsClient";\n\n'
        f'export default function {comp_name}() {{\n'
        f'  const [form, setForm] = useState({{ {init_state} }});\n'
        '  const [result, setResult] = useState(null);\n'
        '  const [err, setErr] = useState(null);\n'
        '  const [busy, setBusy] = useState(false);\n'
        '  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));\n\n'
        + action_fn +
        '\n  return (\n'
        '    <div className="max-w-5xl">\n'
        '      <div className="mb-6">\n'
        f'        <h1 className="text-xl font-semibold text-slate-800">{name}</h1>\n'
        f'        <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>\n'
        '      </div>\n'
        '      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-7">\n'
        + jsx_readonly +
        '        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">\n'
        + jsx_fields_str + '\n'
        '        </div>\n'
        + (primary_btn + '\n' if primary_btn else '') +
        '      </div>\n'
        '      {err && <div className="mt-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">⚠ {err}</div>}\n'
        '      {result && <div className="mt-4 rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-3"><pre className="text-xs text-emerald-800 whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre></div>}\n'
        '    </div>\n'
        '  );\n'
        '}\n'
    )


_MODULE_ORDER = ["Cadastros", "Conteúdo", "Publicação", "Engajamento", "Relatórios", "Integrações", "Geral"]
_KIND_ICON = {"crud": "▦", "report": "▤", "agent": "✦", "form": "▧"}

def _template_business_app(comp_meta: list, project_name: str) -> str:
    """App shell: sidebar AGRUPADA por módulo (com subitens) + aba Admin (Petri)."""
    imports = "\n".join(f'import {{ {c} }} from "./screens";' for _, _, c, _, _, _ in comp_meta) if comp_meta else ""
    items = ",\n".join(
        f'  {{ id: {json.dumps(cid)}, label: {json.dumps(cname)}, Comp: {c}, kind: {json.dumps(kind)}, module: {json.dumps(module or "Geral")} }}'
        for cid, cname, c, _route, kind, module in comp_meta
    )
    return (
        'import React, { useEffect, useState } from "react";\n'
        'import MainExecutor from "./components/MainExecutor";\n'
        + imports + '\n\n'
        'const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";\n\n'
        'const SCREENS = [\n' + items + '\n];\n'
        f'const MODULE_ORDER = {json.dumps(_MODULE_ORDER, ensure_ascii=False)};\n'
        f'const KIND_ICON = {json.dumps(_KIND_ICON, ensure_ascii=False)};\n'
        f'const BRAND = {json.dumps(project_name, ensure_ascii=False)};\n\n'
        'function App() {\n'
        '  const [view, setView] = useState(SCREENS.length ? SCREENS[0].id : "admin");\n'
        '  const [project, setProject] = useState(null);\n'
        '  const [collapsed, setCollapsed] = useState({});\n\n'
        '  useEffect(() => {\n'
        '    fetch(`${BACKEND_URL}/api/projects`).then((r) => r.json()).then((d) => {\n'
        '      const p = (d.projects || [])[0];\n'
        '      if (p) fetch(`${BACKEND_URL}/api/projects/${p.id}`).then((r) => r.json()).then((x) => setProject(x.project));\n'
        '    }).catch(() => {});\n'
        '  }, []);\n\n'
        '  // agrupa telas por módulo, na ordem canônica\n'
        '  const groups = {};\n'
        '  SCREENS.forEach((s) => { (groups[s.module] = groups[s.module] || []).push(s); });\n'
        '  const orderedMods = MODULE_ORDER.filter((m) => groups[m]).concat(Object.keys(groups).filter((m) => !MODULE_ORDER.includes(m)));\n\n'
        '  const current = SCREENS.find((s) => s.id === view);\n'
        '  const itemCls = (active) => "px-4 py-2 cursor-pointer text-sm rounded-md mx-2 flex items-center gap-2 " + (active ? "bg-indigo-600 text-white font-medium" : "text-slate-300 hover:bg-slate-800");\n\n'
        '  return (\n'
        '    <div className="flex min-h-screen bg-slate-100" style={{fontFamily:"Inter,sans-serif"}}>\n'
        '      <aside className="w-64 bg-slate-900 flex flex-col shrink-0">\n'
        '        <div className="px-5 py-4 text-white font-bold text-base flex items-center gap-2 border-b border-slate-800">\n'
        '          <span className="w-7 h-7 rounded-lg bg-indigo-500 inline-flex items-center justify-center text-sm">{BRAND.slice(0,1)}</span>\n'
        '          {BRAND}\n'
        '        </div>\n'
        '        <nav className="mt-2 flex-1 overflow-y-auto pb-4">\n'
        '          {orderedMods.map((mod) => (\n'
        '            <div key={mod} className="mb-1">\n'
        '              <div className="px-4 py-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-500 flex items-center justify-between cursor-pointer select-none"\n'
        '                   onClick={() => setCollapsed((c) => ({ ...c, [mod]: !c[mod] }))}>\n'
        '                <span>{mod}</span><span className="text-slate-600">{collapsed[mod] ? "▸" : "▾"}</span>\n'
        '              </div>\n'
        '              {!collapsed[mod] && groups[mod].map((s) => (\n'
        '                <div key={s.id} className={itemCls(view === s.id)} onClick={() => setView(s.id)}>\n'
        '                  <span className="text-xs opacity-70">{KIND_ICON[s.kind] || "•"}</span>{s.label}\n'
        '                </div>\n'
        '              ))}\n'
        '            </div>\n'
        '          ))}\n'
        '          <div className="border-t border-slate-800 mt-2 pt-2">\n'
        '            <div className={itemCls(view === "admin")} onClick={() => setView("admin")}><span className="text-xs">⚙</span>Admin / Petri</div>\n'
        '          </div>\n'
        '        </nav>\n'
        '      </aside>\n'
        '      <main className="flex-1 p-8 overflow-auto">\n'
        '        {current && <current.Comp />}\n'
        '        {view === "admin" && (project ? <MainExecutor project={project} onBack={() => {}} /> : <p className="text-slate-400">Carregando projeto…</p>)}\n'
        '      </main>\n'
        '    </div>\n'
        '  );\n'
        '}\n\n'
        'export default App;\n'
    )


def _validate_generated_project(files: List[Dict[str, str]], state: LangNetFullState) -> List[str]:
    """Verifica coerência interna da árvore gerada e retorna list de warnings.

    Não bloqueia — só sinaliza. Cada warning é uma string curta no formato
    "<categoria>: <detalhe>" para exibir num banner na UI.

    Verificações:
    1. tools em TASK_TOOLS/AGENT_TOOLS existem em TOOL_REGISTRY?
    2. tasks em TASK_TOOLS existem em tasks.yaml?
    3. agentes em AGENT_TOOLS existem em agents.yaml?
    4. cada task de tasks.yaml tem <task>_input_func e <task>_output_func em adapters.py?
    5. place.agentId da Petri Net existe em agents.yaml?
    6. place.nome (após "Pronto para: X") referencia task que existe em tasks.yaml?
    """
    import re as _re
    warnings: List[str] = []

    by_path = {f["path"]: f.get("content", "") for f in files}
    tools_py = by_path.get("tools.py", "")
    adapters_py = by_path.get("adapters.py", "")
    agents_yaml = by_path.get("agents.yaml", "")
    tasks_yaml = by_path.get("tasks.yaml", "")
    petri_json = by_path.get("petri_net.json", "")

    # Parse top-level keys dos YAMLs (deterministic)
    def _yaml_top_keys(text: str) -> List[str]:
        try:
            data = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            return []
        return list(data.keys()) if isinstance(data, dict) else []

    agent_ids = set(_yaml_top_keys(agents_yaml))
    task_ids = set(_yaml_top_keys(tasks_yaml))

    # Extrai TOOL_REGISTRY keys do tools.py
    # Suporta:  TOOL_REGISTRY = {...}  e  TOOL_REGISTRY: Dict[...] = {...}
    tool_keys: set = set()
    reg_match = _re.search(r"TOOL_REGISTRY(?:\s*:\s*[^=]+)?\s*=\s*\{(.*?)\n\}", tools_py, _re.DOTALL)
    if reg_match:
        for m in _re.finditer(r"['\"]([a-zA-Z0-9_]+)['\"]\s*:", reg_match.group(1)):
            tool_keys.add(m.group(1))
    # Também captura linhas TOOL_REGISTRY["xxx"] = Yyy() fora do dict literal
    for m in _re.finditer(r"TOOL_REGISTRY\s*\[\s*['\"]([a-zA-Z0-9_]+)['\"]\s*\]\s*=", tools_py):
        tool_keys.add(m.group(1))

    # Extrai TASK_TOOLS / AGENT_TOOLS keys do adapters.py
    def _parse_str_list_dict(src: str, dict_name: str) -> Dict[str, List[str]]:
        m = _re.search(rf"{dict_name}\s*=\s*\{{([^}}]+)\}}", src, _re.DOTALL)
        if not m:
            return {}
        out: Dict[str, List[str]] = {}
        for entry in _re.finditer(r"['\"]([a-zA-Z0-9_]+)['\"]\s*:\s*\[(.*?)\]", m.group(1), _re.DOTALL):
            key = entry.group(1)
            items = _re.findall(r"['\"]([a-zA-Z0-9_]+)['\"]", entry.group(2))
            out[key] = items
        return out

    task_tools_map = _parse_str_list_dict(adapters_py, "TASK_TOOLS")
    agent_tools_map = _parse_str_list_dict(adapters_py, "AGENT_TOOLS")

    # 1. tools órfãs (em bindings mas não em TOOL_REGISTRY)
    referenced_tools: set = set()
    for tools in list(task_tools_map.values()) + list(agent_tools_map.values()):
        referenced_tools.update(tools)
    orphan_tools = sorted(referenced_tools - tool_keys)
    if orphan_tools:
        sample = ", ".join(orphan_tools[:6]) + (f" (+{len(orphan_tools) - 6} mais)" if len(orphan_tools) > 6 else "")
        warnings.append(
            f"tools_orphan: {len(orphan_tools)} tool(s) referenciada(s) em adapters.py mas ausente(s) em tools.TOOL_REGISTRY — {sample}"
        )

    # 2. tasks em TASK_TOOLS que não estão em tasks.yaml
    if task_ids:
        unknown_tasks = sorted(set(task_tools_map.keys()) - task_ids)
        if unknown_tasks:
            warnings.append(
                f"unknown_task_in_bindings: {len(unknown_tasks)} task_id em TASK_TOOLS sem definição em tasks.yaml — "
                + ", ".join(unknown_tasks[:6])
            )

    # 3. agentes em AGENT_TOOLS que não estão em agents.yaml
    if agent_ids:
        unknown_agents = sorted(set(agent_tools_map.keys()) - agent_ids)
        if unknown_agents:
            warnings.append(
                f"unknown_agent_in_bindings: {len(unknown_agents)} agent_id em AGENT_TOOLS sem definição em agents.yaml — "
                + ", ".join(unknown_agents[:6])
            )

    # 3.1. tasks.yaml: cada task tem `agent:` apontando para agent existente
    if task_ids and agent_ids:
        try:
            tasks_data = yaml.safe_load(tasks_yaml) or {}
        except yaml.YAMLError:
            tasks_data = {}
        tasks_without_agent: List[str] = []
        tasks_bad_agent: List[str] = []
        for tid, cfg in tasks_data.items() if isinstance(tasks_data, dict) else []:
            agent_ref = (cfg.get("agent") or cfg.get("agent_id")) if isinstance(cfg, dict) else None
            if not agent_ref:
                tasks_without_agent.append(tid)
            elif agent_ref not in agent_ids:
                tasks_bad_agent.append(f"{tid}→{agent_ref}")
        if tasks_without_agent:
            sample = ", ".join(tasks_without_agent[:6]) + (f" (+{len(tasks_without_agent) - 6} mais)" if len(tasks_without_agent) > 6 else "")
            warnings.append(
                f"task_missing_agent: {len(tasks_without_agent)} task(s) em tasks.yaml sem campo 'agent:' — {sample}"
            )
        if tasks_bad_agent:
            sample = ", ".join(tasks_bad_agent[:6])
            warnings.append(
                f"task_unknown_agent: {len(tasks_bad_agent)} task(s) referenciam agente ausente em agents.yaml — {sample}"
            )

    # 4. adapter functions ausentes
    if task_ids:
        missing_adapters: List[str] = []
        for tid in sorted(task_ids):
            if f"def {tid}_input_func" not in adapters_py:
                missing_adapters.append(f"{tid}_input_func")
            if f"def {tid}_output_func" not in adapters_py:
                missing_adapters.append(f"{tid}_output_func")
        if missing_adapters:
            sample = ", ".join(missing_adapters[:6]) + (f" (+{len(missing_adapters) - 6} mais)" if len(missing_adapters) > 6 else "")
            warnings.append(
                f"missing_adapters: {len(missing_adapters)} função(ões) ausente(s) em adapters.py — {sample}"
            )

    # 5 & 6. Petri Net coherence
    if petri_json:
        try:
            petri = json.loads(petri_json)
        except json.JSONDecodeError:
            petri = {}
        if isinstance(petri, dict):
            # 5. place.agentId existe?
            if agent_ids:
                bad_agent_refs: List[str] = []
                for lugar in petri.get("lugares", []) or []:
                    aid = lugar.get("agentId") if isinstance(lugar, dict) else None
                    if aid and aid not in agent_ids:
                        bad_agent_refs.append(f"{lugar.get('id')}→{aid}")
                if bad_agent_refs:
                    warnings.append(
                        f"petri_unknown_agent: {len(bad_agent_refs)} place(s) apontam para agentId fora de agents.yaml — "
                        + ", ".join(bad_agent_refs[:6])
                    )
            # 6. place.nome após "Pronto para: X" → X em tasks.yaml?
            if task_ids:
                bad_task_refs: List[str] = []
                for lugar in petri.get("lugares", []) or []:
                    if not isinstance(lugar, dict):
                        continue
                    nome = (lugar.get("nome") or "").strip()
                    m = _re.match(r"(?:pronto para|aguardando)\s*[:\-]\s*([a-zA-Z0-9_]+)", nome, _re.IGNORECASE)
                    if m and m.group(1) not in task_ids:
                        bad_task_refs.append(f"{lugar.get('id')}→{m.group(1)}")
                if bad_task_refs:
                    warnings.append(
                        f"petri_unknown_task: {len(bad_task_refs)} place(s) referenciam task fora de tasks.yaml — "
                        + ", ".join(bad_task_refs[:6])
                    )

    # 7. missing_runtime_dep: imports do tools.py que não estão em
    # requirements.txt E não estão disponíveis no env conda langnet.
    # (descoberto empiricamente no SPRINT4: import PyPDF2 sem entrada no req)
    if tools_py:
        # Stdlib do Python 3.11 — não precisa estar em requirements
        STDLIB = {
            "abc", "argparse", "array", "ast", "asyncio", "base64", "binascii",
            "builtins", "calendar", "collections", "concurrent", "configparser",
            "contextlib", "copy", "csv", "ctypes", "dataclasses", "datetime",
            "decimal", "difflib", "email", "enum", "errno", "fnmatch", "functools",
            "gc", "glob", "gzip", "hashlib", "heapq", "hmac", "html", "http",
            "imaplib", "importlib", "inspect", "io", "ipaddress", "itertools",
            "json", "logging", "math", "mimetypes", "multiprocessing", "operator",
            "os", "pathlib", "pickle", "pkgutil", "platform", "pprint", "queue",
            "random", "re", "secrets", "shutil", "signal", "smtplib", "socket",
            "socketserver", "sqlite3", "ssl", "stat", "string", "struct",
            "subprocess", "sys", "sysconfig", "tarfile", "tempfile", "textwrap",
            "threading", "time", "timeit", "token", "tokenize", "traceback",
            "types", "typing", "unittest", "urllib", "uuid", "warnings",
            "weakref", "xml", "xmlrpc", "zipfile", "zipimport", "zlib",
        }

        # Extrai top-level imports do tools.py (1ª palavra após import/from)
        import_lines = _re.findall(
            r"(?:^|\n)\s*(?:from\s+([a-zA-Z0-9_]+)|import\s+([a-zA-Z0-9_]+))",
            tools_py,
        )
        imports: List[str] = sorted({(a or b) for a, b in import_lines if (a or b)})

        # Parse requirements.txt: extrai nome do pacote antes de qualquer comparador
        req_txt = by_path.get("requirements.txt", "") or ""
        req_names = set()
        for line in req_txt.splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            # pacote pode ser "X>=1", "X==1", "X[extras]", "X<2,>=1"
            m = _re.match(r"([A-Za-z0-9_.\-]+)", line)
            if m:
                req_names.add(m.group(1).lower().replace("_", "-"))

        # Mapeamento conhecido: nome do import → nome do pacote pip
        # (preferimos detectar overrides comuns; senão usamos o próprio nome)
        IMPORT_TO_PKG = {
            "PIL": "pillow", "cv2": "opencv-python", "yaml": "pyyaml",
            "dotenv": "python-dotenv", "jose": "python-jose", "docx": "python-docx",
            "googleapiclient": "google-api-python-client", "telegram": "python-telegram-bot",
            "magic": "python-magic", "sklearn": "scikit-learn", "skimage": "scikit-image",
            "bs4": "beautifulsoup4", "Crypto": "pycryptodome", "MySQLdb": "mysqlclient",
            "pymongo": "pymongo", "redis": "redis", "psycopg2": "psycopg2-binary",
            "win32com": "pywin32",
        }

        # Verifica disponibilidade no env conda langnet (importlib.util.find_spec
        # rodando em subprocess para usar O python do env, não o do backend)
        env_python = "/home/pasteurjr/miniconda3/envs/langnet/bin/python"
        missing_from_req: List[str] = []
        missing_from_env: List[str] = []
        for imp in imports:
            if imp in STDLIB or imp.lower() in STDLIB:
                continue
            pkg = IMPORT_TO_PKG.get(imp, imp).lower().replace("_", "-")
            # check requirements.txt
            in_req = pkg in req_names or imp.lower().replace("_", "-") in req_names
            if not in_req:
                missing_from_req.append(imp)
            # check env (best-effort, só se backend tem acesso ao env)
            try:
                import subprocess as _sp
                if Path(env_python).exists():
                    r = _sp.run(
                        [env_python, "-c", f"import importlib.util; print(1 if importlib.util.find_spec({imp!r}) else 0)"],
                        capture_output=True, text=True, timeout=5,
                    )
                    if r.returncode == 0 and r.stdout.strip() == "0":
                        missing_from_env.append(imp)
            except Exception:
                pass  # silencioso — env check é opcional

        if missing_from_req:
            sample = ", ".join(missing_from_req[:6]) + (f" (+{len(missing_from_req) - 6})" if len(missing_from_req) > 6 else "")
            warnings.append(
                f"missing_runtime_dep: {len(missing_from_req)} import(s) em tools.py sem entrada em requirements.txt — {sample}"
            )
        if missing_from_env:
            sample = ", ".join(missing_from_env[:6]) + (f" (+{len(missing_from_env) - 6})" if len(missing_from_env) > 6 else "")
            warnings.append(
                f"missing_runtime_env: {len(missing_from_env)} import(s) em tools.py ausente(s) no env conda langnet — {sample}"
            )

    return warnings


def generate_code_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Adapter que extrai tools.py/adapters.py do LLM e monta a árvore completa
    do projeto Python agêntico via templates."""
    import re as _re

    def _extract(obj: Any) -> str:
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            for k in ("team_result", "raw_output", "raw", "output", "final_output", "result"):
                if k in obj:
                    return _extract(obj[k])
            return json.dumps(obj)
        return getattr(obj, "raw", None) or str(obj)

    output_json = _extract(result)

    def _parse(s: str) -> Dict[str, Any]:
        try:
            return json.loads(s)
        except (json.JSONDecodeError, TypeError):
            pass
        fence = _re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, _re.DOTALL)
        if fence:
            try:
                return json.loads(fence.group(1))
            except json.JSONDecodeError:
                pass
        outer = _re.search(r"\{.*\}", s, _re.DOTALL)
        if outer:
            try:
                return json.loads(outer.group(0))
            except json.JSONDecodeError:
                return {}
        return {}

    llm_files = _parse(output_json) if isinstance(output_json, str) else (output_json or {})
    if not isinstance(llm_files, dict):
        llm_files = {}

    files = _build_project_templates(state, llm_files)
    print(f"[CODE GEN] generated {len(files)} files: {[f['path'] for f in files]}")

    warnings = _validate_generated_project(files, state)
    if warnings:
        print(f"[CODE GEN] {len(warnings)} validation warning(s):")
        for w in warnings:
            print(f"  ⚠ {w}")

    updated_state = {
        **state,
        "code_generation_json": json.dumps({"files": files}, ensure_ascii=False),
        "generated_files_list": files,
        "validation_warnings": warnings,
    }
    return log_task_complete(updated_state, "generate_python_code")


# =============================================================================
# SPECIFICATION PIPELINE OUTPUT FUNCTIONS
# =============================================================================

def _extract_crewai_result(result: Any) -> str:
    """Helper to extract raw output from CrewAI result"""
    raw_output = ""

    if hasattr(result, 'raw'):
        raw_output = result.raw
    elif hasattr(result, 'json_dict') and result.json_dict:
        return json.dumps(result.json_dict)
    elif hasattr(result, 'model_dump'):
        return json.dumps(result.model_dump())
    elif isinstance(result, dict):
        # Check if it's the new CrewAI format with 'team_result'
        if 'team_result' in result:
            raw_output = result['team_result']
        else:
            return json.dumps(result)
    else:
        raw_output = str(result)

    # Remove markdown code fences if present
    if isinstance(raw_output, str):
        # Remove ```json ... ``` wrappers
        import re
        raw_output = re.sub(r'^```json\s*\n', '', raw_output)
        raw_output = re.sub(r'\n```\s*$', '', raw_output)
        raw_output = re.sub(r'^```\s*\n', '', raw_output)  # Also handle plain ``` without json

    return raw_output


def classify_specification_intent_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with classify_specification_intent results (Router)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {"intent": "create", "scope": "functional_spec"}

    updated_state = {
        **state,
        "spec_classification_json": output_json,
        "spec_intent": parsed.get("intent", "create"),
        "spec_scope": parsed.get("scope", "functional_spec"),
        "spec_target_sections": parsed.get("target_sections", list(range(1, 15))),
        "spec_estimated_complexity": parsed.get("estimated_complexity", "medium")
    }

    return log_task_complete(updated_state, "classify_specification_intent", output_json[:200])


def extract_specification_entities_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with extract_specification_entities results (EntityExtractor)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_entities_json": output_json,
        "spec_actors": parsed.get("actors", []),
        "spec_functional_requirements": parsed.get("functional_requirements", []),
        "spec_non_functional_requirements": parsed.get("non_functional_requirements", []),
        "spec_use_cases": parsed.get("use_cases", []),
        "spec_business_rules": parsed.get("business_rules", []),
        "spec_data_entities": parsed.get("data_entities", []),
        "spec_apis": parsed.get("apis", []),
        "spec_workflows": parsed.get("workflows", []),
        "spec_gaps": parsed.get("gaps", []),
        "spec_extraction_summary": parsed.get("extraction_summary", {})
    }

    return log_task_complete(updated_state, "extract_specification_entities", output_json[:200])


def research_specification_context_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for research_specification_context task (WebResearcher)"""
    return {
        "entities_json": state.get("spec_entities_json", "{}"),
        "project_name": state.get("project_name", "Sistema")
    }


def research_specification_context_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with research_specification_context results (WebResearcher)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_research_context_json": output_json,
        "spec_technical_standards": parsed.get("technical_standards", []),
        "spec_compliance_requirements": parsed.get("compliance_requirements", []),
        "spec_best_practices": parsed.get("best_practices", []),
        "spec_reference_architectures": parsed.get("reference_architectures", []),
        "spec_research_summary": parsed.get("research_summary", {})
    }

    return log_task_complete(updated_state, "research_specification_context", output_json[:200])


def compose_spec_use_cases_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with compose_spec_use_cases results - use cases for section 5"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_use_cases_json": output_json,
        "spec_use_cases": parsed.get("use_cases", []),
        "spec_use_cases_count": parsed.get("use_cases_count", 0),
        "spec_use_cases_with_min_steps": parsed.get("use_cases_with_min_steps", 0),
        "spec_actors_identified": parsed.get("actors_identified", []),
        "spec_uc_gaps": parsed.get("gaps", [])
    }

    return log_task_complete(updated_state, "compose_spec_use_cases", output_json[:200])


def compose_spec_document_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with compose_spec_document results - sections 1-4 and 6-14"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    document_md = parsed.get("document_md", "")

    updated_state = {
        **state,
        "spec_draft_sections_json": output_json,
        "spec_draft_document_md": document_md,
        "spec_sections": parsed.get("sections", []),
        "spec_business_rules_count": parsed.get("business_rules_count", 0),
        "spec_generation_gaps": parsed.get("gaps", []),
        "spec_generation_summary": parsed.get("generation_summary", {})
    }

    return log_task_complete(updated_state, "compose_spec_document", output_json[:200])


def verify_specification_grounding_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with verify_specification_grounding results (Verifier)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    verification_summary = parsed.get("verification_summary", {})

    updated_state = {
        **state,
        "spec_verification_json": output_json,
        "spec_verified_items": parsed.get("verified_items", []),
        "spec_verification_issues": parsed.get("issues", {}),
        "spec_actions_recommended": parsed.get("actions_recommended", []),
        "spec_grounding_score": verification_summary.get("grounding_score", 0),
        "spec_verification_summary": verification_summary
    }

    return log_task_complete(updated_state, "verify_specification_grounding", output_json[:200])


def validate_specification_compliance_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with validate_specification_compliance results (Compliance)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_compliance_json": output_json,
        "spec_compliance_ok": parsed.get("compliance_ok", False),
        "spec_compliance_violations": parsed.get("violations", []),
        "spec_checks_passed": parsed.get("checks_passed", {}),
        "spec_compliance_score": parsed.get("compliance_score", 0),
        "spec_corrections_needed": parsed.get("corrections_needed", []),
        "spec_minimum_requirements_check": parsed.get("minimum_requirements_check", {})
    }

    return log_task_complete(updated_state, "validate_specification_compliance", output_json[:200])


def apply_spec_corrections_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with apply_spec_corrections results - corrected sections"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_corrected_sections_json": output_json,
        "spec_corrected_sections": parsed.get("corrected_sections", []),
        "spec_corrections_applied": parsed.get("corrections_applied", []),
        "spec_grounding_score": parsed.get("grounding_score", 0),
        "spec_compliance_score": parsed.get("compliance_score", 0),
        "spec_remaining_gaps": parsed.get("remaining_gaps", [])
    }

    return log_task_complete(updated_state, "apply_spec_corrections", output_json[:200])


def render_final_specification_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with render_final_specification results - final document"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    document_md = parsed.get("document_md", "")
    metadata = parsed.get("metadata", {})

    updated_state = {
        **state,
        "spec_final_json": output_json,
        "spec_status": parsed.get("status", "failed"),
        "spec_document_md": document_md,
        "spec_final_gaps": parsed.get("gaps", []),
        "spec_warnings": parsed.get("warnings", []),
        "spec_metadata": metadata,
        "spec_grounding_score_final": metadata.get("grounding_score", 0),
        "spec_compliance_score_final": metadata.get("compliance_score", 0),
        "spec_total_sections": metadata.get("total_sections", 0),
        "spec_complete_sections": metadata.get("complete_sections", 0)
    }

    return log_task_complete(updated_state, "render_final_specification", output_json[:200])


# ============================================================================
# TASK REGISTRY (Maps task names to configurations)
# ============================================================================

TASK_REGISTRY = {
    "analyze_document": {
        "input_func": analyze_document_input_func,
        "output_func": analyze_document_output_func,
        "requires": [],
        "produces": ["document_content", "document_structure", "document_metadata"],
        "agent": AGENTS["document_analyst"],
        "tools": [LANGNET_TOOLS["document_reader"]],
        "phase": "document_analysis"
    },
    "extract_requirements": {
        "input_func": extract_requirements_input_func,
        "output_func": extract_requirements_output_func,
        "requires": ["document_content"],
        "produces": ["requirements_json", "requirements_data"],
        "agent": AGENTS["requirements_engineer"],
        "tools": [],
        "phase": "requirements_extraction"
    },
    "research_additional_info": {
        "input_func": research_additional_info_input_func,
        "output_func": research_additional_info_output_func,
        "requires": ["requirements_json"],
        "produces": ["research_findings_json", "research_findings_data"],
        "agent": AGENTS["web_researcher"],
        "tools": [
            LANGNET_TOOLS["serpapi_search"],  # DuckDuckGo for general searches
            LANGNET_TOOLS["tavily_search"],   # Tavily for deep research
            LANGNET_TOOLS["serper_search"]    # Google for specific/regulatory info
        ],
        "phase": "requirements_extraction"
    },
    "enrich_requirements": {
        "input_func": enrich_requirements_input_func,
        "output_func": enrich_requirements_output_func,
        "requires": ["requirements_json", "research_findings_json"],
        "produces": ["enriched_requirements", "validation_status"],
        "agent": AGENTS["requirements_validator"],
        "tools": [],
        "phase": "requirements_extraction"
    },
    "validate_quality": {
        "input_func": validate_quality_input_func,
        "output_func": validate_quality_output_func,
        "requires": ["enriched_requirements"],
        "produces": ["quality_validation", "quality_scores"],
        "agent": AGENTS["requirements_validator"],
        "tools": [],
        "phase": "requirements_extraction"
    },
    "generate_document": {
        "input_func": generate_document_input_func,
        "output_func": generate_document_output_func,
        "requires": ["enriched_requirements", "quality_validation"],
        "produces": ["requirements_document_md", "validation_data"],
        "agent": AGENTS["requirements_validator"],
        "tools": [],
        "phase": "requirements_extraction"
    },
    "generate_specification": {
        "input_func": generate_specification_input_func,
        "output_func": generate_specification_output_func,
        "requires": ["validation_data"],
        "produces": ["specification_md", "specification_data"],
        "agent": AGENTS["specification_generator"],
        "tools": [LANGNET_TOOLS["markdown_writer"]],
        "phase": "requirements_extraction"
    },
    "suggest_agents": {
        "input_func": suggest_agents_input_func,
        "output_func": suggest_agents_output_func,
        "requires": ["requirements_json", "specification_data"],
        "produces": ["agents_suggestions_json", "agents_data"],
        "agent": AGENTS["agent_specifier"],
        "tools": [],
        "phase": "agent_design"
    },
    "decompose_tasks": {
        "input_func": decompose_tasks_input_func,
        "output_func": decompose_tasks_output_func,
        "requires": ["requirements_json", "agents_data"],
        "produces": ["tasks_decomposition_json", "tasks_data", "dependencies"],
        "agent": AGENTS["task_decomposer"],
        "tools": [],
        "phase": "agent_design"
    },
    "design_petri_net": {
        "input_func": design_petri_net_input_func,
        "output_func": design_petri_net_output_func,
        "requires": ["tasks_data", "dependencies", "agents_data"],
        "produces": ["petri_net_json", "petri_net_data"],
        "agent": AGENTS["petri_net_designer"],
        "tools": [],
        "phase": "workflow_design"
    },
    "generate_yaml_files": {
        "input_func": generate_yaml_input_func,
        "output_func": generate_yaml_output_func,
        "requires": ["agents_data", "tasks_data"],
        "produces": ["agents_yaml", "tasks_yaml"],
        "agent": AGENTS["yaml_generator"],
        "tools": [LANGNET_TOOLS["yaml_writer"], LANGNET_TOOLS["yaml_validator"]],
        "phase": "code_generation"
    },
    "generate_python_code": {
        "input_func": generate_code_input_func,
        "output_func": generate_code_output_func,
        "requires": ["agents_yaml", "tasks_yaml", "petri_net_data"],
        "produces": ["generated_code", "generated_files"],
        "agent": AGENTS["code_generator"],
        "tools": [LANGNET_TOOLS["python_code_writer"]],
        "phase": "code_generation"
    },

    # =========================================================================
    # SPECIFICATION GENERATION PIPELINE (Multi-Step following Generative Computing)
    # =========================================================================

    "classify_specification_intent": {
        "input_func": classify_specification_intent_input_func,
        "output_func": classify_specification_intent_output_func,
        "requires": ["requirements_document"],
        "produces": ["spec_classification_json", "spec_intent", "spec_scope", "spec_target_sections"],
        "agent": AGENTS["specification_router"],
        "tools": [],
        "phase": "specification_generation"
    },
    "extract_specification_entities": {
        "input_func": extract_specification_entities_input_func,
        "output_func": extract_specification_entities_output_func,
        "requires": ["requirements_document", "spec_classification_json"],
        "produces": ["spec_entities_json", "spec_actors", "spec_functional_requirements", "spec_use_cases"],
        "agent": AGENTS["specification_entity_extractor"],
        "tools": [],
        "phase": "specification_generation"
    },
    "research_specification_context": {
        "input_func": research_specification_context_input_func,
        "output_func": research_specification_context_output_func,
        "requires": ["spec_entities_json"],
        "produces": ["spec_research_context_json", "spec_technical_standards", "spec_compliance_requirements", "spec_best_practices"],
        "agent": AGENTS["specification_web_researcher"],
        "tools": [
            LANGNET_TOOLS["tavily_search"],
            LANGNET_TOOLS["serpapi_search"],
            LANGNET_TOOLS["serper_search"]
        ],
        "phase": "specification_generation"
    },
    "compose_spec_use_cases": {
        "input_func": compose_spec_use_cases_input_func,
        "output_func": compose_spec_use_cases_output_func,
        "requires": ["spec_entities_json", "requirements_document"],
        "produces": ["spec_use_cases_json", "spec_use_cases", "spec_use_cases_count"],
        "agent": AGENTS["specification_composer"],
        "tools": [],
        "phase": "specification_generation"
    },
    "compose_spec_document": {
        "input_func": compose_spec_document_input_func,
        "output_func": compose_spec_document_output_func,
        "requires": ["spec_entities_json", "spec_research_context_json", "spec_use_cases_json"],
        "produces": ["spec_draft_sections_json", "spec_draft_document_md", "spec_sections"],
        "agent": AGENTS["specification_composer"],
        "tools": [],
        "phase": "specification_generation"
    },
    "verify_specification_grounding": {
        "input_func": verify_specification_grounding_input_func,
        "output_func": verify_specification_grounding_output_func,
        "requires": ["spec_draft_sections_json", "spec_entities_json", "requirements_document"],
        "produces": ["spec_verification_json", "spec_verified_items", "spec_grounding_score"],
        "agent": AGENTS["specification_verifier"],
        "tools": [],
        "phase": "specification_generation"
    },
    "validate_specification_compliance": {
        "input_func": validate_specification_compliance_input_func,
        "output_func": validate_specification_compliance_output_func,
        "requires": ["spec_draft_sections_json", "spec_verification_json"],
        "produces": ["spec_compliance_json", "spec_compliance_ok", "spec_compliance_score"],
        "agent": AGENTS["specification_compliance"],
        "tools": [],
        "phase": "specification_generation"
    },
    "apply_spec_corrections": {
        "input_func": apply_spec_corrections_input_func,
        "output_func": apply_spec_corrections_output_func,
        "requires": ["spec_draft_sections_json", "spec_verification_json", "spec_compliance_json"],
        "produces": ["spec_corrected_sections_json", "spec_corrections_applied", "spec_grounding_score"],
        "agent": AGENTS["specification_formatter"],
        "tools": [],
        "phase": "specification_generation"
    },
    "render_final_specification": {
        "input_func": render_final_specification_input_func,
        "output_func": render_final_specification_output_func,
        "requires": ["spec_corrected_sections_json"],
        "produces": ["spec_final_json", "spec_status", "spec_document_md", "spec_metadata"],
        "agent": AGENTS["specification_formatter"],
        "tools": [],
        "phase": "specification_generation"
    }
}


# ============================================================================
# EXECUTOR FUNCTIONS
# ============================================================================

def execute_task_with_context(
    task_name: str,
    context_state: LangNetFullState,
    verbose_callback: Optional[Callable[[str], None]] = None
) -> LangNetFullState:
    """
    Execute a single task with context state

    Args:
        task_name: Name of task from TASK_REGISTRY
        context_state: Current state
        verbose_callback: Optional callback for progress messages

    Returns:
        Updated context state
    """
    if task_name not in TASK_REGISTRY:
        raise ValueError(f"Task '{task_name}' not found in TASK_REGISTRY")

    task_config = TASK_REGISTRY[task_name]

    # Log task start
    context_state = log_task_start(context_state, task_name)
    context_state["current_phase"] = task_config["phase"]

    if verbose_callback:
        verbose_callback(f"Starting task: {task_name}")

    try:
        # 1. Extract input from context state
        task_input = task_config["input_func"](context_state)

        # VALIDAÇÃO: Verificar se inputs críticos não estão vazios
        if task_name in ["analyze_document", "extract_requirements"]:
            doc_content = context_state.get("document_content", "")
            if not doc_content or len(doc_content) < 100:
                error_msg = f"ERROR: Task '{task_name}' requires document_content but it's empty or too short ({len(doc_content)} chars)"
                print(f"\n{'='*80}")
                print(f"[VALIDATION ERROR] {error_msg}")
                print(f"{'='*80}\n")
                return {
                    **context_state,
                    "errors": context_state.get("errors", []) + [error_msg],
                    "status": "failed",
                    "last_error": error_msg
                }

        if verbose_callback:
            verbose_callback(f"Task input: {json.dumps(task_input, indent=2)[:200]}")

        # 2. Get agent (lazy load with DeepSeek support)
        use_deepseek = context_state.get("use_deepseek", False)
        agent_ref = task_config["agent"]

        # If agent is None or we need DeepSeek, load dynamically
        if agent_ref is None or use_deepseek:
            # Determine agent name from task name
            agent_name_map = {
                "analyze_document": "document_analyst",
                "extract_requirements": "requirements_engineer",
                "research_additional_info": "web_researcher",
                "enrich_requirements": "requirements_validator",
                "validate_quality": "requirements_validator",
                "generate_document": "requirements_validator",
                "generate_specification": "specification_generator",
                "suggest_agents": "agent_specifier",
                "decompose_tasks": "task_decomposer",
                "design_petri_net": "petri_net_designer",
                "generate_yaml_files": "yaml_generator",
                "generate_python_code": "code_generator",
                # Specification multi-step pipeline agents
                "classify_specification_intent": "specification_router",
                "extract_specification_entities": "specification_entity_extractor",
                "research_specification_context": "specification_web_researcher",
                "compose_spec_use_cases": "specification_composer",
                "compose_spec_document": "specification_composer",
                "verify_specification_grounding": "specification_verifier",
                "validate_specification_compliance": "specification_compliance",
                "apply_spec_corrections": "specification_formatter",
                "render_final_specification": "specification_formatter"
            }

            agent_name = agent_name_map.get(task_name)
            if not agent_name:
                raise ValueError(f"Cannot determine agent for task: {task_name}")

            agent = get_agent(agent_name, use_deepseek)
        else:
            agent = agent_ref

        # 3. Create task
        print(f"\n{'='*80}")
        print(f"[PHASE 3] BEFORE formatting task description for '{task_name}'")
        print(f"[PHASE 3] task_input keys: {list(task_input.keys())}")
        print(f"[PHASE 3] task_input['document_content'] length: {len(task_input.get('document_content', ''))} chars")
        print(f"[PHASE 3] task_input['additional_instructions'] length: {len(task_input.get('additional_instructions', ''))} chars")
        print(f"[PHASE 3] Raw task description template (first 500 chars):")
        print(f"{TASKS_CONFIG[task_name]['description'][:500]}")
        print(f"{'='*80}\n")

        task_description = TASKS_CONFIG[task_name]['description'].format(**task_input)

        # Note: After .format(), all template variables have been replaced with actual values.
        # Any remaining braces {} in the content (from JSON in LLM outputs) should not be
        # interpreted as template variables by CrewAI - we'll pass empty inputs to prevent this.

        print(f"\n{'='*80}")
        print(f"[PHASE 3] AFTER formatting task description for '{task_name}'")
        print(f"[PHASE 3] Formatted description length: {len(task_description)} chars")
        print(f"[PHASE 3] Formatted description preview (first 800 chars):")
        print(f"{task_description[:800]}")
        print(f"[PHASE 3] Formatted description preview (search for 'document_content' keyword):")
        if 'document_content:' in task_description:
            idx = task_description.index('document_content:')
            print(f"{task_description[idx:idx+400]}")
        else:
            print("⚠️  'document_content:' NOT FOUND in formatted description!")
        print(f"{'='*80}\n")

        task_expected_output = TASKS_CONFIG[task_name]['expected_output']
        # No escaping needed - expected_output now uses textual descriptions instead of JSON with braces

        # Convert tools to framework format: [(crewai_tool, phidata_tool), ...]
        # Since we only use CrewAI tools, we create tuples with (tool, None)
        tools_list = task_config.get("tools", [])
        framework_tools = [(tool, None) for tool in tools_list] if tools_list else []

        task_obj = TaskClass(
            description=task_description,
            expected_output=task_expected_output,
            agent=agent,
            tools=framework_tools
        )

        # 4. Execute task
        crew = TeamClass(
            agents=[agent],  # Use the agent (potentially recreated with DeepSeek)
            tasks=[task_obj],
            verbose=False,
            process=ProcessClass(ProcessType.SEQUENTIAL)
        )

        # Execute the crew - check which method is available
        # LangGraphTeamAdapter uses executar(), CrewAI Crew uses kickoff()
        # Pass empty inputs since we've already formatted the description with all values
        # This prevents CrewAI from trying to interpolate any braces in the content

        if hasattr(crew, 'kickoff'):
            result = crew.kickoff(inputs={})
        elif hasattr(crew, 'executar'):
            result = crew.executar(inputs={})
        else:
            raise AttributeError(f"Team object has neither 'kickoff' nor 'executar' method: {type(crew).__name__}")

        # Debug CrewOutput structure to understand what we're receiving
        print(f"\n{'='*80}")
        print(f"[CREW RESULT DEBUG] Task: {task_name}")
        print(f"[CREW RESULT DEBUG] Result type: {type(result)}")
        print(f"[CREW RESULT DEBUG] Has 'raw' attribute: {hasattr(result, 'raw')}")
        print(f"[CREW RESULT DEBUG] Has 'json_dict' attribute: {hasattr(result, 'json_dict')}")
        print(f"[CREW RESULT DEBUG] Has 'model_dump' method: {hasattr(result, 'model_dump')}")
        if hasattr(result, 'raw'):
            raw_preview = str(result.raw)[:500] if result.raw else '(None)'
            print(f"[CREW RESULT DEBUG] result.raw preview (first 500 chars):\n{raw_preview}")
        if hasattr(result, 'json_dict'):
            json_dict_keys = list(result.json_dict.keys()) if result.json_dict else '(None)'
            print(f"[CREW RESULT DEBUG] result.json_dict keys: {json_dict_keys}")
        print(f"{'='*80}\n")

        if verbose_callback:
            verbose_callback(f"Task result: {str(result)[:200]}")

        # 4. Update context state
        updated_context = task_config["output_func"](context_state, result)

        if verbose_callback:
            verbose_callback(f"Task completed: {task_name}")

        return updated_context

    except Exception as e:
        import traceback
        full_traceback = traceback.format_exc()

        if verbose_callback:
            verbose_callback(f"Task failed: {task_name} - {str(e)}")
            verbose_callback(f"Full traceback:\n{full_traceback}")

        # Always print to console for debugging
        print(f"\n{'='*80}")
        print(f"ERROR in task: {task_name}")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"\nFull Traceback:")
        print(full_traceback)
        print(f"{'='*80}\n")

        return log_task_error(context_state, task_name, e)


def execute_full_pipeline(
    project_id: str,
    document_id: str,
    document_path: str,
    framework_choice: str = "crewai",
    additional_instructions: str = "",
    verbose_callback: Optional[Callable[[str], None]] = None
) -> LangNetFullState:
    """
    Execute the complete LangNet pipeline

    Flow:
    1. Document Analysis → Extract Requirements → Web Research → Validate → Specify
    2. Suggest Agents → Decompose Tasks
    3. Design Petri Net
    4. Generate YAML → Generate Python Code

    Args:
        project_id: Project UUID
        document_id: Document UUID
        document_path: Path to uploaded document
        framework_choice: Target framework (crewai, autogen, langgraph)
        additional_instructions: Custom instructions from user
        verbose_callback: Optional callback for progress updates

    Returns:
        Final context state with all results
    """
    # Initialize state
    state = init_full_state(
        project_id=project_id,
        document_id=document_id,
        document_path=document_path,
        framework_choice=framework_choice,
        additional_instructions=additional_instructions
    )

    # Define execution order (NOW WITH 12 TASKS!)
    pipeline_tasks = [
        "analyze_document",
        "extract_requirements",
        "research_additional_info",  # Web research
        "enrich_requirements",      # NEW: Validate completeness + AI suggestions (replaces validate_requirements)
        "validate_quality",          # NEW: Quality validation + gap analysis
        "generate_document",         # NEW: Generate final markdown document
        "generate_specification",
        "suggest_agents",
        "decompose_tasks",
        "design_petri_net",
        "generate_yaml_files",
        "generate_python_code"
    ]

    # Execute each task sequentially
    for task_name in pipeline_tasks:
        if verbose_callback:
            verbose_callback(f"\n{'='*60}\nExecuting: {task_name}\n{'='*60}")

        state = execute_task_with_context(task_name, state, verbose_callback)

        # Check for errors
        if state.get("errors") and len(state["errors"]) > 0:
            if verbose_callback:
                verbose_callback(f"Pipeline stopped due to error in {task_name}")
            break

    # Mark completion
    state["completed_at"] = datetime.now().isoformat()

    return state


# Note: init_full_state is imported from langnetstate.py
# Do not redefine it here


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def execute_document_analysis_workflow(
    project_id: str,
    document_id: str,
    document_path: str,
    project_name: str = "",
    project_description: str = "",
    project_domain: str = "",
    additional_instructions: str = "",
    document_type: str = "pdf",
    use_deepseek: bool = False,
    document_content: str = "",
    enable_web_research: bool = True
) -> LangNetFullState:
    """
    Execute only document analysis workflow

    Args:
        project_id: Project UUID
        document_id: Document UUID
        document_path: Path to document file
        project_name: Name of the project
        project_description: Project description
        project_domain: Project domain/industry
        additional_instructions: Additional instructions for agents
        document_type: Type of document (pdf, docx, txt, etc.)
        use_deepseek: If True, uses DeepSeek LLM; if False, uses OpenAI GPT-4
        document_content: Pre-extracted and chunked document content (optional)
        enable_web_research: If True, enables web research for additional context (default: True)

    Returns:
        Final state with requirements document
    """
    print(f"\n{'='*80}")
    print(f"[PHASE 2] execute_document_analysis_workflow() called")
    print(f"[PHASE 2] Parameters received:")
    print(f"[PHASE 2]   - document_content length: {len(document_content)} chars")
    print(f"[PHASE 2]   - document_content preview (first 300 chars):")
    print(f"{document_content[:300] if document_content else '(EMPTY!)'}")
    print(f"{'='*80}\n")

    # Initialize state with all parameters
    state = init_full_state(
        project_id=project_id,
        document_id=document_id,
        document_path=document_path,
        project_name=project_name,
        project_description=project_description,
        project_domain=project_domain,
        additional_instructions=additional_instructions,
        document_type=document_type,
        document_content=document_content
    )

    print(f"\n{'='*80}")
    print(f"[PHASE 2] State returned from init_full_state")
    print(f"[PHASE 2] state['document_content'] length: {len(state.get('document_content', ''))} chars")
    print(f"[PHASE 2] state['additional_instructions'] length: {len(state.get('additional_instructions', ''))} chars")
    print(f"{'='*80}\n")

    # Add DeepSeek flag to state
    state["use_deepseek"] = use_deepseek

    print(f"\n{'='*80}")
    print(f"[PHASE 2] About to execute analyze_document task")
    print(f"[PHASE 2] State passed to task has document_content: {len(state.get('document_content', ''))} chars")
    print(f"{'='*80}\n")

    # Execute workflow tasks
    state = execute_task_with_context("analyze_document", state)
    state = execute_task_with_context("extract_requirements", state)

    # Web research task (can be enabled/disabled via parameter)
    if enable_web_research:
        print(f"\n🌐 Web research HABILITADA - Buscando best practices e padrões da indústria...")
        state = execute_task_with_context("research_additional_info", state)
    else:
        print(f"\n⏭️  Web research DESABILITADA - Pulando pesquisa complementar...")

    # Dividido em 3 tasks para reduzir tamanho do prompt e evitar timeouts
    state = execute_task_with_context("enrich_requirements", state)
    state = execute_task_with_context("validate_quality", state)
    state = execute_task_with_context("generate_document", state)

    return state


def execute_agent_design_workflow(requirements_data: Dict, specification_data: Dict) -> LangNetFullState:
    """Execute only agent design workflow"""
    state = init_full_state(
        project_id="temp",
        document_id="temp",
        document_path="temp"
    )
    state["requirements_data"] = requirements_data
    state["specification_data"] = specification_data
    state["requirements_json"] = json.dumps(requirements_data)
    state = execute_task_with_context("suggest_agents", state)
    state = execute_task_with_context("decompose_tasks", state)
    return state


def execute_specification_workflow(
    project_id: str,
    requirements_document: str,
    requirements_version: int = 1,
    requirements_created_at: str = "",
    project_name: str = "Sistema",
    detail_level: str = "detailed",
    target_audience: str = "mixed",
    use_deepseek: bool = False,
    wireframe_format: str = 'ascii',
    verbose_callback: Optional[Callable[[str], None]] = None
) -> LangNetFullState:
    """
    Execute the multi-step specification generation workflow following Generative Computing principles.

    Pipeline:
    1. classify_specification_intent (RouterAgent) - Classify intent and scope
    2. extract_specification_entities (EntityExtractorAgent) - Extract all entities with context_ids
    3. research_specification_context (WebResearcherAgent) - Research standards and best practices
    4. compose_spec_use_cases (ComposerAgent) - Generate detailed Use Cases (section 5 only)
    5. compose_spec_document (ComposerAgent) - Generate sections 1-4 and 6-14
    6. verify_specification_grounding (VerifierAgent) - Validate all items have context support
    7. validate_specification_compliance (ComplianceAgent) - Check language, structure, policies
    8. apply_spec_corrections (FormatterAgent) - Apply verification and compliance corrections
    9. render_final_specification (FormatterAgent) - Render final Markdown document

    Args:
        project_id: Project UUID
        requirements_document: The requirements document (Markdown) to generate specification from
        requirements_version: Version number of the requirements document
        requirements_created_at: Creation date of the requirements document
        project_name: Name of the project/system
        detail_level: Level of detail ("detailed", "summary", "executive")
        target_audience: Target audience ("technical", "business", "mixed")
        use_deepseek: If True, uses DeepSeek LLM; if False, uses configured LLM
        verbose_callback: Optional callback for progress updates

    Returns:
        Final state with specification document in spec_document_md
    """
    print(f"\n{'='*80}")
    print(f"[SPECIFICATION] Starting multi-step specification generation workflow")
    print(f"[SPECIFICATION] Pipeline: Router → EntityExtractor → WebResearcher → UseCases → Document → Verifier → Compliance → Corrections → Renderer")
    print(f"[SPECIFICATION] Requirements document length: {len(requirements_document)} chars")
    print(f"[SPECIFICATION] Project: {project_name}, Version: {requirements_version}")
    print(f"{'='*80}\n")

    # Initialize state with specification-specific parameters
    state = init_full_state(
        project_id=project_id,
        document_id="spec_gen",
        document_path=""
    )

    # Add specification-specific state
    state["requirements_document"] = requirements_document
    state["requirements_version"] = requirements_version
    state["requirements_created_at"] = requirements_created_at or datetime.now().strftime("%Y-%m-%d")
    state["project_name"] = project_name
    state["spec_detail_level"] = detail_level
    state["spec_target_audience"] = target_audience
    state["use_deepseek"] = use_deepseek
    state["wireframe_format"] = wireframe_format

    # Define specification pipeline tasks (9 steps following Generative Computing)
    spec_pipeline_tasks = [
        "classify_specification_intent",      # Step 1: Router - classify intent
        "extract_specification_entities",     # Step 2: EntityExtractor - extract entities with context_ids
        "research_specification_context",     # Step 3: WebResearcher - research standards and best practices
        "compose_spec_use_cases",             # Step 4: Composer - generate Use Cases (section 5)
        "compose_spec_document",              # Step 5: Composer - generate sections 1-4 and 6-14
        "verify_specification_grounding",     # Step 6: Verifier - validate grounding
        "validate_specification_compliance",  # Step 7: Compliance - check language/structure
        "apply_spec_corrections",             # Step 8: Formatter - apply corrections
        "render_final_specification"          # Step 9: Formatter - render final document
    ]

    # Execute each task sequentially
    for i, task_name in enumerate(spec_pipeline_tasks, 1):
        if verbose_callback:
            verbose_callback(f"\n[Step {i}/9] Executing: {task_name}")

        print(f"\n{'='*80}")
        print(f"[SPECIFICATION] Step {i}/9: {task_name}")
        print(f"{'='*80}\n")

        state = execute_task_with_context(task_name, state, verbose_callback)

        # Check for errors
        if state.get("errors") and len(state["errors"]) > 0:
            print(f"\n⚠️  [SPECIFICATION] Pipeline stopped due to error in {task_name}")
            if verbose_callback:
                verbose_callback(f"Pipeline stopped due to error in {task_name}")
            break

        # Log intermediate progress
        if verbose_callback:
            if task_name == "classify_specification_intent":
                verbose_callback(f"   Intent: {state.get('spec_intent', 'N/A')}, Scope: {state.get('spec_scope', 'N/A')}")
            elif task_name == "extract_specification_entities":
                verbose_callback(f"   Extracted: {len(state.get('spec_actors', []))} actors, {len(state.get('spec_use_cases', []))} use cases")
            elif task_name == "research_specification_context":
                summary = state.get('spec_research_summary', {})
                verbose_callback(f"   Researched: {summary.get('total_standards', 0)} standards, {summary.get('total_compliance', 0)} compliance, {summary.get('total_practices', 0)} practices")
            elif task_name == "compose_spec_use_cases":
                verbose_callback(f"   Use cases generated: {state.get('spec_use_cases_count', 0)}")
            elif task_name == "compose_spec_document":
                verbose_callback(f"   Generated: {len(state.get('spec_sections', []))} sections")
            elif task_name == "verify_specification_grounding":
                verbose_callback(f"   Grounding score: {state.get('spec_grounding_score', 'N/A')}%")
            elif task_name == "validate_specification_compliance":
                verbose_callback(f"   Compliance: {'OK' if state.get('spec_compliance_ok') else 'Issues found'}")
            elif task_name == "apply_spec_corrections":
                verbose_callback(f"   Corrections applied: {len(state.get('spec_corrections_applied', []))}")
            elif task_name == "render_final_specification":
                verbose_callback(f"   Final status: {state.get('spec_status', 'N/A')}")

    # Mark completion
    state["completed_at"] = datetime.now().isoformat()

    # Log final results
    print(f"\n{'='*80}")
    print(f"[SPECIFICATION] Workflow completed")
    print(f"[SPECIFICATION] Status: {state.get('spec_status', 'unknown')}")
    print(f"[SPECIFICATION] Document length: {len(state.get('spec_document_md', ''))} chars")
    print(f"[SPECIFICATION] Grounding score: {state.get('spec_grounding_score_final', 'N/A')}")
    print(f"[SPECIFICATION] Compliance score: {state.get('spec_compliance_score_final', 'N/A')}")
    print(f"[SPECIFICATION] Total sections: {state.get('spec_total_sections', 'N/A')}")
    print(f"[SPECIFICATION] Complete sections: {state.get('spec_complete_sections', 'N/A')}")
    print(f"[SPECIFICATION] Gaps: {len(state.get('spec_final_gaps', []))}")
    print(f"[SPECIFICATION] Warnings: {len(state.get('spec_warnings', []))}")
    print(f"{'='*80}\n")

    return state


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("LangNet Agents System")
    print(f"Loaded {len(AGENTS)} agents")
    print(f"Loaded {len(TASK_REGISTRY)} tasks")
    print("\nAgents:", list(AGENTS.keys()))
    print("\nTasks:", list(TASK_REGISTRY.keys()))
