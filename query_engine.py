from langchain.chains import RetrievalQA
#from langchain.llms import Ollama
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


class LogQueryEngine:
    def __init__(self, vectorstore, model_name="llama3:8b"):
        self.vectorstore = vectorstore
        #self.llm = Ollama(model=model_name)
        self.llm =OllamaLLM(model=model_name)
        
        # Create prompt template
        template = """
        You are an HTTP access log analysis expert. You analyze log entries to provide insights, identify patterns, and answer questions about web server activity.

        Given the following HTTP access log entries, answer the user's question with accurate information derived directly from the logs.

        For security-related questions, look for patterns like:
        - Multiple failed authentication attempts (401/403 status codes)
        - Unusual HTTP methods or paths
        - High request rates from single IPs
        - Suspicious user agents or payloads

        For performance questions, focus on:
        - Response times
        - Status codes (especially 5xx errors)
        - Resource sizes
        - Peak traffic periods

        Always cite specific log entries that support your answer.

        LOG ENTRIES:
        {context}

        USER QUESTION:
        {question}
        
        ANSWER:
        """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 10}),
            chain_type_kwargs={"prompt": self.prompt}
        )
    
    def query(self, question: str) -> str:
        """Process a question and return an answer."""
        return self.qa_chain.run(question)
