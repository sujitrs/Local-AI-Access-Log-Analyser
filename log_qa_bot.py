import os
import argparse
from log_parser import LogParser
from vector_store import LogVectorDB
from query_engine import LogQueryEngine

def main():
    parser = argparse.ArgumentParser(description="HTTP Access Log Q&A Bot")
    parser.add_argument("--log_file", type=str, required=True, help="Path to the log file")
    parser.add_argument("--log_format", type=str, default="apache_common", 
                        choices=["apache_common", "apache_combined"], 
                        help="Log file format")
    parser.add_argument("--model", type=str, default="llama3:8b", help="Ollama model to use")
    parser.add_argument("--vector_db", type=str, default="vector_db", help="Path to save/load vector database")
    parser.add_argument("--rebuild_db", action="store_true", help="Force rebuild of vector database")
    
    args = parser.parse_args()
    
    # Initialize log parser
    parser = LogParser(log_format=args.log_format)
    
    # Parse logs
    print(f"Parsing log file: {args.log_file}")
    logs = parser.parse_file(args.log_file)
    print(f"Parsed {len(logs)} log entries")
    
    # Initialize vector database
    vector_db = LogVectorDB(model_name=args.model)
    
    # Check if vector database exists and should be used
    if os.path.exists(args.vector_db) and not args.rebuild_db:
        print(f"Loading existing vector database from {args.vector_db}")
        vector_db.load_vectorstore(args.vector_db)
    else:
        print("Creating new vector database")
        documents = vector_db.create_documents(logs)
        print("Created docs")
        
        chunked_docs = vector_db.chunk_documents(documents)
        print("Created chunked docs")
        
        vector_db.create_vectorstore(chunked_docs)
        print("Created vector store")
        
        vector_db.save_vectorstore(args.vector_db)
        print(f"Vector database saved to {args.vector_db}")
    
    # Initialize query engine
    query_engine = LogQueryEngine(vector_db.vectorstore, model_name=args.model)
    
    # Interactive query loop
    print("\nHTTP Access Log Q&A Bot")
    print("Type 'exit' to quit")
    
    while True:
        question = input("\nEnter your question: ")
        if question.lower() in ["exit", "quit", "q"]:
            break
        
        print("\nProcessing question...")
        answer = query_engine.query(question)
        print("\nAnswer:")
        print(answer)

if __name__ == "__main__":
    main()
