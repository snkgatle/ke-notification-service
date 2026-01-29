import pytest
from unittest.mock import MagicMock, patch
from app.notifications.email import BrevoEmailAdapter

@pytest.mark.asyncio
async def test_brevo_adapter_send_success():
    # Mock settings
    with patch("app.notifications.email.settings") as mock_settings:
        mock_settings.BREVO_API_KEY = "test_key"
        mock_settings.BREVO_FROM_EMAIL = "test@example.com"
        
        # Mock Brevo API Client
        with patch("sib_api_v3_sdk.TransactionalEmailsApi") as mock_api:
            adapter = BrevoEmailAdapter()
            
            # Setup mock response
            mock_response = MagicMock()
            mock_response.message_id = "test_message_id"
            mock_api.return_value.send_transac_email.return_value = mock_response
            
            result = await adapter.send(
                recipient="user@example.com",
                message="Test content",
                subject="Test Subject"
            )
            
            assert result["status"] == "success"
            assert result["message_id"] == "test_message_id"
            
            # Verify the call structure
            call_args = mock_api.return_value.send_transac_email.call_args[0][0]
            assert call_args.to[0]["email"] == "user@example.com"
            assert call_args.subject == "Test Subject"
            assert call_args.text_content == "Test content"

@pytest.mark.asyncio
async def test_brevo_adapter_client_not_initialized():
    with patch("app.notifications.email.settings") as mock_settings:
        mock_settings.BREVO_API_KEY = None # Simulate missing API key
        
        adapter = BrevoEmailAdapter()
        result = await adapter.send("user@example.com", "Testing")
        
        assert result["status"] == "error"
        assert "not initialized" in result["message"]
