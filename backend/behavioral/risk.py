def compute_risk(
    deberta_score,
    role_shift,
    topic_shift,
    attack_pattern,
    probing,
    repetition,
    flag_rate,
    escalation,
    prev_risk,
    history_risks
):
    # 1. Soft-clip DeBERTa — prevent extreme scores from dominating
    # Squashes 1.0 → ~0.88, leaves 0.5 at 0.5, leaves 0.0 at 0.0
    # This is what allows WARN to exist when DeBERTa is highly confident
    deberta_score = deberta_score * (1 - 0.15 * deberta_score)

    # 2. Behavioral feature score
    # escalation_rate replaces the previously dead 0.0 placeholder
    # Weights sum to 1.0
    feature_score = (
        0.20 * role_shift +
        0.16 * topic_shift +
        0.14 * attack_pattern +
        0.14 * probing +
        0.08 * repetition +
        0.18 * flag_rate +
        0.10 * escalation
    )

    # 3. Fusion — DeBERTa leads, behavioral supports
    combined_score = (
        0.55 * deberta_score +
        0.45 * feature_score
    )

    # 4. Synergy boost — role shift + topic shift together = suspicious
    synergy = 1 + (0.5 * role_shift * topic_shift)
    synergy = min(synergy, 1.3)
    current_risk = min(combined_score * synergy, 1.0)

    # 5. History weighting — contributes but never dominates
    if history_risks:
        window = history_risks[-5:]
        weights = [0.5 ** (len(window) - i) for i in range(len(window))]
        total_w = sum(weights)
        weighted_history = sum(w * r for w, r in zip(weights, window)) / total_w
        # FIXED: renamed to risky_count so it never overwrites escalation_rate
        risky_count = len([r for r in history_risks[-4:] if r > 0.35])
        history_weight = min(0.20 + risky_count * 0.05, 0.35)
    else:
        weighted_history = prev_risk
        history_weight = 0.20

    final_risk = (
        (1 - history_weight) * current_risk +
        history_weight * weighted_history
    )

    # 6. Consecutive spike booster — only after 2 genuinely risky turns
    # Kept at 1.35 to match research paper results
    if len(history_risks) >= 2 and all(r > 0.35 for r in history_risks[-2:]):
        final_risk = min(final_risk * 1.35, 1.0)

    # 7. False positive guard — behavioral screaming but DeBERTa sees nothing
    # Prevents pure behavioral noise from blocking benign messages
    behavioral_max = max(
        role_shift, topic_shift, attack_pattern, probing, repetition
    )
    if deberta_score < 0.30 and behavioral_max > 0.70:
        final_risk = min(final_risk, 0.64)

    # NOTE: Confidence Guard (step 8) removed — caused overblocking
    # NOTE: Nonlinear Gate (step 9) removed — caused shadowing bug blocking "hi"
    # The soft-clip on DeBERTa + spike booster handles escalation naturally

    final_risk = round(final_risk, 4)

    if final_risk < 0.35:
        decision = "ALLOW"
    elif final_risk < 0.65:
        decision = "WARN"
    else:
        decision = "BLOCK"

    return final_risk, decision
