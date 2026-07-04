SELECT COUNT(*) AS policy_term_count
FROM synthetic.policy_terms;

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