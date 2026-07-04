BEGIN;

CREATE SCHEMA IF NOT EXISTS synthetic;

DROP TABLE IF EXISTS synthetic.policy_terms;

CREATE TABLE synthetic.policy_terms (
    policy_id TEXT NOT NULL,
    term_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    named_insured_id TEXT NOT NULL,

    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone_number TEXT,
    street_address TEXT,

    company TEXT,
    product TEXT,
    policy_status TEXT,
    new_renewal_ind TEXT,
    term_number INTEGER,

    effective_date DATE,
    expiration_date DATE,
    cancel_date DATE,

    state CHAR(2),
    market TEXT,
    garaging_zip TEXT,
    urbanicity TEXT,
    channel TEXT,
    agency_id TEXT,

    payment_plan TEXT,
    paperless_ind CHAR(1),
    autopay_ind CHAR(1),

    driver_age INTEGER,
    driver_gender CHAR(1),
    marital_status TEXT,
    homeowner_ind CHAR(1),
    household_driver_count INTEGER,
    household_vehicle_count INTEGER,

    prior_carrier_tier TEXT,
    prior_bi_limits TEXT,
    prior_lapse_ind CHAR(1),
    prior_tenure_months INTEGER,
    cbr_group TEXT,
    underwriting_score INTEGER,
    preferred_risk_ind CHAR(1),

    vehicle_year INTEGER,
    vehicle_make TEXT,
    vehicle_body_style TEXT,
    vehicle_symbol INTEGER,
    vehicle_age INTEGER,
    vehicle_use TEXT,
    annual_mileage INTEGER,
    anti_theft_ind CHAR(1),
    vin TEXT,

    bi_limits TEXT,
    pd_limit INTEGER,
    has_physical_damage CHAR(1),
    coll_deductible INTEGER,
    comp_deductible INTEGER,
    rental_ind CHAR(1),
    roadside_ind CHAR(1),

    rate_change_pct NUMERIC(8, 4),
    total_written_premium NUMERIC(12, 2),
    total_earned_premium NUMERIC(12, 2),
    expected_loss_cost NUMERIC(12, 2),
    target_loss_ratio NUMERIC(8, 4),
    expected_profit NUMERIC(12, 2),

    CONSTRAINT pk_policy_terms PRIMARY KEY (term_id),

    CONSTRAINT chk_policy_status
        CHECK (
            policy_status IN (
                'Active',
                'Expired',
                'Cancelled',
                'Non-Renewed'
            )
        ),

    CONSTRAINT chk_new_renewal_ind
        CHECK (
            new_renewal_ind IN (
                'New',
                'Renewal'
            )
        ),

    CONSTRAINT chk_term_number
        CHECK (
            term_number IS NULL
            OR term_number >= 1
        ),

    CONSTRAINT chk_effective_expiration_dates
        CHECK (
            effective_date IS NULL
            OR expiration_date IS NULL
            OR expiration_date > effective_date
        ),

    CONSTRAINT chk_cancel_date
        CHECK (
            cancel_date IS NULL
            OR effective_date IS NULL
            OR expiration_date IS NULL
            OR (
                cancel_date >= effective_date
                AND cancel_date <= expiration_date
            )
        ),

    CONSTRAINT chk_state
        CHECK (
            state IS NULL
            OR state IN (
                'MO',
                'TN',
                'IL',
                'TX',
                'GA'
            )
        ),

    CONSTRAINT chk_yes_no_flags
        CHECK (
            (paperless_ind IS NULL OR paperless_ind IN ('Y', 'N'))
            AND (autopay_ind IS NULL OR autopay_ind IN ('Y', 'N'))
            AND (homeowner_ind IS NULL OR homeowner_ind IN ('Y', 'N'))
            AND (prior_lapse_ind IS NULL OR prior_lapse_ind IN ('Y', 'N'))
            AND (preferred_risk_ind IS NULL OR preferred_risk_ind IN ('Y', 'N'))
            AND (anti_theft_ind IS NULL OR anti_theft_ind IN ('Y', 'N'))
            AND (has_physical_damage IS NULL OR has_physical_damage IN ('Y', 'N'))
            AND (rental_ind IS NULL OR rental_ind IN ('Y', 'N'))
            AND (roadside_ind IS NULL OR roadside_ind IN ('Y', 'N'))
        ),

    CONSTRAINT chk_driver_age
        CHECK (
            driver_age IS NULL
            OR driver_age BETWEEN 16 AND 100
        ),

    CONSTRAINT chk_driver_gender
        CHECK (
            driver_gender IS NULL
            OR driver_gender IN ('M', 'F')
        ),

    CONSTRAINT chk_household_counts
        CHECK (
            (household_driver_count IS NULL OR household_driver_count >= 1)
            AND (household_vehicle_count IS NULL OR household_vehicle_count >= 1)
        ),

    CONSTRAINT chk_prior_tenure_months
        CHECK (
            prior_tenure_months IS NULL
            OR prior_tenure_months >= 0
        ),

    CONSTRAINT chk_cbr_group
        CHECK (
            cbr_group IS NULL
            OR cbr_group IN (
                'Excellent',
                'Good',
                'Average',
                'I/N',
                'Poor'
            )
        ),

    CONSTRAINT chk_underwriting_score
        CHECK (
            underwriting_score IS NULL
            OR underwriting_score BETWEEN 0 AND 1000
        ),

    CONSTRAINT chk_vehicle_year
        CHECK (
            vehicle_year IS NULL
            OR vehicle_year BETWEEN 1980 AND 2035
        ),

    CONSTRAINT chk_vehicle_age
        CHECK (
            vehicle_age IS NULL
            OR vehicle_age >= 0
        ),

    CONSTRAINT chk_annual_mileage
        CHECK (
            annual_mileage IS NULL
            OR annual_mileage >= 0
        ),

    CONSTRAINT chk_vin_length
        CHECK (
            vin IS NULL
            OR LENGTH(vin) = 17
        ),

    CONSTRAINT chk_pd_limit
        CHECK (
            pd_limit IS NULL
            OR pd_limit > 0
        ),

    CONSTRAINT chk_deductibles
        CHECK (
            (
                has_physical_damage = 'Y'
                AND coll_deductible IS NOT NULL
                AND comp_deductible IS NOT NULL
            )
            OR (
                has_physical_damage = 'N'
                AND coll_deductible IS NULL
                AND comp_deductible IS NULL
            )
            OR has_physical_damage IS NULL
        ),

    CONSTRAINT chk_rate_change_pct
        CHECK (
            rate_change_pct IS NULL
            OR rate_change_pct BETWEEN -1.0000 AND 5.0000
        ),

    CONSTRAINT chk_premium_values
        CHECK (
            (total_written_premium IS NULL OR total_written_premium >= 0)
            AND (total_earned_premium IS NULL OR total_earned_premium >= 0)
            AND (expected_loss_cost IS NULL OR expected_loss_cost >= 0)
        ),

    CONSTRAINT chk_target_loss_ratio
        CHECK (
            target_loss_ratio IS NULL
            OR target_loss_ratio BETWEEN 0 AND 5
        )
);

CREATE INDEX idx_policy_terms_policy_id
    ON synthetic.policy_terms (policy_id);

CREATE INDEX idx_policy_terms_account_id
    ON synthetic.policy_terms (account_id);

CREATE INDEX idx_policy_terms_named_insured_id
    ON synthetic.policy_terms (named_insured_id);

CREATE INDEX idx_policy_terms_effective_date
    ON synthetic.policy_terms (effective_date);

CREATE INDEX idx_policy_terms_expiration_date
    ON synthetic.policy_terms (expiration_date);

CREATE INDEX idx_policy_terms_state_market
    ON synthetic.policy_terms (state, market);

CREATE INDEX idx_policy_terms_state_market_zip
    ON synthetic.policy_terms (state, market, garaging_zip);

CREATE INDEX idx_policy_terms_policy_status
    ON synthetic.policy_terms (policy_status);

CREATE INDEX idx_policy_terms_new_renewal
    ON synthetic.policy_terms (new_renewal_ind);

CREATE INDEX idx_policy_terms_agency_id
    ON synthetic.policy_terms (agency_id);

CREATE INDEX idx_policy_terms_channel
    ON synthetic.policy_terms (channel);

CREATE INDEX idx_policy_terms_cbr_group
    ON synthetic.policy_terms (cbr_group);

CREATE INDEX idx_policy_terms_preferred_risk
    ON synthetic.policy_terms (preferred_risk_ind);

CREATE INDEX idx_policy_terms_prior_lapse
    ON synthetic.policy_terms (prior_lapse_ind);

CREATE INDEX idx_policy_terms_prior_bi_limits
    ON synthetic.policy_terms (prior_bi_limits);

CREATE INDEX idx_policy_terms_bi_limits
    ON synthetic.policy_terms (bi_limits);

CREATE INDEX idx_policy_terms_vehicle_make
    ON synthetic.policy_terms (vehicle_make);

CREATE INDEX idx_policy_terms_written_premium
    ON synthetic.policy_terms (total_written_premium);

CREATE INDEX idx_policy_terms_expected_profit
    ON synthetic.policy_terms (expected_profit);

COMMIT;