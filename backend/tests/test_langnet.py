"""
LangNet Multi-Agent System Tests

Test coverage:
1. State Management
2. Tools
3. Agent Creation
4. Task Execution
5. Workflows
6. API Endpoints
"""
import pytest
import sys
from pathlib import Path
from typing import Dict, Any
import json
import yaml
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_state():
    """Sample LangNetFullState for testing"""
    from agents.langnetstate import LangNetFullState

    state: LangNetFullState = {
        "project_id": "test-project-123",
        "document_id": "test-doc-456",
        "document_path": "/test/path/document.pdf",
        "framework_choice": "crewai",
        "document_content": "This is a test document content with requirements.",
        "requirements_json": json.dumps({
            "functional_requirements": [
                {"id": "FR1", "description": "User login", "priority": "high"}
            ],
            "non_functional_requirements": [
                {"id": "NFR1", "description": "Response time < 2s", "priority": "medium"}
            ],
            "business_rules": [
                {"id": "BR1", "description": "Users must be 18+", "priority": "high"}
            ]
        }),
        "requirements_data": {
            "functional_requirements": [
                {"id": "FR1", "description": "User login", "priority": "high"}
            ],
            "non_functional_requirements": [
                {"id": "NFR1", "description": "Response time < 2s", "priority": "medium"}
            ],
            "business_rules": [
                {"id": "BR1", "description": "Users must be 18+", "priority": "high"}
            ]
        },
        "validation_data": {
            "total_requirements": 3,
            "issues": [],
            "quality_score": 95.0
        },
        "specification_md": "# Functional Specification\n\n## Requirements\n...",
        "agents_data": [
            {
                "name": "data_collector_agent",
                "role": "Data Collection Specialist",
                "goal": "Collect user data",
                "backstory": "Expert in data collection",
                "tools": [],
                "verbose": True,
                "allow_delegation": False
            }
        ],
        "tasks_data": [
            {
                "name": "collect_data_task",
                "description": "Collect user data from forms",
                "expected_output": "JSON with collected data",
                "tools": []
            }
        ],
        "petri_net_data": {
            "places": ["p1", "p2"],
            "transitions": ["t1"],
            "arcs": [["p1", "t1"], ["t1", "p2"]]
        },
        "agents_yaml": "data_collector_agent:\n  role: Data Collection Specialist\n",
        "tasks_yaml": "collect_data_task:\n  description: Collect user data\n",
        "generated_code": "# Generated CrewAI code\nfrom crewai import Agent\n",
        "execution_log": [],
        "current_task": None,
        "current_phase": None,
        "progress_percentage": 0.0,
        "completed_tasks": 0,
        "total_tasks": 9,
        "errors": []
    }

    return state


@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    llm = Mock()
    llm.invoke = Mock(return_value="Mocked LLM response")
    return llm


@pytest.fixture
def sample_document_path(tmp_path):
    """Create temporary test document"""
    doc_path = tmp_path / "test_document.txt"
    doc_path.write_text("Test requirement: User authentication system")
    return str(doc_path)


# ============================================================================
# STATE MANAGEMENT TESTS
# ============================================================================

class TestStateManagement:
    """Test Context State management"""

    def test_init_full_state(self):
        """Test state initialization"""
        from agents.langnetagents import init_full_state

        state = init_full_state(
            project_id="proj-123",
            document_id="doc-456",
            document_path="/path/to/doc.pdf",
            framework_choice="crewai"
        )

        assert state["project_id"] == "proj-123"
        assert state["document_id"] == "doc-456"
        assert state["document_path"] == "/path/to/doc.pdf"
        assert state["framework_choice"] == "crewai"
        assert state["progress_percentage"] == 0.0
        assert state["completed_tasks"] == 0
        assert state["total_tasks"] == 9
        assert isinstance(state["execution_log"], list)

    def test_log_task_start(self, sample_state):
        """Test task start logging"""
        from agents.langnetagents import log_task_start

        updated_state = log_task_start(sample_state, "extract_requirements", "requirements_extraction")

        assert updated_state["current_task"] == "extract_requirements"
        assert updated_state["current_phase"] == "requirements_extraction"
        assert len(updated_state["execution_log"]) == 1

        log_entry = updated_state["execution_log"][0]
        assert log_entry["task"] == "extract_requirements"
        assert log_entry["status"] == "started"
        assert log_entry["phase"] == "requirements_extraction"

    def test_log_task_complete(self, sample_state):
        """Test task completion logging"""
        from agents.langnetagents import log_task_complete

        sample_state["current_task"] = "extract_requirements"
        sample_state["total_tasks"] = 9
        sample_state["completed_tasks"] = 0

        updated_state = log_task_complete(sample_state, "extract_requirements", "Output preview")

        assert updated_state["completed_tasks"] == 1
        assert updated_state["progress_percentage"] == pytest.approx(11.11, rel=0.1)

        log_entry = updated_state["execution_log"][-1]
        assert log_entry["task"] == "extract_requirements"
        assert log_entry["status"] == "completed"


# ============================================================================
# TOOLS TESTS
# ============================================================================

class TestLangNetTools:
    """Test custom LangChain tools"""

    def test_document_reader_tool(self, sample_document_path):
        """Test DocumentReaderTool"""
        from agents.langnettools import DocumentReaderTool

        tool = DocumentReaderTool()

        assert tool.name == "document_reader"
        assert "document" in tool.description.lower()

        # Test reading a text file
        result = tool._run(document_path=sample_document_path, document_type="txt")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert "User authentication" in result_data["content"]

    def test_yaml_writer_tool(self, tmp_path):
        """Test YAMLWriterTool"""
        from agents.langnettools import YAMLWriterTool

        tool = YAMLWriterTool()

        # YAMLWriterTool expects JSON string or Python dict, not YAML
        data = {
            "test_agent": {
                "role": "Test Role",
                "goal": "Test Goal"
            }
        }
        yaml_content = json.dumps(data)

        output_path = str(tmp_path / "test_agents.yaml")
        result = tool._run(content=yaml_content, file_path=output_path)
        result_data = json.loads(result)

        assert result_data["success"] is True, f"YAML write failed: {result_data.get('error')}"
        assert Path(output_path).exists()

        # Verify YAML content is valid
        with open(output_path, 'r') as f:
            loaded_data = yaml.safe_load(f)
            assert loaded_data == data

    def test_yaml_validator_tool(self):
        """Test YAMLValidatorTool"""
        from agents.langnettools import YAMLValidatorTool

        tool = YAMLValidatorTool()

        # Valid YAML
        valid_yaml = "key: value\nlist:\n  - item1\n  - item2"
        result = tool._run(yaml_content=valid_yaml)
        result_data = json.loads(result)

        assert result_data["valid"] is True
        assert "error" not in result_data  # Valid YAML doesn't have error key

        # Invalid YAML (tabs not allowed for indentation)
        invalid_yaml = "key: value\n\t- invalid tab indentation"
        result = tool._run(yaml_content=invalid_yaml)
        result_data = json.loads(result)

        assert result_data["valid"] is False
        assert "error" in result_data
        assert result_data["error"] is not None

    def test_markdown_writer_tool(self, tmp_path):
        """Test MarkdownWriterTool"""
        from agents.langnettools import MarkdownWriterTool

        tool = MarkdownWriterTool()

        md_content = "# Test\n\nThis is a test."
        output_path = str(tmp_path / "test.md")

        result = tool._run(content=md_content, file_path=output_path)
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert Path(output_path).exists()

    def test_python_code_writer_tool(self, tmp_path):
        """Test PythonCodeWriterTool"""
        from agents.langnettools import PythonCodeWriterTool

        tool = PythonCodeWriterTool()

        code_content = "from crewai import Agent\n\ndef main():\n    pass"
        output_path = str(tmp_path / "test_code.py")

        result = tool._run(code=code_content, file_path=output_path)
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert Path(output_path).exists()


# ============================================================================
# AGENT CREATION TESTS
# ============================================================================

class TestAgentCreation:
    """Test agent creation functions"""

    @patch('agents.langnetagents.ChatOpenAI')
    def test_create_agents(self, mock_chat_openai):
        """Test all agents can be created"""
        from agents.langnetagents import AGENTS

        # Mock LLM
        mock_chat_openai.return_value = Mock()

        # Check all 8 agents exist
        expected_agents = [
            "document_analyst",
            "requirements_validator",
            "specification_generator",
            "agent_specifier",
            "task_decomposer",
            "petri_net_designer",
            "yaml_generator",
            "code_generator"
        ]

        for agent_name in expected_agents:
            assert agent_name in AGENTS
            agent = AGENTS[agent_name]
            assert agent is not None


# ============================================================================
# TASK REGISTRY TESTS
# ============================================================================

class TestTaskRegistry:
    """Test Task Registry structure"""

    def test_task_registry_structure(self):
        """Test Task Registry has all required tasks"""
        from agents.langnetagents import TASK_REGISTRY

        expected_tasks = [
            "analyze_document",
            "extract_requirements",
            "validate_requirements",
            "generate_specification",
            "suggest_agents",
            "decompose_tasks",
            "design_petri_net",
            "generate_yaml_files",
            "generate_python_code"
        ]

        for task_name in expected_tasks:
            assert task_name in TASK_REGISTRY

            task_config = TASK_REGISTRY[task_name]
            assert "input_func" in task_config
            assert "output_func" in task_config
            assert "requires" in task_config
            assert "produces" in task_config
            assert "agent" in task_config
            assert "phase" in task_config

    def test_task_dependencies(self):
        """Test task dependency chain is valid"""
        from agents.langnetagents import TASK_REGISTRY

        # extract_requirements requires document_content
        assert "document_content" in TASK_REGISTRY["extract_requirements"]["requires"]

        # validate_requirements requires requirements_data
        assert "requirements_data" in TASK_REGISTRY["validate_requirements"]["requires"]

        # suggest_agents requires requirements_data and specification_md
        assert "requirements_data" in TASK_REGISTRY["suggest_agents"]["requires"]
        assert "specification_md" in TASK_REGISTRY["suggest_agents"]["requires"]


# ============================================================================
# INPUT/OUTPUT FUNCTION TESTS
# ============================================================================

class TestInputOutputFunctions:
    """Test input and output functions"""

    def test_analyze_document_input_func(self, sample_state):
        """Test analyze_document input function"""
        from agents.langnetagents import analyze_document_input_func

        input_data = analyze_document_input_func(sample_state)

        assert "document_path" in input_data
        assert input_data["document_path"] == sample_state["document_path"]

    def test_extract_requirements_input_func(self, sample_state):
        """Test extract_requirements input function"""
        from agents.langnetagents import extract_requirements_input_func

        input_data = extract_requirements_input_func(sample_state)

        assert "document_content" in input_data
        assert input_data["document_content"] == sample_state["document_content"]

    def test_extract_requirements_output_func(self, sample_state):
        """Test extract_requirements output function"""
        from agents.langnetagents import extract_requirements_output_func

        mock_result = json.dumps({
            "functional_requirements": [{"id": "FR1", "description": "Test"}],
            "non_functional_requirements": [],
            "business_rules": []
        })

        updated_state = extract_requirements_output_func(sample_state, mock_result)

        assert "requirements_json" in updated_state
        assert "requirements_data" in updated_state
        assert isinstance(updated_state["requirements_data"], dict)


# ============================================================================
# WORKFLOW TESTS
# ============================================================================

class TestWorkflows:
    """Test workflow execution"""

    @patch('agents.langnetagents.execute_task_with_context')
    def test_execute_document_analysis_workflow(self, mock_execute_task, sample_state):
        """Test document analysis workflow"""
        from agents.langnetagents import execute_document_analysis_workflow

        # Mock task execution to return sample state
        mock_execute_task.return_value = sample_state

        result = execute_document_analysis_workflow(
            document_id="doc-123",
            document_path="/test/doc.pdf"
        )

        # Verify tasks were executed in order
        assert mock_execute_task.call_count == 4
        call_args = [call[0][0] for call in mock_execute_task.call_args_list]

        assert "analyze_document" in call_args
        assert "extract_requirements" in call_args
        assert "validate_requirements" in call_args
        assert "generate_specification" in call_args

    @patch('agents.langnetagents.execute_task_with_context')
    def test_execute_agent_design_workflow(self, mock_execute_task, sample_state):
        """Test agent design workflow"""
        from agents.langnetagents import execute_agent_design_workflow

        mock_execute_task.return_value = sample_state

        result = execute_agent_design_workflow(
            requirements_data=sample_state["requirements_data"],
            specification_data={"spec": "test"}
        )

        # Verify tasks were executed
        assert mock_execute_task.call_count == 2
        call_args = [call[0][0] for call in mock_execute_task.call_args_list]

        assert "suggest_agents" in call_args
        assert "decompose_tasks" in call_args


# ============================================================================
# API TESTS
# ============================================================================

class TestLangNetAPI:
    """Test LangNet API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from app.main import app

        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        # Note: In real tests, you'd generate a valid JWT token
        return {"Authorization": "Bearer test-token"}

    @patch('api.langnetapi.get_current_user')
    @patch('api.langnetapi.execute_full_pipeline')
    def test_execute_full_pipeline_endpoint(self, mock_execute, mock_auth, client, auth_headers, sample_state):
        """Test POST /api/langnet/execute-full-pipeline"""
        mock_auth.return_value = {"id": 1, "username": "test"}
        mock_execute.return_value = sample_state

        response = client.post(
            "/api/langnet/execute-full-pipeline",
            json={
                "project_id": "proj-123",
                "document_id": "doc-456",
                "document_path": "/test/doc.pdf",
                "framework_choice": "crewai"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "execution_id" in data
        assert data["status"] == "running"
        assert "started_at" in data

    @patch('api.langnetapi.get_current_user')
    def test_list_available_tasks(self, mock_auth, client, auth_headers):
        """Test GET /api/langnet/tasks/list"""
        mock_auth.return_value = {"id": 1, "username": "test"}

        response = client.get("/api/langnet/tasks/list", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "tasks" in data
        assert len(data["tasks"]) == 9

        # Check first task structure
        task = data["tasks"][0]
        assert "name" in task
        assert "description" in task
        assert "phase" in task
        assert "requires" in task
        assert "produces" in task

    @patch('api.langnetapi.get_current_user')
    def test_list_available_agents(self, mock_auth, client, auth_headers):
        """Test GET /api/langnet/agents/list"""
        mock_auth.return_value = {"id": 1, "username": "test"}

        response = client.get("/api/langnet/agents/list", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "agents" in data
        assert len(data["agents"]) == 8

        # Check first agent structure
        agent = data["agents"][0]
        assert "name" in agent
        assert "role" in agent
        assert "goal" in agent
        assert "backstory" in agent


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for end-to-end workflows"""

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_full_pipeline_integration(self, sample_document_path):
        """Test complete pipeline execution (requires API key)"""
        from agents.langnetagents import execute_full_pipeline

        result = execute_full_pipeline(
            project_id="test-proj",
            document_id="test-doc",
            document_path=sample_document_path,
            framework_choice="crewai"
        )

        # Verify all outputs are generated
        assert "document_content" in result
        assert "requirements_data" in result
        assert "agents_data" in result
        assert "tasks_data" in result
        assert "generated_code" in result


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
