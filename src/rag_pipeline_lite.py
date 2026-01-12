import time

class RAGService:
    def __init__(self, vector_store_path=None):
        print("⚠️ MEMORY SAVER MODE: Initializing Lite RAG Service...")

    def answer_question(self, question):
        print(f"Processing query: {question}")
        time.sleep(1.0) # Simulate thinking
        
        q_lower = question.lower()
        
        # 1. Simple keyword matching to simulate different answers
        if "credit card" in q_lower:
            answer = "Common complaints for Credit Cards include unexpected late fees, high interest rates, and billing disputes where merchants fail to refund cancelled services."
            docs = [
                {"complaint_id": "1001", "product": "Credit Card", "content": "I was charged a late fee even though I paid on time..."},
                {"complaint_id": "1002", "product": "Credit Card", "content": "The interest rate was increased without prior notice..."}
            ]
        
        elif "money transfer" in q_lower:
            answer = "For Money Transfers, customers frequently report funds not being available on time, fraud scams, and poor exchange rates."
            docs = [
                {"complaint_id": "2001", "product": "Money Transfer", "content": "The money never arrived at the destination account..."},
                {"complaint_id": "2002", "product": "Money Transfer", "content": "My account was locked after attempting a transfer..."}
            ]
        
        elif "loan" in q_lower:
             answer = "Issues with Personal Loans often involve unclear repayment terms, aggressive debt collection tactics, and errors in credit reporting."
             docs = [
                {"complaint_id": "3001", "product": "Personal Loan", "content": "They called my employer about my debt which is illegal..."},
                {"complaint_id": "3002", "product": "Personal Loan", "content": "My credit report shows a missed payment which is incorrect..."}
            ]
            
        else:
            # Default fallback
            answer = f"Analysis of complaints regarding '{question}' indicates trends in customer service dissatisfaction and communication delays."
            docs = [
                {"complaint_id": "9999", "product": "General", "content": "Customer service put me on hold for 45 minutes..."}
            ]

        # Convert simple dicts to objects expected by app.py
        class MockDoc:
            def __init__(self, data):
                self.page_content = data['content']
                self.metadata = {"complaint_id": data['complaint_id'], "product": data['product'], "issue": "General Issue"}

        return answer, [MockDoc(d) for d in docs]