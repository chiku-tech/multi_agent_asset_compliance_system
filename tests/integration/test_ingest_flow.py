"""
Integration tests for the document ingestion flow.

Tests the full HTTP request → ingest handler → Pinecone upsert chain
using moto for S3 and mock clients for Pinecone and OpenAI.
No real network calls are made.
"""

from unittest.mock import MagicMock

import pytest

from tests.integration.helpers import patch_dependencies


@pytest.mark.asyncio
async def test_ingest_create_event(
    async_client, auth_headers, s3_bucket, mock_pinecone_index, mock_embeddings_model
):
    """POST /ingest with create event should return 200 and upsert vectors."""
    # Upload a fake PDF to mock S3
    s3_bucket.put_object(
        Bucket="test-bucket",
        Key="manuals/pump_v2.pdf",
        Body=b"%PDF-1.4 fake pdf content with text",
    )
    mock_pinecone_index.describe_index_stats.return_value = MagicMock(namespaces={})

    with patch_dependencies(
        pinecone=mock_pinecone_index, embeddings=mock_embeddings_model, s3=s3_bucket
    ):
        response = await async_client.post(
            "/api/v1/ingest",
            json={
                "asset_id": "abc-123",
                "event": "create",
                "documents": [
                    {
                        "s3_key": "manuals/pump_v2.pdf",
                        "doc_id": "manual-v2",
                        "doc_type": "user_manual",
                        "filename": "pump_v2.pdf",
                    }
                ],
            },
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["asset_id"] == "abc-123"
    assert body["event"] == "create"
    assert body["namespace"] == "asset_abc-123"


@pytest.mark.asyncio
async def test_ingest_create_idempotent(
    async_client, auth_headers, s3_bucket, mock_pinecone_index, mock_embeddings_model
):
    """POST /ingest with create event on existing namespace should be a no-op."""
    # Namespace already has docs
    mock_pinecone_index.describe_index_stats.return_value = MagicMock(
        namespaces={"asset_abc-123": MagicMock(vector_count=10)}
    )

    with patch_dependencies(
        pinecone=mock_pinecone_index, embeddings=mock_embeddings_model, s3=s3_bucket
    ):
        response = await async_client.post(
            "/api/v1/ingest",
            json={
                "asset_id": "abc-123",
                "event": "create",
                "documents": [
                    {
                        "s3_key": "manuals/pump_v2.pdf",
                        "doc_id": "manual-v2",
                        "doc_type": "user_manual",
                        "filename": "pump_v2.pdf",
                    }
                ],
            },
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    # Should be a no-op — zero vectors processed
    assert body["documents_processed"] == 0
    assert body["vectors_upserted"] == 0


@pytest.mark.asyncio
async def test_ingest_update_requires_single_document(
    async_client, auth_headers, s3_bucket, mock_pinecone_index, mock_embeddings_model
):
    """POST /ingest with update event and multiple documents should return 422."""
    with patch_dependencies(
        pinecone=mock_pinecone_index, embeddings=mock_embeddings_model, s3=s3_bucket
    ):
        response = await async_client.post(
            "/api/v1/ingest",
            json={
                "asset_id": "abc-123",
                "event": "update",
                "documents": [
                    {
                        "s3_key": "a.pdf",
                        "doc_id": "doc-1",
                        "doc_type": "user_manual",
                        "filename": "a.pdf",
                    },
                    {
                        "s3_key": "b.pdf",
                        "doc_id": "doc-2",
                        "doc_type": "safety_sheet",
                        "filename": "b.pdf",
                    },
                ],
            },
            headers=auth_headers,
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ingest_missing_api_key(
    async_client, s3_bucket, mock_pinecone_index, mock_embeddings_model
):
    """POST /ingest without X-API-Key header should return 401."""
    with patch_dependencies(
        pinecone=mock_pinecone_index, embeddings=mock_embeddings_model, s3=s3_bucket
    ):
        response = await async_client.post(
            "/api/v1/ingest",
            json={
                "asset_id": "abc-123",
                "event": "create",
                "documents": [
                    {
                        "s3_key": "a.pdf",
                        "doc_id": "doc-1",
                        "doc_type": "user_manual",
                        "filename": "a.pdf",
                    }
                ],
            },
            # No X-API-Key header
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_check_no_auth_required(async_client):
    """GET /health should return 200 without authentication."""
    response = await async_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_ingest_add_event(
    async_client, auth_headers, s3_bucket, mock_pinecone_index, mock_embeddings_model
):
    """POST /ingest with add event should return 200 and add vectors to existing namespace."""
    s3_bucket.put_object(
        Bucket="test-bucket",
        Key="manuals/pump_v3.pdf",
        Body=b"%PDF-1.4 fake pdf content with text",
    )
    mock_pinecone_index.describe_index_stats.return_value = MagicMock(
        namespaces={"asset_abc-123": MagicMock(vector_count=5)}
    )

    with patch_dependencies(
        pinecone=mock_pinecone_index, embeddings=mock_embeddings_model, s3=s3_bucket
    ):
        response = await async_client.post(
            "/api/v1/ingest",
            json={
                "asset_id": "abc-123",
                "event": "add",
                "documents": [
                    {
                        "s3_key": "manuals/pump_v3.pdf",
                        "doc_id": "manual-v3",
                        "doc_type": "user_manual",
                        "filename": "pump_v3.pdf",
                    }
                ],
            },
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["asset_id"] == "abc-123"
    assert body["event"] == "add"
    assert body["documents_processed"] == 1


@pytest.mark.asyncio
async def test_ingest_update_event(
    async_client, auth_headers, s3_bucket, mock_pinecone_index, mock_embeddings_model
):
    """POST /ingest with update event should delete old doc vectors and insert new ones."""
    s3_bucket.put_object(
        Bucket="test-bucket",
        Key="manuals/pump_v2_updated.pdf",
        Body=b"%PDF-1.4 updated fake pdf content with text",
    )
    # Namespace has old vectors
    mock_pinecone_index.describe_index_stats.return_value = MagicMock(
        namespaces={"asset_abc-123": MagicMock(vector_count=10)}
    )
    mock_pinecone_index.list.return_value = iter([["vec1", "vec2"]])

    with patch_dependencies(
        pinecone=mock_pinecone_index, embeddings=mock_embeddings_model, s3=s3_bucket
    ):
        response = await async_client.post(
            "/api/v1/ingest",
            json={
                "asset_id": "abc-123",
                "event": "update",
                "documents": [
                    {
                        "s3_key": "manuals/pump_v2_updated.pdf",
                        "doc_id": "manual-v2",
                        "doc_type": "user_manual",
                        "filename": "pump_v2_updated.pdf",
                    }
                ],
            },
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["asset_id"] == "abc-123"
    assert body["event"] == "update"
    assert body["documents_processed"] == 1
    # delete_by_doc_id is called
    mock_pinecone_index.delete.assert_called_once_with(
        ids=["vec1", "vec2"],
        namespace="asset_abc-123",
    )


@pytest.mark.asyncio
async def test_upload_and_ingest_documents(
    async_client, auth_headers, s3_bucket, mock_pinecone_index, mock_embeddings_model
):
    """POST /ingest/upload with files should upload to S3 and ingest."""
    mock_pinecone_index.describe_index_stats.return_value = MagicMock(namespaces={})

    with patch_dependencies(
        pinecone=mock_pinecone_index, embeddings=mock_embeddings_model, s3=s3_bucket
    ):
        # Create a fake PDF file for upload using proper tuple format
        fake_pdf = ("test_manual.pdf", b"%PDF-1.4 fake pdf content", "application/pdf")
        response = await async_client.post(
            "/api/v1/ingest/upload",
            data={
                "asset_id": "test-upload-asset",
                "event": "create",
            },
            files={"files": fake_pdf},
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["asset_id"] == "test-upload-asset"
    assert body["event"] == "create"
    assert body["documents_processed"] == 1


@pytest.mark.asyncio
async def test_upload_invalid_asset_id(
    async_client, auth_headers, s3_bucket, mock_pinecone_index, mock_embeddings_model
):
    """POST /ingest/upload with invalid asset_id should return 400."""
    with patch_dependencies(
        pinecone=mock_pinecone_index, embeddings=mock_embeddings_model, s3=s3_bucket
    ):
        fake_pdf = ("test.pdf", b"%PDF-1.4 fake pdf content", "application/pdf")
        response = await async_client.post(
            "/api/v1/ingest/upload",
            data={
                "asset_id": "../../etc/passwd",
                "event": "create",
            },
            files={"files": fake_pdf},
            headers=auth_headers,
        )

    assert response.status_code == 400
    assert "asset_id" in response.json()["detail"]["message"].lower()
