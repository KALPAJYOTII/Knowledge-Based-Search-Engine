from typing import List, Optional
from langchain_classic.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_classic.prompts import PromptTemplate

from app.config.settings import GEMINI_API_KEY, GEMINI_MODEL


class LLMService:
    """Service for LLM operations using Google Gemini"""

    def __init__(self):
        """Initialize Gemini LLM"""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
            top_p=0.85,
        )

    def create_qa_chain(self, retriever):
        """
        Create a QA chain with the retriever
        
        Args:
            retriever: LangChain retriever for document retrieval
            
        Returns:
            RetrievalQA chain
        """
        # Custom prompt template for better answers
        prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        return qa_chain

    def answer_question(self, query: str, retrieved_documents: List[Document]) -> str:
        """
        Generate an answer based on retrieved documents
        
        Args:
            query: The question to answer
            retrieved_documents: List of relevant documents
            
        Returns:
            Generated answer string
        """
        if not retrieved_documents:
            return "I don't have any relevant information to answer this question."
        
        # Build context from documents
        context = "\n\n".join([doc.page_content for doc in retrieved_documents])
        
        # Create prompt
        prompt = f"""Based on the following context, answer the question. If the answer is not in the context, say "I don't know".

Context:
{context}

Question: {query}

Answer:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            raise Exception(f"Failed to generate answer: {str(e)}")
