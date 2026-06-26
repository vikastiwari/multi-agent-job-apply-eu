import pytest
from unittest.mock import patch, MagicMock
from tools.lance_rag_tool import CompanyContextRAGTool

@patch('tools.lance_rag_tool.os.environ.get')
@patch('tools.lance_rag_tool.DDGS.text')
@patch('tools.lance_rag_tool.requests.get')
@patch('tools.lance_rag_tool.genai.embed_content')
@patch('tools.lance_rag_tool.lancedb.connect')
def test_company_context_rag_tool(mock_connect, mock_embed, mock_get, mock_ddgs, mock_env):
    mock_env.return_value = "fake_api_key"
    mock_ddgs.return_value = [{'href': 'https://example.com'}]
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"content": "Company makes rockets.\n\nThey value innovation."}}
    mock_get.return_value = mock_response
    
    # Mocking embeddings: 2 chunks + 1 query
    mock_embed.side_effect = [
        {"embedding": [[0.1, 0.2], [0.3, 0.4]]},
        {"embedding": [[0.1, 0.2]]}
    ]
    
    # Mock LanceDB
    mock_db = MagicMock()
    mock_connect.return_value = mock_db
    mock_table = MagicMock()
    mock_db.create_table.return_value = mock_table
    
    mock_search = MagicMock()
    mock_table.search.return_value = mock_search
    mock_search.limit.return_value = mock_search
    
    import pandas as pd
    mock_search.to_pandas.return_value = pd.DataFrame({"text": ["Company makes rockets.", "They value innovation."]})
    
    tool = CompanyContextRAGTool()
    result = tool._run("Acme Corp")
    
    assert "Company: Acme Corp" in result
    assert "Company makes rockets" in result
    assert "They value innovation" in result

def test_company_context_rag_tool_no_api_key():
    with patch('tools.lance_rag_tool.os.environ.get', return_value=None):
        tool = CompanyContextRAGTool()
        result = tool._run("Acme Corp")
        assert "Error: GEMINI_API_KEY environment variable not set" in result

@patch('tools.lance_rag_tool.os.environ.get', return_value="fake_api_key")
@patch('tools.lance_rag_tool.DDGS.text')
def test_company_context_rag_tool_no_ddg_results(mock_ddgs, mock_env):
    mock_ddgs.return_value = []
    tool = CompanyContextRAGTool()
    result = tool._run("Acme Corp")
    assert "No results found for Acme Corp." in result

@patch('tools.lance_rag_tool.os.environ.get', return_value="fake_api_key")
@patch('tools.lance_rag_tool.DDGS.text')
def test_company_context_rag_tool_ddg_exception(mock_ddgs, mock_env):
    mock_ddgs.side_effect = Exception("DDG Error")
    tool = CompanyContextRAGTool()
    result = tool._run("Acme Corp")
    assert "Error searching DuckDuckGo: DDG Error" in result

@patch('tools.lance_rag_tool.os.environ.get', return_value="fake_api_key")
@patch('tools.lance_rag_tool.DDGS.text', return_value=[{'href': 'https://example.com'}])
@patch('tools.lance_rag_tool.requests.get')
def test_company_context_rag_tool_jina_exception(mock_get, mock_ddgs, mock_env):
    mock_get.side_effect = Exception("Jina Error")
    tool = CompanyContextRAGTool()
    result = tool._run("Acme Corp")
    assert "Error extracting content from https://example.com: Jina Error" in result

@patch('tools.lance_rag_tool.os.environ.get', return_value="fake_api_key")
@patch('tools.lance_rag_tool.DDGS.text', return_value=[{'href': 'https://example.com'}])
@patch('tools.lance_rag_tool.requests.get')
def test_company_context_rag_tool_jina_no_content(mock_get, mock_ddgs, mock_env):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {}}
    mock_get.return_value = mock_response
    tool = CompanyContextRAGTool()
    result = tool._run("Acme Corp")
    assert "Failed to extract meaningful content from https://example.com" in result

@patch('tools.lance_rag_tool.os.environ.get', return_value="fake_api_key")
@patch('tools.lance_rag_tool.DDGS.text', return_value=[{'href': 'https://example.com'}])
@patch('tools.lance_rag_tool.requests.get')
@patch('tools.lance_rag_tool.genai.embed_content')
def test_company_context_rag_tool_embed_exception(mock_embed, mock_get, mock_ddgs, mock_env):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"content": "Company makes rockets."}}
    mock_get.return_value = mock_response
    mock_embed.side_effect = Exception("Embed Error")
    tool = CompanyContextRAGTool()
    result = tool._run("Acme Corp")
    assert "Error generating embeddings: Embed Error" in result

@patch('tools.lance_rag_tool.os.environ.get', return_value="fake_api_key")
@patch('tools.lance_rag_tool.DDGS.text', return_value=[{'href': 'https://example.com'}])
@patch('tools.lance_rag_tool.requests.get')
@patch('tools.lance_rag_tool.genai.embed_content')
@patch('tools.lance_rag_tool.lancedb.connect')
def test_company_context_rag_tool_db_exception(mock_connect, mock_embed, mock_get, mock_ddgs, mock_env):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"content": "Company makes rockets."}}
    mock_get.return_value = mock_response
    mock_embed.side_effect = [{"embedding": [[0.1, 0.2]]}]
    
    mock_db = MagicMock()
    mock_connect.return_value = mock_db
    mock_table = MagicMock()
    mock_db.create_table.return_value = mock_table
    
    mock_embed.side_effect = [{"embedding": [[0.1, 0.2]]}, Exception("Search Embed Error")]
    
    tool = CompanyContextRAGTool()
    result = tool._run("Acme Corp")
    assert "Error searching vector database: Search Embed Error" in result
