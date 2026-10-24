"""test_booking_system.py - Comprehensive automated test suite for CLIPY.

Tests cover:
- Route lookups, distances, bidirectionality, invalid cities, identical source/dest.
- Six-step individual fare calculations (slab fare, senior citizen discount,
  train premium, class multiplier, excess baggage fees, flat train surcharges).
- Promotional codes (ADG20, WINTER500, edge cases with subtotal < 500, whitespace/case).
- Multi-passenger integration bookings and bill reconciliation.
- Input validation functions.
"""

from decimal import Decimal
import unittest

from routes import (
    CITIES,
    calculate_travel_time,
    format_travel_time,
    get_available_destinations,
    get_cities,
    get_class_info,
    get_distance,
    get_train_info,
    normalize_city_name,
)
from fare import (
    apply_class_multiplier,
    apply_promotional_discount,
    apply_senior_citizen_discount,
    apply_train_premium,
    apply_train_surcharge,
    calculate_complete_passenger_fare,
    calculate_excess_baggage_charges,
    calculate_final_payable,
    calculate_slab_fare,
)
from booking import Booking, Passenger
from validation import (
    validate_baggage_weight,
    validate_city_choice,
    validate_passenger_age,
    validate_passenger_count,
    validate_passenger_name,
    validate_route_pair,
)


class TestRoutes(unittest.TestCase):
    """Test static route data, bidirectionality, and train/class specifications."""

    def test_all_ten_routes_distances(self):
        """Verify the exact specified distances for all ten bidirectional routes."""
        expected_routes = {
            ("New Delhi", "Mumbai"): 1460,
            ("New Delhi", "Kolkata"): 1525,
            ("New Delhi", "Chennai"): 2200,
            ("New Delhi", "Hyderabad"): 1670,
            ("Mumbai", "Kolkata"): 1970,
            ("Mumbai", "Chennai"): 1300,
            ("Mumbai", "Hyderabad"): 711,
            ("Kolkata", "Chennai"): 1200,
            ("Kolkata", "Hyderabad"): 1600,
            ("Chennai", "Hyderabad"): 633,
        }

        for (src, dst), expected_dist in expected_routes.items():
            dist_forward = get_distance(src, dst)
            dist_reverse = get_distance(dst, src)
            self.assertEqual(
                dist_forward,
                expected_dist,
                f"Forward distance mismatch for {src} -> {dst}",
            )
            self.assertEqual(
                dist_reverse,
                expected_dist,
                f"Reverse distance mismatch for {dst} -> {src}",
            )

    def test_identical_source_and_destination_rejected(self):
        """Verify selecting the same city for source and destination raises ValueError."""
        with self.assertRaises(ValueError):
            get_distance("New Delhi", "New Delhi")

        with self.assertRaises(ValueError):
            get_distance("Mumbai", "mumbai")

    def test_invalid_city_rejected(self):
        """Verify invalid or unserviced cities raise ValueError."""
        with self.assertRaises(ValueError):
            get_distance("New Delhi", "Bangalore")

        with self.assertRaises(ValueError):
            get_distance("UnknownCity", "Mumbai")

    def test_city_normalization(self):
        """Verify city normalization strips whitespace and is case-insensitive."""
        self.assertEqual(normalize_city_name("  new delhi  "), "New Delhi")
        self.assertEqual(normalize_city_name("mUmBaI"), "Mumbai")
        self.assertIsNone(normalize_city_name("Tokyo"))

    def test_get_available_destinations(self):
        """Verify destinations reachable from New Delhi."""
        dests = get_available_destinations("New Delhi")
        self.assertEqual(len(dests), 4)
        self.assertNotIn("New Delhi", dests)
        self.assertIn("Mumbai", dests)

    def test_travel_time_calculation(self):
        """Verify estimated travel time calculation and formatting."""
        # 1460 km at 120 km/h: 1460 / 120 = 12.1666... hours -> 12 hrs 10 mins
        hours, mins = calculate_travel_time(1460, 120)
        self.assertEqual(hours, 12)
        self.assertEqual(mins, 10)
        self.assertEqual(format_travel_time(hours, mins), "12 hrs 10 mins")

        # 633 km at 110 km/h: 633 / 110 = 5.7545... -> 5 hrs 45 mins
        hours, mins = calculate_travel_time(633, 110)
        self.assertEqual(hours, 5)
        self.assertEqual(mins, 45)


class TestSlabFare(unittest.TestCase):
    """Test Step 1: Cumulative distance-based slab fare calculation."""

    def test_boundary_1_km(self):
        """Distance 1 km: Base 100 + 1 * 1.00 = 101.00."""
        self.assertEqual(calculate_slab_fare(1), Decimal("101.00"))

    def test_boundary_100_km(self):
        """Distance exactly 100 km: Base 100 + 100 * 1.00 = 200.00."""
        self.assertEqual(calculate_slab_fare(100), Decimal("200.00"))

    def test_boundary_300_km(self):
        """Distance exactly 300 km: Base 100 + 100*1.00 + 200*0.80 = 360.00."""
        self.assertEqual(calculate_slab_fare(300), Decimal("360.00"))

    def test_boundary_301_km(self):
        """Distance 301 km: Base 100 + 100*1.00 + 200*0.80 + 1*0.60 = 360.60."""
        self.assertEqual(calculate_slab_fare(301), Decimal("360.60"))

    def test_long_distance_routes(self):
        """Test realistic long-distance journeys."""
        # 1460 km: 100 + 100 + 160 + (1460 - 300) * 0.60 = 360 + 696 = 1056.00
        self.assertEqual(calculate_slab_fare(1460), Decimal("1056.00"))

        # 2200 km: 100 + 100 + 160 + (2200 - 300) * 0.60 = 360 + 1140 = 1500.00
        self.assertEqual(calculate_slab_fare(2200), Decimal("1500.00"))

    def test_negative_distance_rejected(self):
        """Verify negative distances raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_slab_fare(-10)


class TestSeniorCitizenDiscount(unittest.TestCase):
    """Test Step 2: Senior citizen discount (strictly age > 60)."""

    def test_age_59_no_discount(self):
        """Age 59 is <= 60: no discount."""
        fare = Decimal("1000.00")
        self.assertEqual(apply_senior_citizen_discount(fare, 59), Decimal("1000.00"))

    def test_age_60_exactly_no_discount(self):
        """Age 60 is NOT strictly greater than 60: must NOT receive discount."""
        fare = Decimal("1000.00")
        self.assertEqual(apply_senior_citizen_discount(fare, 60), Decimal("1000.00"))

    def test_age_61_receives_40_percent_discount(self):
        """Age 61 is strictly > 60: receives 40% discount (fare * 0.60)."""
        fare = Decimal("1000.00")
        self.assertEqual(apply_senior_citizen_discount(fare, 61), Decimal("600.00"))

    def test_age_80_receives_discount(self):
        """Age 80: receives 40% discount."""
        fare = Decimal("1056.00")
        # 1056.00 * 0.60 = 633.60
        self.assertEqual(apply_senior_citizen_discount(fare, 80), Decimal("633.60"))


class TestTrainPremium(unittest.TestCase):
    """Test Step 3: Train type multipliers."""

    def test_fast_passenger_multiplier(self):
        """Fast Passenger: 1.0x."""
        fare = Decimal("500.00")
        self.assertEqual(apply_train_premium(fare, Decimal("1.00")), Decimal("500.00"))

    def test_express_multiplier(self):
        """Express: 1.25x."""
        fare = Decimal("500.00")
        self.assertEqual(apply_train_premium(fare, Decimal("1.25")), Decimal("625.00"))

    def test_superfast_multiplier(self):
        """Superfast: 1.50x."""
        fare = Decimal("500.00")
        self.assertEqual(apply_train_premium(fare, Decimal("1.50")), Decimal("750.00"))


class TestClassPremium(unittest.TestCase):
    """Test Step 4: Travel class multipliers."""

    def test_sleeper_multiplier(self):
        """Sleeper: 1.0x."""
        fare = Decimal("750.00")
        self.assertEqual(apply_class_multiplier(fare, Decimal("1.0")), Decimal("750.00"))

    def test_ac_3_tier_multiplier(self):
        """AC 3-Tier: 1.5x."""
        fare = Decimal("750.00")
        self.assertEqual(apply_class_multiplier(fare, Decimal("1.5")), Decimal("1125.00"))

    def test_ac_2_tier_multiplier(self):
        """AC 2-Tier: 2.0x."""
        fare = Decimal("750.00")
        self.assertEqual(apply_class_multiplier(fare, Decimal("2.0")), Decimal("1500.00"))


class TestExcessBaggageFee(unittest.TestCase):
    """Test Step 5: Baggage allowances and excess fees."""

    def test_below_allowance_no_fee(self):
        """15 kg with 20 kg allowance -> INR 0.00."""
        fee = calculate_excess_baggage_charges(15, 20)
        self.assertEqual(fee, Decimal("0.00"))

    def test_exact_allowance_no_fee(self):
        """Exactly 20 kg in Sleeper (20 kg allowance) -> INR 0.00."""
        fee = calculate_excess_baggage_charges(20, 20)
        self.assertEqual(fee, Decimal("0.00"))

    def test_above_allowance_fee(self):
        """23 kg in Sleeper (20 kg allowance): 3 kg excess * INR 15 = INR 45.00."""
        fee = calculate_excess_baggage_charges(23, 20)
        self.assertEqual(fee, Decimal("45.00"))

    def test_decimal_baggage_weight(self):
        """22.5 kg in Sleeper (20 kg allowance): 2.5 kg * 15 = INR 37.50."""
        fee = calculate_excess_baggage_charges(Decimal("22.5"), Decimal("20.0"))
        self.assertEqual(fee, Decimal("37.50"))

    def test_ac_tier_allowances(self):
        """AC 3-Tier (30 kg) and AC 2-Tier (40 kg) allowances."""
        # 35 kg in AC 3-Tier (30 kg allowance) -> 5 * 15 = 75.00
        self.assertEqual(
            calculate_excess_baggage_charges(35, 30), Decimal("75.00")
        )
        # 42 kg in AC 2-Tier (40 kg allowance) -> 2 * 15 = 30.00
        self.assertEqual(
            calculate_excess_baggage_charges(42, 40), Decimal("30.00")
        )

    def test_zero_or_negative_baggage_rejected(self):
        """Zero or negative weight must raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_excess_baggage_charges(0, 20)
        with self.assertRaises(ValueError):
            calculate_excess_baggage_charges(-5, 20)


class TestTrainSurcharge(unittest.TestCase):
    """Test Step 6: Flat per-passenger train surcharges."""

    def test_fast_passenger_surcharge(self):
        """Fast Passenger surcharge: INR 0."""
        self.assertEqual(apply_train_surcharge(Decimal("500.00"), 0), Decimal("500.00"))

    def test_express_surcharge(self):
        """Express surcharge: INR 50."""
        self.assertEqual(apply_train_surcharge(Decimal("500.00"), 50), Decimal("550.00"))

    def test_superfast_surcharge(self):
        """Superfast surcharge: INR 100."""
        self.assertEqual(apply_train_surcharge(Decimal("500.00"), 100), Decimal("600.00"))


class TestPromoCodes(unittest.TestCase):
    """Test promotional discounts: ADG20, WINTER500, edge cases, and invalid inputs."""

    def test_adg20_discount(self):
        """ADG20 deducts 20% from subtotal."""
        subtotal = Decimal("2000.00")
        disc, final_p, code, _ = apply_promotional_discount(subtotal, "ADG20")
        self.assertEqual(disc, Decimal("400.00"))
        self.assertEqual(final_p, Decimal("1600.00"))
        self.assertEqual(code, "ADG20")

    def test_winter500_discount(self):
        """WINTER500 deducts flat INR 500."""
        subtotal = Decimal("2000.00")
        disc, final_p, code, _ = apply_promotional_discount(subtotal, "WINTER500")
        self.assertEqual(disc, Decimal("500.00"))
        self.assertEqual(final_p, Decimal("1500.00"))
        self.assertEqual(code, "WINTER500")

    def test_winter500_subtotal_below_500_never_negative(self):
        """WINTER500 with subtotal < 500 must floor final total at 0, not negative."""
        subtotal = Decimal("350.00")
        disc, final_p, code, _ = apply_promotional_discount(subtotal, "WINTER500")
        self.assertEqual(disc, Decimal("350.00"))
        self.assertEqual(final_p, Decimal("0.00"))
        self.assertGreaterEqual(final_p, Decimal("0.00"))

    def test_empty_or_none_code(self):
        """Empty or None promo code results in 0 discount."""
        subtotal = Decimal("1500.00")
        disc, final_p, code, _ = apply_promotional_discount(subtotal, "")
        self.assertEqual(disc, Decimal("0.00"))
        self.assertEqual(final_p, subtotal)

        disc, final_p, code, _ = apply_promotional_discount(subtotal, None)
        self.assertEqual(disc, Decimal("0.00"))
        self.assertEqual(final_p, subtotal)

    def test_invalid_promo_code(self):
        """Invalid non-empty promo code gives 0 discount with informative message."""
        subtotal = Decimal("1500.00")
        disc, final_p, code, msg = apply_promotional_discount(subtotal, "DISCOUNT99")
        self.assertEqual(disc, Decimal("0.00"))
        self.assertEqual(final_p, subtotal)
        self.assertIn("Invalid", msg)

    def test_promo_normalization(self):
        """Promo codes should be case-insensitive and ignore whitespace."""
        subtotal = Decimal("1000.00")
        disc, final_p, code, _ = apply_promotional_discount(subtotal, "  adg20 \t")
        self.assertEqual(disc, Decimal("200.00"))
        self.assertEqual(final_p, Decimal("800.00"))
        self.assertEqual(code, "ADG20")

        disc, final_p, code, _ = apply_promotional_discount(subtotal, "winter500 ")
        self.assertEqual(disc, Decimal("500.00"))
        self.assertEqual(final_p, Decimal("500.00"))
        self.assertEqual(code, "WINTER500")


class TestCompletePassengerFare(unittest.TestCase):
    """Test full 6-step calculation for individual passenger."""

    def test_senior_ac3_superfast_with_excess_baggage(self):
        """Calculate complete fare for a senior passenger.

        Route: 1460 km
        Step 1: 100 + 100*1 + 200*0.8 + 1160*0.6 = 1056.00
        Step 2: Senior (age 65 > 60) -> 1056.00 * 0.60 = 633.60
        Step 3: Superfast (1.5x) -> 633.60 * 1.5 = 950.40
        Step 4: AC 3-Tier (1.5x) -> 950.40 * 1.5 = 1425.60
        Step 5: Baggage 35 kg (allowance 30 kg -> 5 kg * 15 = 75.00) -> 1425.60 + 75.00 = 1500.60
        Step 6: Superfast Surcharge -> 1500.60 + 100.00 = 1600.60
        """
        breakdown = calculate_complete_passenger_fare(
            distance=1460,
            age=65,
            train_multiplier=Decimal("1.50"),
            class_multiplier=Decimal("1.5"),
            baggage_weight=Decimal("35.0"),
            free_allowance=Decimal("30.0"),
            train_surcharge=Decimal("100.00"),
        )
        self.assertEqual(breakdown["step1_slab_fare"], Decimal("1056.00"))
        self.assertTrue(breakdown["is_senior"])
        self.assertEqual(breakdown["senior_discount_amount"], Decimal("422.40"))
        self.assertEqual(breakdown["step2_fare"], Decimal("633.60"))
        self.assertEqual(breakdown["step3_fare"], Decimal("950.40"))
        self.assertEqual(breakdown["step4_fare"], Decimal("1425.60"))
        self.assertEqual(breakdown["excess_baggage_weight"], Decimal("5.0"))
        self.assertEqual(breakdown["excess_baggage_fee"], Decimal("75.00"))
        self.assertEqual(breakdown["step5_fare"], Decimal("1500.60"))
        self.assertEqual(breakdown["train_surcharge"], Decimal("100.00"))
        self.assertEqual(breakdown["final_fare"], Decimal("1600.60"))

    def test_non_senior_ac3_superfast_no_excess_baggage(self):
        """Calculate complete fare for a non-senior passenger without excess baggage.

        Route: 1460 km
        Step 1: 1056.00
        Step 2: Non-senior (age 30 <= 60) -> 1056.00
        Step 3: Superfast (1.5x) -> 1056.00 * 1.5 = 1584.00
        Step 4: AC 3-Tier (1.5x) -> 1584.00 * 1.5 = 2376.00
        Step 5: Baggage 25 kg (allowance 30 kg -> 0 excess) -> 2376.00
        Step 6: Superfast Surcharge -> 2376.00 + 100.00 = 2476.00
        """
        breakdown = calculate_complete_passenger_fare(
            distance=1460,
            age=30,
            train_multiplier=Decimal("1.50"),
            class_multiplier=Decimal("1.5"),
            baggage_weight=Decimal("25.0"),
            free_allowance=Decimal("30.0"),
            train_surcharge=Decimal("100.00"),
        )
        self.assertEqual(breakdown["step1_slab_fare"], Decimal("1056.00"))
        self.assertFalse(breakdown["is_senior"])
        self.assertEqual(breakdown["senior_discount_amount"], Decimal("0.00"))
        self.assertEqual(breakdown["step2_fare"], Decimal("1056.00"))
        self.assertEqual(breakdown["step3_fare"], Decimal("1584.00"))
        self.assertEqual(breakdown["step4_fare"], Decimal("2376.00"))
        self.assertEqual(breakdown["excess_baggage_fee"], Decimal("0.00"))
        self.assertEqual(breakdown["step5_fare"], Decimal("2376.00"))
        self.assertEqual(breakdown["final_fare"], Decimal("2476.00"))


class TestIntegrationBooking(unittest.TestCase):
    """End-to-end integration tests for multi-passenger booking workflows."""

    def test_multi_passenger_booking_with_adg20(self):
        """Verify entire booking workflow with 2 passengers, differing ages and baggage."""
        booking = Booking(
            source="New Delhi",
            destination="Mumbai",
            train_type="Superfast",
            travel_class="AC 3-Tier",
        )

        p1 = booking.add_passenger("Rajesh Sharma", 65, Decimal("35.0"))
        p2 = booking.add_passenger("Priya Sharma", 30, Decimal("25.0"))

        subtotal = booking.calculate_all_fares()

        # Passenger 1 fare: 1600.60
        self.assertEqual(p1.fare_breakdown["final_fare"], Decimal("1600.60"))
        # Passenger 2 fare: 2476.00
        self.assertEqual(p2.fare_breakdown["final_fare"], Decimal("2476.00"))

        # Reconcile subtotal: 1600.60 + 2476.00 = 4076.60
        self.assertEqual(subtotal, Decimal("4076.60"))
        self.assertEqual(booking.subtotal, Decimal("4076.60"))

        # Apply ADG20: 20% of 4076.60 = 815.32
        disc, final_p, _ = booking.apply_promo("ADG20")
        self.assertEqual(disc, Decimal("815.32"))
        self.assertEqual(final_p, Decimal("3261.28"))
        self.assertEqual(booking.final_total, Decimal("3261.28"))

    def test_multi_passenger_booking_with_winter500(self):
        """Verify booking workflow with WINTER500 discount."""
        booking = Booking(
            source="Mumbai",
            destination="Hyderabad",
            train_type="Express",
            travel_class="Sleeper",
        )
        # Distance: 711 km
        # Base: 100, Dist: 100*1 + 200*0.8 + 411*0.6 = 100 + 160 + 246.60 = 506.60
        # Step 1: 606.60
        # Age 40: Step 2 = 606.60
        # Express (1.25): Step 3 = 606.60 * 1.25 = 758.25
        # Sleeper (1.0): Step 4 = 758.25
        # Baggage 18 kg <= 20 kg: Step 5 = 758.25
        # Surcharge Express (50): Step 6 = 808.25

        p = booking.add_passenger("Arun Kumar", 40, Decimal("18.0"))
        subtotal = booking.calculate_all_fares()
        self.assertEqual(subtotal, Decimal("808.25"))

        disc, final_p, _ = booking.apply_promo("WINTER500")
        self.assertEqual(disc, Decimal("500.00"))
        self.assertEqual(final_p, Decimal("308.25"))


class TestValidationHelpers(unittest.TestCase):
    """Test pure input validation helper functions."""

    def test_passenger_name_validation(self):
        """Check valid and invalid names."""
        self.assertEqual(validate_passenger_name(" Amit Verma "), "Amit Verma")
        with self.assertRaises(ValueError):
            validate_passenger_name("")
        with self.assertRaises(ValueError):
            validate_passenger_name("   ")
        with self.assertRaises(ValueError):
            validate_passenger_name("12345")

    def test_passenger_age_validation(self):
        """Check valid and invalid ages."""
        self.assertEqual(validate_passenger_age("25"), 25)
        self.assertEqual(validate_passenger_age(" 60 "), 60)
        with self.assertRaises(ValueError):
            validate_passenger_age("abc")
        with self.assertRaises(ValueError):
            validate_passenger_age("0")
        with self.assertRaises(ValueError):
            validate_passenger_age("-5")
        with self.assertRaises(ValueError):
            validate_passenger_age("150")

    def test_baggage_weight_validation(self):
        """Check valid positive baggage weights and rejection of <= 0."""
        self.assertEqual(validate_baggage_weight("15.5"), Decimal("15.5"))
        self.assertEqual(validate_baggage_weight("20"), Decimal("20"))
        with self.assertRaises(ValueError):
            validate_baggage_weight("0")
        with self.assertRaises(ValueError):
            validate_baggage_weight("-2")
        with self.assertRaises(ValueError):
            validate_baggage_weight("heavy")
        with self.assertRaises(ValueError):
            validate_baggage_weight("250")  # exceeds 150 kg limit

    def test_passenger_count_validation(self):
        """Check valid range (1 to 6)."""
        self.assertEqual(validate_passenger_count("1"), 1)
        self.assertEqual(validate_passenger_count("6"), 6)
        with self.assertRaises(ValueError):
            validate_passenger_count("0")
        with self.assertRaises(ValueError):
            validate_passenger_count("7")
        with self.assertRaises(ValueError):
            validate_passenger_count("two")

    def test_city_choice_validation(self):
        """Check numeric index or name selection."""
        cities = ["New Delhi", "Mumbai", "Kolkata"]
        self.assertEqual(validate_city_choice("1", cities), "New Delhi")
        self.assertEqual(validate_city_choice("mumbai", cities), "Mumbai")
        with self.assertRaises(ValueError):
            validate_city_choice("4", cities)
        with self.assertRaises(ValueError):
            validate_city_choice("London", cities)

    def test_route_pair_validation(self):
        """Check source and destination validation."""
        dist = validate_route_pair("New Delhi", "Mumbai")
        self.assertEqual(dist, 1460)
        with self.assertRaises(ValueError):
            validate_route_pair("New Delhi", "New Delhi")


if __name__ == "__main__":
    unittest.main()
