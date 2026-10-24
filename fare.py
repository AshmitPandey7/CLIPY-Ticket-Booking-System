"""fare.py - Core mathematical fare calculation engine for CLIPY.

This module implements pure mathematical logic for calculating railway ticket fares.
It operates independently of any terminal I/O or user prompts. All calculations
use Python's Decimal type to guarantee financial precision and avoid floating-point errors.

Calculation Order:
1. Distance-based Slab Fare
2. Senior Citizen Discount (strictly age > 60)
3. Train Premium Multiplier
4. Travel Class Multiplier
5. Excess Baggage Fee
6. Flat Train Surcharge (per-passenger)
Followed by:
- Booking subtotal aggregation
- Optional promotional discounts (ADG20, WINTER500)
- Final payable amount
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional, Tuple, Union

# Constant rates and limits
BASE_FARE = Decimal("100.00")
SLAB_1_KM_LIMIT = Decimal("100.00")
SLAB_1_RATE = Decimal("1.00")
SLAB_2_KM_LIMIT = Decimal("200.00")
SLAB_2_RATE = Decimal("0.80")
SLAB_3_RATE = Decimal("0.60")

SENIOR_AGE_THRESHOLD = 60
SENIOR_DISCOUNT_PERCENT = Decimal("0.40")
SENIOR_FARE_FACTOR = Decimal("1.00") - SENIOR_DISCOUNT_PERCENT  # 0.60

BAGGAGE_RATE_PER_KG = Decimal("15.00")

TWO_PLACES = Decimal("0.01")


def _to_decimal(value: Union[int, float, str, Decimal]) -> Decimal:
    """Safely convert any numeric input to Decimal."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _round_currency(amount: Decimal) -> Decimal:
    """Round currency amount to two decimal places using standard half-up rounding."""
    return amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


# --- Step 1: Slab Fare ---
def calculate_slab_fare(distance: Union[int, float, str, Decimal]) -> Decimal:
    """Calculate the distance-based cumulative slab fare.

    Formula:
    - Base fare: INR 100.00
    - First 100 km: INR 1.00 / km
    - Next 200 km (101 - 300 km): INR 0.80 / km
    - Distance beyond 300 km: INR 0.60 / km

    Raises ValueError if distance is negative.
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
    """Apply senior citizen discount (40% off) if age is STRICTLY GREATER than 60.

    Passengers aged 60 or below receive no discount.
    Formula: Step 2 fare = Step 1 fare * 0.60
    """
    if age < 0:
        raise ValueError("Age cannot be negative.")

    if age > SENIOR_AGE_THRESHOLD:
        discounted = fare * SENIOR_FARE_FACTOR
        return _round_currency(discounted)
    return _round_currency(fare)


# --- Step 3: Train Premium ---
def apply_train_premium(fare: Decimal, train_multiplier: Union[float, str, Decimal]) -> Decimal:
    """Apply the train type multiplier to the Step 2 fare.

    Fast Passenger: 1.00
    Express: 1.25
    Superfast: 1.50
    """
    multiplier = _to_decimal(train_multiplier)
    if multiplier <= Decimal("0"):
        raise ValueError("Train multiplier must be positive.")
    result = fare * multiplier
    return _round_currency(result)


# --- Step 4: Class Multiplier ---
def apply_class_multiplier(fare: Decimal, class_multiplier: Union[float, str, Decimal]) -> Decimal:
    """Apply the travel class multiplier to the Step 3 fare.

    Sleeper: 1.0
    AC 3-Tier: 1.5
    AC 2-Tier: 2.0
    """
    multiplier = _to_decimal(class_multiplier)
    if multiplier <= Decimal("0"):
        raise ValueError("Class multiplier must be positive.")
    result = fare * multiplier
    return _round_currency(result)


# --- Step 5: Excess Baggage Fee ---
def calculate_excess_baggage_charges(
    baggage_weight: Union[int, float, str, Decimal],
    free_allowance: Union[int, float, str, Decimal],
) -> Decimal:
    """Calculate baggage fee based on weight and free allowance.

    Baggage weight must be strictly positive (> 0).
    Fee = max(0, weight - allowance) * INR 15.00
    """
    weight = _to_decimal(baggage_weight)
    allowance = _to_decimal(free_allowance)

    if weight <= Decimal("0"):
        raise ValueError("Baggage weight must be strictly positive.")
    if allowance < Decimal("0"):
        raise ValueError("Free baggage allowance cannot be negative.")

    excess_weight = max(Decimal("0"), weight - allowance)
    fee = excess_weight * BAGGAGE_RATE_PER_KG
    return _round_currency(fee)


# --- Step 6: Flat Train Surcharge ---
def apply_train_surcharge(fare: Decimal, surcharge: Union[int, float, str, Decimal]) -> Decimal:
    """Add flat per-passenger train surcharge to Step 5 fare.

    Superfast: INR 100.00
    Express: INR 50.00
    Fast Passenger: INR 0.00
    """
    sc = _to_decimal(surcharge)
    if sc < Decimal("0"):
        raise ValueError("Surcharge cannot be negative.")
    return _round_currency(fare + sc)


# --- Complete Passenger Fare Calculation ---
def calculate_complete_passenger_fare(
    distance: int,
    age: int,
    train_multiplier: Union[float, str, Decimal],
    class_multiplier: Union[float, str, Decimal],
    baggage_weight: Union[float, str, Decimal],
    free_allowance: Union[float, str, Decimal],
    train_surcharge: Union[int, float, str, Decimal],
) -> Dict[str, object]:
    """Execute all six fare calculation steps in exact required sequence for one passenger.

    Returns a comprehensive breakdown dictionary containing intermediate and final values.
    """
    # Step 1: Slab Fare
    step1_slab_fare = calculate_slab_fare(distance)
    distance_charge = step1_slab_fare - BASE_FARE

    # Step 2: Senior Citizen Discount
    is_senior = age > SENIOR_AGE_THRESHOLD
    step2_fare = apply_senior_citizen_discount(step1_slab_fare, age)
    senior_discount_amount = step1_slab_fare - step2_fare

    # Step 3: Train Premium
    t_mult = _to_decimal(train_multiplier)
    step3_fare = apply_train_premium(step2_fare, t_mult)

    # Step 4: Class Premium
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


# --- Promotional Discounts ---
def apply_promotional_discount(
    subtotal: Decimal, promo_code: Optional[str]
) -> Tuple[Decimal, Decimal, str, str]:
    """Calculate promotional discount on booking subtotal.

    Supported codes:
    - 'ADG20': 20% discount on subtotal
    - 'WINTER500': Flat INR 500 discount (capped at subtotal)

    Rules:
    - Case-insensitive, leading/trailing whitespace ignored.
    - Empty or None entry: no discount.
    - Invalid nonempty code: 0 discount, reported as invalid.
    - Final payable amount never becomes negative.

    Returns:
    (discount_amount, final_payable, normalized_code, status_message)
    """
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

    # Invalid code
    return (
        Decimal("0.00"),
        sub,
        normalized,
        f"Invalid promo code '{normalized}'. No discount applied.",
    )


def calculate_final_payable(subtotal: Decimal, discount_amount: Decimal) -> Decimal:
    """Calculate final payable amount, ensuring it never drops below INR 0.00."""
    sub = _round_currency(_to_decimal(subtotal))
    disc = _round_currency(_to_decimal(discount_amount))
    return max(Decimal("0.00"), sub - disc)
