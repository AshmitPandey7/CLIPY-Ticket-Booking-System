"""CLIPY - Modular Railway Ticket Booking System."""

import os
import sys
import time
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

# Terminal styling and color setup
try:
    import colorama
    colorama.init(autoreset=True)
except ImportError:
    pass

os.system("")

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
RED = "\033[91m"
WHITE = "\033[97m"


def render_progress(task_name: str, duration: float = 0.35) -> None:
    """Displays a clean progress bar for terminal feedback."""
    steps = 22
    delay = duration / steps
    for i in range(steps + 1):
        bar = "#" * i + "-" * (steps - i)
        percent = int((i / steps) * 100)
        sys.stdout.write(f"\r  {CYAN}{task_name:<28}{RESET} [{GREEN}{bar}{RESET}] {percent:>3}%")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")


def print_header() -> None:
    """Prints the application header banner."""
    print(f"\n{BOLD}{BLUE}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}             CLIPY -- RAILWAY TICKET BOOKING SYSTEM{RESET}")
    print(f"{BOLD}{BLUE}======================================================================{RESET}")


def display_cities(cities: List[str]) -> None:
    """Prints available railway stations."""
    print(f"\n{BOLD}{WHITE}Supported Stations:{RESET}")
    for i, city in enumerate(cities, start=1):
        print(f"  {CYAN}{i}.{RESET} {city}")


def display_train_types(train_keys: List[str]) -> None:
    """Prints train options."""
    print(f"\n{BOLD}{WHITE}Available Train Services:{RESET}")
    for i, name in enumerate(train_keys, start=1):
        info = TRAIN_TYPES[name]
        speed = info["speed"]
        desc = info["description"]
        print(f"  {CYAN}{i}.{RESET} {BOLD}{name:<15}{RESET} | Speed: {YELLOW}{speed:>3} km/h{RESET} | {DIM}{desc}{RESET}")


def display_travel_classes(class_keys: List[str]) -> None:
    """Prints travel class options."""
    print(f"\n{BOLD}{WHITE}Available Travel Classes:{RESET}")
    for i, name in enumerate(class_keys, start=1):
        info = TRAVEL_CLASSES[name]
        multiplier = info["multiplier"]
        allowance = info["baggage_allowance"]
        desc = info["description"]
        print(
            f"  {CYAN}{i}.{RESET} {BOLD}{name:<12}{RESET} | Fare: {YELLOW}{multiplier}x{RESET} | Free Baggage: {GREEN}{allowance:>2} kg{RESET} | {DIM}{desc}{RESET}"
        )


def display_passenger_breakdown(booking: Booking) -> None:
    """Displays detailed itemized calculation for each traveler."""
    print(f"\n{BOLD}{BLUE}======================================================================{RESET}")
    print(f"{BOLD}{WHITE}                      PASSENGER FARE BREAKDOWN{RESET}")
    print(f"{BOLD}{BLUE}======================================================================{RESET}")

    for i, p in enumerate(booking.passengers, start=1):
        b = p.fare_breakdown
        if not b:
            continue

        category_tag = f"{GREEN}[Senior Citizen >60]{RESET}" if b["is_senior"] else f"{DIM}[General <=60]{RESET}"
        print(f"\n{BOLD}Passenger #{i}: {p.name}{RESET} (Age: {p.age}) {category_tag}")
        print(f"  * Base Fare:                            INR {b['base_fare']:>8.2f}")
        print(f"  * Distance Charge ({b['distance']} km):             INR {b['distance_charge']:>8.2f}")
        print(f"  * Step 1 (Cumulative Slab Fare):        INR {b['step1_slab_fare']:>8.2f}")

        if b["is_senior"]:
            print(
                f"  * Step 2 (Senior Discount 40%):        {GREEN}-INR {b['senior_discount_amount']:>8.2f}{RESET} -> INR {b['step2_fare']:>8.2f}"
            )
        else:
            print(
                f"  * Step 2 (Senior Discount):             {DIM}Not applicable (Age {p.age} <= 60){RESET} -> INR {b['step2_fare']:>8.2f}"
            )

        print(f"  * Step 3 (Train Premium {b['train_multiplier']}x):             INR {b['step3_fare']:>8.2f}")
        print(f"  * Step 4 (Class Multiplier {b['class_multiplier']}x):          INR {b['step4_fare']:>8.2f}")

        excess_wt = b["excess_baggage_weight"]
        bag_fee = b["excess_baggage_fee"]
        if excess_wt > 0:
            print(
                f"  * Step 5 (Luggage {b['baggage_weight']} kg, {YELLOW}+{excess_wt} kg excess{RESET}):  {YELLOW}+INR {bag_fee:>8.2f}{RESET} -> INR {b['step5_fare']:>8.2f}"
            )
        else:
            print(
                f"  * Step 5 (Luggage {b['baggage_weight']} kg <= {b['baggage_allowance']} kg):  +INR {bag_fee:>8.2f} -> INR {b['step5_fare']:>8.2f}"
            )

        print(f"  * Step 6 (Train Surcharge):            +INR {b['train_surcharge']:>8.2f}")
        print(f"  ---------------------------------------------------------")
        print(f"  {BOLD}Final Individual Fare:                  {GREEN}INR {b['final_fare']:>8.2f}{RESET}")

    print(f"\n{BLUE}----------------------------------------------------------------------{RESET}")
    print(f"{BOLD}Booking Subtotal ({len(booking.passengers)} passenger(s)):             {GREEN}INR {booking.subtotal:>8.2f}{RESET}")
    print(f"{BLUE}----------------------------------------------------------------------{RESET}")


def display_final_receipt(booking: Booking) -> None:
    """Displays formatted journey receipt."""
    summary = booking.get_summary()

    print(f"\n{BOLD}{BLUE}======================================================================{RESET}")
    print(f"{BOLD}{GREEN}                      OFFICIAL BOOKING RECEIPT{RESET}")
    print(f"{BOLD}{BLUE}======================================================================{RESET}")
    print(f"{DIM}[Demonstration Reference -- Not an official railway PNR]{RESET}")
    print(f"Reference ID:    {BOLD}{CYAN}{summary['reference_id']}{RESET}")
    print(f"Journey:         {BOLD}{summary['source']} -> {summary['destination']}{RESET} ({summary['distance']} km)")
    formatted_time = format_travel_time(
        summary["travel_time_hours"], summary["travel_time_minutes"]
    )
    print(f"Train Service:   {summary['train_type']} ({summary['train_speed']} km/h)")
    print(f"Travel Class:    {summary['travel_class']}")
    print(f"Estimated Time:  {formatted_time}")
    print(f"Total Travelers: {summary['passenger_count']}")

    print(f"\n{BOLD}Passenger Roster:{RESET}")
    for idx, p in enumerate(summary["passengers"], start=1):
        final_p_fare = p["breakdown"]["final_fare"]
        print(
            f"  {idx}. {p['name']:<22} | Age: {p['age']:>3} | Luggage: {p['baggage_weight']:>4.1f} kg | Fare: {GREEN}INR {final_p_fare:>8.2f}{RESET}"
        )

    print(f"\n{BOLD}Payment Summary:{RESET}")
    print(f"  Subtotal:                               INR {summary['subtotal']:>8.2f}")
    if summary["promo_code"] and summary["promo_discount"] > 0:
        print(
            f"  Promo Discount ({CYAN}{summary['promo_code']}{RESET}):               {GREEN}-INR {summary['promo_discount']:>8.2f}{RESET}"
        )
    else:
        print(f"  Promo Discount:                         INR     0.00")
    print(f"  {DIM}-------------------------------------------------------{RESET}")
    print(f"  {BOLD}FINAL AMOUNT PAYABLE:                   {BOLD}{GREEN}INR {summary['final_total']:>8.2f}{RESET}")
    print(f"{BOLD}{BLUE}======================================================================{RESET}")
    print(f"{GREEN}Booking confirmed! Have a pleasant journey.{RESET}")


def run_booking_flow() -> None:
    """Runs a single ticket reservation."""
    cities = get_cities()
    display_cities(cities)

    # Station selection
    source = prompt_city(f"\n{BOLD}Select Origin station (number or name): {RESET}", cities)
    print(f"  -> Origin: {GREEN}{source}{RESET}")

    destination = prompt_city(
        f"{BOLD}Select Destination station (number or name): {RESET}", cities, disallowed_city=source
    )
    print(f"  -> Destination: {GREEN}{destination}{RESET}")

    # Train selection
    train_keys = list(TRAIN_TYPES.keys())
    display_train_types(train_keys)
    train_choice = prompt_menu_selection(
        f"\n{BOLD}Select Train Service (1-{len(train_keys)}): {RESET}", len(train_keys)
    )
    selected_train = train_keys[train_choice - 1]
    print(f"  -> Selected Service: {GREEN}{selected_train}{RESET}")

    # Class selection
    class_keys = list(TRAVEL_CLASSES.keys())
    display_travel_classes(class_keys)
    class_choice = prompt_menu_selection(
        f"\n{BOLD}Select Travel Class (1-{len(class_keys)}): {RESET}", len(class_keys)
    )
    selected_class = class_keys[class_choice - 1]
    print(f"  -> Selected Class: {GREEN}{selected_class}{RESET}")

    # Route summary
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
        f"\n{CYAN}[i] Distance: {booking.distance} km | Estimated Duration: {formatted_time}{RESET}"
    )

    # Passenger details
    passenger_count = prompt_passenger_count()
    for i in range(1, passenger_count + 1):
        name, age, weight = prompt_passenger_details(i)
        booking.add_passenger(name, age, weight)

    # Calculate fares
    print()
    render_progress("Calculating passenger fares...")
    booking.calculate_all_fares()

    # Breakdown table
    display_passenger_breakdown(booking)

    # Promotional Code
    print(f"\n{BOLD}{WHITE}Available Offers:{RESET}")
    print(f"  - {CYAN}ADG20{RESET}     : 20% discount on entire booking subtotal")
    print(f"  - {CYAN}WINTER500{RESET} : Flat INR 500 off on booking subtotal")
    promo_input = prompt_input(
        f"\nEnter promo code (or press Enter to skip): "
    ).strip()

    if promo_input:
        discount, final_payable, message = booking.apply_promo(promo_input)
        if discount > 0:
            print(f"  {GREEN}[+] {message}{RESET}")
        else:
            print(f"  {YELLOW}[!] {message}{RESET}")
    else:
        booking.apply_promo(None)

    # Final receipt
    print()
    render_progress("Generating booking receipt...")
    display_final_receipt(booking)


def main() -> None:
    """Main program loop."""
    print_header()

    while True:
        try:
            run_booking_flow()
            print()
            book_again = prompt_yes_no("Would you like to make another booking?", default=False)
            if not book_again:
                print(f"\n{CYAN}Thank you for using CLIPY. Goodbye!{RESET}\n")
                break
            print("\n" * 2)
            print_header()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{YELLOW}Session cancelled by user. Exiting CLIPY.{RESET}")
            sys.exit(0)
        except Exception as err:
            print(f"\n{RED}[Error] Unexpected issue: {err}{RESET}")
            retry = prompt_yes_no("Restart booking?", default=True)
            if not retry:
                print(f"\n{CYAN}Exiting CLIPY.{RESET}")
                break


if __name__ == "__main__":
    main()
