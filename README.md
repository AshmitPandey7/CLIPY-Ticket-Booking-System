# CLIPY - Modular Railway Ticket Booking System

A modular command-line railway ticket booking system in Python that simulates journey reservations across five major Indian cities. It calculates individual passenger fares based on distance slabs, age concessions, train speed premiums, travel classes, excess baggage charges, and promotional discounts.

---

## Quick Start (How to Run on Your Machine)

### 1. Clone the Repository
```bash
git clone https://github.com/AshmitPandey7/CLIPY-Ticket-Booking-System.git
cd CLIPY-Ticket-Booking-System
```

### 2. Run the Program
CLIPY is built entirely with Python's standard library. No `pip install` or external packages are required to run the application or test suite.

**Windows:**
```bash
python main.py
```
*(or `py main.py`)*

**Linux / macOS:**
```bash
python3 main.py
```

### 3. Run the Tests
To run the automated unit test suite (47 tests):

**Windows:**
```bash
python -m unittest discover -s tests -v
```

**Linux / macOS:**
```bash
python3 -m unittest discover -s tests -v
```

---

## Features

- **Bidirectional Routes**: 10 routes connecting New Delhi, Mumbai, Kolkata, Chennai, and Hyderabad.
- **Train Services**: Superfast (120 km/h), Express (110 km/h), and Fast Passenger (90 km/h) with travel duration estimates.
- **Travel Classes**: Sleeper, AC 3-Tier, and AC 2-Tier with distinct fare multipliers and free baggage allowances.
- **6-Step Fare Calculation**: Uses Python's `Decimal` module for currency precision and half-up rounding.
- **Senior Citizen Concession**: Automatic 40% discount on the slab fare for travelers strictly above 60 years of age.
- **Excess Baggage Fee**: Per-passenger luggage assessment (INR 15 per excess kg).
- **Promotional Discounts**: Supports `ADG20` (20% off subtotal) and `WINTER500` (flat INR 500 off subtotal).
- **Crash-Proof Input Validation**: Friendly reprompts on invalid entries without unexpected crashes.
- **Styled Terminal Interface**: Clean colored badges and a progress bar.

---

## Project Structure

```
CLIPY-Ticket-Booking-System/
│
├── main.py                    # Application entry point and CLI coordinator
├── routes.py                  # Static stations, distances, train types, and classes
├── fare.py                    # 6-step mathematical fare calculations and discounts
├── booking.py                 # Passenger roster and booking state management
├── validation.py              # Input validation rules and interactive prompts
├── README.md                  # Project overview and run guide
├── .gitignore                 # Standard Python gitignore
└── tests/
    └── test_booking_system.py # Automated test suite (47 unit and integration tests)
```

---

## Route Network & Distances

All routes are bidirectional:

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

## Train Types & Travel Classes

### Train Types

| Train Type | Average Speed | Multiplier | Flat Surcharge |
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

## Six-Step Fare Calculation Order

Individual passenger fares are calculated in the following order:

1. **Step 1 - Slab Fare**:
   - Fixed base fare = INR 100.00
   - First 100 km: INR 1.00 per km
   - 101 to 300 km: INR 0.80 per km
   - Beyond 300 km: INR 0.60 per km

2. **Step 2 - Senior Citizen Discount**:
   - If passenger age is strictly greater than 60 (`age > 60`), apply a 40% discount to the Step 1 fare (`Step 1 fare * 0.60`).
   - If 60 or below, no discount is applied.

3. **Step 3 - Train Premium**:
   - Multiply the Step 2 fare by the train multiplier (1.00x, 1.25x, or 1.50x).

4. **Step 4 - Class Multiplier**:
   - Multiply the Step 3 fare by the travel class multiplier (1.0x, 1.5x, or 2.0x).

5. **Step 5 - Excess Baggage Fee**:
   - If luggage exceeds the class allowance, charge INR 15 per excess kg:
     `Excess Fee = (Weight - Allowance) * 15`
   - Added to the Step 4 fare.

6. **Step 6 - Flat Train Surcharge**:
   - Add flat train surcharge based on service (Superfast: INR 100, Express: INR 50, Fast Passenger: INR 0).

---

## Promotional Codes

Applied after summing all passenger fares into the booking subtotal:

- **`ADG20`**: 20% discount on the booking subtotal (`Subtotal * 0.20`).
- **`WINTER500`**: Flat INR 500 discount (`min(Subtotal, 500)`).
- Promo codes are case-insensitive. Blank entries proceed without a discount.
- The final total is never negative.

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
