import pytest
import os
from unittest.mock import patch, MagicMock
from tools.scraper_tool import JinaReaderScraperTool
from tools.pdf_tool import MarkdownToPDFTool

def test_jina_reader_tool_success(mocker):
    # Mock urllib.request.urlopen
    mock_urlopen = mocker.patch('urllib.request.urlopen')
    mock_response = MagicMock()
    mock_response.read.return_value = b"# Job Description\nThis is a mock markdown."
    
    # Context manager setup
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    tool = JinaReaderScraperTool()
    result = tool._run("https://example.com/job")
    
    assert "Job Description" in result
    assert "mock markdown" in result

def test_jina_reader_tool_failure(mocker):
    # Mock urllib.request.urlopen to throw an exception
    mock_urlopen = mocker.patch('urllib.request.urlopen')
    mock_urlopen.side_effect = Exception("Mock network error")
    
    tool = JinaReaderScraperTool()
    result = tool._run("https://example.com/job")
    
    assert "Unexpected error" in result
    assert "Mock network error" in result

def test_pdf_tool():
    tool = MarkdownToPDFTool()
    test_filepath = "test_output.pdf"
    
    # Run the tool
    result = tool._run("# Title\nThis is a test.", test_filepath)
    
    # Assert
    assert "Successfully generated PDF" in result
    assert os.path.exists(test_filepath)
    
    # Cleanup
    if os.path.exists(test_filepath):
        os.remove(test_filepath)

def test_jina_reader_tool_urlerror(mocker):
    import urllib.error
    mock_urlopen = mocker.patch('urllib.request.urlopen')
    mock_urlopen.side_effect = urllib.error.URLError("Mock URL error")
    
    tool = JinaReaderScraperTool()
    result = tool._run("https://example.com/job")
    
    assert "Failed to scrape URL" in result
    assert "Mock URL error" in result

def test_pdf_tool_failure(mocker):
    tool = MarkdownToPDFTool()
    mock_fpdf = mocker.patch('tools.pdf_tool.FPDF')
    mock_fpdf.side_effect = Exception("PDF Engine Error")
    
    result = tool._run("# Title", "test_output.pdf")
    assert "Failed to generate PDF" in result
    assert "PDF Engine Error" in result
