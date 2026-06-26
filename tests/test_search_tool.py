import pytest
from unittest.mock import patch, MagicMock
from tools.search_tool import JobSearchTool
import json

def test_search_tool_success():
    with patch('duckduckgo_search.DDGS') as mock_ddgs:
        mock_instance = MagicMock()
        mock_ddgs.return_value = mock_instance
        mock_instance.text.return_value = [
            {'href': 'https://example.com/job1'},
            {'href': 'https://example.com/job2'},
            {'title': 'No href here'}
        ]
        
        tool = JobSearchTool()
        result = tool._run("query")
        
        urls = json.loads(result)
        assert len(urls) == 2
        assert 'https://example.com/job1' in urls
        assert 'https://example.com/job2' in urls

def test_search_tool_exception():
    with patch('duckduckgo_search.DDGS') as mock_ddgs:
        mock_ddgs.side_effect = Exception("Search Failed")
        
        tool = JobSearchTool()
        result = tool._run("query")
        
        urls = json.loads(result)
        assert urls == []
