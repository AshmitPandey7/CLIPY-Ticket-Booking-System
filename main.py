"""main.py - Entry point and user-facing coordinator for CLIPY.

CLIPY: Modular Railway Ticket Booking System.
This module coordinates the CLI user interface, prompts the user for inputs,
delegates validation and business operations to supporting modules,
and presents fare breakdowns and booking receipts.

Architecture Note:
- No static route tables reside in this file (owned by routes.py).
- No fare mathematics are implemented in this file (owned by fare.py).
"""

import sys
from typing import List

from routes import (
    format_travel_time,
    get_cities,
    TRAIN_TYPES,
    TRAVEL_CLASSES,
)
from booking import Booking
from validation import (
    prompt_city,
    prompt_input,
    prompt_menu_selection,
    prompt_passenger_count,
    prompt_passenger_details,
    prompt_yes_no,
)


def print_header() -> None:
    """Display the main CLI header banner."""
    print("=" * 68)
    print("           CLIPY -- MODULAR RAILWAY TICKET BOOKING SYSTEM")
    print("=" * 68)


def display_cities(cities: List[str]) -> None:
    """Display numbered list of supported railway stations."""
    print("\nSupported Railway Stations:")
    for i, city in enumerate(cities, start=1):
        print(f"  {i}. {city}")


def display_train_types(train_keys: List[str]) -> None:
    """Display available train types with speeds and descriptions."""
    print("\nAvailable Train Types:")
    for i, name in enumerate(train_keys, start=1):
        info = TRAIN_TYPES[name]
        speed = info["speed"]
        desc = info["description"]
        print(f"  {i}. {name:<15} | Speed: {speed:>3} km/h | {desc}")


def display_travel_classes(class_keys: List[str]) -> None:
    """Display available travel classes with fare multipliers and free baggage allowances."""
    print("\nAvailable Travel Classes:")
    for i, name in enumerate(class_keys, start=1):
        info = TRAVEL_CLASSES[name]
        multiplier = info["multiplier"]
        allowance = info["baggage_allowance"]
        desc = info["description"]
        print(
            f"  {i}. {name:<12} | Multiplier: {multiplier}x | Free Baggage: {allowance:>2} kg | {desc}"
        )


def display_passenger_breakdown(booking: Booking) -> None:
    """Display detailed step-by-step fare breakdown for all passengers."""
    print("\n" + "=" * 68)
    print("                      PASSENGER FARE BREAKDOWN")
    print("=" * 68)

    for i, p in enumerate(booking.passengers, start=1):
        b = p.fare_breakdown
        if not b:
            continue

        senior_tag = "Senior Citizen (>60)" if b["is_senior"] else "General (<=60)"
        print(f"\nPassenger #{i}: {p.name} (Age: {p.age}, {senior_tag})")
        print(f"  - Base Fare:                            INR {b['base_fare']:>8.2f}")
        print(
            f"  - Distance Charge ({b['distance']} km):             INR {b['distance_charge']:>8.2f}"
        )
        print(f"  - Step 1 (Cumulative Slab Fare):        INR {b['step1_slab_fare']:>8.2f}")

        if b["is_senior"]:
            print(
                f"  - Step 2 (Senior Discount 40%):        -INR {b['senior_discount_amount']:>8.2f} -> INR {b['step2_fare']:>8.2f}"
            )
        else:
            print(
                f"  - Step 2 (Senior Discount):             Not applicable (Age {p.age} <= 60) -> INR {b['step2_fare']:>8.2f}"
            )

        print(
            f"  - Step 3 (Train Premium {b['train_multiplier']}x):             INR {b['step3_fare']:>8.2f}"
        )
        print(
            f"  - Step 4 (Class Multiplier {b['class_multiplier']}x):          INR {b['step4_fare']:>8.2f}"
        )

        excess_wt = b["excess_baggage_weight"]
        bag_fee = b["excess_baggage_fee"]
        if excess_wt > 0:
            print(
                f"  - Step 5 (Baggage {b['baggage_weight']} kg, +{excess_wt} kg):      +INR {bag_fee:>8.2f} -> INR {b['step5_fare']:>8.2f}"
            )
        else:
            print(
                f"  - Step 5 (Baggage {b['baggage_weight']} kg <= {b['baggage_allowance']} kg):  +INR {bag_fee:>8.2f} -> INR {b['step5_fare']:>8.2f}"
            )

        print(
            f"  - Step 6 (Train Surcharge):            +INR {b['train_surcharge']:>8.2f}"
        )
        print(f"  ---------------------------------------------------------")
        print(f"  Final Individual Fare:                  INR {b['final_fare']:>8.2f}")

    print("\n" + "-" * 68)
    print(f"Booking Subtotal ({len(booking.passengers)} passenger(s)):             INR {booking.subtotal:>8.2f}")
    print("-" * 68)


def display_final_receipt(booking: Booking) -> None:
    """Display clean final booking summary and receipt."""
    summary = booking.get_summary()

    print("\n" + "=" * 68)
    print("                      OFFICIAL BOOKING RECEIPT")
    print("=" * 68)
    print("[Demonstration Reference -- Not an official railway PNR]")
    print(f"Reference ID:    {summary['reference_id']}")
    print(f"Journey:         {summary['source']} -> {summary['destination']} ({summary['distance']} km)")
    formatted_time = format_travel_time(
        summary["travel_time_hours"], summary["travel_time_minutes"]
    )
    print(f"Train Service:   {summary['train_type']} ({summary['train_speed']} km/h)")
    print(f"Travel Class:    {summary['travel_class']}")
    print(f"Estimated Time:  {formatted_time}")
    print(f"Total Travelers: {summary['passenger_count']}")

    print("\nPassenger Roster:")
    for idx, p in enumerate(summary["passengers"], start=1):
        final_p_fare = p["breakdown"]["final_fare"]
        print(
            f"  {idx}. {p['name']:<22} | Age: {p['age']:>3} | Luggage: {p['baggage_weight']:>4.1f} kg | Fare: INR {final_p_fare:>8.2f}"
        )

    print("\nPayment Summary:")
    print(f"  Subtotal:                               INR {summary['subtotal']:>8.2f}")
    if summary["promo_code"] and summary["promo_discount"] > 0:
        print(
            f"  Promo Discount ({summary['promo_code']}):               -INR {summary['promo_discount']:>8.2f}"
        )
    else:
        print(f"  Promo Discount:                         INR     0.00")
    print("  " + "-" * 55)
    print(f"  FINAL AMOUNT PAYABLE:                   INR {summary['final_total']:>8.2f}")
    print("=" * 68)
    print("Thank you for choosing CLIPY Railway System!")


def run_booking_flow() -> None:
    """Execute a single ticket booking workflow."""
    cities = get_cities()
    display_cities(cities)

    # 1. Select Origin
    source = prompt_city("\nSelect Origin station (number or name): ", cities)
    print(f"-> Origin selected: {source}")

    # 2. Select Destination
    destination = prompt_city(
        "Select Destination station (number or name): ", cities, disallowed_city=source
    )
    print(f"-> Destination selected: {destination}")

    # 3. Train Type Selection
    train_keys = list(TRAIN_TYPES.keys())
    display_train_types(train_keys)
    train_choice = prompt_menu_selection(
        f"\nSelect Train Type (1-{len(train_keys)}): ", len(train_keys)
    )
    selected_train = train_keys[train_choice - 1]
    print(f"-> Train selected: {selected_train}")

    # 4. Travel Class Selection
    class_keys = list(TRAVEL_CLASSES.keys())
    display_travel_classes(class_keys)
    class_choice = prompt_menu_selection(
        f"\nSelect Travel Class (1-{len(class_keys)}): ", len(class_keys)
    )
    selected_class = class_keys[class_choice - 1]
    print(f"-> Class selected: {selected_class}")

    # Initialize Booking object
    booking = Booking(
        source=source,
        destination=destination,
        train_type=selected_train,
        travel_class=selected_class,
    )

    formatted_time = format_travel_time(
        booking.travel_time[0], booking.travel_time[1]
    )
    print(
        f"\n[Route Info] Distance: {booking.distance} km | Estimated Travel Time: {formatted_time}"
    )

    # 5. Passengers Entry
    passenger_count = prompt_passenger_count()
    for i in range(1, passenger_count + 1):
        name, age, weight = prompt_passenger_details(i)
        booking.add_passenger(name, age, weight)

    # 6. Calculate individual fares and subtotal
    booking.calculate_all_fares()

    # 7. Display Step-by-Step Breakdown
    display_passenger_breakdown(booking)

    # 8. Promotional Code
    print("\nPromotional Offers Available:")
    print("  - ADG20     : 20% discount on entire booking subtotal")
    print("  - WINTER500 : Flat INR 500 off on booking subtotal")
    promo_input = prompt_input(
        "Enter promo code (or press Enter to skip): "
    ).strip()

    if promo_input:
        discount, final_payable, message = booking.apply_promo(promo_input)
        print(f"  -> {message}")
    else:
        booking.apply_promo(None)

    # 9. Final Booking Summary & Receipt
    display_final_receipt(booking)


def main() -> None:
    """Coordinate the overall CLI application loop."""
    print_header()

    while True:
        try:
            run_booking_flow()
            print()
            book_again = prompt_yes_no("Would you like to book another journey?", default=False)
            if not book_again:
                print("\nExiting CLIPY. Safe travels!")
                break
            print("\n" * 2)
            print_header()
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user. Exiting CLIPY. Goodbye!")
            sys.exit(0)
        except Exception as err:
            print(f"\n[Error] An unexpected error occurred: {err}")
            retry = prompt_yes_no("Would you like to restart the booking?", default=True)
            if not retry:
                print("\nExiting CLIPY.")
                break


if __name__ == "__main__":
    main()
