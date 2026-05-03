import json
import os
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from utils.prompts import EXTRACTION_PROMPT, RISK_CLASSIFICATION_PROMPT


def extract_from_clause(clause_text: str) -> Dict[str, Any]:
    """Extract obligations, deadlines, risks using Groq."""
    
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant", 
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    try:
        prompt = EXTRACTION_PROMPT.format(clause=clause_text)
        
        print(f"🤖 Calling Groq for extraction...")
        response_text = llm.invoke(prompt).content.strip()
        print(f"✅ Response received: {response_text[:100]}...")
        
        # Clean JSON markdown if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        # Try to parse JSON
        data = json.loads(response_text)
        
        return {
            "obligations": data.get("obligations", []),
            "deadlines": data.get("deadlines", []),
            "risks": data.get("risks", [])
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print(f"Response was: {response_text[:200]}")
        return {"obligations": [], "deadlines": [], "risks": []}
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return {"obligations": [], "deadlines": [], "risks": []}


def classify_risk_level(risk_text: str) -> str:
    """Classify a risk using Groq."""
    
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant", 
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    try:
        prompt = RISK_CLASSIFICATION_PROMPT.format(risk_text=risk_text)
        
        print(f"🔍 Classifying: {risk_text[:50]}...")
        response = llm.invoke(prompt).content.strip().upper()
        print(f"Category: {response}")
        
        valid = ["LIABILITY", "TERMINATION", "PENALTY", "RESTRICTION", "COMPLIANCE", "OTHER"]
        
        # Check if response contains any valid category
        for v in valid:
            if v in response:
                return v
        
        return "OTHER"
        
    except Exception as e:
        print(f"❌ Classification error: {e}")
        return "OTHER"


def extract_all_clauses(chunks: List[dict]) -> List[dict]:
    """Extract data from all clauses in contract."""
    enriched_chunks = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n📄 [{i}/{len(chunks)}] Extracting from: {chunk['header']}")
        print(f"   Content length: {len(chunk['content'])} chars")
        
        extracted = extract_from_clause(chunk['content'])
        
        print(f"   Risks found: {len(extracted['risks'])}")
        
        # Classify each risk
        classified_risks = []
        for risk in extracted['risks']:
            category = classify_risk_level(risk.get('risk_text', ''))
            classified_risks.append({
                **risk,
                "category": category
            })
        
        extracted['risks'] = classified_risks
        chunk['extracted_data'] = extracted
        enriched_chunks.append(chunk)
    
    return enriched_chunks