import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import openai
import PyPDF2
import re
import json
from typing import List, Dict, Any
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OPENAI_API_KEY

class ChromaDBSearch:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.chroma_client = chromadb.Client(Settings(persist_directory="./chroma_db"))
        
        # Use OpenAI's embedding function
        openai.api_key = OPENAI_API_KEY
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai.api_key,
            model_name="text-embedding-ada-002"
        )
        
        self.collection = self.chroma_client.create_collection(name="pdf_content", embedding_function=self.embedding_function)
        self.load_pdf_content()

    def load_pdf_content(self):
        text = self.extract_text_from_pdf()
        chunks = self.chunk_text(text)
        self.collection.add(
            documents=chunks,
            ids=[f"chunk_{i}" for i in range(len(chunks))]
        )

    def extract_text_from_pdf(self) -> str:
        text = ""
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text

    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        words = text.split()
        return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    def search(self, query: str, n_results: int = 1) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0]

    def process_questions(self, questions: List[str]) -> str:
        results = []
        for question in questions:
            answer = self.search(question)[0]
            results.append({
                "question": question,
                "answer": answer
            })
        return json.dumps(results, indent=2)

# Example usage
def main():
    pdf_path = "../docs/handbook.pdf"
    chroma_search = ChromaDBSearch(pdf_path)

    questions = [
        #"What is the name of the company?",
        "Who is the CEO of the company?",
        #"What is their vacation policy?",
        #"What is the termination policy?"
    ]

    output = chroma_search.process_questions(questions)
    print(output)

if __name__ == "__main__":
    main()