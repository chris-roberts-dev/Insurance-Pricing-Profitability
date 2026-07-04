from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta

import factory
from faker import Faker

fake = Faker("en_US")

Faker.seed(42)
random.seed(42)

AS_OF_DATE = date(2026, 6, 30)


STATE_CONFIG = {
    "MO": {
        "base_rate": 1080,
        "markets": {"STL": 5, "KC": 3, "Rural": 2},
        "zips": {
            "STL": ["63101", "63110", "63122", "63139", "63146"],
            "KC": ["64105", "64111", "64118", "64131"],
            "Rural": ["65301", "65401", "64601"],
        },
    },
    "TN": {
        "base_rate": 980,
        "markets": {"Nashville": 5, "Knoxville": 2, "Rural": 3},
        "zips": {
            "Nashville": ["37203", "37206", "37209", "37211"],
            "Knoxville": ["37902", "37919", "37922"],
            "Rural": ["38501", "37110", "37055"],
        },
    },
    "IL": {
        "base_rate": 1225,
        "markets": {"Chicago": 6, "Metro East": 2, "Rural": 2},
        "zips": {
            "Chicago": ["60601", "60614", "60622", "60657"],
            "Metro East": ["62201", "62220", "62025"],
            "Rural": ["62521", "62901", "61820"],
        },
    },
    "TX": {
        "base_rate": 1350,
        "markets": {"Dallas": 4, "Houston": 4, "Austin": 2},
        "zips": {
            "Dallas": ["75201", "75206", "75230", "75001"],
            "Houston": ["77002", "77007", "77024", "77056"],
            "Austin": ["78701", "78704", "78745"],
        },
    },
    "GA": {
        "base_rate": 1180,
        "markets": {"Atlanta": 6, "Savannah": 2, "Rural": 2},
        "zips": {
            "Atlanta": ["30303", "30309", "30318", "30339"],
            "Savannah": ["31401", "31405", "31419"],
            "Rural": ["31021", "31701", "30501"],
        },
    },
}


VEHICLE_MAKES = {
    "Toyota": 18,
    "Honda": 16,
    "Ford": 14,
    "Chevrolet": 13,
    "Nissan": 10,
    "Hyundai": 8,
    "Kia": 8,
    "Jeep": 6,
    "Subaru": 5,
    "BMW": 2,
}


def weighted_choice(weight_map: dict[str, float]) -> str:
    values = list(weight_map.keys())
    weights = list(weight_map.values())
    return random.choices(values, weights=weights, k=1)[0]


def random_yes_no(probability_yes: float) -> str:
    return "Y" if random.random() < probability_yes else "N"


def fake_vin() -> str:
    vin_chars = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
    return "".join(random.choices(vin_chars, k=17))


def random_effective_date() -> date:
    return fake.date_between_dates(
        date_start=date(2024, 1, 1),
        date_end=date(2026, 12, 31),
    )


def calculate_underwriting_score(policy: "PolicyRecord") -> int:
    score = 700

    if policy.driver_age < 21:
        score -= 110
    elif policy.driver_age < 25:
        score -= 70
    elif policy.driver_age >= 55:
        score += 25

    if policy.prior_lapse_ind == "Y":
        score -= 90

    if policy.prior_bi_limits in {"25/50", "< 50/100"}:
        score -= 55
    elif policy.prior_bi_limits in {"100/300", "250/500"}:
        score += 30

    if policy.prior_tenure_months < 6:
        score -= 50
    elif policy.prior_tenure_months >= 36:
        score += 35

    if policy.cbr_group == "Poor":
        score -= 100
    elif policy.cbr_group == "I/N":
        score -= 45
    elif policy.cbr_group == "Excellent":
        score += 70

    if policy.homeowner_ind == "Y":
        score += 20

    return max(250, min(950, score + random.randint(-25, 25)))


def calculate_written_premium(policy: "PolicyRecord") -> float:
    base = STATE_CONFIG[policy.state]["base_rate"]

    age_factor = (
        2.20
        if policy.driver_age < 21
        else (
            1.65
            if policy.driver_age < 25
            else (
                1.15
                if policy.driver_age < 35
                else 0.95 if policy.driver_age < 60 else 1.05
            )
        )
    )

    cbr_factor = {
        "Excellent": 0.82,
        "Good": 0.95,
        "Average": 1.05,
        "I/N": 1.18,
        "Poor": 1.35,
    }[policy.cbr_group]

    prior_bi_factor = {
        "25/50": 1.25,
        "< 50/100": 1.14,
        "50/100": 1.10,
        "100/300": 1.00,
        "250/500": 0.90,
    }[policy.prior_bi_limits]

    current_bi_factor = {
        "25/50": 0.85,
        "50/100": 1.00,
        "100/300": 1.18,
        "250/500": 1.35,
        "500 CSL": 1.50,
    }[policy.bi_limits]

    vehicle_age_factor = (
        1.12
        if policy.vehicle_age <= 2
        else (
            1.04
            if policy.vehicle_age <= 5
            else 0.96 if policy.vehicle_age <= 10 else 0.88
        )
    )

    use_factor = {
        "Pleasure": 0.94,
        "Commute": 1.00,
        "Business": 1.18,
    }[policy.vehicle_use]

    mileage_factor = (
        0.88
        if policy.annual_mileage < 6000
        else 1.00 if policy.annual_mileage < 14000 else 1.13
    )

    lapse_factor = 1.25 if policy.prior_lapse_ind == "Y" else 1.00
    homeowner_factor = 0.95 if policy.homeowner_ind == "Y" else 1.00
    multi_vehicle_factor = 1 + ((policy.household_vehicle_count - 1) * 0.62)
    driver_count_factor = 1 + ((policy.household_driver_count - 1) * 0.18)

    physical_damage_factor = 1.28 if policy.has_physical_damage == "Y" else 0.72

    deductible_factor = 1.00
    if policy.has_physical_damage == "Y":
        if policy.coll_deductible == 250:
            deductible_factor = 1.10
        elif policy.coll_deductible == 500:
            deductible_factor = 1.00
        elif policy.coll_deductible == 1000:
            deductible_factor = 0.92

    optional_coverage_factor = 1.00
    if policy.rental_ind == "Y":
        optional_coverage_factor += 0.04
    if policy.roadside_ind == "Y":
        optional_coverage_factor += 0.02

    premium = (
        base
        * age_factor
        * cbr_factor
        * prior_bi_factor
        * current_bi_factor
        * vehicle_age_factor
        * use_factor
        * mileage_factor
        * lapse_factor
        * homeowner_factor
        * multi_vehicle_factor
        * driver_count_factor
        * physical_damage_factor
        * deductible_factor
        * optional_coverage_factor
    )

    premium *= 1 + policy.rate_change_pct

    random_noise = random.gauss(mu=1.0, sigma=0.06)
    premium *= random_noise

    return round(max(275, premium), 2)


def calculate_earned_premium(policy: "PolicyRecord") -> float:
    if AS_OF_DATE < policy.effective_date:
        return 0.00

    policy_end_date = policy.cancel_date or policy.expiration_date
    earning_end_date = min(AS_OF_DATE, policy_end_date)

    earned_days = max(0, (earning_end_date - policy.effective_date).days)
    total_days = max(1, (policy_end_date - policy.effective_date).days)

    earned_ratio = min(1.0, earned_days / total_days)

    return round(policy.total_written_premium * earned_ratio, 2)


def calculate_expected_loss_cost(policy: "PolicyRecord") -> float:
    expected_loss_ratio = 0.62

    if policy.cbr_group == "Poor":
        expected_loss_ratio += 0.18
    elif policy.cbr_group == "I/N":
        expected_loss_ratio += 0.08
    elif policy.cbr_group == "Excellent":
        expected_loss_ratio -= 0.08

    if policy.prior_lapse_ind == "Y":
        expected_loss_ratio += 0.10

    if policy.driver_age < 25:
        expected_loss_ratio += 0.12

    if policy.annual_mileage >= 14000:
        expected_loss_ratio += 0.05

    if policy.preferred_risk_ind == "Y":
        expected_loss_ratio -= 0.07

    expected_loss_ratio = max(0.35, min(1.20, expected_loss_ratio))

    return round(policy.total_written_premium * expected_loss_ratio, 2)


def fake_us_phone_number() -> str:
    area_code = random.choice(
        [
            "314",
            "636",
            "816",  # MO
            "615",
            "629",
            "931",  # TN
            "312",
            "618",
            "773",  # IL
            "214",
            "469",
            "512",
            "713",
            "972",  # TX
            "404",
            "470",
            "678",
            "770",  # GA
        ]
    )

    exchange = random.randint(200, 999)
    line_number = random.randint(1000, 9999)

    return f"({area_code}) {exchange}-{line_number}"


@dataclass(slots=True)
class PolicyRecord:
    policy_id: str
    term_id: str
    account_id: str
    named_insured_id: str

    first_name: str
    last_name: str
    email: str
    phone_number: str
    street_address: str

    company: str
    product: str
    policy_status: str
    new_renewal_ind: str
    term_number: int

    effective_date: date
    expiration_date: date
    cancel_date: date | None

    state: str
    market: str
    garaging_zip: str
    urbanicity: str
    channel: str
    agency_id: str

    payment_plan: str
    paperless_ind: str
    autopay_ind: str

    driver_age: int
    driver_gender: str
    marital_status: str
    homeowner_ind: str
    household_driver_count: int
    household_vehicle_count: int

    prior_carrier_tier: str
    prior_bi_limits: str
    prior_lapse_ind: str
    prior_tenure_months: int
    cbr_group: str
    underwriting_score: int
    preferred_risk_ind: str

    vehicle_year: int
    vehicle_make: str
    vehicle_body_style: str
    vehicle_symbol: int
    vehicle_age: int
    vehicle_use: str
    annual_mileage: int
    anti_theft_ind: str
    vin: str

    bi_limits: str
    pd_limit: int
    has_physical_damage: str
    coll_deductible: int | None
    comp_deductible: int | None
    rental_ind: str
    roadside_ind: str

    rate_change_pct: float
    total_written_premium: float
    total_earned_premium: float
    expected_loss_cost: float
    target_loss_ratio: float
    expected_profit: float


class PolicyRecordFactory(factory.Factory):
    class Meta:
        model = PolicyRecord

    policy_id = factory.Sequence(lambda n: f"PA{n + 1_000_000}")
    term_id = factory.Sequence(lambda n: f"TERM{n + 1_000_000}")
    account_id = factory.Sequence(lambda n: f"ACCT{n + 500_000}")
    named_insured_id = factory.Sequence(lambda n: f"NI{n + 700_000}")

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(
        lambda o: f"{o.first_name}.{o.last_name}{random.randint(1, 9999)}@example.com".lower()
    )
    phone_number = factory.LazyFunction(fake_us_phone_number)
    street_address = factory.Faker("street_address")

    company = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "Heritage Mutual": 45,
                "Summit Casualty": 35,
                "Pioneer Indemnity": 20,
            }
        )
    )
    product = "Personal Auto"

    policy_status = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "Active": 74,
                "Expired": 12,
                "Cancelled": 10,
                "Non-Renewed": 4,
            }
        )
    )

    term_number = factory.LazyFunction(
        lambda: int(
            weighted_choice(
                {
                    "1": 28,
                    "2": 20,
                    "3": 16,
                    "4": 12,
                    "5": 9,
                    "6": 7,
                    "7": 5,
                    "8": 3,
                }
            )
        )
    )

    new_renewal_ind = factory.LazyAttribute(
        lambda o: "New" if o.term_number == 1 else "Renewal"
    )

    effective_date = factory.LazyFunction(random_effective_date)
    expiration_date = factory.LazyAttribute(
        lambda o: o.effective_date + timedelta(days=365)
    )
    cancel_date = factory.LazyAttribute(
        lambda o: (
            o.effective_date + timedelta(days=random.randint(30, 300))
            if o.policy_status in {"Cancelled", "Non-Renewed"}
            else None
        )
    )

    state = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "MO": 28,
                "TN": 24,
                "IL": 18,
                "TX": 20,
                "GA": 10,
            }
        )
    )
    market = factory.LazyAttribute(
        lambda o: weighted_choice(STATE_CONFIG[o.state]["markets"])
    )
    garaging_zip = factory.LazyAttribute(
        lambda o: random.choice(STATE_CONFIG[o.state]["zips"][o.market])
    )
    urbanicity = factory.LazyAttribute(
        lambda o: (
            "Urban"
            if o.market
            in {"STL", "KC", "Chicago", "Dallas", "Houston", "Atlanta", "Nashville"}
            else "Rural"
        )
    )

    channel = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "Agent": 62,
                "Direct": 22,
                "Call Center": 14,
            }
        )
    )
    agency_id = factory.LazyAttribute(
        lambda o: (
            f"AGY{random.randint(1000, 9999)}"
            if o.channel == "Independent Agent"
            else "DIRECT"
        )
    )

    payment_plan = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "Paid in Full": 22,
                "Monthly EFT": 44,
                "Monthly Direct Bill": 24,
                "Quarterly": 10,
            }
        )
    )
    paperless_ind = factory.LazyFunction(lambda: random_yes_no(0.58))
    autopay_ind = factory.LazyFunction(lambda: random_yes_no(0.52))

    driver_age = factory.LazyFunction(
        lambda: int(
            random.choices(
                population=[19, 22, 28, 36, 45, 55, 68],
                weights=[6, 10, 20, 24, 20, 14, 6],
                k=1,
            )[0]
            + random.randint(-2, 2)
        )
    )
    driver_gender = factory.LazyFunction(lambda: weighted_choice({"F": 50, "M": 50}))
    marital_status = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "Single": 34,
                "Married": 52,
                "Divorced": 10,
                "Widowed": 4,
            }
        )
    )
    homeowner_ind = factory.LazyFunction(lambda: random_yes_no(0.58))
    household_driver_count = factory.LazyFunction(
        lambda: int(weighted_choice({"1": 34, "2": 48, "3": 13, "4": 5}))
    )
    household_vehicle_count = factory.LazyFunction(
        lambda: int(weighted_choice({"1": 30, "2": 50, "3": 15, "4": 5}))
    )

    prior_carrier_tier = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "Preferred": 34,
                "Standard": 48,
                "Non-Standard": 13,
                "No Prior": 5,
            }
        )
    )
    prior_bi_limits = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "25/50": 15,
                "< 50/100": 16,
                "50/100": 30,
                "100/300": 28,
                "250/500": 11,
            }
        )
    )
    prior_tenure_months = factory.LazyFunction(
        lambda: random.choice([0, 3, 6, 9, 12, 18, 24, 36, 48, 60, 84, 120])
    )
    prior_lapse_ind = factory.LazyAttribute(
        lambda o: random_yes_no(0.18 if o.prior_tenure_months < 6 else 0.06)
    )
    cbr_group = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "Excellent": 18,
                "Good": 32,
                "Average": 30,
                "I/N": 8,
                "Poor": 12,
            }
        )
    )

    underwriting_score = factory.LazyAttribute(calculate_underwriting_score)
    preferred_risk_ind = factory.LazyAttribute(
        lambda o: (
            "Y"
            if o.underwriting_score >= 690
            and o.prior_lapse_ind == "N"
            and o.prior_bi_limits in {"100/300", "250/500"}
            else "N"
        )
    )

    vehicle_year = factory.LazyFunction(lambda: random.randint(2007, 2026))
    vehicle_make = factory.LazyFunction(lambda: weighted_choice(VEHICLE_MAKES))
    vehicle_body_style = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "Sedan": 30,
                "SUV": 38,
                "Truck": 20,
                "Van": 5,
                "Coupe": 4,
                "Wagon": 3,
            }
        )
    )
    vehicle_symbol = factory.LazyFunction(lambda: random.randint(3, 27))
    vehicle_age = factory.LazyAttribute(lambda o: 2026 - o.vehicle_year)
    vehicle_use = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "Pleasure": 38,
                "Commute": 56,
                "Business": 6,
            }
        )
    )
    annual_mileage = factory.LazyFunction(
        lambda: int(
            random.choices(
                population=[4500, 7500, 10000, 12000, 15000, 18000, 22000],
                weights=[8, 14, 22, 28, 16, 8, 4],
                k=1,
            )[0]
            + random.randint(-750, 750)
        )
    )
    anti_theft_ind = factory.LazyFunction(lambda: random_yes_no(0.68))
    vin = factory.LazyFunction(fake_vin)

    bi_limits = factory.LazyFunction(
        lambda: weighted_choice(
            {
                "25/50": 10,
                "50/100": 26,
                "100/300": 42,
                "250/500": 18,
                "500 CSL": 4,
            }
        )
    )
    pd_limit = factory.LazyFunction(
        lambda: int(
            weighted_choice(
                {
                    "25000": 16,
                    "50000": 36,
                    "100000": 34,
                    "250000": 14,
                }
            )
        )
    )

    has_physical_damage = factory.LazyAttribute(
        lambda o: (
            "Y"
            if (o.vehicle_age <= 12 and random.random() < 0.82)
            or random.random() < 0.22
            else "N"
        )
    )
    coll_deductible = factory.LazyAttribute(
        lambda o: (
            random.choice([250, 500, 1000]) if o.has_physical_damage == "Y" else None
        )
    )
    comp_deductible = factory.LazyAttribute(
        lambda o: (
            random.choice([250, 500, 1000]) if o.has_physical_damage == "Y" else None
        )
    )
    rental_ind = factory.LazyFunction(lambda: random_yes_no(0.42))
    roadside_ind = factory.LazyFunction(lambda: random_yes_no(0.36))

    rate_change_pct = factory.LazyFunction(
        lambda: round(random.uniform(-0.08, 0.22), 4)
    )
    total_written_premium = factory.LazyAttribute(calculate_written_premium)
    total_earned_premium = factory.LazyAttribute(calculate_earned_premium)
    expected_loss_cost = factory.LazyAttribute(calculate_expected_loss_cost)
    target_loss_ratio = 0.62
    expected_profit = factory.LazyAttribute(
        lambda o: round(o.total_earned_premium - o.expected_loss_cost, 2)
    )
