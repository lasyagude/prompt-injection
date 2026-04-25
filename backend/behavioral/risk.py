
def compute_risk(
    deberta_score,
    role_shift,
    topic_shift,
    attack_pattern,
    probing,
    repetition,
    flag_rate,
    prev_risk,
    history_risks
):
    # 1. NO soft-clip — trust the model at full strength
    deberta_score = deberta_score  # used directly

    # 2. Behavioral feature score
    feature_score = (
        0.20 * role_shift +
        0.16 * topic_shift +
        0.14 * attack_pattern +
        0.14 * probing +
        0.08 * repetition +
        0.28 * flag_rate
    )

    # 3. Fusion — DeBERTa leads, behavioral supports
    combined_score = (
        0.55 * deberta_score +
        0.45 * feature_score
    )

    # 4. Synergy boost (unchanged — valid idea)
    synergy = 1 + (0.5 * role_shift * topic_shift)
    synergy = min(synergy, 1.3)
    current_risk = min(combined_score * synergy, 1.0)

    # 5. History weight — contributes but doesn't dominate
    if history_risks:
        window = history_risks[-5:]
        weights = [0.5 ** (len(window) - i) for i in range(len(window))]
        total_w = sum(weights)
        weighted_history = sum(w * r for w, r in zip(weights, window)) / total_w
        escalation = len([r for r in history_risks[-4:] if r > 0.35])
        # Cap history_weight lower — max 0.35 so current turn always dominates
        history_weight = min(0.20 + escalation * 0.05, 0.35)
    else:
        weighted_history = prev_risk
        history_weight = 0.20

    final_risk = (
        (1 - history_weight) * current_risk +
        history_weight * weighted_history
    )

    # 6. Consecutive spike booster (unchanged)
    if len(history_risks) >= 2 and all(r > 0.35 for r in history_risks[-2:]):
        final_risk = min(final_risk * 1.35, 1.0)

    # 7. FIXED false positive guard — protect against LOW deberta + HIGH behavior
    #    NOT the other way around. If DeBERTa is confident, trust it fully.
    behavioral_max = max(role_shift, topic_shift, attack_pattern, probing, repetition)
    if deberta_score < 0.30 and behavioral_max > 0.70:
        # Behavioral is screaming but model sees nothing — cap at WARN
        final_risk = min(final_risk, 0.64)

    final_risk = round(final_risk, 4)

    if final_risk < 0.35:
        decision = "ALLOW"
    elif final_risk < 0.65:
        decision = "WARN"
    else:
        decision = "BLOCK"

    return final_risk, decision
