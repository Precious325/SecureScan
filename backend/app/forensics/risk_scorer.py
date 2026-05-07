def compute_risk_score(metadata_result: dict, ela_result: dict, hash_result: dict) -> dict:
    """
    Synthesize the three forensic layer results into a single risk score and verdict.
    """
    score = 0
    
    # ── Layer 1: Metadata scoring ─────────────────────────────────────────
    anomalies = metadata_result.get("anomalies", [])
    for anomaly in anomalies:
        severity = anomaly.get("severity", "LOW")
        if severity == "CRITICAL":
            score += 30
        elif severity == "HIGH":
            score += 15
        elif severity == "MEDIUM":
            score += 8
        elif severity == "LOW":
            score += 3
    
    # ── Layer 2: ELA scoring ──────────────────────────────────────────────
    ela_score = ela_result.get("ela_score", 0)
    if ela_result.get("suspicion_flag"):
        score += 25
    if ela_score > 0.30:
        score += 15
    
    # ── Layer 3: Hash scoring ─────────────────────────────────────────────
    match_status = hash_result.get("match_status", "NOT_IN_DATABASE")
    if match_status == "NO_MATCH":
        score += 40
    elif match_status == "MATCH":
        score -= 10
    
    # Cap score at 100
    score = max(0, min(100, score))
    
    # ── Determine verdict ─────────────────────────────────────────────────
    if score <= 15:
        verdict = "AUTHENTIC"
        recommendation = "No forensic indicators detected. Document may be accepted pending other institutional checks."
        color = "GREEN"
    elif score <= 40:
        verdict = "SUSPICIOUS"
        recommendation = "Low-level anomalies present. Human review of the specific findings is recommended before acceptance."
        color = "YELLOW"
    elif score <= 70:
        verdict = "LIKELY FORGED"
        recommendation = "Multiple significant anomalies detected. Institutional cross-verification strongly recommended."
        color = "ORANGE"
    else:
        verdict = "FORGED"
        recommendation = "Critical forensic indicators detected. Document should be rejected pending full investigation."
        color = "RED"
    
    return {
        "risk_score": score,
        "risk_verdict": verdict,
        "recommendation": recommendation,
        "color": color
    }