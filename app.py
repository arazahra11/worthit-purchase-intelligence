from calendar import monthcalendar
from datetime import date, timedelta
from html import escape
import textwrap

import streamlit as st

from database import (
    create_purchase,
    create_usage_log,
    delete_purchase,
    delete_usage_log,
    get_purchases,
    get_supabase_client,
    get_usage_logs,
    update_purchase,
)

from scoring import calculate_worthit_score


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="WorthIt — Personal Purchase Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HTML HELPER
# ============================================================

def ui(content: str) -> None:
    st.html(textwrap.dedent(content).strip())


# ============================================================
# GLOBAL DESIGN SYSTEM
# ============================================================

ui(
    """
    <style>
    :root {
        --wi-bg: #f7f7fc;
        --wi-surface: rgba(255,255,255,.88);
        --wi-text: #111426;
        --wi-muted: #70778b;

        --wi-purple: #705cff;
        --wi-purple-2: #9b70ff;
        --wi-indigo: #25214f;
        --wi-mint: #54d6bb;
        --wi-coral: #ff7878;
        --wi-gold: #ffd56f;
        --wi-sky: #70d7ff;
        --wi-pink: #ff8ecf;
        --wi-peach: #ffb18a;

        --wi-border: rgba(17,20,38,.08);
        --wi-border-strong: rgba(17,20,38,.13);

        --wi-shadow-sm: 0 10px 28px rgba(34,39,78,.06);
        --wi-shadow: 0 18px 48px rgba(34,39,78,.09);
        --wi-shadow-lg: 0 28px 80px rgba(31,29,86,.16);
    }

    html {
        scroll-behavior: smooth;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(
                circle at 8% 8%,
                rgba(112,92,255,.18),
                transparent 25%
            ),
            radial-gradient(
                circle at 88% 10%,
                rgba(84,214,187,.16),
                transparent 22%
            ),
            radial-gradient(
                circle at 82% 92%,
                rgba(255,120,120,.14),
                transparent 26%
            ),
            linear-gradient(
                140deg,
                #faf8ff 0%,
                #f6fbff 48%,
                #fff9fb 100%
            );
        color: var(--wi-text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.4rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        color: var(--wi-text);
        letter-spacing: -.035em;
    }

    p, label {
        line-height: 1.65;
    }

    .wi-brand {
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 24px;
    }

    .wi-logo {
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        color: white;
        font-size: 22px;
        font-weight: 950;
        background:
            linear-gradient(
                135deg,
                #705cff 0%,
                #9a70ff 52%,
                #ff7878 100%
            );
        box-shadow:
            0 12px 30px rgba(112,92,255,.28);
    }

    .wi-brand-name {
        color: var(--wi-text);
        font-size: 24px;
        font-weight: 950;
        letter-spacing: -.04em;
        line-height: 1;
    }

    .wi-brand-sub {
        margin-top: 5px;
        color: var(--wi-muted);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .105em;
        text-transform: uppercase;
    }

    .wi-kicker {
        color: var(--wi-purple);
        font-size: 10px;
        font-weight: 900;
        letter-spacing: .145em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .wi-page-title {
        max-width: 880px;
        color: var(--wi-text);
        font-size: clamp(32px, 4.8vw, 50px);
        line-height: 1.02;
        font-weight: 950;
        letter-spacing: -.055em;
        margin-bottom: 10px;
    }

    .wi-page-copy {
        max-width: 760px;
        color: var(--wi-muted);
        font-size: 14px;
        line-height: 1.75;
        margin-bottom: 28px;
    }

    .wi-hero {
        position: relative;
        overflow: hidden;
        min-height: 430px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 58px;
        border-radius: 34px;
        color: white;
        background:
            linear-gradient(
                125deg,
                #11142d 0%,
                #292761 50%,
                #654bd0 100%
            );
        box-shadow: var(--wi-shadow-lg);
        margin-bottom: 34px;
    }

    .wi-hero::before,
    .wi-hero::after {
        content: "";
        position: absolute;
        border-radius: 50%;
        animation: wiFloat 9s ease-in-out infinite;
    }

    .wi-hero::before {
        width: 430px;
        height: 430px;
        right: -125px;
        top: -165px;
        background: rgba(84,214,187,.17);
    }

    .wi-hero::after {
        width: 300px;
        height: 300px;
        right: 90px;
        bottom: -205px;
        background: rgba(255,120,120,.22);
        animation-delay: 1.2s;
    }

    .wi-hero-chip {
        position: relative;
        z-index: 2;
        width: fit-content;
        padding: 8px 13px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.14);
        background: rgba(255,255,255,.08);
        color: rgba(255,255,255,.9);
        font-size: 10px;
        font-weight: 900;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-bottom: 22px;
    }

    .wi-hero-title {
        position: relative;
        z-index: 2;
        max-width: 790px;
        color: white;
        font-size: clamp(42px, 5.7vw, 72px);
        line-height: .98;
        font-weight: 950;
        letter-spacing: -.065em;
        margin-bottom: 22px;
    }

    .wi-hero-accent {
        background:
            linear-gradient(
                90deg,
                var(--wi-gold),
                #ff9c8a,
                var(--wi-sky)
            );
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .wi-hero-copy {
        position: relative;
        z-index: 2;
        max-width: 650px;
        color: rgba(255,255,255,.74);
        font-size: 16px;
        line-height: 1.78;
    }

    @keyframes wiFloat {
        0%,100% {
            transform: translateY(0px) translateX(0px);
        }
        50% {
            transform: translateY(10px) translateX(-6px);
        }
    }

    .wi-card {
        position: relative;
        overflow: hidden;
        height: 100%;
        padding: 25px;
        border-radius: 22px;
        border: 1px solid var(--wi-border);
        background: var(--wi-surface);
        backdrop-filter: blur(18px);
        box-shadow: var(--wi-shadow);
        transition:
            transform .22s ease,
            box-shadow .22s ease,
            border-color .22s ease;
    }

    .wi-card:hover {
        transform: translateY(-4px);
        box-shadow:
            0 24px 58px rgba(34,39,78,.12);
        border-color: rgba(112,92,255,.16);
    }

    .wi-card::after {
        content: "";
        position: absolute;
        width: 150px;
        height: 150px;
        right: -48px;
        top: -58px;
        border-radius: 50%;
        background:
            linear-gradient(
                135deg,
                rgba(112,92,255,.14),
                rgba(84,214,187,.10)
            );
    }

    .wi-card-icon {
        position: relative;
        z-index: 2;
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 17px;
        border-radius: 14px;
        color: var(--wi-indigo);
        font-size: 20px;
        font-weight: 900;
        background:
            linear-gradient(
                135deg,
                rgba(112,92,255,.13),
                rgba(84,214,187,.14)
            );
    }

    .wi-card-title {
        position: relative;
        z-index: 2;
        color: var(--wi-text);
        font-size: 17px;
        font-weight: 900;
        margin-bottom: 7px;
    }

    .wi-card-copy {
        position: relative;
        z-index: 2;
        color: var(--wi-muted);
        font-size: 12px;
        line-height: 1.7;
    }

    .wi-welcome {
        position: relative;
        overflow: hidden;
        padding: 34px;
        border-radius: 28px;
        color: white;
        background:
            linear-gradient(
                120deg,
                #151832 0%,
                #353176 45%,
                #705cff 100%
            );
        box-shadow:
            0 22px 62px rgba(31,29,86,.17);
        margin-bottom: 25px;
    }

    .wi-welcome::before,
    .wi-welcome::after {
        content: "";
        position: absolute;
        border-radius: 50%;
        animation: wiFloat 9s ease-in-out infinite;
    }

    .wi-welcome::before {
        width: 240px;
        height: 240px;
        top: -90px;
        right: -70px;
        background: rgba(84,214,187,.17);
    }

    .wi-welcome::after {
        width: 180px;
        height: 180px;
        bottom: -80px;
        left: 45%;
        background: rgba(255,120,120,.15);
        animation-delay: 1.3s;
    }

    .wi-welcome-kicker {
        position: relative;
        z-index: 2;
        color: rgba(255,255,255,.62);
        font-size: 10px;
        font-weight: 900;
        letter-spacing: .14em;
        text-transform: uppercase;
    }

    .wi-welcome-title {
        position: relative;
        z-index: 2;
        max-width: 720px;
        margin-top: 8px;
        color: white;
        font-size: 30px;
        font-weight: 950;
        line-height: 1.06;
        letter-spacing: -.045em;
    }

    .wi-welcome-copy {
        position: relative;
        z-index: 2;
        max-width: 670px;
        margin-top: 10px;
        color: rgba(255,255,255,.74);
        font-size: 13px;
        line-height: 1.65;
    }

    .wi-metric {
        position: relative;
        overflow: hidden;
        min-height: 148px;
        padding: 22px;
        border-radius: 22px;
        border: 1px solid var(--wi-border);
        background: rgba(255,255,255,.90);
        box-shadow: var(--wi-shadow-sm);
        transition:
            transform .18s ease,
            box-shadow .18s ease;
    }

    .wi-metric:hover {
        transform: translateY(-3px);
        box-shadow: var(--wi-shadow);
    }

    .wi-metric::after {
        content: "";
        position: absolute;
        width: 120px;
        height: 120px;
        right: -28px;
        bottom: -42px;
        border-radius: 50%;
        background:
            linear-gradient(
                135deg,
                rgba(112,92,255,.10),
                rgba(255,142,207,.10)
            );
    }

    .wi-metric-label {
        position: relative;
        z-index: 2;
        color: var(--wi-muted);
        font-size: 10px;
        font-weight: 900;
        letter-spacing: .11em;
        text-transform: uppercase;
    }

    .wi-metric-value {
        position: relative;
        z-index: 2;
        margin-top: 10px;
        color: var(--wi-text);
        font-size: 33px;
        font-weight: 950;
        letter-spacing: -.055em;
    }

    .wi-metric-note {
        position: relative;
        z-index: 2;
        margin-top: 5px;
        color: var(--wi-muted);
        font-size: 11px;
        line-height: 1.45;
    }

    .wi-item {
        position: relative;
        overflow: hidden;
        padding: 23px;
        border-radius: 22px;
        border: 1px solid var(--wi-border);
        background: rgba(255,255,255,.92);
        box-shadow: var(--wi-shadow-sm);
        margin-bottom: 10px;
        transition:
            transform .18s ease,
            box-shadow .18s ease;
    }

    .wi-item:hover {
        transform: translateY(-2px);
        box-shadow: var(--wi-shadow);
    }

    .wi-item::after {
        content: "";
        position: absolute;
        width: 190px;
        height: 190px;
        right: -90px;
        top: -82px;
        border-radius: 50%;
        background:
            var(
                --item-accent,
                linear-gradient(
                    135deg,
                    rgba(112,92,255,.12),
                    rgba(84,214,187,.09)
                )
            );
    }

    .wi-item-name {
        position: relative;
        z-index: 2;
        color: var(--wi-text);
        font-size: 18px;
        font-weight: 950;
    }

    .wi-item-meta {
        position: relative;
        z-index: 2;
        margin-top: 6px;
        margin-bottom: 12px;
        color: var(--wi-muted);
        font-size: 11px;
    }

    .wi-pill {
        position: relative;
        z-index: 2;
        display: inline-block;
        padding: 6px 11px;
        border-radius: 999px;
        color: var(--wi-purple);
        background: rgba(112,92,255,.10);
        font-size: 11px;
        font-weight: 900;
    }

    .wi-category-badge {
        position: relative;
        z-index: 2;
        display: inline-flex;
        align-items: center;
        gap: 7px;
        margin-left: 8px;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        color: #3a3560;
        background: rgba(255,255,255,.76);
        border: 1px solid rgba(17,20,38,.06);
    }

    .wi-insight-box {
        position: relative;
        overflow: hidden;
        min-height: 190px;
        padding: 25px;
        border-radius: 24px;
        color: white;
        background:
            linear-gradient(
                135deg,
                #6a58ff 0%,
                #ab6bff 100%
            );
        box-shadow:
            0 20px 55px rgba(112,92,255,.22);
    }

    .wi-insight-box::after {
        content: "";
        position: absolute;
        width: 170px;
        height: 170px;
        right: -65px;
        bottom: -80px;
        border-radius: 50%;
        background: rgba(255,255,255,.11);
    }

    .wi-insight-box.secondary {
        background:
            linear-gradient(
                135deg,
                #18b9a0 0%,
                #5bd8c1 100%
            );
    }

    .wi-insight-box.coral {
        background:
            linear-gradient(
                135deg,
                #ff7878 0%,
                #ff9e89 100%
            );
    }

    .wi-insight-title {
        position: relative;
        z-index: 2;
        font-size: 19px;
        font-weight: 950;
        margin-bottom: 8px;
    }

    .wi-insight-copy {
        position: relative;
        z-index: 2;
        font-size: 13px;
        line-height: 1.75;
        color: rgba(255,255,255,.87);
    }

    .wi-note-card {
        min-height: 150px;
        padding: 20px;
        border-radius: 20px;
        background: rgba(255,255,255,.72);
        border: 1px solid var(--wi-border);
        box-shadow: var(--wi-shadow-sm);
    }

    .wi-note-title {
        font-size: 16px;
        font-weight: 900;
        color: var(--wi-text);
        margin-bottom: 6px;
    }

    .wi-note-copy {
        font-size: 12px;
        color: var(--wi-muted);
        line-height: 1.75;
    }

    .wi-callout {
        padding: 19px 20px;
        border-radius: 18px;
        border: 1px solid rgba(112,92,255,.10);
        background:
            linear-gradient(
                135deg,
                rgba(112,92,255,.07),
                rgba(84,214,187,.055)
            );
        color: var(--wi-muted);
        font-size: 12px;
        line-height: 1.7;
        margin-bottom: 18px;
    }

    .wi-account {
        padding: 15px;
        border-radius: 17px;
        border: 1px solid var(--wi-border);
        background:
            linear-gradient(
                135deg,
                rgba(112,92,255,.07),
                rgba(84,214,187,.055)
            );
        margin-top: 8px;
        margin-bottom: 10px;
    }

    .wi-account-label {
        color: var(--wi-muted);
        font-size: 9px;
        font-weight: 900;
        letter-spacing: .12em;
        text-transform: uppercase;
    }

    .wi-account-email {
        margin-top: 5px;
        color: var(--wi-text);
        font-size: 11px;
        font-weight: 750;
        word-break: break-word;
    }

    .wi-nav-group {
        margin-top: 20px;
        margin-bottom: 8px;
        color: #989dab;
        font-size: 9px;
        font-weight: 900;
        letter-spacing: .145em;
        text-transform: uppercase;
    }

    [data-testid="stSidebar"] {
        background: rgba(255,255,255,.97);
        border-right: 1px solid var(--wi-border);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.8rem;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        min-height: 44px;
        border-radius: 13px;
        font-weight: 850;
        transition:
            transform .15s ease,
            box-shadow .15s ease,
            border-color .15s ease;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px);
    }

    button[kind="primary"] {
        border: none !important;
        color: white !important;
        background:
            linear-gradient(
                135deg,
                #705cff,
                #956cff
            ) !important;
        box-shadow:
            0 9px 20px rgba(112,92,255,.23);
    }

    button[kind="secondary"] {
        border:
            1px solid var(--wi-border-strong) !important;
        background:
            rgba(255,255,255,.84) !important;
        color: var(--wi-text) !important;
    }

    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    [role="combobox"]:focus-visible {
        outline:
            3px solid rgba(112,92,255,.25) !important;
        outline-offset: 2px;
    }

    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: .001ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: .001ms !important;
            scroll-behavior: auto !important;
        }
    }

    @media (max-width: 900px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .wi-hero {
            min-height: 390px;
            padding: 38px 28px;
            border-radius: 26px;
        }

        .wi-hero-title {
            font-size: 44px;
        }

        .wi-page-title {
            font-size: 34px;
        }
    }

    @media (max-width: 640px) {
        .wi-hero {
            min-height: 360px;
            padding: 32px 22px;
        }

        .wi-hero-title {
            font-size: 38px;
        }

        .wi-hero-copy {
            font-size: 14px;
        }

        .wi-page-title {
            font-size: 31px;
        }

        .wi-metric {
            min-height: 116px;
        }

        .wi-metric-value {
            font-size: 28px;
        }

        .wi-category-badge {
            display: none;
        }
    }
    </style>
    """
)


# ============================================================
# SUPABASE / SESSION
# ============================================================

supabase = get_supabase_client()

DEFAULT_STATE = {
    "user": None,
    "access_token": None,
    "refresh_token": None,
    "page": "Overview",
    "editing_purchase_id": None,
    "deleting_purchase_id": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# AUTH HELPERS
# ============================================================

def save_auth(response) -> None:
    if response.user:
        st.session_state.user = response.user

    if response.session:
        st.session_state.access_token = (
            response.session.access_token
        )

        st.session_state.refresh_token = (
            response.session.refresh_token
        )


def restore_session() -> None:
    if (
        not st.session_state.access_token
        or not st.session_state.refresh_token
    ):
        return

    try:
        response = supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token,
        )

        save_auth(response)

    except Exception:
        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.refresh_token = None


def logout() -> None:
    try:
        supabase.auth.sign_out()

    finally:
        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.page = "Overview"
        st.session_state.editing_purchase_id = None
        st.session_state.deleting_purchase_id = None
        st.rerun()


restore_session()


# ============================================================
# GENERAL HELPERS
# ============================================================

CATEGORY_OPTIONS = [
    "Skincare",
    "Makeup",
    "Haircare",
    "Bodycare",
    "Fragrance",
    "Fashion",
    "Shoes",
    "Electronics",
    "Food & Drink",
    "Restaurant",
    "Entertainment",
    "Treatment",
    "Travel",
    "Home",
    "Lifestyle",
    "Other",
]

USAGE_OPTIONS = [
    "Not sure yet",
    "Almost daily",
    "Frequent",
    "Frequent / rotating",
    "Weekly",
    "Occasional",
    "Rare",
]


def render_brand() -> None:
    ui(
        """
        <div
            class="wi-brand"
            aria-label="WorthIt brand"
        >
            <div
                class="wi-logo"
                aria-label="WorthIt logo"
            >
                W
            </div>

            <div>
                <div class="wi-brand-name">
                    WorthIt
                </div>

                <div class="wi-brand-sub">
                    Personal Purchase Intelligence
                </div>
            </div>
        </div>
        """
    )


def format_idr(value) -> str:
    return (
        "Rp"
        + f"{int(float(value)):,.0f}".replace(",", ".")
    )


def category_style(category: str) -> tuple[str, str]:
    mapping = {
        "Makeup": (
            "💄",
            "linear-gradient(135deg, rgba(255,142,207,.25), rgba(255,120,120,.18))",
        ),
        "Skincare": (
            "🫧",
            "linear-gradient(135deg, rgba(112,92,255,.18), rgba(112,215,255,.20))",
        ),
        "Haircare": (
            "🧴",
            "linear-gradient(135deg, rgba(255,213,111,.24), rgba(255,177,138,.18))",
        ),
        "Bodycare": (
            "🛁",
            "linear-gradient(135deg, rgba(84,214,187,.22), rgba(112,215,255,.16))",
        ),
        "Fragrance": (
            "🌸",
            "linear-gradient(135deg, rgba(255,142,207,.24), rgba(255,177,138,.18))",
        ),
        "Fashion": (
            "👜",
            "linear-gradient(135deg, rgba(255,177,138,.20), rgba(255,142,207,.18))",
        ),
        "Shoes": (
            "👟",
            "linear-gradient(135deg, rgba(112,92,255,.18), rgba(84,214,187,.16))",
        ),
        "Electronics": (
            "🔌",
            "linear-gradient(135deg, rgba(112,215,255,.20), rgba(112,92,255,.16))",
        ),
        "Food & Drink": (
            "🍜",
            "linear-gradient(135deg, rgba(255,213,111,.24), rgba(255,120,120,.14))",
        ),
        "Restaurant": (
            "🍽️",
            "linear-gradient(135deg, rgba(255,177,138,.22), rgba(255,213,111,.16))",
        ),
        "Entertainment": (
            "🎟️",
            "linear-gradient(135deg, rgba(154,112,255,.20), rgba(255,142,207,.17))",
        ),
        "Treatment": (
            "✨",
            "linear-gradient(135deg, rgba(84,214,187,.19), rgba(255,213,111,.15))",
        ),
        "Travel": (
            "✈️",
            "linear-gradient(135deg, rgba(112,215,255,.20), rgba(84,214,187,.14))",
        ),
        "Home": (
            "🏠",
            "linear-gradient(135deg, rgba(255,177,138,.17), rgba(84,214,187,.12))",
        ),
        "Lifestyle": (
            "🌷",
            "linear-gradient(135deg, rgba(255,142,207,.20), rgba(112,92,255,.16))",
        ),
        "Other": (
            "🪄",
            "linear-gradient(135deg, rgba(112,92,255,.16), rgba(84,214,187,.14))",
        ),
    }

    return mapping.get(
        category,
        mapping["Other"],
    )


def purchase_score(purchase: dict) -> dict:
    purchased_on = None

    if purchase.get("purchase_date"):
        purchased_on = date.fromisoformat(
            purchase["purchase_date"]
        )

    return calculate_worthit_score(
        purchase_type=purchase["purchase_type"],
        satisfaction=int(
            purchase["satisfaction"]
        ),
        would_buy_again=purchase["would_buy_again"],
        usage_frequency=purchase.get(
            "usage_frequency"
        ),
        purchase_date=purchased_on,
        purchase_date_precision=purchase.get(
            "date_precision",
            "Actual",
        ),
        satisfaction_is_verified=purchase.get(
            "satisfaction_is_verified",
            True,
        ),
        repurchase_is_verified=purchase.get(
            "repurchase_is_verified",
            True,
        ),
        value_for_money=purchase.get(
            "value_for_money"
        ),
        value_for_money_is_verified=True,
    )


# ============================================================
# AUTH PAGE
# ============================================================

def render_auth_page() -> None:
    render_brand()

    ui(
        """
        <section
            class="wi-hero"
            aria-label="WorthIt introduction"
        >
            <div class="wi-hero-chip">
                ✦ Purchase Intelligence
            </div>

            <div class="wi-hero-title">
                Buy with intention.
                <br>
                Learn what was
                <span class="wi-hero-accent">
                    actually worth it.
                </span>
            </div>

            <div class="wi-hero-copy">
                WorthIt helps you understand what you
                truly use, what you would buy again,
                what you regret, and which purchases
                deserve your money next time.
            </div>
        </section>
        """
    )

    left, right = st.columns(
        [1.05, .95],
        gap="large",
    )

    with left:
        ui(
            """
            <div class="wi-card">
                <div class="wi-card-icon">✦</div>

                <div class="wi-card-title">
                    More than expense tracking
                </div>

                <div class="wi-card-copy">
                    WorthIt looks at purchase quality:
                    satisfaction, repurchase intention,
                    value for money, and actual usage.
                </div>
            </div>
            """
        )

    with right:
        login_tab, register_tab = st.tabs(
            [
                "Log in",
                "Create account",
            ]
        )

        with login_tab:
            email = st.text_input(
                "Email",
                placeholder="you@example.com",
            )

            password = st.text_input(
                "Password",
                type="password",
            )

            if st.button(
                "Log in to WorthIt",
                use_container_width=True,
                type="primary",
            ):
                if not email.strip() or not password:
                    st.warning(
                        "Enter your email and password."
                    )

                else:
                    try:
                        with st.spinner(
                            "Signing you in..."
                        ):
                            response = (
                                supabase.auth
                                .sign_in_with_password(
                                    {
                                        "email":
                                            email.strip(),
                                        "password":
                                            password,
                                    }
                                )
                            )

                        save_auth(response)
                        st.toast(
                            "Welcome back ✨"
                        )
                        st.rerun()

                    except Exception:
                        st.error(
                            "Login failed. Check your "
                            "email and password."
                        )

        with register_tab:
            reg_email = st.text_input(
                "Email",
                key="reg_email",
            )

            reg_password = st.text_input(
                "Password",
                type="password",
                key="reg_password",
            )

            reg_confirm = st.text_input(
                "Confirm password",
                type="password",
                key="reg_confirm",
            )

            if st.button(
                "Create account",
                use_container_width=True,
                type="primary",
            ):
                if (
                    not reg_email.strip()
                    or "@"
                    not in reg_email
                ):
                    st.warning(
                        "Enter a valid email."
                    )

                elif len(reg_password) < 8:
                    st.warning(
                        "Password must contain at "
                        "least 8 characters."
                    )

                elif reg_password != reg_confirm:
                    st.warning(
                        "Passwords do not match."
                    )

                else:
                    try:
                        response = (
                            supabase.auth
                            .sign_up(
                                {
                                    "email":
                                        reg_email.strip(),
                                    "password":
                                        reg_password,
                                }
                            )
                        )

                        if response.session:
                            save_auth(response)
                            st.rerun()

                        else:
                            st.success(
                                "Account created. Check your "
                                "email to confirm it."
                            )

                    except Exception as error:
                        st.error(
                            "Could not create account."
                        )

                        with st.expander(
                            "Technical details"
                        ):
                            st.code(
                                str(error)
                            )


# ============================================================
# SIDEBAR
# ============================================================

def nav_button(
    label: str,
    target: str,
    icon: str,
) -> None:
    active = (
        st.session_state.page
        == target
    )

    if st.button(
        f"{icon}   {label}",
        key=f"nav_{target}",
        use_container_width=True,
        type=(
            "primary"
            if active
            else "secondary"
        ),
    ):
        st.session_state.page = target
        st.session_state.editing_purchase_id = None
        st.session_state.deleting_purchase_id = None
        st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        render_brand()

        ui(
            '<div class="wi-nav-group">Overview</div>'
        )

        nav_button(
            "Dashboard",
            "Overview",
            "▣",
        )

        ui(
            '<div class="wi-nav-group">Tracking</div>'
        )

        nav_button(
            "Add Purchase",
            "Add Purchase",
            "＋",
        )

        nav_button(
            "My Items",
            "My Items",
            "◇",
        )

        nav_button(
            "Usage Calendar",
            "Usage Calendar",
            "◫",
        )

        ui(
            '<div class="wi-nav-group">Insights</div>'
        )

        nav_button(
            "Analytics",
            "Analytics",
            "↗",
        )

        st.divider()

        email = (
            st.session_state.user.email
            if st.session_state.user
            else ""
        )

        ui(
            f"""
            <div class="wi-account">
                <div class="wi-account-label">
                    Signed in as
                </div>

                <div class="wi-account-email">
                    {escape(email)}
                </div>
            </div>
            """
        )

        if st.button(
            "Log out",
            use_container_width=True,
        ):
            logout()


# ============================================================
# DASHBOARD
# ============================================================

def render_overview() -> None:
    with st.spinner(
        "Loading your dashboard..."
    ):
        purchases = get_purchases(
            supabase
        )

        usage_logs = get_usage_logs(
            supabase
        )

    scores = []

    for purchase in purchases:
        try:
            result = purchase_score(
                purchase
            )

            scores.append(
                {
                    "name":
                        purchase["item_name"],
                    "score":
                        result["score"],
                    "category":
                        purchase["category"],
                }
            )

        except Exception:
            continue

    avg_score = (
        round(
            sum(
                item["score"]
                for item in scores
            )
            / len(scores),
            1,
        )
        if scores
        else "—"
    )

    best_purchase = (
        max(
            scores,
            key=lambda item:
                item["score"],
        )["name"]
        if scores
        else "—"
    )

    total_spent = sum(
        float(
            purchase["price_idr"]
        )
        for purchase in purchases
    )

    today = date.today()

    usage_this_month = sum(
        1
        for log in usage_logs
        if (
            date.fromisoformat(
                log["used_on"]
            ).year
            == today.year
            and
            date.fromisoformat(
                log["used_on"]
            ).month
            == today.month
        )
    )

    ui(
        """
        <section class="wi-welcome">
            <div class="wi-welcome-kicker">
                Dashboard
            </div>

            <div class="wi-welcome-title">
                Your purchases are starting
                to tell a story.
            </div>

            <div class="wi-welcome-copy">
                Follow value, routine, repurchase intention,
                and usage in one colorful little decision system.
            </div>
        </section>
        """
    )

    c1, c2, c3, c4 = st.columns(
        4,
        gap="medium",
    )

    with c1:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Purchases
                </div>

                <div class="wi-metric-value">
                    {len(purchases)}
                </div>

                <div class="wi-metric-note">
                    tracked purchases
                </div>
            </div>
            """
        )

    with c2:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Avg. WorthIt
                </div>

                <div class="wi-metric-value">
                    {avg_score}
                </div>

                <div class="wi-metric-note">
                    average current score
                </div>
            </div>
            """
        )

    with c3:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Usage This Month
                </div>

                <div class="wi-metric-value">
                    {usage_this_month}
                </div>

                <div class="wi-metric-note">
                    calendar usage events
                </div>
            </div>
            """
        )

    with c4:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Tracked Spend
                </div>

                <div
                    class="wi-metric-value"
                    style="font-size:22px;"
                >
                    {format_idr(total_spent)}
                </div>

                <div class="wi-metric-note">
                    historical purchase value
                </div>
            </div>
            """
        )

    st.write("")
    st.write("")

    left, right = st.columns(
        [1.05, .95],
        gap="large",
    )

    with left:
        best_emoji = "✨"

        if scores:
            best_category = max(
                scores,
                key=lambda x:
                    x["score"],
            )["category"]

            best_emoji, _ = (
                category_style(
                    best_category
                )
            )

        ui(
            f"""
            <div class="wi-insight-box">
                <div class="wi-insight-title">
                    {best_emoji}
                    Your current best purchase
                </div>

                <div class="wi-insight-copy">
                    <strong>
                        {escape(str(best_purchase))}
                    </strong>
                    currently has your highest WorthIt score.
                    As you add real usage logs, this picture
                    becomes more behavior-driven.
                </div>
            </div>
            """
        )

    with right:
        ui(
            """
            <div class="wi-insight-box secondary">
                <div class="wi-insight-title">
                    ◫ Usage lives in one place
                </div>

                <div class="wi-insight-copy">
                    Usage Calendar is the single source of truth.
                    Choose a product, jump to a month and year,
                    then click the exact days you used it.
                </div>
            </div>
            """
        )

    st.write("")
    st.write("")

    if st.button(
        "Open Usage Calendar →",
        use_container_width=True,
        type="primary",
    ):
        st.session_state.page = (
            "Usage Calendar"
        )
        st.rerun()


# ============================================================
# ADD PURCHASE
# ============================================================

def render_add_purchase() -> None:
    ui(
        """
        <div class="wi-kicker">
            Add Purchase
        </div>

        <div class="wi-page-title">
            Add something you bought.
        </div>

        <div class="wi-page-copy">
            Choose the purchase type first.
            WorthIt adapts the questions for
            products, durable goods, food,
            and one-time experiences.
        </div>
        """
    )

    left, right = st.columns(
        [1.18, .82],
        gap="large",
    )

    with left:
        item_name = st.text_input(
            "Purchase name",
            placeholder=(
                "e.g. ESQA Cushion, Sushi Dinner, "
                "Nike Air Force 1"
            ),
        )

        c1, c2 = st.columns(2)

        with c1:
            purchase_type = st.selectbox(
                "Purchase type",
                [
                    "Consumable",
                    "Durable",
                    "One-time",
                ],
            )

        with c2:
            category = st.selectbox(
                "Category",
                CATEGORY_OPTIONS,
            )

        c3, c4 = st.columns(2)

        with c3:
            price = st.number_input(
                "Price (IDR)",
                min_value=0,
                step=1000,
            )

        with c4:
            purchased_on = st.date_input(
                "Purchase date",
                value=date.today(),
                max_value=date.today(),
            )

        precision = st.radio(
            "How certain is the date?",
            [
                "Actual",
                "Estimated",
            ],
            horizontal=True,
        )

        satisfaction = st.slider(
            "Satisfaction",
            min_value=1,
            max_value=5,
            value=4,
        )

        repurchase = st.radio(
            "Would you buy/order it again at roughly the same price?",
            [
                "Yes",
                "Maybe",
                "No",
            ],
            horizontal=True,
        )

        value_for_money = None
        usage_frequency = None

        if purchase_type == "One-time":
            value_for_money = st.slider(
                "Value for Money",
                min_value=1,
                max_value=5,
                value=4,
            )

        else:
            usage_option = st.selectbox(
                "Estimated usage frequency",
                USAGE_OPTIONS,
            )

            usage_frequency = (
                None
                if usage_option
                == "Not sure yet"
                else usage_option
            )

        notes = st.text_area(
            "Notes",
            placeholder=(
                "Optional: texture, fit, taste, "
                "quality, regret, service, etc."
            ),
        )

    with right:
        try:
            preview = (
                calculate_worthit_score(
                    purchase_type=
                        purchase_type,
                    satisfaction=
                        satisfaction,
                    would_buy_again=
                        repurchase,
                    usage_frequency=
                        usage_frequency,
                    purchase_date=
                        purchased_on,
                    purchase_date_precision=
                        precision,
                    satisfaction_is_verified=
                        True,
                    repurchase_is_verified=
                        True,
                    value_for_money=
                        value_for_money,
                    value_for_money_is_verified=
                        True,
                )
            )

            emoji, accent = (
                category_style(
                    category
                )
            )

            ui(
                f"""
                <div
                    class="wi-item"
                    style="--item-accent:{accent};"
                >
                    <div class="wi-kicker">
                        Live Preview
                    </div>

                    <div
                        class="wi-item-name"
                        style="font-size:24px;"
                    >
                        {emoji}
                        {escape(
                            item_name.strip()
                            or "Your purchase"
                        )}
                    </div>

                    <div class="wi-item-meta">
                        {escape(category)}
                        ·
                        {escape(purchase_type)}
                    </div>

                    <span class="wi-pill">
                        {preview["score"]}
                        ·
                        {escape(preview["label"])}
                    </span>
                </div>
                """
            )

            st.write("")

            ui(
                f"""
                <div class="wi-note-card">
                    <div class="wi-note-title">
                        Evidence
                    </div>

                    <div class="wi-note-copy">
                        {preview["confidence"]}%
                        ·
                        {escape(
                            preview["confidence_label"]
                        )}
                        <br><br>
                        Evidence measures how complete and
                        reliable the supporting data is.
                    </div>
                </div>
                """
            )

        except Exception as error:
            st.warning(
                f"Score preview unavailable: {error}"
            )

    st.write("")

    if st.button(
        "Save Purchase",
        use_container_width=True,
        type="primary",
    ):
        if not item_name.strip():
            st.warning(
                "Purchase name is required."
            )

        elif price <= 0:
            st.warning(
                "Price must be greater than 0."
            )

        else:
            payload = {
                "user_id":
                    str(
                        st.session_state
                        .user.id
                    ),

                "item_name":
                    item_name.strip(),

                "purchase_type":
                    purchase_type,

                "category":
                    category,

                "price_idr":
                    float(price),

                "purchase_date":
                    purchased_on.isoformat(),

                "date_precision":
                    precision,

                "status":
                    "Active",

                "usage_frequency":
                    usage_frequency,

                "satisfaction":
                    satisfaction,

                "would_buy_again":
                    repurchase,

                "satisfaction_is_verified":
                    True,

                "repurchase_is_verified":
                    True,

                "value_for_money":
                    value_for_money,

                "notes":
                    notes.strip()
                    or None,
            }

            try:
                with st.spinner(
                    "Saving your purchase..."
                ):
                    create_purchase(
                        supabase,
                        payload,
                    )

                st.toast(
                    "Purchase saved ✨"
                )

                st.session_state.page = (
                    "My Items"
                )

                st.rerun()

            except Exception as error:
                st.error(
                    "Purchase could not be saved."
                )

                with st.expander(
                    "Technical details"
                ):
                    st.code(
                        str(error)
                    )


# ============================================================
# EDIT PURCHASE
# ============================================================

def render_edit_purchase(
    purchase: dict,
) -> None:
    st.divider()

    ui(
        f"""
        <div class="wi-kicker">
            Edit
        </div>

        <div
            class="wi-page-title"
            style="font-size:32px;"
        >
            {escape(purchase["item_name"])}
        </div>
        """
    )

    current_category = (
        purchase.get(
            "category",
            "Other",
        )
    )

    if (
        current_category
        not in CATEGORY_OPTIONS
    ):
        current_category = "Other"

    current_type = purchase[
        "purchase_type"
    ]

    type_options = [
        "Consumable",
        "Durable",
        "One-time",
    ]

    with st.form(
        f"edit_form_{purchase['id']}"
    ):
        name = st.text_input(
            "Purchase name",
            value=purchase["item_name"],
        )

        c1, c2 = st.columns(2)

        with c1:
            ptype = st.selectbox(
                "Purchase type",
                type_options,
                index=type_options.index(
                    current_type
                ),
            )

        with c2:
            category = st.selectbox(
                "Category",
                CATEGORY_OPTIONS,
                index=CATEGORY_OPTIONS.index(
                    current_category
                ),
            )

        c3, c4 = st.columns(2)

        with c3:
            price = st.number_input(
                "Price (IDR)",
                min_value=0,
                value=int(
                    float(
                        purchase["price_idr"]
                    )
                ),
                step=1000,
            )

        with c4:
            purchase_date_value = (
                date.fromisoformat(
                    purchase[
                        "purchase_date"
                    ]
                )
            )

            purchased_on = st.date_input(
                "Purchase date",
                value=purchase_date_value,
                max_value=date.today(),
            )

        precision_options = [
            "Actual",
            "Estimated",
        ]

        current_precision = purchase.get(
            "date_precision",
            "Actual",
        )

        if (
            current_precision
            not in precision_options
        ):
            current_precision = "Actual"

        precision = st.radio(
            "Date precision",
            precision_options,
            index=precision_options.index(
                current_precision
            ),
            horizontal=True,
        )

        satisfaction = st.slider(
            "Satisfaction",
            min_value=1,
            max_value=5,
            value=int(
                purchase["satisfaction"]
            ),
        )

        repurchase_options = [
            "Yes",
            "Maybe",
            "No",
        ]

        repurchase_current = (
            purchase["would_buy_again"]
        )

        repurchase = st.radio(
            "Would you buy/order it again at roughly the same price?",
            repurchase_options,
            index=repurchase_options.index(
                repurchase_current
            ),
            horizontal=True,
        )

        usage_frequency = None
        value_for_money = None

        if ptype == "One-time":
            current_value = (
                purchase.get(
                    "value_for_money"
                )
                or 4
            )

            value_for_money = st.slider(
                "Value for Money",
                min_value=1,
                max_value=5,
                value=int(
                    current_value
                ),
            )

        else:
            current_usage = (
                purchase.get(
                    "usage_frequency"
                )
            )

            usage_current_label = (
                current_usage
                if current_usage
                in USAGE_OPTIONS
                else "Not sure yet"
            )

            usage_choice = st.selectbox(
                "Estimated usage frequency",
                USAGE_OPTIONS,
                index=USAGE_OPTIONS.index(
                    usage_current_label
                ),
            )

            usage_frequency = (
                None
                if usage_choice
                == "Not sure yet"
                else usage_choice
            )

        notes = st.text_area(
            "Notes",
            value=purchase.get(
                "notes"
            )
            or "",
        )

        csave, ccancel = st.columns(2)

        with csave:
            save_clicked = (
                st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                    type="primary",
                )
            )

        with ccancel:
            cancel_clicked = (
                st.form_submit_button(
                    "Cancel",
                    use_container_width=True,
                )
            )

    if cancel_clicked:
        st.session_state.editing_purchase_id = None
        st.rerun()

    if save_clicked:
        if not name.strip():
            st.warning(
                "Purchase name is required."
            )
            return

        payload = {
            "item_name":
                name.strip(),

            "purchase_type":
                ptype,

            "category":
                category,

            "price_idr":
                float(price),

            "purchase_date":
                purchased_on.isoformat(),

            "date_precision":
                precision,

            "usage_frequency":
                usage_frequency,

            "satisfaction":
                satisfaction,

            "would_buy_again":
                repurchase,

            "value_for_money":
                value_for_money,

            "notes":
                notes.strip()
                or None,
        }

        try:
            update_purchase(
                supabase,
                purchase["id"],
                payload,
            )

            st.session_state.editing_purchase_id = None
            st.toast(
                "Purchase updated ✨"
            )
            st.rerun()

        except Exception as error:
            st.error(
                "Could not update purchase."
            )

            with st.expander(
                "Technical details"
            ):
                st.code(
                    str(error)
                )


# ============================================================
# MY ITEMS
# ============================================================

def render_my_items() -> None:
    with st.spinner(
        "Loading purchases..."
    ):
        purchases = get_purchases(
            supabase
        )

    ui(
        """
        <div class="wi-kicker">
            My Items
        </div>

        <div class="wi-page-title">
            Your purchase collection.
        </div>

        <div class="wi-page-copy">
            Review scores, update details,
            finish products, or remove purchases.
            Usage itself is logged only in Usage Calendar.
        </div>
        """
    )

    if not purchases:
        st.info(
            "No purchases yet."
        )
        return

    f1, f2 = st.columns(
        [.35, .65]
    )

    with f1:
        type_filter = st.selectbox(
            "Type",
            [
                "All",
                "Consumable",
                "Durable",
                "One-time",
            ],
        )

    with f2:
        search = st.text_input(
            "Search",
            placeholder="Search purchases...",
        )

    filtered = purchases

    if type_filter != "All":
        filtered = [
            purchase
            for purchase in filtered
            if (
                purchase["purchase_type"]
                == type_filter
            )
        ]

    if search.strip():
        needle = (
            search.strip().lower()
        )

        filtered = [
            purchase
            for purchase in filtered
            if (
                needle
                in purchase[
                    "item_name"
                ].lower()
                or
                needle
                in purchase[
                    "category"
                ].lower()
            )
        ]

    st.caption(
        f"{len(filtered)} item(s) shown"
    )

    for purchase in filtered:
        emoji, accent = (
            category_style(
                purchase["category"]
            )
        )

        try:
            score = purchase_score(
                purchase
            )

            score_text = (
                f'{score["score"]}'
                f' · '
                f'{score["label"]}'
            )

            evidence_text = (
                f'Evidence '
                f'{score["confidence"]}%'
                f' · '
                f'{score["confidence_label"]}'
            )

        except Exception:
            score_text = (
                "Score unavailable"
            )

            evidence_text = (
                "Review purchase data"
            )

        ui(
            f"""
            <div
                class="wi-item"
                style="--item-accent:{accent};"
            >
                <div class="wi-item-name">
                    {escape(
                        purchase["item_name"]
                    )}

                    <span class="wi-category-badge">
                        {emoji}
                        {escape(
                            purchase["category"]
                        )}
                    </span>
                </div>

                <div class="wi-item-meta">
                    {escape(
                        purchase["purchase_type"]
                    )}
                    ·
                    {format_idr(
                        purchase["price_idr"]
                    )}
                    ·
                    {escape(
                        purchase["status"]
                    )}
                </div>

                <span class="wi-pill">
                    {escape(score_text)}
                </span>
            </div>
            """
        )

        actions = st.columns(
            [1, 1, 1, 1.15],
            gap="small",
        )

        with actions[0]:
            if st.button(
                "Edit",
                key=(
                    f"edit_"
                    f"{purchase['id']}"
                ),
                use_container_width=True,
            ):
                st.session_state.editing_purchase_id = (
                    purchase["id"]
                )
                st.session_state.deleting_purchase_id = None
                st.rerun()

        with actions[1]:
            if (
                purchase["status"]
                == "Finished"
            ):
                status_label = "Reopen"
                next_status = "Active"

            else:
                status_label = "Finish"
                next_status = "Finished"

            if st.button(
                status_label,
                key=(
                    f"status_"
                    f"{purchase['id']}"
                ),
                use_container_width=True,
            ):
                try:
                    update_purchase(
                        supabase,
                        purchase["id"],
                        {
                            "status":
                                next_status
                        },
                    )

                    st.toast(
                        f"Status changed to "
                        f"{next_status}"
                    )

                    st.rerun()

                except Exception as error:
                    st.error(
                        "Could not update status."
                    )

                    with st.expander(
                        "Technical details"
                    ):
                        st.code(
                            str(error)
                        )

        with actions[2]:
            if st.button(
                "Delete",
                key=(
                    f"delete_"
                    f"{purchase['id']}"
                ),
                use_container_width=True,
            ):
                st.session_state.deleting_purchase_id = (
                    purchase["id"]
                )
                st.session_state.editing_purchase_id = None
                st.rerun()

        with actions[3]:
            st.caption(
                evidence_text
            )

        if (
            st.session_state
            .deleting_purchase_id
            == purchase["id"]
        ):
            st.warning(
                "Delete this purchase? "
                "Its usage history will also be removed."
            )

            d1, d2 = st.columns(2)

            with d1:
                if st.button(
                    "Yes, delete",
                    key=(
                        f"confirm_delete_"
                        f"{purchase['id']}"
                    ),
                    use_container_width=True,
                    type="primary",
                ):
                    try:
                        delete_purchase(
                            supabase,
                            purchase["id"],
                        )

                        st.session_state.deleting_purchase_id = None
                        st.toast(
                            "Purchase deleted"
                        )
                        st.rerun()

                    except Exception as error:
                        st.error(
                            "Could not delete purchase."
                        )

                        with st.expander(
                            "Technical details"
                        ):
                            st.code(
                                str(error)
                            )

            with d2:
                if st.button(
                    "Cancel",
                    key=(
                        f"cancel_delete_"
                        f"{purchase['id']}"
                    ),
                    use_container_width=True,
                ):
                    st.session_state.deleting_purchase_id = None
                    st.rerun()

        if (
            st.session_state
            .editing_purchase_id
            == purchase["id"]
        ):
            render_edit_purchase(
                purchase
            )

        st.write("")
        st.write("")


# ============================================================
# USAGE CALENDAR
# ============================================================

def render_usage_calendar_page() -> None:
    with st.spinner(
        "Loading usage history..."
    ):
        all_purchases = (
            get_purchases(
                supabase
            )
        )

        usage_logs = (
            get_usage_logs(
                supabase
            )
        )

    purchases = [
        purchase
        for purchase in all_purchases
        if (
            purchase["purchase_type"]
            in {
                "Consumable",
                "Durable",
            }
        )
    ]

    ui(
        """
        <div class="wi-kicker">
            Usage Calendar
        </div>

        <div class="wi-page-title">
            Click the exact days you used it.
        </div>

        <div class="wi-page-copy">
            Purple means Used.
            Click a purple date again to undo.
            This is the only place where usage is logged.
        </div>
        """
    )

    if not purchases:
        st.info(
            "No Consumable or Durable "
            "purchases yet."
        )
        return

    by_id = {
        purchase["id"]:
            purchase
        for purchase in purchases
    }

    selected_id = st.selectbox(
        "Product",
        options=list(
            by_id.keys()
        ),
        format_func=lambda pid: (
            by_id[pid]["item_name"]
        ),
    )

    purchase = by_id[
        selected_id
    ]

    purchase_date = (
        date.fromisoformat(
            purchase[
                "purchase_date"
            ]
        )
    )

    today = date.today()

    years = list(
        range(
            purchase_date.year,
            today.year + 1,
        )
    )

    c1, c2 = st.columns(2)

    with c1:
        selected_year = st.selectbox(
            "Year",
            years,
            index=len(years) - 1,
        )

    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    valid_months = list(
        range(1, 13)
    )

    if (
        selected_year
        == today.year
    ):
        valid_months = [
            month
            for month
            in valid_months
            if (
                month
                <= today.month
            )
        ]

    if (
        selected_year
        == purchase_date.year
    ):
        valid_months = [
            month
            for month
            in valid_months
            if (
                month
                >= purchase_date.month
            )
        ]

    if not valid_months:
        valid_months = [
            purchase_date.month
        ]

    default_month = (
        today.month
        if (
            selected_year
            == today.year
            and
            today.month
            in valid_months
        )
        else valid_months[-1]
    )

    with c2:
        selected_month = (
            st.selectbox(
                "Month",
                valid_months,
                index=(
                    valid_months
                    .index(
                        default_month
                    )
                ),
                format_func=lambda month: (
                    month_names[
                        month - 1
                    ]
                ),
            )
        )

    product_logs = [
        log
        for log in usage_logs
        if (
            log["purchase_id"]
            == purchase["id"]
        )
    ]

    log_by_date = {
        date.fromisoformat(
            log["used_on"]
        ):
            log
        for log in product_logs
    }

    total_days = len(
        product_logs
    )

    last_30_cutoff = (
        today
        - timedelta(days=29)
    )

    last_30 = sum(
        1
        for log in product_logs
        if (
            date.fromisoformat(
                log["used_on"]
            )
            >= last_30_cutoff
        )
    )

    selected_month_count = (
        sum(
            1
            for log
            in product_logs
            if (
                date.fromisoformat(
                    log["used_on"]
                ).year
                == selected_year
                and
                date.fromisoformat(
                    log["used_on"]
                ).month
                == selected_month
            )
        )
    )

    m1, m2, m3 = st.columns(
        3,
        gap="medium",
    )

    with m1:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Total Used Days
                </div>

                <div class="wi-metric-value">
                    {total_days}
                </div>

                <div class="wi-metric-note">
                    all logged dates
                </div>
            </div>
            """
        )

    with m2:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Last 30 Days
                </div>

                <div class="wi-metric-value">
                    {last_30}
                </div>

                <div class="wi-metric-note">
                    recent used days
                </div>
            </div>
            """
        )

    with m3:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Selected Month
                </div>

                <div class="wi-metric-value">
                    {selected_month_count}
                </div>

                <div class="wi-metric-note">
                    used days this month
                </div>
            </div>
            """
        )

    st.write("")
    st.write("")

    emoji, accent = (
        category_style(
            purchase["category"]
        )
    )

    ui(
        f"""
        <div
            class="wi-item"
            style="--item-accent:{accent};"
        >
            <div class="wi-item-name">
                {emoji}
                {escape(
                    purchase["item_name"]
                )}
            </div>

            <div class="wi-item-meta">
                Click once = Used.
                Click purple again = Undo.
            </div>
        </div>
        """
    )

    header_cols = st.columns(7)

    weekdays = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]

    for col, weekday in zip(
        header_cols,
        weekdays,
    ):
        with col:
            ui(
                f"""
                <div style="
                    text-align:center;
                    color:#85899a;
                    font-size:10px;
                    font-weight:850;
                    padding:6px 0;
                ">
                    {weekday}
                </div>
                """
            )

    for week in monthcalendar(
        selected_year,
        selected_month,
    ):
        week_cols = st.columns(7)

        for col, day_num in zip(
            week_cols,
            week,
        ):
            with col:
                if day_num == 0:
                    st.write("")
                    continue

                current_date = date(
                    selected_year,
                    selected_month,
                    day_num,
                )

                existing_log = (
                    log_by_date.get(
                        current_date
                    )
                )

                is_used = (
                    existing_log
                    is not None
                )

                disabled = (
                    current_date
                    < purchase_date
                    or
                    current_date
                    > today
                )

                clicked = st.button(
                    (
                        f"✓ {day_num}"
                        if is_used
                        else str(day_num)
                    ),
                    key=(
                        f"cal_"
                        f"{purchase['id']}_"
                        f"{current_date.isoformat()}"
                    ),
                    use_container_width=True,
                    type=(
                        "primary"
                        if is_used
                        else "secondary"
                    ),
                    disabled=disabled,
                )

                if clicked:
                    try:
                        if is_used:
                            delete_usage_log(
                                supabase,
                                existing_log["id"],
                            )

                            st.toast(
                                "Usage removed"
                            )

                        else:
                            create_usage_log(
                                supabase,
                                purchase["id"],
                                str(
                                    st.session_state
                                    .user.id
                                ),
                                current_date,
                            )

                            st.toast(
                                "Usage logged ✨"
                            )

                        st.rerun()

                    except Exception as error:
                        st.error(
                            "Could not update usage."
                        )

                        with st.expander(
                            "Technical details"
                        ):
                            st.code(
                                str(error)
                            )


# ============================================================
# ANALYTICS
# ============================================================

def render_analytics() -> None:
    with st.spinner(
        "Building your insights..."
    ):
        purchases = get_purchases(
            supabase
        )

        usage_logs = get_usage_logs(
            supabase
        )

    ui(
        """
        <div class="wi-kicker">
            Analytics
        </div>

        <div class="wi-page-title">
            Understand your buying patterns.
        </div>

        <div class="wi-page-copy">
            Your 40-item history now becomes useful:
            value, regret signals, category patterns,
            and repurchase behavior in one place.
        </div>
        """
    )

    if not purchases:
        st.info(
            "Add purchases first."
        )
        return

    scored = []

    for purchase in purchases:
        try:
            result = purchase_score(
                purchase
            )

            scored.append(
                {
                    "id":
                        purchase["id"],
                    "name":
                        purchase["item_name"],
                    "category":
                        purchase["category"],
                    "type":
                        purchase["purchase_type"],
                    "score":
                        result["score"],
                    "repurchase":
                        purchase["would_buy_again"],
                    "price":
                        float(
                            purchase["price_idr"]
                        ),
                }
            )

        except Exception:
            continue

    if not scored:
        st.info(
            "Not enough valid score data."
        )
        return

    highest = max(
        scored,
        key=lambda item:
            item["score"],
    )

    lowest = min(
        scored,
        key=lambda item:
            item["score"],
    )

    buy_again_count = sum(
        1
        for item in scored
        if (
            item["repurchase"]
            == "Yes"
        )
    )

    rebuy_rate = round(
        (
            buy_again_count
            / len(scored)
        )
        * 100,
        1,
    )

    category_scores = {}

    for item in scored:
        category_scores.setdefault(
            item["category"],
            [],
        ).append(
            item["score"]
        )

    category_averages = {
        category:
            round(
                sum(values)
                / len(values),
                1,
            )
        for category, values
        in category_scores.items()
    }

    best_category = max(
        category_averages,
        key=category_averages.get,
    )

    worst_category = min(
        category_averages,
        key=category_averages.get,
    )

    top_5 = sorted(
        scored,
        key=lambda x:
            x["score"],
        reverse=True,
    )[:5]

    bottom_5 = sorted(
        scored,
        key=lambda x:
            x["score"],
    )[:5]

    a1, a2, a3, a4 = st.columns(
        4,
        gap="medium",
    )

    with a1:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Highest
                </div>

                <div
                    class="wi-metric-value"
                    style="font-size:20px;"
                >
                    {escape(highest["name"])}
                </div>

                <div class="wi-metric-note">
                    score {highest["score"]}
                </div>
            </div>
            """
        )

    with a2:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Lowest
                </div>

                <div
                    class="wi-metric-value"
                    style="font-size:20px;"
                >
                    {escape(lowest["name"])}
                </div>

                <div class="wi-metric-note">
                    score {lowest["score"]}
                </div>
            </div>
            """
        )

    with a3:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Rebuy Rate
                </div>

                <div class="wi-metric-value">
                    {rebuy_rate}%
                </div>

                <div class="wi-metric-note">
                    would buy again
                </div>
            </div>
            """
        )

    with a4:
        ui(
            f"""
            <div class="wi-metric">
                <div class="wi-metric-label">
                    Best Category
                </div>

                <div
                    class="wi-metric-value"
                    style="font-size:20px;"
                >
                    {escape(best_category)}
                </div>

                <div class="wi-metric-note">
                    avg {category_averages[best_category]}
                </div>
            </div>
            """
        )

    st.write("")
    st.write("")

    left, right = st.columns(
        2,
        gap="medium",
    )

    with left:
        best_emoji, _ = (
            category_style(
                best_category
            )
        )

        ui(
            f"""
            <div class="wi-insight-box">
                <div class="wi-insight-title">
                    {best_emoji}
                    Strongest category
                </div>

                <div class="wi-insight-copy">
                    <strong>
                        {escape(best_category)}
                    </strong>
                    currently has your highest average
                    WorthIt score at
                    <strong>
                        {category_averages[best_category]}
                    </strong>.
                </div>
            </div>
            """
        )

    with right:
        worst_emoji, _ = (
            category_style(
                worst_category
            )
        )

        ui(
            f"""
            <div class="wi-insight-box coral">
                <div class="wi-insight-title">
                    {worst_emoji}
                    Watch this category
                </div>

                <div class="wi-insight-copy">
                    <strong>
                        {escape(worst_category)}
                    </strong>
                    currently has your lowest average
                    score at
                    <strong>
                        {category_averages[worst_category]}
                    </strong>.
                    That makes it a good place to inspect
                    regret or low-value purchases.
                </div>
            </div>
            """
        )

    st.write("")
    st.write("")

    top_col, bottom_col = st.columns(
        2,
        gap="large",
    )

    with top_col:
        ui(
            """
            <div class="wi-kicker">
                Top 5
            </div>
            """
        )

        for index, item in enumerate(
            top_5,
            start=1,
        ):
            emoji, accent = (
                category_style(
                    item["category"]
                )
            )

            ui(
                f"""
                <div
                    class="wi-item"
                    style="--item-accent:{accent};"
                >
                    <div class="wi-item-name">
                        #{index}
                        {emoji}
                        {escape(item["name"])}
                    </div>

                    <div class="wi-item-meta">
                        {escape(item["category"])}
                        ·
                        {format_idr(item["price"])}
                    </div>

                    <span class="wi-pill">
                        Score {item["score"]}
                    </span>
                </div>
                """
            )

    with bottom_col:
        ui(
            """
            <div class="wi-kicker">
                Bottom 5 / Regret Watch
            </div>
            """
        )

        for index, item in enumerate(
            bottom_5,
            start=1,
        ):
            emoji, accent = (
                category_style(
                    item["category"]
                )
            )

            ui(
                f"""
                <div
                    class="wi-item"
                    style="--item-accent:{accent};"
                >
                    <div class="wi-item-name">
                        #{index}
                        {emoji}
                        {escape(item["name"])}
                    </div>

                    <div class="wi-item-meta">
                        {escape(item["category"])}
                        ·
                        {format_idr(item["price"])}
                    </div>

                    <span class="wi-pill">
                        Score {item["score"]}
                    </span>
                </div>
                """
            )

    st.write("")
    st.write("")

    n1, n2, n3 = st.columns(
        3,
        gap="medium",
    )

    with n1:
        ui(
            f"""
            <div class="wi-note-card">
                <div class="wi-note-title">
                    ✨ Rebuy behavior
                </div>

                <div class="wi-note-copy">
                    {buy_again_count}
                    of
                    {len(scored)}
                    scored purchases are marked
                    “Yes” for buy again.
                </div>
            </div>
            """
        )

    with n2:
        ui(
            f"""
            <div class="wi-note-card">
                <div class="wi-note-title">
                    ◫ Usage evidence
                </div>

                <div class="wi-note-copy">
                    {len(usage_logs)}
                    actual calendar usage event(s)
                    are currently recorded.
                    This can later support
                    cost-per-use and observed frequency.
                </div>
            </div>
            """
        )

    with n3:
        ui(
            """
            <div class="wi-note-card">
                <div class="wi-note-title">
                    ↗ Next intelligence layer
                </div>

                <div class="wi-note-copy">
                    Later we can add spending composition,
                    cost-per-use, observed usage frequency,
                    and a personalized regret-risk model.
                </div>
            </div>
            """
        )


# ============================================================
# APP ROUTER
# ============================================================

def render_app() -> None:
    render_sidebar()
    render_brand()

    if (
        st.session_state.page
        == "Overview"
    ):
        render_overview()

    elif (
        st.session_state.page
        == "Add Purchase"
    ):
        render_add_purchase()

    elif (
        st.session_state.page
        == "My Items"
    ):
        render_my_items()

    elif (
        st.session_state.page
        == "Usage Calendar"
    ):
        render_usage_calendar_page()

    elif (
        st.session_state.page
        == "Analytics"
    ):
        render_analytics()


# ============================================================
# START
# ============================================================

if st.session_state.user is None:
    render_auth_page()

else:
    render_app()
