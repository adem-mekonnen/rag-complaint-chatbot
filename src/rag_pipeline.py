# src/rag_pipeline.py
import os
# FORCE CPU MODE TO SAVE VRAM/RAM
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

class RAGService:
    def __init__(self, vector_store_path="./vector_store"):
        print(f"Initializing RAG Service from {vector_store_path}...")
        
        # 1. Load Embeddings with minimal memory
        print("Loading Embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # 2. Load Vector Store
        if not os.path.exists(vector_store_path):
             if os.path.exists("vector_store_full"):
                 print(f"Path {vector_store_path} not found. Switching to 'vector_store_full'...")
                 vector_store_path = "vector_store_full"
             else:
                 raise FileNotFoundError(f"Vector store not found at {vector_store_path}")

        collection_name = "complaints_rag_full" if "full" in vector_store_path else "complaints_rag"
        self.vector_db = Chroma(
            persist_directory=vector_store_path,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
        
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 3}) # Reduced k to 3 to save RAM
        
        # 4. Setup LLM (Smallest possible)
        print("Loading LLM (flan-t5-small)...")
        model_id = "google/flan-t5-small"
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            # Load model directly to CPU
            model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

            pipe = pipeline(
                "text2text-generation",
                model=model, 
                tokenizer=tokenizer, 
                max_new_tokens=256,
                device=-1 # Force CPU
            )
            self.llm = HuggingFacePipeline(pipeline=pipe)
            print("LLM loaded.")
            
        except Exception as e:
            print(f"Error loading LLM: {e}")
            raise

        self.template = """
        You are a helpful assistant. Answer based on the context below.
        
        Context: {context}
        
        Question: {question}
        
        Answer:
        """
        self.prompt = PromptTemplate.from_template(self.template)

    def format_docs(self, docs):
        return "\n\n".join(f"[ID: {doc.metadata.get('complaint_id', 'N/A')}] {doc.page_content}" for doc in docs)

    def answer_question(self, question):
        print(f"Processing: {question}")
        docs = self.retriever.invoke(question)
        context_text = self.format_docs(docs)
        chain = self.prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context_text, "question": question})
        return answer, docs

if __name__ == "__main__":
    # Test path logic
    path = "vector_store_full" if os.path.exists("vector_store_full") else "vector_store"
    rag = RAGService(vector_store_path=path)
    q = "What are common complaints?"
    ans, _ = rag.answer_question(q)
    print(f"Answer: {ans}")