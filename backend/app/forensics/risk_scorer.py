def compute_risk_score(metadata_result: dict, ela_result: dict, hash_result: dict, doc_type: str = "official_pdf") -> dict:
    """
    Context-aware risk scoring based on document type.
    doc_type: official_pdf, scanned, phone_photo, downloaded
    """
    score = 0

    # ── Layer 1: Metadata scoring ─────────────────────────────────────────
    anomalies = metadata_result.get("anomalies", [])
    for anomaly in anomalies:
        rule_id = anomaly.get("rule_id", "")
        severity = anomaly.get("severity", "LOW")

        # Phone photos and scanned docs — skip camera and transfer metadata rules
        if doc_type in ["phone_photo", "scanned"]:
            if rule_id in ["MD-06", "MD-07", "MD-03", "MD-04"]:
                continue

        # Downloaded files — skip metadata stripping rules
        if doc_type == "downloaded":
            if rule_id in ["MD-07", "MD-04", "MD-06"]:
                continue

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
    ela_flag = ela_result.get("suspicion_flag", False)

    if ela_flag:
        if doc_type == "phone_photo":
            if ela_score > 0.35:
                score += 10
        elif doc_type == "scanned":
            if ela_score > 0.25:
                score += 15
        else:
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