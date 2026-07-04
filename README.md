# Insurance Pricing & Profitability Command Center

Synthetic auto insurance data pipeline for building portfolio analytics, pricing diagnostics, profitability views, and future insurance-domain datasets such as quotes, claims, rate changes, and policy-term snapshots.

This project currently focuses on generating a large synthetic **personal auto policy-term dataset**, writing it directly into **PostgreSQL**, and validating the loaded data with SQL queries.

The goal is to create a realistic analytics portfolio project that demonstrates:

- Synthetic data generation
- Insurance domain modeling
- PostgreSQL schema design
- Bulk data loading
- Reusable Python project structure
- Policy-level profitability analytics
- Pricing and segmentation foundations

---

## Current Project Status

The project currently supports:

1. Generating synthetic auto insurance policy-term records using `factory-boy` and `Faker`
2. Creating the PostgreSQL database/table structure from Python
3. Loading generated records directly into PostgreSQL using `psycopg`
4. Optionally exporting generated data to CSV
5. Running SQL validation queries against the loaded policy table

The current primary table is:

```text
synthetic.policy_terms
```

The primary dataset grain is:

```text
One row per auto insurance policy term
```

---

## Project Structure

```text
Insurance Pricing Profitability/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
│
├── data/
│   └── .gitkeep
│
├── sql/
│   ├── create_policy_terms.sql
│   └── validation_queries.sql
│
└── src/
    ├── __init__.py
    │
    ├── db/
    │   ├── __init__.py
    │   ├── bootstrap_postgres.py
    │   └── rebuild_policy_dataset.py
    │
    └── generators/
        ├── __init__.py
        ├── factories.py
        ├── generate_policies.py
        └── load_policies_to_postgres.py
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Data generation and pipeline orchestration |
| factory-boy | Factory pattern for synthetic policy records |
| Faker | Realistic fake customer/location/contact values |
| PostgreSQL | Analytics database |
| psycopg | Python-to-Postgres connection and bulk load |
| python-dotenv | Environment variable management |
| SQL | Table creation, validation, and analytics queries |

---

## Installation

Create and activate a virtual environment.

```bash
py -m venv .venv
```

Activate the environment.

For Git Bash:

```bash
source .venv/Scripts/activate
```

For PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies.

```bash
py -m pip install -r requirements.txt
```

---

## Requirements File

The current `requirements.txt` should contain:

```txt
faker
factory-boy
numpy
pandas
sqlalchemy
psycopg[binary]
python-dotenv
dbt-postgres
great-expectations
streamlit
plotly
```

---

## Environment Configuration

Create a `.env` file in the project root.

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5434
POSTGRES_DB=insurance_pricing
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

Update the values based on your local PostgreSQL setup.

For this project, the current local PostgreSQL port is:

```text
5434
```

---

## Data Generation Overview

Synthetic policy records are generated in:

```text
src/generators/factories.py
```

This file contains:

- `PolicyRecord` dataclass
- `PolicyRecordFactory`
- State, market, and ZIP configurations
- Vehicle make distributions
- Premium calculation logic
- Earned premium calculation logic
- Expected loss cost calculation logic
- Underwriting score logic
- Custom US phone number generator
- Synthetic VIN generator

The generated records are intentionally correlated.

For example:

```text
state → market → ZIP → base rate → written premium
```

```text
prior lapse + low prior BI limits + poor CBR group → lower underwriting score → higher premium
```

```text
vehicle age + physical damage coverage + deductible → premium impact
```

This makes the dataset more useful for analytics than fully random fake data.

---

## Current Policy Table

The current destination table is:

```text
synthetic.policy_terms
```

The table is created by:

```text
sql/create_policy_terms.sql
```

The Python bootstrap script reads and executes this SQL file:

```text
src/db/bootstrap_postgres.py
```

---

## Core Policy Variables

The synthetic policy-term dataset currently includes the following major groups of variables.

### Policy Identifiers

- `policy_id`
- `term_id`
- `account_id`
- `named_insured_id`

### Customer Information

- `first_name`
- `last_name`
- `email`
- `phone_number`
- `street_address`

### Policy Details

- `company`
- `product`
- `policy_status`
- `new_renewal_ind`
- `term_number`
- `effective_date`
- `expiration_date`
- `cancel_date`

### Geography and Distribution

- `state`
- `market`
- `garaging_zip`
- `urbanicity`
- `channel`
- `agency_id`

### Billing and Customer Behavior

- `payment_plan`
- `paperless_ind`
- `autopay_ind`

### Driver and Household Risk

- `driver_age`
- `driver_gender`
- `marital_status`
- `homeowner_ind`
- `household_driver_count`
- `household_vehicle_count`

### Prior Insurance and Underwriting

- `prior_carrier_tier`
- `prior_bi_limits`
- `prior_lapse_ind`
- `prior_tenure_months`
- `cbr_group`
- `underwriting_score`
- `preferred_risk_ind`

### Vehicle Characteristics

- `vehicle_year`
- `vehicle_make`
- `vehicle_body_style`
- `vehicle_symbol`
- `vehicle_age`
- `vehicle_use`
- `annual_mileage`
- `anti_theft_ind`
- `vin`

### Coverage Variables

- `bi_limits`
- `pd_limit`
- `has_physical_damage`
- `coll_deductible`
- `comp_deductible`
- `rental_ind`
- `roadside_ind`

### Pricing and Profitability

- `rate_change_pct`
- `total_written_premium`
- `total_earned_premium`
- `expected_loss_cost`
- `target_loss_ratio`
- `expected_profit`

---

## Create the Database and Table

To create the database, schema, table, constraints, and indexes, run:

```bash
py -m src.db.bootstrap_postgres
```

This script will:

1. Read database settings from `.env`
2. Create the `insurance_pricing` database if it does not exist
3. Execute `sql/create_policy_terms.sql`
4. Create the `synthetic.policy_terms` table
5. Create supporting indexes and constraints

---

## Load Synthetic Data Directly into PostgreSQL

To generate and load 1,000 policy records:

```bash
py -m src.generators.load_policies_to_postgres --rows 1000 --truncate
```

To generate and load 250,000 policy records:

```bash
py -m src.generators.load_policies_to_postgres --rows 250000 --truncate
```

The `--truncate` flag clears the existing table before loading new records.

This is useful because the synthetic factory sequences restart each time the script runs, and `term_id` is the primary key.

---

## One-Command Rebuild

The project also includes a rebuild script:

```text
src/db/rebuild_policy_dataset.py
```

This script can:

1. Create or verify the database
2. Rebuild the policy table
3. Generate synthetic policy records
4. Load the records into Postgres

Run a test rebuild:

```bash
py -m src.db.rebuild_policy_dataset --rows 1000
```

Run a full rebuild:

```bash
py -m src.db.rebuild_policy_dataset --rows 250000
```

---

## Optional CSV Export

A CSV generator is also available:

```text
src/generators/generate_policies.py
```

Generate a sample CSV:

```bash
py -m src.generators.generate_policies --rows 1000 --out data/sample_policy_terms.csv
```

Generate a larger CSV:

```bash
py -m src.generators.generate_policies --rows 250000 --out data/policy_terms.csv
```

CSV files are treated as generated artifacts and should not be committed to Git.

---

## Run Validation Queries

Validation queries are stored in:

```text
sql/validation_queries.sql
```

Run them with:

```bash
psql -h localhost -p 5434 -U postgres -d insurance_pricing -P border=2 -f sql/validation_queries.sql
```

Optional: save the output to a file.

```bash
psql -h localhost -p 5434 -U postgres -d insurance_pricing -f sql/validation_queries.sql -o data/validation_results.txt
```

---

## Example Validation Queries

The validation file should include checks such as:

```sql
SELECT COUNT(*) AS policy_term_count
FROM synthetic.policy_terms;
```

```sql
SELECT
    state,
    COUNT(*) AS policy_terms,
    ROUND(SUM(total_written_premium), 2) AS written_premium,
    ROUND(SUM(total_earned_premium), 2) AS earned_premium,
    ROUND(SUM(expected_loss_cost), 2) AS expected_loss_cost,
    ROUND(SUM(expected_profit), 2) AS expected_profit
FROM synthetic.policy_terms
GROUP BY state
ORDER BY state;
```

```sql
SELECT
    preferred_risk_ind,
    cbr_group,
    COUNT(*) AS policy_terms,
    ROUND(AVG(total_written_premium), 2) AS avg_written_premium,
    ROUND(
        SUM(expected_loss_cost) / NULLIF(SUM(total_earned_premium), 0),
        4
    ) AS expected_loss_ratio
FROM synthetic.policy_terms
GROUP BY preferred_risk_ind, cbr_group
ORDER BY preferred_risk_ind, cbr_group;
```

---

## Current Workflow

The current preferred workflow is:

```bash
py -m src.db.bootstrap_postgres
```

Then:

```bash
py -m src.generators.load_policies_to_postgres --rows 1000 --truncate
```

Validate the test load.

```bash
psql -h localhost -p 5434 -U postgres -d insurance_pricing -P border=2 -f sql/validation_queries.sql
```

Then run the full load.

```bash
py -m src.generators.load_policies_to_postgres --rows 250000 --truncate
```

Or rebuild everything with one command:

```bash
py -m src.db.rebuild_policy_dataset --rows 250000
```

---

## Analytics Use Cases Supported

The current policy-term dataset supports analysis such as:

- Written premium by state and market
- Earned premium by policy month
- Expected loss ratio by risk segment
- Profitability by prior BI limit
- Premium by CBR group
- Preferred versus non-preferred risk performance
- New business versus renewal mix
- Agency-level book quality
- Rate-change impact simulation
- Vehicle and coverage segmentation
- Policy status distribution
- Geographic profitability diagnostics

---

## Example Analytical Questions

This dataset can answer questions like:

```text
Which states have the highest expected profitability?
```

```text
Are non-preferred risks priced adequately?
```

```text
How does prior BI limit correlate with expected loss ratio?
```

```text
Which markets have the largest premium concentration?
```

```text
Are rate increases concentrated in underperforming segments?
```

```text
How does agency channel mix affect book quality?
```

---

## Data Privacy

This project uses fully synthetic data.

No real customer, policy, claim, driver, vehicle, or financial data is used.

The dataset is designed for portfolio, analytics, and engineering demonstration purposes only.

---

## Git Ignore Recommendations

Generated data and secrets should not be committed.

Recommended `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc

data/*.csv
data/*.parquet
data/*.txt

.DS_Store
```

---

## Current Limitations

The project currently includes only the policy-term domain.

It does not yet include:

- Quote transactions
- Claims
- Claimants
- Vehicles as a separate normalized table
- Drivers as a separate normalized table
- Rate-change events
- Monthly earned exposure snapshots
- Retention outcomes
- Payment transactions
- Commission data
- External weather or catastrophe indicators

---

## Planned Enhancements

Future project phases may include:

### 1. Claims Domain

Add claim-level data such as:

- `claim_id`
- `policy_id`
- `term_id`
- `claim_date`
- `loss_type`
- `claim_status`
- `paid_loss`
- `case_reserve`
- `incurred_loss`
- `loss_adjustment_expense`
- `at_fault_ind`

### 2. Quote Domain

Add quote-level data such as:

- `quote_id`
- `quote_date`
- `quoted_premium`
- `bound_ind`
- `conversion_ind`
- `channel`
- `marketing_source`

### 3. Rate Change Domain

Add rate-change simulation data such as:

- `rate_change_id`
- `state`
- `market`
- `coverage`
- `effective_date`
- `rate_change_pct`
- `target_segment`

### 4. Monthly Snapshot Table

Add monthly policy exposure snapshots for BI/dashboarding:

- `snapshot_month`
- `policy_id`
- `term_id`
- `written_premium`
- `earned_premium`
- `earned_exposure`
- `inforce_count`

### 5. Power BI or Tableau Dashboard

Build a portfolio command center with views such as:

- Executive KPI summary
- State and market profitability
- Segment diagnostics
- Rate-change impact
- Agency distribution
- Risk mix shift
- Expected loss ratio analysis

---

## Portfolio Positioning

This project is intended to demonstrate more than basic Python scripting.

It shows the ability to:

- Design insurance-domain data models
- Create realistic synthetic data
- Build reusable data generation pipelines
- Work with PostgreSQL
- Use bulk loading patterns
- Validate data quality with SQL
- Prepare data for pricing and profitability analytics
- Structure a project in a production-style format

The long-term goal is to evolve this into a full insurance analytics command center that can be showcased as a senior-level analytics portfolio project.

---

## Current Primary Commands

Create or rebuild the table:

```bash
py -m src.db.bootstrap_postgres
```

Load 1,000 test records:

```bash
py -m src.generators.load_policies_to_postgres --rows 1000 --truncate
```

Load 250,000 records:

```bash
py -m src.generators.load_policies_to_postgres --rows 250000 --truncate
```

Run a full rebuild:

```bash
py -m src.db.rebuild_policy_dataset --rows 250000
```

Run validation queries:

```bash
psql -h localhost -p 5434 -U postgres -d insurance_pricing -P border=2 -f sql/validation_queries.sql
```
