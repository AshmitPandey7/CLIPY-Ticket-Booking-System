"""Booking management and passenger data handling."""

from dataclasses import dataclass
from decimal import Decimal
import random
import string
from typing import Any, Dict, List, Optional, Tuple, Union

from routes import (
    calculate_travel_time,
    get_class_info,
    get_distance,
    get_train_info,
)
from fare import (
    apply_promotional_discount,
    calculate_complete_passenger_fare,
)


@dataclass
class Passenger:
    """Stores individual passenger information."""

    name: str
    age: int
    baggage_weight: Decimal
    fare_breakdown: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Passenger name cannot be empty.")
        if self.age <= 0 or self.age > 125:
            raise ValueError(f"Invalid age '{self.age}'. Must be between 1 and 125.")
        if not isinstance(self.baggage_weight, Decimal):
            self.baggage_weight = Decimal(str(self.baggage_weight))
        if self.baggage_weight <= Decimal("0"):
            raise ValueError("Baggage weight must be strictly positive.")


class Booking:
    """Manages the booking workflow for a journey and its passengers."""

    def __init__(
        self,
        source: str,
        destination: str,
        train_type: str,
        travel_class: str,
    ) -> None:
        self.source = source
        self.destination = destination
        self.train_type = train_type
        self.travel_class = travel_class

        # Fetch route details
        self.distance: int = get_distance(self.source, self.destination)
        self.train_info: Dict[str, Any] = get_train_info(self.train_type)
        self.class_info: Dict[str, Any] = get_class_info(self.travel_class)

        # Calculate estimated journey time
        speed = int(self.train_info["speed"])
        self.travel_time: Tuple[int, int] = calculate_travel_time(self.distance, speed)

        # Passenger list
        self.passengers: List[Passenger] = []

        # Totals and discounts
        self.subtotal: Decimal = Decimal("0.00")
        self.promo_code: Optional[str] = None
        self.promo_discount: Decimal = Decimal("0.00")
        self.promo_message: str = "No promo code applied."
        self.final_total: Decimal = Decimal("0.00")

        # Demo reference ID
        random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.reference_id: str = f"DEMO-CLP-{random_suffix}"

    def add_passenger(
        self,
        name: str,
        age: int,
        baggage_weight: Union[Decimal, float, str],
    ) -> Passenger:
        """Adds a new passenger to the booking."""
        p = Passenger(name=name, age=age, baggage_weight=Decimal(str(baggage_weight)))
        self.passengers.append(p)
        return p

    def calculate_all_fares(self) -> Decimal:
        """Calculates fares for each passenger and sums the subtotal."""
        if not self.passengers:
            raise ValueError("Cannot calculate fares without passengers.")

        running_subtotal = Decimal("0.00")
        train_multiplier = self.train_info["premium_multiplier"]
        train_surcharge = self.train_info["surcharge"]
        class_multiplier = self.class_info["multiplier"]
        baggage_allowance = self.class_info["baggage_allowance"]

        for passenger in self.passengers:
            breakdown = calculate_complete_passenger_fare(
                distance=self.distance,
                age=passenger.age,
                train_multiplier=train_multiplier,
                class_multiplier=class_multiplier,
                baggage_weight=passenger.baggage_weight,
                free_allowance=baggage_allowance,
                train_surcharge=train_surcharge,
            )
            passenger.fare_breakdown = breakdown
            running_subtotal += breakdown["final_fare"]

        self.subtotal = running_subtotal

        # Re-apply discount if a promo was already entered
        if self.promo_code:
            self.apply_promo(self.promo_code)
        else:
            self.final_total = self.subtotal

        return self.subtotal

    def apply_promo(self, code: Optional[str]) -> Tuple[Decimal, Decimal, str]:
        """Applies a promo code and updates the final total."""
        discount, final_payable, normalized_code, message = apply_promotional_discount(
            self.subtotal, code
        )
        self.promo_code = normalized_code if (discount > Decimal("0.00") and normalized_code) else None
        self.promo_discount = discount
        self.promo_message = message
        self.final_total = final_payable
        return discount, final_payable, message

    def get_summary(self) -> Dict[str, Any]:
        """Returns structured summary dictionary of the booking."""
        return {
            "reference_id": self.reference_id,
            "source": self.source,
            "destination": self.destination,
            "distance": self.distance,
            "train_type": self.train_type,
            "train_speed": self.train_info["speed"],
            "travel_class": self.travel_class,
            "travel_time_hours": self.travel_time[0],
            "travel_time_minutes": self.travel_time[1],
            "passenger_count": len(self.passengers),
            "passengers": [
                {
                    "name": p.name,
                    "age": p.age,
                    "baggage_weight": p.baggage_weight,
                    "breakdown": p.fare_breakdown,
                }
                for p in self.passengers
            ],
            "subtotal": self.subtotal,
            "promo_code": self.promo_code,
            "promo_discount": self.promo_discount,
            "promo_message": self.promo_message,
            "final_total": self.final_total,
        }
