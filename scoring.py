from datetime import date
from typing import Optional


# ============================================================
# WorthIt Scoring Engine v1.2
# ============================================================

SATISFACTION_WEIGHTS = {
    1: 0.00,
    2: 0.25,
    3: 0.50,
    4: 0.75,
    5: 1.00,
}

REPURCHASE_WEIGHTS = {
    "yes": 1.00,
    "maybe": 0.50,
    "no": 0.00,
}

USAGE_WEIGHTS = {
    "almost daily": 1.00,
    "frequent": 0.85,
    "frequent / rotating": 0.70,
    "weekly": 0.50,
    "occasional": 0.25,
    "rare": 0.10,
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_satisfaction(value: int) -> float:
    if value not in SATISFACTION_WEIGHTS:
        raise ValueError(
            "Satisfaction must be between 1 and 5."
        )

    return SATISFACTION_WEIGHTS[value]


def normalize_value_for_money(
    value: Optional[int],
) -> Optional[float]:

    if value is None:
        return None

    if value not in SATISFACTION_WEIGHTS:
        raise ValueError(
            "Value for money must be between 1 and 5."
        )

    return SATISFACTION_WEIGHTS[value]


def normalize_repurchase(value: str) -> float:
    if not isinstance(value, str):
        raise ValueError(
            "Repurchase must be Yes, Maybe, or No."
        )

    key = value.strip().lower()

    if key not in REPURCHASE_WEIGHTS:
        raise ValueError(
            "Repurchase must be Yes, Maybe, or No."
        )

    return REPURCHASE_WEIGHTS[key]


def normalize_usage(
    value: Optional[str],
) -> Optional[float]:

    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError(
            "Usage frequency must be a string or None."
        )

    key = value.strip().lower()

    if key in {"", "finished"}:
        return None

    if key not in USAGE_WEIGHTS:
        raise ValueError(
            f"Unknown usage frequency: {value}"
        )

    return USAGE_WEIGHTS[key]


# ============================================================
# LONGEVITY
# ============================================================

def calculate_longevity(
    purchase_date: date,
    reference_date: Optional[date] = None,
) -> float:

    if reference_date is None:
        reference_date = date.today()

    if purchase_date > reference_date:
        raise ValueError(
            "Purchase date cannot be in the future."
        )

    ownership_days = (
        reference_date - purchase_date
    ).days

    return min(
        max(
            ownership_days / 365,
            0.0,
        ),
        1.0,
    )


# ============================================================
# WEIGHTED SCORE
# ============================================================

def weighted_score(
    components: list[
        tuple[
            float,
            Optional[float],
        ]
    ],
) -> float:

    available = [
        (weight, value)
        for weight, value in components
        if value is not None
    ]

    if not available:
        raise ValueError(
            "Cannot calculate score without evidence."
        )

    numerator = sum(
        weight * value
        for weight, value in available
    )

    denominator = sum(
        weight
        for weight, _ in available
    )

    return min(
        max(
            100 * numerator / denominator,
            0,
        ),
        100,
    )


# ============================================================
# LABELS
# ============================================================

def get_score_label(
    score: float,
) -> str:

    if score >= 85:
        return "Highly Worth It"

    if score >= 70:
        return "Worth It"

    if score >= 55:
        return "Mixed Value"

    if score >= 40:
        return "Questionable"

    return "Not Worth It"


def get_confidence_label(
    confidence: float,
) -> str:

    if confidence >= 80:
        return "High Evidence"

    if confidence >= 60:
        return "Moderate Evidence"

    return "Low Evidence"


# ============================================================
# EVIDENCE CONFIDENCE
# ============================================================

def calculate_evidence_confidence(
    purchase_type: str,
    usage_frequency: Optional[str] = None,
    purchase_date_precision: str = "Estimated",
    satisfaction_is_verified: bool = False,
    repurchase_is_verified: bool = True,
    value_for_money_is_verified: bool = True,
) -> dict:

    product_type = (
        purchase_type
        .strip()
        .lower()
    )

    if product_type not in {
        "consumable",
        "durable",
        "one-time",
    }:
        raise ValueError(
            "Purchase type must be "
            "Consumable, Durable, or One-time."
        )

    satisfaction_quality = (
        1.00
        if satisfaction_is_verified
        else 0.40
    )

    repurchase_quality = (
        1.00
        if repurchase_is_verified
        else 0.50
    )

    value_quality = (
        1.00
        if value_for_money_is_verified
        else 0.50
    )

    normalized_usage = (
        normalize_usage(
            usage_frequency
        )
    )

    usage_quality = (
        0.50
        if normalized_usage is not None
        else 0.00
    )

    date_precision = (
        purchase_date_precision
        .strip()
        .lower()
    )

    if date_precision == "actual":
        date_quality = 1.00

    elif date_precision == "estimated":
        date_quality = 0.40

    else:
        raise ValueError(
            "Purchase date precision must "
            "be Actual or Estimated."
        )

    if product_type == "consumable":

        confidence = (
            0.40 * satisfaction_quality
            + 0.35 * repurchase_quality
            + 0.25 * usage_quality
        )

    elif product_type == "durable":

        confidence = (
            0.35 * satisfaction_quality
            + 0.30 * repurchase_quality
            + 0.25 * usage_quality
            + 0.10 * date_quality
        )

    else:

        confidence = (
            0.40 * satisfaction_quality
            + 0.35 * repurchase_quality
            + 0.25 * value_quality
        )

    confidence = round(
        confidence * 100,
        1,
    )

    return {
        "confidence":
            confidence,

        "confidence_label":
            get_confidence_label(
                confidence
            ),
    }


# ============================================================
# MAIN SCORE
# ============================================================

def calculate_worthit_score(
    purchase_type: str,
    satisfaction: int,
    would_buy_again: str,
    usage_frequency: Optional[str] = None,
    purchase_date: Optional[date] = None,
    reference_date: Optional[date] = None,
    purchase_date_precision: str = "Estimated",
    satisfaction_is_verified: bool = False,
    repurchase_is_verified: bool = True,
    value_for_money: Optional[int] = None,
    value_for_money_is_verified: bool = True,
) -> dict:

    product_type = (
        purchase_type
        .strip()
        .lower()
    )

    if product_type not in {
        "consumable",
        "durable",
        "one-time",
    }:
        raise ValueError(
            "Purchase type must be "
            "Consumable, Durable, or One-time."
        )

    satisfaction_component = (
        normalize_satisfaction(
            satisfaction
        )
    )

    repurchase_component = (
        normalize_repurchase(
            would_buy_again
        )
    )

    usage_component = None

    longevity_component = None

    value_component = None


    # ========================================================
    # CONSUMABLE
    # ========================================================

    if product_type == "consumable":

        usage_component = (
            normalize_usage(
                usage_frequency
            )
        )

        components = [
            (
                0.40,
                satisfaction_component,
            ),
            (
                0.35,
                repurchase_component,
            ),
            (
                0.25,
                usage_component,
            ),
        ]


    # ========================================================
    # DURABLE
    # ========================================================

    elif product_type == "durable":

        usage_component = (
            normalize_usage(
                usage_frequency
            )
        )

        if purchase_date is not None:

            longevity_component = (
                calculate_longevity(
                    purchase_date,
                    reference_date,
                )
            )

        components = [
            (
                0.35,
                satisfaction_component,
            ),
            (
                0.30,
                repurchase_component,
            ),
            (
                0.25,
                usage_component,
            ),
            (
                0.10,
                longevity_component,
            ),
        ]


    # ========================================================
    # ONE-TIME
    # ========================================================

    else:

        value_component = (
            normalize_value_for_money(
                value_for_money
            )
        )

        if value_component is None:
            raise ValueError(
                "One-time purchases require "
                "a Value for Money rating."
            )

        components = [
            (
                0.40,
                satisfaction_component,
            ),
            (
                0.35,
                repurchase_component,
            ),
            (
                0.25,
                value_component,
            ),
        ]


    score = round(
        weighted_score(
            components
        ),
        1,
    )

    evidence = (
        calculate_evidence_confidence(
            purchase_type=
                purchase_type,

            usage_frequency=
                usage_frequency,

            purchase_date_precision=
                purchase_date_precision,

            satisfaction_is_verified=
                satisfaction_is_verified,

            repurchase_is_verified=
                repurchase_is_verified,

            value_for_money_is_verified=
                value_for_money_is_verified,
        )
    )

    return {
        "score":
            score,

        "label":
            get_score_label(
                score
            ),

        "confidence":
            evidence[
                "confidence"
            ],

        "confidence_label":
            evidence[
                "confidence_label"
            ],

        "satisfaction_component":
            satisfaction_component,

        "repurchase_component":
            repurchase_component,

        "usage_component":
            usage_component,

        "longevity_component":
            longevity_component,

        "value_for_money_component":
            value_component,
    }