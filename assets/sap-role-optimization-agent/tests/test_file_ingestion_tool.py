"""Unit tests for file_ingestion_tool."""
import json
import pytest

from role_discovery_tool import clear_session_dataset, get_session_dataset
from file_ingestion_tool import file_ingestion_tool


@pytest.fixture(autouse=True)
def reset_dataset():
    clear_session_dataset()
    yield
    clear_session_dataset()


def test_file_ingestion_valid_csv():
    csv = "user_id,role_name,environment,functional_type\nUSR001,BR_ADMIN,BTP,Security\nUSR002,BR_DEV,S4_CLOUD,Technical\n"
    result = json.loads(file_ingestion_tool.invoke({"file_content": csv, "file_format": "csv"}))
    assert result["status"] == "success"
    assert result["records_added"] == 2


def test_file_ingestion_missing_columns():
    csv = "user_id,role_name\nUSR001,BR_ADMIN\n"
    result = json.loads(file_ingestion_tool.invoke({"file_content": csv, "file_format": "csv"}))
    assert result["status"] == "error"
    assert "environment" in str(result["missing_columns"])


def test_file_ingestion_normalizes_environment():
    csv = "user_id,role_name,environment\nUSR001,BR_TEST,on-premise\n"
    json.loads(file_ingestion_tool.invoke({"file_content": csv, "file_format": "csv"}))
    assert get_session_dataset()[0]["environment"] == "S4_ON_PREM"


def test_file_ingestion_unsupported_format():
    result = json.loads(file_ingestion_tool.invoke({"file_content": "data", "file_format": "xml"}))
    assert result["status"] == "error"
    assert "Unsupported" in result["message"]


def test_file_ingestion_empty_csv():
    csv = "user_id,role_name,environment\n"
    result = json.loads(file_ingestion_tool.invoke({"file_content": csv, "file_format": "csv"}))
    assert result["status"] == "success"
    assert result["records_added"] == 0
