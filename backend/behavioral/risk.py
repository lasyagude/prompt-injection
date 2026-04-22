def compute_risk(
    deberta_score,
    role_shift,
    topic_shift,
    attack_pattern,
    probing,
    repetition,
    prev_risk,
    history_risks
):

    # -------------------------------
    # 1. Weighted Feature Score
    # -------------------------------
    feature_score = (
        0.22 * role_shift +
        0.22 * topic_shift +
        0.16 * attack_pattern +
        0.16 * probing +
        0.10 * repetition
    )

    # -------------------------------
    # 2. Balanced Fusion (NOT max)
    # -------------------------------
    combined_score = (
        0.55 * feature_score +   # behavior more important
        0.45 * deberta_score     # model still important but not dominant
    )

    # -------------------------------
    # 3. Mild Synergy Boost
    # -------------------------------
    synergy = 1 + (0.5 * role_shift * topic_shift)
    synergy = min(synergy, 1.3)

    current_risk = min(combined_score * synergy, 1.0)

    # -------------------------------
    # 4. LIMITED TEMPORAL MEMORY
    # -------------------------------
    history_weight = 0.25   # 👈 controlled (0.2–0.3 as you wanted)

    final_risk = (
        (1 - history_weight) * current_risk +
        history_weight * prev_risk
    )

    # -------------------------------
    # 5. STABLE THRESHOLDS
    # -------------------------------
    if final_risk < 0.35:
        decision = "ALLOW"
    elif final_risk < 0.65:
        decision = "WARN"
    else:
        decision = "BLOCK"

    return round(final_risk, 4), decision