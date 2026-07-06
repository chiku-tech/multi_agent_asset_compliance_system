"""
DynamoDB service — audit run idempotency tracking.

Stores a record per audit run keyed on ``run_id``.  Before executing the
LangGraph pipeline the audit endpoint checks this table:

  - run not found  → proceed normally; record IN_PROGRESS first
  - IN_PROGRESS    → return HTTP 409 (another invocation is running)
  - COMPLETE       → return the cached verdict immediately (HTTP 200)

This prevents duplicate LLM expenditure when backend client retries a timed-out
Lambda request, and gives the system a single source of truth for every
audit verdict.

Table schema
------------
  PK (run_id)          : str  — the backend client-supplied idempotency key
  asset_id             : str  — for GSI / query by asset
  status               : str  — IN_PROGRESS | COMPLETE | FAILED | ERASED
  verdict              : str  — JSON-encoded verdict dict (set on COMPLETE)
  created_at           : str  — ISO 8601 UTC
  updated_at           : str  — ISO 8601 UTC
  expires_at           : int  — Unix epoch for DynamoDB TTL (30-day retention)
"""

import asyncio
import json
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)

_TTL_DAYS = 30

STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_COMPLETE = "COMPLETE"
STATUS_FAILED = "FAILED"
STATUS_ERASED = "ERASED"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _ttl_epoch() -> int:
    return int((datetime.now(UTC) + timedelta(days=_TTL_DAYS)).timestamp())


# ── Sync helpers (run in thread pool to avoid blocking the event loop) ──────


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
def _put_audit_run_sync(
    dynamodb_client: Any,
    table_name: str,
    run_id: str,
    asset_id: str,
) -> None:
    now = _now_iso()
    dynamodb_client.put_item(
        TableName=table_name,
        Item={
            "run_id": {"S": run_id},
            "asset_id": {"S": asset_id},
            "status": {"S": STATUS_IN_PROGRESS},
            "created_at": {"S": now},
            "updated_at": {"S": now},
            "expires_at": {"N": str(_ttl_epoch())},
        },
        ConditionExpression="attribute_not_exists(run_id)",
    )
    logger.info("audit_run_created", run_id=run_id, asset_id=asset_id)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
def _get_audit_run_sync(
    dynamodb_client: Any,
    table_name: str,
    run_id: str,
) -> dict[str, Any] | None:
    response = dynamodb_client.get_item(
        TableName=table_name,
        Key={"run_id": {"S": run_id}},
        ConsistentRead=True,
    )
    item = response.get("Item")
    if not item:
        return None

    result: dict[str, Any] = {
        "run_id": item["run_id"]["S"],
        "asset_id": item["asset_id"]["S"],
        "status": item["status"]["S"],
        "created_at": item["created_at"]["S"],
        "updated_at": item["updated_at"]["S"],
    }
    if "verdict" in item:
        result["verdict"] = json.loads(item["verdict"]["S"])

    logger.debug("audit_run_fetched", run_id=run_id, status=result["status"])
    return result


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
def _complete_audit_run_sync(
    dynamodb_client: Any,
    table_name: str,
    run_id: str,
    verdict: dict[str, Any],
) -> None:
    dynamodb_client.update_item(
        TableName=table_name,
        Key={"run_id": {"S": run_id}},
        UpdateExpression="SET #s = :s, verdict = :v, updated_at = :u",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": {"S": STATUS_COMPLETE},
            ":v": {"S": json.dumps(verdict, default=str)},
            ":u": {"S": _now_iso()},
        },
    )
    logger.info("audit_run_completed", run_id=run_id)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
def _fail_audit_run_sync(
    dynamodb_client: Any,
    table_name: str,
    run_id: str,
    error: str,
) -> None:
    dynamodb_client.update_item(
        TableName=table_name,
        Key={"run_id": {"S": run_id}},
        UpdateExpression="SET #s = :s, error_message = :e, updated_at = :u",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": {"S": STATUS_FAILED},
            ":e": {"S": error[:1000]},
            ":u": {"S": _now_iso()},
        },
    )
    logger.warning("audit_run_failed", run_id=run_id, error=error[:200])


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
def _update_item_erased(
    dynamodb_client: Any,
    table_name: str,
    run_id: str,
) -> None:
    dynamodb_client.update_item(
        TableName=table_name,
        Key={"run_id": {"S": run_id}},
        UpdateExpression="SET #s = :s, updated_at = :u",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": {"S": STATUS_ERASED},
            ":u": {"S": _now_iso()},
        },
    )


def _erase_asset_runs_sync(
    dynamodb_client: Any,
    table_name: str,
    asset_id: str,
) -> int:
    erased_count = 0
    last_evaluated_key: dict[str, Any] | None = None

    while True:
        kwargs: dict[str, Any] = {
            "TableName": table_name,
            "IndexName": "AssetIdIndex",
            "KeyConditionExpression": "asset_id = :aid",
            "ExpressionAttributeValues": {":aid": {"S": asset_id}},
            "ProjectionExpression": "run_id",
        }
        if last_evaluated_key:
            kwargs["ExclusiveStartKey"] = last_evaluated_key

        response = dynamodb_client.query(**kwargs)
        items = response.get("Items", [])

        for item in items:
            _update_item_erased(dynamodb_client, table_name, item["run_id"]["S"])
            erased_count += 1

        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:
            break

    logger.info("asset_runs_erased", asset_id=asset_id, count=erased_count)
    return erased_count


def _get_asset_run_summary_sync(
    dynamodb_client: Any,
    table_name: str,
    asset_id: str,
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    latest_run_at: str | None = None
    total_runs = 0
    last_evaluated_key: dict[str, Any] | None = None

    while True:
        kwargs: dict[str, Any] = {
            "TableName": table_name,
            "IndexName": "AssetIdIndex",
            "KeyConditionExpression": "asset_id = :aid",
            "ExpressionAttributeValues": {":aid": {"S": asset_id}},
            "ProjectionExpression": "run_id, #s, created_at",
            "ExpressionAttributeNames": {"#s": "status"},
        }
        if last_evaluated_key:
            kwargs["ExclusiveStartKey"] = last_evaluated_key

        response = dynamodb_client.query(**kwargs)
        items = response.get("Items", [])

        for item in items:
            total_runs += 1
            status = item["status"]["S"]
            status_counts[status] = status_counts.get(status, 0) + 1
            created = item["created_at"]["S"]
            if latest_run_at is None or created > latest_run_at:
                latest_run_at = created

        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:
            break

    return {
        "asset_id": asset_id,
        "total_runs": total_runs,
        "status_counts": status_counts,
        "latest_run_at": latest_run_at,
    }


# ── Async public API ───────────────────────────────────────────────────────


async def put_audit_run(
    dynamodb_client: Any,
    table_name: str,
    run_id: str,
    asset_id: str,
) -> None:
    return await asyncio.to_thread(
        _put_audit_run_sync, dynamodb_client, table_name, run_id, asset_id
    )


async def get_audit_run(
    dynamodb_client: Any,
    table_name: str,
    run_id: str,
) -> dict[str, Any] | None:
    return await asyncio.to_thread(
        _get_audit_run_sync, dynamodb_client, table_name, run_id
    )


async def complete_audit_run(
    dynamodb_client: Any,
    table_name: str,
    run_id: str,
    verdict: dict[str, Any],
) -> None:
    return await asyncio.to_thread(
        _complete_audit_run_sync, dynamodb_client, table_name, run_id, verdict
    )


async def fail_audit_run(
    dynamodb_client: Any,
    table_name: str,
    run_id: str,
    error: str,
) -> None:
    return await asyncio.to_thread(
        _fail_audit_run_sync, dynamodb_client, table_name, run_id, error
    )


async def erase_asset_runs(
    dynamodb_client: Any,
    table_name: str,
    asset_id: str,
) -> int:
    return await asyncio.to_thread(
        _erase_asset_runs_sync, dynamodb_client, table_name, asset_id
    )


async def get_asset_run_summary(
    dynamodb_client: Any,
    table_name: str,
    asset_id: str,
) -> dict[str, Any]:
    return await asyncio.to_thread(
        _get_asset_run_summary_sync, dynamodb_client, table_name, asset_id
    )
