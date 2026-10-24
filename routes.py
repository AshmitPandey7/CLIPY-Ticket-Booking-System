"""routes.py - Static configuration data and lookup helpers for CLIPY.

This module centrally manages:
- Available railway stations (cities) and bidirectional distances.
- Train types, speeds, multipliers, and flat surcharges.
- Travel classes, fare multipliers, and free baggage allowances.
- Reusable lookup and travel-time calculation functions.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple

# Supported cities
CITIES: List[str] = [
    "New Delhi",
    "Mumbai",
    "Kolkata",
    "Chennai",
    "Hyderabad",
]

# Bidirectional route distances in kilometres
# Stored with sorted tuple keys (city_a, city_b) where city_a < city_b
_ROUTE_DISTANCES: Dict[Tuple[str, str], int] = {
    ("Mumbai", "New Delhi"): 1460,
    ("Kolkata", "New Delhi"): 1525,
    ("Chennai", "New Delhi"): 2200,
    ("Hyderabad", "New Delhi"): 1670,
    ("Kolkata", "Mumbai"): 1970,
    ("Chennai", "Mumbai"): 1300,
    ("Hyderabad", "Mumbai"): 711,
    ("Chennai", "Kolkata"): 1200,
    ("Hyderabad", "Kolkata"): 1600,
    ("Chennai", "Hyderabad"): 633,
}

# Train specifications: average speed, premium multiplier, and flat surcharge
TRAIN_TYPES: Dict[str, Dict[str, object]] = {
    "Superfast": {
        "speed": 120,  # km/h
        "premium_multiplier": Decimal("1.50"),
        "surcharge": Decimal("100.00"),
        "description": "High-speed service (120 km/h)",
    },
    "Express": {
        "speed": 110,  # km/h
        "premium_multiplier": Decimal("1.25"),
        "surcharge": Decimal("50.00"),
        "description": "Standard express service (110 km/h)",
    },
    "Fast Passenger": {
        "speed": 90,  # km/h
        "premium_multiplier": Decimal("1.00"),
        "surcharge": Decimal("0.00"),
        "description": "Regular passenger service (90 km/h)",
    },
}

# Travel class specifications: fare multiplier and free baggage allowance
TRAVEL_CLASSES: Dict[str, Dict[str, object]] = {
    "Sleeper": {
        "multiplier": Decimal("1.0"),
        "baggage_allowance": Decimal("20.0"),  # kg
        "description": "Standard non-AC sleeper coach",
    },
    "AC 3-Tier": {
        "multiplier": Decimal("1.5"),
        "baggage_allowance": Decimal("30.0"),  # kg
        "description": "Air-conditioned 3-tier sleeper",
    },
    "AC 2-Tier": {
        "multiplier": Decimal("2.0"),
        "baggage_allowance": Decimal("40.0"),  # kg
        "description": "Air-conditioned 2-tier sleeper",
    },
}


def normalize_city_name(city_input: str) -> Optional[str]:
    """Normalize user input to match canonical city name.

    Handles leading/trailing whitespace and case-insensitive matching.
    Returns canonical city name if found, else None.
    """
    cleaned = city_input.strip().lower()
    for city in CITIES:
        if city.lower() == cleaned:
            return city
    return None


def get_cities() -> List[str]:
    """Return a copy of the list of supported cities."""
    return list(CITIES)


def get_distance(source: str, destination: str) -> int:
    """Retrieve the distance in km between source and destination.

    Routes are bidirectional.
    Raises ValueError if cities are invalid, identical, or not connected.
    """
    norm_source = normalize_city_name(source)
    norm_dest = normalize_city_name(destination)

    if not norm_source:
        raise ValueError(f"Invalid source city '{source}'.")
    if not norm_dest:
        raise ValueError(f"Invalid destination city '{destination}'.")

    if norm_source == norm_dest:
        raise ValueError("Source and destination cannot be the same city.")

    # Canonical order for dictionary key
    key = tuple(sorted([norm_source, norm_dest]))
    if key in _ROUTE_DISTANCES:
        return _ROUTE_DISTANCES[key]

    raise ValueError(f"No direct route found between {norm_source} and {norm_dest}.")


def get_available_destinations(source: str) -> List[str]:
    """Return list of valid destinations reachable from given source."""
    norm_source = normalize_city_name(source)
    if not norm_source:
        raise ValueError(f"Invalid source city '{source}'.")

    destinations = []
    for city in CITIES:
        if city != norm_source:
            key = tuple(sorted([norm_source, city]))
            if key in _ROUTE_DISTANCES:
                destinations.append(city)
    return destinations


def calculate_travel_time(distance: int, speed: int) -> Tuple[int, int]:
    """Calculate estimated travel time in hours and minutes.

    Formula: Travel time in hours = distance / speed.
    Returns: (hours, minutes)
    """
    if speed <= 0:
        raise ValueError("Train speed must be strictly positive.")
    if distance < 0:
        raise ValueError("Distance cannot be negative.")

    total_minutes = round((distance / speed) * 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return hours, minutes


def format_travel_time(hours: int, minutes: int) -> str:
    """Format travel time into a friendly string (e.g. '12 hrs 10 mins')."""
    parts = []
    if hours > 0:
        parts.append(f"{hours} hr{'s' if hours != 1 else ''}")
    if minutes > 0 or hours == 0:
        parts.append(f"{minutes} min{'s' if minutes != 1 else ''}")
    return " ".join(parts)


def get_train_info(train_type: str) -> Dict[str, object]:
    """Return specifications for a train type, or raise ValueError."""
    for name, info in TRAIN_TYPES.items():
        if name.lower() == train_type.strip().lower():
            return {"name": name, **info}
    raise ValueError(f"Unknown train type '{train_type}'. Valid types: {list(TRAIN_TYPES.keys())}")


def get_class_info(travel_class: str) -> Dict[str, object]:
    """Return specifications for a travel class, or raise ValueError."""
    for name, info in TRAVEL_CLASSES.items():
        if name.lower() == travel_class.strip().lower():
            return {"name": name, **info}
    raise ValueError(f"Unknown travel class '{travel_class}'. Valid classes: {list(TRAVEL_CLASSES.keys())}")
