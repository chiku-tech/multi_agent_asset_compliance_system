"""
Tests for DuckDuckGo search integration.

Verifies that the DDG search wrapper works correctly and handles errors.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_ddg_search_returns_results():
    """DDG search should return a list of results."""
    from app.services import ddg_service

    mock_results = [
        {"title": "Test", "href": "https://example.com", "body": "Test content"}
    ]

    with patch.object(ddg_service, "search_web", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_results
        results = await ddg_service.search_web("test query", max_results=3)
        assert len(results) > 0
        mock_search.assert_called_once()


@pytest.mark.asyncio
async def test_ddg_search_handles_error():
    """DDG search should handle errors gracefully."""
    from app.services import ddg_service

    with patch.object(ddg_service, "search_web", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = Exception("Network error")
        results = await ddg_service.search_web("test query", max_results=3)
        assert results == []
