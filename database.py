import os
from datetime import date
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

try:
    import streamlit as st
except Exception:
    st = None


# ============================================================
# ENV / SECRETS
# ============================================================

load_dotenv()


def _get_config_value(key: str) -> Optional[str]:
    """
    Read config from Streamlit Cloud secrets first,
    then fall back to local .env / environment variables.
    """

    if st is not None:
        try:
            value = st.secrets.get(key)
            if value:
                return str(value)
        except Exception:
            pass

    value = os.getenv(key)

    if value:
        return value

    return None


def get_supabase_client() -> Client:
    url = _get_config_value("SUPABASE_URL")
    key = _get_config_value("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Missing Supabase configuration. "
            "Set SUPABASE_URL and SUPABASE_KEY "
            "in local .env or Streamlit Cloud Secrets."
        )

    return create_client(
        url,
        key,
    )


# ============================================================
# PURCHASES
# ============================================================

def create_purchase(
    client: Client,
    payload: dict,
):
    response = (
        client
        .table("purchases")
        .insert(payload)
        .execute()
    )

    return response.data


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

    rows = response.data or []

    if not rows:
        return None

    return rows[0]


def update_purchase(
    client: Client,
    purchase_id: str,
    payload: dict,
):
    response = (
        client
        .table("purchases")
        .update(payload)
        .eq(
            "id",
            purchase_id,
        )
        .execute()
    )

    return response.data


def delete_purchase(
    client: Client,
    purchase_id: str,
):
    response = (
        client
        .table("purchases")
        .delete()
        .eq(
            "id",
            purchase_id,
        )
        .execute()
    )

    return response.data


# ============================================================
# USAGE LOGS
# ============================================================

def create_usage_log(
    client: Client,
    purchase_id: str,
    user_id: str,
    used_on: date,
):
    payload = {
        "purchase_id":
            purchase_id,

        "user_id":
            user_id,

        "used_on":
            used_on.isoformat(),
    }

    response = (
        client
        .table("usage_logs")
        .insert(payload)
        .execute()
    )

    return response.data


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
    purchase_id: str,
) -> int:
    response = (
        client
        .table("usage_logs")
        .select(
            "id",
            count="exact",
        )
        .eq(
            "purchase_id",
            purchase_id,
        )
        .execute()
    )

    return int(
        response.count
        or 0
    )


def delete_usage_log(
    client: Client,
    usage_log_id: str,
):
    response = (
        client
        .table("usage_logs")
        .delete()
        .eq(
            "id",
            usage_log_id,
        )
        .execute()
    )

    return response.data
