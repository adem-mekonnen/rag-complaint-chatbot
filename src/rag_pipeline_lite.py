# src/rag_pipeline_lite.py
import time

class RAGService:
    def __init__(self, vector_store_path=None):
        """
        Initializes a lightweight mock service that doesn't consume RAM.
        """
        print("⚠️ MEMORY SAVER MODE: Initializing Lite RAG Service...")
        print("   (Skipping heavy model loading to prevent crashes)")

    def answer_question(self, question):
        """
        Simulates answering a question.
        """
        print(f"Processing query: {question}")
        
        # Simulate processing time
        time.sleep(1.5)
        
        # 1. Generate a placeholder answer
        # You can customize this to look like a real AI response for your demo
        answer = (
            f"Based on the complaints regarding '{question}', customers frequently mention "
            "issues with unexpected fees and lack of communication. "
            "Several reports indicate that resolving these disputes takes multiple calls."
        )
        
        # 2. Generate fake source documents (for the UI to display)
        # This ensures the 'View Sources' expander in Streamlit works
        class MockDoc:
            def __init__(self, content, meta):
                self.page_content = content
                self.metadata = meta

        docs = [
            MockDoc(
                content="I was charged a late fee even though I paid on time...",
                meta={"complaint_id": "550123", "product": "Credit Card", "issue": "Late Fees"}
            ),
            MockDoc(
                content="The customer service representative could not explain the transaction...",
                meta={"complaint_id": "559876", "product": "Checking Account", "issue": "Customer Service"}
            )
        ]
        
        return answer, docs