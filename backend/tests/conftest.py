"""
Pytest Configuration for LangNet Tests

Shared fixtures and configuration
"""
import pytest
import sys
from pathlib import Path
import os
from unittest.mock import Mock, MagicMock

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Add framework to Python path
framework_path = backend_path.parent / "framework"
sys.path.insert(0, str(framework_path))

# Mock CrewAI imports to avoid dependency issues in tests
# Create mock BaseTool class
class MockBaseTool:
    pass

mock_crewai_tools = MagicMock()
mock_crewai_tools.BaseTool = MockBaseTool

mock_crewai = MagicMock()
mock_crewai.tools = mock_crewai_tools
mock_crewai.tools.BaseTool = MockBaseTool

# Mock flow module and submodules
mock_flow = MagicMock()
mock_flow.flow = MagicMock()
mock_crewai.flow = mock_flow

sys.modules['crewai_tools'] = mock_crewai_tools
sys.modules['crewai'] = mock_crewai
sys.modules['crewai.tools'] = mock_crewai_tools
sys.modules['crewai.flow'] = mock_flow
sys.modules['crewai.flow.flow'] = mock_flow.flow


@pytest.fixture(scope="session", autouse=True)
def test_env():
    """Set up test environment variables"""
    os.environ["LLM_PROVIDER"] = "deepseek"
    os.environ["OPENAI_API_KEY"] = "test-openai-key"
    os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"
    os.environ["DEEPSEEK_API_KEY"] = "test-deepseek-key"
    os.environ["DEEPSEEK_API_BASE"] = "https://api.deepseek.com/v1"
    os.environ["DEEPSEEK_MODEL_NAME"] = "deepseek/deepseek-chat"
    os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
    os.environ["DATABASE_URL"] = "mysql://test:test@localhost:3306/test_db"
    yield
    # Cleanup if needed


@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    from unittest.mock import Mock

    conn = Mock()
    cursor = Mock()
    conn.cursor.return_value = cursor
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None

    return conn


@pytest.fixture(autouse=True)
def reset_executions():
    """Reset EXECUTIONS dict before each test"""
    try:
        from api.langnetapi import EXECUTIONS
        EXECUTIONS.clear()
    except ImportError:
        pass

    yield

    try:
        from api.langnetapi import EXECUTIONS
        EXECUTIONS.clear()
    except ImportError:
        pass
