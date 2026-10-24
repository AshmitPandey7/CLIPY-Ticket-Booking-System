"""Fare calculation formulas and promotional discounts for CLIPY."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional, Tuple, Union

# Rates and thresholds
BASE_FARE = Decimal("100.00")
SLAB_1_KM_LIMIT = Decimal("100.00")
SLAB_1_RATE = Decimal("1.00")
SLAB_2_KM_LIMIT = Decimal("200.00")
SLAB_2_RATE = Decimal("0.80")
SLAB_3_RATE = Decimal("0.60")

SENIOR_AGE_THRESHOLD = 60
SENIOR_DISCOUNT_PERCENT = Decimal("0.40")
SENIOR_FARE_FACTOR = Decimal("1.00") - SENIOR_DISCOUNT_PERCENT

BAGGAGE_RATE_PER_KG = Decimal("15.00")
TWO_PLACES = Decimal("0.01")


def _to_decimal(value: Union[int, float, str, Decimal]) -> Decimal:
    """Helper to ensure numbers are Decimal instances."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _round_currency(amount: Decimal) -> Decimal:
    """Rounds an amount to 2 decimal places."""
    return amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


# --- Step 1: Distance Slab Fare ---
def calculate_slab_fare(distance: Union[int, float, str, Decimal]) -> Decimal:
    """Calculates the cumulative distance slab fare.

    - Base fare: INR 100.00
    - 0 to 100 km: INR 1.00/km
    - 101 to 300 km: INR 0.80/km
    - Beyond 300 km: INR 0.60/km
    """
    d = _to_decimal(distance)
    if d < Decimal("0"):
        raise ValueError("Distance cannot be negative.")

    d1 = min(d, SLAB_1_KM_LIMIT)
    d2 = min(max(d - SLAB_1_KM_LIMIT, Decimal("0")), SLAB_2_KM_LIMIT)
    d3 = max(d - (SLAB_1_KM_LIMIT + SLAB_2_KM_LIMIT), Decimal("0"))

    distance_charge = (d1 * SLAB_1_RATE) + (d2 * SLAB_2_RATE) + (d3 * SLAB_3_RATE)
    slab_fare = BASE_FARE + distance_charge
    return _round_currency(slab_fare)


# --- Step 2: Senior Citizen Discount ---
def apply_senior_citizen_discount(fare: Decimal, age: int) -> Decimal:
    """Applies 40% senior discount if age is strictly greater than 60."""
    if age < 0:
        raise ValueError("Age cannot be negative.")

    if age > SENIOR_AGE_THRESHOLD:
        discounted = fare * SENIOR_FARE_FACTOR
        return _round_currency(discounted)
    return _round_currency(fare)


# --- Step 3: Train Premium ---
def apply_train_premium(fare: Decimal, train_multiplier: Union[float, str, Decimal]) -> Decimal:
    """Multiplies fare by the train service multiplier."""
    multiplier = _to_decimal(train_multiplier)
    if multiplier <= Decimal("0"):
        raise ValueError("Train multiplier must be positive.")
    return _round_currency(fare * multiplier)


# --- Step 4: Class Multiplier ---
def apply_class_multiplier(fare: Decimal, class_multiplier: Union[float, str, Decimal]) -> Decimal:
    """Multiplies fare by the travel class multiplier."""
    multiplier = _to_decimal(class_multiplier)
    if multiplier <= Decimal("0"):
        raise ValueError("Class multiplier must be positive.")
    return _round_currency(fare * multiplier)


# --- Step 5: Excess Baggage Fee ---
def calculate_excess_baggage_charges(
    baggage_weight: Union[int, float, str, Decimal],
    free_allowance: Union[int, float, str, Decimal],
) -> Decimal:
    """Calculates excess baggage charges at INR 15 per kg over allowance."""
    weight = _to_decimal(baggage_weight)
    allowance = _to_decimal(free_allowance)

    if weight <= Decimal("0"):
        raise ValueError("Baggage weight must be strictly positive.")
    if allowance < Decimal("0"):
        raise ValueError("Free baggage allowance cannot be negative.")

    excess_weight = max(Decimal("0"), weight - allowance)
    fee = excess_weight * BAGGAGE_RATE_PER_KG
    return _round_currency(fee)


# --- Step 6: Train Surcharge ---
def apply_train_surcharge(fare: Decimal, surcharge: Union[int, float, str, Decimal]) -> Decimal:
    """Adds the flat per-passenger train surcharge."""
    sc = _to_decimal(surcharge)
    if sc < Decimal("0"):
        raise ValueError("Surcharge cannot be negative.")
    return _round_currency(fare + sc)


# --- Complete Fare Calculation ---
def calculate_complete_passenger_fare(
    distance: int,
    age: int,
    train_multiplier: Union[float, str, Decimal],
    class_multiplier: Union[float, str, Decimal],
    baggage_weight: Union[float, str, Decimal],
    free_allowance: Union[float, str, Decimal],
    train_surcharge: Union[int, float, str, Decimal],
) -> Dict[str, object]:
    """Calculates the complete 6-step fare for one passenger."""
    # Step 1: Base + Distance Slab Fare
    step1_slab_fare = calculate_slab_fare(distance)
    distance_charge = step1_slab_fare - BASE_FARE

    # Step 2: Senior Citizen Discount
    is_senior = age > SENIOR_AGE_THRESHOLD
    step2_fare = apply_senior_citizen_discount(step1_slab_fare, age)
    senior_discount_amount = step1_slab_fare - step2_fare

    # Step 3: Train Premium
    t_mult = _to_decimal(train_multiplier)
    step3_fare = apply_train_premium(step2_fare, t_mult)

    # Step 4: Class Multiplier
    c_mult = _to_decimal(class_multiplier)
    step4_fare = apply_class_multiplier(step3_fare, c_mult)

    # Step 5: Excess Baggage Fee
    b_weight = _to_decimal(baggage_weight)
    b_allowance = _to_decimal(free_allowance)
    excess_baggage_weight = max(Decimal("0"), b_weight - b_allowance)
    excess_baggage_fee = calculate_excess_baggage_charges(b_weight, b_allowance)
    step5_fare = _round_currency(step4_fare + excess_baggage_fee)

    # Step 6: Flat Train Surcharge
    t_surcharge = _to_decimal(train_surcharge)
    final_fare = apply_train_surcharge(step5_fare, t_surcharge)

    return {
        "base_fare": BASE_FARE,
        "distance": distance,
        "distance_charge": distance_charge,
        "step1_slab_fare": step1_slab_fare,
        "age": age,
        "is_senior": is_senior,
        "senior_discount_amount": senior_discount_amount,
        "step2_fare": step2_fare,
        "train_multiplier": t_mult,
        "step3_fare": step3_fare,
        "class_multiplier": c_mult,
        "step4_fare": step4_fare,
        "baggage_weight": b_weight,
        "baggage_allowance": b_allowance,
        "excess_baggage_weight": excess_baggage_weight,
        "excess_baggage_fee": excess_baggage_fee,
        "step5_fare": step5_fare,
        "train_surcharge": t_surcharge,
        "final_fare": final_fare,
    }


# --- Promo Codes ---
def apply_promotional_discount(
    subtotal: Decimal, promo_code: Optional[str]
) -> Tuple[Decimal, Decimal, str, str]:
    """Applies valid promo code (ADG20 or WINTER500) to subtotal."""
    sub = _round_currency(_to_decimal(subtotal))
    if sub < Decimal("0"):
        raise ValueError("Subtotal cannot be negative.")

    if promo_code is None or not promo_code.strip():
        return Decimal("0.00"), sub, "", "No promo code applied."

    normalized = promo_code.strip().upper()

    if normalized == "ADG20":
        discount = _round_currency(sub * Decimal("0.20"))
        final_payable = calculate_final_payable(sub, discount)
        return discount, final_payable, normalized, "20% discount applied."

    if normalized == "WINTER500":
        flat_deduction = Decimal("500.00")
        discount = _round_currency(min(sub, flat_deduction))
        final_payable = calculate_final_payable(sub, discount)
        return discount, final_payable, normalized, "Flat INR 500 discount applied."

    return (
        Decimal("0.00"),
        sub,
        normalized,
        f"Invalid promo code '{normalized}'. No discount applied.",
    )


def calculate_final_payable(subtotal: Decimal, discount_amount: Decimal) -> Decimal:
    """Calculates final total after discount, ensuring it never goes below zero."""
    sub = _round_currency(_to_decimal(subtotal))
    disc = _round_currency(_to_decimal(discount_amount))
    return max(Decimal("0.00"), sub - disc)
