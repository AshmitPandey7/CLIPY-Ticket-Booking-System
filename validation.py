"""validation.py - Reusable input validation and terminal prompt utilities for CLIPY.

This module provides:
1. Pure validation functions that verify data types, ranges, and business constraints.
2. Robust terminal prompting loops that catch invalid entries, inform the user,
   and reprompt without crashing.
"""

from decimal import Decimal, InvalidOperation
import re
from typing import List, Optional, Tuple

from routes import CITIES, get_distance, normalize_city_name

# Reasonable validation bounds
MIN_PASSENGER_AGE = 1
MAX_PASSENGER_AGE = 125
MIN_PASSENGERS_PER_BOOKING = 1
MAX_PASSENGERS_PER_BOOKING = 6
MAX_BAGGAGE_KG = Decimal("150.0")


# --- Pure Validation Functions ---
def validate_passenger_name(name_str: str) -> str:
    """Validate passenger full name.

    Must be non-empty, between 1 and 50 characters, and contain at least one letter.
    """
    cleaned = name_str.strip()
    if not cleaned:
        raise ValueError("Name cannot be empty. Please enter a valid passenger name.")
    if len(cleaned) > 50:
        raise ValueError("Name is too long (maximum 50 characters).")
    # Must contain at least one alphabet character
    if not re.search(r"[A-Za-z]", cleaned):
        raise ValueError("Name must contain letters.")
    return cleaned


def validate_passenger_age(age_str: str) -> int:
    """Validate passenger age as an integer between 1 and 125."""
    cleaned = age_str.strip()
    try:
        age = int(cleaned)
    except ValueError:
        raise ValueError("Age must be a whole number.")

    if age < MIN_PASSENGER_AGE or age > MAX_PASSENGER_AGE:
        raise ValueError(
            f"Age must be between {MIN_PASSENGER_AGE} and {MAX_PASSENGER_AGE}."
        )
    return age


def validate_baggage_weight(weight_str: str) -> Decimal:
    """Validate baggage weight in kg. Must be strictly positive (> 0)."""
    cleaned = weight_str.strip()
    try:
        weight = Decimal(cleaned)
    except (InvalidOperation, ValueError):
        raise ValueError("Baggage weight must be a valid number (e.g. 15 or 22.5).")

    if weight <= Decimal("0"):
        raise ValueError(
            "Baggage weight must be strictly positive (greater than 0 kg)."
        )
    if weight > MAX_BAGGAGE_KG:
        raise ValueError(
            f"Baggage weight exceeds the maximum allowed limit of {MAX_BAGGAGE_KG} kg."
        )
    return weight


def validate_passenger_count(
    count_str: str,
    min_count: int = MIN_PASSENGERS_PER_BOOKING,
    max_count: int = MAX_PASSENGERS_PER_BOOKING,
) -> int:
    """Validate number of passengers for a single booking."""
    cleaned = count_str.strip()
    try:
        count = int(cleaned)
    except ValueError:
        raise ValueError("Passenger count must be a whole number.")

    if count < min_count or count > max_count:
        raise ValueError(f"Number of passengers must be between {min_count} and {max_count}.")
    return count


def validate_city_choice(choice_str: str, available_cities: List[str]) -> str:
    """Validate a city choice given as either a 1-based index or city name."""
    cleaned = choice_str.strip()
    if not cleaned:
        raise ValueError("Selection cannot be empty.")

    # Try numeric index first
    try:
        index = int(cleaned)
        if 1 <= index <= len(available_cities):
            return available_cities[index - 1]
        raise ValueError(
            f"Please enter a number between 1 and {len(available_cities)}."
        )
    except ValueError as err:
        # If it wasn't a number or out of range, check if it was entered as a city name
        for city in available_cities:
            if city.lower() == cleaned.lower():
                return city
        # If int conversion error, show friendly message
        if "between 1 and" in str(err):
            raise
        raise ValueError(
            f"'{choice_str}' is not a recognized city in the options."
        )


def validate_route_pair(source: str, destination: str) -> int:
    """Validate that source and destination are valid, distinct, and form a route.

    Returns the route distance.
    """
    if source.strip().lower() == destination.strip().lower():
        raise ValueError("Source and destination cannot be the same city.")
    return get_distance(source, destination)


# --- Interactive Terminal Prompters ---
def prompt_input(prompt_text: str) -> str:
    """Read a raw line of input from the user, preserving EOFError / KeyboardInterrupt."""
    return input(prompt_text)


def prompt_city(
    prompt_text: str,
    available_cities: List[str],
    disallowed_city: Optional[str] = None,
) -> str:
    """Prompt user to select a city from a list, reprompting on invalid input.

    If disallowed_city is specified and chosen, rejects with a helpful message.
    """
    while True:
        try:
            raw = prompt_input(prompt_text)
            chosen = validate_city_choice(raw, available_cities)
            if disallowed_city and chosen.lower() == disallowed_city.lower():
                print(
                    f"  [!] Destination cannot be the same as origin ({disallowed_city}). Please choose a different station."
                )
                continue
            return chosen
        except ValueError as e:
            print(f"  [!] {e}")


def prompt_passenger_count() -> int:
    """Prompt for valid number of passengers (1 to 6)."""
    while True:
        try:
            raw = prompt_input(
                f"Enter number of passengers ({MIN_PASSENGERS_PER_BOOKING}-{MAX_PASSENGERS_PER_BOOKING}): "
            )
            return validate_passenger_count(raw)
        except ValueError as e:
            print(f"  [!] {e}")


def prompt_passenger_details(index: int) -> Tuple[str, int, Decimal]:
    """Prompt and collect details for passenger index (1-based)."""
    print(f"\n--- Passenger #{index} Details ---")

    # Name
    while True:
        try:
            raw_name = prompt_input("  Full Name: ")
            name = validate_passenger_name(raw_name)
            break
        except ValueError as e:
            print(f"  [!] {e}")

    # Age
    while True:
        try:
            raw_age = prompt_input("  Age: ")
            age = validate_passenger_age(raw_age)
            break
        except ValueError as e:
            print(f"  [!] {e}")

    # Baggage Weight
    while True:
        try:
            raw_weight = prompt_input("  Baggage Weight (in kg, e.g. 18.5): ")
            weight = validate_baggage_weight(raw_weight)
            break
        except ValueError as e:
            print(f"  [!] {e}")

    return name, age, weight


def prompt_menu_selection(prompt_text: str, max_choice: int) -> int:
    """Prompt for a numbered menu selection between 1 and max_choice."""
    while True:
        try:
            raw = prompt_input(prompt_text).strip()
            val = int(raw)
            if 1 <= val <= max_choice:
                return val
            print(f"  [!] Please select an option between 1 and {max_choice}.")
        except ValueError:
            print(f"  [!] Please enter a valid number between 1 and {max_choice}.")


def prompt_yes_no(prompt_text: str, default: bool = True) -> bool:
    """Prompt for a yes/no confirmation with a default."""
    hint = " [Y/n]: " if default else " [y/N]: "
    while True:
        raw = prompt_input(prompt_text + hint).strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  [!] Please enter 'y' for yes or 'n' for no.")
