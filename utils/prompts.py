"""
All LLM prompts centralized here.
"""

EXTRACTION_PROMPT = """
You are a legal contract expert. Your task is to find and extract RISKS from this contract clause.

IMPORTANT: Look for dangerous, risky, or problematic language like:
- liability, indemnify, damages
- breach, termination, penalty
- liquidated damages, non-compete
- restrictions, confidentiality
- unlimited, exclusive
- ANY threatening or risky language

Clause Text:
{clause}

RESPOND ONLY WITH THIS JSON FORMAT:
{{
    "obligations": [
        {{"party": "who", "action": "what they must do"}},
    ],
    "deadlines": [
        {{"date": "YYYY-MM-DD if mentioned", "description": "what is due"}},
    ],
    "risks": [
        {{"risk_text": "exact risky phrase from clause", "category": "risk type"}},
    ]
}}

IMPORTANT:
- Always look for risks. Return empty [] only if truly no risks exist.
- For "risks" field, extract the EXACT risky phrase from the clause.
- Return valid JSON only.
"""

RISK_CLASSIFICATION_PROMPT = """
Classify this single risk into ONE category ONLY.

Risk: {risk_text}

Choose exactly ONE from this list:
1. LIABILITY - financial responsibility, damages, indemnification
2. TERMINATION - cancellation, ending contract
3. PENALTY - fines, breach costs, damages
4. RESTRICTION - limits, non-compete, confidentiality
5. COMPLIANCE - legal/regulatory requirements
6. OTHER - doesn't fit above

RESPOND WITH ONLY THE WORD (no explanation):
LIABILITY
or
TERMINATION
or
PENALTY
or
RESTRICTION
or
COMPLIANCE
or
OTHER
"""

SUMMARY_PROMPT = """
You are a contract analyst. Create a brief 3-4 sentence summary.

Contract:
{contract_text}

Summary:
"""

RAG_QA_PROMPT = """
Answer this question using ONLY the contract:

Contract:
{context}

Question: {question}

Answer:
"""