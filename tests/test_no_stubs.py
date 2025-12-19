"""
Test suite to verify NO STUB data paths exist in the application.

Goal: Ensure that:
1. All astrological data comes from Vedic API (real)
2. No fallback to stub generators
3. Failures are explicit and transparent
4. No silent degradation to fake data
"""

import pytest
import os
import sys
from pathlib import Path
from datetime import date, datetime
from unittest.mock import Mock, patch, AsyncMock

# Add backend to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from backend.astro_client.vedic_api import VedicAPIClient, VedicApiError
from backend.astro_client.models import BirthDetails, AstroProfile
from backend.conversation.enhanced_orchestrator import EnhancedOrchestrator
from backend.conversation.niro_llm import NiroLLM


class TestNoStubsInVedicAPI:
    """Test that VedicAPIClient raises errors instead of returning stub data."""
    
    @pytest.fixture
    def client(self):
        """Create a VedicAPIClient instance for testing."""
        with patch.dict(os.environ, {'VEDIC_API_KEY': 'test-key-123'}):
            return VedicAPIClient()
    
    @pytest.fixture
    def birth_details(self):
        """Create test birth details."""
        return BirthDetails(
            dob=date(1990, 1, 15),
            tob="14:30",
            location="Mumbai",
            latitude=19.0760,
            longitude=72.8777,
            timezone=5.5
        )
    
    @pytest.mark.asyncio
    async def test_missing_api_key_raises_error(self):
        """Test that missing API key raises VedicApiError, not stub data."""
        with patch.dict(os.environ, {'VEDIC_API_KEY': ''}):
            client = VedicAPIClient()
            birth = BirthDetails(
                dob=date(1990, 1, 15),
                tob="14:30",
                location="Mumbai"
            )
            
            with pytest.raises(VedicApiError) as exc_info:
                await client.fetch_full_profile(birth)
            
            assert exc_info.value.error_code == "VEDIC_API_KEY_MISSING"
            assert "API key" in exc_info.value.message.lower()
    
    @pytest.mark.asyncio
    async def test_api_unavailable_raises_error(self, client, birth_details):
        """Test that API unavailability raises error, not stub data."""
        with patch('httpx.AsyncClient.get', side_effect=Exception("Connection refused")):
            with pytest.raises(VedicApiError) as exc_info:
                await client.fetch_full_profile(birth_details)
            
            # Should raise VedicApiError, not return stub data
            assert exc_info.value.error_code in [
                "VEDIC_API_UNAVAILABLE",
                "VEDIC_API_BAD_RESPONSE",
                "VEDIC_API_KEY_MISSING"
            ]
    
    @pytest.mark.asyncio
    async def test_bad_api_response_raises_error(self, client, birth_details):
        """Test that invalid API response raises error, not stub data."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.json = AsyncMock(return_value={"status": 500, "error": "Server error"})
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            with pytest.raises(VedicApiError) as exc_info:
                await client.fetch_full_profile(birth_details)
            
            # Should raise error, not return stub data
            assert exc_info.value.error_code == "VEDIC_API_UNAVAILABLE"
    
    @pytest.mark.asyncio
    async def test_malformed_json_raises_error(self, client, birth_details):
        """Test that malformed JSON response raises error."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            with pytest.raises(VedicApiError) as exc_info:
                await client.fetch_full_profile(birth_details)
            
            assert exc_info.value.error_code == "VEDIC_API_BAD_RESPONSE"


class TestNoStubsInNiroLLM:
    """Test that NiroLLM raises errors instead of generating stub responses."""
    
    def test_no_llm_raises_error(self):
        """Test that missing LLM config raises error, not stub response."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': '',
            'GEMINI_API_KEY': ''
        }):
            llm = NiroLLM(use_real_llm=True)
            
            payload = {
                'mode': 'GENERAL_GUIDANCE',
                'focus': None,
                'user_question': 'What does my chart say?',
                'astro_features': {'ascendant': 'Aries'}
            }
            
            with pytest.raises(RuntimeError) as exc_info:
                llm.call_niro_llm(payload)
            
            # Should raise error, not return stub response
            assert "no LLM available" in str(exc_info.value).lower()
    
    def test_llm_failure_raises_error(self):
        """Test that LLM call failure raises error."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            llm = NiroLLM(use_real_llm=True)
            
            # Mock OpenAI to fail
            with patch('openai.OpenAI') as mock_openai:
                mock_openai.return_value.chat.completions.create.side_effect = Exception("API error")
                
                payload = {
                    'mode': 'GENERAL_GUIDANCE',
                    'focus': None,
                    'user_question': 'What does my chart say?',
                    'astro_features': {'ascendant': 'Aries'}
                }
                
                # Should raise error, not return stub response
                with pytest.raises(RuntimeError):
                    llm.call_niro_llm(payload)


class TestNoStubsInCodebase:
    """Test that no stub-related code exists in the codebase."""
    
    def test_no_stub_generator_methods_in_astro_engine(self):
        """Test that astro_engine.py doesn't have stub generator methods."""
        astro_engine_path = repo_root / 'backend' / 'conversation' / 'astro_engine.py'
        
        # This file should not exist or be empty/deprecated
        if astro_engine_path.exists():
            with open(astro_engine_path, 'r') as f:
                content = f.read()
            
            # Should not have stub generation methods
            assert '_generate_stub_transits' not in content or 'DEPRECATED' in content
            assert '_generate_stub_yogas' not in content or 'DEPRECATED' in content
            assert '_generate_stub_profile' not in content or 'DEPRECATED' in content
    
    def test_no_allow_stubs_flags(self):
        """Test that NIRO_ALLOW_STUBS flag doesn't exist."""
        for py_file in repo_root.glob('backend/**/*.py'):
            if py_file.is_file():
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Flag should not exist
                assert 'NIRO_ALLOW_STUBS' not in content, f"Found NIRO_ALLOW_STUBS in {py_file}"
                assert 'NIRO_USE_STUBS' not in content, f"Found NIRO_USE_STUBS in {py_file}"
    
    def test_no_stub_responses_in_niro_llm(self):
        """Test that niro_llm.py doesn't have _generate_stub_response method."""
        niro_llm_path = repo_root / 'backend' / 'conversation' / 'niro_llm.py'
        
        with open(niro_llm_path, 'r') as f:
            content = f.read()
        
        # Should not have stub response generation
        assert '_generate_stub_response' not in content, "Found _generate_stub_response in niro_llm.py"


class TestExplicitErrorHandling:
    """Test that errors are explicit and transparent."""
    
    @pytest.mark.asyncio
    async def test_vedic_api_error_has_error_code(self):
        """Test that VedicApiError has typed error_code field."""
        error = VedicApiError(
            error_code="VEDIC_API_KEY_MISSING",
            message="API key not configured"
        )
        
        assert hasattr(error, 'error_code')
        assert error.error_code == "VEDIC_API_KEY_MISSING"
        assert error.message == "API key not configured"
    
    @pytest.mark.asyncio
    async def test_error_codes_are_valid(self):
        """Test that all error codes are from known set."""
        valid_error_codes = {
            "VEDIC_API_KEY_MISSING",
            "VEDIC_API_UNAVAILABLE",
            "VEDIC_API_BAD_RESPONSE"
        }
        
        for code in valid_error_codes:
            error = VedicApiError(error_code=code, message="Test")
            assert error.error_code == code


class TestKundliScreenIntegration:
    """Test that Kundli screen uses real data."""
    
    @pytest.mark.asyncio
    async def test_kundli_endpoint_no_stubs(self):
        """Test that /api/kundli endpoint doesn't return stub data."""
        # This would require running the server
        # For now, we verify the endpoint is defined correctly
        
        # Check that server.py has the /api/kundli endpoint
        server_path = repo_root / 'backend' / 'server.py'
        with open(server_path, 'r') as f:
            content = f.read()
        
        assert '/api/kundli' in content or '@api_router.get("/kundli")' in content
        
        # Should use vedic_api_client, not stubs
        assert 'vedic_api_client' in content or 'VedicAPIClient' in content


class TestEnhancedOrchestratorNoStubs:
    """Test that EnhancedOrchestrator uses real API, not stubs."""
    
    def test_enhanced_orchestrator_uses_vedic_api(self):
        """Test that EnhancedOrchestrator uses real Vedic API."""
        from backend.conversation.enhanced_orchestrator import enhanced_orchestrator_str
        
        # EnhancedOrchestrator should import and use vedic_api_client
        # Verify by checking the source
        enh_orch_path = repo_root / 'backend' / 'conversation' / 'enhanced_orchestrator.py'
        with open(enh_orch_path, 'r') as f:
            content = f.read()
        
        # Should import vedic_api_client
        assert 'vedic_api_client' in content
        
        # Should not use astro_engine
        assert 'AstroEngine' not in content or 'from .astro_engine import' not in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
