# CLIPY - Modular Railway Ticket Booking System

A modular command-line railway ticket booking system in Python that simulates journey reservations across five major Indian cities. It handles route distances, train types, travel classes, individual passenger fare calculations, baggage charges, and promotional discounts.

---

## Features

- **Bidirectional Routes**: Supports journeys between 5 major stations (New Delhi, Mumbai, Kolkata, Chennai, Hyderabad) across 10 routes.
- **Train Services**: Superfast (120 km/h), Express (110 km/h), and Fast Passenger (90 km/h) with travel time estimates.
- **Travel Classes**: Sleeper, AC 3-Tier, and AC 2-Tier with specific fare multipliers and baggage allowances.
- **6-Step Fare Calculation**: Uses Python's `Decimal` module for precision and standard half-up rounding.
- **Senior Citizen Concession**: Automatically gives a 40% discount on the slab fare for travelers strictly above 60 years old.
- **Excess Baggage Fee**: Per-passenger excess luggage charges (INR 15/kg).
- **Promo Codes**: Optional discount codes (`ADG20` and `WINTER500`).
- **Input Validation**: Clean error messages that reprompt on invalid inputs without crashing.
- **Colorized CLI**: Styled terminal interface with colored badges and a progress bar.

---

## Project Structure

```
CLIPY-Ticket-Booking-System/
│
├── main.py                    # Entry point and CLI coordinator
├── routes.py                  # Stations, distances, trains, and classes
├── fare.py                    # 6-step fare calculations and promo discounts
├── booking.py                 # Passenger roster and booking management
├── validation.py              # Input validation helpers and terminal prompts
├── README.md                  # Project documentation and instructions
├── .gitignore                 # Python gitignore
└── tests/
    └── test_booking_system.py # Automated unittest suite (47 tests)
```

---

## Requirements

- Python 3.8 or higher.
- Built with Python's standard library. No external packages are required to run the core program or test suite.
- *(Optional)* `colorama` for enhanced color support on legacy Windows terminals (standard ANSI colors work out-of-the-box on modern Windows 10/11, Linux, and macOS).

---

## How to Run

### 1. Run the Application

On Windows:
```bash
python main.py
```
or with the Windows launcher:
```bash
py main.py
```

On Linux / macOS:
```bash
python3 main.py
```

### 2. Run the Test Suite

Execute the unit test suite:

```bash
python -m unittest discover -s tests -v
```

On Linux / macOS:
```bash
python3 -m unittest discover -s tests -v
```

---

## Route Network and Distances

All routes work in either direction:

| Route | Distance |
|---|---:|
| New Delhi <-> Mumbai | 1,460 km |
| New Delhi <-> Kolkata | 1,525 km |
| New Delhi <-> Chennai | 2,200 km |
| New Delhi <-> Hyderabad | 1,670 km |
| Mumbai <-> Kolkata | 1,970 km |
| Mumbai <-> Chennai | 1,300 km |
| Mumbai <-> Hyderabad | 711 km |
| Kolkata <-> Chennai | 1,200 km |
| Kolkata <-> Hyderabad | 1,600 km |
| Chennai <-> Hyderabad | 633 km |

---

## Train Types and Travel Classes

### Train Types

| Train Type | Speed | Multiplier | Surcharge |
|---|---:|---:|---:|
| Superfast | 120 km/h | 1.50x | INR 100.00 |
| Express | 110 km/h | 1.25x | INR 50.00 |
| Fast Passenger | 90 km/h | 1.00x | INR 0.00 |

*Estimated Travel Time = Route Distance / Train Speed*

### Travel Classes

| Class | Multiplier | Free Baggage Allowance |
|---|---:|---:|
| Sleeper | 1.0x | 20 kg |
| AC 3-Tier | 1.5x | 30 kg |
| AC 2-Tier | 2.0x | 40 kg |

---

## Fare Calculation Steps

Each passenger's fare is calculated in the following order:

1. **Step 1 - Slab Fare**:
   - Base fare = INR 100.00
   - First 100 km: INR 1.00 per km
   - 101 to 300 km: INR 0.80 per km
   - Beyond 300 km: INR 0.60 per km

2. **Step 2 - Senior Citizen Discount**:
   - If passenger age is strictly greater than 60 (`age > 60`), apply a 40% discount to Step 1 fare (`Step 1 fare * 0.60`).
   - If 60 or below, no discount is applied.

3. **Step 3 - Train Premium**:
   - Multiply the Step 2 fare by the train multiplier (1.00x, 1.25x, or 1.50x).

4. **Step 4 - Class Multiplier**:
   - Multiply the Step 3 fare by the travel class multiplier (1.0x, 1.5x, or 2.0x).

5. **Step 5 - Excess Baggage Fee**:
   - If baggage exceeds the class allowance, charge INR 15 per excess kg:
     `Excess Fee = (Weight - Allowance) * 15`
   - Added to Step 4 fare.

6. **Step 6 - Flat Train Surcharge**:
   - Add flat train surcharge based on service (Superfast: INR 100, Express: INR 50, Fast Passenger: INR 0).

---

## Promotional Codes

Applied to the booking subtotal:

- **`ADG20`**: 20% discount on booking subtotal (`Subtotal * 0.20`).
- **`WINTER500`**: Flat INR 500 discount (`min(Subtotal, 500)`).
- Promo codes are case-insensitive. Blank entries proceed without a promo.

---

## Sample Booking Receipt

```text
======================================================================
                      OFFICIAL BOOKING RECEIPT
======================================================================
[Demonstration Reference -- Not an official railway PNR]
Reference ID:    DEMO-CLP-AB12CD
Journey:         New Delhi -> Mumbai (1460 km)
Train Service:   Superfast (120 km/h)
Travel Class:    AC 3-Tier
Estimated Time:  12 hrs 10 mins
Total Travelers: 2

Passenger Roster:
  1. Rajesh Sharma          | Age:  65 | Luggage: 35.0 kg | Fare: INR  1600.60
  2. Priya Sharma           | Age:  30 | Luggage: 25.0 kg | Fare: INR  2476.00

Payment Summary:
  Subtotal:                               INR  4076.60
  Promo Discount (ADG20):               -INR   815.32
  -------------------------------------------------------
  FINAL AMOUNT PAYABLE:                   INR  3261.28
======================================================================
```
