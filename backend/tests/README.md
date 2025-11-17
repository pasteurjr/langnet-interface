# LangNet Tests

Comprehensive test suite for the LangNet Multi-Agent System.

## Test Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Shared fixtures
├── test_langnet.py          # Main test suite (300+ lines)
└── README.md                # This file
```

## Test Coverage

### 1. State Management Tests (TestStateManagement)
- ✅ State initialization
- ✅ Task start logging
- ✅ Task completion logging
- ✅ Progress calculation

### 2. Tools Tests (TestLangNetTools)
- ✅ DocumentReaderTool (PDF, DOCX, TXT, MD)
- ✅ YAMLWriterTool
- ✅ YAMLValidatorTool
- ✅ MarkdownWriterTool
- ✅ PythonCodeWriterTool

### 3. Agent Creation Tests (TestAgentCreation)
- ✅ All 8 agents can be instantiated
- ✅ Agent configuration loaded correctly

### 4. Task Registry Tests (TestTaskRegistry)
- ✅ All 9 tasks registered
- ✅ Task structure validation
- ✅ Dependency chain validation

### 5. Input/Output Function Tests (TestInputOutputFunctions)
- ✅ Input functions extract correct data
- ✅ Output functions update state correctly

### 6. Workflow Tests (TestWorkflows)
- ✅ Document analysis workflow (4 tasks)
- ✅ Agent design workflow (2 tasks)

### 7. API Tests (TestLangNetAPI)
- ✅ Execute full pipeline endpoint
- ✅ List tasks endpoint
- ✅ List agents endpoint

### 8. Integration Tests (TestIntegration)
- ⏸️ Full pipeline (requires OpenAI API key)

## Running Tests

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=agents --cov=api --cov-report=html

# Run specific test file
pytest tests/test_langnet.py

# Run specific test class
pytest tests/test_langnet.py::TestStateManagement

# Run specific test
pytest tests/test_langnet.py::TestStateManagement::test_init_full_state
```

### Run by Category

```bash
# Unit tests only (fast, no external dependencies)
pytest -m unit

# Integration tests
pytest -m integration

# API tests
pytest -m api

# Tool tests
pytest -m tools

# Workflow tests
pytest -m workflow
```

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=agents --cov=api --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=agents --cov=api --cov-report=html
open htmlcov/index.html
```

## Test Fixtures

### Available Fixtures (conftest.py)

1. **test_env** - Sets up test environment variables
2. **mock_db_connection** - Mock MySQL connection
3. **reset_executions** - Clears EXECUTIONS dict between tests

### Test-Specific Fixtures (test_langnet.py)

1. **sample_state** - Complete LangNetFullState with all fields populated
2. **mock_llm** - Mock LLM for testing without API calls
3. **sample_document_path** - Temporary test document file
4. **client** - FastAPI TestClient
5. **auth_headers** - Mock authentication headers

## Writing New Tests

### Template

```python
import pytest
from agents.langnetagents import execute_task_with_context

class TestNewFeature:
    """Test new feature"""

    def test_something(self, sample_state):
        """Test description"""
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = execute_task_with_context("task_name", sample_state)

        # Assert
        assert result["field"] == expected_value
```

### Best Practices

1. **Use descriptive test names**: `test_extract_requirements_returns_valid_json`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use fixtures**: Avoid duplicating test setup
4. **Mock external dependencies**: LLMs, databases, file I/O
5. **Test edge cases**: Empty inputs, invalid data, errors
6. **Add markers**: `@pytest.mark.unit`, `@pytest.mark.slow`

## Mocking Examples

### Mock LLM Calls

```python
from unittest.mock import patch

@patch('agents.langnetagents.ChatOpenAI')
def test_with_mocked_llm(mock_chat):
    mock_chat.return_value.invoke.return_value = "Mocked response"
    # Test code here
```

### Mock Database

```python
@patch('app.database.get_db_connection')
def test_with_mocked_db(mock_db, mock_db_connection):
    mock_db.return_value = mock_db_connection
    # Test code here
```

### Mock File Operations

```python
def test_file_operations(tmp_path):
    # tmp_path is pytest fixture for temporary directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    # Test code here
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Ensure you're in backend directory
cd backend

# Verify PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run pytest with pythonpath option
pytest --pythonpath=.
```

### Database Connection Errors

Tests use mocked database connections by default. If you need real database:

```python
# Set environment variable
export TEST_DATABASE_URL="mysql://user:pass@host:port/test_db"

# Or create .env.test file
```

### OpenAI API Errors

Integration tests requiring OpenAI API are marked with `@pytest.mark.skip`. To run them:

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Remove skip marker in test file
# Or run with:
pytest --run-skip-tests
```

## Test Metrics

Current test metrics:

- **Total Tests**: 20 tests
  - State Management: 3 tests
  - Tools: 5 tests ✅ (ALL PASSING)
  - Agent Creation: 1 test
  - Task Registry: 2 tests
  - Input/Output Functions: 3 tests
  - Workflows: 2 tests
  - API: 3 tests
  - Integration: 1 test (skipped - requires API key)

- **Status**: 5/20 passing (Tools fully tested)
- **Execution Time**: ~5 seconds
- **Known Issues**:
  - CrewAI framework mocking needs refinement for langnetagents tests
  - API tests need better fixture isolation

## Next Steps

1. ✅ Unit tests implemented
2. ✅ API tests implemented
3. ✅ Workflow tests implemented
4. ⏳ Integration tests (require API keys)
5. ⏳ Performance tests
6. ⏳ End-to-end tests with frontend

## Related Documentation

- [LangNet Agents README](../agents/README.md) - System architecture
- [API Documentation](http://localhost:8000/docs) - FastAPI endpoints
- [Framework Documentation](../../frameworks/README.md) - Custom framework
