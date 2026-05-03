# qa.py
import os
from langchain_groq import ChatGroq
from utils.prompts import RAG_QA_PROMPT
from embedder.embedder import ContractRAG

class ContractQA:
    """
    Q&A system for contracts using RAG with Groq.
    """
    
    def __init__(self, rag: ContractRAG):
        self.rag = rag
        # REMOVED: llm initialization from here

    def answer_question(self, question: str, top_k: int = 3) -> dict:
        """Answer a question about the contract using RAG."""
        
        # ADDED: Initialize here to pick up token after Streamlit entry
        llm = ChatGroq(
            model_name="llama-3.1-8b-instant", 
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Search for relevant clauses
        results = self.rag.search(question, top_k=top_k)
        
        if not results:
            return {
                "question": question,
                "answer": "I couldn't find any relevant sections in the contract to answer this.",
                "sources": [],
                "confidence": 0
            }
        
        # Build context from search results
        context_parts = []
        sources = []
        
        for chunk, similarity in results:
            header = chunk.get('header', 'Unknown Section')
            content = chunk.get('content', '')
            context_parts.append(f"SECTION: {header}\nCONTENT: {content}")
            sources.append({
                "header": header,
                "similarity": round(float(similarity), 3),
                "preview": content[:150] + "..."
            })
        
        context = "\n\n".join(context_parts)
        
        # Get LLM answer
        try:
            prompt = RAG_QA_PROMPT.format(
                context=context,
                question=question
            )
            
            # Use the local llm instance created above
            # Note: For ChatGroq, use .invoke(prompt).content to get string
            response = llm.invoke(prompt)
            answer = response.content.strip()
            
            avg_similarity = sum(s['similarity'] for s in sources) / len(sources)
            
            return {
                "question": question,
                "answer": answer,
                "sources": sources,
                "confidence": round(avg_similarity, 3)
            }
            
        except Exception as e:
            return {
                "question": question,
                "answer": f"Processing error: {str(e)}",
                "sources": sources,
                "confidence": 0
            }
