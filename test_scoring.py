from datetime import date

import pytest

from scoring import (
    calculate_evidence_confidence,
    calculate_longevity,
    calculate_worthit_score,
    get_confidence_label,
    get_score_label,
    normalize_repurchase,
    normalize_satisfaction,
    normalize_usage,
)


# ============================================================
# WorthIt Scoring Engine Tests
# ============================================================


# ------------------------------------------------------------
# 1. Satisfaction normalization
# ------------------------------------------------------------

def test_satisfaction_normalization():
    assert normalize_satisfaction(1) == 0.00
    assert normalize_satisfaction(2) == 0.25
    assert normalize_satisfaction(3) == 0.50
    assert normalize_satisfaction(4) == 0.75
    assert normalize_satisfaction(5) == 1.00


def test_invalid_satisfaction():
    with pytest.raises(ValueError):
        normalize_satisfaction(6)

    with pytest.raises(ValueError):
        normalize_satisfaction(0)


# ------------------------------------------------------------
# 2. Repurchase normalization
# ------------------------------------------------------------

def test_repurchase_normalization():
    assert normalize_repurchase("Yes") == 1.00
    assert normalize_repurchase("Maybe") == 0.50
    assert normalize_repurchase("No") == 0.00


def test_repurchase_is_case_insensitive():
    assert normalize_repurchase("YES") == 1.00
    assert normalize_repurchase(" yes ") == 1.00
    assert normalize_repurchase("MAYBE") == 0.50
    assert normalize_repurchase(" no ") == 0.00


def test_invalid_repurchase():
    with pytest.raises(ValueError):
        normalize_repurchase("Sometimes")


# ------------------------------------------------------------
# 3. Usage normalization
# ------------------------------------------------------------

def test_usage_normalization():
    assert normalize_usage("Almost daily") == 1.00
    assert normalize_usage("Frequent") == 0.85
    assert normalize_usage("Frequent / rotating") == 0.70
    assert normalize_usage("Weekly") == 0.50
    assert normalize_usage("Occasional") == 0.25
    assert normalize_usage("Rare") == 0.10


def test_finished_is_not_frequency():
    """
    Finished is a product status, NOT usage frequency.
    It must therefore be treated as missing usage evidence.
    """
    assert normalize_usage("Finished") is None


def test_missing_usage():
    assert normalize_usage(None) is None
    assert normalize_usage("") is None


def test_invalid_usage_frequency():
    with pytest.raises(ValueError):
        normalize_usage("Every century")


# ------------------------------------------------------------
# 4. Known consumable calculation
# ------------------------------------------------------------

def test_consumable_known_example():
    """
    S = 4 -> 0.75
    R = Yes -> 1.00
    U = Frequent / rotating -> 0.70

    Score:
    100 * (
        0.40 * 0.75
        + 0.35 * 1.00
        + 0.25 * 0.70
    )

    = 82.5
    """

    result = calculate_worthit_score(
        purchase_type="Consumable",
        satisfaction=4,
        would_buy_again="Yes",
        usage_frequency="Frequent / rotating",
    )

    assert result["score"] == 82.5
    assert result["label"] == "Worth It"


# ------------------------------------------------------------
# 5. Missing evidence behavior
# ------------------------------------------------------------

def test_missing_usage_does_not_become_zero():
    """
    Missing usage must NOT be interpreted as bad usage.

    The score is dynamically normalized using only
    available evidence.
    """

    result = calculate_worthit_score(
        purchase_type="Consumable",
        satisfaction=5,
        would_buy_again="Yes",
        usage_frequency=None,
    )

    assert result["score"] == 100.0
    assert result["usage_component"] is None


def test_finished_usage_does_not_become_zero():
    result = calculate_worthit_score(
        purchase_type="Consumable",
        satisfaction=5,
        would_buy_again="Yes",
        usage_frequency="Finished",
    )

    assert result["score"] == 100.0
    assert result["usage_component"] is None


# ------------------------------------------------------------
# 6. Durable longevity
# ------------------------------------------------------------

def test_durable_longevity_calculation():
    longevity = calculate_longevity(
        purchase_date=date(2026, 1, 1),
        reference_date=date(2026, 9, 12),
    )

    assert 0 < longevity < 1


def test_durable_longevity_is_capped_at_one():
    longevity = calculate_longevity(
        purchase_date=date(2024, 1, 1),
        reference_date=date(2026, 9, 12),
    )

    assert longevity == 1.0


def test_future_purchase_date_is_rejected():
    with pytest.raises(ValueError):
        calculate_longevity(
            purchase_date=date(2027, 1, 1),
            reference_date=date(2026, 9, 12),
        )


def test_durable_score_stays_in_valid_range():
    result = calculate_worthit_score(
        purchase_type="Durable",
        satisfaction=5,
        would_buy_again="Yes",
        usage_frequency="Frequent",
        purchase_date=date(2026, 1, 1),
        reference_date=date(2026, 9, 12),
    )

    assert 0 <= result["score"] <= 100


# ------------------------------------------------------------
# 7. Purchase type validation
# ------------------------------------------------------------

def test_invalid_purchase_type():
    with pytest.raises(ValueError):
        calculate_worthit_score(
            purchase_type="Food",
            satisfaction=5,
            would_buy_again="Yes",
            usage_frequency="Frequent",
        )


# ------------------------------------------------------------
# 8. Score label boundaries
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "score, expected_label",
    [
        (100, "Highly Worth It"),
        (85, "Highly Worth It"),
        (84.9, "Worth It"),
        (70, "Worth It"),
        (69.9, "Mixed Value"),
        (55, "Mixed Value"),
        (54.9, "Questionable"),
        (40, "Questionable"),
        (39.9, "Not Worth It"),
        (0, "Not Worth It"),
    ],
)
def test_score_label_boundaries(score, expected_label):
    assert get_score_label(score) == expected_label


# ============================================================
# Evidence Confidence Tests
# ============================================================


# ------------------------------------------------------------
# 9. Confidence label boundaries
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "confidence, expected_label",
    [
        (100, "High Evidence"),
        (80, "High Evidence"),
        (79.9, "Moderate Evidence"),
        (60, "Moderate Evidence"),
        (59.9, "Low Evidence"),
        (0, "Low Evidence"),
    ],
)
def test_confidence_label_boundaries(
    confidence,
    expected_label,
):
    assert get_confidence_label(confidence) == expected_label


# ------------------------------------------------------------
# 10. Current dataset confidence
# ------------------------------------------------------------

def test_confidence_with_complete_estimated_consumable_data():
    """
    Current historical dataset assumptions:

    satisfaction = estimated/randomized -> quality 0.40
    repurchase = user-entered          -> quality 1.00
    usage = estimated but available    -> quality 0.50

    Confidence:
    (0.40 * 0.40)
    + (0.35 * 1.00)
    + (0.25 * 0.50)

    = 0.635 -> 63.5%
    """

    result = calculate_worthit_score(
        purchase_type="Consumable",
        satisfaction=4,
        would_buy_again="Yes",
        usage_frequency="Frequent",
    )

    assert result["confidence"] == 63.5
    assert result["confidence_label"] == "Moderate Evidence"


def test_confidence_drops_when_usage_is_missing():
    """
    Finished is not frequency, therefore usage evidence
    is unavailable.

    Confidence:
    (0.40 * 0.40)
    + (0.35 * 1.00)
    + (0.25 * 0.00)

    = 0.51 -> 51%
    """

    result = calculate_worthit_score(
        purchase_type="Consumable",
        satisfaction=5,
        would_buy_again="Yes",
        usage_frequency="Finished",
    )

    assert result["confidence"] == 51.0
    assert result["confidence_label"] == "Low Evidence"


def test_verified_satisfaction_increases_confidence():
    unverified = calculate_evidence_confidence(
        purchase_type="Consumable",
        usage_frequency="Frequent",
        satisfaction_is_verified=False,
        repurchase_is_verified=True,
    )

    verified = calculate_evidence_confidence(
        purchase_type="Consumable",
        usage_frequency="Frequent",
        satisfaction_is_verified=True,
        repurchase_is_verified=True,
    )

    assert verified["confidence"] > unverified["confidence"]


def test_actual_date_increases_durable_confidence():
    estimated = calculate_evidence_confidence(
        purchase_type="Durable",
        usage_frequency="Frequent",
        purchase_date_precision="Estimated",
        satisfaction_is_verified=False,
        repurchase_is_verified=True,
    )

    actual = calculate_evidence_confidence(
        purchase_type="Durable",
        usage_frequency="Frequent",
        purchase_date_precision="Actual",
        satisfaction_is_verified=False,
        repurchase_is_verified=True,
    )

    assert actual["confidence"] > estimated["confidence"]


def test_invalid_date_precision():
    with pytest.raises(ValueError):
        calculate_evidence_confidence(
            purchase_type="Durable",
            usage_frequency="Frequent",
            purchase_date_precision="Unknown",
        )


# ------------------------------------------------------------
# 11. General score safety
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "satisfaction, repurchase, usage",
    [
        (1, "No", "Rare"),
        (3, "Maybe", "Weekly"),
        (5, "Yes", "Almost daily"),
        (4, "No", "Occasional"),
        (2, "Yes", None),
    ],
)
def test_consumable_score_always_between_zero_and_100(
    satisfaction,
    repurchase,
    usage,
):
    result = calculate_worthit_score(
        purchase_type="Consumable",
        satisfaction=satisfaction,
        would_buy_again=repurchase,
        usage_frequency=usage,
    )

    assert 0 <= result["score"] <= 100
    assert 0 <= result["confidence"] <= 100