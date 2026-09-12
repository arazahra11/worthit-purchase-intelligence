import os
from datetime import date
from typing import Any, Optional

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


# ============================================================
# CLIENT
# ============================================================

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Supabase credentials are missing. "
            "Check your .env file."
        )

    return create_client(url, key)


# ============================================================
# PURCHASES
# ============================================================

def create_purchase(
    client: Client,
    purchase_data: dict[str, Any],
) -> dict:
    response = (
        client
        .table("purchases")
        .insert(purchase_data)
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Purchase was not created."
        )

    return response.data[0]


def get_purchases(
    client: Client,
) -> list[dict]:
    response = (
        client
        .table("purchases")
        .select("*")
        .order(
            "created_at",
            desc=True,
        )
        .execute()
    )

    return response.data or []


def get_purchase_by_id(
    client: Client,
    purchase_id: str,
) -> Optional[dict]:
    response = (
        client
        .table("purchases")
        .select("*")
        .eq(
            "id",
            purchase_id,
        )
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def update_purchase(
    client: Client,
    purchase_id: str,
    update_data: dict[str, Any],
) -> dict:
    response = (
        client
        .table("purchases")
        .update(update_data)
        .eq(
            "id",
            purchase_id,
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Purchase was not updated."
        )

    return response.data[0]


def delete_purchase(
    client: Client,
    purchase_id: str,
) -> None:
    (
        client
        .table("purchases")
        .delete()
        .eq(
            "id",
            purchase_id,
        )
        .execute()
    )


# ============================================================
# USAGE LOGS
# ============================================================

def create_usage_log(
    client: Client,
    purchase_id: str,
    user_id: str,
    used_on: date,
) -> dict:
    """
    Record that a product was used on a particular date.

    Database unique constraint prevents the same purchase
    from being logged more than once on the same day.
    """

    response = (
        client
        .table("usage_logs")
        .insert(
            {
                "purchase_id": purchase_id,
                "user_id": user_id,
                "used_on": used_on.isoformat(),
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Usage log was not created."
        )

    return response.data[0]


def get_usage_logs(
    client: Client,
) -> list[dict]:
    response = (
        client
        .table("usage_logs")
        .select("*")
        .order(
            "used_on",
            desc=True,
        )
        .execute()
    )

    return response.data or []


def get_usage_logs_between(
    client: Client,
    start_date: date,
    end_date: date,
) -> list[dict]:
    response = (
        client
        .table("usage_logs")
        .select("*")
        .gte(
            "used_on",
            start_date.isoformat(),
        )
        .lte(
            "used_on",
            end_date.isoformat(),
        )
        .order(
            "used_on",
            desc=True,
        )
        .execute()
    )

    return response.data or []


def get_usage_log_count(
    client: Client,
) -> int:
    response = (
        client
        .table("usage_logs")
        .select(
            "id",
            count="exact",
        )
        .execute()
    )

    return response.count or 0


def delete_usage_log(
    client: Client,
    usage_log_id: str,
) -> None:
    (
        client
        .table("usage_logs")
        .delete()
        .eq(
            "id",
            usage_log_id,
        )
        .execute()
    )