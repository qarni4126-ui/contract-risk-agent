# scorer.py
"""
Risk Scoring
Rule-based + heuristics for risk assessment.
Each risk has: score (0-100), level (low/med/high), reason.
"""

from typing import List, Dict, Any


# Risk keywords for rule-based detection
HIGH_RISK_KEYWORDS = {
    "unlimited liability": 25,
    "indemnify": 15,
    "breach": 15,
    "termination": 12,
    "penalty": 15,
    "liquidated damages": 20,
    "material breach": 10,
    "confidentiality": 8,
    "non-compete": 10,
    "exclusive": 8,
}

MEDIUM_RISK_KEYWORDS = {
    "may terminate": 5,
    "at will": 5,
    "restrict": 5,
    "limit": 3,
    "obligation": 3,
    "warranty": 5,
}


def score_single_risk(risk: dict) -> dict:
    """
    Score a single risk extracted from LLM.
    
    Args:
        risk: Risk dict with keys: risk_text, category
        
    Returns:
        Same risk dict + score, level, reason
    """
    risk_text = risk.get('risk_text', '').lower()
    category = risk.get('category', 'OTHER')
    
    base_score = 0
    reasons = []
    
    # Rule 1: Check for high-risk keywords
    for keyword, points in HIGH_RISK_KEYWORDS.items():
        if keyword in risk_text:
            base_score += points
            reasons.append(f"Contains '{keyword}'")
    
    # Rule 2: Check for medium-risk keywords
    for keyword, points in MEDIUM_RISK_KEYWORDS.items():
        if keyword in risk_text:
            base_score += points
            reasons.append(f"Contains '{keyword}'")
    
    # Rule 3: Category-based scoring
    category_boost = {
        "LIABILITY": 15,
        "TERMINATION": 12,
        "PENALTY": 18,
        "RESTRICTION": 8,
        "COMPLIANCE": 10,
        "OTHER": 0
    }
    
    base_score += category_boost.get(category, 0)
    reasons.append(f"Category: {category}")
    
    # Rule 4: Length matters (very long = more complex = riskier)
    words = len(risk_text.split())
    if words > 30:
        base_score += 5
        reasons.append("Complex clause (long text)")
    
    # Normalize to 0-100
    score = min(base_score, 100)
    
    # Determine level
    if score >= 60:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"
    
    return {
        **risk,
        "score": score,
        "level": level,
        "reasons": reasons
    }


def calculate_contract_risk_score(chunks: List[dict]) -> dict:
    """
    Calculate overall contract risk from all chunks.
    
    Returns:
    {
        "overall_score": 65,
        "overall_level": "MEDIUM",
        "high_risk_count": 5,
        "medium_risk_count": 10,
        "low_risk_count": 20,
        "top_risks": [...]
    }
    
    Args:
        chunks: Chunks with extracted_data
        
    Returns:
        Risk summary dict
    """
    all_risks = []
    all_scores = []
    
    # Collect all risks
    for chunk in chunks:
        extracted = chunk.get('extracted_data', {})
        risks = extracted.get('risks', [])
        
        for risk in risks:
            scored_risk = score_single_risk(risk)
            all_risks.append(scored_risk)
            all_scores.append(scored_risk['score'])
    
    # Calculate overall score (weighted average)
    if all_scores:
        overall_score = sum(all_scores) / len(all_scores)
    else:
        overall_score = 0
    
    # Determine overall level
    if overall_score >= 60:
        overall_level = "HIGH"
    elif overall_score >= 40:
        overall_level = "MEDIUM"
    else:
        overall_level = "LOW"
    
    # Count by level
    high = sum(1 for r in all_risks if r['level'] == 'HIGH')
    medium = sum(1 for r in all_risks if r['level'] == 'MEDIUM')
    low = sum(1 for r in all_risks if r['level'] == 'LOW')
    
    # Top risks (sorted by score)
    top_risks = sorted(all_risks, key=lambda x: x['score'], reverse=True)[:5]
    
    return {
        "overall_score": round(overall_score, 1),
        "overall_level": overall_level,
        "high_risk_count": high,
        "medium_risk_count": medium,
        "low_risk_count": low,
        "total_risks": len(all_risks),
        "top_risks": top_risks,
        "all_risks": all_risks
    }


def score_contract(chunks: List[dict]) -> List[dict]:
    """
    Add scoring to each chunk's extracted risks.
    
    Args:
        chunks: Chunks with extracted_data
        
    Returns:
        Same chunks with scored risks
    """
    scored_chunks = []
    
    for chunk in chunks:
        extracted = chunk.get('extracted_data', {})
        
        # Score risks in this chunk
        scored_risks = [score_single_risk(r) for r in extracted.get('risks', [])]
        
        chunk['extracted_data']['risks'] = scored_risks
        scored_chunks.append(chunk)
    
    return scored_chunks