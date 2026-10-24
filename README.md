# CLIPY -- Modular Railway Ticket Booking System

CLIPY is an interactive command-line railway ticket booking application written in Python. It simulates journey reservations across major Indian metropolitan corridors, calculating individual passenger fares using a cumulative distance slab structure, age-based concessions, train and class premiums, baggage allowances, and promotional discounts.

Built entirely with Python's standard library, CLIPY features a modular architecture that separates static configuration, mathematical computation, booking workflow, input validation, and user interface presentation.

---

## Features

- **Bidirectional Route Network**: Connects five major cities (New Delhi, Mumbai, Kolkata, Chennai, Hyderabad) across ten verified routes.
- **Service Types & Speed Dynamics**: Supports Superfast, Express, and Fast Passenger train types with estimated travel time calculations.
- **Travel Classes**: Sleeper, AC 3-Tier, and AC 2-Tier options with distinct fare multipliers and free baggage allowances.
- **Strict 6-Step Fare Calculation**: Implements financial calculations using Python's `Decimal` module for high precision and half-up rounding.
- **Senior Citizen Concession**: Automatically applies a 40% discount on slab fares for passengers strictly older than 60.
- **Excess Baggage Surcharge**: Per-passenger luggage assessment with automated excess fees (INR 15 per excess kg).
- **Promotional Offers**: Supports booking-level promo codes (`ADG20` and `WINTER500`) with negative total prevention.
- **Crash-Proof Input Validation**: Robust prompts that gracefully catch invalid numbers, strings, negative inputs, and out-of-range selections without crashing.
- **Multi-Passenger Support**: Books up to 6 passengers per journey with itemized breakdowns and reconciled subtotal billing.

---

## Python Version Requirements

- **Python 3.8+** (Tested on Python 3.13)
- No external third-party dependencies required.

---

## Project Structure

```
CLIPY-Ticket-Booking-System/
│
├── main.py                    # CLI coordinator and user interface
├── routes.py                  # Static route data, train types, and class specs
├── fare.py                    # Pure mathematical fare engine (6-step calculation)
├── booking.py                 # Passenger roster and booking business logic
├── validation.py              # Input validation rules and interactive prompters
├── README.md                  # Project documentation and run guide
├── .gitignore                 # Excludes Python bytecode and temporary caches
└── tests/
    └── test_booking_system.py # Automated unittest suite (47 unit/integration tests)
```

---

## How to Run the Application

### 1. Launch CLIPY

On Windows:
```bash
python main.py
# or if using the Windows Python launcher:
py main.py
```

On Linux / macOS:
```bash
python3 main.py
```

### 2. Follow the Interactive Prompts
1. **Select Origin City**: Pick by number (1--5) or type the city name.
2. **Select Destination City**: Pick by number or type the name (cannot be identical to origin).
3. **Select Train Type**: Choose between Superfast, Express, or Fast Passenger.
4. **Select Travel Class**: Choose between Sleeper, AC 3-Tier, or AC 2-Tier.
5. **Enter Passenger Count**: Enter 1 to 6 passengers.
6. **Enter Passenger Details**: Provide name, age, and baggage weight for each traveler.
7. **View Fare Breakdown**: Review the step-by-step calculation for each passenger and the booking subtotal.
8. **Apply Promo Code (Optional)**: Enter `ADG20`, `WINTER500`, or press Enter to skip.
9. **Review Final Receipt**: View the booking receipt and demonstration reference.
10. **Book Again or Exit**: Choose whether to start another booking or exit cleanly.

---

## How to Run the Automated Test Suite

Run the full automated test suite using Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -v
```

On Linux / macOS:
```bash
python3 -m unittest discover -s tests -v
```

All 47 tests verify route distances, cumulative slab pricing, senior citizen age boundaries, class and train multipliers, baggage fees, promotional codes, and end-to-end multi-passenger scenarios.

---

## Supported Routes and Distances

All routes operate bidirectionally:

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

## Train Services and Travel Classes

### Train Types

| Train Type | Average Speed | Multiplier | Flat Surcharge | Description |
|---|---:|---:|---:|---|
| **Superfast** | 120 km/h | 1.50x | INR 100.00 | High-speed express service |
| **Express** | 110 km/h | 1.25x | INR 50.00 | Standard intercity service |
| **Fast Passenger** | 90 km/h | 1.00x | INR 0.00 | Regular passenger service |

*Estimated Travel Time = Route Distance (km) / Train Speed (km/h)*

### Travel Classes

| Class | Fare Multiplier | Free Baggage Allowance |
|---|---:|---:|
| **Sleeper** | 1.0x | 20 kg per passenger |
| **AC 3-Tier** | 1.5x | 30 kg per passenger |
| **AC 2-Tier** | 2.0x | 40 kg per passenger |

---

## Six-Step Fare Calculation Order

Individual passenger fares are calculated strictly in this sequential order:

1. **Step 1 -- Cumulative Slab Fare**:
   - Fixed base fare: INR 100.00
   - First 100 km: INR 1.00 / km
   - Next 200 km (101--300 km): INR 0.80 / km
   - Distance beyond 300 km: INR 0.60 / km
   $$\text{Slab Fare} = 100 + \min(D, 100) \times 1.00 + \min(\max(D - 100, 0), 200) \times 0.80 + \max(D - 300, 0) \times 0.60$$

2. **Step 2 -- Senior Citizen Discount**:
   - If passenger age is **strictly greater than 60** (`age > 60`), apply a 40% discount on the Step 1 fare:
     $$\text{Step 2 Fare} = \text{Step 1 Fare} \times 0.60$$
   - Passengers aged 60 or below receive no discount.

3. **Step 3 -- Train Premium**:
   - Multiply the Step 2 result by the train multiplier (1.0x, 1.25x, or 1.50x).

4. **Step 4 -- Class Multiplier**:
   - Multiply the Step 3 result by the travel class multiplier (1.0x, 1.5x, or 2.0x).

5. **Step 5 -- Excess Baggage Fee**:
   - Free baggage allowance depends on class (20 kg, 30 kg, or 40 kg).
   - If luggage exceeds the allowance:
     $$\text{Excess Fee} = (\text{Baggage Weight} - \text{Allowance}) \times \text{INR 15.00}$$
   - Added directly to the Step 4 fare:
     $$\text{Step 5 Fare} = \text{Step 4 Fare} + \text{Excess Fee}$$

6. **Step 6 -- Flat Train Surcharge**:
   - Added per passenger based on train type:
     - Superfast: INR 100.00
     - Express: INR 50.00
     - Fast Passenger: INR 0.00
   $$\text{Final Individual Fare} = \text{Step 5 Fare} + \text{Train Surcharge}$$

---

## Promotional Discounts

After summing individual passenger fares to compute the booking subtotal, an optional promo code can be applied:

- **`ADG20`**: Deducts 20% of the entire booking subtotal.
  $$\text{Discount} = \text{Subtotal} \times 0.20$$
- **`WINTER500`**: Deducts a flat INR 500.00 from the booking subtotal.
  $$\text{Final Total} = \max(\text{Subtotal} - 500, 0)$$
- **Invalid / Empty Code**: Empty input skips the promo without error. Invalid non-empty codes notify the user and proceed with INR 0.00 discount.
- Promo codes are case-insensitive and ignore leading/trailing whitespace. Only one promo code may be applied per booking.

---

## Sample Booking Interaction

```text
====================================================================
           CLIPY -- MODULAR RAILWAY TICKET BOOKING SYSTEM
====================================================================

Supported Railway Stations:
  1. New Delhi
  2. Mumbai
  3. Kolkata
  4. Chennai
  5. Hyderabad

Select Origin station (number or name): 1
-> Origin selected: New Delhi
Select Destination station (number or name): 2
-> Destination selected: Mumbai

Available Train Types:
  1. Superfast       | Speed: 120 km/h | High-speed service (120 km/h)
  2. Express         | Speed: 110 km/h | Standard express service (110 km/h)
  3. Fast Passenger  | Speed:  90 km/h | Regular passenger service (90 km/h)

Select Train Type (1-3): 1
-> Train selected: Superfast

Available Travel Classes:
  1. Sleeper      | Multiplier: 1.0x | Free Baggage: 20.0 kg | Standard non-AC sleeper coach
  2. AC 3-Tier    | Multiplier: 1.5x | Free Baggage: 30.0 kg | Air-conditioned 3-tier sleeper
  3. AC 2-Tier    | Multiplier: 2.0x | Free Baggage: 40.0 kg | Air-conditioned 2-tier sleeper

Select Travel Class (1-3): 2
-> Class selected: AC 3-Tier

[Route Info] Distance: 1460 km | Estimated Travel Time: 12 hrs 10 mins
Enter number of passengers (1-6): 2

--- Passenger #1 Details ---
  Full Name: Rajesh Sharma
  Age: 65
  Baggage Weight (in kg, e.g. 18.5): 35

--- Passenger #2 Details ---
  Full Name: Priya Sharma
  Age: 30
  Baggage Weight (in kg, e.g. 18.5): 25

====================================================================
                      PASSENGER FARE BREAKDOWN
====================================================================

Passenger #1: Rajesh Sharma (Age: 65, Senior Citizen (>60))
  - Base Fare:                            INR   100.00
  - Distance Charge (1460 km):             INR   956.00
  - Step 1 (Cumulative Slab Fare):        INR  1056.00
  - Step 2 (Senior Discount 40%):        -INR   422.40 -> INR   633.60
  - Step 3 (Train Premium 1.50x):             INR   950.40
  - Step 4 (Class Multiplier 1.5x):          INR  1425.60
  - Step 5 (Baggage 35 kg, +5.0 kg):      +INR    75.00 -> INR  1500.60
  - Step 6 (Train Surcharge):            +INR   100.00
  ---------------------------------------------------------
  Final Individual Fare:                  INR  1600.60

Passenger #2: Priya Sharma (Age: 30, General (<=60))
  - Base Fare:                            INR   100.00
  - Distance Charge (1460 km):             INR   956.00
  - Step 1 (Cumulative Slab Fare):        INR  1056.00
  - Step 2 (Senior Discount):             Not applicable (Age 30 <= 60) -> INR  1056.00
  - Step 3 (Train Premium 1.50x):             INR  1584.00
  - Step 4 (Class Multiplier 1.5x):          INR  2376.00
  - Step 5 (Baggage 25 kg <= 30.0 kg):  +INR     0.00 -> INR  2376.00
  - Step 6 (Train Surcharge):            +INR   100.00
  ---------------------------------------------------------
  Final Individual Fare:                  INR  2476.00

--------------------------------------------------------------------
Booking Subtotal (2 passenger(s)):             INR  4076.60
--------------------------------------------------------------------

Promotional Offers Available:
  - ADG20     : 20% discount on entire booking subtotal
  - WINTER500 : Flat INR 500 off on booking subtotal
Enter promo code (or press Enter to skip): ADG20
  -> 20% discount applied.

====================================================================
                      OFFICIAL BOOKING RECEIPT
====================================================================
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
====================================================================
Thank you for choosing CLIPY Railway System!
```

---

## Limitations

- CLIPY is an educational demonstration CLI application and does not connect to Indian Railways (IRCTC) or external payment gateways.
- Booking references are generated locally for simulation purposes and do not represent active railway PNRs.
- Timetables, seat availability, coach/berth allocations, and real-time train tracking are beyond the defined scope of this simulation.
