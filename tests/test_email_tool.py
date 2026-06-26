import pytest
import os
from unittest.mock import patch, MagicMock
from tools.email_tool import SMTPEmailTool

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": "465",
        "SENDER_EMAIL": "test@example.com",
        "SENDER_APP_PASSWORD": "password123",
        "DRY_RUN": "False"
    }):
        yield

def test_email_tool_dry_run():
    with patch.dict(os.environ, {"DRY_RUN": "True"}):
        tool = SMTPEmailTool()
        # Create a dummy file
        with open("test_dummy.pdf", "w") as f:
            f.write("dummy")
            
        result = tool._run("recipient@example.com", "Test Subject", "Test Body", "test_dummy.pdf")
        
        assert "Dry run successful" in result
        os.remove("test_dummy.pdf")

def test_email_tool_live(mock_env, mocker):
    mock_smtp = mocker.patch("smtplib.SMTP_SSL")
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    tool = SMTPEmailTool()
    
    with open("test_dummy2.pdf", "w") as f:
        f.write("dummy")
        
    result = tool._run("recipient@example.com", "Test Subject", "Test Body", "test_dummy2.pdf")
    
    assert "Successfully sent email" in result
    mock_server.login.assert_called_once_with("test@example.com", "password123")
    mock_server.send_message.assert_called_once()
    
    os.remove("test_dummy2.pdf")

def test_email_tool_missing_credentials():
    with patch.dict(os.environ, {"SENDER_EMAIL": "your_email@gmail.com", "DRY_RUN": "False"}):
        tool = SMTPEmailTool()
        result = tool._run("recipient@example.com", "Test", "Test", None)
        assert "Error: Valid SENDER_EMAIL or SENDER_APP_PASSWORD not set." in result

def test_email_tool_missing_attachment(mock_env):
    tool = SMTPEmailTool()
    result = tool._run("recipient@example.com", "Test", "Test", "non_existent.pdf")
    assert "Warning: Attachment non_existent.pdf not found. Email aborted." in result

def test_email_tool_smtp_exception(mock_env, mocker):
    mock_smtp = mocker.patch("smtplib.SMTP_SSL")
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    mock_server.login.side_effect = Exception("SMTP Auth Failed")
    
    tool = SMTPEmailTool()
    result = tool._run("recipient@example.com", "Test", "Test", None)
    assert "Failed to send email. Error: SMTP Auth Failed" in result
